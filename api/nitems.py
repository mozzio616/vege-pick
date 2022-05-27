from flask import Blueprint, request
from bson.json_util import dumps
from index import db

nitems = Blueprint('nitems', __name__, url_prefix='/api/nitems')

collection_nitems = db.nitems

@nitems.route('/', methods=['GET', 'POST'])
def nitems():
    if request.method == 'GET':
        nitems = collection_nitems.find()
        return dumps(nitems)
    else:
        if type(request.json) is list:
            res = collection_nitems.insert_many(request.json)
            return {'inserted_ids': res.inserted_ids}
        else:
            res = collection_nitems.insert_one(request.json)
            return {'inserted_id': res.inserted_id}
