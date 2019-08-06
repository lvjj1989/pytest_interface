
import sys
import re
import yaml
import os
try:
    file_name = sys.argv[1]
except:
    file_name = 'html/content/js/dashboard.js'

try:
    with open(file_name, 'r+', encoding='utf8') as f:
        lines = f.readlines()
        if lines:
            for item in lines:
                # print(item)
                if "#statisticsTable" in item:
                    # print(item)
                    pattern = re.compile(r'"data":.+?]')
                    result_list = pattern.findall(item)
                    pattern = re.compile(r'"titles":.+?]')
                    title_list = pattern.findall(item)
                    title_list = yaml.load(title_list[0][9:])
                    report_list = []
                    for result in result_list:
                        res = yaml.load(result[8:])
                        # print(res)
                        report_dict = {}
                        for i in range(0, len(title_list)):
                            if res[0] == 'Total':
                                continue
                            report_dict[title_list[i]] = res[i]
                        if report_dict:
                            report_list.append(report_dict)

                    # print(report_list)
    message = ''
    for item in report_list:
        message = message + ("%s 接口，请求次数：%d, 平均响应时间： %.2f，line 90： %.2f, line 95：%.2f, 错误率：%.2f，"
                             "吞吐量：%.2f \n" % (item['Label'], item['#Samples'], item['Average'], item['90th pct'],
                                              item['95th pct'], item['Error %'],item['Throughput']))
    # print(message)
    os.environ['jmeter_res_message'] = message
    # os.putenv("jmeter_res_message", message)
    print(os.getenv('jmeter_res_message', 'no messange'))

except:
    pass
