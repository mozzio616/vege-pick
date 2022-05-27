from flask import Blueprint, request
from bson.json_util import dumps
from api.db import db
import pymongo

locations = Blueprint('locations', __name__)

collection_locations = db.locations
collection_lockers = db.lockers
collection_items = db.items

@locations.route('/api/locations', methods=['GET', 'POST'])
def api_locations():
    if request.method == 'GET':
        locations = collection_locations.find()
        return dumps(locations)
    else:
        if type(request.json) is dict:
            res = collection_locations.insert_one(request.json)
            return dumps(res.inserted_id)
        elif type(request.json) is list:
            res = collection_locations.insert_many(request.json)
            return dumps(res.inserted_ids)
        else:
            return '', 400

@locations.route('/api/locations/<locationId>', methods=['GET', 'PUT', 'DELETE'])
def api_location(locationId):
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

@locations.route('/api/locations/<locationId>/lockers', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_location_lockers(locationId):
    if request.method == 'GET':
        lockers = collection_lockers.find({'locationId': locationId}).sort([('lockerNo', pymongo.ASCENDING)])
        res = []
        for locker in lockers:
            item = collection_items.find_one({'itemId': locker['itemId']})
            locker['itemName'] = item['itemName']
            locker['itemDescription'] = item['itemDescription']
            locker['itemPrice'] = item['itemPrice']
            locker['itemImg'] = item['itemImg']
            res.append(locker)
        return dumps(res)
    elif request.method == 'PUT':
        res = collection_locations.update_one({'locationId': locationId},{'$set': request.json})
        return {'modified_count': res.modified_count}
    else:
        res = collection_locations.delete_one({'locationId': locationId})
        return {'deleted_count': res.deleted_count}