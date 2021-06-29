import sys
import os
from phgl_imp import *

#core_e1
class zqh_cfg_e1__basic(configure):
    def set_cfg(self):
        super(zqh_cfg_e1__basic, self).set_cfg()
        self.cfg_all('zqh_core_common_ifu_parameter', 'mem_latency', 2)

        #lsu no cache, agent should do atomic
        self.cfg_all('zqh_tile_common_parameter', 'mem_agent_do_atomic', 1)

        self.cfg_all('zqh_core_common_wrapper_parameter', 'out_bus_has_buffer', 0)
        self.cfg_all('zqh_tile_common_parameter', 'node_has_buffer', 0)
        self.cfg_all('zqh_system_common_parameter', 'device_has_buffer', 0)

class zqh_cfg_e1__itim_8k__dtim_8k__lsu_num_flights_4(zqh_cfg_e1__basic):
    def set_cfg(self):
        super(zqh_cfg_e1__itim_8k__dtim_8k__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_core_common_lsu_parameter', 'num_arb_ports', 3)
        self.cfg_all('zqh_core_common_ifu_parameter', 'itim_size', 2**13)
        self.cfg_all('zqh_core_common_lsu_parameter', 'dtim_size', 2**13)
        self.cfg_all('zqh_core_common_lsu_parameter', 'num_flights', 4)

class zqh_cfg_e1__num_cores_2__itim_8k__dtim_8k__lsu_num_flights_4(zqh_cfg_e1__itim_8k__dtim_8k__lsu_num_flights_4):
    def set_cfg(self):
        super(zqh_cfg_e1__num_cores_2__itim_8k__dtim_8k__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_tile_common_parameter', 'num_cores', 2)

class zqh_cfg_e1__num_cores_4__itim_8k__dtim_8k__lsu_num_flights_4(zqh_cfg_e1__itim_8k__dtim_8k__lsu_num_flights_4):
    def set_cfg(self):
        super(zqh_cfg_e1__num_cores_4__itim_8k__dtim_8k__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_tile_common_parameter', 'num_cores', 4)

class zqh_cfg_e1__xlen_32__itim_8k__dtim_8k__lsu_num_flights_4(zqh_cfg_e1__basic):
    def set_cfg(self):
        super(zqh_cfg_e1__xlen_32__itim_8k__dtim_8k__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_core_common_lsu_parameter', 'num_arb_ports', 3)
        self.cfg_all('zqh_core_common_ifu_parameter', 'itim_size', 2**13)
        self.cfg_all('zqh_core_common_lsu_parameter', 'dtim_size', 2**13)
        self.cfg_all('zqh_core_common_lsu_parameter', 'num_flights', 4)
        self.cfg_all('zqh_core_common_core_parameter', 'xlen', 32)
