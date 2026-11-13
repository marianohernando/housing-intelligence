"""Evidence of the barrio data (D-232): sections to barrios, official names, walking minutes, rent
and trips by public transport of each barrio, with San Blas-Canillejas next to its district.

Usage: uv run python scripts/barrio_summary.py > evidence/gate-03/<date>/barrios-datos.md
Reads the local database after the panel, admin-names, features and commute runs.
"""

from sqlalchemy import Connection, text

from hi_db.session import make_engine

DISTRICT = "2807920"  # San Blas-Canillejas: Mariano's example, with Simancas
HUB = ("estacion:metro:nuevos ministerios", "Nuevos Ministerios (metro)")
WALK = (
    ("min_a_pie_colegio", "Colegio"),
    ("min_a_pie_centro_salud", "Centro de salud"),
    ("min_a_pie_transporte", "Parada"),
    ("min_a_pie_parque", "Parque"),
)

_SECTIONS = text(
    """
    SELECT count(*) AS sections,
           count(DISTINCT s.parent_admin_unit_id) AS barrios,
           count(*) FILTER (WHERE b.level IS DISTINCT FROM 'barrio') AS without_barrio,
           count(*) FILTER (WHERE NOT ST_Contains(b.geom_4326, ST_PointOnSurface(s.geom_4326)))
             AS point_outside
      FROM geo_admin_unit s
      LEFT JOIN geo_admin_unit b ON b.admin_unit_id = s.parent_admin_unit_id
     WHERE s.level = 'seccion_censal' AND left(s.code_official, 5) = '28079'
    """
)
_UNNAMED = text(
    "SELECT count(*) FROM geo_admin_unit WHERE level = 'barrio' AND coalesce(name, '') = ''"
)
_COVERAGE = text(
    """
    SELECT feature_id, count(*) AS rows, count(value) AS known,
           round(min(confidence)::numeric, 2) AS min_conf
      FROM feature_value
     WHERE territory_level = 'barrio' GROUP BY 1 ORDER BY 1
    """
)
_RENT = text(
    """
    SELECT count(*) FILTER (WHERE value IS NOT NULL AND confidence > 0.3) AS full,
           count(*) FILTER (WHERE value IS NOT NULL AND confidence <= 0.3) AS few,
           string_agg(territory_code, ', ') FILTER (WHERE value IS NULL) AS unknown
      FROM feature_value
     WHERE feature_id = 'alquiler_m2_mensual' AND territory_level = 'barrio'
    """
)
_TRIPS = text(
    """
    SELECT count(*) AS rows, count(minutes) AS known, count(DISTINCT hub_id) AS hubs,
           count(DISTINCT origin_admin_unit_id) AS barrios
      FROM commute_time WHERE origin_admin_unit_id LIKE 'ES.28.BAR.' || '%'
    """
)
_ZONES = text(
    """
    SELECT level, code_official AS code, admin_unit_id, name FROM geo_admin_unit
     WHERE (level = 'distrito' AND code_official = :district)
        OR (level = 'barrio' AND left(code_official, 7) = :district)
     ORDER BY level DESC, code_official
    """
)
_VALUE = text(
    """
    SELECT value, confidence FROM feature_value
     WHERE feature_id = :feature AND territory_level = :level AND territory_code = :code
    """
)
_TRIP = text(
    "SELECT minutes FROM commute_time WHERE hub_id = :hub AND origin_admin_unit_id = :zone"
)


def _fmt(value: object, digits: int = 1) -> str:
    return "—" if value is None else f"{float(str(value)):.{digits}f}"


def _cell(conn: Connection, feature: str, level: str, code: str) -> str:
    row = conn.execute(_VALUE, {"feature": feature, "level": level, "code": code}).first()
    return "—" if row is None else _fmt(row[0])


def _district_table(conn: Connection) -> None:
    header = ["Zona", *(label for _, label in WALK), "€/m² (conf.)", f"min a {HUB[1]}"]
    print("| " + " | ".join(header) + " |")
    print("|" + "---|" * len(header))
    for zone in conn.execute(_ZONES, {"district": DISTRICT}).mappings():
        level, code = str(zone["level"]), str(zone["code"])
        walk = [_cell(conn, feature, level, code) for feature, _ in WALK]
        rent = conn.execute(
            _VALUE, {"feature": "alquiler_m2_mensual", "level": level, "code": code}
        ).first()
        rent_text = "—" if rent is None else f"{_fmt(rent[0])} ({_fmt(rent[1], 2)})"
        trip = conn.execute(_TRIP, {"hub": HUB[0], "zone": zone["admin_unit_id"]}).scalar()
        name = f"**{zone['name']}** (distrito)" if level == "distrito" else str(zone["name"])
        print(f"| {name} | " + " | ".join([*walk, rent_text, _fmt(trip, 0)]) + " |")


def main() -> None:
    with make_engine().connect() as conn:
        sections = conn.execute(_SECTIONS).mappings().one()
        print("# Barrios de Madrid: datos de la fase 1 (D-232)\n")
        print("## Secciones y barrios")
        print(
            f"- {sections['sections']} secciones de Madrid en {sections['barrios']} barrios; "
            f"sin barrio: {sections['without_barrio']}; con su punto interior fuera de su "
            f"barrio: {sections['point_outside']}."
        )
        print(f"- Barrios sin nombre: {conn.execute(_UNNAMED).scalar()}.\n")
        print("## Features por barrio\n")
        print("| Feature | Filas | Con valor | Confidence mínima |\n|---|---|---|---|")
        for row in conn.execute(_COVERAGE).mappings():
            print(f"| `{row['feature_id']}` | {row['rows']} | {row['known']} | {row['min_conf']} |")
        rent = conn.execute(_RENT).mappings().one()
        print(
            f"\nAlquiler: {rent['full']} barrios con confidence 0,6 × cobertura, {rent['few']} "
            f"con menos de 5 lugares (0,3 como mucho) y sin dato: {rent['unknown']}.\n"
        )
        trips = conn.execute(_TRIPS).mappings().one()
        print("## Trayectos en transporte público")
        print(
            f"- {trips['barrios']} barrios × {trips['hubs']} destinos = {trips['rows']} filas; "
            f"{trips['known']} con minutos (el resto no llega a las 9:00).\n"
        )
        print(f"## San Blas-Canillejas ({DISTRICT}): el distrito y sus barrios\n")
        _district_table(conn)


if __name__ == "__main__":
    main()
