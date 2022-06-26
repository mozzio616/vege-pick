from flask import Blueprint, request, _request_ctx_stack
from flask_cors import cross_origin
from bson.json_util import dumps
from datetime import datetime
import urllib.parse

from db import db
from auth import requires_auth, requires_scope, AuthError

v1_am_location_locker_stock = Blueprint('v1_am_location_locker_stock', __name__, url_prefix='/api/v1')

col_locations = db.locations
col_lockers = db.lockers

@v1_am_location_locker_stock.route('/ams/<userId>/locations/<locationId>/lockers/<lockerId>/stock', methods=['GET', 'PATCH'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def am_location_locker_stock(userId, locationId, lockerId):
    userId = urllib.parse.unquote(userId)
    if request.method == 'PATCH':
        if requires_scope('update:am_locations') or requires_scope('update:locations'):
            if requires_scope('update:locations') is False:
                if userId != _request_ctx_stack.top.current_user['sub']:
                    print(request.remote_addr + ' - - [' + datetime.now().strftime('%d/%b/%Y %H:%M:%S') + '] Invalid user ID request. token->' + _request_ctx_stack.top.current_user['sub'] + ' request->' + userId)
                    raise AuthError({
                        "code": "Unauthorized",
                        "description": "You don't have access to this resource (invalid user)"
                    }, 403)
            res_location = col_locations.find_one({
                '$and': [
                    { 'locationId': locationId },
                    { 'ams': { '$in': [ userId ] }}
                ]
            }, {'_id': False})
            if res_location is None:
                return {'code': 'not_found', 'description': 'Location not found'}, 404
            else:
                if 'isAvailable' in request.json and type(request.json['isAvailable']) is bool:
                    isAvailable = request.json['isAvailable']
                    res_locker = col_lockers.update_one({
                        '$and': [
                            { 'locationId': locationId },
                            { 'lockerId': lockerId}
                        ]
                    }, {'$set': {'isAvailable': isAvailable}})
                    if res_locker.modified_count == 0:
                        return {'code': 'not_found', 'description': 'No update'}, 404
                    elif res_locker.modified_count != 1:
                        return {'code': 'update_failure', 'description': 'Unknown error occured'}, 500
                    else:
                        response = { 'lockerId': lockerId, 'isAvailable': isAvailable }
                        return dumps(response)
        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource (invalid scope)"
        }, 403)

    else:
        if requires_scope('read:am_locations') or requires_scope('read:locations'):
            if requires_scope('read:locations') is False:
                if userId != _request_ctx_stack.top.current_user['sub']:
                    print(request.remote_addr + ' - - [' + datetime.now().strftime('%d/%b/%Y %H:%M:%S') + '] Invalid user ID request. token->' + _request_ctx_stack.top.current_user['sub'] + ' request->' + userId)
                    raise AuthError({
                        "code": "Unauthorized",
                        "description": "You don't have access to this resource"
                    }, 403)
            res_location = col_locations.find_one({
                '$and': [
                    { 'locationId': locationId },
                    { 'ams': { '$in': [ userId ] }}
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
                    response = {'lockerId': lockerId, 'isAvailable': res_locker['isAvailable']}
                    return dumps(response)

        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource"
        }, 403)