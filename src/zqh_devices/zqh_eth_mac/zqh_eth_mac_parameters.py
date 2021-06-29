import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

class zqh_eth_mac_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_eth_mac_parameter, self).set_par()
        self.par('tx_bd_fifo_entries', 8)
        self.par('tx_cpl_fifo_entries', 8)
        self.par('rx_bd_fifo_entries', 8)
        self.par('rx_cpl_fifo_entries', 8)
        self.par('tx_buf_size', 4096)
        self.par('rx_buf_size', 4096)
        self.par('tx_fifo_entries', 10)
        self.par('tx_fifo_data_width', 64)
        self.par('rx_fifo_data_width', 64)
        self.par('rx_fifo_entries', 10)
        self.par('min_rx_ipg', 24)
        self.par('sync_delay', 3)

    def check_par(self):
        super(zqh_eth_mac_parameter, self).check_par()

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name, int_source_bits = 1)
