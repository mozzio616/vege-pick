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

from api.private import api_private
app.register_blueprint(api_private)

#from api.v1.public.locations.racks import v1_racks
#app.register_blueprint(v1_racks)

#from api.v1.public.locations.rack import v1_rack
#app.register_blueprint(v1_rack)

#from api.v1.public.locations.lockers import v1_lockers
#app.register_blueprint(v1_lockers)

from api.v1.public.payments.payments import v1_payments
app.register_blueprint(v1_payments)

# for new admin ui
from api.v1.users import v1_users
app.register_blueprint(v1_users)

from api.v1.user import v1_user
app.register_blueprint(v1_user)

from api.v1.racks import v1_racks
app.register_blueprint(v1_racks)

from api.v1.locations import v1_locations
app.register_blueprint(v1_locations)

from api.v1.location import v1_location
app.register_blueprint(v1_location)

from api.v1.location_ams import v1_location_ams
app.register_blueprint(v1_location_ams)

from api.v1.location_am import v1_location_am
app.register_blueprint(v1_location_am)

from api.v1.location_racks import v1_location_racks
app.register_blueprint(v1_location_racks)

from api.v1.location_rack import v1_location_rack
app.register_blueprint(v1_location_rack)

from api.v1.location_lockers import v1_location_lockers
app.register_blueprint(v1_location_lockers)

from api.v1.location_locker import v1_location_locker
app.register_blueprint(v1_location_locker)

from api.v1.items import v1_items
app.register_blueprint(v1_items)

from api.v1.am_locations import v1_am_locations
app.register_blueprint(v1_am_locations)

from api.v1.am_location import v1_am_location
app.register_blueprint(v1_am_location)

from api.v1.am_location_lockers import v1_am_location_lockers
app.register_blueprint(v1_am_location_lockers)

from api.v1.am_location_locker import v1_am_location_locker
app.register_blueprint(v1_am_location_locker)

from api.v1.am_location_locker_stock import v1_am_location_locker_stock
app.register_blueprint(v1_am_location_locker_stock)

if __name__ == '__main__':
    app.run()
