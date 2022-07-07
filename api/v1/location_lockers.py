from flask import Blueprint, request
from flask_cors import cross_origin
from bson.json_util import dumps
from dotenv import load_dotenv
import math, os, re

from db import db
from auth import requires_auth, requires_scope, AuthError

load_dotenv()

try:
    LIMIT = int(os.getenv('DEFAULT_LIMIT'))
except:
    LIMIT = 1000

col_locations = db.locations
col_racks = db.racks
col_lockers = db.lockers

v1_location_lockers = Blueprint('v1_location_lockers', __name__, url_prefix='/api/v1')
@v1_location_lockers.route('/locations/<locationId>/lockers')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(locationId):

    if requires_scope('read:locations'):
        # parameter validation locationId
        if re.fullmatch(r'^L[0-9]{7}', locationId) is None:
            return {'code': 'bad_request', 'description': 'invalid locationId'}, 400
        # validate query string
        try:
            limit = int(request.args.get('limit'))
        except:
            limit = LIMIT
        try:
            page = int(request.args.get('page'))
        except:
            page = 1
        # get all data 

        res_location = col_locations.find_one({'locationId': locationId}, {'_id': False})
        if res_location is None:
            return {'code': 'not_found', 'description': 'Location not found'}, 404

        pipe = [
            {
                '$match': { 'locationId': locationId }
            },
            {
                '$lookup': {
                    'from': 'items',
                    'localField': 'itemId',
                    'foreignField': 'itemId',
                    'as': 'item'
                }
            },
            {
                '$unwind': {
                    'path': '$item',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'itemId': 0,
                    'locationId': 0,
                    'item._id': 0,
                    'location._id': 0,
                }
            },
            {
                '$sort': {
                    'lockerNo': 1
                }
            }
        ]
        res_all = list(col_lockers.aggregate(pipeline=pipe))
        # get paging data
        num = len(res_all)
        if num == 0:
            last_page = 1
        else:
            last_page = math.ceil(num/limit)
        skip = limit * (page - 1)  
        pipe_paging = [
            {
                '$skip': skip
            },
            {
                '$limit': limit
            }
        ]
        pipe.extend(pipe_paging)
        res = list(col_lockers.aggregate(pipeline=pipe))
        # return response
        response = {}
        response['current_page'] = page
        response['last_page'] = last_page
        response['location'] = res_location
        if len(res) == 0:
            response['lockers'] = []
        else:
            response['lockers'] = res
        return dumps(response)

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)