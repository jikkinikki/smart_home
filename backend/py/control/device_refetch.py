"""Fetch the devices again (Tuya wizard + Zigbee bridge) and compare them with the database.

Nothing is saved while fetching. The differences are kept as "changes" (one per device),
and apply() saves the chosen ones and restarts every device with the new data.

    refetch = DeviceRefetch(device_handler)
    refetch.start()              # runs in a background thread
    refetch.get_status()         # {"state": "running" | "done" | ..., "changes": [...]}
    refetch.apply(["dev id"])    # save those changes, then restart the devices

Devices that are in the database but weren't found are left alone (not removed).
"""
import json
import threading
import time

from sqlmodel import Session

from config.paths import PROJECT_DIR
from db.database import engine
from db.device_reader import DeviceReader
from db.models import Device

# The zigbee fields kept in Device.extra (the same ones ZigbeeImporter keeps)
ZIGBEE_KEEP = ("endpoint", "capabilities", "color_temp_mireds", "groups", "manufacturer", "model")

# Never sent to the frontend, it only sees that they changed
SECRET_FIELDS = ("local_key",)

# The tinytuya wizard writes to the working directory by default, so point it at the
# same files `python -m tinytuya wizard` uses when it's run from the project root.
TUYA_CONFIG_FILE = PROJECT_DIR / "tinytuya.json"
TUYA_DEVICES_FILE = PROJECT_DIR / "devices.json"
TUYA_SNAPSHOT_FILE = PROJECT_DIR / "snapshot.json"
TUYA_RAW_FILE = PROJECT_DIR / "tuya-raw.json"

ZIGBEE_READ_TIMEOUT = 300  # seconds; every device on the bridge gets interviewed


class DeviceRefetch:
    def __init__(self, device_handler):
        self.device_handler = device_handler
        self._lock = threading.Lock()

        self.state = "idle"         # idle -> running -> done (-> idle after apply)
        self.started_at = None
        self.finished_at = None
        self.errors = {}            # source -> error message, e.g. {"tuya": "..."}
        self._pending = {}          # device id -> {"status", "row": Device, "fields": [...]}

    # ---------- fetching ----------

    def start(self) -> bool:
        """Start fetching in the background. Returns False if it's already running."""
        with self._lock:
            if self.state == "running":
                return False

            self.state = "running"
            self.started_at = time.time()
            self.finished_at = None
            self.errors = {}
            self._pending = {}

        threading.Thread(target=self._run, name="device-refetch", daemon=True).start()
        return True

    def _run(self):
        # Both sources are slow (network scan / zigbee interview), so fetch them side by side
        results = {}

        def fetch(source, func):
            try:
                results[source] = func()
            except Exception as e:
                print(f"refetch {source} failed:", f"{e.__class__.__name__}: {e}")
                self.errors[source] = f"{e.__class__.__name__}: {e}"

        threads = [
            threading.Thread(target=fetch, args=("tuya", self._fetch_tuya)),
            threading.Thread(target=fetch, args=("zigbee", self._fetch_zigbee)),
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        current = {row.id: row for row in DeviceReader().get_all_devices()}
        pending = {}

        for source in ("tuya", "zigbee"):
            for fetched in results.get(source, []):
                change = self._compare(current.get(fetched.id), fetched)
                if change is not None:
                    pending[fetched.id] = change

        with self._lock:
            self._pending = pending
            self.state = "done"
            self.finished_at = time.time()

    def _fetch_tuya(self) -> list[Device]:
        """Run the tinytuya wizard (same as `python -m tinytuya wizard` answering yes to everything)."""
        # The wizard uses tinytuya.scanner for the local scan but never imports it
        # (`python -m tinytuya` does that first), so import it here
        from tinytuya import scanner, wizard

        wizard.CONFIGFILE = str(TUYA_CONFIG_FILE)
        wizard.DEVICEFILE = str(TUYA_DEVICES_FILE)
        wizard.SNAPSHOTFILE = str(TUYA_SNAPSHOT_FILE)
        wizard.RAWFILE = str(TUYA_RAW_FILE)
        scanner.DEVICEFILE = str(TUYA_DEVICES_FILE)
        scanner.SNAPSHOTFILE = str(TUYA_SNAPSHOT_FILE)

        if not TUYA_CONFIG_FILE.exists():
            raise RuntimeError(f"No {TUYA_CONFIG_FILE.name}. Run `python -m tinytuya wizard` once to set up the Tuya cloud keys")

        before = TUYA_DEVICES_FILE.stat().st_mtime if TUYA_DEVICES_FILE.exists() else None

        wizard.wizard(color=False, assume_yes=True)

        # The wizard only prints its errors, but it only writes devices.json when the cloud answered
        if not TUYA_DEVICES_FILE.exists() or TUYA_DEVICES_FILE.stat().st_mtime == before:
            raise RuntimeError("The Tuya wizard didn't get the device list (expired IoT subscription or wrong keys?). See the backend terminal")

        devices = []

        for data in json.loads(TUYA_DEVICES_FILE.read_text(encoding="utf-8")):
            if not data.get("id"):
                continue

            devices.append(Device(
                id=data["id"],
                name=data.get("name") or "",
                type="lamp" if data.get("category") == "dj" else "unknown",  # dj = light
                source="tuya",
                address=data.get("ip") or None,             # empty if the local scan didn't find it
                local_key=data.get("key") or None,
                version=str(data["version"]) if data.get("version") else None,
            ))

        return devices

    def _fetch_zigbee(self) -> list[Device]:
        """Read every device on the Innr bridge (same as `python -m zigbee.zigbee_remote devices`),
        through the dongle connection the loaded devices already share."""
        from zigbee.zigbee_remote import SharedZigbeeRemote, DEFAULT_DEVICES_FILE

        zigbee = SharedZigbeeRemote.get()
        data = zigbee.run(zigbee.remote.read_devices(DEFAULT_DEVICES_FILE), timeout=ZIGBEE_READ_TIMEOUT)

        if data is None:
            raise RuntimeError("Zigbee dongle isn't joined to the bridge. Run: python -m zigbee.zigbee_remote join")

        devices = []

        for zb in data.get("devices", []):
            ieee = zb.get("ieee")
            if not ieee:
                continue

            device = Device(id=ieee, name="", type="unknown", source="zigbee", address=zb["nwk"])

            # A device that didn't answer only tells us its address, so leave the rest as it is
            if "endpoints" in zb:
                if zb.get("is_light"):
                    device.type = "lamp"
                elif zb.get("role") == "Coordinator":
                    device.type = "bridge"

                device.version = zb.get("sw_build_id")

                endpoint, clusters = self._zigbee_main_endpoint(zb)
                color = clusters.get("0x0300", {}).get("attributes", {})
                temp_min = color.get("color_temp_physical_min", {}).get("value")
                temp_max = color.get("color_temp_physical_max", {}).get("value")

                device.extra = {
                    "endpoint": endpoint,
                    "capabilities": zb.get("capabilities", []),
                    "color_temp_mireds": [temp_min, temp_max] if temp_min and temp_max else None,
                    "groups": zb.get("groups", []),
                    "manufacturer": zb.get("manufacturer"),
                    "model": zb.get("model"),
                }
            else:
                device.extra = None  # unknown, see _compare

            devices.append(device)

        return devices

    @staticmethod
    def _zigbee_main_endpoint(zb):
        """(endpoint number, its input clusters): the one with On/Off, else the first one."""
        endpoints = zb.get("endpoints", {})
        for ep, data in endpoints.items():
            if "0x0006" in data.get("in_clusters", {}):
                return int(ep), data["in_clusters"]
        for ep, data in endpoints.items():
            return int(ep), data.get("in_clusters", {})
        return None, {}

    # ---------- comparing ----------

    @staticmethod
    def _compare(current: Device | None, fetched: Device) -> dict | None:
        """What would change in the database. None if nothing would."""
        if current is None:
            if fetched.extra is None:
                fetched.extra = {}
            fields = [
                {"field": field, "old": None, "new": getattr(fetched, field)}
                for field in ("name", "type", "address", "local_key", "version")
                if getattr(fetched, field)
            ]
            fields += [{"field": f"extra.{key}", "old": None, "new": value} for key, value in fetched.extra.items()]
            return {"status": "new", "row": fetched, "fields": fields}

        # Only what the fetch actually knows. The name stays (it's set in the app), and
        # missing values (e.g. no ip because the scan didn't find it) don't wipe the stored ones.
        updates = {}

        for field in ("type", "address", "local_key", "version"):
            value = getattr(fetched, field)
            if value and value != "unknown" and value != getattr(current, field):
                updates[field] = value

        fields = [{"field": field, "old": getattr(current, field), "new": value} for field, value in updates.items()]

        if fetched.extra is not None:
            old_extra = current.extra or {}
            new_extra = {**old_extra, **{k: fetched.extra[k] for k in ZIGBEE_KEEP if k in fetched.extra}}

            if new_extra != old_extra:
                updates["extra"] = new_extra
                fields += [
                    {"field": f"extra.{key}", "old": old_extra.get(key), "new": value}
                    for key, value in new_extra.items()
                    if old_extra.get(key) != value
                ]

        if not updates:
            return None

        return {"status": "changed", "updates": updates, "fields": fields}

    # ---------- status ----------

    def get_status(self) -> dict:
        with self._lock:
            current = {row.id: row for row in DeviceReader().get_all_devices()} if self._pending else {}

            changes = []
            for device_id, change in self._pending.items():
                row = current.get(device_id) or change.get("row")
                changes.append({
                    "id": device_id,
                    "name": row.name if row else "",
                    "source": row.source if row else None,
                    "status": change["status"],
                    "fields": [self._hide_secret(field) for field in change["fields"]],
                })

            return {
                "state": self.state,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "errors": dict(self.errors),
                "changes": changes,
            }

    @staticmethod
    def _hide_secret(field: dict) -> dict:
        if field["field"] in SECRET_FIELDS:
            return {**field, "old": "***" if field["old"] else None, "new": "***" if field["new"] else None}
        return field

    # ---------- applying ----------

    def apply(self, device_ids: list[str]) -> int:
        """Save the chosen changes, then restart every device with the new data.
        Returns how many devices were saved."""
        with self._lock:
            if self.state != "done":
                raise RuntimeError("Nothing to apply, fetch the devices first")

            chosen = [(device_id, self._pending[device_id]) for device_id in device_ids if device_id in self._pending]

            with Session(engine) as session:
                for device_id, change in chosen:
                    if change["status"] == "new":
                        session.add(change["row"])
                        continue

                    device = session.get(Device, device_id)
                    if device is None:
                        continue

                    for field, value in change["updates"].items():
                        setattr(device, field, value)
                    session.add(device)

                session.commit()

            # Changes not chosen are dropped; fetch again to see them again
            self._pending = {}
            self.state = "idle"

        # The address/key/etc. might have changed, so stop everything and connect again
        self.device_handler.restart_devices()

        return len(chosen)
