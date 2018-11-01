from . import api
from flask import g, request, jsonify, current_app, session
from home.utils.response_code import RET
from home.utils.commons import login_required #登陆装饰器
from home.utils.image_storage import storage  #上传图片
from home.models import User
from home import redis_store, db


#设置用户头像
@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    #图片(多媒体表单), user_id(g对象)
    user_id = g.user_id
    
    image_file = request.files.get('avatar')
    
    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg='未上传图片')
    
    image_data = image_file.read()
    
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='上传图片失败')

    #保存
    try:
        User.query.filter_by(id=user_id).update({'avatar_url':file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库图片保存失败')

    avatar_url = '域名' + file_name
    return jsonify(errno=RET.OK, errmsg='保存成功', data={'avatar_url':avatar_url})

#修改用户姓名
@api.route('/users/name', methods=['PUT'])
@login_required
def chang_user_name():
    user_id = g.user_id

    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    name = req_data.get('name')
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg='名字不能为空')

    try:
        User.query.filter_by(id=user_id).update({'name':name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='设置名字错误')

    #修改session
    session['name'] = name
    return jsonify(errno=RET.OK, errmsg='OK', data={'name':name})