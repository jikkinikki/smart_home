import json
import tinytuya
import time

import threading
from pathlib import Path

from config.paths import JSON_DIR

import devices.TuyaLamp as TuyaLamp
import devices.InnrLamp as InnrLamp
import devices.Device as Device

# type -> source -> function that creates an (unloaded) device
device_loader_map = {

    "lamp": {

        "tuya": lambda: TuyaLamp.TuyaLamp(True),
        "zigbee": InnrLamp.InnrLamp,
    }
}

JSON_FOLDER = JSON_DIR
DEVICES_FILE = JSON_FOLDER / "devices.json"
ZIGBEE_DEVICES_FILE = JSON_FOLDER / "zigbee_devices.json"  # written by: python -m zigbee.zigbee_remote devices

class DeviceHandler:
    def __init__(self):
        self._allDevices = []
        self.devices_lock = threading.Lock()
        self.patch_devices()
        self.patch_zigbee_devices()
        self.load_devices(False)

    def clone_dict(self, dict):
        return dict.copy()
        # return json.loads(json.dumps(dict, default=lambda o: o.__dict__))

    # Starts and runs seperate thread
    def load_devices(self, debug_info = False):
        with open(DEVICES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            self.devices_loading = 0
            threads = []

            i = 0

            for device in data:
                if debug_info:
                    print(device)

                if device["device_name"] == "all_devices":
                    continue

                label = device["device_name"] or device.get("dev_id")

                if device.get("custom_data", {}).get("disabled"):
                    print("disabled, not loading:", label)
                    continue

                if device_loader_map.get(device.get("type"), {}).get(device.get("source")) is None:
                    print("no loader for", device.get("type"), device.get("source"), "- skipping", label)
                    continue

                # Placeholder until the real device has loaded in its thread
                temp_device = Device.Device()
                temp_device._device_name = device["device_name"]
                temp_device.id = device.get("dev_id")
                temp_device.type = device.get("type")
                self._allDevices.append(temp_device)

                threads.append(threading.Thread(target=self.load_device, args=(i, device, debug_info)))
                self.devices_loading += 1
                i += 1

            self.start_time = time.time()
            self._load_threads = threads

            for thread in threads:
                thread.start()

            # for thread in threads:
                # thread.join()

            print("")
            print("Devices loaded:")

    def patch_devices(self, debug_info = False):
        new_json_data = {}
        old_json_data = {}

        with open("snapshot.json", "r") as f:
            if debug_info:
                print("snapshot:", f)
            new_json_data = json.load(f)

        with open(DEVICES_FILE, "r") as f:
            old_json_data = json.load(f)

        json_data_filtered = []

        for device in new_json_data["devices"]:

            if debug_info:
                print(device)
                print("")

            json_data_filtered.append({

                "name": device["name"],
                "ip": device["ip"],
                "local_key": device["key"],
                "dev_id": device["id"],
                "key": device["key"],
                "version": device["ver"]
            })

        if debug_info:
            print("")
            print(old_json_data)
            print("")

        for device_base in old_json_data:
            for device_new in json_data_filtered:

                if debug_info:
                    print("")
                    print(device_base["device_name"].replace("_", " "), device_new["name"])
                if(device_base["device_name"].replace("_", " ") == device_new["name"]):

                    if debug_info:
                        print("match")
                    device_base["address"] = device_new["ip"]
                    device_base["local_key"] = device_new["local_key"]
                    device_base["dev_id"] = device_new["dev_id"]
                    device_base["version"] = device_new["version"]
                

        if debug_info:
            print(json_data_filtered)

        with open(DEVICES_FILE, "w") as f:
            f.write(json.dumps(old_json_data))

        if debug_info:
            print("")

    def patch_zigbee_devices(self, debug_info = False):
        """
        Patch every device in zigbee_devices.json into devices.json.

        Devices are matched on their IEEE address (dev_id), which never changes. A device
        already in devices.json keeps its device_name; a new device is added with an empty
        device_name for you to fill in. A device that didn't answer during the last read
        only gets its address updated, so known info isn't wiped.
        """
        if not ZIGBEE_DEVICES_FILE.exists():
            if debug_info:
                print("No zigbee_devices.json, skipping zigbee patch")
            return

        zigbee_data = json.loads(ZIGBEE_DEVICES_FILE.read_text(encoding="utf-8"))
        devices = json.loads(DEVICES_FILE.read_text(encoding="utf-8"))

        for zb in zigbee_data.get("devices", []):
            ieee = zb.get("ieee")
            if not ieee:
                continue

            entry = next((d for d in devices if d.get("dev_id") == ieee), None)
            if entry is None:
                entry = {
                    "device_name": "",
                    "type": "unknown",
                    "source": "zigbee",
                    "address": None,
                    "dev_id": ieee,
                    "version": None,
                    "custom_data": {"disabled": False},
                    "zigbee": {},
                }
                devices.append(entry)
                if debug_info:
                    print("added", ieee)
            elif debug_info:
                print("updated", entry["device_name"] or ieee)

            reachable = "endpoints" in zb
            info = entry.setdefault("zigbee", {})
            entry["address"] = zb["nwk"]  # short network address, can change after a rejoin
            info.update({"nwk": zb["nwk"], "ieee": ieee, "role": zb.get("role"), "reachable": reachable})

            if not reachable:
                continue

            if zb.get("is_light"):
                entry["type"] = "lamp"
            elif zb.get("role") == "Coordinator":
                entry["type"] = "bridge"

            if zb.get("sw_build_id"):
                entry["version"] = zb["sw_build_id"]

            endpoint, clusters = self._zigbee_main_endpoint(zb)
            color = clusters.get("0x0300", {}).get("attributes", {})
            temp_min = color.get("color_temp_physical_min", {}).get("value")
            temp_max = color.get("color_temp_physical_max", {}).get("value")

            info.update({
                "endpoint": endpoint,
                "manufacturer": zb.get("manufacturer"),
                "model": zb.get("model"),
                "sw_build_id": zb.get("sw_build_id"),
                "date_code": zb.get("date_code"),
                "power_source": zb.get("power_source"),
                "capabilities": zb.get("capabilities", []),
                "groups": zb.get("groups", []),
                "in_clusters": sorted(clusters),
                "color_temp_mireds": [temp_min, temp_max] if temp_min and temp_max else None,
                "last_read": zigbee_data.get("read_at"),
            })

        DEVICES_FILE.write_text(json.dumps(devices, indent=2, ensure_ascii=False), encoding="utf-8")

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

    def wait_until_loaded(self, timeout = 60):
        """Block until every device thread has finished loading (or failed)."""
        end = time.time() + timeout
        for thread in getattr(self, "_load_threads", []):
            thread.join(max(0, end - time.time()))

    def load_device(self, device_index, device_data, debug_info = False):

        type = device_data["type"]
        source = device_data["source"]
        label = device_data["device_name"] or device_data.get("dev_id")

        try:
            create_device = device_loader_map[type][source]
            device = create_device()
            device.load_device(device_data)

            with self.devices_lock:
                self._allDevices[device_index] = device
                self.devices_loading -= 1
                print("waiting for devices: ", self.devices_loading, "time waited: ", time.time() - self.start_time)

            self.printDevicesStatus("all")

        except Exception as e:
            print("failed to load", label, f"({type} {source}):", f"{e.__class__.__name__}: {e}")
            with self.devices_lock:
                self.devices_loading -= 1
        
        # return device
   
    def getDeviceById(self, id):

        with self.devices_lock:
            for device in self._allDevices:
                if device.id == id:
                    return device
                
        return "null"
    
    def getAllDevices(self):
        devices = []
        all_devices = self.clone_dict(self._allDevices)

        for device in all_devices:
            if device.is_ready():
                devices.append(device)
        
        return devices

    def getSelectedDevices(self, selector, get_not_ready = False):

        devices = []
        
        with self.devices_lock:
            if selector == "all":
                all_devices = self.clone_dict(self._allDevices)

                for device in all_devices:
                    if device.is_ready() or get_not_ready:
                        devices.append(device)
            
            else:
                deviceFromId = self.getDeviceById(selector)
                if deviceFromId == "null":
                    return []
                else:
                    devices.append(deviceFromId)
            
        return devices

    def printDevicesStatus(self, selector):

        devices = self.getSelectedDevices(selector, True)

        print()
        print("-------------------")

        for device in devices:

            if device.is_ready():
                print("\033[0m", device.get_device_name(), "\033[1;32m ready")
            else:
                print("\033[0m", device.get_device_name(), "\033[1;31m loading")

        print("\033[0m-------------------")
        print() 

    def printDevicesInfo(self, selector):

        devices = self.getSelectedDevices(selector)

        print()
        print("-------------------")

        for device in devices:

            if hasattr(device, "status"):
                print(device.get_device_name() or device.id, device.status())
            else:
                print(device)

        print("-------------------")
        print()

if(__name__ == "__main__"):
    deviceHandler = DeviceHandler()
    deviceHandler.wait_until_loaded()  # devices load in threads; don't exit before they're done
    deviceHandler.printDevicesInfo("all")
    