from phgl_imp import *
from .zqh_usb_ctrl_parameters import zqh_usb_ctrl_parameter

class zqh_usb_ctrl_utmi_tx_data(bundle):
    def set_par(self):
        super(zqh_usb_ctrl_utmi_tx_data, self).set_par()
        self.p.par('dw', 8)

    def set_var(self):
        super(zqh_usb_ctrl_utmi_tx_data, self).set_var()
        self.var(bits('data', w = self.p.dw))
        self.var(bits('be', w = self.p.dw//8))

class zqh_usb_ctrl_utmi_rx_data(bundle):
    def set_par(self):
        super(zqh_usb_ctrl_utmi_rx_data, self).set_par()
        self.p.par('dw', 8)

    def set_var(self):
        super(zqh_usb_ctrl_utmi_rx_data, self).set_var()
        self.var(bits('data', w = self.p.dw))
        self.var(bits('be', w = self.p.dw//8))
        self.var(bits('ep', w = 4))
