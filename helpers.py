import json
from bs4 import BeautifulSoup


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


def load_config(fname='./client_secrets.json'):
    config = None
    with open(fname) as f:
        config = json.load(f)
    return config


config = load_config()
