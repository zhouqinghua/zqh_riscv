import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

class zqh_dma_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_dma_parameter, self).set_par()
        self.par('num_channels', 1)
        self.par('max_tl_size', 6)
        self.par('data_buffer_entries', 32)
        self.par('asm_buffer_entries', 8)
        self.par('num_flights', 8)

    def check_par(self):
        super(zqh_dma_parameter, self).check_par()
        #each channel has 2 interrupts: done, error

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_master_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(
            name, end_source_id = self.num_flights - 1)

    def gen_tl_slave_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(
            name, int_source_bits = self.num_channels * 2)
