from flask import Blueprint
from bson.json_util import dumps
from db import db

col_racks = db.racks

v1_racks = Blueprint('v1_racks', __name__, url_prefix='/api/v1/locations')
@v1_racks.route('/<locationId>/racks')
def location_racks(locationId):
    res = col_racks.find({'locationId': locationId}, {'_id': False})
    return dumps(res)
