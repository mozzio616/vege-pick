from flask import Flask, render_template, request, redirect
from flask_cors import CORS
from flask_qrcode import QRcode
from slack_sdk.webhook import WebhookClient
import paypayopa
import requests
import os, datetime
from api.locations import locations
from api.lockers import lockers
from api.items import items
from api.payments import payments
from api.sales import sales

API_KEY = os.environ['PP_API_KEY']
API_SECRET = os.environ['PP_API_SECRET']
MERCHANT_ID = os.environ['PP_MERCHANT_ID']
REDIRECT_URL = os.environ['PP_REDIRECT_URL']
WEBHOOK_URL = os.environ['WEBHOOK_URL']

app = Flask(__name__)
app.register_blueprint(locations)
app.register_blueprint(lockers)
app.register_blueprint(items)
app.register_blueprint(payments)
app.register_blueprint(sales)
CORS(app)
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
        res = requests.get(request.root_url + 'api/locations/' + locationId)
        location = res.json()
        res = requests.get(request.root_url + 'api/locations/' + locationId + '/lockers')
        items = res.json()
        if location is None or items is None:
            return redirect('/search')
        else:
            return render_template('items.html', location=location, items=items)

@app.route('/code')
def create_code():
    locationId = request.args.get('locationId')
    lockerId = request.args.get('lockerId')
    if locationId is None or lockerId is None:
        return redirect('/search')
    else:
        res = requests.get(request.root_url + 'api/locations/' + locationId)
        if res.status_code != 200:
            return redirect('/search')
        else:
            location = res.json()
            res = requests.get(request.root_url + 'api/lockers/' + lockerId)
            if res.status_code != 200:
                return redirect('/items?locationId=' + locationId)
            else:
                locker = res.json()
                if locker['isAvailable'] is True:
                    merchantPaymentId = create_merchant_payment_id(lockerId)
                    req = {
                        "merchantPaymentId": merchantPaymentId,
                        "codeType": "ORDER_QR",
                        "redirectUrl": REDIRECT_URL,
                        "redirectType":"WEB_LINK",
                        "orderDescription": locker['itemName'],
                        "orderItems": [{
                            "name": locker['itemName'],
                            "category": "vegetables",
                            "quantity": 1,
                            "productId": lockerId,
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
                        res_api = requests.put(request.root_url + 'api/lockers/' + lockerId + '/status', json={'isAvailable': False})
                        message = merchantPaymentId + ':' + lockerId
                        webhook = WebhookClient(WEBHOOK_URL)
                        res_webhook = webhook.send(text=message)
                        url = response['data']['url']
                        return render_template('code.html', url=url, location=location, item=locker)
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


if __name__ == '__main__':
    app.run()
