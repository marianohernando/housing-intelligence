"""Status of every gap row by municipio and by Madrid district, for the evidence (D-217).

Usage: uv run python scripts/gap_status_summary.py [zone names to detail ...]
"""

import os
import sys
from collections import Counter

from sqlalchemy import create_engine

from hi_api.services.gap_map import gap_row_map
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing"
)
STATUSES = ("FALTA", "JUSTO", "CUBIERTO", "SIN_DATOS")


def main() -> int:
    names = set(sys.argv[1:])
    detail: list[str] = []
    print("| Nivel | Fila | FALTA | JUSTO | CUBIERTO | SIN DATOS | Poco fiable | Agrupadas |")
    print("|---|---|---|---|---|---|---|---|")
    with create_engine(DATABASE_URL).connect() as conn:
        for level in (TerritoryLevel.MUNICIPIO, TerritoryLevel.DISTRITO):
            for row in GapRowKey:
                gap_map, _, _ = gap_row_map(conn, level, row)
                count = Counter(z.status.value for z in gap_map.zones)
                weak = sum(not z.reliable for z in gap_map.zones)
                pooled = sum(z.comparison_group is not None for z in gap_map.zones)
                cells = " | ".join(str(count.get(s, 0)) for s in STATUSES)
                print(f"| {level.value} | {row.value} | {cells} | {weak} | {pooled} |")
                for z in gap_map.zones:
                    if z.name in names:
                        group = (
                            f" · con {', '.join(z.comparison_group.names[1:])} "
                            f"({z.comparison_group.ratio_to_reference:.2f})"
                            if z.comparison_group
                            else ""
                        )
                        detail.append(
                            f"- {z.name} · {row.value}: **{z.status.value}** · valor {z.value} "
                            f"frente a {z.reference} ({z.reference_label}), ratio "
                            f"{z.ratio_to_reference}{group}"
                        )
    if detail:
        print("\n" + "\n".join(detail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
