# https://github.com/jasonacox/tinytuya - tinytuya
# python -m tinytuya wizard  - find devices on network
# "Y`n" * 3 | python -m tinytuya wizard

import time
import threading

import device_commands as dc
import device_handler as dh
import que_reader as qr
import Lamp_cycle as lc

def multithread(func):
        background_thread = threading.Thread(target=func, daemon=True)
        background_thread.start()

        return background_thread

device_handler = dh.DeviceHandler()
device_commands = dc.DeviceCommands(device_handler)
# lamp_cycle = lc.Lamp_cycle(device_handler, "all", device_commands)

device_commands.set_device_selector("all")

que_reader = qr.Que_reader(device_commands, device_handler)

multithread(que_reader.read_que)
# multithread(lamp_cycle.loop)

while True:
    time.sleep(5)
#     print("main loop")