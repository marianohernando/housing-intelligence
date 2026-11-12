"""Evidence of the commute matrix (CORE-009, D-220): inputs, coverage and reference pairs.

Usage: uv run python scripts/commute_summary.py > evidence/gate-03/<date>/commute-matrix.md
Reads the local database after `uv run hi-features commute`.
"""

from sqlalchemy import text

from hi_db.session import make_engine

PAIRS = (
    ("estacion:metro:puerta del sol", "Puerta del Sol (metro)"),
    ("estacion:metro:nuevos ministerios", "Nuevos Ministerios (metro)"),
)
ZONES = (
    "Centro",
    "Chamartín",
    "Ciudad Lineal",
    "Villaverde",
    "Getafe",
    "Leganés",
    "Móstoles",
    "Alcalá de Henares",
    "Torrejón de Ardoz",
    "Tres Cantos",
    "Collado Villalba",
    "Aranjuez",
    "Navalcarnero",
    "Colmenar Viejo",
    "Buitrago del Lozoya",
    "San Martín de Valdeiglesias",
)

_FEEDS = text(
    """
    SELECT f FROM transit_hub, jsonb_array_elements(inputs->'feeds') f
     WHERE hub_id = (SELECT min(hub_id) FROM transit_hub)
    """
)
_INPUTS = text("SELECT method_version, inputs FROM transit_hub ORDER BY hub_id LIMIT 1")
_COVERAGE = text(
    """
    SELECT h.kind, count(DISTINCT h.hub_id) AS hubs, count(*) AS rows,
           count(c.minutes) AS with_minutes,
           percentile_cont(0.5) WITHIN GROUP (ORDER BY c.minutes) AS median
      FROM commute_time c JOIN transit_hub h USING (hub_id)
     GROUP BY h.kind ORDER BY h.kind
    """
)
_PAIR = text(
    """
    SELECT g.name, c.minutes, c.sections_reached, c.sections
      FROM commute_time c JOIN geo_admin_unit g ON g.admin_unit_id = c.origin_admin_unit_id
     WHERE c.hub_id = :hub AND g.name = ANY(:zones) AND g.level IN ('municipio', 'distrito')
     ORDER BY c.minutes NULLS LAST
    """
)
_NO_VALUE = text(
    """
    SELECT g.name FROM commute_time c
      JOIN geo_admin_unit g ON g.admin_unit_id = c.origin_admin_unit_id
     WHERE c.hub_id = :hub AND c.minutes IS NULL ORDER BY 1
    """
)


def main() -> None:
    engine = make_engine()
    with engine.connect() as conn:
        method, inputs = conn.execute(_INPUTS).one()
        feeds = [r[0] for r in conn.execute(_FEEDS)]
        coverage = conn.execute(_COVERAGE).mappings().all()
        print(f"# Tiempo en transporte público al trabajo (CORE-009, `{method}`)\n")
        print(
            f"Llegada a las {', '.join(inputs['arrive_by'])} (mediana de las tres), servicio "
            f"desde las {inputs['window_start']}; a pie a {inputs['walk_km_h']} km/h con un "
            f"rodeo de {inputs['detour']} sobre la línea recta; transbordos a pie hasta "
            f"{inputs['footpath_m']} m, acceso y salida hasta {inputs['access_m']} m, "
            f"{inputs['transfer_s']} s para cambiar en la misma parada.\n"
        )
        print("## GTFS usados (día de referencia de cada uno) y limpieza\n")
        keys = (
            "trips_going_back",
            "calls_interpolated",
            "calls_estimated_by_speed",
            "trips_estimated_by_speed",
            "lines_without_any_time",
            "trips_too_fast",
        )
        print("| Dataset | Día | " + " | ".join(keys) + " |")
        print("|---|---|" + "---|" * len(keys))
        for f in feeds:
            values = " | ".join(str(f.get(k, "")) for k in keys)
            print(f"| {f['dataset_id']} | {f['service_date']} | {values} |")
        print("\n## Cobertura\n")
        print("| Destinos | Nº | Filas | Con minutos | Mediana (min) |")
        print("|---|---|---|---|---|")
        for r in coverage:
            median = "" if r["median"] is None else f"{r['median']:.1f}"
            print(f"| {r['kind']} | {r['hubs']} | {r['rows']} | {r['with_minutes']} | {median} |")
        for hub, label in PAIRS:
            print(f"\n## Hasta {label}\n")
            print("| Zona | Minutos | Secciones que llegan |")
            print("|---|---|---|")
            for r in conn.execute(_PAIR, {"hub": hub, "zones": list(ZONES)}).mappings():
                minutes = "sin dato" if r["minutes"] is None else f"{r['minutes']:.1f}"
                print(f"| {r['name']} | {minutes} | {r['sections_reached']}/{r['sections']} |")
            missing = [r[0] for r in conn.execute(_NO_VALUE, {"hub": hub})]
            print(f"\nSin dato ({len(missing)} zonas): {', '.join(missing)}.")


if __name__ == "__main__":
    main()
