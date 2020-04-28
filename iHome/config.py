# coding:utf-8

import redis


class Config(object):
    """配置信息"""
    SECRET_KEY = "abcd*"

    # 数据库
    DIALCT = 'mysql'
    DRIVER = "pymysql"
    USERNAME = 'root'
    PASSWORD = 'mysql'
    HOST = '39.108.106.122'
    PORT = '3306'
    DBNAME = 'iHome_db'
    SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}?charset=utf8'.format(DIALCT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DBNAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = True        #将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
    SQLALCHEMY_ECHO = True					#查询时会显示原始SQL语句

    # redis
    REDIS_HOST = "39.108.106.122"
    REDIS_PORT = 6379

    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 对cookie中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期，单位秒

    #redis存储验证码有效期（秒）
    IMAGE_CODE_REDIS_EXPIRES = 180
    # 验证码有效期
    SMS_CODE_REDIS_EXPIRES = 300
    # 短信验证码发送间隔
    SEND_SMS_CODE_INTERVAL = 60

    # 限制错误登录次数
    LOGIN_ERROR_MAX_TIMES = 5
    # 限制时间 秒
    LOGIN_ERROR_FORBID_TIME = 600

    # 文件存储url
    QINIU_URL_DOMAIN = "http://q9brfcv78.bkt.clouddn.com/"

    # area_info缓存时间 秒
    AREA_INFO_REDIS_CACHE_EXPIRES = 7200

    # 首页展示房子最大数量
    HOME_PAGE_MAX_HOUSES = 5
    # 首页展示房屋数据缓存 秒
    HOME_PAGE_DATA_REDIS_EXPIRES = 3600

    # 房屋详情缓存时间 秒
    HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 600

    # 房屋评论显示限制条数
    HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 10

    # 搜索列表页每页显示房屋个数
    HOUSE_LIST_PAGE_CAPACITY = 2

    # 搜索列表房屋信息缓存时间
    HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES = 600


class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}