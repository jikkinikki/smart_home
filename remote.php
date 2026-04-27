<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>

<body>

    <p id="out">a</p>
    <button id="enableMotion">Enable Motion Access</button>

</body>

<script src="res/js/motion_tools.js"></script>

<script>
    

    // out.innerHTML += "<br>"
    // out.innerHTML += 'orientation' in screen;
    // out.innerHTML += " " + screen.orientation;

    // out.innerHTML += "<br>"
    // out.innerHTML += window.DeviceMotionEvent.requestPermission == 'function';
    // out.innerHTML += "<br>"
    // out.innerHTML += DeviceMotionEvent.requestPermission == 'function';
    // out.innerHTML += "<br>"
    // out.innerHTML += window.DeviceMotionEvent == true;
    // out.innerHTML += "<br>"

    // out.innerHTML += window.DeviceOrientationEvent.requestPermission == 'function';
    // out.innerHTML += "<br>"
    // out.innerHTML += window.DeviceOrientationEvent == true;
    // out.innerHTML += "<br>"
    // out.innerHTML += DeviceOrientationEvent.requestPermission == 'function';

    // document.getElementById('enableMotion').addEventListener('click', function() {
    //     // Check if DeviceOrientationEvent and DeviceMotionEvent are supported
    //     if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
    //         DeviceOrientationEvent.requestPermission()
    //             .then(permissionState => {
    //                 if (permissionState === 'granted') {
    //                     window.addEventListener('deviceorientation', function(event) {
    //                         console.log(`Device Orientation: alpha ${event.alpha}, beta ${event.beta}, gamma ${event.gamma}`);
    //                     });
    //                 } else {
    //                     console.error('Permission not granted for Device Orientation');
    //                 }
    //             })
    //             .catch(console.error);
    //     } else {
    //         // DeviceOrientationEvent may not require permissions or is not supported
    //         window.addEventListener('deviceorientation', function(event) {
    //             console.log(`Device Orientation: alpha ${event.alpha}, beta ${event.beta}, gamma ${event.gamma}`);
    //         });
    //     }

    //     if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {
    //         DeviceMotionEvent.requestPermission()
    //             .then(permissionState => {
    //                 if (permissionState === 'granted') {
    //                     window.addEventListener('devicemotion', function(event) {
    //                         console.log(`Device Motion: acceleration x ${event.acceleration.x}, y ${event.acceleration.y}, z ${event.acceleration.z}`);
    //                     });
    //                 } else {
    //                     console.error('Permission not granted for Device Motion');
    //                 }
    //             })
    //             .catch(console.error);
    //     } else {
    //         // DeviceMotionEvent may not require permissions or is not supported
    //         window.addEventListener('devicemotion', function(event) {
    //             console.log(`Device Motion: acceleration x ${event.acceleration.x}, y ${event.acceleration.y}, z ${event.acceleration.z}`);
    //         });
    //     }
    // });
</script>

</html>