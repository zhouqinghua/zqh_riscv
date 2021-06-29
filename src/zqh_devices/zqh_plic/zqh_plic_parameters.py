import sys
import os
from phgl_imp import *
from .zqh_plic_misc import zqh_plic_consts
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_buffer_parameter

class zqh_plic_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_plic_parameter, self).set_par()
        self.par('max_priorities', 7)
        self.par('num_cores', 1)
        self.par('use_vms', [1])
        self.par('num_devices', 2)
        self.par('buf_params', {
            'a': zqh_buffer_parameter.default_p(),
            'd': zqh_buffer_parameter.default_p(),
            'b': zqh_buffer_parameter.default_p(),
            'c': zqh_buffer_parameter.default_p(),
            'e': zqh_buffer_parameter.default_p() 
            })

    def check_par(self):
        super(zqh_plic_parameter, self).check_par()
        assert(self.max_priorities >= 0)
        assert(zqh_plic_consts.hartBase() >= zqh_plic_consts.enableBase(zqh_plic_consts.maxHarts))
        self.is_int_sink = 1

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_bundle_p(self, name = ''):
        int_sum = sum(list(map(
            lambda _: 2 if (self.use_vms[_]) else 1,
            range(self.num_cores))))
        return zqh_tl_bundle_all_channel_parameter(name, int_source_bits = int_sum)

    def num_priorities(self):
        return (1 << log2_ceil(self.max_priorities+1)) - 1

    def priority_bits(self):
        return log2_ceil(self.num_priorities()+1)
