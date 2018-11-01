
from celery import Celery
from home.libs.yuntongxun.SendTemplateSMS import CCP

#创建celery对象
app = Celery("home", broker='redis://:redis@localhost:6379/2')

@app.tasks
def send_sms(to, datas, temmp_id):
    #发送短信

    ccp = CCP()
    ccp.sendTemplateSMS(to, datas, temmp_id)
