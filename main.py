# from pywebio.platform import path_deploy_http
#
#
# def index(path: str):
#     print(path)
#     return "hellox"
#
#
# if __name__ == '__main__':
#     path_deploy_http(base='./tools', host='0.0.0.0', port=8087, debug=False)

from pywebio import start_server
from pywebio.output import *
from pywebio.session import *

from tools.html2md import html2md
from tools.md2go import md2go


# 实现网页跳转
# def task_1():
#     put_text('task_1')
#     put_buttons(['Go task 2'], [lambda: go_app('task_B')])
#
#
# def task_2():
#     put_text('task_2')
#     put_buttons(['Go task 1'], [lambda: go_app('task_A')])


def index():
    put_info("Ye工具箱")
    put_button('1.将md文件转化成go', lambda: go_app('md2go'))
    put_button('2.将html转成md', lambda: go_app('html2md'))


# equal to `start_server({'index': index, 'task_1': task_1, 'task_2': task_2})`
start_server([index, md2go, html2md], host="0.0.0.0", port=8087)
