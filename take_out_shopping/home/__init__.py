from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import redis
import logging
from logging.handlers import RotatingFileHandler

from config import config_map
from home.utils.commons import ReConverter #自定义正则表达器


#创建数据库
db = SQLAlchemy()

redis_store = None

#配置日志信息
logging.basicConfig(level=logging.INFO) #开发模式的话这个设置的没用，DRBUG设置了true
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10) #路径，文件大小，最大文件个数
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s') #格式
file_log_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_log_handler) #全局日志对象

#工厂模式
def create_app(config_name):
    """
    根据参数来创建app是开发模式还是生产环境
    ('develop', 'product')
    """
    app = Flask(__name__)

    #载入配置
    config_class = config_map.get(config_name)

    # 载入配置
    app.config.from_object(config_class)

    #app初始化db
    db.init_app(app)

    # 初始化连接redis
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT, password='redis')

    # session --redis
    Session(app)

    # csrf防护
    CSRFProtect(app)

    #自定义正则转换器
    app.url_map.converters['re'] = ReConverter

    from home import api_v1  # 导入蓝图 放这里 用到再导入
    #注册蓝图
    app.register_blueprint(api_v1.api, url_prefix="/api/v1")

    #提供静态文件的蓝图
    from home.web_html import html
    app.register_blueprint(html)

    return app