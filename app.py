import json
import logging
import requests
import jwt
from waitress import serve
from flask import Flask, request, render_template, jsonify
from helpers import allowed_base64_image, parse_response_error, parse_response_status, config


APP = Flask(__name__)
JWT_ALGORITHM = "HS256"


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
    session_token_decoded = jwt.decode(session_token, config['YOONIK_SESSION_SECRET'], algorithms=[JWT_ALGORITHM])
    user_id = session_token_decoded['sub']
    if request.json['photo'] and allowed_base64_image(request.json['photo']):
        photo_str = request.json['photo'].split('base64,')[1]

        yoonik_request_data = {
            'user_id': user_id,
            'user_photo': photo_str,
            'create_if_new': True
        }
        response = requests.post(
            config['YOONIK_AUTHENTICATION_API_URL'],
            headers={'x-api-key': config['YOONIK_AUTHENTICATION_API_KEY']},
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
                                           config['YOONIK_SESSION_SECRET'], algorithm=JWT_ALGORITHM)
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

