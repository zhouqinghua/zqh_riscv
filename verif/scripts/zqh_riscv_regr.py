#!/usr/bin/python3
import os
import getopt
import sys
import importlib
import re

def main():
    print(sys.argv)
    try:
        #opts, args = getopt.getopt(sys.argv[1:], "hi:m:o:p:", ["help", "inputfile=", "module=", "outputpath=", "project=", "cfgfile=", "cfg="])
        opts, args = getopt.getopt(sys.argv[1:], 'h:', ['help', 'cmd=', 'sw_root_dir=', 'sw_tc_grp_dir=', 'sw_tc_dir=', 'sw_tc=', 'gcc_xlen=', 'gcc_isa=', 'wave='])
    except getopt.GetoptError:
        print("argv error,please input")

    params = {}
    params['cmd'] = 'all'
    params['sw_root_dir'] = '../tests/zqh_riscv_sw'
    params['sw_tc_grp_dir'] = 'isa'
    params['sw_tc_dir'] = 'rv64ui'
    params['sw_tc'] = 'p-add'
    params['gcc_xlen'] = '64'
    params['gcc_isa'] = 'gc'
    params['wave'] = 'fsdb'

    print(opts)
    for (k,v) in opts:
        if (k == '--cmd'):
            params['cmd'] = v
        elif (k == '--sw_root_dir'):
            params['sw_root_dir'] = v
        elif (k == '--sw_tc_dir'):
            params['sw_tc_dir'] = v
        elif (k == '--sw_tc_grp_dir'):
            params['sw_tc_grp_dir'] = v
        elif (k == '--sw_tc'):
            params['sw_tc'] = v
        elif (k == '--gcc_xlen'):
            params['gcc_xlen'] = v
        elif (k == '--gcc_isa'):
            params['gcc_isa'] = v
        elif (k == '--wave'):
            params['wave'] = v
        else:
            assert(0), 'illegal prameter name: %s' %(n)

        # if n in ("-p","--project"):
        #     project = v
        # elif n in ("-i","--inputfile"):
        #     #print(n,v)
        #     inputfile = v
        # elif n in ("-o","--outputpath"):
        #     #print(n,v)
        #     outputpath= v
        # elif n in ("-m","--module"):
        #     #print(n,v)
        #     module_name = v
        # elif n in ("--cfg"):
        #     print(n,v)
        #     cfg_name = v
        # elif n in ("--cfgfile"):
        #     print(n,v)
        #     cfgfile = v
        # else:
        #     assert(0), "illegal prameter name: %s" %(n)

    make_cmd_ret = 0
    make_cmd = 'make'

    #make_cmd += ' ' + params['cmd']
    for i in params:
        print((i, params[i]))
        if (i != 'cmd' and i != 'sw_tc'):
            make_cmd += ' ' + i + '=' + params[i]

    #tmp if (params['cmd'] == 'all'):
    #tmp     #make_cmd_ret = os.system('make all')
    #tmp     make_cmd += ' all'
    #tmp elif (params['cmd'] == 'gen_rtl'):
    #tmp     make_cmd += ' gen_rtl'

    if (params['sw_tc_grp_dir'] == 'isa' and params['sw_tc'] == 'p-all'):
        isa_tc_dir_list = os.listdir('%s/%s/%s' % (params['sw_root_dir'], params['sw_tc_grp_dir'], params['sw_tc_dir']))
        isa_tc_list = list(map(lambda _: _.group(1), filter(lambda _ : _ is not None, map(lambda _: re.match(r'(.*)\.S', _), isa_tc_dir_list))))
        #print(isa_tc_list)
        if (params['cmd'] == 'all'):
            cur_cmd = make_cmd + ' gen_rtl'
            os.system(cur_cmd)
            cur_cmd = make_cmd + ' cmp'
            os.system(cur_cmd)
        elif (params['cmd'] == 'gen_rtl'):
            cur_cmd = make_cmd + ' gen_rtl'
            os.system(cur_cmd)
            cur_cmd = make_cmd + ' cmp'
            os.system(cur_cmd)
        elif (params['cmd'] == 'cmp'):
            cur_cmd = make_cmd + ' cmp'
            os.system(cur_cmd)
        #print('cur_cmd: %s' % cur_cmd)
        for i in isa_tc_list:
            cur_cmd = make_cmd + ' sw_sim' + ' sw_tc=p-%s' % (i)
            #print('cur_cmd: %s' % cur_cmd)
            os.system(cur_cmd)
    else:
        cur_cmd = make_cmd + ' ' + params['cmd'] + ' sw_tc=%s' % (params['sw_tc'])
        print('cur_cmd: %s' % cur_cmd)
        os.system(cur_cmd)

    #input_split = os.path.splitext(inputfile)
    #input_split = os.path.split(input_split[0])
    #sys.path.append(input_split[0])
    #sys.path.append(input_split[0]+'/../')

if __name__ == "__main__":
    main()
