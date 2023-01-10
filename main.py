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
from tools.md2go_v2 import md2go_v2

HOST = "0.0.0.0"
PORT = 8087


def index():
    put_info("Ye工具箱")
    put_button('1.Mardown转go解析器', lambda: go_app('md2go'))
    put_button('2.markdown转go解析器(非侵入版)', lambda: go_app('md2go_v2'))
    put_button('2.将html转成md', lambda: go_app('html2md'))


# equal to `start_server({'index': index, 'task_1': task_1, 'task_2': task_2})`
start_server([index, md2go, md2go_v2, html2md], host=HOST, port=PORT)
