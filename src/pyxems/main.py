from pathlib import Path
from typing import Literal, get_args
from dataclasses import dataclass, field

Boundary = Literal["MUR", "PEC", "PMC", "PML"]


@dataclass(frozen=True)
class Material:
    name: str
    epsilon_r: float
    mu_r: float
    kappa: float = 0.0
    sigma: float = 0.0

    def to_xml(self) -> str:
        return f'<{self.name} Epsilon="{self.epsilon_r:g}" Mue="{self.mu_r:g}" Kappa="{self.kappa:g}" Sigma="{self.sigma:g}" />'


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


Axes = Literal["X", "Y", "Z"]


@dataclass(frozen=True)
class Line:
    axe: Axes
    position: list[float] = field(default_factory=list)

    def to_xml(self) -> str:
        xml = f'<{self.axe.upper()}Lines Qty="{len(self.position)}">'
        xml += ",".join([f"{value}" for value in self.position])
        xml += f"</{self.axe.upper()}Lines>"
        return xml


@dataclass(frozen=True)
class ContinousStructure:
    coordinates_system: int = 0
    lines: dict[Axes, Line] = field(default_factory=dict)
    background_material: Material = field(
        default_factory=lambda: Material("BackgroundMaterial", 1.0, 1.0)
    )
    # TODO: add parameters settings for the structure

    def __post_init__(self):
        for axe in get_args(Axes):
            self.lines[axe] = Line(axe.upper())

    def add_line(self, axe: Axes, position: float):
        self.lines[axe].position.append(position)

    def to_xml(self) -> str:
        xml = f'<ContinuousStructure CoordSystem="{self.coordinates_system}">\n'
        xml += '    <RectilinearGrid DeltaUnit="0.001" CoordSystem="0">\n'
        for line in self.lines.values():
            xml += f"        {line.to_xml()}\n"
        xml += "    </RectilinearGrid>\n"
        xml += f"    {self.background_material.to_xml()}\n"
        xml += "</ContinuousStructure>\n"
        return xml


@dataclass(frozen=True)
class PyXEMSConfig:
    fdtd: FDTDConfig = field(default_factory=FDTDConfig)
    csx: ContinousStructure = field(default_factory=ContinousStructure)

    def to_xml(self) -> str:
        xml = "<openEMS>\n"
        xml += self.fdtd.to_xml()
        xml += self.csx.to_xml()
        xml += "</openEMS>"
        return xml


def write_openEMS_xml(filename: Path | str, config: PyXEMSConfig):
    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
        f.write(config.to_xml())
