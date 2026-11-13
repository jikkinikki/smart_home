import threading
from contextlib import asynccontextmanager

import control.device_commands as dc
import control.device_handler as dh
import automation.que_reader as qr
import automation.Lamp_cycle as lc

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import devices


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

    que_reader = qr.Que_reader(
        device_commands,
        device_handler
    )

    # Share instances with API routers
    app.state.device_handler = device_handler
    app.state.device_commands = device_commands

    # Start background tasks
    multithread(que_reader.read_que)

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