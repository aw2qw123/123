from datetime import datetime, timedelta

from django_redis import get_redis_connection
from flask import request, flash, render_template, jsonify, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from redis import Redis
from models import User
from util import parser, id_worker

from util.database import db_session
from util.jwt_util import generate_jwt
from celery_tasks.sms.tasks import send_message


class Register(Resource):
    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        mobile = request.form.get('mobile')
        if not all([username, password, mobile]):
            return jsonify({'code': 0, 'msg': '参数不正确'})
        user = User(username=username, password=password, mobile=mobile)
        if not user:
            return jsonify({'code': 0, 'msg': '该用户未注册'})
        db_session.add(user)
        db_session.commit()
        return jsonify({'code': 1, 'msg': '注册成功'})


class Login(Resource):

    def _generate_token(self, user_id, refresh=True):
        payload = {
            'user_id': user_id,
            'refresh': refresh
        }
        expiry = datetime.utcnow() + \
                 timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])

        token = generate_jwt(payload, expiry)
        if refresh:
            expiry = datetime.utcnow() + \
                     timedelta(hours=current_app.config['JWT_REFRESH_DAYS'])
            refresh_token = generate_jwt(payload, expiry)
        else:
            refresh_token = None
        return token, refresh_token

    def post(self):
        # login_type = request.form.get('login_type')
        # if login_type == '1':
        #     username = request.form.get('username')
        #     password = request.form.get('password')
        #     if not all([username, password]):
        #         return jsonify({'code': 0, 'msg': '参数不正确'})
        #     user = User.query.filter(User.username == username, User.password == password).first()
        #     if not user:
        #         return jsonify({'code': 0, 'msg': '没有该用户'})
        #
        #     return jsonify({'code': 1, 'msg': '登陆成功'})

        json_parser = RequestParser()
        json_parser.add_argument('mobile', required=True, location='json',
                                 type=parser.mobile)
        json_parser.add_argument('code', required=True, location='json',
                                 type=parser.code)
        args = json_parser.parse_args()
        mobile = args.get('mobile')
        code = args.get('code')
        mobile_code = f'mobile_code{mobile}'
        flag_code = f'flag_code{mobile}'
        redis_conn = Redis(host='127.0.0.1', port=6379, db=0)
        if not redis_conn.get(mobile_code):
            return {'message': 'code is invalid'}, 400
        new_code = redis_conn.get(mobile_code).decode('utf8')
        if new_code != code if new_code else 0:
            return {'message': 'code is invalid'}, 400
        user = User.query.filter_by(mobile=mobile).first()
        if not user:
            user_id = id_worker.get_id()
            user = User(id=user_id, mobile=mobile)
            db_session.add(user)
            db_session.commit()
        else:
            if user.status == 0:
                return {'message': 'Invalid User'}, 400
        token, refresh_token = self._generate_token(user.id)
        return {'message': 'ok', 'token': token, 'refresh_token': refresh_token}, 201
    # else:
    # return jsonify({'code': 0, 'msg': '登录方式错误'})


# class LoginView(Resource):
#     def post(self):
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')
#         if username == 'chenhao' and password == '123456':
#             payload = {
#                 'user_id': 1,
#                 'username': 'chenhao'
#             }
#
#             expiry = datetime.utcnow() + \
#                      timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])
#             token = generate_jwt(payload, expiry,
#                                  secret=current_app.config['JWT_SECRET'])
#             return jsonify({'code': 1, 'msg': '登陆成功', 'token': token})
#         return jsonify({'code': 0, 'msg': '登录失败'})


class SMS_Code(Resource):

    def get(self, mobile):
        exp_time = 5 * 60
        try:
            parser.mobile(mobile_str=mobile)
        except ValueError:
            return {'message': 'mobile is invalid'}, 404

        mobile_code = f'mobile_code{mobile}'
        flag_code = f'flag_code{mobile}'
        redis_conn = Redis(host='127.0.0.1', port=6379, db=0)
        flag = redis_conn.get(flag_code)
        if flag:
            # return jsonify({'code': '0', 'msg': '验证码还在有效期'})
            return {'message': 'cannot be sent frequently'}, 429
        code = SMS_Code.make_code()
        pl = redis_conn.pipeline()
        pl.setex(name=mobile_code, value=code, time=exp_time)
        pl.setex(name=flag_code, value=1, time=exp_time)
        pl.execute()
        ret = send_message.delay(mobile=mobile, code=code, exp_time=exp_time)
        if ret:
            #     return jsonify({'code': 1, 'msg': '验证码发送成功'})
            # return jsonify({'code': 0, 'msg': '验证码发送失败'})
            return {'message': 'ok', 'mobile': mobile}, 200
        return {'message': 'not ok', 'mobile': mobile}, 429

    @staticmethod
    def make_code():
        import string, random
        return ''.join(random.choices(string.digits, k=6))
