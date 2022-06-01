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
        res = requests.get(request.root_url + 'api/locations/' + locationId)
        if res.status_code != 200:
            return redirect('/search')
        else:
            location = res.json()
            res = collection_token.find_one({'_id': 'token'})
            token = res['token']
            headers = {'Authorization': 'Bearer ' + token}
            res = requests.get(request.root_url + 'api/locations/' + locationId + '/lockers', headers=headers)
            if res.status_code == 401:
                token = get_token()
                headers = {'Authorization': 'Bearer ' + token}
                res = requests.get(request.root_url + 'api/locations/' + locationId + '/lockers', headers=headers)
            items = res.json()
            return render_template('items.html', location=location, items=items)
