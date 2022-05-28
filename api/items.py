from flask import Blueprint, request
from bson.json_util import dumps
from api.db import db

api_items = Blueprint('api_items', __name__)

collection_items = db.items

@api_items.route('/api/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        items = collection_items.find()
        return dumps(items)
    else:
        if type(request.json) is list:
            res = collection_items.insert_many(request.json)
            return dumps(res.inserted_ids)
        else:
            res = collection_items.insert_one(request.json)
            return dumps(res.inserted_id)

@api_items.route('/api/items/<itemId>')
def item(itemId):
    item = collection_items.find_one({'itemId': itemId})
    return dumps(item)