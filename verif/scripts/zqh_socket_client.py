#!/usr/bin/python
 
import os
import sys
import socket
import time

def jtag_pin_all(tck, tms, tdi):
    return str((tck << 2) + (tms << 1) + tdi)

def jtag_init(socket, a = 10):
    for i in range(a):
        socket.send(jtag_pin_all(0, 1, 0))
        socket.send(jtag_pin_all(1, 1, 0))

def jtag_quit(socket):
    socket.send('Q')

def jtag_goto_run_test_idle(socket, a = 1):
    for i in range(a):
        socket.send(jtag_pin_all(0, 0, 0))
        socket.send(jtag_pin_all(1, 0, 0))

def jtag_goto_select_dr_scan(socket):
    socket.send(jtag_pin_all(0, 1, 0))
    socket.send(jtag_pin_all(1, 1, 0))

def jtag_goto_select_ir_scan(socket):
    socket.send(jtag_pin_all(0, 1, 0))
    socket.send(jtag_pin_all(1, 1, 0))

def jtag_goto_capture_ir(socket):
    socket.send(jtag_pin_all(0, 0, 0))
    socket.send(jtag_pin_all(1, 0, 0))

def jtag_goto_shift_ir(socket, tdi = 0):
    socket.send(jtag_pin_all(0, 0, tdi))
    socket.send(jtag_pin_all(1, 0, tdi))

def jtag_do_shift_ir(socket, a):
    tdi_bit = 0
    #shift idcode instruction
    for i in range(5):
        tdi_bit = (a >> i) & 1

        #last bit
        if (i == 4):
            jtag_goto_exit_1_ir(socket, tdi_bit)
        else:
            jtag_goto_shift_ir(socket, tdi_bit)


def jtag_goto_exit_1_ir(socket, tdi):
    socket.send(jtag_pin_all(0, 1, tdi))
    socket.send(jtag_pin_all(1, 1, tdi))

def jtag_goto_update_ir(socket):
    socket.send(jtag_pin_all(0, 1, 0))
    socket.send(jtag_pin_all(1, 1, 0))

def jtag_goto_capture_dr(socket):
    socket.send(jtag_pin_all(0, 0, 0))
    socket.send(jtag_pin_all(1, 0, 0))

def jtag_goto_shift_dr(socket, tdi = 0):
    socket.send(jtag_pin_all(0, 0, tdi))

    #read tdo
    socket.send('R')
    recv_data = socket.recv(1)

    #write tdi
    socket.send(jtag_pin_all(1, 0, tdi))

    return ord(recv_data) - ord('0')

def jtag_do_shift_dr(socket, a = 0):
    tdi_bit = 0
    tdo_bit = 0
    tdo_all = 0
    for i in range(32):
        tdi_bit = (a >> i) & 1
        if (i == 31):
            tdo_bit = jtag_goto_exit_1_dr(socket, tdi_bit)
        else:
            tdo_bit = jtag_goto_shift_dr(socket, tdi_bit)

        tdo_all = tdo_all | (tdo_bit << i)

    return tdo_all

def jtag_goto_exit_1_dr(socket, tdi = 0):
    socket.send(jtag_pin_all(0, 1, tdi))

    #read tdo
    socket.send('R')
    recv_data = socket.recv(1)

    #write tdi
    socket.send(jtag_pin_all(1, 1, tdi))

    return ord(recv_data) - ord('0')

def jtag_goto_update_dr(socket):
    socket.send(jtag_pin_all(0, 1, 0))
    socket.send(jtag_pin_all(1, 1, 0))


c = socket.socket()
host = socket.gethostname()
port =  5900

c.connect((host, port))

jtag_init(c)

idle_cycle = 5
inst = 0x10
wdata = 0
rdata = 0

for i in range(1000):
    jtag_goto_run_test_idle(c)
    jtag_goto_select_dr_scan(c)
    jtag_goto_select_ir_scan(c)
    jtag_goto_capture_ir(c)
    jtag_goto_shift_ir(c)
    jtag_do_shift_ir(c, inst)
    jtag_goto_update_ir(c)
    jtag_goto_select_dr_scan(c)
    jtag_goto_capture_dr(c)
    jtag_goto_shift_dr(c)
    rdata = jtag_do_shift_dr(c, wdata)
    jtag_goto_update_dr(c)
    jtag_goto_run_test_idle(c, 5)

    print('inst %x' % (inst))
    print('wdata %x' % (wdata))
    print('rdata %x' % (rdata))


jtag_quit(c)
c.close()

#cnt = 0
#tmp while (cnt < 10000):
#tmp     if (cnt % 2 == 0):
#tmp         send_data = '2'
#tmp     else:
#tmp         send_data = '6'
#tmp     c.send(send_data)
#tmp 
#tmp     #recv_data = c.recv(1024)
#tmp     #print(recv_data)
#tmp     cnt = cnt +1
#tmp     #time.sleep(1)
