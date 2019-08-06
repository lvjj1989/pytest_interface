# @Time    :2019/2/12 9:40
# @Author  :lvjunjie
import requests
import re
import json
import sys
import os
from urllib.parse import urlparse
python_version = sys.version[0]


def format_json(content, space_num=0):
    """
    格式化JSON
    """
    if python_version == '3':
        result = json.dumps(content, sort_keys=True, indent=4, separators=(',', ': ')). \
            encode('latin-1').decode('unicode_escape')
    else:
        result = json.dumps(content, sort_keys=True, indent=4, separators=(',', ': ')). \
            decode("unicode_escape")
    result = result.split('\n')
    result = [u' '*space_num + i for i in result]
    return '\n'.join(result).replace('true', 'True').replace('false', 'False')


class Swagger(object):
    def __init__(self, swagger_url):
        try:
            self.raw_data = requests.get(swagger_url).json()
        except:
            try:
                host = urlparse(swagger_url).netloc
                raw_json = requests.get('http://{}/swagger-resources'.format(host)).json()[0]
                url = raw_json['url']
                self.raw_data = requests.get('http://' + host + url).json()
            except:
                self.raw_data = {}
        self.tags = self.raw_data["tags"]
        self.paths = self.raw_data["paths"]
        self.template_name_list = []
        self.template_description_list = []

        for tag in self.tags:
            self.template_name_list.append(tag['name'])
            self.template_description_list.append(tag['description'])


    # 获取接口url
    def get_url(self):
        self.url_list = []
        for path in self.paths:
            self.url_list.append(path)
        return self.url_list

    # 获取接口请求方法
    def get_method(self):
        self.method_list = []
        self.method_desc_list = []
        for url in self.get_url():
            self.method_list.append(list(self.paths[url].keys())[0])
            self.method_desc_list.append(self.paths[url])

        return self.method_list

    # 获取接口所属模块
    def get_tags(self):
        method_list = self.get_method()
        # print(method_list)
        self.tags_list = []
        for method in self.method_desc_list:
            self.tags_list.append(method[list(method.keys())[0]]['tags'][0])
        return self.tags_list

    # 获取接口注释
    def get_summary(self):
        method_list = self.get_method()
        # print(method_list)
        self.summary_list = []
        for method in self.method_desc_list:
            self.summary_list.append(method[list(method.keys())[0]]['summary'])
        return self.summary_list

    # 获取接口入参
    def get_parameters(self):
        self.parameters_list = []
        self.url_parameters_list = []
        self.params_list = []
        self.json_list = []

        for url in self.get_url():
            url_parameters = []
            params_parameters = []
            json_parameters = []
            header_parameters = []
            method = list(self.paths[url].keys())[0]
            method_desc = self.paths[url]
            # print(method_desc)
            if method == 'get':
                # print(url)
                if "{" in url:
                    url_parameters.append(url[url.index('{') + 1: url.index('}')])
                if 'parameters' in list(method_desc['get'].keys()) and type(method_desc['get']['parameters']) is list:
                    for parameter in method_desc['get']['parameters']:
                        params_parameters.append(parameter['name'])
            elif method == 'post':
                if "{" in url:
                    url_parameters.append(url[url.index('{') + 1: url.index('}')])
                if 'parameters' in list(method_desc['post'].keys()) and type(method_desc['post']['parameters']) is list:
                    try:
                        for parameter in method_desc['post']['parameters']:
                            if parameter['in'] == 'query':
                                params_parameters.append(parameter['name'])
                            elif parameter['in'] == 'body':
                                json_parameters.append(parameter['name'])
                            elif parameter['in'] == 'header':
                                header_parameters.append(parameter['name'])
                            else:
                                json_parameters.append(parameter['name'])
                    except:
                        pass
            parameters = url_parameters + params_parameters + json_parameters + header_parameters

            self.url_parameters_list.append(url_parameters)
            self.params_list.append(params_parameters)
            self.json_list.append(json_parameters)

            self.parameters_list.append(list(set(parameters)))


        return self.parameters_list, self.params_list, self.json_list, self.url_parameters_list


if __name__ == '__main__':
    swagger_url = os.getenv('swagger_url', 'http://172.16.204.29:8044/swagger-ui.html')
    # swagger_url = 'http://172.16.204.55:8143/v2/api-docs?group=v1'
    # swagger_url = 'http://172.16.204.55:8143/swagger-ui.html#/user-info-controller/updateUserInfoByMobileUsingPOST'
    # swagger_url = 'http://172.16.204.29:8044/v2/api-docs?group=v1'
    swagger = Swagger(swagger_url)
    inter_swagger_data_list = []
    inter_template_name_list = swagger.template_name_list
    inter_template_description_list = swagger.template_description_list
    inter_url_list = swagger.get_url()
    inter_method_list = swagger.get_method()
    inter_tags_list = swagger.get_tags()
    inter_parameters_list = swagger.get_parameters()[0]
    inter_params_list = swagger.get_parameters()[1]
    inter_body_list = swagger.get_parameters()[2]
    inter_urlparameters_list = swagger.get_parameters()[3]
    inter_summary_list = swagger.get_summary()
    num = 0
    inter_swagger_data = {}

    # 数据处理
    for inter_template_name in inter_template_name_list:
        inter_swagger_data[inter_template_name] = []
    for inter_tags in inter_tags_list:
        swagger_data = {
                'url': inter_url_list[num],
                'method': inter_method_list[num],
                'parameters': inter_parameters_list[num],
                'params': inter_params_list[num],
                'body': inter_body_list[num],
                'urlparameters': inter_urlparameters_list[num],
                'summary': inter_summary_list[num]
            }
        inter_swagger_data[inter_tags].append(swagger_data)
        num = num + 1
        # inter_swagger_data_list.append(inter_swagger_data)
    # print(inter_swagger_data)

    # 转为pytest的api格式
    for swagger_data in list(inter_swagger_data.keys()):
        class_api = ''
        class_inter_api = ''
        # 首字母大写
        class_name = swagger_data.title()
        # 去掉非字母数字
        class_name = re.sub('[^a-zA-Z0-9]', '', class_name)
        class_api = class_api + '\n\nclass {}:'.format(class_name)
        # print(inter_swagger_data[swagger_data])

        # 编写该模块单接口API
        for inter_data in inter_swagger_data[swagger_data]:
            inter_api = ''
            inter_return = '        return {'
            # print(list(inter_data.keys()))
            if inter_data['urlparameters']:
                inter_api = inter_api + '\n\n    @request(method="{}")\n'.format(inter_data['method'])
            else:
                inter_api = '\n\n    @request(method="{}", url="{}")\n'.format(inter_data['method'], inter_data['url'])

            inter_name = inter_data['url'].replace("/", "_").replace("-", "_").replace("{", "").replace("}", "")[1:]
            if inter_data['parameters']:
                parameters = ''
                for item in inter_data['parameters']:
                    parameters = parameters + ', ' + item
                inter_api = inter_api + '    def {}(self{}):\n'.format(inter_name, parameters)
                if inter_data['urlparameters']:
                    # url_params = path[path.find('{') + 1:path.find('}')]
                    inter_api = inter_api + "        url = '" + inter_data['url'][:inter_data['url'].find('{')] + '{}' \
                     + "'.format(" + inter_data['urlparameters'][0] + ')\n'
                    inter_return = inter_return + "'url': url, "
            else:
                inter_api = '\n\n    @request(method="{}", url="{}")\n'.format(inter_data['method'], inter_data['url'])
                inter_api = inter_api + '    def {}(self):\n'.format(inter_name)

            if inter_data['summary']:
                inter_api = inter_api + '        # {}\n'.format(inter_data['summary'])

            if inter_data['params']:
                params = {}
                for item in inter_data['params']:
                    params[item] = item
                inter_return = inter_return + "'params': params, "
                inter_api = inter_api + '        params = ' + format_json(params, 8)[8:].replace(': "', ': ').replace('",', ',').replace('"\n', '\n')

            if inter_data['body']:
                body = {}
                for item in inter_data['body']:
                    body[item] = item
                inter_api = inter_api + '        json = ' + format_json(body, 8)[8:].replace(': "', ': ').replace('",', ',').replace('"\n', '\n')
                inter_return = inter_return + "'json': json, "
            inter_return = (inter_return + '}') if inter_return == '        return {' else (inter_return[:-2] + '}')
            inter_api = inter_api + '\n' + inter_return
            class_inter_api = class_inter_api + inter_api
            # print(inter_api)
        class_api = class_api + class_inter_api
        print(class_api)
    print('\n# 共{}个接口'.format((len(inter_url_list))))

