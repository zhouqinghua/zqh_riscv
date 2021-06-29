import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter

class zqh_core_common_interrupts(bundle):
    def set_par(self):
        super(zqh_core_common_interrupts, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_interrupts,self).set_var()
        self.var(bits('debug'))
        self.var(bits('mtip'))
        self.var(bits('msip'))
        self.var(bits('meip'))
        if (self.p.use_vm):
            self.var(bits('seip'))
        self.var(vec('lip', gen = bits, n = self.p.csr_num_local_interrupts))
