import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

class zqh_bootrom_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_bootrom_parameter, self).set_par()
        self.par('bootrom_file', '../tests/zqh_riscv_sw/bootrom/bootrom.hex.fix')

    def check_par(self):
        super(zqh_bootrom_parameter, self).check_par()

    def address(self):
        return self.extern_slaves[0].address[0]
