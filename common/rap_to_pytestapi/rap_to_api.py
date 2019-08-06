# coding=utf-8
from common.rap_to_pytestapi.login_rag import RapLogin
import json

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
                name_list.append(module_name +'_'+ j['name'])
                for k in j['actionList']:
                    notes_list.append('""" ' + module_name +'_'+ name + '_' +  k['name'] + '"""')
        return notes_list
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

    def get_api_request_parameter(self,json):
        request_parameter_list = []
        for i in json['projectData']['moduleList']:
            for j in i['pageList']:
                # print(i['pageList'])
                for k in j['actionList']:
                    method_name = (k['requestUrl']).replace('\\','').replace('/','_')[1:]
                    parameter = ''
                    for l in k['requestParameterList']:
                        parameter = parameter + l['identifier'] + ', '
                    request_parameter_list.append('def ' + method_name + '(self, ' + parameter[:-2] +'):')

        return request_parameter_list
    def get_api_json(self,json):
        json_list = []
        for i in json['projectData']['moduleList']:
            for j in i['pageList']:
                # print(i['pageList'])
                for k in j['actionList']:
                    json_parameter = ''
                    for l in k['requestParameterList']:
                        json_parameter =json_parameter + '      "' + l['identifier'] + '": ' + l['identifier'] + ',\n'
                    json_parameter = json_parameter[:-2]# 去掉最后一个逗号
                    json_parameter = 'json = {\n' + json_parameter + '\n   }'
                    json_list.append(json_parameter)
        return json_list





if __name__ == '__main__':
    import time
    rap_login = RapLogin()
    json_rap = eval(rap_login.login('lvjunjie', 'a1478520B',60))

    # print(json_rap)
    rap_to_api = RapToApi()
    # print(rap_to_api.get_api_Notes(json_rap))
    # print(rap_to_api.get_api_path(json_rap))
    # print(rap_to_api.get_api_path(json_rap))
    # print(rap_to_api.get_api_request_parameter(json_rap))
    # print(rap_to_api.get_api_json(json_rap)[0])

    for i in range(1, len(rap_to_api.get_api_Notes(json_rap))):
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

    print('\n一共生成' + str(i) + '个接口' )



