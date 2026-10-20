import json
from pathlib import Path

import pytest

from hi_ingestion.bronze import BronzeWriter, sha256_bytes


def test_same_content_is_idempotent_different_content_is_refused(tmp_path: Path) -> None:
    writer = BronzeWriter("ns", "run", root=tmp_path)
    a = writer.write("x.json", b"{}", "https://x", 200, {"ETag": "1", "Set-Cookie": "secret"})
    b = writer.write("x.json", b"{}", "https://x", 200, {})
    assert a.sha256 == b.sha256 == sha256_bytes(b"{}")
    assert "Set-Cookie" not in a.headers
    with pytest.raises(FileExistsError, match="immutable"):
        writer.write("x.json", b"[]", "https://x", 200, {})


def test_manifest_lists_artifacts(tmp_path: Path) -> None:
    writer = BronzeWriter("ns", "run", root=tmp_path)
    writer.write("a.json", b"1", "https://a", 200, {})
    manifest = json.loads(writer.write_manifest({"status": "OK"}).read_text())
    assert manifest["status"] == "OK"
    assert [a["name"] for a in manifest["artifacts"]] == ["a.json"]
