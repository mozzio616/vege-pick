import math
import os
from bson.json_util import dumps
from dotenv import load_dotenv
from flask import Blueprint, request
from flask_cors import cross_origin
from db import db
from auth import requires_auth, requires_scope, AuthError

load_dotenv()

AUTH0_DOMAIN = os.environ['AUTH0_DOMAIN']

try:
    LIMIT = int(os.getenv('DEFAULT_LOCATIONS_LIMIT'))
except:
    LIMIT = 1000

col_token = db.token
col_locations = db.locations
col_users = db.users
col_items = db.items

def new_item_id():
    res = list(col_items.find({ 'itemId': { '$not': { '$regex': 'I9999999'}}}).sort([('itemId', -1)]).limit(1))
    current_max_item_id = res[0]['itemId']
    num = int(current_max_item_id[1:]) + 1
    new_item_id = 'I' + str(num).zfill(7)
    return new_item_id    


v1_items = Blueprint('v1_items', __name__, url_prefix='/api/v1')
@v1_items.route('/items', methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def locations():
    if request.method == 'POST':
        if requires_scope('post:items'):
            # validate request parameters
            try:
                itemName = request.json['itemName']
            except KeyError:
                return {'code': 'bad_request', 'description': 'item name missing'}, 400

            try:
                itemDescription = request.json['itemDescription']
            except KeyError:
                return {'code': 'bad_request', 'description': 'item description missing'}, 400

            try:
                itemPrice = request.json['itemPrice']
                itemPrice = int(itemPrice)
            except KeyError:
                return {'code': 'bad_request', 'description': 'item price missing'}, 400
            except ValueError:
                return {'code': 'bad_request', 'description': 'item price must be integer'}, 400                

            try:
                itemImg = request.json['itemImg']
            except KeyError:
                return {'code': 'bad_request', 'description': 'item image missing'}, 400

            # create item in database
            itemId = new_item_id()
            res = col_items.insert_one({
                'itemId': itemId,
                'itemName': itemName,
                'itemDescription': itemDescription,
                'itemPrice': itemPrice,
                'itemImg': itemImg
            })
            if res.acknowledged is True:
                print('item added to mongodb: ' + str(res.inserted_id))
                response = request.json
                response['itemId'] = itemId
                return dumps(response), 201
            else:
                print('failed to add item to mongodb')
                return {'code': 'unknown', 'description': 'failed to create the item'}, 500

    else:
        if requires_scope('read:items'):

            if request.args.get('q') is None:
                q = ''
            else:
                q = request.args.get('q')
            
            if request.args.get('limit') is None:
                limit = LIMIT
            else:
                limit = int(request.args.get('limit'))
            
            if request.args.get('page') is None:
                page = 1
            else:
                page = int(request.args.get('page'))

            res_all = list(col_items.find({
                '$and': [
                    { '$or':
                        [
                            {'itemName': { '$regex': q }},
                            {'itemDescription': { '$regex': q}},
                            {'itemId': { '$regex': q}}
                        ]
                    }
                ]
            }, {'_id': 0}))

            num = len(res_all)

            skip = limit * (page - 1)  
            last_page = math.ceil(num/limit)

            res = list(col_items.find({
                '$and': [
                    { '$or':
                        [
                            {'itemName': { '$regex': q }},
                            {'itemDescription': { '$regex': q}},
                            {'itemId': { '$regex': q}}
                        ]
                    }
                ]
            }, {'_id': 0}).sort([('name', 1)]).skip(skip).limit(limit))

            response = {
                'current_page': page,
                'last_page': last_page,
                'items': res
            }
            return dumps(response)

    raise AuthError({
        "code": "Unauthorized",
        "description": "You don't have access to this resource"
    }, 403)