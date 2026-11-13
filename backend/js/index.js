const devices = document.getElementById("devices").children;

for (const device of devices) {

    device.addEventListener("click", () => {


    })
}

document.getElementById("brightness").addEventListener("input", e => {

    console.log(e.target.value);

    sendData({
        "action": "brightness",
        "value": e.target.value
    });
});

document.getElementById("temp").addEventListener("input", e => {

    console.log(e.target.value);

    sendData({
        "action": "temp",
        "value": e.target.value
    });
});

document.getElementById("color-inp").addEventListener("input", e => {

    console.log(e.target.value);

    sendData({
        "action": "color",
        "value": e.target.value
    });
});

document.getElementById("turn-on").addEventListener("click", e => {

    sendData({
        "action": "switch_power",
        "value": "on"
    });
});

document.getElementById("turn-off").addEventListener("click", e => {

    sendData({
        "action": "switch_power",
        "value": "off"
    });
});

function setSelectedDevice(deviceToSelect) {

    for (const device of document.getElementById("devices").children) {

        if (device != deviceToSelect)
            device.classList.remove("selected");
        else
            device.classList.add("selected");
    }
}

addDeviceSelectListeners()

function addDeviceSelectListeners() {

    for (const device of document.getElementById("devices").children) {

        device.addEventListener("click", e => {

            setSelectedDevice(device);
        });
    }
}

setSelectedDevice(document.getElementById("devices").children[0])

function sendData(dataObj) {

    const formData = new FormData();

    formData.append("device_id", document.getElementsByClassName("selected")[0].getAttribute("id"))

    for (const key in dataObj)
        formData.append(key, dataObj[key]);

    fetch("res/php/control_devices.php", { method: "POST", body: formData });
}