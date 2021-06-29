import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_buffer_parameter
from zqh_amba.zqh_axi4_parameters import zqh_axi4_all_channel_parameter

class zqh_axi4_sram_control_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_axi4_sram_control_parameter, self).set_par()
        self.par('mem_size', 2**21)
        self.par('data_ecc', "identity")
        self.par('data_ecc_bytes', 1)
        self.par('buf_params_in', {
            'ar': zqh_buffer_parameter.normal_p(8),
            'aw': zqh_buffer_parameter.normal_p(8),
            'w': zqh_buffer_parameter.normal_p(8),
            'b': zqh_buffer_parameter.normal_p(4),
            'r': zqh_buffer_parameter.normal_p(4)
            })

    def check_par(self):
        super(zqh_axi4_sram_control_parameter, self).check_par()
        self.par('data_ecc_bits', self.data_ecc_bytes * 8)
        self.par('data_enc_bits', ecc_code(self.data_ecc).width(self.data_ecc_bits))

    def gen_tl_bundle_p(self, name = ''):
        return zqh_axi4_all_channel_parameter(name)
