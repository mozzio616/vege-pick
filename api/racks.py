from flask import Blueprint, request
from bson.json_util import dumps
from db import db
import pymongo
from auth import requires_auth
from flask_cors import cross_origin
from dotenv import load_dotenv
import math

api_racks = Blueprint('api_racks', __name__)

collection_locations = db.locations
collection_racks = db.racks
collection_lockers = db.lockers
collection_items = db.items

@api_racks.route('/api/racks', methods=['GET', 'POST'])
def racks():
    if request.method == 'GET':
        res_total_racks = list(collection_racks.find())
        num_total_racks = len(res_total_racks)

        searchKey = request.args.get('searchKey')
        if request.args.get('limit') is None:
            limit = 3
        else:
            limit = int(request.args.get('limit'))
        if request.args.get('page') is None:
            page = 1
        else:
            page = int(request.args.get('page'))
        skip = limit * (page - 1)

        last_page = math.ceil(num_total_racks/limit)
        current_page = page
        if page == 1:
            previous_page = None
        else:
            previous_page = page - 1
        if page == last_page:
            next_page = None
        else:
            next_page = page + 1
        
        if searchKey is None:

            pipe = [
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
                    '$project': {
                        '_id': 0,
                        'rackId': 1,
                        'lockerIds': 1,
                        'location.locationId': 1,
                        'location.locationNameJp': 1,
                        'location.locationNameEn': 1,
                        'location.lat': 1,
                        'location.lng': 1,
                        'location.icon': 1
                },
                },
                {
                    '$sort': {
                        'rackId': 1
                    }
                },
                {
                    '$skip': skip
                },
                {
                    '$limit': limit
                }
            ]

            racks = collection_racks.aggregate(pipeline=pipe)
            #racks = collection_racks.find().sort([('rackId', pymongo.ASCENDING)])
        else: # currently not work
            locations = collection_locations.find({'$or':[{'locationNameJp': {'$regex': searchKey}}, {'locationNameEn': {'$regex': searchKey}}]})
            cnt = 0
            conds = []
            matched = list(locations)
            if len(matched) > 0:
                while cnt < len(matched):
                    cond = {'locationId': matched[cnt]['locationId']}
                    conds.append(cond)
                    cnt = cnt + 1
                racks = collection_racks.find({'$or': conds}).sort([('rackId', pymongo.ASCENDING)])
            else:
                racks = []
        
        response = {
            'current_page': current_page,
            'previous_page': previous_page,
            'next_page': next_page,
            'last_page': last_page,
            'racks': racks
        }
        return dumps(response)
    else:
        if type(request.json) is dict:
            rackId = request.json['rackId']
            numLockers = request.json['numLockers']
            initialItemId = request.json['initialItemId']
            lockerIds = []
            lockers = []
            cnt = 0
            while cnt < numLockers:
                cnt = cnt + 1
                lockerId = rackId + 'B' + str(cnt).zfill(3)
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
            rack = {
                'rackId': rackId,
                'locationId': None,
                'lockerIds': lockerIds
            }
            res_racks = collection_racks.insert_one(rack)
            res_lockers = collection_lockers.insert_many(lockers)
            response = {
                'rack': res_racks.inserted_id,
                'lockers': res_lockers.inserted_ids
            }
            return dumps(response)
        elif type(request.json) is list:
            res = collection_racks.insert_many(request.json)
            return dumps(res.inserted_ids)
        else:
            return '', 400

@api_racks.route('/api/racks/<rackId>', methods=['GET', 'PUT', 'DELETE'])
def rack(rackId):
    if request.method == 'GET':
        res = collection_racks.find_one({'rackId': rackId})
        if res is None:
            return '', 404
        else:
            return dumps(res)
    elif request.method == 'PUT':
        res = collection_racks.update_one({'rackId': rackId},{'$set': request.json})
        return {'modified_count': res.modified_count}
    else:
        res = collection_racks.delete_one({'rackId': rackId})
        return {'deleted_count': res.deleted_count}

@api_racks.route('/api/racks/<rackId>/lockers', methods=['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def rack_lockers(rackId):
    if request.method == 'GET':
        rack = collection_racks.find_one({'rackId': rackId})
        lockers = collection_lockers.find({'rackId': rackId}).sort([('lockerNo', pymongo.ASCENDING)])
        items = list(collection_items.find().sort([('itemId', pymongo.ASCENDING)]))
        res = []
        for locker in lockers:
            idx = next((i for i, x in enumerate(items) if x["itemId"] == locker['itemId']), None)
            locker['rackNameJp'] = rack['rackNameJp']
            locker['rackNameEn'] = rack['rackNameEn']
            locker['lat'] = rack['lat']
            locker['lng'] = rack['lng']
            locker['icon'] = rack['icon']
            locker['itemName'] = items[idx]['itemName']
            locker['itemDescription'] = items[idx]['itemDescription']
            locker['itemPrice'] = items[idx]['itemPrice']
            locker['itemImg'] = items[idx]['itemImg']
            res.append(locker)
        return dumps(res)
    elif request.method == 'PUT':
        res = collection_racks.update_one({'rackId': rackId},{'$set': request.json})
        return {'modified_count': res.modified_count}
    else:
        res = collection_racks.delete_one({'rackId': rackId})
        return {'deleted_count': res.deleted_count}