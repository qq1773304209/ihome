# coding: utf-8

from flask import request, jsonify, g, session
from ihome.utils.response_code import RET
from functools import wraps


# 登录验证装饰器
def login_required(view_func):
    '''
    登录装饰器
    :param view_func:
    :return:
    '''
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户登录状态
        user_id = session.get("user_id")
        # 使用应用上下文g对象保存session, 当视图函数用到时不用重复查询数据库
        if user_id is None:
            return jsonify(error=RET.SESSIONERR, errmsg="用户未登录")
        # 已登录
        g.user_id = user_id
        return view_func(*args, **kwargs)
    return wrapper