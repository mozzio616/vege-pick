from flask import request, Blueprint
from auth import requires_auth, requires_scope, AuthError
from flask_cors import cross_origin

api_private = Blueprint('api_private', __name__)

@api_private.route('/api/private')
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def private():
    return {'message': 'You are authorized to access this resource'}

@api_private.route('/api/private-scoped', methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])
@requires_auth
def private_scoped():
    if request.method == 'POST':
        if requires_scope("post:private"):
            return {'message': 'You have post:private permission to access this resource'}
        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource"
        }, 403)
    else:
        if requires_scope("read:private"):
            return {'message': 'You have read:private permission to access this resource'}
        raise AuthError({
            "code": "Unauthorized",
            "description": "You don't have access to this resource"
        }, 403)
