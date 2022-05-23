from flask import request, g, abort, current_app
from util.jwt_util import verify_jwt


def jwt_authentication():
    if not request.path.startswith('/app/v1_0/sms/codes/') and \
            not request.path.startswith('/app/v1_0/authorizations'):
        token = request.headers.get('Authorization', '')
        if not token:
            abort(403)
        if not token.startswith('Bearer '):
            abs(403)
        token = token.split('Bearer ')[1]
        payload = verify_jwt(token=token, secret=current_app.config['JWT_SECRET'])
        if not payload:
            abort(403)
        g.user_id = payload.get('user_id')
