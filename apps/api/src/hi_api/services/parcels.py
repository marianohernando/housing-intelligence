"""Clients of the official services behind the search by parcel (D-250), async with timeouts.

- **Catastro** (Sede Electrónica del Catastro, free JSON services): the parcel of a reference
  (Consulta_DNPRC), its reference point (Consulta_CPMRC), the parcel at a point (Consulta_RCCOOR,
  and the nearest ones when the point is on the street) and the parcels of a street number
  (ObtenerNumerero). It always answers HTTP 200: an error comes in `control.cuerr` and `lerr`
  (a list, or `{"err": [...]}` in ObtenerNumerero); when it is down it answers HTML.
- **Ayuntamiento de Madrid** (sigma.madrid.es, ArcGIS REST, EPSG:25830): the planning at a point
  (USOS_SUELO layer 3, «Urbanismo. Destino urbanístico del suelo»), the instrument in force
  (PLANEAMIENTO_URBANISTICO layer 3) and, for norma zonal 1 only, the Z of the 1997 plan of
  building conditions. ArcGIS reports an error as `{"error": ...}` with HTTP 200.
- **CartoCiudad** (IGN): the portals that match a typed address, with their parcel.

Every answer is turned into our own fields here (licence of the Catastro: only transformed
information, never its raw answer): nothing raw leaves this module or is kept. No retries inside
a request (a second try would break the time budget): a failure degrades the sheet.
"""

import asyncio
import re
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any, Literal

import httpx
from pydantic import HttpUrl, ValidationError
from pyproj import Transformer

from hi_contracts.pro.investors import NearbyParcel, ParcelCandidate
from hi_domain.geo.names import title_case
from hi_domain.parcels import (
    MADRID_CATASTRO_MUNICIPIO,
    MADRID_INE_MUNICIPIO,
    TypedAddress,
    Unit,
    UnitsSummary,
    catastro_number,
    classify_planning,
    is_vacant,
    normalize_rc,
    street_address,
    summarize_units,
)

CATASTRO = "https://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero"
CALLEJERO = f"{CATASTRO}/COVCCallejero.svc/json"
COORDENADAS = f"{CATASTRO}/COVCCoordenadas.svc/json"
SIGMA = "https://sigma.madrid.es/hosted/rest/services"
USOS_SUELO_SERVICE = f"{SIGMA}/DESARROLLO_URBANO_ACTUALIZADO/USOS_SUELO/MapServer"
USOS_SUELO = f"{USOS_SUELO_SERVICE}/3/query"
# D-252: the plan's buildable m² of the urban parcel, by its UBOV_ID (= CODIGO): table 4 for
# the principal use («Uso cualificado principal»), table 5 for the others
PLAN_USES = (f"{USOS_SUELO_SERVICE}/4/query", f"{USOS_SUELO_SERVICE}/5/query")
# Review of #109, R-01: tables 4 and 5 run after layer 3, so they get their own time, never past
# the sheet's deadline: out of time they degrade only the plan's uses, never the planning
PLAN_USES_TIMEOUT_S = 4.0
DEADLINE_MARGIN_S = 0.5
PLANEAMIENTO = f"{SIGMA}/DESARROLLO_URBANO_ACTUALIZADO/PLANEAMIENTO_URBANISTICO/MapServer/3/query"
CONDICIONES = f"{SIGMA}/PGOUM97/PG_CONDICIONES_EDIFICACION/MapServer/6/query"
CARTOCIUDAD = "https://www.cartociudad.es/geocoder/api/geocoder/candidates"

# Generic: who calls, never a person
USER_AGENT = "VidaFacil/0.1 (+https://vidafacil-madrid.vercel.app/desarrolladores)"
CONNECT_S = 3.0
CATASTRO_TIMEOUT = httpx.Timeout(5.0, connect=CONNECT_S)
SIGMA_TIMEOUT = httpx.Timeout(10.0, connect=CONNECT_S)  # cold peaks of 6-9 s (spike §3.6)
GEOCODER_TIMEOUT = httpx.Timeout(4.0, connect=CONNECT_S)
GEOCODER_LIMIT = 8  # candidates asked; at most MAX_CANDIDATES portals are returned
MAX_CANDIDATES = 5

Upstream = Literal["catastro", "planning", "geocoder"]

# Catastro codes (annex I of its web services document)
MALFORMED_CODES = frozenset({3, 4})  # 14, 18 or 20 positions; badly formed (control letters)
MISSING_CODES = frozenset({5, 9, 33, 43})  # no such parcel, reference, street or number
ON_THE_STREET = 16  # no parcel at those coordinates
NO_CARTOGRAPHY = 72  # a parcel without cartography: its sheet goes without a point


class UpstreamError(RuntimeError):
    """A source did not answer usable data: down, timed out, HTML or an ArcGIS error."""

    def __init__(self, source: Upstream, reason: str) -> None:
        super().__init__(f"{source}: {reason}")
        self.source = source


class CatastroAnswerError(RuntimeError):
    """The Catastro answered with one of its error codes."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"Catastro {code}: {message}")
        self.code = code


class OutOfMadridError(RuntimeError):
    """The parcel exists but is not in Madrid capital."""


SHAPE_ERRORS = (AttributeError, TypeError, ValueError, KeyError, IndexError)


@contextmanager
def parsing(source: "Upstream") -> Iterator[None]:
    """An answer of an unexpected shape (a list where an object was, an empty reference) is the
    source failing, as an HTML page is: the sheet degrades or serves its demo copy, never a 500."""
    try:
        yield
    except SHAPE_ERRORS as exc:
        raise UpstreamError(source, f"unexpected answer ({type(exc).__name__})") from exc


def https_url(value: Any) -> str | None:
    """A link a source gives, when it is a valid https address (else None, never an error)."""
    text = str(value or "").strip()
    if not text.startswith("https://") or re.search(r"\s", text):
        return None
    try:
        HttpUrl(text)
    except ValidationError:
        return None
    return text


_TO_LONLAT = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)
_TO_METRES = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)


def to_lonlat(x: float, y: float) -> tuple[float, float]:
    lon, lat = _TO_LONLAT.transform(x, y)
    return round(lon, 6), round(lat, 6)


def to_metres(lon: float, lat: float) -> tuple[float, float]:
    x, y = _TO_METRES.transform(lon, lat)
    return round(x, 2), round(y, 2)


def today() -> date:
    return datetime.now(UTC).date()


def new_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        timeout=CATASTRO_TIMEOUT,
        follow_redirects=True,
    )


class ClientHolder:
    """One shared client per event loop (keep-alive pays the TLS handshake once); a new loop
    (tests) gets a new client."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def get(self) -> httpx.AsyncClient:
        loop = asyncio.get_running_loop()
        if self._client is None or self._loop is not loop or self._client.is_closed:
            self._client = new_client()
            self._loop = loop
        return self._client


async def get_json(
    client: httpx.AsyncClient,
    source: Upstream,
    url: str,
    params: Mapping[str, str],
    timeout: httpx.Timeout,
) -> Any:
    try:
        response = await client.get(url, params=dict(params), timeout=timeout)
    except httpx.HTTPError as exc:
        raise UpstreamError(source, type(exc).__name__) from exc
    kind = response.headers.get("content-type", "")
    if response.status_code != 200 or "json" not in kind:
        raise UpstreamError(source, f"HTTP {response.status_code} {kind or 'no content-type'}")
    try:
        return response.json()
    except ValueError as exc:
        raise UpstreamError(source, "not JSON") from exc


# --- Catastro ---


def catastro_result(payload: Any) -> dict[str, Any]:
    """The body inside the root key («consulta_dnprcResult», «Consulta_RCCOORResult»…), with its
    error code raised as CatastroAnswerError."""
    with parsing("catastro"):
        return catastro_body(payload)


def catastro_body(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or len(payload) != 1:
        raise UpstreamError("catastro", "unexpected answer")
    result = next(iter(payload.values()))
    if not isinstance(result, dict):
        raise UpstreamError("catastro", "unexpected answer")
    for key in ("control", "bico", "lrcdnp", "coordenadas"):
        if result.get(key) is not None and not isinstance(result[key], dict):
            raise TypeError(key)  # an object of another shape: the source failing
    errors = result.get("lerr")
    if isinstance(errors, dict):  # ObtenerNumerero: {"err": [...]}
        errors = errors.get("err")
    if isinstance(errors, dict):
        errors = [errors]
    failed = int(catastro_number((result.get("control") or {}).get("cuerr")) or 0)
    if errors or failed:
        first = (errors or [{}])[0]
        code = int(catastro_number(first.get("cod")) or 0)
        raise CatastroAnswerError(code, str(first.get("des") or "").strip())
    return result


def pc_of(item: Mapping[str, Any]) -> str:
    pc = item.get("pc") or {}
    return normalize_rc(f"{pc.get('pc1', '')}{pc.get('pc2', '')}")


def lourb(dt: Mapping[str, Any]) -> Mapping[str, Any]:
    return ((dt.get("locs") or {}).get("lous") or {}).get("lourb") or {}


def address_of(dt: Mapping[str, Any]) -> tuple[str | None, str | None]:
    """The street address and postal code of a Catastro location, without floor or door."""
    urban = lourb(dt)
    street = urban.get("dir") or {}
    postal = str(urban.get("dp") or "").strip() or None
    text = street_address(street.get("tv"), street.get("nv"), street.get("pnp"), postal)
    return text, postal if postal and len(postal) == 5 else None


def in_madrid(dt: Mapping[str, Any]) -> bool:
    ine = str((dt.get("loine") or {}).get("cm") or "").strip()
    catastro = str(dt.get("cmc") or "").strip()
    return ine.lstrip("0") == MADRID_INE_MUNICIPIO and catastro == MADRID_CATASTRO_MUNICIPIO


def year_of(value: Any) -> int | None:
    number = catastro_number(value)
    return int(number) if number and 1000 <= number <= 2100 else None


@dataclass(frozen=True)
class CatastroParcel:
    """Our fields of a parcel, worked out from the Catastro's answers."""

    rc14: str
    address: str | None
    postal_code: str | None
    area_m2: float | None
    rustic: bool | None
    horizontal_division: bool
    units: UnitsSummary | None
    built_m2: float | None
    year_built: int | None
    current_use: str | None
    is_vacant: bool | None
    official_url: str | None
    x: float | None
    y: float | None
    observed_at: date


def finca_of(result: Mapping[str, Any]) -> Mapping[str, Any]:
    return (result.get("bico") or {}).get("finca") or {}


def official_url(finca: Mapping[str, Any]) -> str | None:
    return https_url((finca.get("infgraf") or {}).get("igraf"))


def single_parcel(rc14: str, result: Mapping[str, Any]) -> dict[str, Any]:
    """A parcel with one unit (`bico`)."""
    bico = result.get("bico") or {}
    bi = bico.get("bi") or {}
    dt = bi.get("dt") or {}
    if not in_madrid(dt):
        raise OutOfMadridError(rc14)
    debi = bi.get("debi") or {}
    finca = finca_of(result)
    use = str(debi.get("luso") or "").strip() or None
    built = catastro_number(debi.get("sfc"))
    address, postal = address_of(dt)
    return {
        "address": address,
        "postal_code": postal,
        "area_m2": catastro_number((finca.get("dff") or {}).get("ss")),
        "rustic": rustic_of(bi),
        "horizontal_division": "division horizontal" in str(finca.get("ltp") or "").lower(),
        "units": None,
        "built_m2": built,
        "year_built": year_of(debi.get("ant")),
        "current_use": use,
        "is_vacant": is_vacant(use, built, bool(bico.get("lcons"))),
        "official_url": official_url(finca),
    }


def rustic_of(bi: Mapping[str, Any]) -> bool | None:
    kind = str((bi.get("idbi") or {}).get("cn") or "").strip().upper()
    return {"UR": False, "RU": True}.get(kind)


def unit_rc20(item: Mapping[str, Any]) -> str:
    rc = item.get("rc") or {}
    return "".join(str(rc.get(k, "")) for k in ("pc1", "pc2", "car", "cc1", "cc2"))


def divided_parcel(units: list[Mapping[str, Any]]) -> tuple[dict[str, Any], str]:
    """A building in horizontal division: its units summarised by use (never one by one) and
    the reference of one unit, to ask for the parcel's area."""
    first = units[0].get("dt") or {}
    if not in_madrid(first):
        raise OutOfMadridError("divided parcel")
    summary = summarize_units(
        Unit(
            str((u.get("debi") or {}).get("luso") or "").strip() or None,
            catastro_number((u.get("debi") or {}).get("sfc")),
            year_of((u.get("debi") or {}).get("ant")),
        )
        for u in units
    )
    address, postal = address_of(first)
    fields = {
        "address": address,
        "postal_code": postal,
        "horizontal_division": True,
        "units": summary,
        "built_m2": summary.built_m2,
        "year_built": summary.year_built,
        "current_use": summary.main_use,
        "is_vacant": False,
    }
    return fields, unit_rc20(units[0])


async def dnprc(client: httpx.AsyncClient, rc: str) -> dict[str, Any]:
    payload = await get_json(
        client, "catastro", f"{CALLEJERO}/Consulta_DNPRC", {"RefCat": rc}, CATASTRO_TIMEOUT
    )
    return catastro_result(payload)


async def reference_point(client: httpx.AsyncClient, rc14: str) -> tuple[float, float] | None:
    """The parcel's reference point (EPSG:25830): inside its polygon, as the WFS gives it."""
    params = {"Provincia": "", "Municipio": "", "SRS": "EPSG:25830", "RefCat": rc14}
    payload = await get_json(
        client, "catastro", f"{COORDENADAS}/Consulta_CPMRC", params, CATASTRO_TIMEOUT
    )
    try:
        result = catastro_result(payload)
    except CatastroAnswerError as exc:
        if exc.code == NO_CARTOGRAPHY:  # the sheet goes without a point (and is not cached)
            return None
        raise UpstreamError("catastro", f"reference point: code {exc.code}") from exc
    with parsing("catastro"):
        coords = (result.get("coordenadas") or {}).get("coord") or []
        geo = (coords[0] if coords else {}).get("geo") or {}
        x, y = catastro_number(geo.get("xcen")), catastro_number(geo.get("ycen"))
    return (x, y) if x and y else None


async def fetch_parcel(client: httpx.AsyncClient, rc14: str) -> CatastroParcel:
    """The parcel of a reference: its data and its reference point, in parallel; a building in
    horizontal division asks once more, for one unit, to get the parcel's area and link."""
    result, point = await asyncio.gather(dnprc(client, rc14), reference_point(client, rc14))
    with parsing("catastro"):
        units = (result.get("lrcdnp") or {}).get("rcdnp") or []
        if units:
            fields, rc20 = divided_parcel(units)
        elif result.get("bico"):
            fields, rc20 = single_parcel(rc14, result), None
        else:
            raise CatastroAnswerError(5, "no parcel in the answer")
    if rc20 is not None:
        unit = await dnprc(client, rc20)
        with parsing("catastro"):
            finca = finca_of(unit)
            fields |= {
                "area_m2": catastro_number((finca.get("dff") or {}).get("ss")),
                "rustic": rustic_of((unit.get("bico") or {}).get("bi") or {}),
                "official_url": official_url(finca),
            }
    x, y = point or (None, None)
    return CatastroParcel(rc14=rc14, x=x, y=y, observed_at=today(), **fields)


async def parcel_at(client: httpx.AsyncClient, lat: float, lon: float) -> str:
    """The parcel at a point; CatastroAnswerError(16) when the point is on the street."""
    params = {"CoorX": f"{lon:.6f}", "CoorY": f"{lat:.6f}", "SRS": "EPSG:4326"}
    payload = await get_json(
        client, "catastro", f"{COORDENADAS}/Consulta_RCCOOR", params, CATASTRO_TIMEOUT
    )
    result = catastro_result(payload)
    with parsing("catastro"):
        coords = (result.get("coordenadas") or {}).get("coord") or []
        if not coords:
            raise CatastroAnswerError(ON_THE_STREET, "no parcel at the point")
        return pc_of(coords[0])


async def parcels_near(client: httpx.AsyncClient, lat: float, lon: float) -> list[NearbyParcel]:
    """The parcels nearest to a point on the street, nearest first (at most 3)."""
    params = {"CoorX": f"{lon:.6f}", "CoorY": f"{lat:.6f}", "SRS": "EPSG:4326"}
    url = f"{COORDENADAS}/Consulta_RCCOOR_Distancia"
    result = catastro_result(await get_json(client, "catastro", url, params, CATASTRO_TIMEOUT))
    nearby = []
    with parsing("catastro"):
        groups = (result.get("coordenadas_distancias") or {}).get("coordd") or []
        items = (groups[0] if groups else {}).get("lpcd") or []
        for item in items:
            try:
                rc14 = pc_of(item)
            except ValueError:
                continue
            distance = catastro_number(item.get("dis"))
            address = re.sub(r"\s+", " ", str(item.get("ldt") or "")).strip() or None
            nearby.append(NearbyParcel(rc14=rc14, address=address, distance_m=distance))
    return sorted(nearby, key=lambda p: p.distance_m or 0)[:3]


async def parcels_at_number(client: httpx.AsyncClient, address: TypedAddress) -> list[str]:
    """The parcels of a street number in Madrid, from the Catastro's street index."""
    params = {
        "Provincia": "MADRID",
        "Municipio": "MADRID",
        "TipoVia": address.street_type,
        "NomVia": address.street,
        "Numero": str(address.number),
    }
    url = f"{CALLEJERO}/ObtenerNumerero"
    result = catastro_result(await get_json(client, "catastro", url, params, CATASTRO_TIMEOUT))
    found = []
    with parsing("catastro"):
        for item in result.get("nump") or []:
            number = str((item.get("num") or {}).get("pnp") or "").strip().lstrip("0")
            if number == str(address.number):
                found.append(pc_of(item))
    return list(dict.fromkeys(found))


# --- Ayuntamiento de Madrid (sigma) ---


@dataclass(frozen=True)
class PlanRow:
    use: str | None
    value: float | None
    unit: str | None
    principal: bool


@dataclass(frozen=True)
class PlanningRecord:
    """Our fields of the planning at a point, and which secondary layer did not answer."""

    code: str
    name: str | None
    use: str | None
    urban_parcel: str | None
    zone_name: str | None
    figure: str | None
    instrument_name: str | None
    file_number: str | None
    instrument_url: str | None
    coef_z: float | None
    observed_at: date
    instrument_failed: bool = False  # PLANEAMIENTO_URBANISTICO did not answer
    z_failed: bool = False  # the 1997 plan of building conditions did not answer (NZ 1 only)
    urban_parcel_area_m2: float | None = None
    # D-252: (use, figure, unit, principal) of tables 4 and 5; None when they did not answer
    plan_rows: tuple[PlanRow, ...] | None = ()
    uses_failed: bool = False

    @property
    def complete(self) -> bool:
        return not (self.instrument_failed or self.z_failed or self.uses_failed)


def clean(value: Any) -> str | None:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text or None


async def arcgis_point(
    client: httpx.AsyncClient, url: str, x: float, y: float, fields: str
) -> dict[str, Any] | None:
    """The attributes of the first feature at a point (EPSG:25830); None when there is none."""
    params = {
        "geometry": f"{x},{y}",
        "geometryType": "esriGeometryPoint",
        "inSR": "25830",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": fields,
        "returnGeometry": "false",
        "f": "json",
    }
    payload = await get_json(client, "planning", url, params, SIGMA_TIMEOUT)
    if not isinstance(payload, dict) or "error" in payload:
        raise UpstreamError("planning", "ArcGIS error")
    with parsing("planning"):
        features = payload.get("features") or []
        attributes = (features[0] or {}).get("attributes") if features else None
        if attributes is not None and not isinstance(attributes, dict):
            raise TypeError("attributes")
        return attributes


async def arcgis_rows(
    client: httpx.AsyncClient, url: str, where: str, fields: str
) -> list[dict[str, Any]]:
    """The attributes of every row of a table that match `where`."""
    params = {"where": where, "outFields": fields, "returnGeometry": "false", "f": "json"}
    payload = await get_json(client, "planning", url, params, SIGMA_TIMEOUT)
    if not isinstance(payload, dict) or "error" in payload:
        raise UpstreamError("planning", "ArcGIS error")
    with parsing("planning"):
        rows = [(f or {}).get("attributes") for f in payload.get("features") or []]
        if any(not isinstance(r, dict) for r in rows):
            raise TypeError("attributes")
        return [r for r in rows if isinstance(r, dict)]


async def plan_rows(client: httpx.AsyncClient, urban_parcel_id: int) -> tuple[PlanRow, ...]:
    """D-252: tables 4 and 5 of the urban parcel, in parallel."""
    where = f"CODIGO={int(urban_parcel_id)}"
    principal, others = await asyncio.gather(
        *(arcgis_rows(client, url, where, "USO,EDIFICABIL,UNIDAD") for url in PLAN_USES)
    )
    with parsing("planning"):
        return tuple(
            PlanRow(
                clean(r.get("USO")),
                catastro_number(r.get("EDIFICABIL")),
                clean(r.get("UNIDAD")),
                main,
            )
            for rows, main in ((principal, True), (others, False))
            for r in rows
        )


FAILED = object()


async def optional(task: Any) -> Any:
    """A secondary layer: its failure (FAILED) leaves its fields empty, not the whole planning."""
    try:
        return await task
    except UpstreamError:
        return FAILED


def needs_z(code: str) -> bool:
    _, zone = classify_planning(code)
    return zone is not None and zone.nz == 1 and (zone.grado or 0) in {1, 2, 3, 4}


def instrument_url(value: Any) -> str | None:
    return https_url(clean(value))


async def bounded_plan_rows(
    client: httpx.AsyncClient, urban_parcel_id: int, deadline: float | None
) -> tuple[PlanRow, ...]:
    """Tables 4 and 5 within PLAN_USES_TIMEOUT_S and before the sheet's deadline; out of time,
    UpstreamError (so FAILED: only `plan_uses` is degraded)."""
    budget = PLAN_USES_TIMEOUT_S
    if deadline is not None:
        budget = min(budget, deadline - asyncio.get_running_loop().time() - DEADLINE_MARGIN_S)
    if budget <= 0:
        raise UpstreamError("planning", "no time left for the plan's uses")
    try:
        async with asyncio.timeout(budget):
            return await plan_rows(client, urban_parcel_id)
    except TimeoutError as exc:
        raise UpstreamError("planning", "the plan's uses out of time") from exc


def urban_parcel_id(uses: Mapping[str, Any]) -> int:
    """The UBOV_ID of the urban parcel; a planning without it is the layer failing (R-07)."""
    with parsing("planning"):
        value = catastro_number(uses.get("UBOV_ID"))
        if value is None:
            raise ValueError("UBOV_ID")
        return int(value)


async def fetch_planning(
    client: httpx.AsyncClient, x: float, y: float, deadline: float | None = None
) -> PlanningRecord | None:
    """The planning at the parcel's reference point, its three layers in parallel; None when no
    layer covers it. The Z of norma zonal 1 is asked always (one cheap call) and read only there.
    Tables 4 and 5 follow layer 3 (they need its UBOV_ID), within their own time."""

    async def uses_and_rows() -> tuple[dict[str, Any] | None, Any]:
        uses = await arcgis_point(
            client,
            USOS_SUELO,
            x,
            y,
            "AMB_TX_ETIQ,AMB_TX_DENOM,ZURV_TX_NOMBRE,UBOV_TX_ETIQ,USP_TX_DENOM,UBOV_ID,SHAPE.STArea()",
        )
        if uses is None or clean(uses.get("AMB_TX_ETIQ")) is None:
            return uses, ()
        try:
            ubov = urban_parcel_id(uses)
        except UpstreamError:
            return uses, FAILED
        return uses, await optional(bounded_plan_rows(client, ubov, deadline))

    (uses, rows), instrument, conditions = await asyncio.gather(
        uses_and_rows(),
        optional(
            arcgis_point(
                client, PLANEAMIENTO, x, y, "EXP_TX_NUMERO,EXP_TX_DENOM,FIG_TX_ETIQ,ENLACE"
            )
        ),
        optional(arcgis_point(client, CONDICIONES, x, y, "COEF_Z")),
    )
    code = clean((uses or {}).get("AMB_TX_ETIQ"))
    if uses is None or code is None:
        return None
    z_layer = needs_z(code)
    with parsing("planning"):
        found = {} if instrument is FAILED or instrument is None else instrument
        z = {} if conditions is FAILED or conditions is None or not z_layer else conditions
        return PlanningRecord(
            code=code,
            name=clean(uses.get("AMB_TX_DENOM")),
            use=clean(uses.get("USP_TX_DENOM")),
            urban_parcel=clean(uses.get("UBOV_TX_ETIQ")),
            zone_name=clean(uses.get("ZURV_TX_NOMBRE")),
            figure=clean(found.get("FIG_TX_ETIQ")),
            instrument_name=clean(found.get("EXP_TX_DENOM")),
            file_number=clean(found.get("EXP_TX_NUMERO")),
            instrument_url=instrument_url(found.get("ENLACE")),
            coef_z=catastro_number(z.get("COEF_Z")),
            observed_at=today(),
            instrument_failed=instrument is FAILED,
            z_failed=z_layer and conditions is FAILED,
            urban_parcel_area_m2=catastro_number(uses.get("SHAPE.STArea()")),
            plan_rows=None if rows is FAILED else rows,
            uses_failed=rows is FAILED,
        )


# --- CartoCiudad ---


@dataclass(frozen=True)
class Candidate:
    """A portal that matches a typed address, with its number to compare with the typed one."""

    candidate: ParcelCandidate
    number: int | None


@dataclass(frozen=True)
class Candidates:
    portals: tuple[Candidate, ...]
    streets_only: bool


def portal_address(text: str) -> str:
    """«CALLE MAYOR 61, Madrid» -> «Calle Mayor 61, Madrid»."""
    street, _, rest = text.partition(",")
    return f"{title_case(street.strip())}{',' + rest if rest else ''}".strip()


def as_candidate(item: Mapping[str, Any]) -> Candidate | None:
    if item.get("type") != "portal" or str(item.get("muniCode") or "") != "28079":
        return None
    try:
        rc14 = normalize_rc(str(item.get("refCatastral") or ""))
    except ValueError:
        return None
    postal = str(item.get("postalCode") or "").strip()
    lat, lon = catastro_number(item.get("lat")), catastro_number(item.get("lng"))
    number = catastro_number(item.get("portalNumber"))
    return Candidate(
        ParcelCandidate(
            address=portal_address(str(item.get("address") or rc14)),
            postal_code=postal if re.fullmatch(r"\d{5}", postal) else None,
            rc14=rc14,
            lat=round(lat, 6) if lat else None,
            lon=round(lon, 6) if lon else None,
        ),
        int(number) if number is not None else None,
    )


async def geocode(client: httpx.AsyncClient, query: str) -> Candidates:
    """The portals of Madrid capital that match the text, with their parcel (never picked here)."""
    params = {"q": query, "limit": str(GEOCODER_LIMIT), "municipio_filter": "Madrid"}
    payload = await get_json(client, "geocoder", CARTOCIUDAD, params, GEOCODER_TIMEOUT)
    if not isinstance(payload, list):  # its answer is a list, even an empty one
        raise UpstreamError("geocoder", "unexpected answer")
    with parsing("geocoder"):
        items = [i for i in payload if isinstance(i, dict)]
        portals = [c for item in items if (c := as_candidate(item))]
        unique = list({c.candidate.rc14 + c.candidate.address: c for c in portals}.values())
        streets = any(i.get("type") == "callejero" for i in items)
    return Candidates(tuple(unique[:MAX_CANDIDATES]), streets_only=streets and not unique)
