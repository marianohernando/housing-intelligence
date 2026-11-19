"""D-250: the saved sheets of the four demo parcels of the search by parcel (spike §7).

The API serves them when the Catastro or the Ayuntamiento fail (`fallback: "demo_snapshot"`),
and they are the only parcels with PARCEL_UPSTREAMS off (offline demo, e2e). This script asks
the services once for each parcel, in series (about five requests each), through the API's own
clients, and writes what the sheet shows: our fields, never the Catastro's answers (its licence:
only transformed information). The barrio around each parcel is not saved: the API reads it from
its database.

    uv run python scripts/parcel_demo_snapshot.py
"""

import asyncio
import json
import sys
from datetime import UTC, datetime

from hi_api.services.parcel_sheet import (
    DEMO_PATH,
    DemoParcel,
    DemoSnapshot,
    Lookup,
    live_parts,
)

# Méndez Álvaro 47-49 (solar, VEDA), Almería 1 (Portal del Suelo), Luis Misón 2 (solar, NZ 4,
# no coefficient) and Mayor 61 (horizontal division, NZ 1)
DEMO_RCS = ("2122202VK4722A", "3959601VK4735H", "0390314VK4709A", "9943003VK3794D")
METHOD = (
    "Fichas de demostración: los campos de Vida Fácil de cada parcela (datos de la parcela, "
    "planeamiento y edificabilidad), elaborados el día `observed_at` a partir de la Sede "
    "Electrónica del Catastro y del Ayuntamiento de Madrid por scripts/parcel_demo_snapshot.py. "
    "Sin respuestas originales de ningún servicio."
)


async def main() -> int:
    parcels = []
    for rc14 in DEMO_RCS:
        parts = await live_parts(rc14, Lookup("snapshot"))
        if parts.degraded or parts.planning is None:
            print(f"{rc14}: the Ayuntamiento did not answer; run it again later")
            return 1
        parcels.append(
            DemoParcel(
                parcel=parts.parcel, planning=parts.planning, buildability=parts.buildability
            )
        )
        print(rc14, parts.parcel.address, parts.planning.code, parts.buildability.value_m2)
    snapshot = DemoSnapshot(observed_at=datetime.now(UTC).date(), method=METHOD, parcels=parcels)
    body = json.dumps(snapshot.model_dump(mode="json"), ensure_ascii=False, indent=2)
    DEMO_PATH.write_text(body + "\n", encoding="utf-8")
    print(f"{len(parcels)} parcels -> {DEMO_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
