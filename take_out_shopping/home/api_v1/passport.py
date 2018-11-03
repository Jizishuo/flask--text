"""
用户注册,登录,登陆状态， 退出
"""
from flask import request, jsonify, current_app, session
import re
from sqlalchemy.exc import IntegrityError #数据库异常(重复键)
from werkzeug.security import generate_password_hash, check_password_hash

from . import api
from home.utils.response_code import RET
from home import redis_store, db
from home.models import User
from home import constants

@api.route("/users", methods=['POST'])
def register():
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r'1[34578]\d{9}]', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不对')

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='2个密码不对')


    try:
        real_sms_code = redis_store.get('send_sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='读取验证码验证码异常')

    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码失效')

    #删除短信验证码 防止多次验证（后边再删 一条短信可以多次验证）
    try:
        redis_store.delete('send_sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)

    if real_sms_code != sms_code:
        return jsonify(errno=RET.DBERR, errmsg='短信验证码错误')
    ''' 2次查询(不用)
    try:
        user = User.query.filter_by(phone_num=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经存在')
    
    user = User()
    db.session.add(user)
    db.session.commit()
    '''

    user = User(phone_num=mobile, name=mobile)
    user.password_hash = password #方法变属性
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()#回滚操作
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已经存在')
    except Exception as e:
        db.session.rollback()  # 回滚操作
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='数据库存异常')

    #保存登录状态

    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg='注册成功')


#登录
@api.route('/sessions', methods=['POST'])
def login():
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r'1[34578]\d{9}]', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不对')

    #判断错误次数是否超过限制
    user_ip = request.remote_addr #获取用户ip
    try:
        access_nums = redis_store.get('access_num_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES: #5次
            return jsonify(errno=RET.REQERR, errmsg='错误次数超过限制')


    try:
        user = User.query.filter_by(phone_num=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户失败')

    # 用户和密码一起校验（防止暴力刷取手机号码信息）
    if user is None or user.check_password(password):
        try:
            #记录错误次数 incr 有加一 没有创建
            redis_store.incr('access_num_%s' % user_ip)
            redis_store.expire('access_num_%s' % user_ip, constants.LOGIN_ERROR_TIME) #60秒
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg='用户不存在或密码失败')

    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg='登陆成功')


#检查登陆状态
@api.route('/session', methods=['GET'])
def check_session():
    name = session.get('name')
    if name is not None:
        return jsonify(errno=RET.OK, errmsg=True, data={'name':name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg='false')

#退出
@api.route('/session', methods=['DELETE'])
def logout():
    csrf_token = session.get('csrf_token')
    session.clear()
    session['csrf_token'] = csrf_token

    # 重点
    # 退出的时候 cookies, bobdy, session 都需要有csrf_token 不能全部删除了session读取是从redis
    # 浏览器重新加载 需要保留csrf_token
    #if field_name not in g:
        #if field_name not in session:
            #session[field_name] = hashlib.sha1(os.urandom(64)).hexdigest()

    #源码 这个的 问题

    return jsonify(errno=RET.OK, errmsg='ok')

