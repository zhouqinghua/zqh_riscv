import sys
import os
from phgl_imp import *
from .zqh_core_common_misc import D_CONSTS
from .zqh_core_common_misc import M_CONSTS
from .zqh_core_common_lsu_parameters import zqh_core_common_lsu_parameter

class zqh_core_common_lsu_mem_req(bundle):
    def set_par(self):
        super(zqh_core_common_lsu_mem_req, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_common_lsu_mem_req,self).set_var()
        self.var(bits('cmd', w = M_CONSTS.SZ))
        self.var(bits('type', w = D_CONSTS.SZ_MT))
        self.var(bits('tag', w = self.p.req_tag_bits))
        self.var(bits('addr', w = self.p.max_addr_bits))
        self.var(bits('error'))
        self.var(bits('data', w = self.p.core_data_bits))
        self.var(bits('mask', w = self.p.core_data_bits//8))

class zqh_core_common_lsu_exception_pair(bundle):
    def set_var(self):
        super(zqh_core_common_lsu_exception_pair, self).set_var()
        self.var(bits('ld'))
        self.var(bits('st'))

class zqh_core_common_lsu_exceptions(bundle):
    def set_var(self):
        super(zqh_core_common_lsu_exceptions, self).set_var()
        self.var(zqh_core_common_lsu_exception_pair('ma'))
        self.var(zqh_core_common_lsu_exception_pair('pf'))
        self.var(zqh_core_common_lsu_exception_pair('ae'))

class zqh_core_common_lsu_mem_resp(bundle):
    def set_par(self):
        super(zqh_core_common_lsu_mem_resp, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_common_lsu_mem_resp,self).set_var()
        self.var(bits('tag', w = self.p.req_tag_bits))
        self.var(bits('type', w = D_CONSTS.SZ_MT))
        self.var(bits('replay'))
        self.var(bits('slow')) #means from tile's d_resp(uncache)
        self.var(bits('has_data'))
        self.var(bits('data', w = self.p.core_data_bits))
        self.var(bits('data_word_bypass', w = self.p.core_data_bits))
        self.var(bits('data_no_shift', w = self.p.core_data_bits))
        self.var(zqh_core_common_lsu_exceptions('xcpt'))

class zqh_core_common_lsu_write_data(bundle):
    def set_par(self):
        super(zqh_core_common_lsu_write_data, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_common_lsu_write_data, self).set_var()
        self.var(bits('data', w = self.p.core_data_bits))
        self.var(bits('mask', w = self.p.core_data_bits//8))

class zqh_core_common_lsu_hpm_events(bundle):
    def set_var(self):
        super(zqh_core_common_lsu_hpm_events, self).set_var()
        self.var(bits('refill'))
        self.var(bits('write_back'))

class zqh_core_common_lsu_mem_io(bundle):
    def set_par(self):
        super(zqh_core_common_lsu_mem_io, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_common_lsu_mem_io,self).set_var()
        self.var(ready_valid('req', zqh_core_common_lsu_mem_req).flip())
        self.var(inp('s1_kill'))
        self.var(zqh_core_common_lsu_write_data('s1_data').as_input())
        self.var(valid('resp', gen = zqh_core_common_lsu_mem_resp))
        self.var(outp('slow_kill'))
        self.var(outp('busy'))
        self.var(zqh_core_common_lsu_hpm_events('events').as_output())

class zqh_core_common_lsu_errors_io(bundle):
    def set_par(self):
        super(zqh_core_common_lsu_errors_io, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def set_var(self):
        super(zqh_core_common_lsu_errors_io, self).set_var()
        self.var(valid('correctable', gen = bits, w = self.p.paddr_bits))
        self.var(valid('uncorrectable', gen = bits, w = self.p.paddr_bits))
        self.var(valid('bus', gen = bits, w = self.p.paddr_bits))
