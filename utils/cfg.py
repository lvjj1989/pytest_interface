# @Time    :2018/10/29 16:57
# @Author  :lvjunjie
import allure
import os


class Test:

    # data_mock
    DATS_MOCK_HOST = "http://lvjunjie.cn:5000"

    class ACCOUNT:
        CRM_USER = '18000000000', '123456'


class Beta:

    # data_mock
    DATS_MOCK_HOST = "http://lvjunjie.cn:5000"

    class ACCOUNT:
        CRM_USER = '18000000000', '123456'


class Online:

    # data_mock
    DATS_MOCK_HOST = "http://lvjunjie.cn:5000"

    class ACCOUNT:
        CRM_USER = '18000000000', '123456'




CONFIG = Test

BUILD_USER = os.getenv('BUILD_USER', 'tester')
if BUILD_USER == '':
    BUILD_USER = 'tester'

environment = os.getenv('environment', 'test')

if environment == 'test':
    CONFIG = Test
else:
    CONFIG = Test

allure.environment(测试环境=environment, host=CONFIG.DATS_MOCK_HOST, 执行人=BUILD_USER, 测试项目='DMP后台接口')
