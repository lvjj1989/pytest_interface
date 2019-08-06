# @Time    :2018/11/22 10:05
# @Author  :lvjunjie

from common.api import request
from utils.cfg import CONFIG

host = CONFIG.DATS_MOCK_HOST

class DataMockApi(object):

    def __init__(self):
        self.base_url = host
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }

    @request(url='/mock/count', method='post')
    def data_count_register(self, username=None, remarks=None):
        """
        注册
        :param username: 用户名
        :param remarks: 备注
        :return:
        """

        json = {
            "operation": "register",
            "username": username,
            "remarks": remarks
        }
        return {"json": json, "headers": self.headers}


    @request(url='/mock/count', method='post')
    def data_count_post(self,usertoken=None, operation=None):
        """
        计数器
        :param usertoken: 用户标识
        :param operation: 操作，add为加1，clean为清零
        :return:
        """
        json = {
            "operation": operation,
            "usertoken": usertoken
        }
        return {"json": json, "headers": self.headers}

    @request(url='/mock/count', method='get')
    def data_count_get(self, usertoken):
        """
        获取数据
        :param usertoken: 用户标识
        :return:
        """
        params = {
            "usertoken": usertoken
        }
        return {"params": params, "headers": self.headers}
