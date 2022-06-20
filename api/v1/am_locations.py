import math
import os
import urllib.parse
import pymongo
from bson.json_util import dumps
from datetime import datetime
from dotenv import load_dotenv
from flask import Blueprint, request, _request_ctx_stack
from flask_cors import cross_origin
from db import db
from auth import requires_auth, requires_scope, AuthError

load_dotenv()

try:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))
except:
    LIMIT = 5

col_locations = db.locations

v1_am_locations = Blueprint('v1_am_locations', __name__, url_prefix='/api/v1')
@v1_am_locations.route('/ams/<user_id>/locations')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(user_id):
    user_id = urllib.parse.unquote(user_id)
    if requires_scope('read:am_locations') or requires_scope('read:locations'):
        if requires_scope('read:locations') is False:
            if user_id != _request_ctx_stack.top.current_user['sub']:
                print(request.remote_addr + ' - - [' + datetime.now().strftime('%d/%b/%Y %H:%M:%S') + '] Invalid user ID request. token->' + _request_ctx_stack.top.current_user['sub'] + ' request->' + user_id)
                raise AuthError({
                    "code": "Unauthorized",
                    "description": "You don't have access to this resource"
                }, 403)
        if request.args.get('searchKey') is None:
            searchKey = ''
        else:
            searchKey = request.args.get('searchKey')
        
        if request.args.get('limit') is None:
            limit = LIMIT
        else:
            limit = int(request.args.get('limit'))
        
        if request.args.get('page') is None:
            page = 1
        else:
            page = int(request.args.get('page'))
        print('for debug: ' + user_id)
        res_all = col_locations.find({
            '$and': [
                {'ams': [user_id]},
                {
                    '$or': [
                        {'locationNameJp': {'$regex': searchKey}},
                        {'locationNameEn': {'$regex': searchKey}}
                    ]
                }
            ]
        })
        all = list(res_all)
        num = len(all)

        skip = limit * (page - 1)  
        last_page = math.ceil(num/limit)

        locations = col_locations.find({
            '$and': [
                {'ams': [user_id]},
                {
                    '$or': [
                        {'locationNameJp': {'$regex': searchKey}},
                        {'locationNameEn': {'$regex': searchKey}}
                    ]
                }
            ]
        }, {'_id': False}).sort([('locationId', pymongo.ASCENDING)]).skip(skip).limit(limit) 
        response = {
            'current_page': page,
            'last_page': last_page,
            'locations': locations
        }
        return dumps(response)
    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)