import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_tile_common.zqh_tile_common_parameters import zqh_tile_common_front_bus_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_buffer_parameter
from zqh_amba.zqh_tilelink_2_axi4_parameters import zqh_tilelink_2_axi4_parameter

class zqh_system_common_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_system_common_parameter, self).set_par()
        self.par('imp_mode','sim')#sim/fpga/asic
        self.par('fbus', zqh_tile_common_front_bus_parameter())
        self.par('num_ext_ints',2)
        self.par('device_has_buffer',1)
        self.par('has_ddr',1)
        self.par('has_eth',1)
        self.par('has_axi4_sram',1)
        self.par('has_print_monitor',1)
        self.par('debug_dumy',0)
        self.par('tl_sram_size',64*1024)
        self.par('tl_io_sram_size',1024)
        self.par('axi4_sram_size',1024)
        self.par('buf_params', {
            'a': zqh_buffer_parameter.default_p(),
            'd': zqh_buffer_parameter.default_p(),
            'b': zqh_buffer_parameter.default_p(),
            'c': zqh_buffer_parameter.default_p(),
            'e': zqh_buffer_parameter.default_p() 
            })
        self.par('buf_axi4_params', {
            'ar': zqh_buffer_parameter.default_p(),
            'aw': zqh_buffer_parameter.default_p(),
            'w': zqh_buffer_parameter.default_p(),
            'r': zqh_buffer_parameter.default_p(),
            'b': zqh_buffer_parameter.default_p() 
            })
        self.par('mem_tl2axi4_params', zqh_tilelink_2_axi4_parameter())
        self.par('gpio0_ports_num', 32)
        self.par('gpio1_ports_num', 32)

    def gen_fbus_tl_bundle_p(self, name=''):
        return zqh_tl_bundle_all_channel_parameter(
            name,
            end_source_id =
            self.fbus.source_id_num - 1)
