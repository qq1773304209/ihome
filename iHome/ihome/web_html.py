# coding:utf-8
'''
功能：返回静态页面
实现：无需/static/html/~.html 直接 /~.html
'''

from flask import Blueprint, current_app
from flask_wtf import csrf

# 创建蓝图对象
html = Blueprint('web_html', __name__)


#127.0.0.1：5000/~.html
#127.0.0.1：5000/   ->   127.0.0.1：5000/index.html
@html.route('/<re(".*"):get_file_name>')
def get_html(get_file_name):
    '''
    :param file_name:
    :return: static_html
    '''
    # 127.0.0.1：5000/   ->   127.0.0.1：5000/index.html
    if not get_file_name:
        get_file_name = 'index.html'

    # 127.0.0.1：5000/~.html
    if get_file_name != 'favicon.ico':
        get_file_name = 'html/' + get_file_name

    # 生成csrf_token
    csrf_token = csrf.generate_csrf()

    resp = current_app.send_static_file(get_file_name)

    #设置csrf_token
    resp.set_cookie('csrf_token', csrf_token)

    return resp