import math
import os, re, json
import pymongo
from bson.json_util import dumps
from dotenv import load_dotenv
from flask import Blueprint, request
from flask_cors import cross_origin
from db import db
from auth import requires_auth, requires_scope, AuthError
import requests
from auth0 import get_mgmt_token
import urllib.parse

load_dotenv()

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']

try:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))
except:
    LIMIT = 1000

col_token = db.token
col_locations = db.locations
col_users = db.users

v1_user = Blueprint('v1_user', __name__, url_prefix='/api/v1')
@v1_user.route('/users/<userId>', methods=['GET', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def user(userId):
    if request.method == 'DELETE':
        if requires_scope('delete:users'):
            userId = urllib.parse.unquote(userId)
            res = col_users.find_one({'userId': userId})
            if res is None:
                return {'code': 'not_found', 'description': 'user not found'}, 404
            url = 'https://' + AUTH0_DOMAIN + '/api/v2/users/' + userId
            res = col_token.find_one({'_id': 'mgmt_token'})
            token = res['token']
            headers = { 'Authorization': 'Bearer ' + token }
            res_api = requests.get(url, headers=headers)
            if res_api.status_code >= 400:
                token = get_mgmt_token()
                headers = { 'Authorization': 'Bearer ' + token }
                res_api = requests.get(url, headers=headers)
            if res_api.status_code == 200:
                res = col_users.delete_one({'userId': userId})
                if res.acknowledged != 1:
                    return {'code': 'unknown', 'description': 'failed to delete user from db'}, 500
                else:
                    res_api = requests.delete(url, headers=headers)
                    return None, res_api.status_code

    else:
        if requires_scope('read:users'):
            userId = urllib.parse.unquote(userId)
            url = 'https://' + AUTH0_DOMAIN + '/api/v2/users/' + userId
            res = col_token.find_one({'_id': 'mgmt_token'})
            token = res['token']
            headers = { 'Authorization': 'Bearer ' + token }
            res_api = requests.get(url, headers=headers)
            if res_api.status_code >= 400:
                token = get_mgmt_token()
                headers = { 'Authorization': 'Bearer ' + token }
                res_api = requests.get(url, headers=headers)
            return res_api.json(), res_api.status_code

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)