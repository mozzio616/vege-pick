from flask import Flask, render_template, request, redirect
from flask_qrcode import QRcode
import paypayopa
import pymongo
from slack_sdk.webhook import WebhookClient
import os, datetime

API_KEY = os.environ['PP_API_KEY']
API_SECRET = os.environ['PP_API_SECRET']
MERCHANT_ID = os.environ['PP_MERCHANT_ID']
REDIRECT_URL = os.environ['PP_REDIRECT_URL']
DB_HOST = os.environ['MONGO_HOST']
WEBHOOK_URL = os.environ['WEBHOOK_URL']

connection_url = DB_HOST

app = Flask(__name__)

mongoClient = pymongo.MongoClient(connection_url)
db = mongoClient.lvl
collection_locations = db.locations
collection_items = db.items

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
        return locations
    elif request.method == 'POST':
        for i, location in enumerate(request.json):
            collection_locations.insert_one(location)
        response = {'message': str(len(request.json)) + ' locations created.'}
        return response
    else:
        return '{}'

@app.route('/api/items', methods=['GET', 'POST'])
def api_items():
    if request.method == 'GET':
        items = collection_items.find()
        return items
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

            
if __name__ == '__main__':
    app.run()
