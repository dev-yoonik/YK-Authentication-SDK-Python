import json
import logging
import requests
import jwt
from waitress import serve
from flask import Flask, request, render_template, jsonify, abort
from helpers import allowed_base64_image, parse_response_error, parse_response_status, config
from forms import FaceAuthenticationForm


APP = Flask(__name__)
APP.config.update({'SECRET_KEY': config['APP_SECRET']})
JWT_ALGORITHM = "HS256"


@APP.route("/", methods=['GET', 'POST'])
def home():
    """Example endpoint for handling YooniK's Action integration from Auth0
    :return:
    """
    if request.method == 'GET':
        return render_template("take_photo.html", form=FaceAuthenticationForm())

    form = FaceAuthenticationForm()
    if not form.validate_on_submit():
        abort(400, "Error in selfie submission")

    status = 'FAILED'
    message_class = 'text-danger'
    message = 'Face authentication failed'
    continue_url = ''

    state = request.args.get("state")
    session_token = request.args.get('session_token')
    session_token_decoded = jwt.decode(session_token, config['YOONIK_SESSION_SECRET'], algorithms=[JWT_ALGORITHM])
    user_id = session_token_decoded['sub']

    if allowed_base64_image(form.user_selfie.data):
        yoonik_request_data = {
            'user_id': user_id,
            'user_photo': form.user_selfie.data.split('base64,')[1],
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

    if status == 'SUCCESS' or status == 'NEW_USER':
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

