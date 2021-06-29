import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

class zqh_uart_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_uart_parameter, self).set_par()
        self.par('div_width', 16)
        self.par('div_init', 8680 - 1) #115200 baud @ 1GHz bus clock
        self.par('tx_fifo_entries', 8)
        self.par('rx_fifo_entries', 8)
        self.par('parity_check', 1)
        self.par('sync_delay', 3)

    def check_par(self):
        super(zqh_uart_parameter, self).check_par()

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name, int_source_bits = 1)
