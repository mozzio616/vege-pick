from flask import Flask
from flask_cors import CORS
from flask_qrcode import QRcode

app = Flask(__name__)
CORS(app)
QRcode(app)

from views.base import page_base   
app.register_blueprint(page_base)

from views.items import page_items
app.register_blueprint(page_items)

from views.code import page_code
app.register_blueprint(page_code)

from api.locations import api_locations
app.register_blueprint(api_locations)

from api.lockers import api_lockers
app.register_blueprint(api_lockers)

from api.items import api_items
app.register_blueprint(api_items)

from api.payments import api_payments
app.register_blueprint(api_payments)

from api.sales import api_sales
app.register_blueprint(api_sales)

if __name__ == '__main__':
    app.run()
