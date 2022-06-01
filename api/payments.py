from flask import Blueprint, request
from bson.json_util import dumps
from slack_sdk.webhook import WebhookClient
from dotenv import load_dotenv
import paypayopa
import os, datetime

from db import db
collection_payments = db.payments
collection_locations = db.locations
collection_lockers = db.lockers
collection_items = db.items

load_dotenv()
PP_API_KEY = os.getenv('PP_API_KEY')
PP_API_SECRET = os.getenv('PP_API_SECRET')
PP_MERCHANT_ID = os.getenv('PP_MERCHANT_ID')
PP_REDIRECT_URL = os.getenv('PP_REDIRECT_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

client = paypayopa.Client(auth=(PP_API_KEY, PP_API_SECRET), production_mode=False)
client.set_assume_merchant(PP_MERCHANT_ID)

api_payments = Blueprint('api_payments', __name__)

def create_merchant_payment_id(itemId):
    dt = datetime.datetime.now()
    merchantPaymentId = itemId + dt.strftime('%Y%m%d%H%M%S')
    return merchantPaymentId

@api_payments.route('/api/payments/locations/<locationId>/lockers/<lockerId>/code')
def create_qr_code(locationId, lockerId):
    locker = collection_lockers.find_one({'locationId': locationId, 'lockerId': lockerId})
    if locker is None:
        return {'code': 'locker_not_found', 'description': 'The locker is not found in the location'}, 400
    else:
        lockerNo = locker['lockerNo']
        itemId = locker['itemId']
        isAvailable = locker['isAvailable']
        if isAvailable is True:
            location = collection_locations.find_one({'locationId': locationId})
            if location is None:
                return {'code': 'location_not_found', 'description': 'The location is not found'}, 400
            else:
                locationNameJp = location['locationNameJp']
                item = collection_items.find_one({'itemId': itemId})
                itemName = item['itemName']
                itemPrice = item['itemPrice']
                itemImg = item['itemImg']
                merchantPaymentId = create_merchant_payment_id(lockerId)
                req = {
                    'merchantPaymentId': merchantPaymentId,
                    'codeType': 'ORDER_QR',
                    'redirectUrl': PP_REDIRECT_URL,
                    'redirectType': 'WEB_LINK',
                    'orderDescription': itemName,
                    'orderItems': [{
                        'name': itemName,
                        'category': 'vegetables',
                        'quantity': 1,
                        'productId': lockerId,
                        'unitPrice': {
                                'amount': itemPrice,
                                'currency': 'JPY'
                        }
                    }],
                    'amount': {
                        'amount': itemPrice,
                        'currency': 'JPY'
                    },
                }
                res_payment = client.Code.create_qr_code(req)
                resultCode = res_payment['resultInfo']['code']
                if resultCode == 'SUCCESS':
                    res_db = collection_lockers.update_one({'lockerId': lockerId}, {'$set': {'isAvailable': False}})
                    message = merchantPaymentId + ':' + lockerId
                    webhook = WebhookClient(WEBHOOK_URL)
                    res_webhook = webhook.send(text=message)
                    url = res_payment['data']['url']
                    return {'url': url, 'locationNameJp': locationNameJp, 'lockerNo': lockerNo, 'itemName': itemName, 'itemPrice': itemPrice, 'itemImg': itemImg}
                else:
                    return {'code': resultCode, 'description': 'Failed to create QR code'}, 500
        else:
            return {'code': 'out_of_stock', 'description': 'This item is sold out'}, 404

@api_payments.route('/api/payments/<merchantPaymentId>/status')
def payment_status(merchantPaymentId):
    payment_detail = client.Code.get_payment_details(merchantPaymentId)
    status = payment_detail['data']['status']
    res = {'merchantPaymentId': merchantPaymentId, 'status': status}
    return res

@api_payments.route('/api/payments/logs', methods=['GET', 'POST'])
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
                log['paid_at'] = datetime.datetime.fromisoformat(
                    log['paid_at'])
                log['order_amount'] = int(log['order_amount'])
                log['year'] = int(log['year'])
                log['month'] = int(log['month'])
                log['day'] = int(log['day'])
                res = collection_payments.insert_one(log)
                message.append(res.inserted_id)
            return dumps(message)
        else:
            dt = datetime.datetime.fromisoformat(request.json['paid_at'])
            request.json['paid_at'] = dt
            request.json['order_amount'] = int(request.json['order_amount'])
            request.json['year'] = dt.year
            request.json['month'] = dt.month
            request.json['day'] = dt.day
            res = collection_payments.insert_one(request.json)
            #message = request.json['merchant_order_id'] + ':' + request.json['state']
            #webhook = WebhookClient(WEBHOOK_URL)
            #res_webhook = webhook.send(text=message)
            return dumps(res.inserted_id)
    else:
        return {}
