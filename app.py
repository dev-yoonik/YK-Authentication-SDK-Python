import json
import logging
import requests
import jwt
from waitress import serve
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, jsonify

# ------------ SET THESE CONFIGURATION VALUES ------------ #
YOONIK_SESSION_SECRET = 'A random long string that is used to sign the session token from Auth0'
YOONIK_AUTHENTICATION_API_URL = 'URL for YooniK Authentication APIs'
YOONIK_AUTHENTICATION_API_KEY = 'Your YooniK API key for accessing the YooniK APIs (please contact support@yoonik.me).'
# -------------------------------------------------------- #


APP = Flask(__name__)
JWT_ALGORITHM = "HS256"


def allowed_base64_image(image_str):
    if not image_str.startswith('data:image/'):
        return False
    return image_str[11:14] in {'png', 'jpg', 'jpeg', 'gif'}


def parse_response_error(html_text: str) -> str:
    """Parse HTML error response
    :param html_text:
        HTML error message.
    :return:
        Parsed error message.
    """
    message = ''
    html = BeautifulSoup(markup=html_text, features="html.parser")
    if html.p:
        inner_html = BeautifulSoup(markup=html.p.text, features="html.parser")
        message = inner_html.text if inner_html.p is None else inner_html.p.text

    if "face_not_found" in message:
        message = "Could not find a face in the image."
    elif "multiple_faces" in message:
        message = "The image has more than one person."
    elif "quality_failed" in message:
        message = "The provided image does not have enough quality."
    else:
        message = "An error occurred. Please contact your systems administrator."
        print(f"ERROR: {html.text}")
    return message


def parse_response_status(status: str) -> str:
    """Create a message from the response status data
    :param status:
        Status of the operation.
    :return:
        Resulting message to be sent to the UI.
    """
    message = status
    if status == 'SUCCESS':
        message = "Face authentication successful"
    elif status == 'NEW_USER':
        message = "Face signup successful"
    elif status == 'USER_NOT_FOUND':
        message = "User not registered"
    elif status == 'FAILED':
        message = "Face authentication failed"
    return message


@APP.route("/")
def home():
    """Example endpoint for handling YooniK's Action integration from Auth0
    :return:
    """
    return render_template("take_photo.html")


@APP.route("/verify_user", methods=['POST'])
def verify_user():
    """Check user photo with YooniK Authentication API.
    :return:
    """
    status = 'FAILED'
    message_class = 'text-danger'
    message = 'Face authentication failed'

    state = request.json['state']
    session_token = request.json['session_token']
    session_token_decoded = jwt.decode(session_token, YOONIK_SESSION_SECRET, algorithms=[JWT_ALGORITHM])
    user_id = session_token_decoded['sub']
    if request.json['photo'] and allowed_base64_image(request.json['photo']):
        photo_str = request.json['photo'].split('base64,')[1]

        yoonik_request_data = {
            'user_id': user_id,
            'user_photo': photo_str,
            'create_if_new': True
        }
        response = requests.post(
            YOONIK_AUTHENTICATION_API_URL,
            headers={'x-api-key': YOONIK_AUTHENTICATION_API_KEY},
            json=yoonik_request_data
        )
        if response.ok:
            result = json.loads(response.text)
            status = result['status']
            message_class = 'text-success' if status == 'SUCCESS' or status == 'NEW_USER' else 'text-danger'
            message = parse_response_status(status)
        else:
            message = f'Ups! {parse_response_error(response.text)}'

    session_token_decoded["status"] = status
    session_token_decoded["state"] = state
    new_session_token_encoded = jwt.encode(session_token_decoded,
                                           YOONIK_SESSION_SECRET, algorithm=JWT_ALGORITHM)
    continue_url = f"{session_token_decoded['iss']}continue?state={state}&" \
                   f"yoonik_authentication=true&" \
                   f"session_token={new_session_token_encoded}"

    return jsonify(
        status=status,
        html=render_template("result.html", message_class=message_class, message=message, continue_url=continue_url))


if __name__ == "__main__":
    # APP.run(host="127.0.0.1", port=3031)
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(APP, host="0.0.0.0", port=3031)

