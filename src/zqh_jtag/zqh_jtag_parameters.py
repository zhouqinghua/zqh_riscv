#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/jtag/*.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *

class zqh_jtag_parameter(parameter):
    def set_par(self):
        super(zqh_jtag_parameter, self).set_par()
        self.par('hasTRSTn', 0)
        self.par('irLength', 8)
        self.par('initialInstruction', 0)
