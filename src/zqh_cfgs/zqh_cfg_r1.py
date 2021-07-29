import sys
import os
from phgl_imp import *

#zqh_core_r1
class zqh_cfg_r1__basic(configure):
    def set_cfg(self):
        super(zqh_cfg_r1__basic, self).set_cfg()
        self.cfg_all('zqh_core_common_core_parameter', 'use_btb', 1)
        self.cfg_all('zqh_core_common_core_parameter', 'use_bht', 1)
        self.cfg_all('zqh_core_common_core_parameter', 'use_ras', 1)
        self.cfg_all('zqh_core_common_lsu_parameter', 'num_arb_ports', 2)
        self.cfg_all('zqh_core_common_ifu_parameter', 'btb_pre_update_en', 1)

        #lsu has cache, agent no need do atomic
        self.cfg_all('zqh_tile_common_parameter', 'mem_agent_do_atomic', 0)

class zqh_cfg_r1__no_ddr(zqh_cfg_r1__basic):
    def set_cfg(self):
        super(zqh_cfg_r1__no_ddr, self).set_cfg()
        self.cfg_all('zqh_system_common_parameter', 'has_ddr', 0)

class zqh_cfg_r1__no_eth(zqh_cfg_r1__basic):
    def set_cfg(self):
        super(zqh_cfg_r1__no_eth, self).set_cfg()
        self.cfg_all('zqh_system_common_parameter', 'has_eth', 0)

class zqh_cfg_r1__fpga_base(zqh_cfg_r1__basic):
    def set_cfg(self):
        super(zqh_cfg_r1__fpga_base, self).set_cfg()
        self.cfg_all('zqh_system_common_parameter', 'has_ddr', 0)
        self.cfg_all('zqh_system_common_parameter', 'has_eth', 1)
        self.cfg_all('zqh_system_common_parameter', 'has_print_monitor', 1)
        self.cfg_all('zqh_system_common_parameter', 'has_axi4_sram', 0)
        self.cfg_all('zqh_system_common_parameter', 'debug_dumy', 0)
        self.cfg_all('DefaultDebugModuleParams', 'dumy', 0)

class zqh_cfg_r1__fpga_min(zqh_cfg_r1__fpga_base):
    def set_cfg(self):
        super(zqh_cfg_r1__fpga_min, self).set_cfg()
        self.cfg_all('zqh_full_chip_common_parameter', 'imp_mode', 'sim')

        #self.cfg_all('zqh_core_common_core_parameter', 'csr_have_basic_counters', 1)
        #self.cfg_all('zqh_core_common_core_parameter', 'csr_num_perf_counters', 0)

        self.cfg_all('zqh_core_common_ifu_parameter', 'cache_size', 4*1024)
        self.cfg_all('zqh_core_common_ifu_parameter', 'tag_ecc', 'identity')
        self.cfg_all('zqh_core_common_ifu_parameter', 'data_ecc', 'identity')

        self.cfg_all('zqh_core_common_lsu_parameter', 'cache_size', 4*1024)
        self.cfg_all('zqh_core_common_lsu_parameter', 'tag_ecc','identity')
        self.cfg_all('zqh_core_common_lsu_parameter', 'data_ecc','identity')

        self.cfg_all('zqh_core_common_ifu_parameter', 'itim_size', 64*1024)
        self.cfg_all('zqh_core_common_lsu_parameter', 'dtim_size', 64*1024)

        #self.cfg_all('zqh_core_common_wrapper_parameter', 'out_bus_has_buffer', 0)
        #self.cfg_all('zqh_tile_common_parameter', 'node_has_buffer', 0)
        #self.cfg_all('zqh_system_common_parameter', 'device_has_buffer', 0)

class zqh_cfg_r1__fpga_min__xlen_32(zqh_cfg_r1__fpga_min):
    def set_cfg(self):
        super(zqh_cfg_r1__fpga_min__xlen_32, self).set_cfg()
        self.cfg_all('zqh_core_common_core_parameter', 'xlen', 32)
        self.cfg_all('zqh_core_common_core_parameter', 'flen', 32)
        self.cfg_all('zqh_core_common_core_parameter', 'isa_f', 0)
        self.cfg_all('zqh_core_common_lsu_parameter', 'data_ecc_bytes', 4)

class zqh_cfg_r1__lsu_num_flights_4(zqh_cfg_r1__basic):
    def set_cfg(self):
        super(zqh_cfg_r1__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_core_common_lsu_parameter', 'num_flights', 4)

class zqh_cfg_r1__itim_8k__dtim_8k__lsu_num_flights_4(zqh_cfg_r1__basic):
    def set_cfg(self):
        super(zqh_cfg_r1__itim_8k__dtim_8k__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_core_common_ifu_parameter', 'itim_size', 2**13)
        self.cfg_all('zqh_core_common_lsu_parameter', 'dtim_size', 2**13)
        self.cfg_all('zqh_core_common_lsu_parameter', 'num_flights', 4)

class zqh_cfg_r1__num_cores_2__itim_8k__dtim_8k__lsu_num_flights_4(zqh_cfg_r1__itim_8k__dtim_8k__lsu_num_flights_4):
    def set_cfg(self):
        super(zqh_cfg_r1__num_cores_2__itim_8k__dtim_8k__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_tile_common_parameter', 'num_cores', 2)

class zqh_cfg_r1__num_cores_4__itim_8k__dtim_8k__lsu_num_flights_4(zqh_cfg_r1__itim_8k__dtim_8k__lsu_num_flights_4):
    def set_cfg(self):
        super(zqh_cfg_r1__num_cores_4__itim_8k__dtim_8k__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_tile_common_parameter', 'num_cores', 4)

class zqh_cfg_r1__xlen_32__itim_8k__dtim_8k__lsu_num_flights_4(zqh_cfg_r1__basic):
    def set_cfg(self):
        super(zqh_cfg_r1__xlen_32__itim_8k__dtim_8k__lsu_num_flights_4, self).set_cfg()
        self.cfg_all('zqh_core_common_ifu_parameter', 'itim_size', 2**13)
        self.cfg_all('zqh_core_common_lsu_parameter', 'dtim_size', 2**13)
        self.cfg_all('zqh_core_common_lsu_parameter', 'num_flights', 4)
        self.cfg_all('zqh_core_common_core_parameter', 'xlen', 32)
