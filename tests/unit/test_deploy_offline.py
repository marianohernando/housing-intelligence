"""The offline demo package dumps exactly the tables of the Supabase demo profile.

Both copy the same data to a second database; if one gains a table the other would miss it.
"""

import re
from pathlib import Path

SYNC_SCRIPT = Path("scripts/supabase_sync.sh")
OFFLINE_SCRIPT = Path("infra/deploy/offline/demo_offline.sh")


def _bash_array(path: Path, name: str) -> list[str]:
    match = re.search(rf"^{name}=\(([^)]*)\)", path.read_text(encoding="utf-8"), re.MULTILINE)
    assert match, f"{name}=(...) not found in {path}"
    return match.group(1).split()


def test_offline_package_dumps_the_demo_profile(repo_root: Path) -> None:
    demo_profile = _bash_array(repo_root / SYNC_SCRIPT, "BASE")
    assert "geo_admin_unit" in demo_profile
    assert _bash_array(repo_root / OFFLINE_SCRIPT, "TABLES") == demo_profile
