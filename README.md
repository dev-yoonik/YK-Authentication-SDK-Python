# YK-Authentication-SDK-Python

This is a sample Flask Web App for capturing a selfie using the webcam and perform face authentication using YooniK APIs.

It handles the [YooniK's](https://yoonik.me) redirect rule in [Auth0](https://auth0.com).

For more information please contact our [support team](mailto:support@yoonik.me).

## Getting Started

```bash
$ git clone https://github.com/dev-yoonik/YK-Authentication-SDK-Python.git
$ cd YK-Authentication-SDK-Python
$ pip install -r requirements.txt
$ python app.py
```

Set the configuration values in the file app.py:

```
# app.py

SESSION_TOKEN_SECRET = 'A random long string that is used to sign the session token from Auth0'
YOONIK_AUTHENTICATION_API_URL = 'URL for YooniK Authentication APIs'
YOONIK_AUTHENTICATION_API_KEY = 'Your YooniK API key for accessing the YooniK APIs (please contact support@yoonik.me).'
```

Run the app:

```bash
$ python app.py
```

The app should be listening on http://localhost:3031!
