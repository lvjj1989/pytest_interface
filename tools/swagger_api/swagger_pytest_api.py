# coding=utf-8
import requests
import sys
import json
import yaml

from jinja2 import Template
from collections import deque

python_version = sys.version[0]


class Swagger(object):

    def __init__(self, swagger_url):
        self.raw_data = requests.get(swagger_url).json()
        self._definitions = self.raw_data['definitions']
        self.tags = [self._make_class_name(tag['name']) for tag in self.raw_data['tags']]
        self.result = []
        self.q = deque(maxlen=5)

    def parse(self):
        for path, api_dicts in self.raw_data['paths'].items():
            if_params_in_url = '{' in path
            for method, values in api_dicts.items():
                # print(path)
                # print(values.get('summary'))

                # path中带有参数
                if '{' in path:
                    path_format = path[:path.index('{') - 1] + '\'.format('+ path[path.index('{') +1 : path.index('}')] +')'
                    # print('path中带有参数')
                    # print(path_format)

                else:
                    path_format = path
                    # print(path_format)


                if list(self._parse_parameters(values.get('parameters', [])).values()):
                    list_params = list(yaml.load(list(self._parse_parameters(values.get('parameters', [])).values())[0]).keys())
                    if list_params:
                        params = ""
                        for param in list_params:
                            params = "=None, " + param + params
                        params = params[5:] + "=None"
                        params = params.replace("-", "_")
                # print(params)
                name = path.replace("/", "_").replace("-", "_").replace("{", "").replace("}", "")[1:]
                self.result.append(
                    {
                        'if_params_in_url': if_params_in_url,
                        'tag': self._make_class_name(values.get('tags')[0]),
                        'path': path,
                        'name': self._make_function_name(path),
                        'name': name,
                        'method': method,
                        'summary': values.get('summary'),
                        'type': values.get('consumes'),
                        'parameters': self._parse_parameters(values.get('parameters', [])),
                        'params': params,
                        'path_format': path_format
                    }

                )
        print("共 " + str(len(self.raw_data['paths'].items())) + " 个接口")
    def _parse_parameters(self, parameters):
        print('parameters')
        print(parameters)
        result = {}
        if isinstance(parameters, dict):
            return result

        for parameter in parameters:
            _in = parameter['in']
            name = parameter['name']
            _type = parameter.get('type')
            schema = parameter.get('schema')
            if _type:
                result[_in] = result.get(_in, {})
                result[_in][name] = self._type2value(_type)
            elif schema:
                result[_in] = self._parse_schema(schema)
            else:
                raise Exception(u'错错错')
        for k, v in result.items():
            result[k] = self.format_json(v)
        return result

    @staticmethod
    def _type2value(t):
        if t == 'string':
            return 'string'
        elif t == 'integer':
            return 1
        elif t == 'array':
            return []
        elif t == 'boolean':
            return True
        elif t == 'object':
            return {}
        elif t == 'number':
            return 1
        else:
            return 'string'

    def _parse_schema(self, schema):
        result = {}
        try:
            if self.q[0] == self.q[4]:
                return result
        except:
            pass

        _type = schema.get('type')
        if _type == 'array':
            return [self._parse_schema(schema['items']), ]
        elif _type in ['integer', 'string', 'boolean', 'number']:
            return self._type2value(schema.get('type'))

        try:
            definition_name = schema['$ref'].split('/')[-1]
        except KeyError:
            return {}

        self.q.append(definition_name)
        try:
            definition = self._definitions[definition_name]
        except:
            return {}
        if definition['type'] == 'object':
            properties = definition.get('properties')
            if not properties:
                return result
            for name, value in properties.items():
                if value.get('type') == 'array' or value.get('$ref'):
                    result[name] = self._parse_schema(value)
                else:
                    result[name] = self._type2value(value['type'])
        else:
            raise Exception('unknown type')

        return result

    def _make_class_name(self, s):
        return self._underline2camel(s)

    def _make_function_name(self, s):
        s = [i for i in s.split('/') if '{' not in i]
        return self._camel2underline(s[-1])

    @staticmethod
    def _camel2underline(s):
        """
            驼峰命名格式转下划线命名格式
        """
        s = list(s)
        for index, value in enumerate(s[1:]):
            if 'A' <= value <= 'Z':
                s[index + 1] = '_' + value.lower()
        return ''.join(s).lower().replace('-', '_')

    @staticmethod
    def _underline2camel(underline_format):
        """
            下划线命名格式驼峰命名格式
        """
        camel_format = ''
        if isinstance(underline_format, str):
            for _s_ in underline_format.replace('-', '_').split('_'):
                camel_format += _s_.capitalize()
        return camel_format

    @staticmethod
    def format_json(content):
        """
        格式化JSON
        """
        # if isinstance(content, basestring):
        #     content = json.loads(content)

        if python_version == '3':
            result = json.dumps(content, sort_keys=True, indent=4, separators=(',', ': ')). \
                encode('latin-1').decode('unicode_escape')
        else:
            result = json.dumps(content, sort_keys=True, indent=4, separators=(',', ': ')). \
                decode("unicode_escape")

        result = result.split('\n')
        result = [result[0]] + [u'        ' + i for i in result[1:]]

        return '\n'.join(result).replace('true', 'True').replace('false', 'False')

SCRIPT_TEMPLATE = u"""
from pithy import request, response
from utils.cfg import CONFIG


class {{ class_name }}(object):
    def __init__(self):
        self.base_url = CONFIG.CRM_BASE_URL_HTTP
    {% for item in items %}
    @request({% if not item['if_params_in_url'] %}url='{{ item['path'] }}', {% endif %}method='{{ item['method'] }}')
    def {{ item['name'] }}(self{{ item['params'] }}):
        \"\"\"
        {{ item['summary'] }}
        \"\"\"
        {% set response = [] -%}
        {%- if item['if_params_in_url'] %}
        url = '{{ item['path_format'] -}}
        {%set response = response + ['url=url']  -%}
        {% endif -%}
        {%- if item['parameters'].get('query') %}
        params = {{ item['parameters'].get('query') -}}
        {%set response = response + ['params=params']  -%}
        {% endif -%}
        {%- if item['parameters'].get('fromData') %}
        data = {{ item['parameters'].get('data') -}}
        {%set response = response + ['data=data']  -%}
        {% endif -%}
        {%- if item['parameters'].get('body') %}
        _json = {{ item['parameters'].get('body') -}}
        {%set response = response + ['json=_json']  -%}
        {% endif %}
        return response({{ ', '.join(response) }})
    {% endfor %}
"""

if __name__ == '__main__':
    swagger_url = 'http://172.16.204.55:8143/v2/api-docs?group=v1'
    class_name = 'Controller'
    object_file_name = '../apis/test_api.py'

    ss = Swagger(swagger_url)
    ss.parse()
    t = Template(SCRIPT_TEMPLATE).render(class_name=class_name, tags=ss.tags, items=ss.result)
    print(t)
    with open(object_file_name, 'wb') as f:
        f.write(t.encode('utf-8'))
