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


@dataclass(frozen=True)
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
class ExcitationProperty:
    number: int = 0
    enable: int = 1
    frequency: float = 0.0
    delay: float = 0
    type = 0
    excite: tuple[float, float, float] = (0.0, 0.0, -1.0)
    propdir: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def to_xml(self, short=True) -> str:
        return f' Number="{self.number}" Enabled="{self.enable}" Frequency="{self.frequency:e}" Delay="{self.delay:e}" Type="{self.type}" Excite="{",".join([f"{v:e}" for v in self.excite])}" PropDir="{",".join([f"{v:e}" for v in self.propdir])}"'


@dataclass(frozen=True)
class ProbeBoxProperty:
    number: int = 0
    type: int = 0
    weight: int = -1
    normdir: int = -1
    starttime: float = 0
    stoptime: float = 0

    def to_xml(self, short=True) -> str:
        return f' Number="{self.number}" Type="{self.type}" Weight="{self.weight}" NormDir="{self.normdir}" StartTime="{self.starttime:g}" StopTime="{self.stoptime:g}"'


@dataclass(frozen=True)
class DumpBoxProperty:
    number: int = 0
    type: int = 0
    weight: int = 1
    normdir: int = -1
    starttime: float = 0
    stoptime: float = 0
    dumptype: int = 0
    dumpmode: int = 1
    filetype: int = 1
    multigridlevel: int = 0

    def to_xml(self, short=True) -> str:
        return f' Number="{self.number}" Type="{self.type}" Weight="{self.weight}" NormDir="{self.normdir}" StartTime="{self.starttime:g}" StopTime="{self.stoptime:g}" DumpType="{self.dumptype}" DumpMode="{self.dumpmode}" FileType="{self.filetype}" MultiGridLevel="{self.multigridlevel}"'


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
    material: (
        MaterialProperty
        | LumpedProperty
        | ExcitationProperty
        | ProbeBoxProperty
        | DumpBoxProperty
    ) = field(
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
            case "Material":
                iso = ' Isotropy="1"'
            case "LumpedElement" | "ProbeBox" | "Excitation" | "DumpBox":
                iso = self.material.to_xml()
            case _:
                iso = ""
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
        if self.kind == "Excitation":
            xml += '    <Weight X="1.000000e+00" Y="1.000000e+00" Z="1.000000e+00" />\n'
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
        prop_conf: Optional[dict[str, float | int]] = None,
    ):
        id = len(self.properties)
        if prop_conf is None:
            prop_conf = {}
        match kind:
            case "Material" | "Metal":
                property = MaterialProperty(
                    "Property",
                    Physical(prop_conf["eps"] if "eps" in prop_conf else 1.0),
                    Physical(prop_conf["mu"] if "mu" in prop_conf else 1.0),
                    Physical(
                        (prop_conf["kappa"] if "kappa" in prop_conf else 0.0, 0, 0)
                    ),
                    Physical(
                        (prop_conf["sigma"] if "sigma" in prop_conf else 0.0, 0, 0)
                    ),
                )
            case "LumpedElement":
                property = LumpedProperty()
            case "Excitation":
                property = ExcitationProperty()
            case "ProbeBox":
                property = ProbeBoxProperty(
                    number=int(prop_conf["number"] if "number" in prop_conf else 0),
                    type=int(prop_conf["type"] if "type" in prop_conf else 0),
                    weight=int(prop_conf["weight"] if "weight" in prop_conf else -1),
                    normdir=int(prop_conf["normdir"] if "normdir" in prop_conf else -1),
                    starttime=prop_conf["starttime"] if "starttime" in prop_conf else 0,
                    stoptime=prop_conf["stoptime"] if "stoptime" in prop_conf else 0,
                )
            case "DumpBox":
                property = DumpBoxProperty(
                    dumptype=int(
                        prop_conf["dumptype"] if "dumptype" in prop_conf else 0
                    ),
                )
            case _:
                raise ValueError(f"Unknown property kind: {kind}")
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
