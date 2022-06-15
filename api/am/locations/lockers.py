from flask import Blueprint, request
from bson.json_util import dumps
from db import db
import pymongo
from auth import requires_auth
from flask_cors import cross_origin
from dotenv import load_dotenv
import math
api_am_location_lockers = Blueprint('api_location_lockers', __name__, url_prefix='/api/am/locations/<locationId>')

collection_locations = db.locations
collection_racks = db.racks
collection_lockers = db.lockers
collection_items = db.items

@api_am_location_lockers.route('/lockers', methods=['GET', 'POST', 'PUT', 'DELETE'])
#@cross_origin(headers=["Content-Type", "Authorization"])
#@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
#@requires_auth
def am_location_lockers(locationId):
    if request.method == 'GET':
        pipe = [
            {
                '$match': {
                    'locationId': locationId
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
                        'locationID': '$locationId',
                        'locationNameJp': '$locationNameJp',
                        'locationNameEn': '$locationNameEn',
                        'lat': '$lat',
                        'lng': '$lng',
                        'icon': '$icon'
                    },
                    'racks': {
                        '$push': '$rack',
                    }

                }
            }
        ]

        res = list(collection_locations.aggregate(pipeline=pipe))
        response = {}
        response['location'] = res[0]['_id']
        response['racks'] = res[0]['racks']
        return dumps(response)
    elif request.method == 'PUT':
        res = collection_locations.update_one({'locationId': locationId},{'$set': request.json})
        return {'modified_count': res.modified_count}
    else:
        res = collection_locations.delete_one({'locationId': locationId})
        return {'deleted_count': res.deleted_count}