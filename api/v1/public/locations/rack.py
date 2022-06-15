import os
from json import load
from flask import Blueprint
from bson.json_util import dumps
from db import db

col_racks = db.racks

v1_rack = Blueprint('v1_rack', __name__, url_prefix='/api/v1/locations')
@v1_rack.route('/<locationId>/racks/<rackId>')
def location_rack(locationId, rackId):
    res = col_racks.find_one({'rackId': rackId, 'locationId': locationId})
    if res is None:
        return {'code': 'rack_not_found', 'description': 'Rack not found'}, 404
    else:
        return dumps(res)
