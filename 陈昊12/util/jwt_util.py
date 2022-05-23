import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_jwt(payload, expiry, secret=None):
    _payload = {'exp': expiry}
    _payload.update(payload)

    secret = secret if secret else current_app.config['JWT_SECRET']

    token = jwt.encode(payload=_payload, key=secret, algorithm='HS256')
    return token.decode()


def verify_jwt(token, secret=None):
    secret = secret if secret else current_app.config['JWT_SECRET']
    try:
        payload = jwt.decode(token, secret, algorithm='HS256')
    except jwt.PyJWTError:
        payload = None
    return payload


if __name__ == '__main__':
    payload = {
        'user_id': 1,
        'username': 'chenhao'
    }
    expiry = datetime.utcnow() + timedelta(hours=1)
    secret = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'
    # token = generate_jwt(payload, expiry, secret=secret)
    # print(token, type(token))

    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTMwMTk0OTYsInVzZXJfaWQiOjEsInVzZXJuYW1lIjoiY2hlbmhhbyJ9.h7ffEI-f09IvwZDUWj-ePCKsrBbz1kjF3VTkGGJRBnc'

    payload = verify_jwt(token=token, secret=secret)
    print(payload, type(payload))
