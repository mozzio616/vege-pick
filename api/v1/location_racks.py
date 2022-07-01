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

v1_location_racks = Blueprint('v1_location_racks', __name__, url_prefix='/api/v1')
@v1_location_racks.route('/locations/<locationId>/racks', methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations(locationId):

    if request.method == 'POST':
        if requires_scope('update:locations'):
            # parameter validation locationId
            if re.fullmatch(r'^L[0-9]{7}', locationId) is None:
                return {'code': 'bad_request', 'description': 'invalid locationId'}, 400
            # parameter validation rackId
            if request.json['rackId'] is None:
                return {'code': 'bad_request', 'description': 'rackId missing'}, 400
            elif re.fullmatch(r'^R[0-9]{7}', request.json['rackId']) is None:
                return {'code': 'bad_request', 'description': 'invalid rackId'}, 400
            else:
                rackId = request.json['rackId']
            # resource validation location
            if col_locations.find_one({'locationId': locationId}) is None:
                return {'code': 'not_found', 'description': 'Location not found'}, 404
            # resource validation rack
            rack = col_racks.find_one({'rackId': rackId})
            if rack is None:
                return {'code': 'not_found', 'description': 'Rack not found'}, 404
            elif rack['locationId'] is not None:
                return {'code': 'bad_request', 'description': 'Rack already assigned'}, 400
            # resource validation locker
            lockers = list(col_lockers.find({'rackId': rackId}).sort([('lockerId', 1)]))
            num = len(lockers)
            if num == 0:
                return {'code': 'not_found', 'description': 'Locker not found'}, 404
            # set start locker no.
            pipe = [
                {
                    '$match': { 'locationId': locationId }
                },
                {
                    '$group': {
                        '_id': '$locationId',
                        'min': { '$min': '$lockerNo'},
                        'max': { '$max': '$lockerNo'}
                    }
                }
            ]
            res = list(col_lockers.aggregate(pipeline=pipe))
            if len(res) == 0:
                startLockerNo = 1
            else:
                startLockerNo = res[0]['max'] + 1
            # update rack
            res = col_racks.update_one({'rackId': rackId}, {'$set': {'locationId': locationId}})
            if res.modified_count != 1:
                return {'code': 'unknown', 'description': 'failed to update rack'}, 500
            # update lockers
            i = 0
            lockerNo = startLockerNo
            while (i < num):
                res = col_lockers.update_one({'lockerId': lockers[i]['lockerId']}, {'$set': {'locationId': locationId, 'rackId': rackId, 'lockerNo': lockerNo}})
                if res.modified_count != 1:
                    return {'code': 'unknown', 'description': 'failed to update locker ' + lockers[i]['lockerId']}, 500
                    break
                i += 1
                lockerNo += 1
            response = request.json
            response['locationId'] = locationId
            return dumps(response)
    else:
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
            print(locationId)
            pipe = [
                {
                    '$match': { 'locationId': locationId }
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
                    '$unwind': {
                        'path': '$lockerIds',
                        'preserveNullAndEmptyArrays': True
                    }
                },
                {
                    '$lookup': {
                        'from': 'lockers',
                        'localField': 'lockerIds',
                        'foreignField': 'lockerId',
                        'as': 'locker'
                    }
                },
                {
                    '$unwind': {
                        'path': '$locker',
                        'preserveNullAndEmptyArrays': True
                    }
                },
                {
                    '$group': {
                        '_id': '$rackId',
                        'rackId': {
                            '$addToSet': '$rackId'
                        },
                        'location': {
                            '$addToSet': '$location'
                        },
                        'lockers': {
                            '$push': {
                                'lockerId': '$locker.lockerId',
                                'lockerNo': '$locker.lockerNo',
                                'itemId': '$locker.itemId',
                                'isAvailable': '$locker.isAvailable'
                            }
                        }
                    }
                },
                {
                    '$unwind': {
                        'path': '$rackId',
                        'preserveNullAndEmptyArrays': True
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
                        'location._id': 0
                    }
                },
                {
                    '$sort': {
                        'rackId': 1,
                        'lockers.lockerId': 1
                    }
                }
            ]
            res_all = list(col_racks.aggregate(pipeline=pipe))
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
            res = list(col_racks.aggregate(pipeline=pipe))
            # return response
            response = {}
            response['current_page'] = page
            response['last_page'] = last_page
            if len(res) == 0:
                response['racks'] = []
            else:
                response['racks'] = res
            return dumps(response)

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)