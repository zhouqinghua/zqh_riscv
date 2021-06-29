import sys
import os
from phgl_imp import *

class zqh_pwm_io(bundle):
    def set_par(self):
        super(zqh_pwm_io, self).set_par()
        self.p.par('ncmp', 4)

    def set_var(self):
        super(zqh_pwm_io, self).set_var()
        self.var(outp('do', w = self.p.ncmp))

class zqh_pwm_pad(bundle):
    def set_par(self):
        super(zqh_pwm_pad, self).set_par()
        self.p.par('ncmp', 4)

    def set_var(self):
        super(zqh_pwm_pad, self).set_var()
        self.var(outp('do', w = self.p.ncmp))
