class Device:
    def __init__(self):
        self._is_ready = False
        self.allow_auto_updates = True
        self._device_name = ""
        self.id = None
        self.type = None
        self.hidden = False  # not shown in device control

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

    def close(self):
        """Close the connection to the device. Override if the device keeps one open."""
        self._is_ready = False

    def set_allow_auto_updates(self, allow: bool):
        self.allow_auto_updates = allow