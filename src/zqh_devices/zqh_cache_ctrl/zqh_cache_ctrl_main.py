import sys
import os
from phgl_imp import *
from .zqh_cache_ctrl_parameters import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module

class zqh_cache_ctrl(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_cache_ctrl, self).set_par()
        self.p = zqh_cache_ctrl_parameter()

    def gen_node_tree(self):
        super(zqh_cache_ctrl, self).gen_node_tree()
        self.gen_node_slave('cache_ctrl_slave', tl_type = 'tl_uh')

    def set_port(self):
        super(zqh_cache_ctrl, self).set_port()

    def main(self):
        super(zqh_cache_ctrl, self).main()
        self.gen_node_interface('cache_ctrl_slave')

        #define config regs
        flush = self.cfg_reg(csr_reg_group(
            'flush', 
            offset = 0, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 32, access = 'VOL', reset = 0)]))
