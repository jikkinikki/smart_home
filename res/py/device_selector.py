from device_handler import DeviceHandler

class DeviceSelector:

    def __init__(self, device_handler):

        self.keyWords = {

            "all": lambda input: self.device_handler.getAllDevices(),
            "id": lambda id: self.id_selector(id),
            "name": lambda name: self.name_selector(name),
        }

    def id_selector(self, id):
        return self.device_handler.getDeviceById(id)

    def name_selector(self, name):
        return self.device_handler.getDeviceByName(name)

    # start with selector type followed by a separator ':' and then the selector value
    # e.g. "id:1234567890" or "name:Living Room"
    def smart_selector(self, selector):
        
        type, value = selector.split(":")
        type = type.lower()

        return self.keyWords[type](value)

if __name__ == "__main__":
    device_handler = DeviceHandler()
    device_selector = DeviceSelector(device_handler)
    print(device_selector.smart_selector("id:1234567890"))