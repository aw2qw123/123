from flask import Blueprint
from flask_restful import Api

from user import api

user_ap = Blueprint('user_api', __name__)
user_apii = Api(user_ap)

user_apii.add_resource(api.Login, '/app/v1_0/authorizations')
user_apii.add_resource(api.Register, '/register/')


user_apii.add_resource(api.SMS_Code, '/app/v1_0/sms/codes/<string:mobile>')
