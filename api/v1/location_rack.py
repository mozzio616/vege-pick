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

v1_location_rack = Blueprint('v1_location_rack', __name__, url_prefix='/api/v1')
@v1_location_rack.route('/locations/<locationId>/racks/<rackId>', methods=['GET', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(locationId, rackId):

    if request.method == 'DELETE':
        if requires_scope('update:locations'):
            # parameter validation locationId
            if re.fullmatch(r'^L[0-9]{7}', locationId) is None:
                return {'code': 'bad_request', 'description': 'invalid locationId'}, 400
            # parameter validation rackId
            if re.fullmatch(r'^R[0-9]{7}', rackId) is None:
                return {'code': 'bad_request', 'description': 'invalid rackId'}, 400
            # resource validation location
            if col_locations.find_one({'locationId': locationId}) is None:
                return {'code': 'not_found', 'description': 'Location not found'}, 404
            # resource validation rack
            rack = col_racks.find_one({'$and': [{'rackId': rackId}, {'locationId': locationId}]})
            if rack is None:
                return {'code': 'not_found', 'description': 'Rack not found'}, 404
            # resource validation locker
            lockers = list(col_lockers.find({'$and': [{'rackId': rackId}, {'locationId': locationId}]}).sort([('lockerId', 1)]))
            num = len(lockers)
            if num == 0:
                return {'code': 'not_found', 'description': 'Locker not found'}, 404
            # set locationId: null for lockers
            res = col_lockers.update_many({'$and': [{'rackId': rackId}, {'locationId': locationId}]}, {'$set': {'locationId': None, 'lockerNo': None}})
            if res.modified_count != num:
                return {'code': 'unknown', 'description': 'Number of deleted locker mismatch'}, 500
            # set locationId: null for racks
            res = col_racks.update_one({'$and': [{'rackId': rackId}, {'locationId': locationId}]}, {'$set': {'locationId': None}})
            if res.modified_count != 1:
                return {'code': 'unknown', 'description': 'Number of deleted rack mismatch'}, 500
            response = {
                'locationId': locationId,
                'rackId': rackId
            }
            return dumps(response)
    else:
        if requires_scope('read:locations'):
            # parameter validation locationId
            if re.fullmatch(r'^L[0-9]{7}', locationId) is None:
                return {'code': 'bad_request', 'description': 'invalid locationId'}, 400
            # parameter validation rackId
            if re.fullmatch(r'^R[0-9]{7}', rackId) is None:
                return {'code': 'bad_request', 'description': 'invalid rackId'}, 400
            res = col_racks.find_one({'$and': [{'rackId': rackId}, {'locationId': locationId}]})
            if res is None:
                return {'code': 'not_found', 'description': 'Locker or rack not found'}, 400
            return dumps(res)

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)