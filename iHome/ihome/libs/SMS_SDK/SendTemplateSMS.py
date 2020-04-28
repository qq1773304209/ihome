# coding:utf-8

#-*- coding: UTF-8 -*-  

from .CCPRestSDK import REST

#主帐号
accountSid= '8a216da8719c20ad0171a55ec453052c'

#主帐号Token
accountToken= '436a910beaed4d48a14b9de6e26d1fd6'

#应用Id
appId='8a216da8719c20ad0171a55ec4bc0532'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

class SMS(object):
    # 用来保存对象的类属性
    instance = None
    # 单例，只创建一次
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            obj = super(SMS, cls).__new__(cls)
            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls.instance = obj

        return cls.instance


    def send_Template_SMS(self, to, datas, tempId):

        result = self.rest.sendTemplateSMS(to, datas, tempId)

        for k, v in result.items():

            if k =='templateSMS' :
                    for k, s in v.items():
                        print('%s:%s' % (k, s))
            else:
                print('%s:%s' % (k, v))

        # smsMessageSid:ff75e0f84f05445ba08efdd0787ad7d0
        # dateCreated:20171125124726
        # statusCode:000000
        # 判断是否发送成功
        status_code = result.get("statusCode")
        if status_code == "000000":
            # 表示发送短信成功
            return 0
        else:
            # 发送失败
            return -1
   
#sendTemplateSMS(手机号码,内容数据,模板Id)

if __name__ == "__main__":
    sms = SMS()
    ret = sms.send_Template_SMS("13168352291", ['1234', '5', ], 1)
    print(ret)