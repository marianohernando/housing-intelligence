"""Write the data the investor version reads into the API image (D-248), as
scripts/export_search_scope.py does for the search scope: the YAML files are the versioned
source; the API image only carries the Python packages.

- hi_domain/viability_data.py from data/catalog/manual/pem_visados_cm.yaml (the PEM of the
  permits, written by scripts/pem_visados_cm.py) and costes_referencia_construccion.yaml (D-252:
  the CRG of the Comunidad de Madrid, whose midpoint is the calculator's PEM, and the press
  figure of Sociedad de Tasación).
- hi_domain/investors_pilot.py from data/catalog/manual/inversores_barrios_m40.yaml (D-247, the
  pilot barrios inside the M-40, written by line A's scripts/m40_barrios.py).
- hi_domain/parcel_data.py from data/catalog/manual/veda_parcelas.yaml and
  portal_suelo_madrid_parcelas.yaml (D-250: the parcels of Madrid with official buildable m², by
  cadastral reference, written by scripts/buildable_parcels.py).
- hi_domain/plan_uses_data.py from data/catalog/manual/usos_suelo_edificabilidad.csv and
  usos_suelo_parcelas.csv (D-252c: tables 4 and 5 of USOS_SUELO, written by
  scripts/usos_suelo_tablas.py).
- hi_domain/ambit_status.py from data/catalog/manual/pgoum_ambitos_estado.yaml (D-252: the
  four phases of each planning area and its VEDA situation, written by
  scripts/pgoum_ambitos_estado.py).
- apps/web/src/lib/investorMethod.ts (D-251, D-252): the figures «Cómo lo calculamos» gives for the
  investor version, from the same tables and the code's constants (hi_domain.viability,
  hi_domain.zonal_norms, hi_domain.parcels), so the page never types a number of its own.

Usage: uv run python scripts/export_investor_data.py [--check]
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from hi_contracts.pro.investors import UseClass
from hi_domain import viability as v
from hi_domain.parcels import DONE_PHASES, LOOKUP_BUDGET_S, PENDING_STAGES, classify_use
from hi_domain.supplies import BASIC_KW, SIMULTANEITY, STEP, TRANSFORMER_KW
from hi_domain.zonal_norms import (
    NNUU_CITATION,
    NZ1_FACTORS,
    NZ8_G6,
    NZ8_G6_EXCESS,
    NZ8_G6_LIMIT_M2,
    RULES,
)

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "data" / "catalog" / "manual"
DOMAIN = ROOT / "packages" / "domain" / "src" / "hi_domain"
PEM_SOURCE = MANUAL / "pem_visados_cm.yaml"
COSTS_SOURCE = MANUAL / "costes_referencia_construccion.yaml"
PEM_TARGET = DOMAIN / "viability_data.py"
PILOT_SOURCE = MANUAL / "inversores_barrios_m40.yaml"
PILOT_TARGET = DOMAIN / "investors_pilot.py"
VEDA_SOURCE = MANUAL / "veda_parcelas.yaml"
PORTAL_SOURCE = MANUAL / "portal_suelo_madrid_parcelas.yaml"
PARCELS_TARGET = DOMAIN / "parcel_data.py"
AMBITS_SOURCE = MANUAL / "pgoum_ambitos_estado.yaml"
PLAN_FIGURES_SOURCE = MANUAL / "usos_suelo_edificabilidad.csv"
PLAN_PARCELS_SOURCE = MANUAL / "usos_suelo_parcelas.csv"
PLAN_USE_NAMES_SOURCE = MANUAL / "usos_suelo_usos.csv"
PLAN_USES_TARGET = DOMAIN / "plan_uses_data.py"
AMBITS_TARGET = DOMAIN / "ambit_status.py"
METHOD_TARGET = ROOT / "apps" / "web" / "src" / "lib" / "investorMethod.ts"


def q(value: object) -> str:
    """A string literal as ruff formats it (double quotes)."""
    return json.dumps(value, ensure_ascii=False)


def midpoint(low: int, high: int) -> int:
    """The middle of a range, half up: 871–1.064 → 968."""
    return (low + high + 1) // 2


def render_costs(costs: dict[str, Any]) -> list[str]:
    crg, st = costs["crg"], costs["st"]
    types = crg["types"]
    default = types[crg["default"]]
    lines = [
        "",
        "# D-252: public references of the construction cost (costes_referencia_construccion).",
        "# The calculator's PEM is the midpoint of the CRG of the Comunidad de Madrid for its",
        "# default type in area 1 (Madrid); the PEM of the permits above is the low reference.",
        f"CRG_YEAR = {crg['updated_year']}",
        f"CRG_URL = {q(crg['url'])}",
        f"CRG_AREA = {crg['area']}",
        f"CRG_DEFAULT_TYPE = {q(crg['default'])}",
    ]
    for key, row in types.items():
        name = key.upper()
        lines += [f"CRG_{name}_LOW = {row['low']}", f"CRG_{name}_HIGH = {row['high']}"]
    lines += [
        f"REFERENCE_PEM_EUR_M2 = {midpoint(default['low'], default['high'])}",
        f"ST_EUR_M2 = {st['eur_m2']}",
        f"ST_ABOVE_GROUND_EUR_M2 = {st['above_ground_eur_m2']}",
        f"ST_BELOW_GROUND_EUR_M2 = {st['below_ground_eur_m2']}",
        f"ST_PERIOD = {q(st['period'])}",
        f"ST_URL = {q(st['url'])}",
        "",
    ]
    return lines


def render_pem(spec: dict[str, Any], costs: dict[str, Any]) -> str:
    default = spec["default"]
    entry = next(e for e in spec["series"] if e["year"] == default["year"])
    figures = entry[default["kind"]]
    previous = [e for e in spec["series"] if e["year"] == default["year"] - 1]
    previous_m2 = previous[0][default["kind"]]["pem_eur_m2"] if previous else None
    lines = [
        '"""Generated by scripts/export_investor_data.py from',
        "data/catalog/manual/pem_visados_cm.yaml: do not edit by hand.",
        "",
        f"Source: {spec['publisher']},",
        f"dataset {spec['portal_id']} ({spec['url']}),",
        f"{spec['source']} Read on {spec['consulted']}.",
        '"""',
        "",
        f"PEM_EUR_M2 = {figures['pem_eur_m2']}",
        f"PEM_YEAR = {default['year']}",
        f"PEM_PREVIOUS_EUR_M2 = {previous_m2}",
        f"PEM_KIND = {q(default['kind'])}",
        f"PEM_BUDGET_KEUR = {figures['pem_miles_eur']}",
        f"PEM_AREA_M2 = {figures['superficie_m2']}",
        f"PEM_PROVISIONAL = {figures['provisional']}",
        f"PEM_DATASET_URL = {q(spec['url'])}",
        f"PEM_CONSULTED = {q(spec['consulted'])}",
        f"PEM_UPDATED = {q(spec['updated'])}",
        f"PEM_SHA256 = {q(spec['sha256'])}",
        *render_costs(costs),
    ]
    return "\n".join(lines)


def pilot_entries(spec: dict[str, Any]) -> list[tuple[str, str, str]]:
    """(code, name, district) of each pilot barrio, by code. A repeated code stops it."""
    entries = [(str(b["code"]), str(b["name"]), str(b["distrito"])) for b in spec["barrios"]]
    codes = [code for code, _, _ in entries]
    if len(codes) != len(set(codes)):
        raise ValueError("a pilot barrio is listed twice")
    return sorted(entries)


def render_pilot(spec: dict[str, Any]) -> str:
    lines = [
        '"""Generated by scripts/export_investor_data.py from',
        "data/catalog/manual/inversores_barrios_m40.yaml (D-247): do not edit by hand.",
        "",
        f"Source: {spec.get('title', 'barrios piloto')}, read on {spec.get('consulted')}.",
        '"""',
        "",
        "# (barrio code, name, district): the investor pilot, Madrid inside the M-40",
        "PILOT_BARRIOS: tuple[tuple[str, str, str], ...] = (",
        *(f"    ({q(c)}, {q(n)}, {q(d)})," for c, n, d in pilot_entries(spec)),
        ")",
        f"PILOT_CONSULTED = {q(str(spec.get('consulted')))}",
        "",
    ]
    return "\n".join(lines)


def parcel_table(name: str, spec: dict[str, Any]) -> list[str]:
    """One table of parcels: (buildable m², area m², planning, use) by rc14, with its source."""
    rows = sorted(spec["parcels"], key=lambda p: p["rc14"])
    if len({p["rc14"] for p in rows}) != len(rows):
        raise ValueError(f"{name}: a parcel is listed twice")
    return [
        f"{name}_DATASET = {q(spec['dataset_id'])}",
        f"{name}_SOURCE = {q(spec['source_text'])}",
        f"{name}_URL = {q(spec['url'])}",
        f"{name}_CONSULTED = {q(str(spec['consulted']))}",
        f"{name}_PARCELS: dict[str, Parcel] = {{",
        *(
            f"    {q(p['rc14'])}: ({p['buildable_m2']}, {p.get('area_m2')}, "
            f"{literal(p.get('planning'))}, {literal(p.get('use'))}),"
            for p in rows
        ),
        "}",
    ]


def literal(value: str | None) -> str:
    return "None" if value is None else q(value)


def render_parcels(veda: dict[str, Any], portal: dict[str, Any]) -> str:
    lines = [
        "# ruff: noqa: E501",
        '"""Generated by scripts/export_investor_data.py from',
        "data/catalog/manual/veda_parcelas.yaml and portal_suelo_madrid_parcelas.yaml (D-250):",
        "do not edit by hand.",
        "",
        "The parcels of Madrid capital with official buildable m², by cadastral reference (rc14).",
        '"""',
        "",
        "# fmt: off",
        "# (buildable m², area m², planning area or parcel label, use as the source writes it)",
        "Parcel = tuple[float, float | None, str | None, str | None]",
        "",
        *parcel_table("VEDA", veda),
        "",
        *parcel_table("PORTAL", portal),
        "",
        "# D-252: the Portal del Suelo's own reference of each parcel (its land item in a barrio)",
        "PORTAL_REFS: dict[str, str] = {",
        *(f"    {q(x['rc14'])}: {q(x['ref'])}," for x in portal["parcels"] if x.get("ref")),
        "}",
        "",
    ]
    return "\n".join(lines)


def render_ambits(spec: dict[str, Any]) -> str:
    dev, veda = spec["development"], spec["veda"]
    lines = [
        "# ruff: noqa: E501",
        '"""Generated by scripts/export_investor_data.py from',
        "data/catalog/manual/pgoum_ambitos_estado.yaml (D-252): do not edit by hand.",
        "",
        "The state of each planning area (ámbito) of the Plan General: its four phases as",
        f"the Ayuntamiento publishes them (datos.madrid.es {dev['dataset']}, {spec['license']})",
        f"and its situation in VEDA ({veda['dataset']}), by the code the Ayuntamiento gives it.",
        '"""',
        "",
        "# fmt: off",
        "# ((planeamiento, gestión, proyecto de urbanización, obras de urbanización) or None,",
        "#  VEDA situation or None)",
        "Phases = tuple[str, str, str, str]",
        "Ambit = tuple[Phases | None, str | None]",
        "",
        f"AS_OF = {q(dev['as_of'])}",
        f"DEVELOPMENT_URL = {q(dev['url'])}",
        f"VEDA_URL = {q(veda['url'])}",
        "AMBITS: dict[str, Ambit] = {",
    ]
    for entry in spec["ambits"]:
        phases = entry.get("phases")
        shown = "None" if phases is None else "(" + ", ".join(q(x) for x in phases) + ")"
        stage = q(entry["veda"]) if entry.get("veda") else "None"
        lines.append(f"    {q(entry['code'])}: ({shown}, {stage}),")
    lines += ["}", ""]
    return "\n".join(lines)


def csv_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    """The comment lines (#) and the rows of a versioned CSV, its header dropped."""
    lines = path.read_text(encoding="utf-8").splitlines()
    comments = [line[2:] for line in lines if line.startswith("#")]
    rows = list(csv.reader(line for line in lines if not line.startswith("#")))
    return comments, rows[1:]


def render_plan_uses(figures: Path, parcels: Path, uses_file: Path) -> str:
    """D-252c: tables 4 and 5 of USOS_SUELO by CODIGO, compact (uses and units as indexes),
    and the principal use of every urban parcel of table 4 as runs of the same use."""
    comments, rows = csv_rows(figures)
    day = next(c for c in comments if "leída el" in c).split("leída el ")[1].split(" ")[0]
    _, indexed = csv_rows(uses_file)
    uses = [use for _, use in indexed]
    units = sorted({r[4] for r in rows})
    by_code: dict[int, list[str]] = {}
    for code, principal, use, value, unit in rows:
        entry = f"({uses.index(use)}, {value}, {units.index(unit)}, {principal == '1'})"
        by_code.setdefault(int(code), []).append(entry)
    _, runs = csv_rows(parcels)
    deltas, last = [], -1  # (gap from the previous run, span, use): small numbers
    for low, high, use in ((int(a), int(b), int(u)) for a, b, u in runs):
        deltas.append(f"({low - last - 1}, {high - low}, {use})")
        last = high
    packed = [", ".join(deltas[i : i + 10]) for i in range(0, len(deltas), 10)]
    lines = [
        "# ruff: noqa: E501",
        '"""Generated by scripts/export_investor_data.py from',
        "data/catalog/manual/usos_suelo_edificabilidad.csv, usos_suelo_parcelas.csv and",
        "usos_suelo_usos.csv (D-252c): do not edit by hand.",
        "",
        "The plan's buildable m² by use of the urban parcels of Madrid (USOS_SUELO, tables 4",
        "and 5; Ayuntamiento de Madrid, datos.madrid.es 300744, CC BY 4.0), by CODIGO (UBOV_ID).",
        '"""',
        "",
        "# fmt: off",
        f"AS_OF = {q(day)}",
        'URL = "https://datos.madrid.es/dataset/300744-0-usos-suelo-urbanismo"',
        f"USES: tuple[str, ...] = ({', '.join(q(u) for u in uses)},)",
        f"UNITS: tuple[str, ...] = ({', '.join(q(u) for u in units)},)",
        "# CODIGO: ((use index, figure, unit index, principal), ...): the rows with a figure",
        "ROWS: dict[int, tuple[tuple[int, float, int, bool], ...]] = {",
        *(f"    {code}: ({', '.join(e)},)," for code, e in sorted(by_code.items())),
        "}",
        "# Table 4 as runs of consecutive CODIGO with the same principal use, each one (gap from",
        "# the previous run, span, use index): every urban parcel there has its principal use,",
        "# most of them without a figure. hi_domain.parcels decodes it once.",
        "TABLE_4: tuple[tuple[int, int, int], ...] = (",
        *(f"    {line}," for line in packed),
        ")",
        "",
    ]
    return "\n".join(lines)


def pct(share: float) -> float:
    return round(share * 100, 2)


def by_use(parcels: list[dict[str, Any]]) -> dict[str, int]:
    """How many parcels a source publishes of each use (D-252): one figure with one use each."""
    counts = Counter(classify_use(p.get("use"))[0] for p in parcels)
    return {kind.value: counts[kind] for kind in UseClass if counts[kind]}


def cost_references(pem: dict[str, Any], costs: dict[str, Any]) -> dict[str, Any]:
    """D-252: the three references of «De dónde sale el coste y cuánto varía»."""
    crg, st = costs["crg"], costs["st"]
    default = crg["types"][crg["default"]]
    return {
        "crg": {
            "year": crg["updated_year"],
            "url": crg["url"],
            "area": crg["area"],
            "defaultPem": midpoint(default["low"], default["high"]),
            "types": [
                {"key": k, "label": t["label"], "low": t["low"], "high": t["high"]}
                for k, t in crg["types"].items()
            ],
        },
        "st": {
            "eurM2": st["eur_m2"],
            "aboveGround": st["above_ground_eur_m2"],
            "belowGround": st["below_ground_eur_m2"],
            "period": st["period"],
            "territory": st["territory"],
            "url": st["url"],
        },
    }


def method_figures(
    pem: dict[str, Any],
    pilot: dict[str, Any],
    veda: dict[str, Any],
    portal: dict[str, Any],
    costs: dict[str, Any],
) -> dict[str, Any]:
    default = pem["default"]
    entry = next(e for e in pem["series"] if e["year"] == default["year"])
    rules = [r for r in RULES.values() if r.coefficients]
    return {
        "pilotBarrios": len(pilot["barrios"]),
        "vedaParcels": len(veda["parcels"]),
        "vedaByUse": by_use(veda["parcels"]),
        "vedaSource": veda["source_text"],
        "portalParcels": len(portal["parcels"]),
        "portalByUse": by_use(portal["parcels"]),
        "portalSource": portal["source_text"],
        "pem": {
            "eurM2": entry[default["kind"]]["pem_eur_m2"],
            "year": default["year"],
            "url": pem["url"],
        },
        "costReferences": cost_references(pem, costs),
        "costCoefficient": v.COST_COEFFICIENT,
        "icioPct": pct(v.ICIO_RATE),
        "appraisalMinMarginPct": pct(v.APPRAISAL_MIN_MARGIN),
        "costParts": [{"label": p.label, "pct": pct(p.share)} for p in v.COST_PARTS],
        "salesCostsPct": pct(v.SALES_COSTS_SHARE),
        "salesCostParts": [{"label": p.label, "pct": pct(p.share)} for p in v.SALES_COST_PARTS],
        "targetMarginPct": pct(v.TARGET_MARGIN),
        "adjustFloorPct": pct(v.ADJUST_FLOOR),
        "scenarios": [
            {
                "key": s.key,
                "label": s.label,
                "pricePct": pct(s.price_factor - 1),
                "costPct": pct(s.cost_factor - 1),
            }
            for s in v.SCENARIOS
        ],
        "homeM2": v.HOME_M2,
        "ltvPct": pct(v.LOAN_TO_VALUE),
        "loanYears": v.LOAN_YEARS,
        "loanRatePct": pct(v.LOAN_RATE),
        "effortThresholdPct": pct(v.EFFORT_THRESHOLD),
        "nnuuCitation": NNUU_CITATION,
        "zonalNorms": [
            {
                "nz": r.nz,
                "name": r.name,
                "article": r.article.number,
                "url": r.article.url,
                "coefficients": [
                    {"grado": g, "value": c} for g, c in sorted(r.coefficients.items())
                ],
            }
            for r in rules
        ],
        # The grado whose coefficient changes past a parcel size (art. 8.8.9.1.f)
        "split": {
            "nz": NZ8_G6[0],
            "grado": NZ8_G6[1],
            "limitM2": NZ8_G6_LIMIT_M2,
            "excess": NZ8_G6_EXCESS,
        },
        # The normas zonales whose text fixes no coefficient: the person types the m²
        "withoutCoefficient": [r.nz for r in RULES.values() if not r.coefficients and r.nz != 1],
        "nz1": {
            "article": RULES[1].article.number,
            "url": RULES[1].article.url,
            "factors": [{"grado": g, "value": c} for g, c in sorted(NZ1_FACTORS.items())],
        },
        "lookupBudgetS": LOOKUP_BUDGET_S,
        # The finished states of an area's works, as the domain reads them (review of #110, R-09)
        "doneWorks": sorted(DONE_PHASES),
        # VEDA's situations of an unfinished area, as AmbitState.pending reads them (F14, R-03)
        "pendingStages": sorted(PENDING_STAGES),
        # D-253: the power estimate (ITC-BT-10) and the transformer threshold (RD 1048/2013)
        "supplies": {
            "kwPerHome": BASIC_KW,
            "transformerKw": TRANSFORMER_KW,
            "simultaneityOne": SIMULTANEITY[1],
            "simultaneityMax": SIMULTANEITY[max(SIMULTANEITY)],
            "tableHomes": max(SIMULTANEITY),
            "stepPastTable": STEP,
        },
    }


def render_method(figures: dict[str, Any]) -> str:
    body = json.dumps(figures, ensure_ascii=False, indent=2)
    lines = [
        "/**",
        " * Generated by scripts/export_investor_data.py (D-251): the figures that «Cómo lo",
        " * calculamos» gives for the investor version, from the code's constants and the",
        " * versioned tables. Do not edit: change the code or the table and run the script.",
        " */",
        f"export const INVESTOR_METHOD = {body} as const;",
        "",
    ]
    return "\n".join(lines)


def load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def outputs() -> list[tuple[Path, str]]:
    return [
        (PEM_TARGET, render_pem(load(PEM_SOURCE), load(COSTS_SOURCE))),
        (PILOT_TARGET, render_pilot(load(PILOT_SOURCE))),
        (PARCELS_TARGET, render_parcels(load(VEDA_SOURCE), load(PORTAL_SOURCE))),
        (AMBITS_TARGET, render_ambits(load(AMBITS_SOURCE))),
        (
            PLAN_USES_TARGET,
            render_plan_uses(PLAN_FIGURES_SOURCE, PLAN_PARCELS_SOURCE, PLAN_USE_NAMES_SOURCE),
        ),
        (
            METHOD_TARGET,
            render_method(
                method_figures(
                    load(PEM_SOURCE),
                    load(PILOT_SOURCE),
                    load(VEDA_SOURCE),
                    load(PORTAL_SOURCE),
                    load(COSTS_SOURCE),
                )
            ),
        ),
    ]


def main() -> int:
    check = "--check" in sys.argv
    rendered = outputs()
    stale = [p for p, content in rendered if not p.exists() or p.read_text() != content]
    if check:
        if stale:
            print("stale (run scripts/export_investor_data.py):", [p.name for p in stale])
            return 1
        return 0
    for path, content in rendered:
        path.write_text(content)
        print("wrote", path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
