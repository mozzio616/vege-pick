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

load_dotenv()

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']

try:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))
except:
    LIMIT = 5

col_token = db.token
col_locations = db.locations
col_users = db.users

v1_users = Blueprint('v1_users', __name__, url_prefix='/api/v1')
@v1_users.route('/users', methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations():
    if request.method == 'POST':
        if requires_scope('post:users'):
            # validate request parameters
            try:
                email = request.json['email']
                if re.fullmatch(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) is None:
                    return {'code': 'bad_request', 'description': 'invalid email'}, 400
            except KeyError:
                return {'code': 'bad_request', 'description': 'email missing'}, 400
            roles_preset = {'admin', 'am', 'operator'}
            roleIds_dict = {'admin': 'rol_LoUONbA8CLs4N882', 'am': 'rol_451smviuNOkT6C6K'}
            try:
                roles = request.json['roles']
                if type(roles) is not list:
                    return {'code': 'bad_request', 'description': 'roles must be list'}, 400
                elif len(roles) == 0:
                    return {'code': 'bad_request', 'description': 'at reast a role required'}, 400
                elif set(roles).issubset(roles_preset) is False:
                    return {'code': 'bad_request', 'description': 'including invalid roles'}, 400
            except KeyError:
                return {'code': 'bad_request', 'description': 'roles missing'}, 400
            # convert role name to role id
            roleIds = []
            i = 0
            while i < len(roles):
                if roles[i] == 'admin':
                    roleIds.append(roleIds_dict['admin'])
                elif roles[i] == 'am':
                    roleIds.append(roleIds_dict['am'])
                i += 1
            # create auth0 user (1st try)
            url = 'https://' + AUTH0_DOMAIN + '/api/v2/users'
            res = col_token.find_one({'_id': 'mgmt_token'})
            token = res['token']
            headers = { 'Authorization': 'Bearer ' + token }
            data = {
                'email': email,
                'name': email,
                'connection': 'Username-Password-Authentication',
                'password': 'P@ssw0rd',
                'app_metadata': {
                    'roles': roles
                }}
            res_api = requests.post(url, json=data, headers=headers)
            # create auth0 user (retry)
            if res_api.status_code >= 400:
                token = get_mgmt_token()
                headers = { 'Authorization': 'Bearer ' + token }
                res_api = requests.post(url, json=data, headers=headers)
            if res_api.status_code != 201:
                return res_api.json(), res_api.status_code
            else:
                user_id = res_api.json()['user_id']
            # assign roles to the user (1st try)
            url = 'https://' + AUTH0_DOMAIN + '/api/v2/users/' + user_id + '/roles'
            data = { 'roles': roleIds }
            res_api = requests.post(url, json=data, headers=headers)
            # assign roles to the user (retry)
            if res_api.status_code >= 400:
                token = get_mgmt_token()
                headers = { 'Authorization': 'Bearer ' + token }
                res_api = requests.post(url, json=data, headers=headers)
                if res_api.status_code >= 400:
                    return res_api.json(), res_api.status_code
            # create user in database
            res = col_users.insert_one({'name': email, 'roles': roles, 'userId': user_id})
            if res.acknowledged is True:
                print('user added to mongodb: ' + str(res.inserted_id))
            else:
                print('failed to add user to mongodb')
            return request.json

    else:
        if requires_scope('read:users'):

            if request.args.get('role') is None:
                roles = [ 'admin', 'am', 'operator' ]
            else:
                roles = [ request.args.get('role') ]

            if request.args.get('name') is None:
                name = ''
            else:
                name = request.args.get('name')

            if request.args.get('excl') is None:
                excl_users = [ None ]
            else:
                excl = request.args.get('excl')
                res = col_locations.find_one({'locationId': excl})
                try:
                    excl_users = res['ams']
                except KeyError:
                    excl_users = [ None ]
            
            if request.args.get('limit') is None:
                limit = LIMIT
            else:
                limit = int(request.args.get('limit'))
            
            if request.args.get('page') is None:
                page = 1
            else:
                page = int(request.args.get('page'))

            res_all = list(col_users.find({
                '$and': [
                    { 'roles': { '$in': roles }},
                    { 'userId': { '$nin': excl_users }},
                    { '$or':
                        [
                            {'name': { '$regex': name }},
                            {'givenName': { '$regex': name}},
                            {'familyName': { '$regex': name}}
                        ]
                    }
                ]
            }, {'_id': 0}))

            num = len(res_all)

            skip = limit * (page - 1)  
            last_page = math.ceil(num/limit)

            res = list(col_users.find({
                '$and': [
                    { 'roles': { '$in': roles }},
                    { 'userId': { '$nin': excl_users }},
                    { '$or':
                        [
                            {'name': { '$regex': name }},
                            {'givenName': { '$regex': name}},
                            {'familyName': { '$regex': name}}
                        ]
                    }
                ]
            }, {'_id': 0}).sort([('name', pymongo.ASCENDING)]).skip(skip).limit(limit))

            response = {
                'current_page': page,
                'last_page': last_page,
                'users': res
            }
            return dumps(response)

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)