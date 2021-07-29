import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_common.zqh_replacement import zqh_random_replacement

class zqh_core_common_lsu_parameter(zqh_tilelink_node_module_parameter, zqh_core_common_core_parameter):
    def set_par(self):
        super(zqh_core_common_lsu_parameter, self).set_par()
        self.par('cache_size', 16*1024)
        self.par('cache_block_size', 64)

        self.par('num_ways', 4)
        self.par('num_flights', 2) #source 0 is cache refill, the other is uncache reqs
        self.par('tag_ecc', 'secded')
        self.par('data_ecc', 'secded')
        self.par('data_ecc_bytes', 8)

        self.par('lrsc_back_off', 3) ## disallow LRSC reacquisition briefly

        self.par('slave_ready_stall_threshold', 5)
        self.par('block_threshold', 15)

        self.par('dtim_base', 0x60200000)
        self.par('dtim_size', 0)

        self.par('cache_l1_flush_base', 0x02010000)
        self.par('cache_l1_flush_size', 0x1000)
        self.par('cache_l1_flush_slave_offset', 0x0300000)

        self.par('num_arb_ports', 1)
        self.par('lrsc_cycles', 128)

    def check_par(self):
        super(zqh_core_common_lsu_parameter, self).check_par()
        self.par('num_sets', (self.cache_size // self.cache_block_size) // self.num_ways)
        self.par('block_off_bits', log2_up(self.cache_block_size))
        self.par('idx_bits', log2_up(self.num_sets))
        self.par('untag_bits', self.block_off_bits + self.idx_bits)
        self.par('tag_bits', self.paddr_bits - self.untag_bits)

        self.par('word_bits', self.core_data_bits)
        self.par('word_bytes', self.core_data_bits//8)
        self.par('word_off_bits', log2_up(self.word_bytes))

        self.par('data_ecc_bits', self.data_ecc_bytes * 8)
        self.par('data_enc_bits', self.data_code().width(self.data_ecc_bits))

        self.par('dtim_addr_bits', log2_up(self.dtim_size))
        self.par('dtim_data_bits', self.core_data_bits)
        self.par('dtim_data_bytes', self.core_data_bits//8)
        self.par('dtim_data_off_bits', log2_up(self.dtim_data_bytes))

        self.par('cache_l1_addr_bits', log2_up(self.cache_l1_flush_size))
        if (self.num_sets > 0):
            assert(is_pow_of_2(self.num_sets))
        assert(self.num_flights >= 2)
        if (self.use_vm):
            assert(self.untag_bits <= 12) #min 4KB page
        assert(self.slave_ready_stall_threshold <= 15)
        assert(self.block_threshold <= 15)
        if (self.dtim_size != 0):
            assert(is_pow_of_2(self.dtim_size))

        assert(self.data_ecc_bytes <= (self.core_data_bits//8))

        self.par(
            'req_tag_bits',
            log2_ceil(self.num_gprs) + 1 + log2_ceil(self.num_arb_ports))
    def tag_code(self):
        return ecc_code(self.tag_ecc)

    def data_code(self):
        return ecc_code(self.data_ecc)

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name, end_source_id = self.num_flights - 1)
