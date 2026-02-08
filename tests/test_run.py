from pathlib import Path
from pyxems.run import simulate, check_config
import pytest


@pytest.mark.skipif(not check_config(), reason="OpenEMS exe not found.")
def test_simulate(tmp_path: Path):
    config_path = Path(__file__).parent / "data" / "simp_patch.xml"
    result = simulate(config_path, tmp_path)
    assert result.returncode == 0
