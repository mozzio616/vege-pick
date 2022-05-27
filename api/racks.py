from flask import Blueprint, request
from bson.json_util import dumps
from index import db

rack_lockers = Blueprint('rack_items', __name__, url_prefix='/api/locations/<locationId>/racks/<rackId>/lockers')

collection_racks = db.racks
collection_items = db.items

@rack_lockers.route('/', methods=['GET', 'POST'])
def rack_lockers(locationId, rackId):
    if request.method == 'GET':
        rack = collection_racks.find_one({'locationId': locationId, 'rackId': rackId})
        lockers = rack['lockers']
        for locker in lockers:
            item = collection_items.find_one({'itemId': locker['itemId']})
            locker['itemName'] = item['itemName']
            locker['itemDescription'] = item['itemDescription']
            locker['itemPrice'] = item['itemPrice']
            locker['itemImg'] = item['itemImg']
        return lockers

