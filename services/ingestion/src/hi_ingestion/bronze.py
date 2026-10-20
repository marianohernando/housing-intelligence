"""Bronze layer: immutable raw artifacts + checksum manifest (docs/02_data/25)."""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BRONZE_ROOT = REPO_ROOT / "data" / "bronze"
KEPT_HEADERS = ("etag", "last-modified", "content-type", "content-length")


@dataclass(frozen=True)
class BronzeArtifact:
    name: str
    path: str
    sha256: str
    bytes: int
    url: str
    status_code: int
    retrieved_at: str
    headers: dict[str, str]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while block := fh.read(chunk):
            digest.update(block)
    return digest.hexdigest()


class BronzeWriter:
    """Writes artifacts under <root>/<namespace>/<run_label>/ and a manifest.json."""

    def __init__(self, namespace: str, run_label: str, root: Path = DEFAULT_BRONZE_ROOT) -> None:
        self.directory = root / namespace / run_label
        self.directory.mkdir(parents=True, exist_ok=True)
        self.namespace = namespace
        self.run_label = run_label
        self._artifacts: list[BronzeArtifact] = []

    def write(
        self, name: str, content: bytes, url: str, status_code: int, headers: dict[str, str]
    ) -> BronzeArtifact:
        path = self.directory / name
        if path.exists() and sha256_file(path) != sha256_bytes(content):
            msg = f"Bronze is immutable: {path} already exists with different content"
            raise FileExistsError(msg)
        path.write_bytes(content)
        artifact = BronzeArtifact(
            name=name,
            path=str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path),
            sha256=sha256_bytes(content),
            bytes=len(content),
            url=url,
            status_code=status_code,
            retrieved_at=datetime.now(UTC).isoformat(),
            headers={k: v for k, v in headers.items() if k.lower() in KEPT_HEADERS},
        )
        self._artifacts.append(artifact)
        return artifact

    def write_manifest(self, extra: dict[str, object] | None = None) -> Path:
        manifest = {
            "namespace": self.namespace,
            "run_label": self.run_label,
            "written_at": datetime.now(UTC).isoformat(),
            "artifacts": [asdict(a) for a in self._artifacts],
            **(extra or {}),
        }
        path = self.directory / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        return path
