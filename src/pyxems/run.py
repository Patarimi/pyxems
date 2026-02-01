from pathlib import Path
from subprocess import run, CompletedProcess
from shutil import which
import os
from typing import Optional

try:
    import cyclopts
    from dotenv import load_dotenv
except ImportError:
    raise ImportError(
        """
Please install pyxems with the 'simulate' extra package to use the simulation features.
You can do this by running: pip install pyxems[simulate]"""
    )

app = cyclopts.App(__name__)


@app.command()
def simulate(config_path: Path, run_dir: Optional[Path]) -> CompletedProcess:
    if which("openEMS") is None:
        load_dotenv()
        if "OPENEMS_PATH" in os.environ:
            openems_path = Path(os.environ["OPENEMS_PATH"]) / "openEMS"
    else:
        openems_path = "openEMS"
    config_path = config_path.resolve()
    if run_dir is None:
        run_dir = config_path.parent
    os.chdir(run_dir)
    cmd = [
        str(openems_path),
        config_path,
    ]
    proc = run(cmd, capture_output=True, text=True)
    return proc
