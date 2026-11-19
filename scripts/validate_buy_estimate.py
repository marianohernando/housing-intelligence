"""Validation of the estimated purchase price of Madrid districts (D-234) against public asking
prices: rank correlation, the common level and the error of each district once that level is
taken out.

The references (district, €/m², period, source and its URL) are in a CSV under evidence; they
are asking prices of a private portal, used only to check the estimate, never as data.

Usage: uv run python scripts/validate_buy_estimate.py [references.csv] > <evidence>.txt
Reads `precio_compra_estimado_m2` by district from DATABASE_URL. Exits with 1 when the order
or the error is off (Spearman < 0.9 or a district beyond ±30 %).
"""

import csv
import math
import sys
from pathlib import Path

from sqlalchemy import text

from hi_db.session import make_engine

REPO = Path(__file__).resolve().parents[1]
REFERENCES = REPO / "evidence" / "gate-04" / "2026-11-14" / "referencias-precio-distritos.csv"
FEATURE = "precio_compra_estimado_m2"
MIN_SPEARMAN, MAX_ERROR = 0.9, 0.30

_ESTIMATES = text(
    """
    SELECT DISTINCT ON (territory_code) territory_code, value
      FROM feature_value
     WHERE feature_id = :feature AND territory_level = 'distrito' AND value IS NOT NULL
     ORDER BY territory_code, feature_version DESC, period_start DESC
    """
)


def ranks(values: list[float]) -> list[float]:
    """1-based ranks, ties sharing their mean rank."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return out


def spearman(xs: list[float], ys: list[float]) -> float:
    """Pearson correlation of the ranks (exact with ties)."""
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry, strict=True))
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return cov / (sx * sy)


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else REFERENCES
    with path.open(encoding="utf-8", newline="") as handle:
        references = list(csv.DictReader(handle))
    with make_engine().connect() as conn:
        estimates = {
            str(r.territory_code): float(r.value)
            for r in conn.execute(_ESTIMATES, {"feature": FEATURE})
        }
    rows = [(r, estimates[r["territory_code"]]) for r in references]
    names = [r["distrito"] for r, _ in rows]
    estimate = [e for _, e in rows]
    asking = [float(r["precio_oferta_eur_m2"]) for r, _ in rows]
    rho = spearman(estimate, asking)
    ratios = [e / a for e, a in zip(estimate, asking, strict=True)]
    level = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
    errors = [x / level - 1 for x in ratios]

    sources = sorted({(r["fuente"], r["url"], r["periodo"], r["publicado"]) for r in references})
    print(f"# Precio de compra estimado (D-234) frente a precios de oferta, {len(rows)} distritos")
    for name, url, period, published in sources:
        print(f"Fuente: {name} ({url}), precios de {period}, publicado el {published}")
    print()
    print(f"{'Distrito':<22}{'estimado':>10}{'oferta':>9}{'est/oferta':>12}{'error':>9}")
    for n, e, a, x, err in zip(names, estimate, asking, ratios, errors, strict=True):
        print(f"{n:<22}{e:>10.0f}{a:>9.0f}{x:>12.2f}{100 * err:>+8.1f}%")
    print()
    print(f"Spearman: {rho:.3f}")
    print(f"Nivel común (media geométrica de estimado/oferta): {level:.3f}")
    low, high = 100 * min(errors), 100 * max(errors)
    print(f"Error por distrito, quitado ese nivel: de {low:+.1f} % a {high:+.1f} %")
    ok = rho >= MIN_SPEARMAN and max(abs(e) for e in errors) <= MAX_ERROR
    verdict = "OK" if ok else "NO"
    print(
        f"Criterio: Spearman ≥ {MIN_SPEARMAN} y ningún error de más del {MAX_ERROR:.0%}: {verdict}"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
