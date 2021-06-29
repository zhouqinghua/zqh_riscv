#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/Multiplier.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
class zqh_core_common_multiplier_parameter(parameter):
    def set_par(self):
        self.par('mul_unroll', 1)
        self.par('div_unroll', 1)
        self.par('mul_early_out', 1)
        self.par('div_early_out', 1)

    def check_par(self):
        assert(self.mul_unroll > 0)
        assert(self.div_unroll > 0)
