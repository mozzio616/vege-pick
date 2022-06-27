from flask import Blueprint, request
from flask_cors import cross_origin
from bson.json_util import dumps
from dotenv import load_dotenv
import math, os

from db import db
from auth import requires_auth, requires_scope, AuthError

load_dotenv()

try:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))
except:
    LIMIT = 5

col_locations = db.locations

v1_location_am = Blueprint('v1_location_am', __name__, url_prefix='/api/v1')
@v1_location_am.route('/locations/<locationId>/ams/<userId>', methods=['GET', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(locationId, userId):

    if request.method == 'DELETE':
        if requires_scope('update:locations'):            
            res = col_locations.find_one({'$and': [{'locationId': locationId}, {'ams': {'$in': [userId]}}]})
            if res is None:
                return {'code': 'not_found', 'description': 'Location or area manager not found'}, 404
            ams = res['ams']
            ams.remove(userId)
            res = col_locations.update_one({'locationId': locationId}, {'$set': {'ams': ams}})
            if res.modified_count == 0:
                return {'code': 'not_found', 'description': 'No delete'}, 404
            elif res.modified_count != 1:
                return {'code': 'delete_failure', 'description': 'Unknown error occured'}, 500
            else:
                response = {'ams': [], 'locationId': locationId}
                return dumps(response)
    else:
        if requires_scope('read:locations'):            
            res = col_locations.find_one({'$and': [{'locationId': locationId}, {'ams': {'$in': [userId]}}]})
            if res is None:
                return {'code': 'not_found', 'description': 'Location or area manager not found'}, 404
            else:
                return {'ams': [userId], 'locationId': locationId}

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)