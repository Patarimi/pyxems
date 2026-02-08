from dataclasses import dataclass, field
from typing import Literal, get_args

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
class Material:
    name: str
    epsilon_r: float
    mu_r: float
    kappa: float = 0.0
    sigma: float = 0.0

    def to_xml(self) -> str:
        return f'<{self.name} Epsilon="{self.epsilon_r:g}" Mue="{self.mu_r:g}" Kappa="{self.kappa:g}" Sigma="{self.sigma:g}" />'


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
