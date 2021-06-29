import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

class zqh_pwm_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_pwm_parameter, self).set_par()
        self.par('cmp_width', 16)
        self.par('ncmp', 4)

    def check_par(self):
        super(zqh_pwm_parameter, self).check_par()
        assert(self.ncmp <= 4), 'ncmp must less than 4'

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name, int_source_bits = 1)
