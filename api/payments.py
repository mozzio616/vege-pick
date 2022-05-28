from flask import Blueprint, request
from bson.json_util import dumps
from api.db import db
import os, datetime
import paypayopa

api_payments = Blueprint('api_payments', __name__)

API_KEY = os.environ['PP_API_KEY']
API_SECRET = os.environ['PP_API_SECRET']
MERCHANT_ID = os.environ['PP_MERCHANT_ID']
REDIRECT_URL = os.environ['PP_REDIRECT_URL']

collection_payments = db.payments

client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
client.set_assume_merchant(MERCHANT_ID)

@api_payments.route('/api/payments/<merchantPaymentId>/status')
def payment_status(merchantPaymentId):
    payment_detail = client.Code.get_payment_details(merchantPaymentId)
    status = payment_detail['data']['status']
    response = {'merchantPaymentId': merchantPaymentId, 'status': status}
    return response

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