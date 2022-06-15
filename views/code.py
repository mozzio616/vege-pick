from flask import render_template, request, redirect, Blueprint
import requests
from db import db
from auth0 import get_token

col_token = db.token

page_code = Blueprint('page_code', __name__)
@page_code.route('/code')
def create_code():
    locationId = request.args.get('locationId')
    lockerId = request.args.get('lockerId')
    if locationId is None or lockerId is None:
        return redirect('/search')
    else:

        res = col_token.find_one({'_id': 'token'})
        token = res['token']
        headers = {'Authorization': 'Bearer ' + token}
        create_code_api = request.root_url + 'api/v1/payments/locations/' + locationId + '/lockers/' + lockerId + '/code'
        res = requests.get(create_code_api, headers = headers)
        if res.status_code == 401:
            token = get_token()
            headers = {'Authorization': 'Bearer ' + token}
            res = requests.get(create_code_api, headers = headers)
        if res.status_code == 200:
            data = res.json()
            return render_template('code.html', data=data)
        elif res.status_code == 404:
            return redirect('/sold?locationId=' + locationId)
        else:
            return redirect('/items?locationId=' + locationId)