from flask import Flask, render_template, request, redirect
import paypayopa
from flask_qrcode import QRcode
import os, datetime

app = Flask(__name__)
QRcode(app)

API_KEY = os.environ['PP_API_KEY']
API_SECRET = os.environ['PP_API_SECRET']
MERCHANT_ID = os.environ['PP_MERCHANT_ID']
REDIRECT_URL = os.environ['PP_REDIRECT_URL']

client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
client.set_assume_merchant(MERCHANT_ID)

def create_merchant_payment_id():
    dt = datetime.datetime.now()
    return dt.strftime('%Y%m%d%H%M%S')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/items')
def items():
    locationId = request.args.get('locationId')
    if locationId is None:
        return redirect('/search')
    else:
        i = 0
        while i < len(data):
            if data[i]['locationId'] == locationId:
                break
            else:
                i += 1
        if i < len(data):
            return render_template('items.html', data=data[i])
        else:
            return redirect('/search')

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/sold')
def sold():
    return render_template('sold.html')

@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/code', methods=['GET'])
def create_code():
    locationId = request.args.get('locationId')
    itemId = request.args.get('itemId')
    if locationId is None or itemId is None:
        return redirect('/sold')
    else:
        i = 0
        while i < len(data):
            if data[i]['locationId'] == locationId:
                break
            else:
                i += 1
        if i < len(data):
            lockerItems = data[i]['lockerItems']
            j = 0
            while j < len(lockerItems):
                if data[i]['lockerItems'][j]['itemId'] == itemId:
                    break
                else:
                    j += 1
            if j < len(lockerItems):
                if lockerItems[j]['isAvailable'] is True:
                    merchantPaymentId = create_merchant_payment_id()
                    req = {
                        "merchantPaymentId": merchantPaymentId,
                        "codeType": "ORDER_QR",
                        "redirectUrl": REDIRECT_URL,
                        "redirectType":"WEB_LINK",
                        "orderDescription": lockerItems[j]['itemName'],
                        "orderItems": [{
                            "name": lockerItems[j]['itemName'],
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
                    return render_template('code.html', paypay_url = paypay_url)
                else:
                    return redirect('/sold')
            else:
                return redirect('/search')
        else:
            return redirect('/search')

data = [
    {
        'locationId': '1001',
        'locationNameEn': 'Komazawa-daigaku Sta.',
        'locationNameJp': '駒沢大学駅',
        'lockerItems': [
            {
                'lockerNo': 1,
                'itemId': '1001001',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': True
            },
            {
                'lockerNo': 2,
                'itemId': '1001002',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': False
            },
            {
                'lockerNo': 3,
                'itemId': '1001003',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': True
            },
            {
                'lockerNo': 4,
                'itemId': '1001004',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': True
            },
            {
                'lockerNo': 5,
                'itemId': '1001005',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': False
            },
            {
                'lockerNo': 6,
                'itemId': '1001006',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': False
            },
            {
                'lockerNo': 7,
                'itemId': '1001007',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': True
            },
            {
                'lockerNo': 8,
                'itemId': '1001008',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': True
            },
            {
                'lockerNo': 9,
                'itemId': '1001009',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': False
            },
            {
                'lockerNo': 10,
                'itemId': '1001010',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': False
            },
            {
                'lockerNo': 11,
                'itemId': '1001011',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': False
            },
            {
                'lockerNo': 12,
                'itemId': '1001012',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': True
            }
        ]
    },
    {
        'locationId': '1002',
        'locationNameEn': 'Shin-machi Nursery School',
        'locationNameJp': '新町保育園',
        'lockerItems': [
            {
                'lockerNo': 1,
                'itemId': '1001001',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': True
            },
            {
                'lockerNo': 2,
                'itemId': '1001002',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': False
            },
            {
                'lockerNo': 3,
                'itemId': '1001003',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': True
            },
            {
                'lockerNo': 4,
                'itemId': '1001004',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': True
            },
            {
                'lockerNo': 5,
                'itemId': '1001005',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': False
            },
            {
                'lockerNo': 6,
                'itemId': '1001006',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': False
            },
            {
                'lockerNo': 7,
                'itemId': '1001007',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': True
            },
            {
                'lockerNo': 8,
                'itemId': '1001008',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': True
            },
            {
                'lockerNo': 9,
                'itemId': '1001009',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': False
            },
            {
                'lockerNo': 10,
                'itemId': '1001010',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': False
            },
            {
                'lockerNo': 11,
                'itemId': '1001011',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': False
            },
            {
                'lockerNo': 12,
                'itemId': '1001012',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': True
            },
        ]
    },
    {
        'locationId': '1003',
        'locationNameEn': 'Fukasawa Elementary School',
        'locationNameJp': '深沢小学校',
        'lockerItems': [
            {
                'lockerNo': 1,
                'itemId': '1001001',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': True
            },
            {
                'lockerNo': 2,
                'itemId': '1001002',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': False
            },
            {
                'lockerNo': 3,
                'itemId': '1001003',
                'itemName': 'せたがやそだち キャベツ 1玉',
                'itemDescription': '世田谷で育った新鮮なキャベツです。',
                'itemPrice': 200,
                'itemImg': 'cabbage.png',
                'isAvailable': True
            },
            {
                'lockerNo': 4,
                'itemId': '1001004',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': True
            },
            {
                'lockerNo': 5,
                'itemId': '1001005',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': False
            },
            {
                'lockerNo': 6,
                'itemId': '1001006',
                'itemName': 'せたがやそだち トマト 大3個',
                'itemDescription': '世田谷で育った新鮮なトマトです。',
                'itemPrice': 300,
                'itemImg': 'tomato.png',
                'isAvailable': False
            },
            {
                'lockerNo': 7,
                'itemId': '1001007',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': True
            },
            {
                'lockerNo': 8,
                'itemId': '1001008',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': True
            },
            {
                'lockerNo': 9,
                'itemId': '1001009',
                'itemName': 'せたがやそだち たまねぎ 中3個',
                'itemDescription': '世田谷で育った新鮮な玉ねぎです。',
                'itemPrice': 300,
                'itemImg': 'onion.png',
                'isAvailable': False
            },
            {
                'lockerNo': 10,
                'itemId': '1001010',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': False
            },
            {
                'lockerNo': 11,
                'itemId': '1001011',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': False
            },
            {
                'lockerNo': 12,
                'itemId': '1001012',
                'itemName': 'せたがやそだち 詰め合わせ',
                'itemDescription': 'カレーにぴったりな、じゃがいも（中3個）、にんじん（1本）、たまねぎ（中3個）のセットです。',
                'itemPrice': 500,
                'itemImg': 'vegset1.png',
                'isAvailable': True
            }
        ]
    }
]


if __name__ == '__main__':
    app.run()
