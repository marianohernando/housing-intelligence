"""Download dataset resources into content-addressed Bronze folders."""

import json
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import httpx

from hi_contracts.catalog import DatasetSpec
from hi_ingestion.bronze import DEFAULT_BRONZE_ROOT, REPO_ROOT, sha256_file
from hi_ingestion.http import make_client


@dataclass(frozen=True)
class FetchedFile:
    dataset_id: str
    role: str
    path: Path
    sha256: str
    bytes: int
    url: str
    retrieved_at: str

    def manifest_entry(self) -> dict[str, object]:
        data = asdict(self)
        path = self.path.resolve()
        data["path"] = (
            str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
        )
        return data


def _store(
    dataset_id: str, role: str, tmp: Path, url: str, filename: str, root: Path
) -> FetchedFile:
    digest = sha256_file(tmp)
    folder = root / "datasets" / dataset_id / digest[:12]
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / filename
    if not target.exists():
        shutil.move(str(tmp), target)
    else:
        tmp.unlink()
    fetched = FetchedFile(
        dataset_id=dataset_id,
        role=role,
        path=target,
        sha256=digest,
        bytes=target.stat().st_size,
        url=url,
        retrieved_at=datetime.now(UTC).isoformat(),
    )
    manifest = folder / "manifest.json"
    entries = json.loads(manifest.read_text())["files"] if manifest.exists() else []
    entries = [e for e in entries if e["path"] != fetched.manifest_entry()["path"]]
    manifest.write_text(
        json.dumps({"files": [*entries, fetched.manifest_entry()]}, indent=2) + "\n"
    )
    return fetched


def download(client: httpx.Client, url: str, dest: Path) -> None:
    with client.stream("GET", url) as response:
        response.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in response.iter_bytes(1 << 20):
                fh.write(chunk)


def fetch_role(spec: DatasetSpec, role: str, root: Path = DEFAULT_BRONZE_ROOT) -> FetchedFile:
    resource = next((r for r in spec.resources if r.role == role), None)
    if resource is None:
        msg = f"{spec.dataset_id}: no resource with role {role!r}"
        raise KeyError(msg)
    url = str(resource.url)
    filename = url.rstrip("/").rsplit("/", 1)[-1]
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=root, delete=False, suffix=".part") as handle:
        tmp = Path(handle.name)
    with make_client(timeout=300) as client:
        download(client, url, tmp)
    return _store(spec.dataset_id, role, tmp, url, filename, root)


def local_file(dataset_id: str, role: str, path: Path) -> FetchedFile:
    """Wrap a local file (fixtures, offline demo snapshot) with the same metadata."""
    return FetchedFile(
        dataset_id=dataset_id,
        role=role,
        path=path,
        sha256=sha256_file(path),
        bytes=path.stat().st_size,
        url=path.resolve().as_uri(),
        retrieved_at=datetime.now(UTC).isoformat(),
    )
