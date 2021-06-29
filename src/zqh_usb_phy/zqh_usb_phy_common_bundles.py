from phgl_imp import *
from .zqh_usb_phy_parameters import zqh_usb_phy_parameter

class zqh_usb_utmi_l0(bundle):
    def set_par(self):
        super(zqh_usb_utmi_l0, self).set_par()
        self.p.par('dw', 8)

    def set_var(self):
        super(zqh_usb_utmi_l0, self).set_var()
        self.var(outp('CLK'))
        self.var(inp('Reset'))
        self.var(inp('XcvrSelect'))
        self.var(inp('TermSelect'))
        self.var(inp('SuspendM'))
        self.var(outp('LineState', w = 2))
        self.var(inp('OpMode', w = 2))

        self.var(inp('DataIn', w = self.p.dw))
        self.var(inp('TXValid'))
        if (self.p.dw > 8):
            self.var(inp('TXValidH'))
        self.var(outp('TXReady'))

        self.var(outp('DataOut', w = self.p.dw))
        self.var(outp('RXValid'))
        if (self.p.dw > 8):
            self.var(outp('RXValidH'))
        self.var(outp('RXActive'))
        self.var(outp('RXError'))

class zqh_usb_utmi_l1(zqh_usb_utmi_l0):
    def set_var(self):
        super(zqh_usb_utmi_l1, self).set_var()
        self.var(inp('IdPullup'))
        self.var(inp('DpPulldown'))
        self.var(inp('DmPulldown'))

        self.var(inp('DrvVbus'))
        self.var(inp('ChrgVbus'))
        self.var(inp('DischrgVbus'))

        self.var(inp('TxBitstuffEnable'))
        if (self.p.dw > 8):
            self.var(inp('TxBitstuffEnableH'))

        self.var(inp('Tx_Enable_N'))
        self.var(inp('Tx_DAT'))
        self.var(inp('Tx_SE0'))
        self.var(inp('FsLsSerialMode'))

        self.var(outp('HostDisconnect'))

        self.var(outp('IdDig'))

        self.var(outp('AValid'))
        self.var(outp('BValid'))
        self.var(outp('VbusValid'))
        self.var(outp('SessEnd'))

        self.var(outp('Rx_DP'))
        self.var(outp('Rx_DM'))
        self.var(outp('Rx_RCV'))

class zqh_usb_phy_tx_data(bundle):
    def set_par(self):
        super(zqh_usb_phy_tx_data, self).set_par()
        self.p.par('dw', 8)

    def set_var(self):
        super(zqh_usb_phy_tx_data, self).set_var()
        self.var(bits('data', w = self.p.dw))
        self.var(bits('sync'))
        self.var(bits('eop'))

class zqh_usb_phy_rx_data(bundle):
    def set_par(self):
        super(zqh_usb_phy_rx_data, self).set_par()
        self.p.par('dw', 8)

    def set_var(self):
        super(zqh_usb_phy_rx_data, self).set_var()
        self.var(bits('data', w = self.p.dw))
        self.var(bits('error'))
        self.var(bits('sync'))
        self.var(bits('eop'))
