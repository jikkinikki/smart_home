<?php

echo "executed<br>";

$allowedKeys = [

    "brightness",
    "switch_power",
    "temp",
    "color"
];

function validateInput($inp){

    global $allowedKeys;

    if(!in_array($inp, $allowedKeys)){

        echo "inp not valid: " . $inp;
        return "null";
    }

    return $inp;
}

$action = validateInput($_POST["action"]);

$data = [

    "action"=> $action,
    "value"=> $_POST["value"],
    "device_id"=> $_POST["device_id"]
];

$queActionPath = "../change_que/";

$jsonData = json_encode($data, JSON_PRETTY_PRINT);

file_put_contents($queActionPath . microtime() . random_int(0, 1000) . ".json", $jsonData);