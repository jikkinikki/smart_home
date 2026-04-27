<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lamps controller</title>

    <link rel="stylesheet" href="res/css/standards.css">
    <link rel="stylesheet" href="res/css/index.css">
</head>
<body>
    
    <main class="pop-out-box">

        <div id="devices" class="pop-in-box">
        <?php

            $jsonFilePath = "res/json/devices.json"; // Replace with the actual path to your JSON file

            $jsonData = file_get_contents($jsonFilePath);
            $devices = json_decode($jsonData, true);
        
            if ($devices != null) {
                foreach ($devices as $device) {
                    $deviceName = $device['device_name'];
                    $deviceId = $device['dev_id'];
                    $address = $device['address'];
                    $localKey = $device['local_key'];
                    $version = $device['version'];
        
                    echo '<div id="' . $deviceId . '">';
                    echo '<h2>' . str_replace("_", " ", $deviceName). '</h2>';
                    // echo '<p>Device ID: ' . $deviceId . '</p>';
                    // echo '<p>Address: ' . $address . '</p>';
                    // echo '<p>Local Key: ' . $localKey . '</p>';
                    // echo '<p>Version: ' . $version . '</p>';
                    echo '</div>';
                }
            } else {
                echo 'Error decoding JSON data';
            }

        ?>
        </div>
        <div id="light" class="pop-out-box">

        <!-- <label for="">color</label> -->
        <input id="color-inp" type="color">
        <label for="">brightness</label>
        <input id="brightness" type="range" name="" id="" steps="1" min="1" max="100">
        <label for="">temperature</label>
        <input id="temp" type="range" name="" id="" steps="10" min="1" max="100">
        
        <input type="button" value="turn on" id="turn-on">
        <input type="button" value="turn off" id="turn-off">

        </div>

    </main>

    <a href="remote.php">Remote</a>

    <script src="res/js/index.js"></script>

</body>
</html>