import sys
import os
from phgl_imp import *

class zqh_spi_io(bundle):
    def set_par(self):
        super(zqh_spi_io, self).set_par()
        self.p.par('cs_width', 1)

    def set_var(self):
        super(zqh_spi_io, self).set_var()
        self.var(outp('sck'))
        self.var(outp('cs', w = self.p.cs_width))
        self.var(vec('dq', inout_pin_io, 4))

class zqh_spi_pad(bundle):
    def set_par(self):
        super(zqh_spi_pad, self).set_par()
        self.p.par('cs_width', 1)

    def set_var(self):
        super(zqh_spi_pad, self).set_var()
        self.var(outp('sck'))
        self.var(outp('cs', w = self.p.cs_width))
        self.var(vec('dq', inoutp, 4))

class zqh_spi_tx_fifo_data(bundle):
    def set_var(self):
        super(zqh_spi_tx_fifo_data, self).set_var()
        self.var(bits('data', w = 8))
        self.var(bits('proto', w = 2))
        self.var(bits('endian'))
        self.var(bits('dir'))
        self.var(bits('len', w = 4))
        self.var(bits('csmode', w = 2))
        self.var(bits('pol'))
        self.var(bits('pha'))
