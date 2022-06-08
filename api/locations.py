from flask import Blueprint, request
from bson.json_util import dumps
from db import db
import pymongo
from auth import requires_auth
from flask_cors import cross_origin
from dotenv import load_dotenv
api_locations = Blueprint('api_locations', __name__)

collection_locations = db.locations
collection_lockers = db.lockers
collection_items = db.items

@api_locations.route('/api/locations', methods=['GET', 'POST'])
def locations():
    if request.method == 'GET':
        locations = collection_locations.find().sort([('locationId', pymongo.ASCENDING)])
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