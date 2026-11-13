from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/devices")
def get_devices():
    return [
        {"id": 1, "name": "Living Room", "isOn": True},
        {"id": 2, "name": "Bedroom", "isOn": False}
    ]