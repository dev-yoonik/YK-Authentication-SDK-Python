"""This script deletes a user from YooniK Authentication API"""
import requests

# ------------------- SET THESE VALUES ------------------- #
YOONIK_AUTHENTICATION_API_URL = 'URL for YooniK Authentication API'
YOONIK_AUTHENTICATION_API_KEY = 'Your YooniK API key for accessing the YooniK APIs (please contact support@yoonik.me).'

USER_ID = 'User ID to be deleted'
# -------------------------------------------------------- #

response = requests.delete(
    YOONIK_AUTHENTICATION_API_URL,
    headers={'x-api-key': YOONIK_AUTHENTICATION_API_KEY},
    json={'user_id': USER_ID}
)

if response.ok:
    print(f'User {USER_ID} successfully deleted!')
else:
    print(f'Error deleting user {USER_ID}: {response.text}.')
