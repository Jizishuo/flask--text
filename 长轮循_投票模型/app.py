from flask import Flask, render_template, request, jsonify, session
import uuid
import queue

app = Flask(__name__)
app.secret_key = 'ydgkuaugugFGKFGF' #session加密

User_list = {
    '1': {'name': '淘宝', 'count': 2},
    '2': {'name': '京东', 'count': 1},
    '3': {'name': '平多多', 'count': 0}
}

#队列列表
QUEUE_DICT = {}

@app.route('/user/list')
def user_lisy():
    user_uuid = str(uuid.uuid4())
    QUEUE_DICT[user_uuid] = queue.Queue() #每一个用户对应一个q
    session['current_user_uuid'] = user_uuid

    return render_template('user_list.html', users=User_list)

@app.route('/vote', methods=['POST'])
def vote():
    uid = request.form.get('uid')
    #print(uid)
    User_list[uid]['count'] += 1
    for q in QUEUE_DICT.values():
        q.put(User_list)

    return '投票成功'

@app.route('/get/vote', methods=['GET'])
def get_vote():
    user_uuid = session['current_user_uuid']
    q = QUEUE_DICT[user_uuid]

    ret = {'status': True, 'data': None}
    try:
        users = q.get(timeout=5)
        ret['data'] = users
    except queue.Empty:
        ret['status'] = False

    #return jsonify(User_list)
    return jsonify(ret)

if __name__ == '__main__':
    app.run(threaded=True)