from multiprocessing import connection
from flask import Flask, render_template, request, redirect
import paypayopa
from flask_qrcode import QRcode
import os, datetime
import pymongo

API_KEY = os.environ['PP_API_KEY']
API_SECRET = os.environ['PP_API_SECRET']
MERCHANT_ID = os.environ['PP_MERCHANT_ID']
REDIRECT_URL = os.environ['PP_REDIRECT_URL']
DB_USER = os.environ['MONGO_USER']
DB_PASS = os.environ['MONGO_PASS']

connection_url = 'mongodb+srv://' + DB_USER + ':' + DB_PASS + '@cluster0.gdlpa.gcp.mongodb.net/?retryWrites=true&w=majority'

app = Flask(__name__)
QRcode(app)
mongoClient = pymongo.MongoClient(connection_url)
db = mongoClient.lvl

client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
client.set_assume_merchant(MERCHANT_ID)

def create_merchant_payment_id():
    dt = datetime.datetime.now()
    return dt.strftime('%Y%m%d%H%M%S')

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
def items():
    locationId = request.args.get('locationId')
    if locationId is None:
        return redirect('/search')
    else:
        locationData = db.locations.find_one({'locationId': locationId})
        itemData = db.items.find({'locationId': locationId})
        if locationData is None or itemData is None:
            return redirect('/search')
        else:
            return render_template('items.html', locationData=locationData, itemData=itemData)

@app.route('/code', methods=['GET'])
def create_code():
    locationId = request.args.get('locationId')
    itemId = request.args.get('itemId')
    if locationId is None or itemId is None:
        return redirect('/search')
    else:
        locationData = db.locations.find_one({'locationId': locationId})
        itemData = db.items.find_one({'locationId': locationId, 'itemId': itemId})
        if locationData is None:
            return redirect('/search')
        elif itemData is None:
            return redirect('/items?locationId=' + locationId)
        elif itemData['isAvailable'] is True:
            merchantPaymentId = create_merchant_payment_id()
            req = {
                "merchantPaymentId": merchantPaymentId,
                "codeType": "ORDER_QR",
                "redirectUrl": REDIRECT_URL,
                "redirectType":"WEB_LINK",
                "orderDescription": itemData['itemName'],
                "orderItems": [{
                    "name": itemData['itemName'],
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
            res = client.Code.create_qr_code(req)
            print(res['resultInfo']['code'])
            print(res['data']['url'])
            paypay_url = res['data']['url']
            return render_template('code.html', paypay_url=paypay_url, locationData=locationData, itemData=itemData)
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
def addLocations():
    collection = db.locations
    if request.method == 'POST':
        for index, location in enumerate(request.json):
            collection.insert_one(location)
        response = {'message': str(len(request.json)) + ' locations created.'}
        return response
    else:
        return '{}'

@app.route('/api/items', methods=['GET', 'POST'])
def addItems():
    collection = db.items
    if request.method == 'POST':
        for index, item in enumerate(request.json):
            collection.insert_one(item)
        response = {'message': str(len(request.json)) + ' items created.'}
        return response
    else:
        return '{}'


if __name__ == '__main__':
    app.run()
