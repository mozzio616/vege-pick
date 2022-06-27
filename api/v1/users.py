import math
import os
import pymongo
from bson.json_util import dumps
from dotenv import load_dotenv
from flask import Blueprint, request
from flask_cors import cross_origin
from db import db
from auth import requires_auth, requires_scope, AuthError

load_dotenv()

try:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))
except:
    LIMIT = 5

col_locations = db.locations
col_users = db.users

v1_users = Blueprint('v1_users', __name__, url_prefix='/api/v1')
@v1_users.route('/users')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations():
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
                { 'name': { '$regex': name }}
            ]
        }, {'_id': 0}))

        num = len(res_all)

        skip = limit * (page - 1)  
        last_page = math.ceil(num/limit)

        res = list(col_users.find({
            '$and': [
                { 'roles': { '$in': roles }},
                { 'userId': { '$nin': excl_users }},
                { 'name': { '$regex': name }}
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