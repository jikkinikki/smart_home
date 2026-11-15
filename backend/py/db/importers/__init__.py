"""Add devices to the database, picking the importer from the device's "source".

Usage:
    from db.importers import add_device
    add_device(data)   # raises ValueError if the data isn't valid or the source is unknown

New source: write an importer in its own file and add an instance to IMPORTERS.
"""
from db.importers.base_importer import BaseImporter
from db.importers.zigbee_importer import ZigbeeImporter
from db.models import Device

# source -> importer
IMPORTERS: dict[str, BaseImporter] = {
    importer.source: importer
    for importer in (
        ZigbeeImporter(),
    )
}


def add_device(data: dict) -> Device:
    """Validate the device data and add it to the database (updates it if it already exists)."""
    source = data.get("source")
    importer = IMPORTERS.get(source)

    if importer is None:
        known = ", ".join(IMPORTERS)
        raise ValueError(f"No importer for source '{source}' (known: {known})")

    return importer.add(data)
