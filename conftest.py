# @Time    :2018/10/29 16:57
# @Author  :lvjunjie
from datetime import datetime
from py.xml import html
import pytest
import os



@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Description'))
    cells.insert(3, html.th('Time', class_='sortable time', col='time'))
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.insert(1, html.td(html.pre(report.description)))
    cells.insert(3, html.td(datetime.utcnow(), class_='col-time'))
    cells.pop()


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    try:
        description = item.function.__doc__.decode('utf-8')
    except:
        description = item.function.__doc__
    # description = html.br.join(description.split('\n'))

    report.description = description

