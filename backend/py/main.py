import threading
from contextlib import asynccontextmanager

import control.device_commands as dc
import control.device_handler as dh

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import db_devices, device_refetch, devices, rooms
from control.device_refetch import DeviceRefetch
from utils.startup_reporter import StartupReporter


def multithread(func):
    thread = threading.Thread(target=func, daemon=True)
    thread.start()
    return thread


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize smart home system
    device_handler = dh.DeviceHandler()
    device_commands = dc.DeviceCommands(device_handler)

    device_commands.set_device_selector("all")

    # Share instances with API routers
    app.state.device_handler = device_handler
    app.state.device_commands = device_commands
    app.state.device_refetch = DeviceRefetch(device_handler)

    StartupReporter(device_handler).start()

    yield

    # Shutdown cleanup goes here


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router, prefix="/api")
app.include_router(db_devices.router, prefix="/api")
app.include_router(device_refetch.router, prefix="/api")
app.include_router(rooms.router, prefix="/api")