import json
import tinytuya
import time

import threading

import devices.TuyaLamp as TuyaLamp
import devices.Device as Device

class DeviceHandler:
    def __init__(self):
        self._allDevices = []
        self.devices_lock = threading.Lock()
        self.patch_devices()
        self.load_devices(False)

    def clone_dict(self, dict):
        return dict.copy()
        # return json.loads(json.dumps(dict, default=lambda o: o.__dict__))

    # Runs on seperate thread
    def load_devices(self, debug_info = False):
        with open("res/json/devices.json", "r") as f:
            data = json.load(f)

            self.devices_loading = 0
            threads = []

            i = 0

            for device in data:
                if debug_info:
                    print(device)

                if device["device_name"] != "all_devices":
                    temp_device = Device.Device()
                    temp_device._device_name = device["device_name"]
                    self._allDevices.append(temp_device)
                    # self._allDevices.append({"loading": device["device_name"]})

                    threads.append(threading.Thread(target=self.loadDevice, args=(i, device, debug_info)))
                    self.devices_loading += 1
                    i += 1

            self.start_time = time.time()

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

        with open("res/json/devices.json", "r") as f:
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

        with open("res/json/devices.json", "w") as f:
            f.write(json.dumps(old_json_data))

        if debug_info:
            print("")

    def loadDevice(self, device_index, device_data, debug_info = False):

        device = ""

        # if debug_info:
            # print("device_info: ", device_type, id, adress, localKey, version, customData)

        connection_timeout = 3
        # adress = "Auto"

        # elif device_type == "outlet":
        #     device = tinytuya.OutletDevice(
        #     dev_id=id,
        #     address=adress,
        #     local_key=localKey,
        #     version=version,
        #     connection_timeout=connection_timeout
        #     )

        # if debug_info:
        #     print(device_name, device.status())

        if device_data["source"] == "tuya":
            if device_data["type"] == "lamp":
                device = TuyaLamp.TuyaLamp(True)

        device.load_device(device_data)

        self.devices_loading -= 1
        print("waiting for devices: ", self.devices_loading, "time waited: ", time.time() - self.start_time)

        # if "Error" in device.status():
            # return
        
        # customData["type"] = device_type 
        
        # device.customData = customData 
        # device.device_name = device_name
        # device.set_socketPersistent(True)
        
        with self.devices_lock:
            self._allDevices[device_index] = device
        
        # self.printDevicesInfo("all")
        self.printDevicesStatus("all")
        
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
                print(device.device_name, device.status())
            else:
                print(device)

        print("-------------------")
        print()

if(__name__ == "__main__"):
    deviceHandler = DeviceHandler()
    deviceHandler.printDevicesInfo("all")
    