from idautils import *
from idaapi import *
import csv
import json


def get_func_for_build():
    func_name = set()
    with open('func_list.csv', 'r') as f:
        r = csv.reader(f, delimiter=',')
        for row in r:
            func_name.add(row[-1])
    return func_name

def dump_function_details(ea):
    disasm = dict()
    cnt = 0

    for bb in FlowChart(get_func(ea), flags=FC_PREDS):
        if bb.start_ea != bb.end_ea:
            bb_disasm = []
            for head in Heads(bb.start_ea, bb.end_ea):
                bb_disasm.append(GetDisasm(head))

            preds_list = []
            if bb.preds():
                for preds_bb in bb.preds():
                    preds_list.append(preds_bb.start_ea)

            succs_list = []
            if bb.succs():
                for succs_bb in bb.succs():
                    succs_list.append(succs_bb.start_ea)

            disasm[bb.start_ea] = {
                'disasm': bb_disasm,
                'preds': preds_list,
                'succs': succs_list
            }
            cnt += 1

    if cnt > 5:
        return disasm
    else:
        return None


file_name = get_root_filename()

procname = get_inf_structure().procname.lower()
disasm_dic = {'arch': procname}

# for reference
if 'fw' not in file_name:
    func_name = get_func_for_build()
    found_func = set()
    for ea in Functions():
        name = get_func_name(ea)
        if name in func_name:
            disasm = dump_function_details(ea)
            if disasm:
                disasm_dic[name] = disasm
                found_func.add(name)
                print(name, 'done')
            else:
                print('Skip', name, 'less than five basic blocks')
    print('Extracted', len(found_func), '/', len(func_name))
    print('Cannot extract', func_name - found_func)
# for firmware
else:
    func_cnt = 0
    for ea in Functions():
        name = get_func_name(ea)
        disasm = dump_function_details(ea)
        if disasm:
            disasm_dic[name] = disasm
            func_cnt += 1
    disasm_dic['num'] = func_cnt
    print(func_cnt, 'done')

disasm_json = json.dumps(disasm_dic)
with open('../output/' + file_name + '_disasm.json', 'w') as f:
    f.write(disasm_json)