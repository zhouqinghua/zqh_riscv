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
            break

def send_dmi_req(op, addr, data = 0):
    send_str = '#%x\n' %(op)
    #tmp print("send: %s" %(send_str), end = '')
    ser.write(send_str.encode("gbk"))
    
    send_str = '@%x\n' %(addr)
    #tmp print("send: %s" %(send_str), end = '')
    ser.write(send_str.encode("gbk"))
    
    send_str = '%x\n' %(data)
    #tmp print("send: %s" %(send_str), end = '')
    ser.write(send_str.encode("gbk"))

def send_dmi_req_fast(op, addr, data = 0):
    send_str = '$%x\n' %(op)
    #tmp print("send: %s" %(send_str), end = '')
    ser.write(send_str.encode("gbk"))
    
    send_str = '@%x\n' %(addr)
    #tmp print("send: %s" %(send_str), end = '')
    ser.write(send_str.encode("gbk"))
    
    send_str = '%x\n' %(data)
    #tmp print("send: %s" %(send_str), end = '')
    ser.write(send_str.encode("gbk"))

def wait_dmi_resp():
    recv_op = 0
    recv_data = 0
    #wait response key
    while(1):
        if(ser.in_waiting):
            recv_str = ser.readline().decode("gbk")
            #tmp print("%s" %(recv_str), end = '')
            if ((recv_str[0] == '#') and (recv_str[1] == '@')):
                #print("%s" %(recv_str), end = '')
                break
            else:
                print("%s" %(recv_str), end = '')

    #wait response.resp
    while(1):
        if(ser.in_waiting):
            recv_str = ser.readline().decode("gbk")
            #print("%s" %(recv_str), end = '')
            recv_op = int(recv_str, 16)
            break
    
    #wait response.data
    while(1):
        if(ser.in_waiting):
            recv_str = ser.readline().decode("gbk")
            #print("%s" %(recv_str), end = '')
            recv_data = int(recv_str, 16)
            break

    return (recv_op, recv_data)

##DMI regs
DMI_SBCS  =                          0x38

DMI_SBCS_SBBUSY_OFFSET  =      21
DMI_SBCS_SBBUSY_LENGTH  =      1
DMI_SBCS_SBBUSY         =      (1 << DMI_SBCS_SBBUSY_OFFSET)

DMI_SBCS_SBBUSYERROR_OFFSET    =    22
DMI_SBCS_SBBUSYERROR_LENGTH    =    1
DMI_SBCS_SBBUSYERROR           =    (1 << DMI_SBCS_SBBUSYERROR_OFFSET)

#/*
#* When a 1 is written here, triggers a read at the address in {\tt
#* sbaddress} using the access size set by \Fsbaccess.
# */
DMI_SBCS_SBSINGLEREAD_OFFSET   =     20
DMI_SBCS_SBSINGLEREAD_LENGTH   =     1
DMI_SBCS_SBSINGLEREAD          =     (1 << DMI_SBCS_SBSINGLEREAD_OFFSET)
#/*
#* Select the access size to use for system bus accesses triggered by
#* writes to the {\tt sbaddress} registers or \Rsbdatazero.
#*
#* 0: 8-bit
#*
#* 1: 16-bit
#*
#* 2: 32-bit
#*
#* 3: 64-bit
#*
#* 4: 128-bit
#*
#* If an unsupported system bus access size is written here,
#* the DM may not perform the access, or may perform the access
#* with any access size.
# */
DMI_SBCS_SBACCESS_OFFSET     =       17
DMI_SBCS_SBACCESS_LENGTH     =       3
DMI_SBCS_SBACCESS            =       (7 << DMI_SBCS_SBACCESS_OFFSET)
#/*
#* When 1, the internal address value (used by the system bus master)
#* is incremented by the access size (in bytes) selected in \Fsbaccess
#* after every system bus access.
# */
DMI_SBCS_SBAUTOINCREMENT_OFFSET   =  16
DMI_SBCS_SBAUTOINCREMENT_LENGTH   =  1
DMI_SBCS_SBAUTOINCREMENT          =  (1 << DMI_SBCS_SBAUTOINCREMENT_OFFSET)
#/*
#* When 1, every read from \Rsbdatazero automatically triggers a system
#* bus read at the new address.
# */
DMI_SBCS_SBAUTOREAD_OFFSET       =   15
DMI_SBCS_SBAUTOREAD_LENGTH       =   1
DMI_SBCS_SBAUTOREAD              =   (1 << DMI_SBCS_SBAUTOREAD_OFFSET)
#/*
#* When the debug module's system bus
#* master causes a bus error, this field gets set. The bits in this
#* field remain set until they are cleared by writing 1 to them.
#* While this field is non-zero, no more system bus accesses can be
#* initiated by the debug module.
#*
#* 0: There was no bus error.
#*
#* 1: There was a timeout.
#*
#* 2: A bad address was accessed.
#*
#* 3: There was some other error (eg. alignment).
#*
#* 4: The system bus master was busy when one of the
#* {\tt sbaddress} or {\tt sbdata} registers was written,
#* or the {\tt sbdata} register was read when it had
#* stale data.
# */
DMI_SBCS_SBERROR_OFFSET     =        12
DMI_SBCS_SBERROR_LENGTH     =        3
DMI_SBCS_SBERROR            =        (7 << DMI_SBCS_SBERROR_OFFSET)
#/*
#* Width of system bus addresses in bits. (0 indicates there is no bus
#* access support.)
# */
DMI_SBCS_SBASIZE_OFFSET     =        5
DMI_SBCS_SBASIZE_LENGTH     =        7
DMI_SBCS_SBASIZE            =        (0x7f << DMI_SBCS_SBASIZE_OFFSET)
#/*
#* 1 when 128-bit system bus accesses are supported.
# */
DMI_SBCS_SBACCESS128_OFFSET  =       4
DMI_SBCS_SBACCESS128_LENGTH  =       1
DMI_SBCS_SBACCESS128         =       (1 << DMI_SBCS_SBACCESS128_OFFSET)
#/*
#* 1 when 64-bit system bus accesses are supported.
# */
DMI_SBCS_SBACCESS64_OFFSET   =       3
DMI_SBCS_SBACCESS64_LENGTH   =       1
DMI_SBCS_SBACCESS64          =       (1 << DMI_SBCS_SBACCESS64_OFFSET)
#/*
#* 1 when 32-bit system bus accesses are supported.
# */
DMI_SBCS_SBACCESS32_OFFSET   =       2
DMI_SBCS_SBACCESS32_LENGTH   =       1
DMI_SBCS_SBACCESS32          =       (1 << DMI_SBCS_SBACCESS32_OFFSET)
#/*
#* 1 when 16-bit system bus accesses are supported.
# */
DMI_SBCS_SBACCESS16_OFFSET    =      1
DMI_SBCS_SBACCESS16_LENGTH    =      1
DMI_SBCS_SBACCESS16           =      (1 << DMI_SBCS_SBACCESS16_OFFSET)
#/*
#* 1 when 8-bit system bus accesses are supported.
# */
DMI_SBCS_SBACCESS8_OFFSET    =       0
DMI_SBCS_SBACCESS8_LENGTH    =       1
DMI_SBCS_SBACCESS8           =       (1 << DMI_SBCS_SBACCESS8_OFFSET)
DMI_SBADDRESS0               =       0x39
#/*
#* Accesses bits 31:0 of the internal address.
# */
DMI_SBADDRESS0_ADDRESS_OFFSET   =    0
DMI_SBADDRESS0_ADDRESS_LENGTH   =    32
DMI_SBADDRESS0_ADDRESS          =    (0xffffffff << DMI_SBADDRESS0_ADDRESS_OFFSET)
DMI_SBADDRESS1                  =    0x3a
#/*
#* Accesses bits 63:32 of the internal address (if the system address
#* bus is that wide).
# */
DMI_SBADDRESS1_ADDRESS_OFFSET   =    0
DMI_SBADDRESS1_ADDRESS_LENGTH   =    32
DMI_SBADDRESS1_ADDRESS          =    (0xffffffff << DMI_SBADDRESS1_ADDRESS_OFFSET)
DMI_SBADDRESS2                  =    0x3b
#/*
#* Accesses bits 95:64 of the internal address (if the system address
#* bus is that wide).
# */
DMI_SBADDRESS2_ADDRESS_OFFSET   =    0
DMI_SBADDRESS2_ADDRESS_LENGTH   =    32
DMI_SBADDRESS2_ADDRESS          =    (0xffffffff << DMI_SBADDRESS2_ADDRESS_OFFSET)
DMI_SBDATA0                     =    0x3c
#/*
#* Accesses bits 31:0 of the internal data.
# */
DMI_SBDATA0_DATA_OFFSET       =      0
DMI_SBDATA0_DATA_LENGTH       =      32
DMI_SBDATA0_DATA              =      (0xffffffff << DMI_SBDATA0_DATA_OFFSET)
DMI_SBDATA1                   =      0x3d
#/*
#* Accesses bits 63:32 of the internal data (if the system bus is
#* that wide).
# */
DMI_SBDATA1_DATA_OFFSET     =        0
DMI_SBDATA1_DATA_LENGTH     =        32
DMI_SBDATA1_DATA            =        (0xffffffff << DMI_SBDATA1_DATA_OFFSET)
DMI_SBDATA2                 =        0x3e
#/*
#* Accesses bits 95:64 of the internal data (if the system bus is
#* that wide).
# */
DMI_SBDATA2_DATA_OFFSET    =         0
DMI_SBDATA2_DATA_LENGTH    =         32
DMI_SBDATA2_DATA           =         (0xffffffff << DMI_SBDATA2_DATA_OFFSET)
DMI_SBDATA3                =         0x3f
#/*
#* Accesses bits 127:96 of the internal data (if the system bus is
#* that wide).
# */
DMI_SBDATA3_DATA_OFFSET    =         0
DMI_SBDATA3_DATA_LENGTH    =         32
DMI_SBDATA3_DATA           =         (0xffffffff << DMI_SBDATA3_DATA_OFFSET)


##spi0 cfg regs
SPI0_BASE = 0x10014000
SPI0_SCKDIV  = (SPI0_BASE + 0x000)
SPI0_SCKMODE = (SPI0_BASE + 0x004)
SPI0_CSID    = (SPI0_BASE + 0x010)
SPI0_CSDEF   = (SPI0_BASE + 0x014)
SPI0_CSMODE  = (SPI0_BASE + 0x018)
SPI0_DELAY0  = (SPI0_BASE + 0x028)
SPI0_DELAY1  = (SPI0_BASE + 0x02c)
SPI0_FMT     = (SPI0_BASE + 0x040)
SPI0_TXDATA  = (SPI0_BASE + 0x048)
SPI0_RXDATA  = (SPI0_BASE + 0x04c)
SPI0_TXMARK  = (SPI0_BASE + 0x050)
SPI0_RXMARK  = (SPI0_BASE + 0x054)
SPI0_FCTRL   = (SPI0_BASE + 0x060)
SPI0_FFMT    = (SPI0_BASE + 0x064)
SPI0_IE      = (SPI0_BASE + 0x070)
SPI0_IP      = (SPI0_BASE + 0x074)


def dmi_reg_read(addr):
    send_dmi_req(0x01, addr)
    return wait_dmi_resp()

def dmi_reg_write(addr, data):
    send_dmi_req(0x02, addr, data)
    return wait_dmi_resp()

def dmi_sba_store_32b_fast(taddr, data):
    send_dmi_req_fast(0x02, taddr, data)
    resp = wait_dmi_resp()
    return resp[1]

def dmi_sba_load_32b_fast(taddr):
    send_dmi_req_fast(0x01, taddr)
    resp = wait_dmi_resp()
    return resp[1]

def dmi_sba_store_32b(taddr, data):

    #print("zqh: dmi_sba_store_32b")
    #print("zqh: dmi_sba_store_32b taddr = 0x%x" %(taddr))
    #print("zqh: dmi_sba_store_32b data = 0x%x" %(data))
    ##set sbcs
    dmi_reg_write(DMI_SBCS, DMI_SBCS_SBBUSYERROR | (2 << DMI_SBCS_SBACCESS_OFFSET) | DMI_SBCS_SBERROR)

    ##set address
    dmi_reg_write(DMI_SBADDRESS1, (taddr >> 32) & 0xffffffff)##high 32bit
    dmi_reg_write(DMI_SBADDRESS0, taddr & 0xffffffff)##low 32bit

    ##set store data
    dmi_reg_write(DMI_SBDATA1, 0)##high 32bit
    dmi_reg_write(DMI_SBDATA0, data)##low 32bit

    ##wait done
    sbcs_busy = 1
    while(sbcs_busy):
        resp = dmi_reg_read(DMI_SBCS)
        sbcs_rd_data = resp[1]
        sbcs_busy = (sbcs_rd_data & DMI_SBCS_SBBUSY) >> DMI_SBCS_SBBUSY_OFFSET
        sbcs_error = (sbcs_rd_data & DMI_SBCS_SBERROR) >> DMI_SBCS_SBERROR_OFFSET
    assert(sbcs_error == 0)

    #print("zqh: dmi_sba_store_32b done")

def dmi_sba_load_32b(taddr):
    #print("zqh: dmi_sba_load_32b")
    #print("zqh: dmi_sba_load_32b taddr = 0x%x" %(taddr))

    ##set sbcs
    dmi_reg_write(DMI_SBCS, DMI_SBCS_SBBUSYERROR | DMI_SBCS_SBSINGLEREAD | (2 << DMI_SBCS_SBACCESS_OFFSET) | DMI_SBCS_SBERROR)

    ##set access address
    dmi_reg_write(DMI_SBADDRESS1, (taddr >> 32) & 0xffffffff)##high 32bit
    dmi_reg_write(DMI_SBADDRESS0, taddr & 0xffffffff)##low 32bit


    ##wait done
    sbcs_busy = 1
    while(sbcs_busy):
        resp = dmi_reg_read(DMI_SBCS)
        sbcs_rd_data = resp[1]
        sbcs_busy = (sbcs_rd_data & DMI_SBCS_SBBUSY) >> DMI_SBCS_SBBUSY_OFFSET
        sbcs_error = (sbcs_rd_data & DMI_SBCS_SBERROR) >> DMI_SBCS_SBERROR_OFFSET
    assert(sbcs_error == 0)



    ##readout data
    resp = dmi_reg_read(DMI_SBDATA0)##low 32b
    data = resp[1]
    #print("zqh: dmi_sba_load_32b data = 0x%x" %(data))
    #print("zqh: dmi_sba_load_32b done")
    return data

def spi0_tx_rx_byte(wrdata, rx):
    ##wait tx_fifo none full
    txdata = 0x80000000
    while((txdata & 0x80000000) != 0):
        txdata = dmi_sba_load_32b_fast(SPI0_TXDATA)
    dmi_sba_store_32b_fast(SPI0_TXDATA, wrdata)

    ##wait tx_fifo empty
    ip = 0
    while(ip == 0):
        ip = dmi_sba_load_32b_fast(SPI0_IP)
        ip = ip & 0x01

    ##wait rx_fifo none empty
    rxdata = 0x80000000
    if (rx):
        while((rxdata & 0x80000000) != 0):
            rxdata = dmi_sba_load_32b_fast(SPI0_RXDATA)
    return rxdata

def spi0_norflash_read_jedec_id():
    ##use hold mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 2) ##0: auto, 1: reserved, 2: hold, 3: off
    dmi_sba_store_32b_fast(SPI0_TXMARK, 1) ##if tx_fifo is empty, ip.txwm will be valid
    dmi_sba_store_32b_fast(SPI0_FMT, 0x00080008)##len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    ##send cmd
    spi0_tx_rx_byte(0x9f, 0)


    ##recieve 3 byte data
    tmp_reg_rddata = dmi_sba_load_32b_fast(SPI0_FMT)
    dmi_sba_store_32b_fast(SPI0_FMT, tmp_reg_rddata & 0xfffffff7)##dir = 0(rx)
    id = 0
    for i in range(3):
        rx_data = spi0_tx_rx_byte(0, 1)
        id = (rx_data << ((2 - i)*8)) | id

    ##reset to auto mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 0)

    return id


def spi0_norflash_read_unique_id():
    ##use hold mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 2) ##0: auto, 1: reserved, 2: hold, 3: off
    dmi_sba_store_32b_fast(SPI0_TXMARK, 1) ##if tx_fifo is empty, ip.txwm will be valid
    dmi_sba_store_32b_fast(SPI0_FMT, 0x00080008)##len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)


    ##send cmd
    spi0_tx_rx_byte(0x4b, 0)

    ##send 4 dumy byte
    for i in range(4):
        spi0_tx_rx_byte(0, 0)

    ##recieve 8 byte data
    tmp_reg_rddata = dmi_sba_load_32b_fast(SPI0_FMT)
    dmi_sba_store_32b_fast(SPI0_FMT, tmp_reg_rddata & 0xfffffff7)##dir = 0(rx)
    id = 0
    for i in range(8):
        rx_data = spi0_tx_rx_byte(0, 1)
        id = (rx_data << ((7 - i)*8)) | id

    ##reset to auto mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 0)

    return id

def spi0_norflash_write_enable():
    ##use hold mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 2) ##0: auto, 1: reserved, 2: hold, 3: off
    dmi_sba_store_32b_fast(SPI0_TXMARK, 1) ##if tx_fifo is empty, ip.txwm will be valid
    dmi_sba_store_32b_fast(SPI0_FMT, 0x00080008)##len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    ##send cmd
    spi0_tx_rx_byte(0x06, 0)

    ##reset to auto mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 0)

def spi0_norflash_read_sr(num):
    ##use hold mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 2) ##0: auto, 1: reserved, 2: hold, 3: off
    dmi_sba_store_32b_fast(SPI0_TXMARK, 1) ##if tx_fifo is empty, ip.txwm will be valid
    dmi_sba_store_32b_fast(SPI0_FMT, 0x00080008)##len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    ##send cmd
    if (num == 1):
        cmd = 0x05
    elif (num == 2):
        cmd = 0x35
    elif (num == 3):
        cmd = 0x15
    else:
        cmd = 0x05
    spi0_tx_rx_byte(cmd, 0)

    ##recieve 1 byte data
    tmp_reg_rddata = dmi_sba_load_32b_fast(SPI0_FMT)
    dmi_sba_store_32b_fast(SPI0_FMT, tmp_reg_rddata & 0xfffffff7)##dir = 0(rx)
    sr = spi0_tx_rx_byte(0, 1)

    ##reset to auto mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 0)

    return sr

def spi0_norflash_chip_erase():
    spi0_norflash_write_enable()

    ##use hold mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 2) ##0: auto, 1: reserved, 2: hold, 3: off
    dmi_sba_store_32b_fast(SPI0_TXMARK, 1) ##if tx_fifo is empty, ip.txwm will be valid
    dmi_sba_store_32b_fast(SPI0_FMT, 0x00080008)##len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    ##send cmd
    spi0_tx_rx_byte(0xc7, 0)

    ##reset to auto mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 0)

    ##wait busy clear
    sr_busy = 1
    while(sr_busy):
        sr_busy = spi0_norflash_read_sr(1) & 0x01

def spi0_norflash_read(addr, length):
    ##use hold mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 2) ##0: auto, 1: reserved, 2: hold, 3: off
    dmi_sba_store_32b_fast(SPI0_TXMARK, 1) ##if tx_fifo is empty, ip.txwm will be valid
    dmi_sba_store_32b_fast(SPI0_FMT, 0x00080008)##len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    ##send read cmd
    spi0_tx_rx_byte(0x03, 0)


    ##send 3 byte address
    for i in range(3):
        spi0_tx_rx_byte(addr >> ((2 - i) * 8), 0)

    ##recieve data
    tmp_reg_rddata = dmi_sba_load_32b_fast(SPI0_FMT)
    dmi_sba_store_32b_fast(SPI0_FMT, tmp_reg_rddata & 0xfffffff7)##dir = 0(rx)
    buf = []
    for i in range(length):
        buf.append(spi0_tx_rx_byte(0, 1))


    ##reset to auto mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 0)

    return buf

def spi0_norflash_write(addr, buf, length):

    spi0_norflash_write_enable()

    ##use hold mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 2) ##0: auto, 1: reserved, 2: hold, 3: off
    dmi_sba_store_32b_fast(SPI0_TXMARK, 1) ##if tx_fifo is empty, ip.txwm will be valid
    dmi_sba_store_32b_fast(SPI0_FMT, 0x00080008)##len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    ##send write cmd
    spi0_tx_rx_byte(0x02, 0)

    ##send 3 byte address
    for i in range(3):
        spi0_tx_rx_byte(addr >> ((2 - i) * 8), 0)

    ##send write data
    for i in range(length):
        spi0_tx_rx_byte(buf[i], 0)

    ##reset to auto mode
    dmi_sba_store_32b_fast(SPI0_CSMODE, 0)

    ##wait busy clear
    sr_busy = 1
    while(sr_busy):
        sr_busy = spi0_norflash_read_sr(1) & 0x01

#test id read
for i in range(1):
    send_dmi_req(0x1, 0x12)
    resp = wait_dmi_resp()
    print('test dmi response: resp = %x, data = %x' %(resp[0], resp[1]))

#tmp for i in range(1):
#tmp     dmi_sba_store_32b_fast(SPI0_SCKDIV, 0xff)
#tmp     resp_data = dmi_sba_load_32b_fast(SPI0_SCKDIV)
#tmp     print('test sba response: data = %x' %(resp_data))

jedec_id = spi0_norflash_read_jedec_id()
print('jedec_id = %x' %(jedec_id))
unique_id = spi0_norflash_read_unique_id()
print('unique_id = %x' %(unique_id))
#tmp spi0_norflash_chip_erase()
#tmp print('spi0_norflash_chip_erase done')

#tmp wrdata_buf = [0,0,0,0]
#tmp spi0_norflash_write(0, wrdata_buf, 4)
#tmp print('spi0_norflash_write done')
#tmp 
norflash_addr_base = 0
for i in range(64):
    norflash_addr = norflash_addr_base + i
    rddata_buf = spi0_norflash_read(norflash_addr, 1)
    print('spi0_norflash_read[%x] = 0x%x' %(norflash_addr, rddata_buf[0]))

ser.close()#关闭串口
sys.exit(0)
    


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
#for fn in (boot_img, sec_ctrl_img, main_img_rom, main_img_ram):
for fn in (boot_img, sec_ctrl_img):
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

    #tmp for i in in_hex:
    #tmp     send_str = i
    #tmp     print("send: %s" %(send_str), end = '')
    #tmp     ser.write(send_str.encode("gbk"))
    flash_addr = 0
    flash_wdata = 0
    for i in range(len(in_hex)):
        if (i%2 == 0):
            flash_addr = int(in_hex[i][1:], 16)
        else:
            flash_wdata = int(in_hex[i], 16)
            print("write: addr = %x, data = %x" %(flash_addr, flash_wdata))
            spi0_norflash_write(flash_addr, [flash_wdata], 1)
    
    img_idx = img_idx + 1

print("flash write success")
ser.close()#关闭串口
sys.exit(0)
