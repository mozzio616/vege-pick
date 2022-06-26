from flask import Blueprint, request, _request_ctx_stack
from flask_cors import cross_origin
from bson.json_util import dumps
from datetime import datetime
import urllib.parse

from db import db
from auth import requires_auth, requires_scope, AuthError

col_locations = db.locations
col_lockers = db.lockers

v1_am_location_locker = Blueprint('v1_am_location_locker', __name__, url_prefix='/api/v1')
@v1_am_location_locker.route('/ams/<user_id>/locations/<locationId>/lockers/<lockerId>')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(user_id, locationId, lockerId):
    user_id = urllib.parse.unquote(user_id)
    if requires_scope('read:am_locations') or requires_scope('read:locations'):
        if requires_scope('read:locations') is False:
            if user_id != _request_ctx_stack.top.current_user['sub']:
                print(request.remote_addr + ' - - [' + datetime.now().strftime('%d/%b/%Y %H:%M:%S') + '] Invalid user ID request. token->' + _request_ctx_stack.top.current_user['sub'] + ' request->' + user_id)
                raise AuthError({
                    "code": "Unauthorized",
                    "description": "You don't have access to this resource"
                }, 403)

        res_location = col_locations.find_one({
            '$and': [
                { 'locationId': locationId },
                { 'ams': { '$in': [ user_id ] }}
            ]
        }, {'_id': False})
        if res_location is None:
            return {'code': 'not_found', 'description': 'Location not found'}, 404
        else:
            res_locker = col_lockers.find_one({
                '$and': [
                    { 'locationId': locationId },
                    { 'lockerId': lockerId}
                ]
            }, {'_id': False})
            if res_locker is None:
                return {'code': 'not_found', 'description': 'Locker not found'}, 404
            else:
                response = {}
                response['location'] = res_location
                response['locker'] = res_locker
                return dumps(response)

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)