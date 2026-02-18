from pathlib import Path
from pyxems.run import simulate, check_config, find_openems_executable
import pytest


@pytest.mark.skipif(
    not check_config(), reason=f"OpenEMS exe not found. {find_openems_executable()}"
)
def test_simulate(tmp_path: Path):
    config_path = Path(__file__).parent / "data" / "simp_patch.xml"
    result = simulate(config_path, tmp_path)
    assert result.returncode == 0
