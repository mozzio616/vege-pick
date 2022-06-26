from flask import Blueprint, request
from flask_cors import cross_origin
from bson.json_util import dumps

from db import db
from auth import requires_auth, requires_scope, AuthError

col_locations = db.locations

v1_location = Blueprint('v1_location', __name__, url_prefix='/api/v1')
@v1_location.route('/locations/<locationId>', methods=['GET', 'PATCH'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(locationId):

    if request.method == 'PATCH':
        if requires_scope('update:locations'):
            data = request.json
            res = col_locations.update_one({'locationId': locationId}, data)
            if res.modified_count == 0:
                return {'code': 'not_found', 'description': 'No update'}, 404
            elif res.modified_count != 1:
                return {'code': 'update_failure', 'description': 'Unknown error occured'}, 500
            else:
                response = request.json
                response['locationId'] = locationId
                return dumps(response)
    else:
        if requires_scope('read:locations'):
            res = col_locations.find_one({
                '$and': [
                    { 'locationId': locationId }
                ]
            }, {'_id': False})
            if res is None:
                return {'code': 'not_found', 'description': 'Location not found'}, 404
            else:
                return dumps(res)
    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)