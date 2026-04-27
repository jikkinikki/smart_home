# http://localhost/smart_home/
# python -m tinytuya wizard

# from scapy.all import sniff
import inspect
import tinytuya
import math
import datetime
import time
import os
import json
import threading
import remote
import assistant_main as Assistant
from gpt import Gpt
from print_handler import PrintHandler
from device_commands import commands
from device_handler import DeviceHandler
import device_commands as dc

assistant = Assistant.Assistant()
gpt = Gpt()
print_handler = PrintHandler()
device_handler = DeviceHandler()

print("start")
allDevices = []

remote_ip = "192.168.1.119"
 
is_ambient = False
ambient_start = 16
ambient_end = 24
 
# scriptFolder = os.path.dirname(os.path.abspath(__file__))
# relDevicesPath = "../json/devices.json"

# # def read_new_mail():

# absDevicesPath = os.path.join(scriptFolder, relDevicesPath)

# with open(absDevicesPath, "r") as devicesFile:
    
#     jsonDevices = json.load(devicesFile)

#     for jsonDevice in jsonDevices:

#         if jsonDevice["version"]  == -1 or ("disabled" in jsonDevice["custom_data"] and jsonDevice["custom_data"]["disabled"]):
#             continue

#         print("adding" , jsonDevice["device_name"])
#         addDevice(jsonDevice["type"], jsonDevice["dev_id"], jsonDevice["address"], jsonDevice["local_key"], jsonDevice["version"], jsonDevice["custom_data"])

print("device added\n")

print(allDevices)

def curved0To1(valueIn, strength):
    return valueIn ** (math.e*strength)

def hexToRGB(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def multiThread(func):
    background_thread = threading.Thread(target=func, daemon=True)
    background_thread.start()

    return background_thread

def queListener():
    que_path = "../change_que" 

    folder_path = os.path.join(scriptFolder, que_path)

    print("starting que listener\n")

    while True:
        # for filename in os.listdir(folder_path):

        filenames = os.listdir(folder_path)
        sorted_filenames = sorted(filenames, key=lambda f: os.path.getctime(os.path.join(folder_path, f)))

        while len(sorted_filenames) > 0:

            filename = sorted_filenames.pop(0)
            # filename = sorted_filenames[0]

            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                # print("loop")
                # print(file_path)
                with open(file_path, "r") as file:
                    try:
                        jsonDevices = json.load(file)
                        devicesToUpdate = getSelectedDevices(jsonDevices["device_id"])

                        if len(devicesToUpdate) == 0:
                            continue

                        if jsonDevices["action"] == "brightness":
                            dc.changeLampsBrighness(int(jsonDevices["value"]), devicesToUpdate, True)

                        elif jsonDevices["action"] == "temp":
                            dc.changeLampsTemp(int(jsonDevices["value"]), devicesToUpdate, True)

                        elif jsonDevices["action"] == "color":

                            color = hexToRGB(jsonDevices["value"])
                            dc.changeLampsRGB(color[0], color[1], color[2], devicesToUpdate, True, True)

                        elif jsonDevices["action"] == "switch_power":
                            if jsonDevices["value"] == "on":
                                dc.turnOnAllDevices(devicesToUpdate, True)
                            elif jsonDevices["value"] == "off":
                                dc.turnOffAllDevices(devicesToUpdate, True)

                        # print(f"Processing {filename}: {jsonDevices}")
                    except json.JSONDecodeError as e:
                        print(f"Error reading {filename}: {e}")

                os.remove(file_path)
        
        time.sleep(.1)

def loop_ambient():

    print(f"looping ambient. Ambient status: ${is_ambient}")

    while True:

        if not is_ambient:
            time.sleep(5)
            continue

        now = datetime.datetime.now()

        if ambient_start <= now.hour <= ambient_end:

            delta_now = now.hour - ambient_start
            percent = ambient_end/delta_now

            print(round(percent))

            dc.changeLampsBrighness(round(percent), allDevices, True)
            dc.changeLampsTemp(round(percent), allDevices, True)

        time.sleep(5)

def singAsong(song):
    assistant.speak(song)

def commandListener():

    print("commands added")

    while True:

        i = 0

        command_str = "Commands: \n"

        for command in commands:
            command_str += f"{i}: {command['desc']} \n"
            i += 1

        # print(command_str)
        print_handler.add_str(command_str, "commands", 0, True)

        action = input("enter option: ")

        option = int(action)

        commands[option]["func"]()

def loop_assistant():

    while True:
        
        print("listening...")
        text = assistant.get_audio()
        print(text)
        text = text.lower()

        if "bixby" in text:
            # assistant.speak("Hello Oskar!")
        
            response = gpt.complete(text, commands)
            print(response["command_id"])
            print(commands[int(response["command_id"])])
            cmd_id = int(response["command_id"])

            func_key = "ai_func" if "ai_func" in commands[cmd_id] else "func"

            if cmd_id != -1:

                print("running command")

                if "parameters" in response:
                    print("params:", response["parameters"])

                    for key in commands[cmd_id]:
                        print(key)

                    response["parameters"] = response["parameters"][:inspect.signature(commands[cmd_id][func_key]).parameters.__len__()]

                    commands[cmd_id][func_key](*response["parameters"])

                else:
                    commands[cmd_id][func_key]()

            else:
                if len(response["explanation"]) > 143:
                    response["explanation"] = response["explanation"][:143]
                    print("reduced explanation to: ", response["explanation"])

                assistant.speak(response["explanation"])

# background_thread = threading.Thread(target=queListener, daemon=True)
# background_thread.start()

# background_thread = threading.Thread(target=loop_ambient, daemon=True)
# background_thread.start()

# background_thread = threading.Thread(target=commandListener, daemon=True)
# background_thread.start()

# multiThread(queListener)
# multiThread(loop_ambient)
multiThread(commandListener)

# background_thread = threading.Thread(target=loop_assistant, daemon=True)
# background_thread.start()

print("running que listener\n")
print("running command listener")

loop_assistant()

while True:
    time.sleep(1)

# commandListener()