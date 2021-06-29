from phgl_imp import *

class zqh_crg_ctrl_core_pll_cfg(bundle):
    def set_var(self):
        super(zqh_crg_ctrl_core_pll_cfg, self).set_var()
        self.var(bits('bypass', w = 1))
        self.var(bits('div_q', w = 8))
        self.var(bits('mul', w = 8))
        self.var(bits('div_r', w = 8))

class zqh_crg_ctrl_eth_pll_cfg(bundle):
    def set_var(self):
        super(zqh_crg_ctrl_eth_pll_cfg, self).set_var()
        self.var(bits('en', w = 1))
        self.var(bits('bypass', w = 1))
        self.var(bits('div_q', w = 8))
        self.var(bits('mul', w = 8))
        self.var(bits('div_r', w = 8))

class zqh_crg_ctrl_ddr_pll_cfg(bundle):
    def set_var(self):
        super(zqh_crg_ctrl_ddr_pll_cfg, self).set_var()
        self.var(bits('en', w = 1))
        self.var(bits('bypass', w = 1))
        self.var(bits('div_q', w = 8))
        self.var(bits('mul', w = 8))
        self.var(bits('div_r', w = 8))

class zqh_crg_ctrl_reset_cfg(bundle):
    def set_var(self):
        super(zqh_crg_ctrl_reset_cfg, self).set_var()
        self.var(bits('eth_rst_n'))
        self.var(bits('reserved2'))
        self.var(bits('ddr_phy_rst_n'))
        self.var(bits('reserved1'))
        self.var(bits('reserved0'))
        self.var(bits('ddr_mc_rst_n'))

class zqh_crg_ctrl_cfg_io(bundle):
    def set_var(self):
        super(zqh_crg_ctrl_cfg_io, self).set_var()
        self.var(zqh_crg_ctrl_core_pll_cfg('core_pll_cfg').as_output())
        self.var(inp('core_pll_lock', w = 1))
        self.var(zqh_crg_ctrl_eth_pll_cfg('eth_pll_cfg').as_output())
        self.var(inp('eth_pll_lock', w = 1))
        self.var(zqh_crg_ctrl_ddr_pll_cfg('ddr_pll_cfg').as_output())
        self.var(inp('ddr_pll_lock', w = 1))
        self.var(outp('clock_ref_cfg'))
        self.var(zqh_crg_ctrl_reset_cfg('reset_cfg').as_output())
