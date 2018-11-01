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


@api.route('/areas')
def get_area_info():
    #reids 读一下有木有数据
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            #有缓存数据
            return resp_json, 200, {"Content-Type": "application/json"}

    #获取地点信息
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='数据库异常')

    #转字典列表
    area_dict_li = []
    for area in area_li:
        area_dict_li.append(area.to_dict())

    #存进redis
    resp_dict = dict(errno=RET.OK, errmsg='OK', data=area_dict_li) #字典
    resp_json = json.dump(resp_dict)
    try:
        redis_store.setex("area_info", constants.AREA_INFO_REDIS_CACHAE_TIME, resp_json) #缓存2小时
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}

#保存房屋信息
@api.route('/houses/info', methods=['POST'])
@login_required
def save_hose_info():

    """{
            "title":"",
            "price":"",
            "area_id":"1",
            "address":"",
            "room_count":"",
            "acreage":"",
            "unit":"",
            "capacity":"",
            "beds":"",
            "deposit":"",
            "min_days":"",
            "max_days":"",
            "facility":["7","8"]
            }"""
    
    #检查
    #保存
    fa_li= [] #前段创来的列表
    Facility.query.filter(Facility.id.in_(fa_li))
    # #返回



#保存房子图片
@api.route('/houses/image', methods=['POST'])
@login_required
def save_house_iamge():
    image_file =request.files.get('house_image')
    house_id = request.form.get('house_id')

    #检查数据

    image_data = image_file.read()

    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='上传图片失败')


#获取放大发布的房源信息
@api.route('/houses/fangdong')
@login_required
def get_user_house():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='数据库异常')

    houses_li =[]
    if houses:
        for house in houses:
            houses_li.append(house.to_basic_dict())
    return jsonify(error=RET.OK, errmsg='OK', data={'houses': houses_li})


#/api/v1/houses/?sd=20181101&ed=2018-11-02&aid=10&sk=new（排序方式）&p=页数
#获取房屋的列表信息
@api.route('/houses')
def get_house_list():
    start_date = request.args.get('sd')
    end_date = request.args.get('ed')
    area_id = request.args.get('aid') #区域编号
    sort_key = request.args.get('sort', 'new') #排序名字 没传 就默认按照new排序（新旧）
    page = request.args.get('p') #页数


    #处理时间
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date

    except Exception as e:
        current_app.logger.error(e)
        jsonify(error=RET.PARAMERR, errmsg='时间有问题')

    #区域id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            jsonify(error=RET.PARAMERR, errmsg='区域参数有误')

    #处理页数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page=1

    # 使用缓存
    redis_key = 'house_%s_%s_%s_%s' % (start_date, end_date, area_id, sort_key)

    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {'Content-Type': 'application/json'}



    #过滤参数列表的容器
    filter_params = []

    #处理时间条件
    conflict_orders = None #可能条件都不存在 先设置为none
    if start_date and end_date:  #有起始时间和结束时间 查询冲突的订单
        conflict_orders = Order.query.filter(Order.begin_date<=end_date, Order.end_date>=start_date)

    elif start_date: #只有起始时间
        conflict_orders = Order.query.filter(Order.end_date>=start_date)

    elif end_date:  #只有结束时间
        conflict_orders = Order.query.filter(Order.begin_date <= end_date)

    #不为空进行处理
    if conflict_orders:
        # 查询冲突的订单 ---取出冲突的房子的id
        conflict_houses_ids = [order.house_id for order in conflict_orders]
        if conflict_houses_ids: #不为空 才进行筛选
            filter_params.append(House.id.noin_(conflict_houses_ids))#不符合条件的


    #区域条件处理
    if area_id:
        filter_params.append(House.area_id == area_id)

    #查询数据库--补充排序条件,分页
    if sort_key == 'booking':
        # 入住最多（销量）
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == 'price-inc':
        # 价格排序 升序
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    elif sort_key =='price-des':
        # 价格排序降序
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    else:
        #默认new 或其他输入都这个# 时间培训
        # House.query.filter(House.id.noin_(conflict_houses_ids),House.area_id == area_id)
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    try:
        #处理分页 #(self, page=None, per_page=None, error_out=True, max_per_page=None):
        #每页20条 参数表也有, 关闭自动错误输出
        page_obj = house_query.paginate(page=page, per_page=20, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        jsonify(error=RET.PARAMERR, errmsg='数据库')


    # 页面数据
    page_li = page_obj.items
    houses = []
    for house in page_li:
        houses.append(house.to_basic_dict())

    # 获取总页数
    total_page = page_obj.pages

    #return jsonify(errno=RET.OK, errmsg='OK', data={'total_page':total_page, 'houses':houses, 'page':page})

    if page <= total_page:
        #缓存 house-开始-结束-区域-排序：｛1：xxx，2：xxx,,,,,,｝
        resp_dict = dict(errno=RET.OK, errmsg='OK', data={'total_page':total_page, 'houses':houses, 'page':page})
        resp_json = json.dumps(resp_dict)
        redis_key ='house_%s_%s_%s_%s' % (start_date, end_date, area_id, sort_key)
        #哈希类型
        try:
            #redis_store.hset(redis_key, page, resp_json)
            #redis_store.expire(redis_key, 3600) #设置时间3600秒
            #pipeline 2条命令一次提交(一次执行多条命令) 防止 第二条没执行 变永久有效
            pipeline = redis_store.pipeline()
            pipeline.hset(redis_key, page, resp_json)
            pipeline.redis_store.expire(redis_key, 3600) #设置时间3600秒
            #执行语句
            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {'Content-Type': 'application/json'}



