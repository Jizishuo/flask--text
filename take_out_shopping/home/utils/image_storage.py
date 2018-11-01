from qiniu import Auth, put_data
#需要填写你的 Access Key 和 Secret Key
access_key = ''
secret_key = ''


def storage(fiel_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'jzishuo'
    #上传到七牛后保存的文件名
    #key = '' 自动生成不指定
    key = None
    #生成上传 Token，可以指定过期时间等

    #3600为token过期时间，秒为单位。3600等于一小时
    token = q.upload_token(bucket_name, key, 3600)

    ret, info = put_data(token, key, fiel_data)
    #print(info)
    if info.status_code ==200:
        return ret.get("key") #文件名字
    else:
        raise Exception('文件上传失败')
