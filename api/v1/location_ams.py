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

v1_location_ams = Blueprint('v1_location_ams', __name__, url_prefix='/api/v1')
@v1_location_ams.route('/locations/<locationId>/ams', methods=['GET', 'PATCH'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(locationId):

    if request.method == 'PATCH':
        if requires_scope('update:locations'):
            if request.json['userId'] is None:
                return {'code': 'bad_request', 'description': 'userId missing'}, 400
            else:
                userId = request.json['userId']
            res = col_locations.find_one({'locationId': locationId})
            if res is None:
                return {'code': 'not_found', 'description': 'Location not found'}, 404
            try:
                ams = res['ams']
            except KeyError:
                ams = []
            ams.append(userId)
            res = col_locations.update_one({'locationId': locationId}, {'$set': {'ams': ams}})
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
                        'locationId': locationId
                    }
                },
                {
                    '$unwind': {
                        'path': '$ams',
                        'preserveNullAndEmptyArrays': True
                    }
                },
                {
                    '$lookup': {
                        'from': 'users',
                        'localField': 'ams',
                        'foreignField': 'userId',
                        'as': 'am'
                    }
                },
                {
                    '$unwind': {
                        'path': '$am',
                        'preserveNullAndEmptyArrays': True
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'ams': 0,
                        'locationId': 0,
                        'locationNameJp': 0,
                        'locationNameEn': 0,
                        'lat': 0,
                        'lng': 0,
                        'icon': 0,
                        'am._id': 0,
                    }
                }
            ]

            res_all = list(col_locations.aggregate(pipeline=pipe))
            num = len(res_all)

            skip = limit * (page - 1)  
            last_page = math.ceil(num/limit)

            pipe = [
                {
                    '$match': {
                        'locationId': locationId
                    }
                },
                {
                    '$unwind': {
                        'path': '$ams',
                        'preserveNullAndEmptyArrays': True
                    }
                },
                {
                    '$lookup': {
                        'from': 'users',
                        'localField': 'ams',
                        'foreignField': 'userId',
                        'as': 'am'
                    }
                },
                {
                    '$unwind': {
                        'path': '$am',
                        'preserveNullAndEmptyArrays': True
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'ams': 0,
                        'locationId': 0,
                        'locationNameJp': 0,
                        'locationNameEn': 0,
                        'lat': 0,
                        'lng': 0,
                        'icon': 0,
                        'am._id': 0,
                    }
                },
                {
                    '$sort': {
                        'am.name': 1
                    }
                },
                {
                    '$skip': skip
                },
                {
                    '$limit': limit
                }
            ]

            res = list(col_locations.aggregate(pipeline=pipe))
            if len(res) == 0:
                return {'code': 'not_found', 'decsription': 'Location not found'}, 404
            else:
                response = {}
                response['current_page'] = page
                response['last_page'] = last_page
                if len(res_all[0]) == 0:
                    response['ams'] = []
                else:
                    response['ams'] = res
                return dumps(response)

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)