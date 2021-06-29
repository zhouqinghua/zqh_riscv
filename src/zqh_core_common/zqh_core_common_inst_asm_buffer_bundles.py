import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_exceptions
from .zqh_core_common_btb_bundles import zqh_core_common_bht_resp

class zqh_core_common_inst_asm_buffer_data(bundle):
    def set_par(self):
        super(zqh_core_common_inst_asm_buffer_data, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_inst_asm_buffer_data, self).set_var()
        self.var(bits('inst', w = self.p.inst_bits))
        self.var(bits('btb_hit'))
        self.var(bits('taken'))
        self.var(zqh_core_common_bht_resp('bht_info'))
        self.var(bits('pc', w = self.p.vaddr_bits))
        self.var(bits('rvc'))
        self.var(zqh_core_common_ifu_exceptions('xcpt'))
