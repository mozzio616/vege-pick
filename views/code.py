from flask import render_template, request, redirect, Blueprint
from slack_sdk.webhook import WebhookClient
import requests
import paypayopa
import os, datetime

API_KEY = os.environ['PP_API_KEY']
API_SECRET = os.environ['PP_API_SECRET']
MERCHANT_ID = os.environ['PP_MERCHANT_ID']
REDIRECT_URL = os.environ['PP_REDIRECT_URL']
WEBHOOK_URL = os.environ['WEBHOOK_URL']

client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
client.set_assume_merchant(MERCHANT_ID)

def create_merchant_payment_id(itemId):
    dt = datetime.datetime.now()
    merchantPaymentId = itemId + dt.strftime('%Y%m%d%H%M%S')
    return merchantPaymentId

page_code = Blueprint('page_code', __name__)

@page_code.route('/code')
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
                    res_payment = client.Code.create_qr_code(req)
                    resultCode = res_payment['resultInfo']['code']
                    if resultCode == 'SUCCESS':
                        res = requests.put(request.root_url + 'api/lockers/' + lockerId + '/status', json={'isAvailable': False})
                        message = merchantPaymentId + ':' + lockerId
                        webhook = WebhookClient(WEBHOOK_URL)
                        res_webhook = webhook.send(text=message)
                        url = res_payment['data']['url']
                        return render_template('code.html', url=url, location=location, item=locker)
                    else:
                        return redirect('/items?locationId=' + locationId)
                else:
                    return redirect('/sold?locationId=' + locationId)