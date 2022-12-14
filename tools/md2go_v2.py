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

NILS = ['nil', 'none', 'empty', 'null', 'false']


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

    # 处理单行
    def split_line(self, line: str) -> (str, int, list, list):
        ls = list(filter(lambda x: x != '',
                         line.replace(" ", "").replace("\n", "").replace('，', ',').replace('\\', '').split('|')))
        # ls = line.replace(' ', '').replace('\n', '').replace('，', ',').replace('\\', '').split('|')
        if len(ls) < 4:
            return None
        # 1 获取event 名称
        event_name = ls[0]
        # 2 获取event 相关itype
        type_id = int(ls[1].replace(' ', ''))
        # 3 获取values 数组
        values = []
        for a in ls[2].split(','):
            if a and a.lower() not in NILS:
                values.append(a.replace('_', '')[0].upper() + a.replace('_', '')[1:])

        # 4 获取values type 数组
        value_types = []
        for b in ls[3].split(','):
            if b and b.lower() not in NILS:
                value_types.append(b)
        if len(value_types) != len(values):
            raise Exception(f"value长度和type长度不一致,line: {line} L1={len(value_types)} L2{len(values)}")
        if not event_name:
            raise Exception(f"EventName不能为空: Line:{line}")
        if type_id <= 0:
            raise Exception(f"Itype不能<=0: Line:{line}")
        if len(ls) == 5:  # 有remarks的时候处理remarks，没有就不处理
            remarks = [a.replace('_', '')[0].upper() + a.replace('_', '')[1:] for a in ls[4].split(',')]
        else:
            remarks = []
        return event_name, type_id, values, value_types, remarks

    # noinspection PyShadowingNames
    def _split_head(self, line: str):
        ls = line.replace(' ', '').replace('\n', '').split('##')
        return list(filter(lambda a: a != '' and a != '##', ls))[0]

    def parse(self, file: str) -> str:
        # 1 生成注释
        self._appen(self._gen_comment())
        # 2 生成pack name
        self._appen(self._gen_packname())
        # 3 生成import列表
        self._appen(self._gen_import())
        # 4 生成数字类型
        self._appen(self._gen_abitype())
        # 5 生成字段解析工具
        self._appen(self._gen_argument())
        # 解析获取event字典表
        data = self._gen_event_map(file)
        # print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
        # 生成IParser接口
        self._appen(self._gen_interface(data))
        # 生成结构体
        self._appen(self._gen_struct(data))
        # 生成类parse
        self._appen(self._gen_parse(data))

        return self._handle_result()

    def _gen_packname(self):
        return f"package {self.pack_name}"

    @pack_name.setter
    def pack_name(self, value):
        self._pack_name = value

    def _appen(self, s):
        self._snippet.append(s)

    def _gen_comment(self):
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return f"""// Code generated by protoc-gen-go. DO NOT EDIT.\n// Versions:v2\n// Author: yepeng\n// Date: 2023-01-11 15:25:32\n// Name: parse\n// Desc:automatic generation of markdown file parser"""

    def _gen_import(self):
        return 'import (\n\t"github.com/ethereum/go-ethereum/accounts/abi"\n\t"github.com/ethereum/go-ethereum/common"\n\t"math/big"\n)'

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
)"""
        return s

    def _handle_result(self):
        return '\n\n'.join(self._snippet)

    def _gen_argument(self) -> str:
        s = """func geneArgument(tys ...abi.Type) abi.Arguments {
	argument := abi.Arguments{}
	for _, v := range tys {
		argument = append(argument, abi.Argument{Type: v})
	}
	return argument
}"""
        return s

    def _gen_event_map(self, file):
        cursor = str()
        data = dict()

        for line in file.split('\n'):
            if line.startswith("-"):
                continue
            if line.startswith("## "):  # 发现事件组
                cursor = self._split_head(line)
                data[cursor] = list()  # 发现事件组后，初始化一个新的合集

            if '|' in line and '-' not in line and 'EventName' not in line:  # 这是有价值数据的普通一行
                line = line.replace(' ', '').replace('，', ',')
                event_name, type_id, values, value_types, remarks = self.split_line(line)
                data[cursor].append({
                    "event_name": event_name,
                    "itype": type_id,
                    "values": values,
                    "value_types": value_types,
                    "remarks": remarks
                })
        return data

    # 生成接口
    def _gen_interface(self, data: dict):
        buff = list()
        buff.append('// IParser :interface of parse client\ntype IParser interface {')
        for group, events in data.items():
            for e in events:
                s = f"	Parse{group}{e['event_name']}(value []byte) (*{group}{e['event_name']}, error)"
                buff.append(s)
        buff.append('}')
        return '\n'.join(buff)

    # 结构体类型判断
    def _hand_t(self, x: str):
        if x == 'address':
            return 'string'
        if x == 'bool':
            return 'bool'

        if x == 'uint8':
            return 'uint8'
        if x == 'int8':
            return 'int8'

        if x == 'uint16':
            return 'uint16'
        if x == 'int16':
            return 'int16'

        if x == 'uint32':
            return 'uint32'
        if x == 'int32':
            return 'int32'

        if x == 'uint64':
            return 'uint64'
        if x == 'int64':
            return 'int64'

        if x == 'uint256' or x == 'int256':
            return '*big.Int'

        if x == 'systemParam':
            return 'uint8'
        raise Exception(f"结构体解析错误，类型判断1失败，未知的类型参数 {x}")

    # 类型转化2
    def _value_type_trans(self, x: str):
        if x == 'address':
            return 'addressTy'
        if x == 'bool':
            return 'boolTy'
        if x == 'uint256':
            return 'uint256Ty'
        if x == 'int256':
            return 'int256Ty'
        if x == 'uint8':
            return 'uint8Ty'
        if x == 'int8':
            return 'int8Ty'
        if x == 'uint16':
            return 'uint16Ty'
        if x == 'int16':
            return 'int16Ty'

        if x == 'uint32':
            return 'uint32Ty'
        if x == 'int32':
            return 'int32Ty'
        if x == 'uint64':
            return 'uint64Ty'
        if x == 'int64':
            return 'int64Ty'
        if x == 'systemParam':
            return 'uint8Ty'
        raise Exception(f"事件解析器生成失败，类型判断2错误，未知的类型参数 {x}")

    # 类型转换3
    def _get_t(self, x: str):
        if x == 'address':
            return '(common.Address).String()'
        if x == 'bool':
            return '(bool)'
        if x == 'uint256':
            return '(*big.Int)'
        if x == 'int256':
            return '(*big.Int)'
        if x == 'uint8':
            return '(uint8)'
        if x == 'int8':
            return '(int8)'
        if x == 'uint16':
            return '(uint16)'
        if x == 'int16':
            return '(int16)'
        if x == 'uint32':
            return '(uint32)'
        if x == 'int32':
            return '(int32)'
        if x == 'uint64':
            return '(uint64)'
        if x == 'int64':
            return '(int64)'
        if x == 'systemParam':
            return '(uint8)'
        return 'UNKNOWN3'

    #  生成结构体
    def _gen_struct(self, data: dict):
        a = '{'
        b = '}'
        buff = list()
        for group, events in data.items():
            for e in events:
                event_name = e['event_name']
                # itype = e['itype']
                values = e['values']
                value_types = e['value_types']
                remarks = e['remarks']

                buff.append(f"// {group}{event_name} : struct of event <{event_name}> in group <{group}>")
                buff.append(f"type {group}{event_name} struct {a}")
                # buff.append(f"	PoolToken      string // 底池币的地址")
                for i, v in enumerate(values):
                    name = v
                    ftyle = self._hand_t(value_types[i])
                    remark = remarks[i] if i < len(remarks) else ''
                    buff.append(f'\t{name} {ftyle} // {remark}')
                buff.append(f"{b}\n")
        return '\n'.join(buff)

    def _gen_parse(self, data: dict):
        a = '{'
        b = '}'
        buff = list()
        cls = "// NewParser :constructor\nfunc NewParser() IParser {\n\treturn &parse{}\n}\ntype parse struct {}\n"
        buff.append(cls)
        for group, events in data.items():
            for e in events:
                event_name = e['event_name']
                # itype = e['itype']
                values = e['values']
                value_types = e['value_types']
                # remarks = e['remarks']
                if len(values) == 0 or len(value_types) == 0:
                    buff.append(
                        f'func (p *parse) Parse{group}{event_name}(bValue []byte) (*{group}{event_name}, error) {a}')
                    buff.append(f'\tvar receive = {group}{event_name}{a}{b}\n')
                    buff.append("\treturn &receive, nil")
                    buff.append(b)
                else:
                    vts = ','.join(list(map(self._value_type_trans, value_types)))
                    buff.append(f"// Parse{group}{event_name} : parse event <{event_name}> in group <{group}>")
                    buff.append(
                        f'func (p *parse) Parse{group}{event_name}(bValue []byte) (*{group}{event_name}, error) {a}')
                    buff.append(f'\tvalues, err := geneArgument({vts}).Unpack(bValue)')
                    buff.append(f'\tif err != nil {a}')
                    buff.append(f'\t\treturn nil, err')
                    buff.append(f'\t{b}')
                    buff.append(f'\tvar receive = {group}{event_name}{a}')
                    for i, v in enumerate(values):
                        buff.append(f'\t\t{v}:\tvalues[{i}].{self._get_t(value_types[i])},')
                    buff.append(f"\t{b}")
                    buff.append("\treturn &receive, nil")
                    buff.append(f"{b}\n")

        return '\n'.join(buff)

    def _gen_mark(self):
        return f"// Code generated by protoc-gen-go. DO NOT EDIT.\n// versions:v2"


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
        "说明:\n1. 本工具将合约事件文件解析成go源代码\n2.非侵入，不建议编辑自动生成的文件\n3. 兼容大小写、部分中英文标点、空置event\n4. 点击下载可下载go文件到本地")
    help_code = """package main

func main() {
	//1. 构造解析器
	parser := NewParser()
	//2. 从本地或远程获取raw event数据
	sender := "0xababababababababababababababababababfuck"
	itype := 1
	bvalue := make([]byte, 0, 0)

	//3. 判断RawEvent的Sender和Itype字段
	switch sender {
	case "0xababababababababababababababababababfuck":
		switch itype {
		case 1:
			//4. 根据sender 和itype 路由到不同的解析方法，输入bValue,输出解析后的结构体数据
			createPool, err := parser.ParseFactoryCreatePool(bvalue)
			if err != nil {
				return
			}
			print(createPool) //5. 处理解析后的数据
		}
	}
}"""
    put_code(content=help_code, language='go')
    put_input(name='pack_name', type='text', label='包名', value='pack_name',
              help_text='生成go文件对应的包名')

    handle()
