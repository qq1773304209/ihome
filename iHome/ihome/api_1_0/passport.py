# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db
from ihome.models import User
# 出现重复异常
from sqlalchemy.exc import IntegrityError


import re

# POST /api/v1.0/register
@api.route("/register", methods=["POST"])
def register():
    '''
    注册
    :return:
    '''

    # 接收数据 (手机号，SMS验证码，密码)
    req_dict = request.get_json()

    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password1 = req_dict.get('password1')
    password2 = req_dict.get('password2')

    # 校验数据完整性
    if not all([mobile, sms_code, password1, password2]):
        return jsonify(error=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号是否符合
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(error=RET.PARAMERR, errmsg="手机格式错误")

    # 密码是否一样, 是否符合格式
    if password1 != password2:
        return jsonify(error=RET.PARAMERR, errmsg="两次密码不一致")

    # 获取真实短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
        print(real_sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="SMS验证码查询错误")

    # 验证码过期
    if real_sms_code is None:
        return jsonify(error=RET.NODATA, errmsg="SMS验证码过期")

    # 删除redis验证码，防止重复校验
    try:
        redis_store.delete("sms_code_%s", mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 验证码是否正确
    if real_sms_code != sms_code:
        return jsonify(error=RET.DATAERR, errmsg="SMS验证码错误")

    # 数据库判断手机号是否重复
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     # 数据库异常
    #     current_app.logger.error(e)
    #     jsonify(error=RET.DBERR, errmsg="数据库查询手机号异常")
    # else:
    #     if user is not None:
    #         return jsonify(error=RET.DATAEXIST, errmsg="手机号已存在")


    # 保存用户资料
    # 合并，减少数据库查询
    user = User(name=mobile, mobile=mobile)
    # 密码加密
    # 封装到模型类中
    #user.generate_password_hash(password1)
    # 使用property装饰器
    user.password = password1
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # 表示手机号存在
        current_app.logger.error(e)
        return jsonify(error=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        jsonify(error=RET.DBERR, errmsg="数据库查询手机号异常")

    # 保存登录状态session
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 返回
    return jsonify(error=RET.OK, errmsg="注册成功")


@api.route("/login", methods=["POST"])
def login():
    '''
    登录
    :return:
    '''

    # 接收数据 （手机号， 密码）
    req_dict = request.get_json()

    mobile = req_dict.get("mobile")
    password = req_dict.get("password")

    # 校验数据
    if not all([mobile, password]):
        return jsonify(error=RET.PARAMERR, errmsg="参数不完整")

    # 判断手机号是否符合
    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(error=RET.PARAMERR, errmsg="手机格式错误")

    # 限制登录错误次数 redis    "access_nums_ip": "次数"
    user_ip = request.remote_addr  # 用户ip
    try:
        access_nums = redis_store.get("access_nums_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= current_app.config.get("LOGIN_ERROR_MAX_TIMES"):
            return jsonify(error=RET.REQERR, errmsg="超过登录限制次数")

    # 手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据库查询错误")
    else:
        # 判断密码是否正确
        if user is None or user.check_password_hash(password) is False:
            # 记录错误次数
            try:
                # incr(name, amount=1) 默认自动+1, 如果为空，则初始化为0
                redis_store.incr("access_nums_%s" % user_ip)
                # 设置限制时间
                redis_store.expire("access_nums_%s" % user_ip, current_app.config.get("LOGIN_ERROR_FORBID_TIME"))
            except Exception as e:
                current_app.logger.error(e)
            return jsonify(error=RET.DATAERR, errmsg="用户名或密码错误")


    # 保存登录状态session
    session["name"] = user.name
    session["mobile"] = user.mobile
    session["user_id"] = user.id

    # reutnr OK
    return jsonify(error=RET.OK, errmsg="登录成功")



@api.route("/session", methods=["GET"])
def check_login():
    '''检验登录状态'''
    name = session.get("name")
    print(name)
    if name is not None:
        return jsonify(error=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(error=RET.SESSIONERR, errmsg="false")

@api.route("/session", methods=["DELETE"])
def logout():
    '''退出登录'''
    # 清除session
    session.clear()
    return jsonify(error=RET.OK, errmsg="成功退出")
