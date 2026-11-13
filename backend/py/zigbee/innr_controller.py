"""
Controls the Innr (Zigbee) lamps listed in devices.json.

Use the shared instance, not a new InnrController:

    from zigbee.innr_controller import innr_controller

    innr_controller.turn_on("desk")                        # by device_name
    innr_controller.turn_off(["0x4F53", "0x751B"])         # a list of short addresses
    innr_controller.toggle("a4:c1:38:9e:4e:72:45:7b")      # by IEEE address
    innr_controller.set_brightness("all", 40)              # 'all' (or None) = every lamp
    innr_controller.set_color(["0xC799"], "#ff8800")
    innr_controller.run("temp", ["0x4F53", "0xCD16"], 20)  # any action by name
    innr_controller.status()                               # {lamp: state} for every lamp

    Actions for run(): on, off, toggle, switch_power, brightness, temp, color, status

The lamps (and the USB dongle connection) are only loaded on first use.
"""

import json
import threading
from pathlib import Path

from config.paths import JSON_DIR
from devices.InnrLamp import InnrLamp

DEVICES_FILE = JSON_DIR / "devices.json"


class InnrController:
    def __init__(self, devices_file=DEVICES_FILE):
        self.devices_file = Path(devices_file)
        self._lamps: list[InnrLamp] = []
        self._loaded = False
        self._lock = threading.Lock()

    # ---------- lamps ----------

    def load(self):
        """(Re)load the Innr lamps from devices.json."""
        with self._lock:
            entries = json.loads(self.devices_file.read_text(encoding="utf-8"))
            lamps = []
            for entry in entries:
                if entry.get("source") != "zigbee" or entry.get("type") != "lamp":
                    continue
                if entry.get("custom_data", {}).get("disabled"):
                    continue
                lamp = InnrLamp()
                lamp.load_device(entry)
                lamps.append(lamp)
            self._lamps = lamps
            self._loaded = True

    def get_lamps(self) -> list[InnrLamp]:
        if not self._loaded:
            self.load()
        return list(self._lamps)

    def get_lamp(self, lamp) -> InnrLamp:
        """Find a lamp by device_name, IEEE address ('a4:c1:...') or short address ('0x4F53')."""
        if isinstance(lamp, InnrLamp):
            return lamp

        ref = str(lamp).strip().lower()
        for candidate in self.get_lamps():
            if ref and ref == candidate.get_device_name().lower():
                return candidate
            if ref == candidate.ieee.lower():
                return candidate
            if ref.startswith("0x") and int(ref, 16) == candidate.nwk:
                return candidate

        known = ", ".join(self.lamp_label(l) for l in self.get_lamps()) or "none"
        raise ValueError(f"Unknown Innr lamp '{lamp}'. Known lamps: {known}")

    def select(self, lamps=None) -> list[InnrLamp]:
        """
        lamps: None or 'all' = every lamp; one address; or a list of addresses.
        An address is a device_name, an IEEE address, '0x4F53' or the number 0x4F53.
        """
        if lamps is None or (isinstance(lamps, str) and lamps.lower() == "all"):
            return self.get_lamps()
        if not isinstance(lamps, (list, tuple, set)):
            lamps = [lamps]
        return [self.get_lamp(f"0x{l:04X}" if isinstance(l, int) else l) for l in lamps]

    @staticmethod
    def lamp_label(lamp: InnrLamp) -> str:
        return lamp.get_device_name() or f"0x{lamp.nwk:04X}"

    # ---------- actions ----------
    # Every action takes (lamps, value). lamps = one address, a list of addresses,
    # or None/'all' for every lamp. Actions without a value ignore it.

    def run(self, action: str, lamps=None, value=None, nowait: bool = False):
        """Run an action by name, e.g. run('brightness', ['0x4F53', 'desk'], 40)."""
        actions = self.get_actions()
        if action not in actions:
            raise ValueError(f"Unknown action '{action}'. Actions: {', '.join(actions)}")
        return actions[action]["func"](lamps, value, nowait=nowait)

    def get_actions(self) -> dict:
        """{name: {desc, func}}. que_reader uses the same names (brightness, temp, color, switch_power)."""
        return {
            "on": {"desc": "turn on", "func": lambda lamps, value=None, nowait=False: self.turn_on(lamps, nowait=nowait)},
            "off": {"desc": "turn off", "func": lambda lamps, value=None, nowait=False: self.turn_off(lamps, nowait=nowait)},
            "toggle": {"desc": "toggle on/off", "func": lambda lamps, value=None, nowait=False: self.toggle(lamps, nowait=nowait)},
            "switch_power": {"desc": "power, value 'on' or 'off'", "func": self.switch_power},
            "brightness": {"desc": "brightness, value 0-100", "func": self.set_brightness},
            "temp": {"desc": "colour temperature, value 0 (warm) - 100 (cool)", "func": self.set_temperature},
            "color": {"desc": "colour, value (r, g, b) or '#rrggbb'", "func": self.set_color},
            "status": {"desc": "read the current state", "func": lambda lamps, value=None, nowait=False: self.status(lamps)},
        }

    def turn_on(self, lamps=None, nowait: bool = False):
        for lamp in self.select(lamps):
            lamp.turn_on(nowait=nowait)

    def turn_off(self, lamps=None, nowait: bool = False):
        for lamp in self.select(lamps):
            lamp.turn_off(nowait=nowait)

    def toggle(self, lamps=None, nowait: bool = False):
        for lamp in self.select(lamps):
            lamp.toggle(nowait=nowait)

    def switch_power(self, lamps=None, power="on", nowait: bool = False):
        """power: 'on'/'off' (or True/False)."""
        on = power is True or str(power).lower() in ("on", "true", "1")
        if on:
            self.turn_on(lamps, nowait=nowait)
        else:
            self.turn_off(lamps, nowait=nowait)

    def set_brightness(self, lamps=None, brightness: int = 100, nowait: bool = False):
        for lamp in self.select(lamps):
            lamp.set_brightness(int(brightness), nowait=nowait)

    def set_temperature(self, lamps=None, temperature: int = 50, nowait: bool = False):
        for lamp in self.select(lamps):
            lamp.set_temperature(int(temperature), nowait=nowait)

    def set_color(self, lamps=None, color=(255, 255, 255), nowait: bool = False):
        """color: (r, g, b) or a hex string like '#ff8800'."""
        if isinstance(color, str):
            hex_color = color.lstrip("#")
            color = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        for lamp in self.select(lamps):
            lamp.set_color(tuple(color), nowait=nowait)

    def status(self, lamps=None) -> dict:
        """{lamp label: state}. A lamp that doesn't answer gets {'error': ...}."""
        result = {}
        for lamp in self.select(lamps):
            try:
                result[self.lamp_label(lamp)] = lamp.status()
            except Exception as exc:
                result[self.lamp_label(lamp)] = {"error": f"{exc.__class__.__name__}: {exc}"}
        return result


# The one instance the rest of the program uses
innr_controller = InnrController()
