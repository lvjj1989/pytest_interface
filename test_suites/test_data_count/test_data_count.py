# @Time    :2018/11/22 17:37
# @Author  :lvjunjie

from apis.data_mock_api import DataMockApi


class TestDataCount(object):

    def test_data_count(self):
        data_mock = DataMockApi()
        res = data_mock.data_count_register(username="testlvjj1", remarks="测试123")
        res_json = res.json
        assert res_json["code"] == 0
        usertoken = res_json["msg"]["usertoken"]
        # usertoken = "cT5mg4kwhCsp2xizVCWOhYs91kXlwSOM"

        res = data_mock.data_count_get(usertoken=usertoken)
        res_json = res.json
        assert res_json["code"] == 0
        count1 = res_json["msg"]["count"]

        res = data_mock.data_count_post(usertoken=usertoken, operation="add")
        res_json = res.json
        assert res_json["code"] == 0

        res = data_mock.data_count_get(usertoken=usertoken)
        res_json = res.json
        assert res_json["code"] == 0
        count2 = res_json["msg"]["count"]
        assert count2 == count1 + 1

        res = data_mock.data_count_post(usertoken=usertoken, operation="clear")
        res_json = res.json
        assert res_json["code"] == 0

        res = data_mock.data_count_get(usertoken=usertoken)
        res_json = res.json
        assert res_json["code"] == 0
        count3 = res_json["msg"]["count"]
        assert count3 == 0

