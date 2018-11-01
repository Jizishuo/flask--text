from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

html = Blueprint('web_html', __name__)

#提供静态文件的蓝图(自定义了正则匹配)
@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    #为空 访问主页
    if not html_file_name:
        html_file_name = 'index.html'

    #不是才拼接
    if html_file_name != 'favicon.ico':
        #提供html文件 current_app=app
        html_file_name = 'html/' + html_file_name

    #创建一个csrf_token值
    csrf_token = csrf.generate_csrf()
    resp = make_response(current_app.send_static_file(html_file_name))

    #设置cookies  csrf_token不能设置有效期（关掉浏览器就没了）
    resp.set_cookie('csrf_token', csrf_token)

    return resp