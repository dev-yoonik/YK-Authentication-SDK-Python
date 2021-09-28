var YooniKFaceAuthenticationSDK = (function(){

    const MAX_TRIES = 10; // Maximum number of authentication requests per session.

    let netDet = undefined;
    let validFrames = 0;
    let sendingResult = false;
    let isRunning = false;

    function detectFaces(img) {
        console.log("Detecting faces")
        let blob = cv.blobFromImage(img, 1, {
            width: 192,
            height: 144
        }, [104, 117, 123, 0], false, false);
        netDet.setInput(blob);
        let out = netDet.forward();

        let faces = [];
        for (let i = 0, n = out.data32F.length; i < n; i += 7) {
            let confidence = out.data32F[i + 2];
            let left = out.data32F[i + 3] * img.cols;
            let top = out.data32F[i + 4] * img.rows;
            let right = out.data32F[i + 5] * img.cols;
            let bottom = out.data32F[i + 6] * img.rows;
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
        console.log(`Detected ${faces.length} faces.`)
        return faces;
    }

    function loadModel(callback) {
        console.log("Loading model");
        let utils = new Utils('');
        const proto = 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy_lowres.prototxt';
        const weights = 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel';
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
            let jsonResponse = {
                "status": this.statusText,
                "html": this.responseText
            };
            if (this.status < 400) {
                jsonResponse = JSON.parse(this.responseText);
            }
            if (!imageData || jsonResponse.status != 'FAILED' || validFrames > MAX_TRIES) {
                isRunning = false;
                document.getElementById('content').innerHTML = jsonResponse.html;
                navigator.vibrate([500,250,1000]);
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
        validFrames = 0;
        sendingResult = false;
        
        // Create a camera object.
        console.log("Initializing video")
        let width = 640;
        let height = 480;
        if(screen.availHeight > screen.availWidth){
            const temp = height;
            height = width;
            width = temp;
        }
        let output = document.getElementById('output');
        output.setAttribute("width", width);
        output.setAttribute("height", height);
        let camera = document.createElement("video");
        camera.setAttribute("width", width);
        camera.setAttribute("height", height);
        camera.setAttribute("playsinline", "true");

        // Get a permission from user to use a camera.
        if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Sorry, your webcam is unavailable to take a photo");
            sendResult(null);
            return;
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
        let cap = new cv.VideoCapture(camera);
        let frame = new cv.Mat(camera.height, camera.width, cv.CV_8UC4);
        let frameBGR = new cv.Mat(camera.height, camera.width, cv.CV_8UC3);
        //! [Open a camera stream]

        //! [Define frames processing]
        let imageData = undefined;
        const FPS = 30; // Target number of frames processed per second.
        function captureFrame() {
            console.log("Capturing frame")
            const begin = Date.now();
            cap.read(frame); // Read a frame from camera
            cv.cvtColor(frame, frameBGR, cv.COLOR_RGBA2BGR);

            let faces = detectFaces(frameBGR);

            // Check if we should send a new face to YooniK Authentication API
            if (!sendingResult && isRunning && faces.length == 1) {
                validFrames++;
                if (validFrames > 1) { // Discard the first valid frame.
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
            });

            cv.imshow(output, frame);

            // Loop this function.
            if (isRunning) {
                const delay = 1000 / FPS - (Date.now() - begin);
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
            loadModel(run); // Load model and run a pipeline;
        } else {
            run();
        }
    }

    window.addEventListener('load', (event) => {
        cv['onRuntimeInitialized'] = () => { main(); };
    });

})();