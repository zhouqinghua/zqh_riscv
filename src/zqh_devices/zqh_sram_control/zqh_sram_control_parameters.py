import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_buffer_parameter

class zqh_sram_control_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_sram_control_parameter, self).set_par()
        self.par('mem_size', 2**21)
        self.par('data_ecc', "identity")
        self.par('data_ecc_bytes', 1)
        #tmp self.par('buf_params_in', {
        #tmp     'a': zqh_buffer_parameter.normal_p(8),
        #tmp     'd': zqh_buffer_parameter.normal_p(4)
        #tmp     })
        self.par('req_buf_entries', 8)
        self.par('resp_buf_entries', 4)

    def check_par(self):
        super(zqh_sram_control_parameter, self).check_par()
        self.par('data_ecc_bits', self.data_ecc_bytes * 8)
        self.par('data_enc_bits', ecc_code(self.data_ecc).width(self.data_ecc_bits))

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name)
