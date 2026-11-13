import threading


class StartupReporter:
    """Prints backend startup info to the terminal once the devices have finished loading."""

    def __init__(self, device_handler, timeout: int = 60):
        self.device_handler = device_handler
        self.timeout = timeout

    def start(self):
        # Devices load in background threads, so wait for them without blocking startup
        threading.Thread(target=self._report, daemon=True).start()

    def _report(self):
        self.device_handler.wait_until_loaded(timeout=self.timeout)

        total = len(self.device_handler._allDevices)
        ready = len(self.device_handler.getAllDevices())

        if total == 0:
            print("[startup] WARNING: no devices to load. Check backend/json/devices.json")
        elif ready < total:
            print(f"[startup] WARNING: only {ready} of {total} devices are ready (see 'failed to load' above)")
        else:
            print(f"[startup] All {total} devices ready")
