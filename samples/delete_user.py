"""This script deletes a user from YooniK Authentication API"""
from yk_utils.apis import FaceAuthentication

# ------------------- SET THESE VALUES ------------------- #
YOONIK_AUTHENTICATION_API_URL = 'URL for YooniK Authentication API'
YOONIK_AUTHENTICATION_API_KEY = 'Your YooniK API key for accessing the YooniK APIs (please contact support@yoonik.me).'

USER_ID = 'User ID to be deleted'
# -------------------------------------------------------- #

face_authentication = FaceAuthentication(
    api_url=YOONIK_AUTHENTICATION_API_URL,
    api_key=YOONIK_AUTHENTICATION_API_KEY
)

success = face_authentication.request_account_deletion(user_id=USER_ID)
if success:
    print(f'User {USER_ID} successfully deleted!')
else:
    print(f'Error deleting user {USER_ID}.')
