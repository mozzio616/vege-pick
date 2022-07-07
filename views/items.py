from flask import render_template, request, redirect, Blueprint
import requests
from bson.json_util import dumps
from db import db
from auth0 import get_token

col_token = db.token

page_items = Blueprint('page_items', __name__)

@page_items.route('/items')
def get_items():
    locationId = request.args.get('locationId')
    if locationId is None:
        return redirect('/search')
    else:

        res = col_token.find_one({'_id': 'token'})
        token = res['token']
        headers = {'Authorization': 'Bearer ' + token}
        api = request.root_url + 'api/v1/locations/' + locationId + '/lockers'
        res = requests.get(api, headers = headers)
        if res.status_code == 401:
            token = get_token()
            headers = {'Authorization': 'Bearer ' + token}
            res = requests.get(api, headers = headers)
        if res.status_code != 200:
            return redirect('/search')
        else:
            data = res.json()
            location = data['location']
            print(location)
            lockers = data['lockers']
            return render_template('items.html', location=location, lockers=lockers)
