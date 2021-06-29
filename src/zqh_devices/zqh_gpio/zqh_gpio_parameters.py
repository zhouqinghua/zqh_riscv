import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

class zqh_gpio_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_gpio_parameter, self).set_par()
        self.par('num_ports', 8)
        self.par('num_ints', 8)
        self.par('sync_delay', 3)

    def check_par(self):
        super(zqh_gpio_parameter, self).check_par()
        assert(self.num_ports <= 32)
        assert(self.num_ints <= self.num_ports)

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name, int_source_bits = self.num_ints)
