from phgl_imp import *

def zqh_usb_ctrl_crc5(din):
    crc_poly = 0b100101
    return crc5(0b11111, din, crc_poly, 1)

def zqh_usb_ctrl_device_crc5(din, data_old):
    crc_poly = 0b100101
    return crc5(data_old, din, crc_poly, 1)

def zqh_usb_ctrl_crc16(din, data_old):
    crc_poly = 0b11000000000000101
    return crc16(data_old, din, crc_poly, 1)
