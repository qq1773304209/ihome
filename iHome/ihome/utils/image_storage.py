# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_data, etag
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 'Uc2nXOL1EYPPjXNdSL4_ftVTyQNjWKOxcEMqRGcW'
secret_key = 'e-qmjCS8JbgVYhik_lGlS5m_W7DgLVjUrfVQRFEL'

def storage_file(file_data):
    '''
    :param file_data: 
    :return: 
    '''
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'ihome-fs'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    """
            def put_data(
                up_token, key, data, params=None, mime_type='application/octet-stream', check_crc=False,
                progress_handler=None,
                fname=None):
           上传二进制流到七牛
            Args:
                up_token:         上传凭证
                data:             上传二进制流
            Returns:
                一个dict变量，类似 {"hash": "<Hash string>", "key": "<Key string>"}
    """
    ret, info = put_data(token, None, file_data)

    if info.status_code != 200:
        # 上传失败
        raise Exception("上传失败")

    return ret.get("key")
    # print(info)
    # print('-------------------')
    # print(ret)


# if __name__ == '__main__':
#     with open('./__init__.py', "rb") as f:
#         file_data = f.read()
#         storage_file(file_data)