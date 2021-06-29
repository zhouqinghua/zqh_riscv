import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_buffer_parameter
from zqh_tilelink.zqh_tilelink_llc_parameters import zqh_tilelink_llc_parameter
from zqh_tilelink.zqh_tilelink_memory_access_pos_parameters import zqh_tilelink_memory_access_pos_parameter
from zqh_tilelink.zqh_tilelink_atomic_transform_parameters import zqh_tilelink_atomic_transform_parameter
from zqh_amba.zqh_tilelink_2_axi4_parameters import zqh_tilelink_2_axi4_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_tilelink.zqh_tilelink_order_fix_parameters import zqh_tilelink_order_fix_parameter
from zqh_amba.zqh_axi4_2_tilelink_parameters import zqh_axi4_2_tilelink_parameter
from zqh_amba.zqh_axi4_parameters import zqh_axi4_all_channel_parameter

class zqh_tile_common_front_bus_parameter(parameter):
    def set_par(self):
        super(zqh_tile_common_front_bus_parameter, self).set_par()
        self.par('source_id_num', 16)

class zqh_tile_common_periphery_bus_parameter(parameter):
    def set_par(self):
        super(zqh_tile_common_periphery_bus_parameter, self).set_par()
        self.par('frequency', 1000000000)

class zqh_tile_common_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_tile_common_parameter, self).set_par()
        self.par('num_cores',1)
        self.par('num_plic_ints',32) #id 0 is always disabled
        self.par('support_atomic', 1)
        self.par('mem_agent_do_atomic', 1)
        self.par('node_has_buffer', 1)
        self.par('buf_params', {
            'a': zqh_buffer_parameter.default_p(),
            'd': zqh_buffer_parameter.default_p(),
            'b': zqh_buffer_parameter.default_p(),
            'c': zqh_buffer_parameter.default_p(),
            'e': zqh_buffer_parameter.default_p() 
            })
        self.par('bh_buf_params', {
            'a': zqh_buffer_parameter.normal_p(7),
            'd': zqh_buffer_parameter.normal_p(7),
            'b': zqh_buffer_parameter.normal_p(7),
            'c': zqh_buffer_parameter.normal_p(7),
            'e': zqh_buffer_parameter.normal_p(7) 
            })
        self.par('peri_params',zqh_tile_common_periphery_bus_parameter('peri_params'))
        self.par('sys_bus_axi4',0)
        self.par('llc',zqh_tilelink_llc_parameter())
        self.par('mem_pos',zqh_tilelink_memory_access_pos_parameter())
        self.par('tl_atomic',zqh_tilelink_atomic_transform_parameter())
        self.par('mem_tl2axi4', zqh_tilelink_2_axi4_parameter())
        self.par('mmio_tl2axi4', zqh_tilelink_2_axi4_parameter())
        self.par('tl_order_fix', zqh_tilelink_order_fix_parameter())
        self.par('fbus_order_fix', zqh_tilelink_order_fix_parameter())
        self.par('fbus', zqh_tile_common_front_bus_parameter())
        self.par('fbus_axi4_2_tilelink', zqh_axi4_2_tilelink_parameter())

    def gen_fbus_tl_bundle_p(self, name=''):
        return zqh_tl_bundle_all_channel_parameter(
            name, 
            end_source_id = self.fbus.source_id_num - 1)

    def gen_fbus_axi4_io_Params(self, name=''):
        p = zqh_axi4_all_channel_parameter(name)
        p.aw.id_w = 8
        p.ar.id_w = 8
        return p
