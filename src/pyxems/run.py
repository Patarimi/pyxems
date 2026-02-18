from pathlib import Path
from subprocess import run, CompletedProcess
from shutil import which
import os
from typing import Optional
import logging

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


def find_openems_executable() -> Optional[Path]:
    if which("openEMS") is not None:
        logging.info(f"Found OpenEMS executable in PATH: {which('openEMS')}")
        return Path(which("openEMS"))  # type: ignore
    load_dotenv()
    if "OPENEMS_PATH" not in os.environ:
        logging.info(
            "OPENEMS_PATH environment variable not set. Please set it to the directory containing the OpenEMS executable."
        )
        return None
    openems_path = Path(os.environ["OPENEMS_PATH"]) / (
        "openEMS" if os.name != "nt" else "openEMS.exe"
    )
    if not openems_path.is_file():
        logging.info(
            f"OpenEMS executable not found at {openems_path}. Please ensure OPENEMS_PATH is set correctly."
        )
        return None
    return openems_path


def check_config() -> bool:
    openems_executable = find_openems_executable()
    return openems_executable is not None


@app.command()
def simulate(config_path: Path, run_dir: Optional[Path]) -> CompletedProcess:
    openems_path = find_openems_executable()
    if openems_path is None:
        raise FileNotFoundError(
            "OpenEMS executable not found. Please ensure it is installed and in your PATH, or set the OPENEMS_PATH environment variable."
        )
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
