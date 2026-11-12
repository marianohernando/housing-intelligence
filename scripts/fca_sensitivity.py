"""How much the 2SFCA rows depend on the 15-minute catchment (D-217).

Recomputes two rows at 10 and 20 minutes (nothing is stored) and compares the municipio values
with the 15-minute ones: Spearman rank correlation and the share of municipios whose position
moves by more than 20 places. Usage: uv run python scripts/fca_sensitivity.py
"""

import json
import os
import sys
from typing import Any

import numpy as np
from scipy.stats import rankdata
from sqlalchemy import Engine, create_engine

from hi_domain.access.fca import zone_totals
from hi_domain.access.graph import FloatArray
from hi_features import fca, walk
from hi_ingestion.catalog.loader import load_catalog

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing"
)
FEATURES = ("aulas_primaria_a_pie_por_1000_ninos", "centros_salud_a_pie_por_10000_hab")


def municipio_values(engine: Engine, formula: dict[str, Any]) -> FloatArray:
    keyed = {k: v for k, v in formula.items() if k != "levels"}
    result = fca.node_access(engine, json.dumps(keyed, sort_keys=True, ensure_ascii=False))
    path = walk.network_version(engine).path
    origins = walk.origins(engine, path, tuple(formula["origin_highways"]))
    zones = walk.zone_codes(engine, "municipio")
    index = fca.zone_index(origins.section.tolist(), "municipio", zones)
    capacity, people = zone_totals(index, result.demand, result.access, len(zones))
    return np.divide(capacity, people, out=np.full(len(zones), np.nan), where=people > 0)


def rank(values: FloatArray) -> FloatArray:
    return np.asarray(rankdata(values), dtype=float)  # ties share their mean rank


def main() -> int:
    engine = create_engine(DATABASE_URL)
    catalog = load_catalog()
    print("| Fila (feature) | Minutos | Spearman frente a 15 min | Se mueven > 20 puestos |")
    print("|---|---|---|---|")
    for feature_id in FEATURES:
        formula = dict(catalog.features[feature_id].formula.model_dump())
        base = municipio_values(engine, formula)
        for minutes in (10, 20):
            other = municipio_values(engine, formula | {"catchment_minutes": minutes})
            ok = ~np.isnan(base) & ~np.isnan(other)
            rho = float(np.corrcoef(rank(base[ok]), rank(other[ok]))[0, 1])  # Spearman
            ranks_a, ranks_b = rank(base[ok]), rank(other[ok])
            moved = float(np.mean(np.abs(ranks_a - ranks_b) > 20))
            print(f"| {feature_id} | {minutes} | {rho:.3f} | {moved:.0%} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
