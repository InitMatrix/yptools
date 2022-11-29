# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         a 
# Author:       yepeng
# Date:         2021/10/22 2:44 下午
# Description: 
# -------------------------------------------------------------------------------

from pywebio.output import put_link


def main():
    put_link('Go task 1', app='md2go.md')  # Use `app` parameter to specify the task name
