import sys
import os
from phgl_imp import *

def zqh_eth_mac_fcs_crc(init_en, init_v, update, din):
    crc_poly = 0x104c11db7
    crc_reg = reg(w = 32)
    with when(init_en):
        crc_reg /= init_v
    with elsewhen(update):
        crc_reg /= crc32(crc_reg, din, crc_poly, 1)
    return crc_reg
