# YK-Authentication-SDK-Python

This is a sample Flask Web App for capturing a selfie using the webcam and perform face authentication using [YooniK](https://www.yoonik.me) APIs.

It handles the YooniK's redirect Action in [Auth0](https://marketplace.auth0.com/integrations/yoonik-face-authentication).

## Getting Started

### Install Auth0 Action

1. You can start by installing the YooniK Face Authentication Action in your Auth0 account. Please follow the instructions [here](https://marketplace.auth0.com/integrations/yoonik-face-authentication).
2. Then, in Auth0 dashboard click the **Actions** > **Flows** tab.
3. Select the **Login** flow.
4. Move your newly installed YooniK Action to your login flow.
5. Click on the YooniK Action box and then on **View Settings**.
6. Fill the **YooniK Application URL** with the URL for this sample app (e.g. http://127.0.0.1:3031); and the **YooniK Session Secret** with a random long string.

### Setup this example app

```bash
$ git clone https://github.com/dev-yoonik/YK-Authentication-SDK-Python.git
$ cd YK-Authentication-SDK-Python
$ pip install -r requirements.txt
```

Copy the [`client_secrets.json.dist`](client_secrets.json.dist) to `client_secrets.json`:

```bash
$ cp client_secrets.json.dist client_secrets.json
```

You now need to set the configuration values in the `client_secrets.json` file.

```json
{
  "YOONIK_SESSION_SECRET": "{{A random long string that is used to sign the session token from Auth0}}",
  "YOONIK_AUTHENTICATION_API_URL": "{{URL for YooniK Authentication APIs}}",
  "YOONIK_AUTHENTICATION_API_KEY": "{{Your YooniK API key for accessing the YooniK APIs (please contact support@yoonik.me).}}",
  "APP_SECRET": "{{A random long string that is used as secret key to this flask app}}"
}
```

> The **YOONIK_SESSION_SECRET** is the string you set before in the Auth0 action configuration.

Run the app:

```bash
$ python app.py
```

The app should be listening on http://localhost:3031!

## Additional Samples

You can find additional code samples [here](samples):

-   [delete_user.py](samples/delete_user.py): Use YooniK Authentication API to delete all data related to a user.

## Container Deployment

You can use the provided [Dockerfile](Dockerfile) to build a docker image with this sample app.

## YooniK Authentication API Details

For a complete specification of our Authentication API please check this [swagger file](authentication_api_swagger.json).

## Contact & Support

For more information, support and trial licenses please [contact us](mailto:support@yoonik.me) or join us at our [discord community](https://discord.gg/SqHVQUFNtN).

