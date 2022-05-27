from flask import Blueprint, request
from bson.json_util import dumps
from api.db import db

items = Blueprint('items', __name__)

collection_items = db.items

@items.route('/api/items', methods=['GET', 'POST'])
def api_items():
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

@items.route('/api/items/<itemId>')
def api_item(itemId):
    item = collection_items.find_one({'itemId': itemId})
    return dumps(item)