import logging
import jwt
from waitress import serve
from flask import Flask, request, render_template, jsonify, abort

from yk_utils.files import load_json_config
from yk_utils.apis import FaceAuthentication

from forms import FaceAuthenticationForm

config = load_json_config(filename='./client_secrets.json')
face_authentication = FaceAuthentication(
    api_url=config["YOONIK_AUTHENTICATION_API_URL"],
    api_key=config["YOONIK_AUTHENTICATION_API_KEY"]
)

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

    continue_url = ''
    state = request.args.get("state")
    session_token = request.args.get('session_token')
    session_token_decoded = jwt.decode(session_token, config['YOONIK_SESSION_SECRET'], algorithms=[JWT_ALGORITHM])

    face_authentication.request_face_authentication(
        user_id=session_token_decoded['sub'],
        user_photo=form.user_selfie.data,
        create_if_new=True
    )

    if face_authentication.status == 'SUCCESS' or face_authentication.status == 'NEW_USER':
        session_token_decoded["status"] = face_authentication.status
        session_token_decoded["state"] = state
        new_session_token_encoded = jwt.encode(session_token_decoded,
                                               config['YOONIK_SESSION_SECRET'], algorithm=JWT_ALGORITHM)
        continue_url = f"{session_token_decoded['iss']}continue?state={state}&" \
                       f"yoonik_authentication=true&" \
                       f"session_token={new_session_token_encoded}"

    return jsonify(
        status=face_authentication.status,
        html=render_template("result.html", message_class=face_authentication.message_class,
                             message=face_authentication.message, continue_url=continue_url))


if __name__ == "__main__":
    # APP.run(host="127.0.0.1", port=3031)
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(APP, host="0.0.0.0", port=3031)

