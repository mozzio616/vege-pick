from flask import Blueprint, request
from bson.json_util import dumps
from db import db
import pymongo
from auth import requires_auth
from flask_cors import cross_origin
from dotenv import load_dotenv
import math
api_locations = Blueprint('api_locations', __name__)

collection_locations = db.locations
collection_racks = db.racks
collection_lockers = db.lockers
collection_items = db.items

@api_locations.route('/api/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'GET':

        if request.args.get('searchKey') is None:
            searchKey = ''
        else:
            searchKey = request.args.get('searchKey')
        if request.args.get('limit') is None:
            limit = 3
        else:
            limit = int(request.args.get('limit'))
        if request.args.get('page') is None:
            page = 1
        else:
            page = int(request.args.get('page'))

        res_total_locations = list(collection_locations.find({'$or':[{'locationNameJp': {'$regex': searchKey}}, {'locationNameEn': {'$regex': searchKey}}]}))
        num_total_locations = len(res_total_locations)

        skip = limit * (page - 1)  
        last_page = math.ceil(num_total_locations/limit)

        locations = collection_locations.find({'$or':[{'locationNameJp': {'$regex': searchKey}}, {'locationNameEn': {'$regex': searchKey}}]}).sort([('locationId', pymongo.ASCENDING)]).skip(skip).limit(limit) 
        response = {
            'crrent_page': page,
            'last_page': last_page,
            'locations': locations
        }
        return dumps(response)
    else:
        if type(request.json) is dict:
            res = collection_locations.insert_one(request.json)
            return dumps(res.inserted_id)
        elif type(request.json) is list:
            res = collection_locations.insert_many(request.json)
            return dumps(res.inserted_ids)
        else:
            return '', 400

@api_locations.route('/api/locations/<locationId>', methods=['GET', 'PUT', 'DELETE'])
def location(locationId):
    if request.method == 'GET':
        res = collection_locations.find_one({'locationId': locationId})
        if res is None:
            return '', 404
        else:
            return dumps(res)
    elif request.method == 'PUT':
        res = collection_locations.update_one({'locationId': locationId},{'$set': request.json})
        return {'modified_count': res.modified_count}
    else:
        res = collection_locations.delete_one({'locationId': locationId})
        return {'deleted_count': res.deleted_count}

@api_locations.route('/api/locations/<locationId>/racks')
def location_racks(locationId):
    res = collection_racks.find({'locationId': locationId})
    return dumps(res)

@api_locations.route('/api/locations/<locationId>/racks/<rackId>', methods=['GET', 'POST', 'DELETE'])
def location_rack(locationId, rackId):
    if request.method == 'GET':
        res = collection_racks.find_one({'rackId': rackId, 'locationId': locationId})
        if res is None:
            return '', 404
        else:
            return dumps(res)
    elif request.method == 'POST':
        res = collection_racks.find_one({'rackId': rackId})
        if res is None:
            return {'code': 'rack_not_found', 'description': 'Rack not found'}, 404
        elif res['locationId'] is not None:
            return {'code': 'rack_already_in_use', 'description': 'Rack already in use'}, 400
        else:
            numNewLockers = len(res['lockerIds'])
            res_lockers = collection_lockers.find({'locationId': locationId})
            res_racks = collection_racks.update_one({'rackId': rackId}, {'$set': {'locationId': locationId}})
            if request.json['startLockerNo'] is None:
                res_lockers = collection_lockers.update_many({'rackId': rackId, 'lockerId': res['lockerIds'][cnt]}, {'$set': {'locationId': locationId, 'lockerNo': None}})
            else:
                cnt = 0
                while cnt < numNewLockers:
                    res_lockers = collection_lockers.update_one({'rackId': rackId, 'lockerId': res['lockerIds'][cnt]}, {'$set': {'locationId': locationId, 'lockerNo': request.json['startLockerNo'] + cnt}})
                    cnt = cnt + 1
                response = { 'modified_count': res_racks.modified_count}
            return dumps(response)
    else:
        res_racks = collection_racks.find_one({'rackId': rackId, 'locationId': locationId})
        if res_racks is None:
            return {'code': 'rack_not_found', 'description': 'Rack not found'}
        else:
            numLockers = len(res_racks['lockerIds'])
            res_lockers = collection_lockers.update_many({'rackId': rackId, 'locationId': locationId}, {'$set': {'locationId': None, 'lockerNo': None}})
            if res_lockers.modified_count != numLockers:
                return {'code': 'mismatch', 'description': 'Modified count is not equal to num of lockers'}, 500
            else:
                res_racks = collection_racks.update_one({'rackId': rackId, 'locationId': locationId}, {'$set': {'locationId': None}})
                if res_racks.modified_count == 1:
                    return {'modified_rack': res_racks.modified_count, 'modified_lockders': res_lockers.modified_count}
                elif res_racks.modified_count == 0 :
                    return {'code': 'rack_not_found', 'description': 'Rack not deleted'}, 404
                else:
                    return {'code': 'unknown_error', 'description': str(res_racks.modified_count) + ' racks deleted'}, 500

@api_locations.route('/api/locations/<locationId>/lockers', methods=['GET', 'POST', 'PUT', 'DELETE'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def location_lockers(locationId):
    if request.method == 'GET':
        location = collection_locations.find_one({'locationId': locationId})
        lockers = collection_lockers.find({'locationId': locationId}).sort([('lockerNo', pymongo.ASCENDING)])
        items = list(collection_items.find().sort([('itemId', pymongo.ASCENDING)]))
        res = []
        for locker in lockers:
            idx = next((i for i, x in enumerate(items) if x["itemId"] == locker['itemId']), None)
            locker['locationNameJp'] = location['locationNameJp']
            locker['locationNameEn'] = location['locationNameEn']
            locker['lat'] = location['lat']
            locker['lng'] = location['lng']
            locker['icon'] = location['icon']
            locker['itemName'] = items[idx]['itemName']
            locker['itemDescription'] = items[idx]['itemDescription']
            locker['itemPrice'] = items[idx]['itemPrice']
            locker['itemImg'] = items[idx]['itemImg']
            res.append(locker)
        return dumps(res)
    elif request.method == 'PUT':
        res = collection_locations.update_one({'locationId': locationId},{'$set': request.json})
        return {'modified_count': res.modified_count}
    else:
        res = collection_locations.delete_one({'locationId': locationId})
        return {'deleted_count': res.deleted_count}