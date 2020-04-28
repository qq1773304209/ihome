# coding:utf-8

from . import api
from flask import request
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, db
from flask import current_app, jsonify, make_response
from ihome.models import User

from ihome.utils.response_code import RET
from ihome.libs.SMS_SDK.SendTemplateSMS import SMS
import random


# GET /api/v1.0/image_code/<image_code_id>
@api.route("/image_code/<image_code_id>")
def get_verify_code(image_code_id):
    '''
    获取图片验证码
    :param image_code_id:
    :return: 图片验证码  error：RET.DBERR
    '''
    # 生成验证码（图片名，）
    name, text, image_data = captcha.generate_captcha()
    # 获取image_code_id，并和生成验证码存入redis,使用string类型
    # 设置存在时间
    # redis_store.set("image_code_%s" % image_code_id, text)
    # redis_store.expire("image_code_%s" % image_code_id, 180)
    try:
        redis_store.setex("image_code_%s" % image_code_id, current_app.config.get('IMAGE_CODE_REDIS_EXPIRES'), text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='save image code failed')

    # 返回验证码
    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


# GET /api/v1.0/SMS_code/phone_no
@api.route("SMS_code/<re(r'1[34578]\d{9}'):phone_no>")
def send_SMS_verify(phone_no):
    '''
    发送短信验证码
    :param phone_no:
    :return:
    '''
    # 获取图片验证码
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 数据是否完整
    if not all([image_code_id, image_code]):
        # 表示参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # redis取出对应验证码，并校验图片验证码
    try:
        code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 验证码是否过期
    if code is None:
        # 表示图片验证码没有或者过期
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")

    # 删除redis中的图片验证码，防止用户使用同一个图片验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 与用户填写的值进行对比
    if code.lower() != image_code.lower():
        # 表示用户填写错误
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

    # 判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % phone_no)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            # 表示在60秒内之前有过发送的记录
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60秒后重试")

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=phone_no).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            # 表示手机号已存在
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 短信验证码生成
    sms_code = "%06d" % random.randint(0, 999999)

    # 保存验证码
    # 以手机号为key，验证码datas为值存入redis string
    try:
        redis_store.setex("sms_code_%s" % phone_no, current_app.config.get('SMS_CODE_REDIS_EXPIRES'), sms_code)
        # 保存发送给这个手机号的记录，防止用户在60s内再次出发发送短信的操作
        redis_store.setex("send_sms_code_%s" % phone_no, current_app.config.get('SEND_SMS_CODE_INTERVAL'), 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg='save image code failed')

    # 发送短信
    # @param to 手机号码
    # @param datas 内容数据 格式为列表 例如：['12','34']，如不需替换请填 ''
    # @param $tempId 模板Id
    try:
        sms = SMS()
        result = sms.send_template_sms(phone_no, [sms_code, int(current_app.config.get('SMS_CODE_REDIS_EXPIRES') / 60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")

    # 返回值
    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")