import sys
import os
from phgl_imp import *
from .zqh_debug_misc import DMIConsts

class DMIAccessUpdate(bundle):
    def set_par(self):
        super(DMIAccessUpdate, self).set_par()
        self.p.par('addrBits', None)

    def set_var(self):
        super(DMIAccessUpdate, self).set_var()
        self.var(bits('addr', w = self.p.addrBits))
        self.var(bits('data', w = DMIConsts.dmiDataSize))
        self.var(bits('op', w = DMIConsts.dmiOpSize))

class DMIAccessCapture(bundle):
    def set_par(self):
        super(DMIAccessCapture, self).set_par()
        self.p.par('addrBits', None)

    def set_var(self):
        super(DMIAccessCapture, self).set_var()
        self.var(bits('addr', w = self.p.addrBits))
        self.var(bits('data', w = DMIConsts.dmiDataSize))
        self.var(bits('resp', w = DMIConsts.dmiRespSize))

class DTMInfo(bundle):
    def set_var(self):
        super(DTMInfo, self).set_var()
        self.var(bits('reserved1', w = 15))
        self.var(bits('dmireset'))
        self.var(bits('reserved0', w = 1))
        self.var(bits('dmiIdleCycles', w = 3))
        self.var(bits('dmiStatus', w = 2))
        self.var(bits('debugAddrBits', w = 6))
        self.var(bits('debugVersion', w = 4))

#/** A wrapper around JTAG providing a reset signal and manufacturer id. */
class SystemJTAGIO(bundle):
    def set_var(self):
        super(SystemJTAGIO, self).set_var()
        self.var(JTAGIO('jtag', hasTRSTn = 0).flip())
        self.var(inp('reset_i'))
        self.var(inp('mfr_id', w = 11))
