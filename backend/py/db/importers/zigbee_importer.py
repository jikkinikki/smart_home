"""Importer for Zigbee devices (the format patch_zigbee_devices writes to devices.json).

Kept:
    dev_id              ieee address - never changes, used as the id
    address             short network address (nwk) - every command is sent to it
    zigbee.endpoint     where on the device the commands go
    zigbee.capabilities which controls the device has (on_off, brightness, color...)
    zigbee.color_temp_mireds  warm/cool range, for converting 0-100 to mireds
    zigbee.groups       for group commands (switch several lamps with one message)
    zigbee.manufacturer / model   to tell device kinds apart (quirks, icons)

Everything else (nwk/ieee duplicates, role, reachable, in_clusters, date_code,
power_source, last_read...) is ignored.
"""
import re

from pydantic import BaseModel, Field, field_validator, model_validator

from db.importers.base_importer import BaseImporter
from db.models import Device

IEEE_PATTERN = re.compile(r"^([0-9a-f]{2}:){7}[0-9a-f]{2}$")  # a4:c1:38:9e:4e:72:45:7b
HEX16_PATTERN = re.compile(r"^0x[0-9a-f]{1,4}$")              # 0x4F53


def _hex16(value: str, what: str) -> str:
    value = value.strip().lower()
    if not HEX16_PATTERN.match(value):
        raise ValueError(f"{what} must be a hex value like 0x4F53, got '{value}'")
    return f"0x{int(value, 16):04X}"


class ZigbeeInfoIn(BaseModel):
    endpoint: int = Field(1, ge=1, le=240)
    capabilities: list[str] = []
    color_temp_mireds: tuple[int, int] | None = None
    groups: list[str] = []
    manufacturer: str | None = None
    model: str | None = None

    @field_validator("groups")
    @classmethod
    def check_groups(cls, groups: list[str]) -> list[str]:
        return [_hex16(group, "group") for group in groups]

    @field_validator("color_temp_mireds")
    @classmethod
    def check_mireds(cls, mireds):
        if mireds is not None and not 0 < mireds[0] < mireds[1]:
            raise ValueError(f"color_temp_mireds must be [min, max] with min < max, got {list(mireds)}")
        return mireds


class ZigbeeDeviceIn(BaseModel):
    dev_id: str
    device_name: str = ""
    type: str
    address: str
    version: str | None = None
    disabled: bool = False
    zigbee: ZigbeeInfoIn = ZigbeeInfoIn()

    @model_validator(mode="before")
    @classmethod
    def read_disabled(cls, data: dict) -> dict:
        # devices.json keeps it in custom_data
        if isinstance(data, dict) and "disabled" not in data:
            data = {**data, "disabled": (data.get("custom_data") or {}).get("disabled", False)}
        return data

    @field_validator("dev_id")
    @classmethod
    def check_ieee(cls, dev_id: str) -> str:
        dev_id = dev_id.strip().lower()
        if not IEEE_PATTERN.match(dev_id):
            raise ValueError(f"dev_id must be an ieee address like a4:c1:38:9e:4e:72:45:7b, got '{dev_id}'")
        return dev_id

    @field_validator("address")
    @classmethod
    def check_address(cls, address: str) -> str:
        return _hex16(address, "address")


class ZigbeeImporter(BaseImporter):
    source = "zigbee"

    def validate_source(self, data: dict) -> dict:
        return ZigbeeDeviceIn.model_validate(data).model_dump()

    def to_device(self, data: dict) -> Device:
        return Device(
            id=data["dev_id"],
            name=data["device_name"],
            type=data["type"],
            source=self.source,
            address=data["address"],
            version=data["version"],
            disabled=data["disabled"],
            extra=data["zigbee"],
        )
