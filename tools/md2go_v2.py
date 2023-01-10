# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------
# Name:         b
# Author:       yepeng
# Date:         2021/10/22 2:44 下午
# Description: 
# -------------------------------------------------------------------------------
import time

import pywebio.input
from pywebio.output import *
from pywebio.pin import *

NILS = ['nil', 'None', 'none', 'empty', 'false']


def fail(msg: str, dur=4):
    toast(content=msg, duration=dur, color='red')


def success(msg='success', dur=3):
    toast(content=msg, duration=dur, color='green')


def show_result(data: str):
    file_name = f"parse_event.go"
    put_file(name=file_name, content=data.encode(), label=f"下载 {file_name}")
    put_code(content=data, language='go')
    #
    # tabs_code = []
    # tabs_load = []
    # for i, data in enumerate(datas):
    #     file_name = f"parse_{data['title'].lower()}.go"
    #     codes = put_code(content=data['content'], language='go')
    #     load = put_file(name=file_name, content=data['content'].encode(), label=f"下载 {file_name}")
    #     tabs_code.append({'title': file_name, 'content': codes})
    #     tabs_load.append(load)
    # put_row(tabs_load)
    # put_tabs(tabs=tabs_code)


# noinspection PyMethodMayBeStatic
class MarkDownParserV2(object):

    def __init__(self):
        self._pack_name = "YOUR_PACKAGE_NAME"
        self._snippet = []

    @property
    def pack_name(self):
        return self._pack_name

    @pack_name.setter
    def pack_name(self, pn: str):
        if not pn:
            self._pack_name = "YOUR_PACKAGE_NAME"
        self._pack_name = pn

    # # 类型转换3
    # def get_t(self, x: str):
    #     if x == 'address':
    #         return '(common.Address).String()'
    #     if x == 'uint256':
    #         return '(*big.Int)'
    #     if x == 'int256':
    #         return '(*big.Int)'
    #     if x == 'uint8':
    #         return '(uint8)'
    #     if x == 'uint16':
    #         return '(uint16)'
    #     if x == 'uint32':
    #         return '(uint32)'
    #     if x == 'uint64':
    #         return '(uint64)'
    #     if x == 'bool':
    #         return '(bool)'
    #     if x == 'systemParam':
    #         return '(uint8)'
    #     return 'UNKNOWN3'
    #
    # # 处理单行
    # def split_line(self, line: str) -> (str, int, list, list):
    #     ls = list(filter(lambda x: x != '',
    #                      line.replace(" ", "").replace("\n", "").replace('，', ',').replace('\\', '').split('|')))
    #     # ls = line.replace(' ', '').replace('\n', '').replace('，', ',').replace('\\', '').split('|')
    #     if len(ls) < 4:
    #         return None
    #     # 1 获取event 名称
    #     event_name = ls[0]
    #     # 2 获取event 相关itype
    #     type_id = int(ls[1].replace(' ', ''))
    #
    #     # 3 获取values 数组
    #     values = []
    #     for a in ls[2].split(','):
    #         if a and a.lower() not in NILS:
    #             values.append(a.replace('_', '')[0].upper() + a.replace('_', '')[1:])
    #
    #     # 4 获取values type 数组
    #     value_types = []
    #     for b in ls[3].split(','):
    #         if b and b.lower() not in NILS:
    #             value_types.append(b)
    #     if len(value_types) != len(values):
    #         raise Exception(f"value长度和type长度不一致,line: {line} L1={len(value_types)} L2{len(values)}")
    #     if not event_name:
    #         raise Exception(f"无法识别的EventName: {event_name} Line:{line}")
    #     if not type_id:
    #         raise Exception(f"无法识别的Itype: {type_id} Line:{line}")
    #     if len(ls) == 5:
    #         remarks = [a.replace('_', '')[0].upper() + a.replace('_', '')[1:] for a in ls[4].split(',')]
    #     else:
    #         remarks = []
    #     return event_name, type_id, values, value_types, remarks
    #
    # # 生成事件处理路由器
    # def gen_router(self, group_name, buff):
    #     class_name = self.class_name
    #     raw_model = self.raw_model
    #
    #     lk = '{'
    #     rk = '}'
    #     result = (
    #         f'func (task *{class_name}) handle{group_name}Event(event {raw_model}) {lk} \n'
    #         f'   itype := event.Itype\n'
    #         f'   sender := event.Sender\n'
    #         f'   log.DebugF("%s handle {group_name} Event group Sender:%s IType:%d", task.Tag(), sender, itype)\n'
    #         f'   switch itype {lk}\n'
    #     )
    #     for line in buff:
    #         event_name, type_id, values, value_types, remarks = self.split_line(line)
    #         result += f'       case {type_id}:\n'
    #         result += f'           task.parse{group_name}{event_name}(event)\n'
    #     result += f'       default:\n'
    #     result += f'           log.WarnF("sender: %s unknown itype: %d ", sender, itype)\n'
    #     result += f'   {rk}\n'
    #     result += f'{rk}\n'
    #     return result
    #
    # # noinspection PyShadowingNames
    # def split_head(self, line: str):
    #     ls = line.replace(' ', '').replace('\n', '').split('##')
    #     return list(filter(lambda a: a != '' and a != '##', ls))[0]
    #
    # # 生成event 结构体
    # # noinspection PyShadowingNames
    # def gen_struct(self, group_name, line) -> str:
    #     try:
    #         event_name, type_id, values, value_types, remarks = self.split_line(line)
    #         lk = '{'
    #         rk = '}'
    #         result = (
    #             f'type {group_name}{event_name} struct {lk}\n'
    #         )
    #
    #         for i, v in enumerate(values):
    #             name = v
    #             ftyle = self.hand_t(value_types[i])
    #             remark = remarks[i] if i < len(remarks) else ''
    #             result += f'  {name} {ftyle} // {remark}\n'
    #         result += f'{rk}\n'
    #         return result
    #     except Exception as e:
    #         raise Exception(f"生成结构体失败:{str(e)} line:{line}")
    #
    # # 3生成单事件解析器
    # def gen_parse(self, group_name, line):
    #     class_name = self.class_name
    #     raw_model = self.raw_model
    #
    #     lk = '{'
    #     rk = '}'
    #     event_name, type_id, values, value_types, remarks = self.split_line(line)
    #     # vs = ','.join(list(map(value_trans, values)))
    #     if len(values) == 0 or len(value_types) == 0:
    #         result = (
    #             f'func (task *{class_name}) parse{group_name}{event_name}(event {raw_model}) {lk}\n'
    #             f'   log.Debug(task.Tag(), event.BlockNumber, "find event: {group_name} {event_name}", "nil values")\n'
    #             f'   var receive = {group_name}{event_name}{lk}\n'
    #         )
    #     else:
    #         vts = ','.join(list(map(self.value_type_trans, value_types)))
    #         result = (
    #             f'func (task *{class_name}) parse{group_name}{event_name}(event {raw_model}) {lk}\n'
    #             f'   values, err := task.geneArgument({vts}).Unpack(event.Bvalue)\n'
    #             f'   if err != nil {lk}\n'
    #             f'       log.Error(task.Tag(), err.Error())\n'
    #             f'       return\n'
    #             f'   {rk}\n'
    #             f'   log.Debug(task.Tag(), event.BlockNumber, "find event: {group_name} {event_name}", values)\n'
    #             f'   var receive = {group_name}{event_name}{lk}\n'
    #             # f'       PoolToken:      values[0].(common.Address).String(),\n'
    #             # f'       DepositManager: values[1].(common.Address).String(),\n'
    #             # f'   {rk}\n'
    #             # f'task.saveEvent(event, receive)\n'
    #             # f'{rk}\n'
    #         )
    #     for i, v in enumerate(values):
    #         result += f'       {v}:      values[{i}].{self.get_t(value_types[i])},\n'
    #     # return f"// {sufix}{upper(event_name)} :\ntype {sufix}{upper(event_name)} struct {lk}\n    {fff}{rk}\n"
    #     result += f'   {rk}\n'
    #     result += f'   task.saveEvent(event, receive)\n'
    #     result += f'   task.save{group_name}{event_name}(event, receive)\n'
    #     result += f'{rk}\n'
    #     return result
    #
    # # 类型判断1
    # def hand_t(self, x: str):
    #     if x == 'address':
    #         return 'string'
    #     if x == 'uint256':
    #         return '*big.Int'
    #     if x == 'int256':
    #         return '*big.Int'
    #     if x == 'uint8':
    #         return 'uint8'
    #     if x == 'bool':
    #         return 'bool'
    #     if x == 'uint16':
    #         return 'uint16'
    #     if x == 'uint32':
    #         return 'uint32'
    #     if x == 'uint64':
    #         return 'uint64'
    #     if x == 'systemParam':
    #         return 'uint8'
    #     raise Exception(f"结构体解析错误，类型判断1失败，未知的类型参数 {x}")
    #
    # # 类型转化2
    # def value_type_trans(self, x: str):
    #     if x == 'address':
    #         return 'addressTy'
    #     if x == 'uint256':
    #         return 'uint256Ty'
    #     if x == 'int256':
    #         return 'int256Ty'
    #     if x == 'uint8':
    #         return 'uint8Ty'
    #     if x == 'uint16':
    #         return 'uint16Ty'
    #     if x == 'bool':
    #         return 'boolTy'
    #     if x == 'uint32':
    #         return 'uint32Ty'
    #     if x == 'uint64':
    #         return 'uint64Ty'
    #     if x == 'systemParam':
    #         return 'uint8Ty'
    #     raise Exception(f"事件解析器生成失败，类型判断2错误，未知的类型参数 {x}")
    #
    # # 处理event 组
    # def handle_event_group(self, group_name: str, buff: list, **kwargs):
    #     pack_name = self.pack_name
    #     if not group_name or not buff:
    #         return
    #     # 1 生产结构体 多个
    #     for line in buff:
    #         data1 = self.gen_struct(group_name, line)
    #         if data1:
    #             result += data1
    #
    #     return result

    def parse(self, file: str) -> str:
        pack_name = self.pack_name
        kwargs = {
            'pack_name': pack_name,
        }
        # 1 生成pack name
        self._appen(self._gen_packname())
        # 3 生成注释
        self._appen(self._gen_comment())
        # 2 生成import列表
        self._appen(self._gen_import())

        # 4 生成数字类型
        self._appen(self._gen_abitype())

        buff = []
        head = ""

        # for line in file.split('\n'):
        #     if line.startswith("-"):
        #         continue
        #     if line.startswith("## "):
        #         new_head = self.split_head(line)  #
        #         resu = self.handle_event_group(head, buff, **kwargs)
        #         if resu is not None:
        #             results.append({'title': head, 'content': resu})
        #
        #         buff.clear()  # 清空栈
        #         head = new_head
        #     if '|' in line and '-' not in line and 'EventName' not in line:
        #         line.replace(' ', '').replace('，', ',')
        #         buff.append(line)
        # resu = self.handle_event_group(head, buff, **kwargs)  # 缺乏结束标识符 强行处理一次buff
        # results.append({'title': head, 'content': resu})
        # buff.clear()
        return self.result()

    def _gen_packname(self):
        return f"package {self.pack_name}"

    @pack_name.setter
    def pack_name(self, value):
        self._pack_name = value

    def _appen(self, s):
        self._snippet.append(s)

    def _gen_comment(self):
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return f"""/**\n *@Author: yepeng\n *@Date: {t}\n *@Name: parse\n *@Desc:automatic generation of markdown file parser \n */"""

    def _gen_import(self):
        return 'import (\n\t"fmt"\n\t"github.com/ethereum/go-ethereum/accounts/abi"\n\t"github.com/ethereum/go-ethereum/common"\n\t"log"\n)'

    def _gen_abitype(self):
        s = """//goland:noinspection GoUnusedGlobalVariable
var (
	addressTy, _ = abi.NewType("address", "", nil)
	boolTy, _    = abi.NewType("bool", "", nil)
	uint8Ty, _   = abi.NewType("uint8", "", nil)
	uint16Ty, _  = abi.NewType("uint16", "", nil)
	uint32Ty, _  = abi.NewType("uint32", "", nil)
	uint64Ty, _  = abi.NewType("uint64", "", nil)
	uint256Ty, _ = abi.NewType("uint256", "", nil)
	int8Ty, _    = abi.NewType("int8", "", nil)
	int16Ty, _   = abi.NewType("int16", "", nil)
	int32Ty, _   = abi.NewType("int32", "", nil)
	int64Ty, _   = abi.NewType("int64", "", nil)
	int256Ty, _  = abi.NewType("int256", "", nil)
)

type Any = interface{}\n"""
        return s

    def result(self):
        return '\n\n'.join(self._snippet)


def handle():
    f = pywebio.input.file_upload(label='上传指定格式的md文件',
                                  accept='.md',
                                  required=True,
                                  help_text='点击上传',
                                  max_size='5M',
                                  helt_text="请输入描述合约日志文件的markdown文档(上限5M)")
    try:
        parser = MarkDownParserV2()
        parser.pack_name = pin['pack_name']
        results = parser.parse(f['content'].decode())
        success("解析成功！")
        show_result(results)
    except Exception as e:
        fail(str(e), dur=8)


def md2go_v2():
    put_info(
        "说明:\n1. 本工具将合约事件文件解析成go源代码\n2. 解析后生成事件结构体、事件组路由器、事件处理器三部分\n3. md文件由合约开发者提供，请使用统一规范\n4. 点击下载可下载go文件到本地")
    put_input(name='pack_name', type='text', label='包名', value='demo',
              help_text='生成go文件对应的包名')

    handle()

# def main():
#     view()
