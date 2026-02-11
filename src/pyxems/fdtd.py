from dataclasses import dataclass, field
from typing import Literal

Boundary = Literal["MUR", "PEC", "PMC", "PML"]


@dataclass(frozen=True)
class BoundaryCond:
    xmin: Boundary = "MUR"
    xmax: Boundary = "MUR"
    ymin: Boundary = "MUR"
    ymax: Boundary = "MUR"
    zmin: Boundary = "MUR"
    zmax: Boundary = "MUR"

    def to_xml(self) -> str:
        elem = "<BoundaryCond "
        for dim, value in self.__dict__.items():
            elem += f'{dim}="{value}" '
        elem += "/>"
        return elem


@dataclass(frozen=True)
class FDTDConfig:
    max_time_step: int = 1_000_000
    boundary_cond: BoundaryCond = field(default_factory=BoundaryCond)
    exitation: int = 0

    def to_xml(self) -> str:
        xml = f'<FDTD MaxTimeStep="{self.max_time_step}">\n'
        xml += f"    {self.boundary_cond.to_xml()}\n"
        xml += f"    <Excitation Type={self.exitation} />\n"
        xml += "</FDTD>\n"
        return xml
