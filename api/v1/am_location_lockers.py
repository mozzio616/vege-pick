import math
import os
import urllib.parse
from urllib.robotparser import RequestRate
import pymongo
from bson.json_util import dumps
from datetime import datetime
from dotenv import load_dotenv
from flask import Blueprint, request, _request_ctx_stack
from flask_cors import cross_origin
from bson.json_util import dumps
from db import db
from auth import requires_auth, requires_scope, AuthError

load_dotenv()

try:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))
except:
    LIMIT = 5

col_locations = db.locations

v1_am_location_lockers = Blueprint('v1_am_location_lockers', __name__, url_prefix='/api/v1')
@v1_am_location_lockers.route('/ams/<user_id>/locations/<locationId>/lockers')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def location_lockers(user_id, locationId):
    user_id = urllib.parse.unquote(user_id)
    if requires_auth('read:am_locations') or requires_scope('read:locations'):
        if requires_scope('read:locations') is False:
            if user_id != _request_ctx_stack.top.current_user['sub']:
                print(request.remote_addr + ' - - [' + datetime.now().strftime('%d/%b/%Y %H:%M:%S') + '] Invalid user ID request. token->' + _request_ctx_stack.top.current_user['sub'] + ' request->' + user_id)
                raise AuthError({
                    "code": "Unauthorized",
                    "description": "You don't have access to this resource"
                }, 403)

        if request.args.get('limit') is None:
            limit = LIMIT
        else:
            limit = int(request.args.get('limit'))

        if request.args.get('page') is None:
            page = 1
        else:
            page = int(request.args.get('page'))

        pipe = [
            {
                '$match': {
                    '$and': [
                        {'locationId': locationId},
                        {'ams': [user_id]}
                    ]
                }
            },
            {
                '$lookup': {
                    'from': 'racks',
                    'localField': 'locationId',
                    'foreignField': 'locationId',
                    'as': 'rack'
                }
            },
            {
                '$unwind': {
                    'path': '$rack',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$lookup': {
                    'from': 'lockers',
                    'localField': 'rack.rackId',
                    'foreignField': 'rackId',
                    'as': 'rack.locker'
                }
            },
            {
                '$unwind': {
                    'path': '$rack.locker',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$lookup': {
                    'from': 'items',
                    'localField': 'rack.locker.itemId',
                    'foreignField': 'itemId',
                    'as': 'rack.locker.item'
                }
            },
            {
                '$unwind': {
                    'path': '$rack.locker.item',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'rack._id': 0,
                    'rack.locationId': 0,
                    'rack.lockerIds': 0,
                    'rack.locker._id': 0,
                    'rack.locker.locationId': 0,
                    'rack.locker.rackId': 0,
                    'rack.locker.locationId': 0,
                    'rack.locker.itemId': 0,
                    'rack.locker.item._id': 0
                },
            },
            {
                '$sort': {
                    'locationId': 1,
                    'rack.rackId': 1,
                    'rack.locker.lockerId': 1
                }
            },
            {
                '$group': {
                    '_id': {
                        'locationId': '$locationId',
                        'locationNameJp': '$locationNameJp',
                        'locationNameEn': '$locationNameEn',
                        'lat': '$lat',
                        'lng': '$lng',
                        'icon': '$icon'
                    },
                    'lockers': {
                        '$push': '$rack',
                    }

                }
            }
        ]

        res_all = list(col_locations.aggregate(pipeline=pipe))
        num = len(res_all[0]['lockers'])
        skip = limit * (page -1)
        last_page = math.ceil(num/limit)

        pipe = [
            {
                '$match': {
                    '$and': [
                        {'locationId': locationId},
                        {'ams': [user_id]}
                    ]
                }
            },
            {
                '$lookup': {
                    'from': 'racks',
                    'localField': 'locationId',
                    'foreignField': 'locationId',
                    'as': 'rack'
                }
            },
            {
                '$unwind': {
                    'path': '$rack',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$lookup': {
                    'from': 'lockers',
                    'localField': 'rack.rackId',
                    'foreignField': 'rackId',
                    'as': 'rack.locker'
                }
            },
            {
                '$unwind': {
                    'path': '$rack.locker',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$lookup': {
                    'from': 'items',
                    'localField': 'rack.locker.itemId',
                    'foreignField': 'itemId',
                    'as': 'rack.locker.item'
                }
            },
            {
                '$unwind': {
                    'path': '$rack.locker.item',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'rack._id': 0,
                    'rack.locationId': 0,
                    'rack.lockerIds': 0,
                    'rack.locker._id': 0,
                    'rack.locker.locationId': 0,
                    'rack.locker.rackId': 0,
                    'rack.locker.locationId': 0,
                    'rack.locker.itemId': 0,
                    'rack.locker.item._id': 0
                },
            },
            {
                '$sort': {
                    'locationId': 1,
                    'rack.rackId': 1,
                    'rack.locker.lockerId': 1
                }
            },
            {
                '$skip': skip
            },
            {
                '$limit': limit
            },
            {
                '$group': {
                    '_id': {
                        'locationId': '$locationId',
                        'locationNameJp': '$locationNameJp',
                        'locationNameEn': '$locationNameEn',
                        'lat': '$lat',
                        'lng': '$lng',
                        'icon': '$icon'
                    },
                    'lockers': {
                        '$push': '$rack',
                    }

                }
            }
        ]

        res = list(col_locations.aggregate(pipeline=pipe))

        if len(res) == 0:
            return {'code': 'invalid_location_id', 'description': 'Invalid locationID'}, 404
        else:
            response = {}
            response['current_page'] = page
            response['last_page'] = last_page
            response['location'] = res[0]['_id']
            if res[0]['lockers'][0]['locker'] == {}:
                response['lockers'] = []
            else:
                response['lockers'] = res[0]['lockers']
            return dumps(response)

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)