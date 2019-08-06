# coding=utf-8

import requests


class RapLogin(object):
    def login(self,account, password, projectId):
        sessiona = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
        }
        data_login = {
            'account': account,
            'password': password
        }
        res_login = sessiona.post(url='http://172.16.2.71:8068/account/doLogin.do',data=data_login,headers=headers)
        # print(res_login.status_code)
        rap_index = sessiona.get('http://172.16.2.71:8068/org/index.do', headers=headers)
        data_getRap = {
            'projectId': projectId
        }
        res = sessiona.post(url='http://172.16.2.71:8068/workspace/loadWorkspace.do', data=data_getRap,headers=headers)
        return res.text


class RapToApi(object):

    # 接口备注
    def get_api_Notes(self,json):
        module_name_list = []
        name_list = []
        notes_list = []
        for i in json['projectData']['moduleList']:
            module_name = i['name']
            module_name_list.append(i['name'])
            for j in i['pageList']:
                name = j['name']
                name_list.append(module_name +'_' + j['name'])
                for k in j['actionList']:
                    notes_list.append('""" ' + module_name +'_'  + name + '_' + k['name'] + '"""')
        return notes_list

    # 接口路径
    def get_api_path(self,json):
        path_list = []
        for i in json['projectData']['moduleList']:
            for j in i['pageList']:
                # print(i['pageList'])
                for k in j['actionList']:
                    # @request(url='/garden/detail', method='post')
                    # print(k['requestUrl'])
                    path_list.append("@request(url='" + k['requestUrl'].replace('\\','') + "', method='post')")
        return path_list

    # 接口入参名
    def get_api_request_parameter(self,json):
        request_parameter_list = []
        for i in json['projectData']['moduleList']:
            for j in i['pageList']:
                # print(i['pageList'])
                for k in j['actionList']:
                    method_name = (k['requestUrl']).replace('\\','').replace('/','_')
                    if method_name[0:1] == '_':
                        method_name = method_name[1:]
                    parameter = ''
                    for l in k['requestParameterList']:
                        parameter = parameter + l['identifier'] + ', '
                    parameter = '(self, ' + parameter
                    request_parameter_list.append('def ' + method_name + parameter[:-2] + '):')

        return request_parameter_list

    # 接口入参格式
    def get_api_json(self, json):
        json_list = []
        for i in json['projectData']['moduleList']:
            for j in i['pageList']:
                for k in j['actionList']:
                    json_parameters = ''
                    for l in k['requestParameterList']:
                        if not l['parameterList']:
                            json_parameters = json_parameters + '      "' + l['identifier'] + '": ' + l['identifier'] + ',\n'
                        elif l['dataType'] == 'object':
                            json_parameter = ''
                            for ll in l['parameterList']:
                                json_parameter = '\n' + '            "' + ll['identifier'] + '": ' + ll['identifier'] + ',' + json_parameter
                            json_parameter = l['identifier'] + '": {' + json_parameter[:-1] + '\n            },\n'
                            json_parameters = json_parameters + '      "' + json_parameter
                        elif l['dataType'] == 'array<object>':
                            json_parameter = ''
                            i = 0
                            for ll in l['parameterList']:
                                json_parameter = '\n' + '            "' + ll['identifier'] + '": ' + ll['identifier'] + ',' + json_parameter
                            json_parameter = l['identifier'] + '": [' + json_parameter[:-1] + '\n            ],\n'
                            json_parameters = json_parameters + '      "' + json_parameter

                    json_parameters = json_parameters[:-2]
                    json_parameters = 'json = {\n' + json_parameters + '\n   }'
                    json_list.append(json_parameters)
        return json_list





if __name__ == '__main__':
    import time
    import sys
    # id = sys.argv[1]
    # account = sys.argv[2]
    # password = sys.argv[3]
    id = 131
    rap_login = RapLogin()
    # json_rap = eval(rap_login.login(account, password,id))
    json_rap = eval(rap_login.login('lvjunjie', 'a1478520B',id))


    print(json_rap)
    rap_to_api = RapToApi()
    print(rap_to_api.get_api_Notes(json_rap))
    print(rap_to_api.get_api_path(json_rap))
    print(rap_to_api.get_api_request_parameter(json_rap))
    print(rap_to_api.get_api_json(json_rap)[0])

    for i in range(0, len(rap_to_api.get_api_Notes(json_rap))):
        print(rap_to_api.get_api_path(json_rap)[i])
        time.sleep(0.1)
        print(rap_to_api.get_api_request_parameter(json_rap)[i])
        time.sleep(0.1)
        print('   ' + rap_to_api.get_api_Notes(json_rap)[i])
        time.sleep(0.1)
        print('   ' + rap_to_api.get_api_json(json_rap)[i])
        print("   return {'json': json, 'headers' : self.headers}")
        print('\n')
        i = i+1

    print('\n一共生成' + str(i) + '个接口')



