
from .houses import api
from home.utils.commons import login_required
from home.models import Order
from flask import g, current_app, jsonify, request
from home.utils.response_code import RET
from home import constants, db
from alipay import AliPay
import os

#支付宝支付
@api.route('/order/<int:order_id>/payment', methods=['POST'])
@login_required
def order_pay(order_id):
    user_id= g.user_id
    #查看订单状态
    try:
        order = Order.query.filter(Order.id==order_id, Order.user_id==user_id, Order.status=='WAIT_PAYMENT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if order_id is None:
        return jsonify(errno=RET.NODATA, errmsg='订单数据有误')

    #构造请求

    app_id = '2016092200568136'
    # post请求，用于最后的检查
    notify_url = 'http://127.0.0.1:8000/pay_result/'
    # get请求,用于页面的跳转展示
    return_url = 'http://127.0.0.1:8000/pay_result/'
    merchant_private_key_path = os.path.join(os.path.dirname(__file__), 'keys/app_private_2048.txt')
    alipay_public_key_path = os.path.join(os.path.dirname(__file__), 'keys/alipay_public_2048.txt')

    alipay_client = AliPay(
        appid=app_id,
        app_notify_url=notify_url,#支付成功支付宝向这个url发送post请求(校验是否交易完成)
        #return_url=return_url,    #支付成功，跳回来的网站地址
        app_private_key_path=merchant_private_key_path,#应用的私钥
        alipay_public_key_path=alipay_public_key_path,#支付宝公钥，验证支付宝回传消息使用
        sign_type='RSA',
        debug=True
    )


    #发起支付
    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no= order.id, #订单编号
        total_amount=str(order.amount/100.0), #总金额
        subject= '啦啦啦jizishuo啦啦啦',   #订单标题
        return_url = '',  #返回的链接地址
        notify_url = None,  #上边有了
    )

    #拼接支付地址
    pay_url = 'https://openapi.alipaydev.com/gateway.do?{}' + order_string

    return jsonify(errno=RET.OK, errmsg='OK', data={'pay_url':pay_url})


#更新订单
@api.route('/pay_result', methods=['PUT'])
def save_order_payment_result():
    #
    alipay_dict = request.form.to_dict()

    alipay_sign = alipay_dict.pop('sign')

    #构造请求
    app_id = '2016092200568136'
    # post请求，用于最后的检查
    notify_url = 'http://127.0.0.1:8000/pay_result/'
    # get请求,用于页面的跳转展示
    return_url = 'http://127.0.0.1:8000/pay_result/'
    merchant_private_key_path = os.path.join(os.path.dirname(__file__), 'keys/app_private_2048.txt')
    alipay_public_key_path = os.path.join(os.path.dirname(__file__), 'keys/alipay_public_2048.txt')

    alipay_client = AliPay(
        appid=app_id,
        app_notify_url=notify_url,#支付成功支付宝向这个url发送post请求(校验是否交易完成)
        #return_url=return_url,    #支付成功，跳回来的网站地址
        app_private_key_path=merchant_private_key_path,#应用的私钥
        alipay_public_key_path=alipay_public_key_path,#支付宝公钥，验证支付宝回传消息使用
        sign_type='RSA',
        debug=True
    )

    #校验
    result = alipay_client.verify(alipay_dict, alipay_sign)

    if result and alipay_dict["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED" ):
        order_id = alipay_dict.get('out_trade_no')
        # 流水账号也要保存
        trade_no = alipay_dict.get('trade_no')
        try:
            Order.query.filter_by(id=order_id).update({'status':'PAID', '流水号': trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg='OK')
