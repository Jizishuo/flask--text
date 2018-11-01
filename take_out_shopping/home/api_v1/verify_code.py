"""
生成验证码
"""
import random
from flask import current_app, jsonify, make_response, request

from . import api
from home.utils.captcha.captcha import captcha #验证码生成
from home.utils.response_code import RET #返回码
from home import redis_store
from home import constants
from home.libs.yuntongxun.SendTemplateSMS import CCP
from home.models import User
from home.tasks import tasks_send_sms #celery发送短信


#图片验证码
@api.route('/image_code/<image_code_id>')
def get_image_code(image_code_id):
    #获取图片验证码,返回验证码图片 image_code_id图片验证码编号
    name, text, image_data = captcha.generate_captcha() #名字，真实文本，图片数据

    #单挑维护记录 'imagecaodeid':'真实值'
    #redis_store.set('image_code_%s' % image_code_id, text)
    #redis_store.expire('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRE) #180秒
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRE, text)
    except Exception as e:
        current_app.logger.error(e)#记录异常
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')

    #返回图片
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp

'''
#短信验证码
#/api/v1/sms_codes/123123123?image_code=xxx&image_coade_id=xxxx
@api.route('/sms_codes/<re(1[34578]\d{9}):mobile>')
def get_sms_code(mobile):
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')


    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis异常')

    if real_image_code == None:
        return jsonify(errno=RET.NODATA, errmsg='验证码过期')

    #删除图片验证码 写前一点 防止同一个验证码验证多次（撞库）
    try:
        redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    #都装小写对比
    if real_image_code.lower() != image_code.lower():
        return jsonify(error=RET.DATAERR, errmsg='验证码错误')

    #检查手机60s有木有发送过
    try:
        send_flag = redis_store.get('send_sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            #60s有过记录
            return jsonify(errno=RET.REQERR, errmsg='发送短信过于频繁60s后重试')

    #手机号是否重复
    try:
        user = User.query.filter_by(phone_num=mobile).first() #怕数据库突然崩了
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经存在')

    #生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999) #06d 最少6位 少的前边加0

    try:
        redis_store.setex('sms_code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRE, sms_code) #5分钟
        #保存发送给手机号的记录防止60s重复发送
        redis_store.setex('send_sms_code_%s' % mobile, constants.SEND_SMS_CODE_EXPIRE, 1) #发送间隔60秒 1随便写
    except Exception as e:
        current_app.logger.error(e)#记录异常
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')

    #发送短信
    try:
        ccp = CCP()
        result = ccp.sendTemplateSMS(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRE)/60], 1)
    except Exception as e:
        current_app.logger.error(e)  # 记录异常
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')


    if result == True:
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR,errmsg='发送短信失败')
'''


#短信验证码
#/api/v1/sms_codes/123123123?image_code=xxx&image_coade_id=xxxx
@api.route('/sms_codes/<re(1[34578]\d{9}):mobile>')
def get_sms_code(mobile):
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')


    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis异常')

    if real_image_code == None:
        return jsonify(errno=RET.NODATA, errmsg='验证码过期')

    #删除图片验证码 写前一点 防止同一个验证码验证多次（撞库）
    try:
        redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    #都装小写对比
    if real_image_code.lower() != image_code.lower():
        return jsonify(error=RET.DATAERR, errmsg='验证码错误')

    #检查手机60s有木有发送过
    try:
        send_flag = redis_store.get('send_sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            #60s有过记录
            return jsonify(errno=RET.REQERR, errmsg='发送短信过于频繁60s后重试')

    #手机号是否重复
    try:
        user = User.query.filter_by(phone_num=mobile).first() #怕数据库突然崩了
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经存在')

    #生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999) #06d 最少6位 少的前边加0

    try:
        redis_store.setex('sms_code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRE, sms_code) #5分钟
        #保存发送给手机号的记录防止60s重复发送
        redis_store.setex('send_sms_code_%s' % mobile, constants.SEND_SMS_CODE_EXPIRE, 1) #发送间隔60秒 1随便写
    except Exception as e:
        current_app.logger.error(e)#记录异常
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')

    #发送短信
    tasks_send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRE)/60], 1)
    return jsonify(errno=RET.OK, errmsg='发送成功')




