var YooniKFaceAuthenticationSDK = (function(){

    var netDet = undefined;
    var validFrames = 0;
    var sendingResult = false;
    var isRunning = false;

    function detectFaces(img) {
        var blob = cv.blobFromImage(img, 1, {
            width: 192,
            height: 144
        }, [104, 117, 123, 0], false, false);
        netDet.setInput(blob);
        var out = netDet.forward();

        var faces = [];
        for (var i = 0, n = out.data32F.length; i < n; i += 7) {
            var confidence = out.data32F[i + 2];
            var left = out.data32F[i + 3] * img.cols;
            var top = out.data32F[i + 4] * img.rows;
            var right = out.data32F[i + 5] * img.cols;
            var bottom = out.data32F[i + 6] * img.rows;
            left = Math.min(Math.max(0, left), img.cols - 1);
            right = Math.min(Math.max(0, right), img.cols - 1);
            bottom = Math.min(Math.max(0, bottom), img.rows - 1);
            top = Math.min(Math.max(0, top), img.rows - 1);

            if (confidence > 0.5 && left < right && top < bottom) {
                faces.push({
                    x: left,
                    y: top,
                    width: right - left,
                    height: bottom - top
                })
            }
        }
        blob.delete();
        out.delete();
        return faces;
    }

    function loadModel(callback) {
        var utils = new Utils('');
        var proto = 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy_lowres.prototxt';
        var weights = 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel';
        utils.createFileFromUrl('face_detector.prototxt', proto, () => {
            document.getElementById('status').innerHTML = '<h3>Loading...</h3>';
            utils.createFileFromUrl('face_detector.caffemodel', weights, () => {
                netDet = cv.readNetFromCaffe('face_detector.prototxt', 'face_detector.caffemodel');
                document.getElementById('status').innerHTML = '<h3>Please look at the camera</h3>';
                callback();
            });
        });
    }

    function sendResult(imageData) {
        console.log("Sending result");
        sendingResult = true;
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const request = new XMLHttpRequest();
        request.open( "POST", "/verify_user" );
        request.setRequestHeader("Content-Type", "application/json");
        request.addEventListener( "load", function(event) {
            if (this.responseText.search("text-danger") == -1 || validFrames > 10) {
                isRunning = false;
                document.getElementById('content').innerHTML = this.responseText
            }
            sendingResult = false;
        });
        data = {
            session_token: urlParams.get('session_token'),
            state: urlParams.get('state'),
            photo: imageData,
        };
        request.send( JSON.stringify(data) );
    }

    function main() {
        // Create a camera object.
        console.log("Initializing video")
        var output = document.getElementById('output');
        var camera = document.createElement("video");
        camera.setAttribute("width", output.width);
        camera.setAttribute("height", output.height);

        // Get a permission from user to use a camera.
        if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Sorry, your webcam is unavailable to take a photo");
            sendResult(null);
        }
        navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        })
        .then(function(stream) {
            camera.srcObject = stream;
            camera.onloadedmetadata = function(e) {
                camera.play();
            };
        })
        .catch(function(err) {
            alert("Sorry, camera permissions are needed for face authentication.");
            sendResult(null);
        });

        //! [Open a camera stream]
        var cap = new cv.VideoCapture(camera);
        var frame = new cv.Mat(camera.height, camera.width, cv.CV_8UC4);
        var frameBGR = new cv.Mat(camera.height, camera.width, cv.CV_8UC3);
        //! [Open a camera stream]

        //! [Define frames processing]
        var imageData = undefined;
        const FPS = 30; // Target number of frames processed per second.
        function captureFrame() {
            console.log("Capturing frame")
            var begin = Date.now();
            cap.read(frame); // Read a frame from camera
            cv.cvtColor(frame, frameBGR, cv.COLOR_RGBA2BGR);

            console.log("Detecting faces")
            var faces = detectFaces(frameBGR);
            console.log(`Detected ${faces.length} faces.`)

            // Check if we should send a new face to YooniK Authentication API
            if (!sendingResult && isRunning && faces.length == 1) {
                validFrames++;
                if (validFrames > 2) {
                    cv.imshow(output, frame);
                    console.log("Converting to base64 URL");
                    imageData = output.toDataURL("image/png");
                    sendResult(imageData);
                }
            }

            faces.forEach(function(rect) {
                cv.rectangle(frame, {
                    x: rect.x,
                    y: rect.y
                }, {
                    x: rect.x + rect.width,
                    y: rect.y + rect.height
                }, [43, 179, 186, 255], 3);

                // var face = frameBGR.roi(rect);
            });

            cv.imshow(output, frame);

            // Loop this function.
            if (isRunning) {
                var delay = 1000 / FPS - (Date.now() - begin);
                setTimeout(captureFrame, delay);
            }
        }
        ;
        //! [Define frames processing]

        function run() {
            isRunning = true;
            captureFrame();
        }
        if (netDet == undefined) {
            console.log("Loading model");
            loadModel(run); // Load model and run a pipeline;
        } else {
            run();
        }
    }

    window.addEventListener('load', (event) => {
        cv['onRuntimeInitialized'] = () => { main(); };
    });

})();