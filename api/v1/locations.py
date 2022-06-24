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

def new_location_id():
    res = list(col_locations.find())
    num = len(res)
    new_location_id = 'L' + str(num).zfill(8)
    return new_location_id    

v1_locations = Blueprint('v1_locations', __name__, url_prefix='/api/v1')
@v1_locations.route('/locations', methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations():
    if request.method == 'POST':
        if requires_scope('post:locations'):
            if type(request.json) is dict:
                data = request.json
                data['locationId'] = new_location_id()
                res = col_locations.insert_one(data)
                return dumps(res.inserted_id)
            elif type(request.json) is list:
                res = col_locations.insert_many(request.json)
                return dumps(res.inserted_ids)
            else:
                return '', 400
    else:
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