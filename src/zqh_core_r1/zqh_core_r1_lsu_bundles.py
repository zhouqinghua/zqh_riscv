import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_misc import D_CONSTS
from zqh_core_common.zqh_core_common_misc import M_CONSTS
from zqh_core_common.zqh_core_common_lsu_parameters import zqh_core_common_lsu_parameter
from zqh_tilelink.zqh_tilelink_meta_data import zqh_client_metadata
from zqh_core_common.zqh_core_common_lsu_bundles import *

class zqh_core_r1_lsu_dcache_metadata(bundle):
    def set_par(self):
        super(zqh_core_r1_lsu_dcache_metadata, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_r1_lsu_dcache_metadata, self).set_var()
        self.var(zqh_client_metadata('coh'))
        self.var(bits('tag', w = self.p.tag_bits))

class zqh_core_r1_lsu_dcache_data_req(bundle):
    def set_par(self):
        super(zqh_core_r1_lsu_dcache_data_req, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_r1_lsu_dcache_data_req, self).set_var()
        self.var(bits('addr', w = max(self.p.untag_bits, self.p.dtim_addr_bits)))
        self.var(bits('write'))
        self.var(bits(
            'wdata',
            w = self.p.data_enc_bits * self.p.row_bytes // self.p.data_ecc_bytes))
        self.var(bits('poison'))
        self.var(bits('wordMask', w = self.p.row_bytes // self.p.word_bytes))
        self.var(bits('eccMask', w = self.p.word_bytes // self.p.data_ecc_bytes))
        self.var(bits('way_en', w = self.p.num_ways))

class zqh_core_r1_lsu_dcache_metadata_req(bundle):
    def set_par(self):
        super(zqh_core_r1_lsu_dcache_metadata_req, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_r1_lsu_dcache_metadata_req, self).set_var()
        self.var(bits('write'))
        self.var(bits('addr', w = self.p.vaddr_bits))
        self.var(bits('way_en', w = self.p.num_ways))
        self.var(zqh_core_r1_lsu_dcache_metadata('data'))

class zqh_core_r1_lsu_dtim_data_req(bundle):
    def set_par(self):
        super(zqh_core_r1_lsu_dtim_data_req, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_r1_lsu_dtim_data_req, self).set_var()
        self.var(bits('addr', w = self.p.dtim_addr_bits))
        self.var(bits('write'))
        self.var(bits(
            'wdata',
            w = self.p.data_enc_bits * self.p.dtim_data_bytes // self.p.data_ecc_bytes))
        self.var(bits('poison'))
        self.var(bits('eccMask', w = self.p.dtim_data_bytes // self.p.data_ecc_bytes))
