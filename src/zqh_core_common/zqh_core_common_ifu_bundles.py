import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter
from .zqh_core_common_misc import IFU_CONSTS
from .zqh_core_common_misc import M_CONSTS
from .zqh_core_common_misc import D_CONSTS
from .zqh_core_common_btb_bundles import zqh_core_common_btb_update
from .zqh_core_common_btb_bundles import zqh_core_common_bht_update
from .zqh_core_common_btb_bundles import zqh_core_common_bht_resp

class zqh_core_common_ifu_cpu_req(bundle):
    def set_par(self):
        super(zqh_core_common_ifu_cpu_req, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_ifu_cpu_req, self).set_var()
        self.var(bits('cmd', w = IFU_CONSTS.SZ))
        self.var(bits('vaddr', w = self.p.vaddr_bits))
        self.var(bits('error'))

class zqh_core_common_ifu_exception_inst(bundle):
    def set_var(self):
        super(zqh_core_common_ifu_exception_inst, self).set_var()
        self.var(bits('inst'))

class zqh_core_common_ifu_exceptions(bundle):
    def set_var(self):
        super(zqh_core_common_ifu_exceptions, self).set_var()
        self.var(zqh_core_common_ifu_exception_inst('ae'))


class zqh_core_common_ifu_cpu_resp(bundle):
    def set_par(self):
        super(zqh_core_common_ifu_cpu_resp, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_ifu_cpu_resp, self).set_var()
        self.var(bits('inst', w = self.p.inst_bits))
        self.var(bits('btb_hit', w =  2 if (self.p.isa_c) else 1))
        self.var(bits('taken', w =  2 if (self.p.isa_c) else 1))
        self.var(zqh_core_common_bht_resp('bht_info'))
        self.var(bits('iv', w = 2 if (self.p.isa_c) else 1))
        self.var(bits('pc', w = self.p.vaddr_bits))
        self.var(zqh_core_common_ifu_exceptions('xcpt'))

class zqh_core_common_ifu_hpm_events(bundle):
    def set_var(self):
        super(zqh_core_common_ifu_hpm_events, self).set_var()
        self.var(bits('refill'))

class zqh_core_common_ifu_cpu_io(bundle):
    def set_par(self):
        super(zqh_core_common_ifu_cpu_io, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_ifu_cpu_io, self).set_var()
        self.var(valid('req', gen = zqh_core_common_ifu_cpu_req).flip())
        self.var(ready_valid('resp', gen = zqh_core_common_ifu_cpu_resp))
        if (self.p.use_btb):
            self.var(valid('btb_update', gen = zqh_core_common_btb_update).flip())
        if (self.p.use_bht):
            self.var(valid('bht_update', gen = zqh_core_common_bht_update).flip())
        self.var(zqh_core_common_ifu_hpm_events('events').as_output())
        self.var(inp('rv64'))

class zqh_core_common_ifu_icache_io(bundle):
    def set_var(self):
        super(zqh_core_common_ifu_icache_io, self).set_var()
        self.var(ready_valid('req', gen = zqh_core_common_ifu_cpu_req).flip())
        self.var(inp('s1_kill'))
        self.var(valid('resp', gen = zqh_core_common_ifu_cpu_resp))
        self.var(outp('valid_s1'))
        self.var(zqh_core_common_ifu_hpm_events('events').as_output())

class zqh_core_common_ifu_slave_req(bundle):
    def set_par(self):
        super(zqh_core_common_ifu_slave_req, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_ifu_slave_req,self).set_var()
        self.var(bits('addr', w = self.p.max_addr_bits))
        self.var(bits('cmd', w = M_CONSTS.SZ))
        self.var(bits('typ', w = D_CONSTS.SZ_MT))
        self.var(bits('data', w = self.p.core_data_bits))
        self.var(bits('mask', w = self.p.core_data_bits//8))

class zqh_core_common_ifu_slave_resp(bundle):
    def set_par(self):
        super(zqh_core_common_ifu_slave_resp, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_ifu_slave_resp,self).set_var()
        self.var(bits('replay'))
        self.var(bits('data', w = self.p.core_data_bits))

class zqh_core_common_ifu_slave_io(bundle):
    def set_var(self):
        super(zqh_core_common_ifu_slave_io,self).set_var()
        self.var(ready_valid('req', gen = zqh_core_common_ifu_slave_req).flip())
        self.var(valid('resp', gen = zqh_core_common_ifu_slave_resp))
