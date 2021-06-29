from phgl_imp import *
from .zqh_usb_phy_parameters import zqh_usb_phy_parameter

class zqh_usb_phy_reg_io(csr_reg_io):
    def set_par(self):
        super(zqh_usb_phy_reg_io, self).set_par()
        self.p.par('addr_bits', 8)
        self.p.par('data_bits', 32)

class zqh_usb_phy_io(bundle):
    def set_var(self):
        super(zqh_usb_phy_io, self).set_var()
        self.var(inout_pin_io('dp'))
        self.var(inout_pin_io('dm'))

class zqh_usb_phy_pad(bundle):
    def set_var(self):
        super(zqh_usb_phy_pad, self).set_var()
        self.var(inoutp('dp'))
        self.var(inoutp('dm'))

