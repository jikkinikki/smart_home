import os
import json
import time

class Que_reader():
    def __init__(self, device_commands, device_handler):
        self.device_commands = device_commands
        self.device_handler = device_handler

        self.action_functions = {
            "brightness": self.device_commands.set_lamps_brightness,
            "temp": self.device_commands.set_lamps_temperature,
            "color": self.device_commands.set_lamps_RGB,
            "switch_power": self.device_commands.switch_power
        }

    def is_int(self, value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False

    def is_float(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False


    def smart_parse(self, value: str) -> int | float | str:
        if self.is_int(value):
            return int(value)
        elif self.is_float(value):
            return float(value)
        else:
            return value

    def run_file(self, file_path):
        with open(file_path, "r") as file:
            try:
                jsonDevices = json.load(file)
                devicesToUpdate = self.device_handler.getSelectedDevices(jsonDevices["device_id"])

                if len(devicesToUpdate) == 0:
                    return

                self.action_functions[jsonDevices["action"]](self.smart_parse(jsonDevices["value"]), True)

            except json.JSONDecodeError as e:
                print(f"Error reading {filename}: {e}")

    def read_que(self):
        que_path = "../change_que" 

        scriptFolder = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(scriptFolder, que_path)

        print("starting que listener\n")

        while True:

            # for filename in os.listdir(folder_path):

            dc = self.device_commands

            filenames = os.listdir(folder_path)
            sorted_filenames = sorted(filenames, key=lambda f: os.path.getctime(os.path.join(folder_path, f)))

            while len(sorted_filenames) > 0:

                filename = sorted_filenames.pop(0)
                # filename = sorted_filenames[0]

                if filename.endswith(".json"):
                    file_path = os.path.join(folder_path, filename)
                    # print("loop")
                    # print(file_path)
                    
                    self.run_file(file_path)
                    os.remove(file_path)
            
            time.sleep(.1)

    def hexToRGB(self, hex):
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))