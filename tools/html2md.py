# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         a 
# Author:       yepeng
# Date:         2021/10/22 2:44 下午
# Description: 
# -------------------------------------------------------------------------------
import re

from bs4 import BeautifulSoup
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *


class Parse(object):
    def __init__(self, html_file, code_inline, language):
        self.soup = BeautifulSoup(html_file, 'html.parser')
        self.buff = []
        self.language = 'solidity'
        self.code_inline = code_inline
        self.language = language

    def view_title(self, tag, n):
        s = tag.get_text(strip=True)
        suf = "#" * n
        self.append(f"\n{suf} {s}\n", 'title', level=n)

    def view_url(self, tag):
        url = tag.attrs['href']
        self.append(f"[{tag.get_text(strip=True)}]({url})\n", itype='url')

    @staticmethod
    def text(tag, sep=''):
        return re.sub(r'\s+', ' ', tag.get_text(separator=sep, strip=True))

    def view_code(self, tag):
        data = self.text(tag)
        self.append(f"`{data}` \n", 'code')

    def view_img(self, tag):
        src = tag.attrs['src']
        self.append(data=f"![图片]({src})\n", itype='img')
        pass

    def append(self, data, itype, level=None):
        self.buff.append({'type': itype, 'level': level, 'data': data})
        pass

    def view_verse(self, tag):
        data = self.text(tag)
        if data == '\n':
            return
        self.append(f"{data}\n", itype='text')

    def hand_other(self, tag):
        for _, ch in enumerate(tag.children):
            if ch.name == 'a':
                self.view_url(ch)
                return
            if ch.name == 'img':
                self.view_img(ch)
                return
            if ch.name == 'span' and ('Consolas' in ch.attrs['style']):
                self.view_code(ch)
                return True
            self.view_verse(ch)

    def hand_p(self, tag):
        # name = tag.name
        attrs = tag.attrs
        if not attrs:
            return
        print("=" * 10)
        print("-----------attrs-----------")
        print(attrs)
        print("-----------text-----------")
        print(self.text(tag))

        if 'font-size:26pt' in attrs or 'text-align:center' in attrs:
            self.view_title(tag, 1)
        if 'font-size:18pt' in attrs['style']:
            self.view_title(tag, 2)
        if 'font-size:16pt' in attrs['style'] or 'margin-left:22.65pt' in attrs:
            self.view_title(tag, 3)
        if 'font-size:15pt' in attrs['style']:
            self.view_title(tag, 4)
        if 'font-size:14pt' in attrs['style']:
            self.view_title(tag, 5)
        if 'font-size' not in attrs['style']:
            self.code_flag = self.hand_other(tag)

    def view_tab(self, tag):
        for n, chi in enumerate(tag.find_all('tr')):
            data = self.text(chi, '|')
            lx = len(data.split('|'))
            if n == 0:
                self.append(data='\n\n', itype='tab')
            if n == 1:
                self.append(' --- '.join(['|' for _ in range(lx + 1)]) + '\n', 'tab')
            self.append(f"|{self.text(chi, '|')}|\n", itype='tab')
        self.append(data='\n\n', itype='tab')

    def merge(self, buf: list):
        def is_start(value: str) -> bool:
            fx = ['function', 'def', 'fun', 'class', 'fn']
            for x in fx:
                if x in value:
                    return True
            return False

        result = []
        temp = []
        flag = False
        for v in buf:
            data = v['data']
            itype = v['type']
            if data == '\n':
                continue
            if itype != 'code':
                if flag:
                    mg = f"```{self.language}\n"
                    for t in temp:
                        # mg += t.replace('`', '') + '\n'
                        mg += t.replace('`', '').replace('\n', '')
                        if self.code_inline:
                            mg += t.replace('`', '').replace('\n', '')
                        else:
                            mg += t.replace('`', '')

                    mg += '\n'
                    mg += "```\n"
                    result.append(mg)
                    temp.clear()
                    flag = False
                result.append(data)
            else:
                if is_start(value=data):
                    flag = True
                    temp.append(data)
                else:
                    if flag:
                        temp.append(data)
                    else:
                        result.append(data)
        return result

    def start(self):
        for i, div in enumerate(self.soup.find_all('div')):
            for j, child in enumerate(div.children):
                if child.name == 'p':
                    self.hand_p(child)
                    pass
                if child.name == 'table':
                    self.view_tab(child)

        result = ''.join(self.merge(self.buff))
        # f = open(self.outfile, 'w')
        # f.write(result)
        # f.close()
        return result


def handle(name: str, file: str):
    code_inline = pin['code_inline'] == '代码显示一行'
    language = pin['language']
    parse = Parse(file.encode(), code_inline, language)
    result = parse.start()
    out_name = pin['out_name']
    if not out_name:
        out_name = name.replace('html', 'md')

    put_file(name=out_name, content=result.encode(), label=f"下载{out_name}")
    put_code(content=result, language='md')


def html2md():
    put_info("1. 本工具将飞书导出的html文档解析成md\n2. md文件中的图片路径与源html中图片链接相同")
    put_input(name='out_name', label='输出文件名', help_text='可以为空,默认输出文件名与源文件相同')
    put_checkbox(name='check', label='解析内容', options=['图片', '超链接', '表格', '代码', '公式'],
                 value=['图片', '超链接', '表格', '代码', '公式'],
                 inline=True)
    put_radio(name='code_inline', label='代码块显示模式', options=['代码显示一行', '代码显示多行'], value='代码显示一行')
    put_radio(name='language', label='代码块语言', options=['solidity', 'javascript', 'golang', 'python', 'base'],
              value='solidity')
    f = file_upload(label='上传html文件', accept='.html', required=True, help_text='点击上传', max_size='10M',
                    helt_text="help text")
    handle(f['filename'], f['content'].decode())
