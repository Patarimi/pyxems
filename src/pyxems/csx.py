from dataclasses import dataclass, field
from typing import Literal, get_args, Protocol, Optional

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


@dataclass()
class Physical:
    value: tuple[float, float, float]

    def __init__(self, value: float | int | tuple[float, float, float]):
        if isinstance(value, float) or isinstance(value, int):
            self.value = (value, 1.0, 1.0)
        else:
            self.value = value

    def __str__(self, short=True) -> str:
        if short:
            return f"{self.value[0]:g}"
        else:
            return ",".join([f"{v:e}" for v in self.value])


@dataclass()
class MaterialProperty:
    name: str
    epsilon_r: Physical
    mu_r: Physical
    kappa: Physical = field(default_factory=lambda: Physical((0, 0, 0)))
    sigma: Physical = field(default_factory=lambda: Physical((0, 0, 0)))
    density: float = 0.0

    def to_xml(self, short=True) -> str:
        if short:
            return f'<{self.name} Epsilon="{self.epsilon_r}" Mue="{self.mu_r}" Kappa="{self.kappa}" Sigma="{self.sigma}" />'
        else:
            return f'<{self.name} Epsilon="{self.epsilon_r.__str__(short=False)}" Mue="{self.mu_r.__str__(short=False)}" Kappa="{self.kappa.__str__(short=False)}" Sigma="{self.sigma.__str__(short=False)}" Density="{self.density:e}" />'


@dataclass
class LumpedProperty:
    direction: Optional[Axes] = "Z"
    caps: int = 1
    resistance: float = 50
    capacitance: float = 0
    inductance: float = 0
    letype: int = 0

    def to_xml(self, short=True) -> str:
        axe_number = {"X": 0, "Y": 1, "Z": 2}
        cap = self.capacitance if self.capacitance != 0 else "-nan(ind)"
        ind = self.inductance if self.inductance != 0 else "-nan(ind)"
        return f' Direction="{axe_number[self.direction]}" Caps="{self.caps}" R="{self.resistance:e}" C="{cap}" L="{ind}" LEtype="{self.letype:e}"'


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255

    def to_xml(self) -> str:
        return f'R="{self.r}" G="{self.g}" B="{self.b}" a="{self.a}"'


class Primitive(Protocol):
    def to_xml(self) -> str: ...


point = tuple[float, float, float]


@dataclass(frozen=True)
class Box(Primitive):
    start: point
    stop: point
    priority: int = 0

    def to_xml(self) -> str:
        xml = f'<Box Priority="{self.priority}">\n'
        xml += f'    <P1 X="{self.start[0]:8e}" Y="{self.start[1]:8e}" Z="{self.start[2]:8e}" />\n'
        xml += f'    <P2 X="{self.stop[0]:8e}" Y="{self.stop[1]:8e}" Z="{self.stop[2]:8e}" />\n'
        xml += "</Box>"
        return xml


PropertyKind = Literal[
    "Metal", "Material", "LumpedElement", "Excitation", "ProbeBox", "DumpBox"
]


@dataclass(frozen=True)
class Property:
    name: str
    id: int
    kind: PropertyKind = "Material"
    fillcolor: Color = field(default_factory=lambda: Color(255, 255, 255, 255))
    edgecolor: Color = field(default_factory=lambda: Color(0, 0, 0, 255))
    material: MaterialProperty | LumpedProperty = field(
        default_factory=lambda: MaterialProperty(
            "Property", Physical(1.0), Physical(1.0)
        )
    )
    weight: MaterialProperty = field(
        default_factory=lambda: MaterialProperty(
            "Weight",
            Physical(1.0),
            Physical(1.0),
            Physical((1.0, 1.0, 1.0)),
            Physical((1.0, 1.0, 1.0)),
            1.0,
        )
    )
    _primitive: list[Primitive] = field(default_factory=list)

    def to_xml(self) -> str:
        match self.kind:
            case "Metal":
                iso = ""
            case "Material":
                iso = ' Isotropy="1"'
            case "LumpedElement":
                iso = self.material.to_xml()
        xml = f'<{self.kind} ID="{self.id}" Name="{self.name}"{iso}>\n'
        xml += f"    <FillColor {self.fillcolor.to_xml()} />\n"
        xml += f"    <EdgeColor {self.edgecolor.to_xml()} />\n"
        xml += "    <Primitives>\n"
        for primitive in self._primitive:
            for line in primitive.to_xml().splitlines():
                xml += f"        {line}\n"
        xml += "    </Primitives>\n"
        if self.kind == "Material":
            xml += f"    {self.material.to_xml(False)}\n"
            xml += f"    {self.weight.to_xml(False)}\n"
        xml += f"</{self.kind}>\n"
        return xml


@dataclass(frozen=True)
class ContinousStructure:
    coordinates_system: int = 0
    lines: dict[Axes, Line] = field(default_factory=dict)
    background_material: MaterialProperty = field(
        default_factory=lambda: MaterialProperty(
            "BackgroundMaterial", Physical(1.0), Physical(1.0)
        )
    )
    properties: list[Property] = field(default_factory=list)

    def __post_init__(self):
        for axe in get_args(Axes):
            self.lines[axe] = Line(axe.upper())

    def add_line(self, axe: Axes, position: float):
        self.lines[axe].position.append(position)

    def add_property(
        self,
        kind: PropertyKind,
        name: str,
        fillcolor: Color = Color(255, 255, 255, 255),
        edgecolor: Optional[Color] = None,
        eps: float = 1.0,
        mu: float = 1.0,
        kappa: float = 0.0,
        sigma: float = 0.0,
    ):
        id = len(self.properties)
        if kind in ("Material", "Metal"):
            property = MaterialProperty(
                "Property",
                Physical(eps),
                Physical(mu),
                Physical((kappa, 0, 0)),
                Physical((sigma, 0, 0)),
            )
        else:
            property = LumpedProperty()
        prop = Property(
            name,
            id,
            kind,
            fillcolor,
            edgecolor if edgecolor is not None else fillcolor,
            material=property,
        )
        self.properties.append(prop)

    def add_box(
        self, start: point, stop: point, priority: int = 0, property_id: int = 0
    ):
        box = Box(start, stop, priority)
        self.properties[property_id]._primitive.append(box)

    def to_xml(self) -> str:
        xml = f'<ContinuousStructure CoordSystem="{self.coordinates_system}">\n'
        xml += '    <RectilinearGrid DeltaUnit="0.001" CoordSystem="0">\n'
        for line in self.lines.values():
            xml += f"        {line.to_xml()}\n"
        xml += "    </RectilinearGrid>\n"
        xml += f"    {self.background_material.to_xml()}\n"
        xml += "    <ParameterSet />\n"
        xml += "    <Properties>\n"
        for property in self.properties:
            for line in property.to_xml().splitlines():
                xml += f"        {line}\n"
        xml += "    </Properties>\n"
        xml += "</ContinuousStructure>\n"
        return xml
