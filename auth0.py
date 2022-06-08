from json import load
import requests
import os
from db import db
from dotenv import load_dotenv

load_dotenv()
AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']
AUTH0_CLIENT_ID = os.environ['AUTH0_CLIENT_ID']
AUTH0_CLIENT_SECRET = os.environ['AUTH0_CLIENT_SECRET']
AUTH0_AUDIENCE = os.environ['API_IDENTIFIER']

collection_token = db.token

def get_token():
    url = 'https://' + AUTH0_DOMAIN + '/oauth/token'
    payload = {
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'audience': AUTH0_AUDIENCE,
        'grant_type': 'client_credentials'
        }
    res_api = requests.post(url, json=payload)
    token = res_api.json()['access_token']
    res_db = collection_token.update_one({'_id': 'token'}, {'$set': {'token': token}})
    print('auth0 access token updated.')
    return token