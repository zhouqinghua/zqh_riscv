import os
import sys
import getopt
import time
import re
import serial
import serial.tools.list_ports

try:
    opts, args = getopt.getopt(sys.argv[1:], 'h:', ['help', 'boot_img=', 'sec_ctrl_img=', 'main_img='])
except getopt.GetoptError:
    print("argv error,please input")

boot_img = './bootloader.hex.fix'
sec_ctrl_img = './sec_ctrl_info.hex.fix'
main_img = './flash_main_img.hex.fix'
main_img_rom = './flash_main_img.hex.rom.fix'
main_img_ram = './flash_main_img.hex.ram.fix'

for (k,v) in opts:
    if (k == '--boot_img'):
        boot_img = v
    elif (k == '--main_img'):
        main_img = v
    elif (k == '--sec_ctrl_img'):
        sec_ctrl_img = v
    else:
        assert(0), 'illegal prameter name: %s' %(k)



#端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
portx="COM3"
#波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
bps=57600
#超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
timex=5
# 打开串口，并得到串口对象
ser=serial.Serial(portx,bps,timeout=timex)
#print("串口详情参数：", ser)

#print(ser.port)#获取到当前打开的串口名
#print(ser.baudrate)#获取波特率


#port_list = list(serial.tools.list_ports.comports())
#print(port_list)
#if len(port_list) == 0:
#   print('无可用串口')
#else:
#    for i in range(0,len(port_list)):
#        print(port_list[i])


#print(ser.read())#读一个字节
#print(ser.read(10).decode("gbk"))#读十个字节
#print(ser.readline().decode("gbk"))#读一行
#print(ser.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
#print(ser.in_waiting)#获取输入缓冲区的剩余字节数
#print(ser.out_waiting)#获取输出缓冲区的字节数

#循环接收数据，此为死循环，可用线程实现

# initial send one byte
#ser.write('\n'.encode("gbk"))
#time.sleep(1)
#ser.write('\n'.encode("gbk"))
#time.sleep(1)

ser.flush() #等待所有数据写出。
ser.flushInput() #丢弃接收缓存中的所有数据
ser.flushOutput() #终止当前写操作，并丢弃发送缓存中的数据。

#1st and 2nd send byte will by droped ???
ser.write('\n'.encode("gbk"))
time.sleep(1)
ser.write('\n'.encode("gbk"))
time.sleep(1)
#3rd send byte can be recieved by target ???
ser.write('\n'.encode("gbk"))
time.sleep(1)

while(1):
    if(ser.in_waiting):
        recv_str = ser.readline().decode("gbk")
        print("%s" %(recv_str), end = '')
        if (recv_str == '**FLASH INIT DONE**\n'):
            time.sleep(2)
            break;
    
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
    
    img_idx = img_idx + 1

#tmp if (img_rom_start_addr is not None):
#tmp     print("img_rom_start_addr = %x" %(img_rom_start_addr))
#tmp if (img_ram_start_addr is not None):
#tmp     print("img_ram_start_addr = %x" %(img_ram_start_addr))
#tmp print("ram_offset = %x" %(ram_offset))
        #wait response
#tmp        while(ser.in_waiting == 0):
#tmp            #time.sleep(1)
#tmp            #print("in_waiting = %d" %(ser.in_waiting))
#tmp            pass
#tmp    
#tmp        #print all recieve byte
#tmp        while(ser.in_waiting):
#tmp            #str=ser.read(ser.in_waiting ).decode("gbk")
#tmp            #recv_str = ser.read(ser.in_waiting ).decode("gbk")
#tmp            recv_str = ser.readline().decode("gbk")
#tmp            #str = str.strip()
#tmp            if (send_str[0] == '@'):
#tmp                exp_str = send_str[1:];
#tmp            else:
#tmp                exp_str = send_str;
#tmp            if (int(recv_str, 16) != int(exp_str, 16)):
#tmp                print("recv: %s" %(recv_str), end = '')
#tmp                print("fail: data compare no match")
#tmp                sys.exit(1)

print("flash write success")
ser.close()#关闭串口
sys.exit(0)
