import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter

class zqh_core_common_wrapper_driven_constants(bundle):
    def set_par(self):
        super(zqh_core_common_wrapper_driven_constants, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_wrapper_driven_constants, self).set_var()
        self.var(inp('hartid', w = self.p.hartid_len))
        self.var(inp('reset_pc', w = self.p.vaddr_bits))
