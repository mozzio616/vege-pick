from flask import Blueprint, request
from flask_cors import cross_origin
from bson.json_util import dumps
from dotenv import load_dotenv
import math, os, re

from db import db
from auth import requires_auth, requires_scope, AuthError

load_dotenv()

try:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))
except:
    LIMIT = 5

col_locations = db.locations
col_racks = db.racks
col_lockers = db.lockers
col_items = db.items

v1_location_locker = Blueprint('v1_location_locker', __name__, url_prefix='/api/v1')
@v1_location_locker.route('/locations/<locationId>/lockers/<lockerId>', methods=['GET', 'PATCH'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def location_locker(locationId, lockerId):

    if request.method == 'PATCH':
        if requires_scope('update:locations'):
            # validate url path parameters
            if re.fullmatch(r'^L[0-9]{7}', locationId) is None:
                return {'code': 'bad_request', 'description': 'invalid locationId'}, 400
            if re.fullmatch(r'^R[0-9]{7}B[0-9]{3}', lockerId) is None:
                return {'code': 'bad_request', 'description': 'invalid lockerId'}, 400
            # validate request body
            params = {}
            try:
                itemId = request.json['itemId']
                if re.fullmatch(r'^I[0-9]{7}', itemId) is None:
                    return {'code': 'bad_request', 'description': 'invalid itemId'}, 400
                else:
                    res = col_items.find_one({'itemId': itemId})
                    if res is None:
                        return {'code': 'not found', 'description': 'itemId not found'}, 404
                    else:
                        params['itemId'] = itemId
            except KeyError:
                params = params
            try:
                isAvailable = request.json['isAvailable']
                if type(isAvailable) is not bool:
                    return {'code': 'bad_request', 'description': 'isAvailable must be bool'}, 400
                else:
                    params['isAvailable'] = isAvailable
            except KeyError:
                params = params
            if len(params) == 0:
                return {'code': 'bad_request', 'description': 'parameter missing'}, 400
            # set locationId: null for lockers
            res = col_lockers.update_one({'$and': [{'lockerId': lockerId}, {'locationId': locationId}]}, {'$set': params})
            if res.modified_count == 0:
                return {'code': 'not_found', 'description': 'nothing updated'}, 404
            elif res.modified_count != 1:
                return {'code': 'unknown', 'description': 'Unknown error occured'}, 500
            else:
                return dumps(params)
    else:
        if requires_scope('read:locations'):
            # parameter validation locationId
            if re.fullmatch(r'^L[0-9]{7}', locationId) is None:
                return {'code': 'bad_request', 'description': 'invalid locationId'}, 400
            # parameter validation rackId
            if re.fullmatch(r'^R[0-9]{7}B[0-9]{3}', lockerId) is None:
                return {'code': 'bad_request', 'description': 'invalid lockerId'}, 400
            pipe = [
                {
                    '$match': { 'lockerId': lockerId }
                },
                {
                    '$match': { 'locationId': locationId}
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
                    '$lookup': {
                        'from': 'locations',
                        'localField': 'locationId',
                        'foreignField': 'locationId',
                        'as': 'location'
                    }
                },
                {
                    '$unwind': {
                        'path': '$location',
                        'preserveNullAndEmptyArrays': True
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'itemId': 0,
                        'locationId': 0,
                        'item._id': 0,
                        'location._id': 0
                    }
                }
            ]
            res = list(col_lockers.aggregate(pipeline=pipe))
            if len(res) == 0:
                return {'code': 'not_found', 'description': 'Locker not found'}, 400
            else:
                return dumps(res[0])

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)