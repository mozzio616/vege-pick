from flask import request, Blueprint
from auth import requires_auth, requires_scope, AuthError
from flask_cors import cross_origin

api_private = Blueprint('api_private', __name__)

@api_private.route('/api/private')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def private():
    return {'message': 'This API requires authorization'}

@api_private.route('/api/private-scoped', methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def private_scoped():
    if request.method == 'POST':
        if requires_scope("post:private"):
            return {'message': 'This API requires post:private scope'}
        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource"
        }, 403)
    else:
        if requires_scope("read:private"):
            return {'message': 'This API requires read:private scope'}
        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource"
        }, 403)
