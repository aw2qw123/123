import json

from ronglian_sms_sdk import SmsSDK

from celery_tasks.main import celery_app

accId = '8a216da8802d68fe018044a7c8eb04c5'
accToken = '932a84a4d11848e0b20dd7cc5242de9e'
appId = '8a216da8802d68fe018044a7c9e904cc'


@celery_app.task(name='send_message')
def send_message(mobile, code, exp_time):
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'
    datas = (code, exp_time // 60)
    resp = sdk.sendMessage(tid, mobile, datas)
    status = json.loads(resp).get('statusCode')
    return True if status == 000000 else False
