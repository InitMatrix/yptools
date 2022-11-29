# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         a 
# Author:       yepeng
# Date:         2021/10/22 2:44 下午
# Description: 
# -------------------------------------------------------------------------------
import pywebio.input
from pywebio.output import *
from pywebio.pin import *


def fail(msg: str, dur=4):
    toast(content=msg, duration=dur, color='red')


def success(msg='success', dur=3):
    toast(content=msg, duration=dur, color='green')


def show_result(datas: list):
    tabs_code = []
    tabs_load = []
    for i, data in enumerate(datas):
        file_name = f"parse_{data['title'].lower()}.go"
        codes = put_code(content=data['content'], language='go')
        load = put_file(name=file_name, content=data['content'].encode(), label=f"下载 {file_name}")
        tabs_code.append({'title': file_name, 'content': codes})
        tabs_load.append(load)
    put_row(tabs_load)
    put_tabs(tabs=tabs_code)


# noinspection PyMethodMayBeStatic
class MarkDownParser(object):

    def __init__(self, pack_name, class_name, raw_model, enable_struct=True, enable_route=True,
                 enable_event_parse=True, enable_save_func=True):
        self.pack_name = pack_name
        self.class_name = class_name
        self.raw_model = raw_model
        self.enable_struct = enable_struct
        self.enable_route = enable_route
        self.enable_event_parse = enable_event_parse
        self.enable_save_func = enable_save_func

    # 类型转换3
    def get_t(self, x: str):
        if x == 'address':
            return '(common.Address).String()'
        if x == 'uint256':
            return '(*big.Int)'
        if x == 'int256':
            return '(*big.Int)'
        if x == 'uint8':
            return '(uint8)'
        if x == 'uint16':
            return '(uint16)'
        if x == 'uint32':
            return '(uint32)'
        if x == 'uint64':
            return '(uint64)'
        if x == 'bool':
            return '(bool)'
        if x == 'systemParam':
            return '(uint8)'
        return 'UNKNOWN3'

    # 处理单行
    def split_line(self, line: str) -> (str, int, list, list):
        ls = list(filter(lambda x: x != '',
                         line.replace(" ", "").replace("\n", "").replace('，', ',').replace('\\', '').split('|')))
        if len(ls) < 4:
            return None
        event_name = ls[0]
        type_id = int(ls[1].replace(' ', ''))
        values = [a.replace('_', '')[0].upper() + a.replace('_', '')[1:] for a in ls[2].split(',')]
        value_types = ls[3].split(',')
        if len(ls) == 5:
            remarks = [a.replace('_', '')[0].upper() + a.replace('_', '')[1:] for a in ls[4].split(',')]
        else:
            remarks = []
        return event_name, type_id, values, value_types, remarks

    # 生成事件处理路由器
    def gen_router(self, group_name, buff):
        class_name = self.class_name
        raw_model = self.raw_model

        lk = '{'
        rk = '}'
        result = (
            f'func (task *{class_name}) handle{group_name}Event(event model.{raw_model}) {lk} \n'
            f'   itype := event.Itype\n'
            f'   sender := event.Sender\n'
            f'   log.DebugF("%s handle {group_name} Event group Sender:%s IType:%d", task.Tag(), sender, itype)\n'
            f'   switch itype {lk}\n'
        )
        for line in buff:
            event_name, type_id, values, value_types, remarks = self.split_line(line)
            result += f'       case {type_id}:\n'
            result += f'           task.parse{group_name}{event_name}(event)\n'
        result += f'       default:\n'
        result += f'           log.WarnF("sender: %s unknown itype: %d ", sender, itype)\n'
        result += f'   {rk}\n'
        result += f'{rk}\n'
        return result

    # noinspection PyShadowingNames
    def split_head(self, line: str):
        ls = line.replace(' ', '').replace('\n', '').split('##')
        return list(filter(lambda a: a != '' and a != '##', ls))[0]

    # 生成event 结构体
    # noinspection PyShadowingNames
    def gen_struct(self, group_name, line) -> str:
        event_name, type_id, values, value_types, remarks = self.split_line(line)
        lk = '{'
        rk = '}'
        result = (
            f'type {group_name}{event_name} struct {lk}\n'
        )
        if len(values) != len(value_types):
            raise Exception(
                f"{group_name} {event_name}解析失败:\nvalues:{values}\nvalue_types{value_types}\nremarks{remarks}")
        for i, v in enumerate(values):
            name = v
            ftyle = self.hand_t(value_types[i])
            remark = remarks[i] if i < len(remarks) else ''
            result += f'  {name} {ftyle} // {remark}\n'
        result += f'{rk}\n'
        return result

    # 3生成单事件解析器
    def gen_parse(self, group_name, line):
        class_name = self.class_name
        raw_model = self.raw_model

        lk = '{'
        rk = '}'
        event_name, type_id, values, value_types, remarks = self.split_line(line)
        # vs = ','.join(list(map(value_trans, values)))
        vts = ','.join(list(map(self.value_type_trans, value_types)))
        result = (
            f'func (task *{class_name}) parse{group_name}{event_name}(event model.{raw_model}) {lk}\n'
            f'   values, err := task.geneArgument({vts}).Unpack(event.BValue)\n'
            f'   if err != nil {lk}\n'
            f'       log.Error(task.Tag(), err.Error())\n'
            f'       return\n'
            f'   {rk}\n'
            f'   log.Debug(task.Tag(), event.BlockNumber, "find event: {group_name} {event_name}", values)\n'
            f'   var receive = {group_name}{event_name}{lk}\n'
            # f'       PoolToken:      values[0].(common.Address).String(),\n'
            # f'       DepositManager: values[1].(common.Address).String(),\n'
            # f'   {rk}\n'
            # f'task.saveEvent(event, receive)\n'
            # f'{rk}\n'
        )
        for i, v in enumerate(values):
            result += f'       {v}:      values[{i}].{self.get_t(value_types[i])},\n'
        # return f"// {sufix}{upper(event_name)} :\ntype {sufix}{upper(event_name)} struct {lk}\n    {fff}{rk}\n"
        result += f'   {rk}\n'
        result += f'   task.saveEvent(event, receive)\n'
        result += f'   task.save{group_name}{event_name}(event, receive)\n'
        result += f'{rk}\n'
        return result

    def gen_save(self, group_name, line):
        class_name = self.class_name
        raw_model = self.raw_model

        lk = '{'
        rk = '}'
        event_name, type_id, values, value_types, remarks = self.split_line(line)
        result = (
            f'func (task *{class_name}) save{group_name}{event_name}(event model.{raw_model},receive {group_name}{event_name}) {lk}\n'
            f'{rk}\n'
        )
        return result

    # 类型判断1
    def hand_t(self, x: str):
        if x == 'address':
            return 'string'
        if x == 'uint256':
            return '*big.Int'
        if x == 'int256':
            return '*big.Int'
        if x == 'uint8':
            return 'uint8'
        if x == 'bool':
            return 'bool'
        if x == 'uint16':
            return 'uint16'
        if x == 'uint32':
            return 'uint32'
        if x == 'uint64':
            return 'uint64'
        if x == 'systemParam':
            return 'uint8'
        raise Exception(f"未知的类型参数 {x}")

    # 类型转化2
    def value_type_trans(self, x: str):
        if x == 'address':
            return 'addressTy'
        if x == 'uint256':
            return 'uint256Ty'
        if x == 'int256':
            return 'uint256Ty'
        if x == 'uint8':
            return 'uint8Ty'
        if x == 'uint16':
            return 'uint16Ty'
        if x == 'bool':
            return 'boolTy'
        if x == 'uint32':
            return 'uint32Ty'
        if x == 'uint64':
            return 'uint64Ty'
        if x == 'systemParam':
            return 'uint8Ty'
        return 'UNKNOWN2'

    # 处理event 组
    def handle_event_group(self, group_name: str, buff: list, **kwargs):
        pack_name = self.pack_name
        if not group_name or not buff:
            return
        result = f'package {pack_name}\n'
        # 1 生产结构体 多个
        if self.enable_struct:
            for line in buff:
                data1 = self.gen_struct(group_name, line)
                result += data1

        if self.enable_route:
            # 2 生成handle router 单个
            data2 = self.gen_router(group_name, buff)
            result += data2

        if self.enable_event_parse:
            # 3 生成解析event方法 多个
            for line in buff:
                data3 = self.gen_parse(group_name, line)
                result += data3
        if self.enable_save_func:
            # 3 生成解析event方法 多个
            for line in buff:
                data4 = self.gen_save(group_name, line)
                result += data4
        return result

    def parse(self, file: str) -> list:
        results = []
        pack_name = self.pack_name
        class_name = self.class_name
        raw_model = self.raw_model
        kwargs = {
            'pack_name': pack_name,
            'class_name': class_name,
            'raw_model': raw_model,
        }
        buff = []
        head = ""
        for line in file.split('\n'):
            if line.startswith("-"):
                continue
            if line.startswith("## "):
                new_head = self.split_head(line)  #
                resu = self.handle_event_group(head, buff, **kwargs)
                if resu is not None:
                    results.append({'title': head, 'content': resu})

                buff.clear()  # 清空栈
                head = new_head
            if '|' in line and '-' not in line and 'EventName' not in line:
                line.replace(' ', '').replace('，', ',')
                buff.append(line)
        resu = self.handle_event_group(head, buff, **kwargs)  # 缺乏结束标识符 强行处理一次buff
        results.append({'title': head, 'content': resu})
        buff.clear()
        return results


def handle():
    f = pywebio.input.file_upload(label='上传指定格式的md文件', accept='.md', required=True, help_text='点击上传',
                                  max_size='5M',
                                  helt_text="help text")
    try:
        pack_name = pin['pack_name']
        class_name = pin['class_name']
        raw_model = pin['raw_model']
        enable_struct = (1 in pin['enable'])
        enable_route = (2 in pin['enable'])
        enable_event_parse = (3 in pin['enable'])
        enable_save_func = (4 in pin['enable'])
        parser = MarkDownParser(pack_name, class_name, raw_model,
                                enable_struct=enable_struct,
                                enable_route=enable_route,
                                enable_event_parse=enable_event_parse,
                                enable_save_func=enable_save_func
                                )
        results = parser.parse(f['content'].decode())
        success("解析成功！")
        show_result(results)
    except Exception as e:
        fail(str(e), dur=6)


def md2go():
    put_info(
        "说明:\n1. 上传指定格式md文件，解析成go源码\n2. 解析后生成事件结构体、事件组路由器、事件处理器三部分\n3. 升级：支持无序字符\n 点击下载可下载go文件到本地")
    put_input(name='pack_name', type='text', label='包名', value='serve_pve',
              help_text='生成go文件对应的包名')
    put_input(name='class_name', type='text', label='方法的接收指针', value='ParsePveTask',
              help_text='任务结构体名称')
    put_input(name='raw_model', type='text', value='PveRaw', label='原始数据来源',
              help_text='存储原始event数据的结构体名称')

    put_checkbox(name='enable', options=[
        {
            "label": '生成结构体',
            "value": 1,
            "selected": True,
        },
        {
            "label": '生成事件路由器',
            "value": 2,
            "selected": True,
        },
        {
            "label": '生成事件解析内容',
            "value": 3,
            "selected": True,
        },
        {
            "label": '生成子事件内容',
            "value": 4,
            "selected": True,
        }
    ],
                 label='生成代码选项', help_text='默认生成全套代码')

    handle()

# def main():
#     view()
