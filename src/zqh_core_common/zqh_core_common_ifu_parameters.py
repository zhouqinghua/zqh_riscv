import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter

class zqh_core_common_ifu_parameter(zqh_tilelink_node_module_parameter, zqh_core_common_core_parameter):
    def set_par(self):
        super(zqh_core_common_ifu_parameter, self).set_par()
        self.par('cache_size', 16*1024)
        self.par('cache_block_size', 64)

        self.par('num_ways', 4)
        self.par('num_flights', 1)
        self.par('num_sets', (self.cache_size // self.cache_block_size) // self.num_ways)
        self.par('num_ras', 8)
        self.par('mem_latency', 2)
        self.par('qout_entryies', 5)
        self.par('tag_ecc', 'secded')
        self.par('data_ecc', 'secded')
        self.par('qout_bypass_en', 1)
        self.par('btb_pre_update_en', 1)

        #uncacheable fetch will drop the refill line after hit
        self.par('uc_invalid_en', 0)

        self.par('itim_base', 0x60000000)
        self.par('itim_size', 0)

    def check_par(self):
        super(zqh_core_common_ifu_parameter, self).check_par()
        self.par('idx_bits', log2_ceil(self.num_sets * self.cache_block_size))
        self.par('tag_bits', self.max_addr_bits - self.idx_bits)
        self.par('line_off_bits', log2_ceil(self.cache_block_size))
        self.par('inst_off_bits', log2_ceil(self.inst_bytes))

        self.par('itim_addr_bits', log2_up(self.itim_size))

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(
            name,
            end_source_id = self.num_flights - 1)
