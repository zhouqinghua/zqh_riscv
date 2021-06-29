import sys
import os
from phgl_imp import *
from .zqh_core_common_multiplier_parameters import zqh_core_common_multiplier_parameter

class zqh_core_common_core_parameter(parameter):
    def set_par(self):
        super(zqh_core_common_core_parameter, self).set_par()
        self.par('xlen', 64)
        self.par('flen', 64)
        self.par('isa_m', 1)
        self.par('isa_a', 1)
        self.par('isa_f', 1)
        self.par('isa_c', 1)
        self.par('isa_custom', 0)
        self.par('use_vm', 0)
        self.par('use_user', 0)
        self.par('use_debug', 1)
        self.par('use_btb', 0)
        self.par('use_bht', 0)
        self.par('use_ras', 0)
        self.par('hartid_len', 4)
        self.par('paddr_bits', 32)
        self.par('inst_bits', 32)
        self.par('num_gprs', 32)

        self.par('csr_num_local_interrupts', 0)
        self.par('csr_have_basic_counters', 1)
        self.par('csr_num_perf_counters', 4)
        self.par('csr_num_breakpoints', 2)
        self.par('csr_event_set_id_bits', 8)
        self.par('csr_misa_wr_en', 1)


    def check_par(self):
        super(zqh_core_common_core_parameter, self).check_par()
        assert(self.xlen in (32, 64))
        self.par('core_data_bits', max(self.xlen, self.flen))
        self.par('isa_d', (1 if (self.flen > 32) else 0) if (self.isa_f) else 0)
        self.par('xbytes', self.xlen // 8)
        self.par('inst_bytes', self.inst_bits // 8)
        self.par('vaddr_bits', min(self.paddr_bits + 1, self.xlen))
        self.par('max_addr_bits', max(self.vaddr_bits, self.paddr_bits))
        self.par('max_paddr_bits', 34 if (self.xlen == 32) else 56)
        self.par('use_user_vm', self.use_vm or self.use_user)

        if (self.use_bht):
            assert(self.use_btb)
        if (self.use_ras):
            assert(self.use_btb)
