from flask import Blueprint, request
from bson.json_util import dumps
from db import db

api_lockers = Blueprint('api_lockers', __name__)

collection_locations = db.locations
collection_lockers = db.lockers
collection_items = db.items

@api_lockers.route('/api/lockers', methods=['GET', 'POST'])
def lockers():
    if request.method == 'GET':
        lockers = collection_lockers.find()
        return dumps(lockers)
    else:
        if type(request.json) is list:
            res = collection_lockers.insert_many(request.json)
            return dumps(res.inserted_ids)
        else:
            res = collection_lockers.insert_one(request.json)
            return dumps(res.inserted_id)

@api_lockers.route('/api/lockers/<lockerId>')
def locker(lockerId):
    locker = collection_lockers.find_one({'lockerId': lockerId})
    if locker is None:
        return {'code': 'locker_not_found', 'description': 'Locker not found'}, 404
    else:
        locationId = locker['locationId']
        location = collection_locations.find_one({'locationId': locationId})
        if location is None:
            return {'code': 'location_not_found', 'description': 'Location not found'}, 404
        else:
            item = collection_items.find_one({'itemId': locker['itemId']})
            if item is None:
                return {'code': 'item_not_found', 'description': 'item not found'}, 404
            else:
                locker['locationNameJp'] = location['locationNameJp']
                locker['locationNameEn'] = location['locationNameEn']
                locker['lat'] = location['lat']
                locker['lng'] = location['lng']
                locker['icon'] = location['icon']
                locker['itemName'] = item['itemName']
                locker['itemDescripton'] = item['itemDescription']
                locker['itemPrice'] = item['itemPrice']
                locker['itemImg'] = item['itemImg']
                return dumps(locker)

@api_lockers.route('/api/lockers/<lockerId>/status', methods=['GET', 'PUT'])
def locker_status(lockerId):
    locker = collection_lockers.find_one({'lockerId': lockerId})
    if locker is None:
        return {'code': 'locker_not_found', 'description': 'Locker not found'}, 404
    elif request.method == 'GET':
        isAvailable = locker['isAvailable']
        return {'lockerId': lockerId, 'isAvailable': isAvailable}
    else:
        if 'isAvailable' in request.json and type(request.json['isAvailable']) is bool:
            isAvailable = request.json['isAvailable']
            locker = collection_lockers.update_one({'lockerId': lockerId}, {'$set':  {'isAvailable': isAvailable}})
            return {'lockerId': lockerId, 'isAvailable': isAvailable}
        else:
            return {'code': 'invalid_parameters', 'description': 'Invalid parameters'}, 400