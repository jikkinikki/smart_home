"""TEMPORARY: copy every device in devices.json into the database.

Delete this script together with devices.json once the database is the only source.

Run directly (from the project root):
    venv\\Scripts\\python backend/py/import_devices_json.py

Safe to run again: devices are matched on dev_id, so existing rows are updated instead
of duplicated. Rows that aren't in devices.json are left untouched.
"""
import json

from sqlmodel import Session

from config.paths import JSON_DIR
from create_tables import main as create_tables
from db.database import engine
from db.models import Device

DEVICES_FILE = JSON_DIR / "devices.json"

# The zigbee fields worth keeping in Device.extra (the same ones ZigbeeImporter keeps)
ZIGBEE_KEEP = ("endpoint", "capabilities", "color_temp_mireds", "groups", "manufacturer", "model")


def to_device(data: dict) -> Device:
    source = data.get("source")
    extra = data.get(source) or {} if source else {}

    if source == "zigbee":
        extra = {key: extra[key] for key in ZIGBEE_KEEP if key in extra}

    return Device(
        id=data["dev_id"],
        name=data.get("device_name") or "",
        type=data.get("type") or "unknown",
        source=source,
        address=data.get("address"),
        local_key=data.get("local_key"),
        version=data.get("version"),
        disabled=bool((data.get("custom_data") or {}).get("disabled", False)),
        extra=extra,
    )


def main() -> None:
    create_tables()

    devices = json.loads(DEVICES_FILE.read_text(encoding="utf-8"))

    with Session(engine) as session:
        for data in devices:
            if not data.get("dev_id"):
                print("no dev_id, skipping:", data.get("device_name"))
                continue

            session.merge(to_device(data))  # insert or update by dev_id
            print("added:", data.get("device_name") or data["dev_id"], f"({data.get('type')} {data.get('source')})")

        session.commit()


if __name__ == "__main__":
    main()
