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

if __name__ == '__main__':
    rap_login = RapLogin()
    res_rap = rap_login.login('lvjunjie','a1478520B', 60)
    print(res_rap)
    json_res =eval(res_rap)
    print(json_res['projectData'])



