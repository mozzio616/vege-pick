from flask import Blueprint, request, _request_ctx_stack
from flask_cors import cross_origin
from bson.json_util import dumps
from datetime import datetime
import urllib.parse

from db import db
from auth import requires_auth, requires_scope, AuthError

col_locations = db.locations

v1_am_location = Blueprint('v1_am_location', __name__, url_prefix='/api/v1')
@v1_am_location.route('/ams/<user_id>/locations/<locationId>')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(user_id, locationId):
    user_id = urllib.parse.unquote(user_id)
    if requires_scope('read:am_locations') or requires_scope('read:locations'):
        if requires_scope('read:locations') is False:
            if user_id != _request_ctx_stack.top.current_user['name']:
                print(request.remote_addr + ' - - [' + datetime.now().strftime('%d/%b/%Y %H:%M:%S') + '] Invalid user ID request. token->' + _request_ctx_stack.top.current_user['name'] + ' request->' + user_id)
                raise AuthError({
                    "code": "Unauthorized",
                    "description": "You don't have access to this resource"
                }, 403)

        res = col_locations.find_one({
            '$and': [
                { 'locationId': locationId },
                { 'ams': { '$in': [ user_id ] }}
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