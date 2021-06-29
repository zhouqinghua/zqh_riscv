import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_buffer_parameter

class zqh_print_monitor_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_print_monitor_parameter, self).set_par()
        self.par('buf_params_in', {
            'a': zqh_buffer_parameter.normal_p(2),
            'd': zqh_buffer_parameter.none_p()
            })

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name)
