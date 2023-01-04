# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         a 
# Author:       yepeng
# Date:         2021/10/22 2:44 下午
# Description: 
# -------------------------------------------------------------------------------


ls = ""
print(ls.split(','))
# s = [a.replace('_', '')[0].upper() + a.replace('_', '')[1:] if a else None for a in ls.split(',')]
# s = [a for a in ls.split(',')]
v = []
for a in ls:
    print(a)
    if a:
        v.append(a.replace('_', '')[0].upper() + a.replace('_', '')[1:])
print(v)
