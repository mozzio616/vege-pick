from flask import Blueprint
from auth import requires_auth
from flask_cors import cross_origin

api_hello = Blueprint('api_hello', __name__)

@api_hello.route('/api/hello')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def hello():
    return {'message': 'Hello, Private!'}
