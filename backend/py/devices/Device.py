import threading


class Device:
    def __init__(self):
        # One command or state read at a time, so their replies don't get mixed up
        self.connection_lock = threading.Lock()
        self._is_ready = False
        self.allow_auto_updates = True
        self._device_name = ""
        self.id = None
        self.type = None
        self.hidden = False  # not shown in device control
        self.room_id = None  # the room it's in (room.id in the database)
        self.vertical = None  # how high up it's placed: "low", "medium", "high"

    def is_ready(self) -> bool:
        return self._is_ready

    def get_device_name(self) -> str:
        return self._device_name

    def set_device_name(self, name: str):
        self._device_name = name

    def load_device(self, jsonData: dict):
        self._device_name = jsonData["device_name"]
        self.id = jsonData.get("dev_id")
        self.type = jsonData.get("type")
        self.hidden = jsonData.get("hidden", False)
        self.room_id = jsonData.get("room_id")
        self.vertical = jsonData.get("vertical")

    def close(self):
        """Close the connection to the device. Override if the device keeps one open."""
        self._is_ready = False

    def set_allow_auto_updates(self, allow: bool):
        self.allow_auto_updates = allow