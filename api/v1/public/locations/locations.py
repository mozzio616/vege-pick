import os
import math
from flask import Blueprint, request
from bson.json_util import dumps
import pymongo
from dotenv import load_dotenv
from db import db

load_dotenv()

if os.getenv('DEFAULT_LOCATIONS_LIMIT') is None:
    LIMIT = 5
else:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))

col_locations = db.locations

v1_locations = Blueprint('v1_locations', __name__, url_prefix='/api/v1/locations')
@v1_locations.route('')
def locations():

    if request.args.get('searchKey') is None:
        searchKey = ''
    else:
        searchKey = request.args.get('searchKey')
    
    if request.args.get('limit') is None:
        limit = LIMIT
    else:
        limit = int(request.args.get('limit'))
    
    if request.args.get('page') is None:
        page = 1
    else:
        page = int(request.args.get('page'))

    res_all = col_locations.find({
        '$or': [
            {'locationNameJp': {'$regex': searchKey}},
            {'locationNameEn': {'$regex': searchKey}}
        ]
    })
    all = list(res_all)
    num = len(all)

    skip = limit * (page - 1)  
    last_page = math.ceil(num/limit)

    locations = col_locations.find({
        '$or': [
            {'locationNameJp': {'$regex': searchKey}},
            {'locationNameEn': {'$regex': searchKey}}
        ]
    }, {'_id': False}).sort([('locationId', pymongo.ASCENDING)]).skip(skip).limit(limit) 
    response = {
        'current_page': page,
        'last_page': last_page,
        'locations': locations
    }
    return dumps(response)
