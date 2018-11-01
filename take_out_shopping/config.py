"""
项目配置文件
"""
import redis

class Config(object):
    """
    配置信息
    """
    #csf
    SECRET_KEY = 'XASDSA*sasdsad'

    #mysql
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@127.0.0.1:3306/wai_mai"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    #redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    #session-redis
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password='redis')
    SESSION_USE_SIGNER = True  #混淆cookies的session_id隐藏
    PERMANENT_SESSION_LIFETIME = 86400 #session有效期一天


class DevelopmentConfig(Config):
    #开发模式配置
    DEBUG = True  #开发才需要debug

class ProductionConfig(Config):
    #生存环境配置
    pass


config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}