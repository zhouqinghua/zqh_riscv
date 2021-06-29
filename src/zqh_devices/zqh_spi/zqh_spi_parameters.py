import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

class zqh_spi_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_spi_parameter, self).set_par()
        self.par('flash_en', 1)
        self.par('div_width', 12)
        self.par('div_init', 16)
        self.par('cs_width', 4)
        self.par('tx_fifo_entries', 8)
        self.par('rx_fifo_entries', 8)

    def check_par(self):
        super(zqh_spi_parameter, self).check_par()

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name, int_source_bits = 1)
