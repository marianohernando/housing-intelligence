"""D-223 evidence: what the CRTM GTFS `wheelchair_boarding` means, read against the topology.

For metro and Metro Ligero, every GTFS stop whose id carries a topology station key
(«par_4_12» -> «4_12») is counted by its GTFS code and by the station's published accessibility
grade (T, P, N). Reads the last valid Bronze of each GTFS feed and the last valid Silver of each
topology from the local database (read-only).

Usage: uv run python scripts/audit_step_free.py
"""

import csv
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from sqlalchemy import text

from hi_db.session import make_engine
from hi_ingestion.bronze import REPO_ROOT
from hi_ingestion.pipelines.station_topology.normalize import TOPOLOGY_FILE, read_topology

NETWORKS = {  # GTFS dataset -> (topology dataset, key of a stop id)
    "crtm_gtfs_metro": ("crtm_topologia_metro", r"^(?:par|est|acc)_(4_\d+)"),
    "crtm_gtfs_metro_ligero": ("crtm_topologia_metro_ligero", r"^(?:par|est|acc)_(10_\d+)"),
}
_MANIFEST = text(
    "SELECT bronze_manifest_path FROM dataset_version WHERE dataset_id = :d AND is_last_valid"
)


def _manifest(dataset_id: str) -> Path:
    with make_engine().connect() as conn:
        path = Path(str(conn.execute(_MANIFEST, {"d": dataset_id}).scalar_one()))
    return path if path.is_absolute() else REPO_ROOT / path


def _stops(gtfs: str) -> list[dict[str, str]]:
    manifest = json.loads(_manifest(gtfs).read_text())
    zip_path = Path(manifest["inputs"][0]["path"].replace("~", str(Path.home()), 1))
    if not zip_path.is_absolute():
        zip_path = REPO_ROOT / zip_path
    with zipfile.ZipFile(zip_path) as archive:
        name = next(n for n in archive.namelist() if n.endswith("stops.txt"))
        body = archive.read(name).decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(body)))


def main() -> None:
    for gtfs, (topology, key) in NETWORKS.items():
        grades = read_topology(_manifest(topology).parent / TOPOLOGY_FILE)
        grade_of = dict(zip(grades["station_id"], grades["grade"], strict=True))
        pattern = re.compile(key)
        counts: Counter[tuple[str, str]] = Counter()
        for stop in _stops(gtfs):
            match = pattern.match(stop["stop_id"])
            if match:
                code = stop.get("wheelchair_boarding", "").strip() or "vacío"
                counts[(code, grade_of.get(match.group(1), "no está"))] += 1
        print(f"## {gtfs} frente a {topology}: paradas por código GTFS y grado de la topología")
        print("| wheelchair_boarding | T | P | N | no está |")
        print("|---|---|---|---|---|")
        for code in sorted({c for c, _ in counts}):
            cells = [str(counts[(code, g)]) for g in ("T", "P", "N", "no está")]
            print(f"| {code} | {' | '.join(cells)} |")
        print()


if __name__ == "__main__":
    main()
