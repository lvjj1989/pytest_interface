# coding=utf-8
import json
import time
import sys
from functools import wraps
from hashlib import md5
import base64
import records



def get_md5(s):
    m = md5()
    m.update(s.encode("utf8"))
    return m.hexdigest()

python_version = sys.version[0]

if python_version == '3':
    basestring = str

def fn_timer(function):
    """
    元素查找计时器
    """
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        total_time = str(t1 - t0)
        return total_time, result

    return function_timer


def format_json(content):
    """
    格式化JSON
    """
    if isinstance(content, basestring):
        content = json.loads(content)

    if python_version >= '3':
        result = json.dumps(content, sort_keys=True, indent=4, separators=(',', ': ')). \
            encode('latin-1').decode('unicode_escape')
    else:
        result = json.dumps(content, sort_keys=True, indent=4, separators=(',', ': ')). \
            decode("unicode_escape")

    return result


def pretty_print(content):
    """
    美化打印
    """
    print(format_json(content))





class DB(object):
    def __init__(self, db_url):
        self.db_url = db_url

    def query(self, statement, **params):
        db = records.Database(self.db_url)
        res = db.query(statement, **params)
        db.close()
        return res

def get_base64(s):
    bytesString = s.encode(encoding="utf-8")
    encodestr = base64.b64encode(bytesString)
    return encodestr





class DB(object):

    def __init__(self, db_url):
        self.db_url = db_url

    def query(self, statement, **params):
        db = records.Database(self.db_url)
        res = db.query(statement, **params)
        db.close()
        return res
