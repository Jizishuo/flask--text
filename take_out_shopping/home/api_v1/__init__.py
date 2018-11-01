

from flask import Blueprint

#创建蓝图

api = Blueprint("api_v1", __name__)

#导入蓝图的视图
from . import text, verify_code, passport, profile, houses