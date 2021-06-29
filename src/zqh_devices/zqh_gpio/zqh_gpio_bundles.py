import sys
import os
from phgl_imp import *

class zqh_gpio_io(bundle):
    def set_par(self):
        super(zqh_gpio_io, self).set_par()
        self.p.par('width', 1)

    def set_var(self):
        super(zqh_gpio_io, self).set_var()
        self.var(vec('port', gen = inout_pu_pin_io, n = self.p.width))

class zqh_gpio_pad(bundle):
    def set_par(self):
        super(zqh_gpio_pad, self).set_par()
        self.p.par('width', 1)

    def set_var(self):
        super(zqh_gpio_pad, self).set_var()
        self.var(vec('port', gen = inoutp, n = self.p.width))

class zqh_gpio_hw_iof_io(bundle):
    def set_par(self):
        super(zqh_gpio_hw_iof_io, self).set_par()
        self.p.par('width', 1)

    def set_var(self):
        super(zqh_gpio_hw_iof_io, self).set_var()
        self.var(vec('port', gen = inout_pin_io, n = self.p.width).flip())
