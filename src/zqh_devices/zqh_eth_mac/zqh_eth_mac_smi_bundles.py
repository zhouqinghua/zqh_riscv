import sys
import os
from phgl_imp import *

class zqh_eth_mac_phy_smi_io(bundle):
    def set_var(self):
        super(zqh_eth_mac_phy_smi_io, self).set_var()
        self.var(outp('mdc'))
        self.var(inout_pin_io('mdio'))

class zqh_eth_mac_phy_smi_pad(bundle):
    def set_var(self):
        super(zqh_eth_mac_phy_smi_pad, self).set_var()
        self.var(outp('mdc'))
        self.var(inoutp('mdio'))
