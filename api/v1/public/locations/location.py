from flask import Blueprint
from bson.json_util import dumps
from db import db

col_locations = db.locations

v1_location = Blueprint('v1_location', __name__, url_prefix='/api/v1/locations')

@v1_location.route('/<locationId>')
def location(locationId):
    res = col_locations.find_one({'locationId': locationId}, {'_id': False})
    if res is None:
        return {'code': 'location_not_found', 'description': 'Location not found'}, 404
    else:
        return dumps(res)
