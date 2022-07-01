from flask import Blueprint, request
from bson.json_util import dumps
from db import db
from auth import requires_auth, requires_scope, AuthError
from flask_cors import cross_origin
from dotenv import load_dotenv
import math, os, re

load_dotenv()

try:
    LIMIT = int(os.getenv('DEFAULT_LIMIT'))
except:
    LIMIT = 1000

if os.getenv('INITIAL_ITEM_ID') is None:
    initialItemId = 'I9999999'
else:
    initialItemId = os.getenv('INITIAL_ITEM_ID')

col_locations = db.locations
col_racks = db.racks
col_lockers = db.lockers
col_items = db.items

def new_rack_id():
    res = list(col_racks.find().sort([('rackId', -1)]).limit(1))
    current_max_rack_id = res[0]['rackId']
    num = int(current_max_rack_id[1:]) + 1
    new_rack_id = 'R' + str(num).zfill(7)
    return new_rack_id    

v1_racks = Blueprint('v1_racks', __name__, url_prefix='/api/v1')
@v1_racks.route('/racks', methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
#@requires_auth
def racks():
    if request.method == 'POST':
        if requires_scope('post:racks'):
            # validate request parameter
            try:
                numLockers = int(request.json['numLockers'])
            except:
                return {'code': 'bad_request', 'description': 'numLockers must be integer'}, 400
            # initialize parameters
            rackId = new_rack_id()
            # generate rack data
            lockerIds = []
            lockers = []
            cnt = 0
            while cnt < numLockers:
                lockerId = rackId + 'B' + str(cnt+1).zfill(3)
                lockerIds.append(lockerId)
                locker = {
                    'lockerId': lockerId,
                    'locationId': None,
                    'lockerNo': None,
                    'rackId': rackId,
                    'itemId': initialItemId,
                    'isAvailable': False
                }
                lockers.append(locker)
                cnt = cnt + 1
            rack = {
                'rackId': rackId,
                'locationId': None,
                'lockerIds': lockerIds
            }
            res_racks = col_racks.insert_one(rack)
            if res_racks.acknowledged is False:
                return {'code': 'unknown', 'description': 'failed to create a rack'}, 500
            res_lockers = col_lockers.insert_many(lockers)
            if len(res_lockers.inserted_ids) != numLockers:
                return {'code': 'unknown', 'description': 'failed to create lockers'}, 500
            return dumps(rack)
    else:
        if requires_scope('read:racks'):
            # validate query string
            try:
                limit = int(request.args.get('limit'))
            except:
                limit = LIMIT
            try:
                page = int(request.args.get('page'))
            except:
                page = 1
            pipe_postfix = [
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
                    '$sort': {
                        'rackId': 1,
                        'lockerIds': 1
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
                        'rackId': 1
                    }
                },
            ]
            if request.args.get('locationId') is None:
                pipe = pipe_postfix
            else:
                if request.args.get('locationId') == 'null':
                    pipe = [ { '$match': { 'locationId': None }} ]
                    pipe.extend(pipe_postfix)
                elif re.fullmatch(r'^L[0-9]{7}', request.args.get('locationId')) is None:
                    pipe = pipe_postfix
                else:
                    pipe = [ { '$match': { 'locationId': request.args.get('locationId') }} ]
                    pipe.extend(pipe_postfix)
            res_all = list(col_racks.aggregate(pipeline=pipe))
            num = len(res_all)
            skip = limit * (page - 1)  
            last_page = math.ceil(num/limit)
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
            if len(res) == 0:
                return {'code': 'not_found', 'decsription': 'Rack not found'}, 404
            else:
                response = {}
                response['current_page'] = page
                response['last_page'] = last_page
                response['racks'] = res
                return dumps(response)            

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)
