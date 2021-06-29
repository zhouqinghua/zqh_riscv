#!/usr/bin/python3
import os
import getopt
import sys
import importlib
import re

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:', ['help', 'hex_in=', 'hex_out=', 'addr_min=', 'addr_max=', 'addr_base='])
    except getopt.GetoptError:
        print("argv error,please input")

    hex_in = ''
    hex_out = ''
    addr_min = 0
    addr_max = 0
    addr_base = None

    for (k,v) in opts:
        if (k == '--hex_in'):
            hex_in = v
        elif (k == '--hex_out'):
            hex_out = v
        elif (k == '--addr_min'):
            addr_min = int(v, 16)
        elif (k == '--addr_max'):
            addr_max = int(v, 16)
        elif (k == '--addr_base'):
            addr_base = int(v, 16)
        else:
            assert(0), 'illegal prameter name: %s' %(k)

    in_fn = hex_in
    in_f = open(in_fn, 'r')
    in_hex = in_f.readlines()
    in_f.close()

    address = 0
    data = []
    out_hex = []
    for i in in_hex:
        mobj = re.match(r'^@(\w+)',i)
        if (mobj != None):
            #print(mobj.group(1))
            address = int(mobj.group(1), 16)
            #print('%x' %(address))
        else:
            if ((addr_max == 0) or (address >= addr_min and address < addr_max)):
                data = i.split()
                for j in range(len(data)):
                    #print('@%x\n%s' % (address, data[j]))
                    if (addr_base is None):
                        new_address = address
                    else:
                        new_address = address + addr_base
                    out_hex.append('@%x\n%s\n' % (new_address, data[j]))
                    address += 1

    if (hex_out == ''):
        out_fn = in_fn + '.fix'
    else:
        out_fn = hex_out
    out_f = open(out_fn, 'w')
    out_f.writelines(out_hex)
    out_f.close()

    print("generate %s" %(out_fn))


if __name__ == "__main__":
    main()
