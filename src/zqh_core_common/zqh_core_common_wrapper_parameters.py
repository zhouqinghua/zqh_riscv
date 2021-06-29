import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_parameters import zqh_buffer_parameter
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_order_fix_parameters import zqh_tilelink_order_fix_parameter

class zqh_core_common_wrapper_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_core_common_wrapper_parameter, self).set_par()
        self.par('int_sync_delay', 3)
        self.par('out_bus_has_buffer',1)
        self.par('buf_params', {
            'a': zqh_buffer_parameter.default_p(),
            'd': zqh_buffer_parameter.default_p(),
            'b': zqh_buffer_parameter.default_p(),
            'c': zqh_buffer_parameter.default_p(),
            'e': zqh_buffer_parameter.default_p() 
            })
        self.par('order_fix', zqh_tilelink_order_fix_parameter())
