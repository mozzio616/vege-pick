from flask import Flask, jsonify, Response
from flask_cors import CORS
from flask_qrcode import QRcode
from auth import AuthError

app = Flask(__name__)
CORS(app)
QRcode(app)

@app.errorhandler(AuthError)
def handle_auth_error(ex: AuthError) -> Response:
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

from views.base import page_base   
app.register_blueprint(page_base)

from views.items import page_items
app.register_blueprint(page_items)

from views.code import page_code
app.register_blueprint(page_code)

from api.locations import api_locations
app.register_blueprint(api_locations)

from api.racks import api_racks
app.register_blueprint(api_racks)

from api.lockers import api_lockers
app.register_blueprint(api_lockers)

from api.items import api_items
app.register_blueprint(api_items)

from api.payments import api_payments
app.register_blueprint(api_payments)

from api.sales import api_sales
app.register_blueprint(api_sales)

from api.private_hello import api_hello
app.register_blueprint(api_hello)

if __name__ == '__main__':
    app.run()
