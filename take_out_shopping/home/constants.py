"""
常量参数数据
"""

#图片验证码redis有效期
IMAGE_CODE_REDIS_EXPIRE = 180

#短信验证码有效期 5分钟
SMS_CODE_REDIS_EXPIRE = 300

#发送短信时间间隔
SEND_SMS_CODE_EXPIRE = 60

#登陆错误尝试次数
LOGIN_ERROR_MAX_TIMES = 5

#登陆错误限制时间
LOGIN_ERROR_TIME = 60

#地区缓存时间 2hours
AREA_INFO_REDIS_CACHAE_TIME = 7200

#房屋列表页 每页条
HOUSES_LIST_NUM = 20