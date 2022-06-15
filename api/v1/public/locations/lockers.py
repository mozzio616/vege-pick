from flask import Blueprint
from bson.json_util import dumps
from db import db

col_locations = db.locations

v1_lockers = Blueprint('v1_lockers', __name__, url_prefix='/api/v1/locations')
@v1_lockers.route('/<locationId>/lockers')
def location_lockers(locationId):

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
        response['location'] = res[0]['_id']
        if res[0]['lockers'][0]['locker'] == {}:
            response['lockers'] = []
        else:
            response['lockers'] = res[0]['lockers']
        return dumps(response)
