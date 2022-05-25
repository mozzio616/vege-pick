from tracemalloc import start
from flask import Flask, render_template, request, redirect
from flask_qrcode import QRcode
import paypayopa
import pymongo
from slack_sdk.webhook import WebhookClient
from flask_cors import CORS
import os, datetime
from bson.json_util import dumps

API_KEY = os.environ['PP_API_KEY']
API_SECRET = os.environ['PP_API_SECRET']
MERCHANT_ID = os.environ['PP_MERCHANT_ID']
REDIRECT_URL = os.environ['PP_REDIRECT_URL']
DB_HOST = os.environ['MONGO_HOST']
WEBHOOK_URL = os.environ['WEBHOOK_URL']

connection_url = DB_HOST

app = Flask(__name__)
CORS(app)

mongoClient = pymongo.MongoClient(connection_url)
db = mongoClient.lvl
collection_locations = db.locations
collection_items = db.items
collection_payments = db.payments

QRcode(app)
client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
client.set_assume_merchant(MERCHANT_ID)

def create_merchant_payment_id(itemId):
    dt = datetime.datetime.now()
    merchantPaymentId = itemId + dt.strftime('%Y%m%d%H%M%S')
    return merchantPaymentId

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/items')
def get_items():
    locationId = request.args.get('locationId')
    if locationId is None:
        return redirect('/search')
    else:
        location = collection_locations.find_one({'locationId': locationId})
        items = collection_items.find({'locationId': locationId}).sort([('itemId', pymongo.ASCENDING)])
        if location is None or items is None:
            return redirect('/search')
        else:
            return render_template('items.html', location=location, items=items)

@app.route('/code')
def create_code():
    locationId = request.args.get('locationId')
    itemId = request.args.get('itemId')
    if locationId is None or itemId is None:
        return redirect('/search')
    else:
        location = collection_locations.find_one({'locationId': locationId})
        item = collection_items.find_one({'locationId': locationId, 'itemId': itemId})
        if location is None:
            return redirect('/search')
        elif item is None:
            return redirect('/items?locationId=' + locationId)
        elif item['isAvailable'] is True:
            merchantPaymentId = create_merchant_payment_id(itemId)
            print(merchantPaymentId)
            req = {
                "merchantPaymentId": merchantPaymentId,
                "codeType": "ORDER_QR",
                "redirectUrl": REDIRECT_URL,
                "redirectType":"WEB_LINK",
                "orderDescription": item['itemName'],
                "orderItems": [{
                    "name": item['itemName'],
                    "category": "vegetables",
                    "quantity": 1,
                    "productId": itemId,
                    "unitPrice": {
                        "amount": 1,
                        "currency": "JPY"
                    }
                }],
                "amount": {
                    "amount": 1,
                    "currency": "JPY"
                },
            }
            response = client.Code.create_qr_code(req)
            resultCode = response['resultInfo']['code']
            if resultCode == 'SUCCESS':
                res_db = collection_items.update_one({'itemId': itemId}, {'$set': {'isAvailable': False}})
                message = merchantPaymentId + ':' + itemId
                webhook = WebhookClient(WEBHOOK_URL)
                res_webhook = webhook.send(text=message)
                url = response['data']['url']
                return render_template('code.html', url=url, location=location, item=item)
            else:
                return redirect('/items?locationId=' + locationId)
        else:
            return redirect('/sold?locationId=' + locationId)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/sold')
def sold():
    locationId = request.args.get('locationId')
    return render_template('sold.html', locationId=locationId)

@app.route('/api/locations', methods=['GET', 'POST'])
def api_locations():
    if request.method == 'GET':
        locations = collection_locations.find()
        return dumps(locations)
    else:
        if type(request.json) is dict:
            response = collection_locations.insert_one(request.json)
            return dumps(response.inserted_id)
        elif type(request.json) is list:
            response = collection_locations.insert_many(request.json)
            return dumps(response.inserted_ids)
        else:
            return 'null', 400

@app.route('/api/locations/<locationId>', methods=['GET', 'PUT', 'DELETE'])
def api_location(locationId):
    if request.method == 'GET':
        location = collection_locations.find_one({'locationId': locationId})
        return dumps(location)
    elif request.method == 'PUT':
        response = collection_locations.update_one({'locationId': locationId},{'$set': request.json})
        return {'modified_count': response.modified_count}
    else:
        response = collection_locations.delete_one({'locationId': locationId})
        return {'deleted_count': response.deleted_count}

@app.route('/api/items', methods=['GET', 'POST'])
def api_items():
    if request.method == 'GET':
        items = collection_items.find()
        return dumps(items)
    elif request.method == 'POST':
        for i, item in enumerate(request.json):
            collection_items.insert_one(item)
        response = {'message': str(len(request.json)) + ' items created.'}
        return response
    else:
        return '{}'

@app.route('/api/items/<itemId>/status', methods=['GET', 'PUT'])
def item_status(itemId):
    if request.method == 'GET':
        item = collection_items.find_one({'itemId': itemId})
        response = {'itemId': itemId, 'isAvailable': item['isAvailable']}
        return response
    elif request.method == 'PUT':
        isAvailable = request.json['isAvailable']
        item = collection_items.update_one({'itemId': itemId}, {'$set': {'isAvailable': isAvailable}})
        response = {'itemId': itemId, 'isAvailable': isAvailable}
        return response
    else:
        return {}

@app.route('/api/payments/<merchantPaymentId>/status')
def payment_status(merchantPaymentId):
    payment_detail = client.Code.get_payment_details(merchantPaymentId)
    status = payment_detail['data']['status']
    response = {'merchantPaymentId': merchantPaymentId, 'status': status}
    return response

@app.route('/api/payments/logs', methods=['GET', 'POST'])
def payments_logs():
    if request.method == 'GET':
        dt = datetime.datetime.now()
        if request.args.get('fm') is None:
            fm = dt + datetime.timedelta(weeks=-1)
        else:
            fm = datetime.datetime.fromisoformat(request.args.get('fm'))
        if request.args.get('to') is None:
            to = dt
        else:
            to = datetime.datetime.fromisoformat(request.args.get('to'))
        logs = collection_payments.find({'paid_at': {'$gte': fm, '$lte': to}})
        return dumps(logs)
    elif request.method == 'POST':
        if type(request.json) is list:   # to insert bulk test data
            logs = request.json
            message = []
            for log in logs:
                log['paid_at']  = datetime.datetime.fromisoformat(log['paid_at'])
                log['order_amount'] = int(log['order_amount'])
                log['year'] = int(log['year'])
                log['month'] = int(log['month'])
                log['day'] = int(log['day'])
                response = collection_payments.insert_one(log)
                message.append(response.inserted_id)
            return dumps(message)
        else:
            dt = datetime.datetime.fromisoformat(request.json['paid_at'])
            request.json['paid_at'] = dt
            request.json['order_amount'] = int(request.json['order_amount'])
            request.json['year'] = dt.year
            request.json['month'] = dt.month
            request.json['day'] = dt.day
            response = collection_payments.insert_one(request.json)
            #message = request.json['merchant_order_id'] + ':' + request.json['state']
            #webhook = WebhookClient(WEBHOOK_URL)
            #res_webhook = webhook.send(text=message)
            return dumps(response.inserted_id)
    else:
        return {}

@app.route('/api/sales')
def sales():
    dt = datetime.datetime.now()
    if request.args.get('fm') is None:
        fm = dt + datetime.timedelta(weeks=-4)
    else:
        fm = datetime.datetime.fromisoformat(request.args.get('fm'))
    if request.args.get('to') is None:
        to = dt
    else:
        to = datetime.datetime.fromisoformat(request.args.get('to'))
    if request.args.get('unit') is None:
        unit = 'day'
    else:
        unit = request.args.get('unit')
    labels = []
    values = []
    if unit == 'day':
        pipe = [
            {
                '$match': { 'paid_at': { '$gte': fm, '$lte': to }}
            },
            {
                '$group': {
                    '_id': { 'year': '$year', 'month': '$month', 'day': '$day' },
                    'total': { '$sum': '$order_amount' }
                }
            },
            {
                '$sort': { '_id.year': 1, '_id.month': 1, '_id.day': 1 }
            }
        ]
        sales = collection_payments.aggregate(pipeline=pipe)
        for sale in sales:
            label = str(sale['_id']['month']) + '-' + str(sale['_id']['day'])
            labels.append(label)
            values.append(sale['total'])
        return dumps({'labels': labels, 'values': values})
    elif unit == 'month':
        pipe = [
            {
                '$match': { 'paid_at': { '$gte': fm, '$lte': to }}
            },
            {
                '$group': {
                    '_id': { 'year': '$year', 'month': '$month' },
                    'total': { '$sum': '$order_amount' }
                }
            },
            {
                '$sort': { '_id.year': 1, '_id.month': 1, }
            }
        ]
        sales = collection_payments.aggregate(pipeline=pipe)
        for sale in sales:
            label = str(sale['_id']['year']) + '-' + str(sale['_id']['month'])
            labels.append(label)
            values.append(sale['total'])
        return dumps({'labels': labels, 'values': values})
    else:
        return {'message': 'invalid unit'}, 400



if __name__ == '__main__':
    app.run()
