# reference:https://github.com/thliebig/openEMS/blob/557483aa21d93fb053825272c5a7eb58f5016af5/openems.cpp#L821

from pathlib import Path
import xml.etree.ElementTree as ET


def openEMS_config() -> ET.Element:
    oems_config = ET.Element("openEMS")
    return oems_config


def add_FDTD(oems_config: ET.Element) -> ET.Element:
    FDTD = ET.SubElement(oems_config, "FDTD")
    return FDTD


def add_boundary(
    oems_config: ET.Element,
) -> ET.Element:
    FDTD = ET.SubElement(oems_config, "FDTD")
    BondaryCond = ET.SubElement(
        FDTD,
        "BoundaryCond",
        attrib={
            "xmin": "MUR",
            "xmax": "MUR",
            "ymin": "MUR",
            "ymax": "MUR",
            "zmin": "MUR",
            "zmax": "MUR",
        },
    )
    return BondaryCond


def add_CSX(oems_config: ET.Element) -> ET.Element:
    CSX = ET.SubElement(oems_config, "CSX")
    return CSX


def write_openEMS_xml(filename: Path | str, config: ET.Element):
    tree = ET.ElementTree(config)
    tree.write(filename, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    oems_config = openEMS_config()
    add_boundary(oems_config)
    add_FDTD(oems_config)
    add_CSX(oems_config)
    write_openEMS_xml("openEMS_config.xml", oems_config)
