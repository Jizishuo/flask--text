from werkzeug.routing import BaseConverter
import functools
from flask import session, jsonify, g
from home.utils.response_code import RET


#定义一个正则表达器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        #调用父类的方法
        super(ReConverter, self).__init__(url_map)

        #保存正则表达
        self.regex = regex


#登陆装饰器
def login_required(view_func):
    @functools.wraps(view_func) #内层函数属性变得跟被装饰的函数一样
    def wrapper(*args, **kwargs):
        #判断用户登录状态
        user_id = session.get('user_id')

        if not user_id:
            #登陆
            g.user_id = user_id #把use-id传给函数 拿use_id = g.user_id
            return view_func(*args, **kwargs)
        else:
            #未登录
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    return wrapper

