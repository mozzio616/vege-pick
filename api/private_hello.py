from flask import request, Blueprint
from auth import requires_auth, requires_scope, AuthError
from flask_cors import cross_origin

api_hello = Blueprint('api_hello', __name__)

@api_hello.route('/api/hello')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def hello():
    return {'message': 'Hello, Private!'}

@api_hello.route('/api/hello-scoped', methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def hello_scoped():
    if request.method == 'POST':
        if requires_scope("post:hello"):
            return {'message': 'Hello, ' + request.json['name'] + '!'}
        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource"
        }, 403)
    else:
        if requires_scope("read:hello"):
            return {'message': 'Hello, private!'}
        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource"
        }, 403)
