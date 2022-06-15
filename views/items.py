from flask import render_template, request, redirect, Blueprint
import requests
from bson.json_util import dumps
from db import db
from auth0 import get_token

collection_token = db.token

page_items = Blueprint('page_items', __name__)

@page_items.route('/items')
def get_items():
    locationId = request.args.get('locationId')
    if locationId is None:
        return redirect('/search')
    else:
        res = requests.get(request.root_url + 'api/v1/locations/' + locationId + '/lockers')
        if res.status_code != 200:
            return redirect('/search')
        else:
            data = res.json()
            location = data['location']
            print(location)
            lockers = data['lockers']
            location = res.json()
            return render_template('items.html', location=location, lockers=lockers)
