from phgl_imp import *

class eth_phy(module):
    def set_par(self):
        super(eth_phy, self).set_par()
        self.pm.vuser  = [
            ('inc' , '../../common/vips/eth_phy/eth_phy_defines.v'),
            #tmp ('inc' , '../env/zqh_riscv_eth_defines.v'),
            ('code', '`define MULTICAST_XFR          0'),
            ('code', '`define UNICAST_XFR            1'),
            ('code', '`define BROADCAST_XFR          2'),
            ('code', '`define UNICAST_WRONG_XFR      3'),
            ('inc' , '../../common/vips/eth_phy/eth_phy_gmii.v')]

    def set_port(self):
        super(eth_phy, self).set_port()
        self.no_crg()
        self.io.var(inp('m_rst_n_i'))
        self.io.var(outp('mtx_clk_o'))
        self.io.var(inp('mtx_gclk_i'))
        self.io.var(inp('mtxd_i', w = 8))
        self.io.var(inp('mtxen_i'))
        self.io.var(inp('mtxerr_i'))
        self.io.var(outp('mrx_clk_o'))
        self.io.var(outp('mrxd_o', w = 8))
        self.io.var(outp('mrxdv_o'))
        self.io.var(outp('mrxerr_o'))
        self.io.var(outp('mcoll_o'))
        self.io.var(outp('mcrs_o'))
        self.io.var(inp('mdc_i'))
        self.io.var(inoutp('md_io'))
        self.io.var(inp('phy_log', w = 32))
