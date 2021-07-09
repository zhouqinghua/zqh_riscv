import os
import sys
import getopt
import time
import re
import serial
import serial.tools.list_ports

try:
    opts, args = getopt.getopt(sys.argv[1:], 'h:', ['help', 'boot_img=', 'sec_ctrl_img=', 'main_img=', 'portx='])
except getopt.GetoptError:
    print("argv error,please input")

boot_img = './bootloader.hex.fix'
sec_ctrl_img = './sec_ctrl_info.hex.fix'
main_img = './flash_main_img.hex.fix'
main_img_rom = './flash_main_img.hex.rom.fix'
main_img_ram = './flash_main_img.hex.ram.fix'

#Linux's /dev/ttyUSB0. or Windows's COM3
portx="COM3"

for (k,v) in opts:
    if (k == '--boot_img'):
        boot_img = v
    elif (k == '--main_img'):
        main_img = v
    elif (k == '--sec_ctrl_img'):
        sec_ctrl_img = v
    elif (k == '--portx'):
        portx = v
    else:
        assert(0), 'illegal prameter name: %s' %(k)



#baudrate: 50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
bps=57600
#timeout None means wait forever, 0 means no wait, other value means wait x seconds
timex=5
ser=serial.Serial(portx,bps,timeout=timex)
#print("ser parameter: ", ser)

#print(ser.port)#port number
#print(ser.baudrate)#baudrate


#port_list = list(serial.tools.list_ports.comports())
#print(port_list)
#if len(port_list) == 0:
#   print('no ser port can use')
#else:
#    for i in range(0,len(port_list)):
#        print(port_list[i])


#print(ser.read())#read one byte
#print(ser.read(10).decode("gbk"))#read 10 bytes
#print(ser.readline().decode("gbk"))#read one line
#print(ser.readlines())#read multy lines
#print(ser.in_waiting)#input buffer's left byte number
#print(ser.out_waiting)#output buffer's left byte number

# initial send one byte
#ser.write('\n'.encode("gbk"))
#time.sleep(1)
#ser.write('\n'.encode("gbk"))
#time.sleep(1)

ser.flush()
ser.flushInput()
ser.flushOutput()

#1st and 2nd send byte will by droped ???
ser.write('\n'.encode("gbk"))
time.sleep(1)
ser.write('\n'.encode("gbk"))
time.sleep(1)
#3rd send byte can be recieved by target ???
ser.write('\n'.encode("gbk"))
time.sleep(1)

check_data_en = 0
while(1):
    if(ser.in_waiting):
        recv_str = ser.readline().decode("gbk")
        print("%s" %(recv_str), end = '')
        if (recv_str == '**FLASH INIT DONE**\n'):
            time.sleep(2)
            break;

#send check_data_en flag
send_str = str(check_data_en)
ser.write(send_str.encode("gbk"))
ser.write('\n'.encode("gbk"))

    
img_idx = 0
boot_loader_size = 0x2000
fash_space_base = 0x20000000
fash_space_top = 0x2fffffff
sram_space_base = 0x40000000
sram_space_top = 0xbfffffff
#for fn in (boot_img, sec_ctrl_img, main_img):
img_rom_start_addr = None
img_ram_start_addr = None
ram_offset = 0
for fn in (boot_img, sec_ctrl_img, main_img_rom, main_img_ram):
    in_fn = fn
    in_f = open(in_fn, 'r')
    in_hex = in_f.readlines()
    in_f.close()

    #main_img need sub it's start address
    #and start from 0x2000 in flash space
    if (len(in_hex) > 0):
        if (img_idx == 2):
            img_rom_start_addr = int(in_hex[0][1:], 16)
            for i in range(len(in_hex)):
                if (in_hex[i][0] == '@'):
                    addr = int(in_hex[i][1:], 16) - img_rom_start_addr + boot_loader_size
                    in_hex[i] = '@%0x\n' % (addr)
                    ram_offset = addr - boot_loader_size + 1
        if (img_idx == 3):
            img_ram_start_addr = int(in_hex[0][1:], 16)
            for i in range(len(in_hex)):
                if (in_hex[i][0] == '@'):
                    addr = int(in_hex[i][1:], 16) - img_ram_start_addr + boot_loader_size + ram_offset
                    in_hex[i] = '@%0x\n' % (addr)
    print("flash will write %s" %(in_fn))
    time.sleep(2)

    for i in in_hex:
        send_str = i
        print("send: %s" %(send_str), end = '')
        ser.write(send_str.encode("gbk"))

        #wait response
        if (check_data_en):
            while(ser.in_waiting == 0):
                #time.sleep(1)
                #print("in_waiting = %d" %(ser.in_waiting))
                pass
            while(ser.in_waiting):
                #str=ser.read(ser.in_waiting ).decode("gbk")
                #recv_str = ser.read(ser.in_waiting ).decode("gbk")
                recv_str = ser.readline().decode("gbk")
                #str = str.strip()
                if (send_str[0] == '@'):
                    exp_str = send_str[1:];
                else:
                    exp_str = send_str;
                if (int(recv_str, 16) != int(exp_str, 16)):
                    print("recv: %s" %(recv_str), end = '')
                    print("fail: data compare no match")
                    sys.exit(1)
    img_idx = img_idx + 1

print("flash write success")
ser.close()
sys.exit(0)
