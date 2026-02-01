from pathlib import Path
from pyxems.run import simulate


def test_simulate(tmp_path: Path):
    config_path = Path(__file__).parent / "data" / "simp_patch.xml"
    result = simulate(config_path, tmp_path)
    assert result.returncode == 0
