"""D-242: coverage of the reference rent and its calibration, from the local database (read-only).

Usage: uv run python scripts/serpavi_summary.py [--csv calibration.csv]
Prints how many zones get the Ministry's reference rent and how many keep the CM rent, by level,
and the CM mean / SERPAVI median of every municipio with both (the calibration the feature uses).
"""

import argparse
import csv
import os
import statistics
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing"
)
FILL = "alquiler_m2_mensual_referencia"
CM = "alquiler_m2_mensual"

_ROWS = text(
    """
    SELECT f.territory_level AS level, f.territory_code AS code, u.name,
           f.value AS fill, f.confidence, f.inputs->'reference_rent' AS ref,
           c.value AS cm
      FROM feature_value f
      LEFT JOIN feature_value c
        ON c.feature_id = :cm AND c.territory_level = f.territory_level
       AND c.territory_code = f.territory_code
      LEFT JOIN geo_admin_unit u
        ON u.level = f.territory_level AND u.code_official = f.territory_code
     WHERE f.feature_id = :fill
     ORDER BY f.territory_level, f.territory_code
    """
)
_CM_2024 = text(
    """
    SELECT territory_code, value FROM metric_observation
     WHERE metric_id = 'alquiler_m2_mensual_municipio' AND territory_level = 'municipio'
       AND dims->>'tipo_vivienda' = 'viviendas_habituales' AND period_start = :period
       AND value IS NOT NULL
    """
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, help="write the calibration table here")
    args = parser.parse_args()
    with create_engine(DATABASE_URL).connect() as conn:
        rows = [dict(r) for r in conn.execute(_ROWS, {"fill": FILL, "cm": CM}).mappings()]
        if not rows:
            print(f"{FILL} has no rows: compute it first", file=sys.stderr)
            return 1
        found = conn.execute(_CM_2024, {"period": "2024-01-01"}).all()
        cm_2024 = {str(code): float(value) for code, value in found}
    for level in ("municipio", "distrito", "barrio"):
        at = [r for r in rows if r["level"] == level]
        filled = [r for r in at if r["fill"] is not None]
        used = [r for r in filled if r["cm"] is None]  # the search reads the fill only here
        houses = [r for r in filled if (r["ref"] or {}).get("typology") == "unifamiliar"]
        few = [r for r in filled if ((r["ref"] or {}).get("contracts") or 0) < 30]
        with_cm = [r for r in at if r["cm"] is not None]
        neither = [r for r in at if r["cm"] is None and r["fill"] is None]
        print(
            f"{level}: {len(at)} zonas · {len(filled)} con referencia ({len(houses)} solo de "
            f"casas, {len(few)} con menos de 30 contratos) · {len(with_cm)} con el dato CM, que "
            f"manda · {len(used)} rellenas con la referencia · {len(neither)} sin ninguno"
        )
        if level != "municipio" and used:
            print(f"  rellenas: {', '.join(str(r['name']) for r in used)}")
    medians = {
        r["code"]: (r["ref"] or {}).get("median_m2") for r in rows if r["level"] == "municipio"
    }
    names = {r["code"]: r["name"] for r in rows if r["level"] == "municipio"}
    table = sorted(
        (float(cm_2024[c]) / m, c, names[c], float(cm_2024[c]), m)
        for c, m in medians.items()
        if m and c in cm_2024
    )
    ratios = [t[0] for t in table]
    print(
        f"calibración: {len(ratios)} municipios · mediana {statistics.median(ratios):.4f} · "
        f"media {statistics.mean(ratios):.4f} · de {min(ratios):.3f} a {max(ratios):.3f}"
    )
    if args.csv:
        with args.csv.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                ["municipio", "nombre", "cm_media_2024", "serpavi_mediana_2024", "cociente"]
            )
            for ratio, code, name, cm, median in table:
                writer.writerow([code, name, cm, round(median, 4), round(ratio, 4)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
