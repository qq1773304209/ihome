# coding: utf-8
'''
用户资料
'''

from . import api
from flask import request, jsonify, current_app, g, session
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage_file
from ihome.utils.login_verify import login_required
from ihome import db
from sqlalchemy.exc import IntegrityError

from ihome.models import User

# POST   /api/v1.0/user/avatar
@api.route("/user/avatar", methods=["POST"])
@login_required
def set_user_avatar():
    '''上传用户头像'''
    # 用户id
    user_id = g.user_id
    # 接收图片文件
    image = request.files.get("avatar")

    # 校验图片
    if image is None:
        return jsonify(error=RET.PARAMERR, errmsg="图片未上传")

    # 判断图片格式
    #if f.name.match

    # 上传图片
    try:
        file_data = image.read()
        file_name = storage_file(file_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.IOERR, errmsg="图片上传失败")

    # 存入数据库
    try:
        User.query.filter_by(id=user_id).update({"avatar_url": file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据库写入错误")

    avatar_url = current_app.config.get("QINIU_URL_DOMAIN") + file_name
    # 返回
    return jsonify(error=RET.OK, errmsg="上传成功", data={"avatar_url": avatar_url})


# 对原有数据修改 PUT
# PUT   /api/v1.0/user/name
@api.route("/user/name", methods=["PUT"])
@login_required
def change_user_name():
    '''修改用户名'''
    user_id = g.user_id

    # 获取用户名称
    req_dict = request.get_json()
    user_name = req_dict.get("user_name")

    # 数据完整性
    if user_name is None:
        return jsonify(error=RET.PARAMERR, errmsg="名字不为空")


    # 用户名称是否符合

    # 修改数据库信息
    try:
        user = User.query.filter_by(id=user_id).update({"name": user_name})
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="用户名重复")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据库错误")

    # 修改session字段
    session["name"] = user_name

    # 返回
    return jsonify(error=RET.OK, errmsg="OK", data={"name": user_name})



@api.route("user", methods=["GET"])
def get_user_profile():
    '''获取个人信息'''
    user_id = g.user_id

    # 查询数据库User
    try:
        user = User.query.filter_by(id=user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="获取用户信息失败")

    if user is None:
        return jsonify(error=RET.NODATA, errmsg="无效操作")

    return jsonify(error=RET.OK, errmsg="OK", data=user.to_dict)

@api.route("user/auth", methods=["POST"])
def set_user_auth():
    '''保存实名信息'''

    user_id = g.user_id
    # 获取信息
    req_dict = request.get_json()

    real_name = req_dict.get("real_name")
    id_card = req_dict.get("id_card")

    # 参数完整性
    if not all([real_name, id_card]):
        return jsonify(error=RET.PARAMERR, errmsg="参数不完整")

    # 公安系统查询
    # 身份证是否存在

    # 设置信息到数据库
    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update({"real_name": real_name, "id_card": id_card})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="实名验证失败")

    return jsonify(error=RET.OK, errmsg="OK")




