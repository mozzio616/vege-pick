from flask import Flask, render_template, request, jsonify
import paypayopa
from flask_qrcode import QRcode
import os, datetime

app = Flask(__name__)
QRcode(app)

API_KEY = os.environ['PP_API_KEY']
API_SECRET = os.environ['PP_API_SECRET']
MERCHANT_ID = os.environ['PP_MERCHANT_ID']

client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
client.set_assume_merchant(MERCHANT_ID)

def create_merchant_payment_id():
    dt = datetime.datetime.now()
    return dt.strftime('%Y%m%d%H%M%S')

@app.route('/')
def index():
    return render_template('menu.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/book')
def book():
    return render_template('menu.html')

@app.route('/code', methods=['GET'])
def create_code():
    merchantPaymentId = create_merchant_payment_id()
    req = {
        "merchantPaymentId": merchantPaymentId,
        "codeType": "ORDER_QR",
        "redirectUrl": "http://vege-pick.vercel.app/thanks",
        "redirectType":"WEB_LINK",
        "orderDescription":"Vege Pick",
        "orderItems": [{
            "name": "Flesh Vegetables",
            "category": "vegetables",
            "quantity": 1,
            "productId": "67678",
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

if __name__ == '__main__':
    app.run()
