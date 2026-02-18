from pathlib import Path
from dataclasses import dataclass, field

from pyxems.fdtd import FDTDConfig
from pyxems.csx import ContinousStructure


@dataclass(frozen=True)
class PyXEMSConfig:
    fdtd: FDTDConfig = field(default_factory=FDTDConfig)
    csx: ContinousStructure = field(default_factory=ContinousStructure)

    def to_xml(self) -> str:
        xml = "<openEMS>\n"
        xml += self.fdtd.to_xml()
        xml += self.csx.to_xml()
        xml += "</openEMS>\n"
        return xml


def write_openEMS_xml(filename: Path | str, config: PyXEMSConfig):
    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
        f.write(config.to_xml())
