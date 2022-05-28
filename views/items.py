from flask import render_template, request, redirect, Blueprint
import requests

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
            res = requests.get(request.root_url + 'api/locations/' + locationId + '/lockers')
            items = res.json()
            return render_template('items.html', location=location, items=items)
