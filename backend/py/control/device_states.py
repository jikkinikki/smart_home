"""
The devices' current values (power, brightness, ...), kept in memory so they can be
handed out right away instead of asking every device each time.

    device_states = DeviceStates(device_handler)
    device_states.start()                        # reads every device now, then every few seconds
    device_states.get(["a4:c1:38:9e:4e:72:45:7b"])  # [{"id", "power", "brightness", "temperature", "color", "mode"}]
    device_states.remember(device, {"brightness": 40})  # after a value was sent to the device

A device that doesn't answer keeps its last known values.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

from config.settings import DEVICE_STATE_REFRESH_SECONDS

UNKNOWN_STATE = {"power": None, "brightness": None, "temperature": None, "color": None, "mode": None}


class DeviceStates:
    def __init__(self, device_handler, refresh_seconds: float = DEVICE_STATE_REFRESH_SECONDS):
        self.device_handler = device_handler
        self.refresh_seconds = refresh_seconds
        self._states: dict[str, dict] = {}  # device id -> state
        self._lock = threading.Lock()

    def start(self):
        threading.Thread(target=self._refresh_forever, daemon=True).start()

    def _refresh_forever(self):
        self.device_handler.wait_until_loaded()

        while True:
            self.refresh(self._shown_devices())
            time.sleep(self.refresh_seconds)

    def _shown_devices(self, ids: list[str] | None = None) -> list:
        devices = [device for device in self.device_handler.getAllDevices() if not device.hidden]

        if ids is not None:
            devices = [device for device in devices if device.id in ids]

        return devices

    def refresh(self, devices: list):
        """Read these devices now. All at once, so one that doesn't answer doesn't hold up the rest."""
        if not devices:
            return

        with ThreadPoolExecutor(max_workers=len(devices)) as pool:
            list(pool.map(self._refresh_device, devices))

    def _refresh_device(self, device):
        get_state = getattr(device, "get_state", None)
        if not get_state:
            return

        # Saved while holding the lock, so a read that started before a command
        # can't overwrite the value the command remembered
        with device.connection_lock:
            try:
                state = get_state()
            except Exception as exc:
                print(f"Couldn't read the state of {device.get_device_name() or device.id}: {exc.__class__.__name__}: {exc}")
                return

            if state is not None:
                with self._lock:
                    self._states[device.id] = state

    def get(self, ids: list[str] | None = None) -> list[dict]:
        """The known values of the shown devices (ids = only these). A device that hasn't been read yet is read now."""
        devices = self._shown_devices(ids)

        with self._lock:
            not_read_yet = [device for device in devices if device.id not in self._states]

        self.refresh(not_read_yet)

        with self._lock:
            return [{"id": device.id, **self._states.get(device.id, UNKNOWN_STATE)} for device in devices]

    def remember(self, device, values: dict):
        """Values that were just sent to the device, e.g. {"brightness": 40, "color": [255, 0, 0]}."""
        with self._lock:
            state = self._states.setdefault(device.id, dict(UNKNOWN_STATE))
            state.update(values)

            # Color is sent after temperature, so it's the one the lamp ends up showing
            if "color" in values:
                state["mode"] = "color"
            elif "temperature" in values:
                state["mode"] = "temperature"
