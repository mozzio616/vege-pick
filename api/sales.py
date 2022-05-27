from flask import Blueprint, request
from bson.json_util import dumps
from api.db import db
import datetime

sales = Blueprint('sales', __name__)

collection_payments = db.payments

@sales.route('/api/sales')
def api_sales():
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
