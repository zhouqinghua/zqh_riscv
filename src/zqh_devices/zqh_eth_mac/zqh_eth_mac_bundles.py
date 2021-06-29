from phgl_imp import *
from .zqh_eth_mac_parameters import zqh_eth_mac_parameter
from .zqh_eth_mac_smi_bundles import *

class zqh_eth_mac_phy_gmii_tx_io(bundle):
    def set_var(self):
        super(zqh_eth_mac_phy_gmii_tx_io, self).set_var()
        self.var(outp('gclk'))
        self.var(inp('clk'))
        self.var(outp('en'))
        self.var(outp('d', w = 8))
        self.var(outp('err'))

class zqh_eth_mac_phy_gmii_rx_io(bundle):
    def set_var(self):
        super(zqh_eth_mac_phy_gmii_rx_io, self).set_var()
        self.var(inp('clk'))
        self.var(inp('dv'))
        self.var(inp('d', w = 8))
        self.var(inp('err'))

class zqh_eth_mac_phy_gmii_cscd_io(bundle):
    def set_var(self):
        super(zqh_eth_mac_phy_gmii_cscd_io, self).set_var()
        self.var(inp('cs'))
        self.var(inp('cd'))

class zqh_eth_mac_phy_gmii_io(bundle):
    def set_var(self):
        super(zqh_eth_mac_phy_gmii_io, self).set_var()
        self.var(zqh_eth_mac_phy_gmii_tx_io('tx'))
        self.var(zqh_eth_mac_phy_gmii_rx_io('rx'))
        self.var(zqh_eth_mac_phy_gmii_cscd_io('cscd'))

class zqh_eth_mac_phy_gmii_smi_io(bundle):
    def set_var(self):
        super(zqh_eth_mac_phy_gmii_smi_io, self).set_var()
        self.var(zqh_eth_mac_phy_gmii_io('gmii'))
        self.var(zqh_eth_mac_phy_smi_io('smi'))
        self.var(outp('reset_n'))

class zqh_eth_mac_phy_gmii_smi_pad(bundle):
    def set_var(self):
        super(zqh_eth_mac_phy_gmii_smi_pad, self).set_var()
        self.var(zqh_eth_mac_phy_gmii_io('gmii'))
        self.var(zqh_eth_mac_phy_smi_pad('smi'))
        self.var(outp('reset_n'))

class zqh_eth_mac_tx_fifo_data_bundle(bundle):
    def set_par(self):
        super(zqh_eth_mac_tx_fifo_data_bundle, self).set_par()
        self.p.par('data_width', 32)

    def set_var(self):
        super(zqh_eth_mac_tx_fifo_data_bundle, self).set_var()
        self.var(bits('data', w = self.p.data_width))
        self.var(bits('start', w = self.p.data_width//8))
        self.var(bits('end', w = self.p.data_width//8))
        self.var(bits('sai'))
        self.var(bits('crc'))
        self.var(bits('pad'))
        self.var(bits('ack'))

class zqh_eth_mac_tx_status_bundle(bundle):
    def set_var(self):
        super(zqh_eth_mac_tx_status_bundle, self).set_var()
        self.var(bits('retry'))
        self.var(bits('abort'))
        self.var(bits('done'))
        self.var(bits('retry_limit'))
        self.var(bits('defer'))
        self.var(bits('cs_lost'))
        self.var(bits('too_long'))
        self.var(bits('defer_abort'))
        self.var(bits('retry_cnt', w = 4))

class zqh_eth_mac_rx_fifo_data_bundle(bundle):
    def set_par(self):
        super(zqh_eth_mac_rx_fifo_data_bundle, self).set_par()
        self.p.par('data_width', 32)

    def set_var(self):
        super(zqh_eth_mac_rx_fifo_data_bundle, self).set_var()
        self.var(bits('data', w = self.p.data_width))
        self.var(bits('start'))
        self.var(bits('end', w = self.p.data_width//8))
        self.var(bits('is_status'))

class zqh_eth_mac_rx_status_bundle(bundle):
    def set_var(self):
        super(zqh_eth_mac_rx_status_bundle, self).set_var()
        self.var(bits('abort'))
        self.var(bits('crc_err'))
        self.var(bits('invalid_symbol'))
        self.var(bits('short_frame'))
        self.var(bits('long_frame'))
        self.var(bits('dribble_nibble'))
        self.var(bits('da_miss'))
        self.var(bits('pause_frame'))
        self.var(bits('late_collision'))

class zqh_eth_mac_rx_fifo_data_with_status_bundle(zqh_eth_mac_rx_fifo_data_bundle):
    def set_var(self):
        super(zqh_eth_mac_rx_fifo_data_with_status_bundle, self).set_var()
        self.var(zqh_eth_mac_rx_status_bundle('status'))

class zqh_eth_mac_tx_bd_bundle(bundle):
    def set_var(self):
        super(zqh_eth_mac_tx_bd_bundle, self).set_var()
        self.var(bits('ptr', w = 32))
        self.var(bits('len', w = 16))
        self.var(bits('irq'))
        self.var(bits('pad'))
        self.var(bits('crc'))
        self.var(bits('sai'))

class zqh_eth_mac_tx_cpl_status(bundle):
    def set_var(self):
        super(zqh_eth_mac_tx_cpl_status, self).set_var()
        self.var(bits('under_flow'))
        self.var(bits('defer_abort'))
        self.var(bits('too_long'))
        self.var(bits('late_col'))
        self.var(bits('retry_cnt', w = 4))
        self.var(bits('retry_limit'))
        self.var(bits('defer'))
        self.var(bits('cs_lost'))
        self.var(bits('error'))

class zqh_eth_mac_rx_bd_bundle(bundle):
    def set_var(self):
        super(zqh_eth_mac_rx_bd_bundle, self).set_var()
        self.var(bits('ptr', w = 32))
        self.var(bits('irq'))

class zqh_eth_mac_rx_cpl_status(bundle):
    def set_var(self):
        super(zqh_eth_mac_rx_cpl_status, self).set_var()
        self.var(bits('len', w = 16))
        self.var(bits('over_flow'))
        self.var(bits('pause'))
        self.var(bits('da_miss'))
        self.var(bits('ivs'))
        self.var(bits('dn'))
        self.var(bits('too_long'))
        self.var(bits('too_short'))
        self.var(bits('crc_err'))
        self.var(bits('late_col'))
        self.var(bits('error'))
