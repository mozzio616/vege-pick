import os
import math
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

v1_locations = Blueprint('v1_locations', __name__, url_prefix='/api/v1/locations')
@v1_locations.route('', methods=['GET'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations():
    if request.method == 'GET':
        if requires_scope('read:locations'):
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

            res_all = col_locations.find({
                '$or': [
                    {'locationNameJp': {'$regex': searchKey}},
                    {'locationNameEn': {'$regex': searchKey}}
                ]
            })
            all = list(res_all)
            num = len(all)

            skip = limit * (page - 1)  
            last_page = math.ceil(num/limit)

            locations = col_locations.find({
                '$or': [
                    {'locationNameJp': {'$regex': searchKey}},
                    {'locationNameEn': {'$regex': searchKey}}
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