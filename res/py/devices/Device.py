class Device:
    def __init__(self):
        self._is_ready = False
        self._device_name = ""

    def is_ready(self) -> bool:
        return self._is_ready

    def get_device_name(self) -> str:
        return self._device_name

    def load_device(self, jsonData: dict):
        self._device_name = jsonData["device_name"]