#!/usr/bin/python3
import os
import getopt
import sys
import importlib
import re
import subprocess

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:', ['help', 'elf_in=', 'hex_out='])
    except getopt.GetoptError:
        print("argv error,please input")

    elf_in = ''
    hex_out = ''

    for (k,v) in opts:
        if (k == '--elf_in'):
            elf_in = v
        elif (k == '--hex_out'):
            hex_out = v
        else:
            assert(0), 'illegal prameter name: %s' %(k)


    cmd = 'riscv64-unknown-elf-readelf -S -W %s' % (elf_in)
    (status, ret) = subprocess.getstatusoutput(cmd)
    if status == 0:
        print('[SUCCESS] %s' % cmd)
    else:
        print('[ERROR] %s' % cmd)
        print(ret)
    #print(ret)
    ret_list = ret.split('\n')
    sec_attr_list = []
    for i in ret_list :
        print(i)
        mobj = re.match(r'^\s+\[\s*\d+\]\s+(\.[.\w]+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s*$',i)
        if (mobj != None):
            #print(mobj.group(1))
            #print(mobj.group(3))
            #print(mobj.group(5))
            #print(mobj.group(7))
            if (mobj.group(7) != 'MS'):
                #name, type, address, size, flg
                sec_attr_list.append((mobj.group(1), mobj.group(2), mobj.group(3), mobj.group(5), mobj.group(7)))
    #for i in sec_attr_list:
    #    print(i)
    #    if (i[0] == '.bss' or i[0] == '.tbss'):
    #        pass
    #    else:
    #        sec_size = int(i[2], 16)
    #        if (sec_size == 0):
    #            pass
    #        else:
    #            hex_fn = elf_in+'.section'+i[0]+'.hex'
    #            cmd = 'riscv64-unknown-elf-objcopy -O verilog -j %s %s %s' %(i[0], elf_in, hex_fn)
    #            (status, ret) = subprocess.getstatusoutput(cmd)
    #            if status == 0:
    #                print('[SUCCESS] %s' % cmd)

    #                cmd = '../../scripts/zqh_sw_hex_fix.py --hex_in=%s' %(hex_fn)
    #                (fix_status, fix_ret) = subprocess.getstatusoutput(cmd)
    #                if fix_status == 0:
    #                    print('[SUCCESS] %s' % cmd)
    #                else:
    #                    print('[ERROR] %s' % cmd)
    #                    print(fix_ret)
    #            else:
    #                print('[ERROR] %s' % cmd)
    #                print(ret)
    cmd = 'riscv64-unknown-elf-objcopy -O verilog'
    for i in sec_attr_list:
        print(i)
        cmd = cmd + ' -j %s' %(i[0])
    hex_fn = elf_in+'.section'+'.hex'
    cmd = '%s %s %s' %(cmd, elf_in, hex_fn)
    (status, ret) = subprocess.getstatusoutput(cmd)
    if status == 0:
        print('[SUCCESS] %s' % cmd)
    else:
        print('[ERROR] %s' % cmd)
        print(ret)

    elf_path = os.path.splitext(elf_in)[0]
    flash_img_path = os.path.split(elf_path)[0]

    #all img info: rom and ram
    flash_img_fn = flash_img_path + '/' + 'flash_main_img.hex.fix'
    cmd = '../../scripts/zqh_sw_hex_fix.py --hex_in=%s --hex_out=%s' %(hex_fn, flash_img_fn)
    (status, ret) = subprocess.getstatusoutput(cmd)
    if status == 0:
        print('[SUCCESS] %s' % cmd)
    else:
        print('[ERROR] %s' % cmd)
        print(ret)

    system_flash_mem_base = 0x20000000
    system_flash_mem_top = 0x2fffffff
    system_ram_mem_base = 0x40000000
    system_ram_mem_top = 0xbfffffff

    #rom img info
    flash_img_fn = flash_img_path + '/' + 'flash_main_img.hex.rom.fix'
    cmd = '../../scripts/zqh_sw_hex_fix.py --addr_min=0x%x --addr_max=0x%x --hex_in=%s --hex_out=%s' %(system_flash_mem_base, system_flash_mem_top+1, hex_fn, flash_img_fn)
    (status, ret) = subprocess.getstatusoutput(cmd)
    if status == 0:
        print('[SUCCESS] %s' % cmd)
    else:
        print('[ERROR] %s' % cmd)
        print(ret)

    #ram img info
    flash_img_fn = flash_img_path + '/' + 'flash_main_img.hex.ram.fix'
    cmd = '../../scripts/zqh_sw_hex_fix.py --addr_min=0x%x --addr_max=0x%x --hex_in=%s --hex_out=%s' %(system_ram_mem_base, system_ram_mem_top+1,  hex_fn, flash_img_fn)
    (status, ret) = subprocess.getstatusoutput(cmd)
    if status == 0:
        print('[SUCCESS] %s' % cmd)
    else:
        print('[ERROR] %s' % cmd)
        print(ret)

   
    #section control info
    boot_loader_size = 0x2000 #flash's 1st 8K space is bootloader's, main img should jump this space
    sec_ctrl_info_fn = flash_img_path + '/' + 'sec_ctrl_info.hex.fix'
    sec_ctrl_info_addr_base = boot_loader_size - 512 #last 512 byte of bloadloader space is sec_ctrl_info table
    sec_ctrl_info_byte_idx = 0
    sec_ctrl_info = []

    #section number
    sec_num = len(sec_attr_list)
    for j in range(4):
        sec_ctrl_info.append([sec_ctrl_info_byte_idx, (sec_num >> (j*8)) & 0xff])
        sec_ctrl_info_byte_idx += 1

    #program start address
    program_start_address = int(sec_attr_list[0][2], 16)
    for j in range(4):
        sec_ctrl_info.append([sec_ctrl_info_byte_idx, (program_start_address >> (j*8)) & 0xff])
        sec_ctrl_info_byte_idx += 1

    #ram start address
    ram_start_address = None

    #get ram offset address
    ram_offset = 0
    for i in range(len(sec_attr_list)):
        tmp_addr = int(sec_attr_list[i][2], 16)
        tmp_len = int(sec_attr_list[i][3], 16)
        if ((tmp_addr >= system_flash_mem_base) and (tmp_addr <= system_flash_mem_top)):
            tmp_new = tmp_addr + tmp_len - program_start_address
            if (tmp_new > ram_offset):
                ram_offset = tmp_new

    #tmp print('ram_offset = %x' % (ram_offset))

    #each section's information
    for i in range(len(sec_attr_list)):
        #section type
        #0: read only
        #1: read write, need initial
        #2: read write, no need initial(clean to zero)
        if (sec_attr_list[i][1] == 'PROGBITS'):
            if (sec_attr_list[i][4] in ('AX', 'AM', 'AMS', 'A')):
                sec_type = 0
            elif (sec_attr_list[i][4] in ('WA', 'WAT')):
                sec_type = 1
            else:
                assert(0)
        elif (sec_attr_list[i][1] == 'NOBITS'):
            if (sec_attr_list[i][4] in ('WA', 'WAT')):
                sec_type = 2
            else:
                assert(0)
        for j in range(4):
            sec_ctrl_info.append([sec_ctrl_info_byte_idx, (sec_type >> (j*8)) & 0xff])
            sec_ctrl_info_byte_idx += 1

        sec_len = int(sec_attr_list[i][3], 16)

        #section source address(flash)
        #sec_flash_addr = (int(sec_attr_list[i][2], 16) & 0x00ffffff) + system_flash_mem_base
        img_addr = int(sec_attr_list[i][2], 16)
        #img rom
        if ((img_addr >= system_flash_mem_base) and (img_addr <= system_flash_mem_top)):
            sec_flash_addr = system_flash_mem_base + boot_loader_size + ((img_addr - program_start_address) & 0x00ffffff)
        #img ram(put after img rom)
        else:
            if (ram_start_address is None):
                ram_start_address = img_addr
            sec_flash_addr = system_flash_mem_base + boot_loader_size + ((img_addr - ram_start_address + ram_offset) & 0x00ffffff)
            #tmp print('sec_flash_addr = %x' % (sec_flash_addr))
            #tmp print(sec_attr_list[i])
        for j in range(4):
            sec_ctrl_info.append([sec_ctrl_info_byte_idx, (sec_flash_addr >> (j*8)) & 0xff])
            sec_ctrl_info_byte_idx += 1

        #section dest address(sram)
        sec_dest_addr = int(sec_attr_list[i][2], 16)
        for j in range(4):
            sec_ctrl_info.append([sec_ctrl_info_byte_idx, (sec_dest_addr >> (j*8)) & 0xff])
            sec_ctrl_info_byte_idx += 1

        #section data len
        for j in range(4):
            sec_ctrl_info.append([sec_ctrl_info_byte_idx, (sec_len >> (j*8)) & 0xff])
            sec_ctrl_info_byte_idx += 1

    out_f = open(sec_ctrl_info_fn, 'w')
    for i in sec_ctrl_info:
        out_f.write('@%x\n' % (sec_ctrl_info_addr_base + i[0]))
        out_f.write('%x\n' % (i[1]))
    out_f.close()
    
    sys.exit(0)

if __name__ == "__main__":
    main()
