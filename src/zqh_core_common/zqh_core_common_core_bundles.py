import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_cpu_io
from .zqh_core_common_lsu_bundles import zqh_core_common_lsu_mem_io
from zqh_fpu.zqh_fpu_bundles import zqh_fpu_core_io
from zqh_rocc.zqh_rocc_bundles import zqh_rocc_core_io
from .zqh_core_common_csr_bundles import zqh_core_common_csr_traced_instruction
from .zqh_core_common_interrupts_bundles import zqh_core_common_interrupts
from .zqh_core_common_btb_bundles import zqh_core_common_btb_update
from .zqh_core_common_btb_bundles import zqh_core_common_bht_update

class zqh_core_common_core_io(bundle):
    def set_par(self):
        super(zqh_core_common_core_io, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_core_io, self).set_var()
        self.var(inp('hartid',w = self.p.hartid_len))
        self.var(inp('reset_pc',w = self.p.paddr_bits))
        self.var(zqh_core_common_interrupts('interrupts').as_input())
        self.var(zqh_core_common_ifu_cpu_io('ifu').flip())
        self.var(zqh_core_common_lsu_mem_io('lsu').flip())
        self.var(zqh_fpu_core_io('fpu').flip())
        self.var(zqh_rocc_core_io('rocc').flip())
        self.var(vec(
            'csr_trace',
            gen = zqh_core_common_csr_traced_instruction,
            n = 1).as_output())
