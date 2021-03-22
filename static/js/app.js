var YooniKFaceAuthenticationSDK = (function(){

    function sendResult(imageData) {
        document.getElementById('content').innerHTML = '<h2>Please wait...</h2>';
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const request = new XMLHttpRequest();
        request.open( "POST", "/verify_user" );
        request.setRequestHeader("Content-Type", "application/json");
        request.addEventListener( "load", function(event) {
            document.getElementById('content').innerHTML = this.responseText
        });
        data = {
            session_token: urlParams.get('session_token'),
            state: urlParams.get('state'),
            photo: imageData,
        };
        request.send( JSON.stringify(data) );
    }

    window.addEventListener('load', (event) => {
        if (!confirm("If this is your first time with YooniK, we will create a new account for you. Do you agree?")) {
            sendResult(null);
            return;
        }
        if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            let htmlCode = '<div class="row"><video id="video-stream" width="640" height="480" autoplay></video></div>';
            htmlCode += '<div class="row"><button style="margin-top: 10px" class="btn btn-info btn-lg btn-block" id="take-photo-btn">Take Photo</button></div>';
            htmlCode += '<canvas id="take-photo-canvas" width="640" height="480" style="display:none;"></canvas>';
            document.getElementById('content').innerHTML = htmlCode
            var video = document.getElementById('video-stream');
            var canvas = document.getElementById('take-photo-canvas');
            var context = canvas.getContext('2d');
            navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
                video.srcObject = stream;
                video.play();
            })
            .catch(function(err) {
                alert("Sorry, camera permissions are needed for face authentication.");
                sendResult(null);
            });
            document.getElementById('take-photo-btn').addEventListener("click", function() {
                context.drawImage(video, 0, 0, 640, 480);
                let imageData = canvas.toDataURL("image/png");
                sendResult(imageData);
            });
        } else {
            alert("Sorry, your webcam is unavailable to take a photo");
            sendResult(null);
        }
    });

})();