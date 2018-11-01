"""
订单模块
"""

from . import api
import json
from flask import g, request, jsonify, current_app
#from handlers.BaseHandler import BaseHandler
from home.utils.response_code import RET
from home.utils.commons import login_required #登陆装饰器
from home.utils.image_storage import storage  #上传图片
from home.models import User, Area, Facility, Order,House
from home import redis_store, db
from home import constants
from datetime import datetime
from home import redis_store


#保存订单
