from phgl_imp import *
from zqh_devices.zqh_crg_ctrl.zqh_crg_ctrl_bundles import zqh_crg_ctrl_cfg_io
from .zqh_crg_fpga_pll import clk_wiz_0

class zqh_crg(module):
    def set_par(self):
        super(zqh_crg, self).set_par()
        self.p.par('reset_core_delay', 8)
        self.p.par('imp_mode', 'sim')

    def check_par(self):
        super(zqh_crg, self).check_par()
        self.pm.reset_name = 'reset_n' #0 valid reset
        self.pm.reset_level = 0 #0 means valid reset

    def set_port(self):
        super(zqh_crg, self).set_port()
        self.io.var(inp('clock_rtc_i'))

        self.io.var(zqh_crg_ctrl_cfg_io('crg_ctrl').flip())

        self.io.var(outp('clock_ref_o'))
        self.io.var(outp('clock_rtc_o'))
        self.io.var(outp('clock_core_o'))
        self.io.var(outp('clock_eth_o'))
        self.io.var(outp('clock_ddr_o'))
        self.io.var(outp('clock_usb_ref_o'))

        self.io.var(outp('reset_por_o'))
        self.io.var(outp('reset_core_o'))
        self.io.var(outp('reset_eth_o'))
        self.io.var(outp('reset_ddr_phy_o'))
        self.io.var(outp('reset_ddr_mc_o'))
        self.io.var(outp('reset_usb_o'))


    def main(self):
        super(zqh_crg, self).main()
        
        #self.io.clock_ref_o /= self.io.clock
        self.io.clock_rtc_o /= self.io.clock_rtc_i
        self.io.reset_por_o /= ~self.io.reset_n

        if (self.p.imp_mode == 'sim'):
            self.gen_pll_sim()
        elif (self.p.imp_mode == 'fpga'):
            self.gen_pll_fpga()

        #core reset
        reset_core_cnt = reg_r('reset_core_cnt', w = 4, clock = self.io.clock_ref_o)
        reset_core_cnt_reach = reset_core_cnt == self.p.reset_core_delay
        with when(~reset_core_cnt_reach):
            reset_core_cnt /= reset_core_cnt + 1
        #old self.io.reset_core_o /= ~reset_core_cnt_reach | self.io.reset
        self.io.reset_core_o /= async_dff(
            ~reset_core_cnt_reach | (~self.io.reset_n),
            3,
            clock = self.io.clock_core_o)

        #eth reset
        #self.io.reset_eth_o /= ~self.io.crg_ctrl.reset_cfg.eth_rst_n
        self.io.reset_eth_o /= async_dff(
            ~self.io.crg_ctrl.reset_cfg.eth_rst_n,
            3,
            clock = self.io.clock_eth_o)

        #ddr reset
        self.io.reset_ddr_phy_o /= async_dff(
            ~self.io.crg_ctrl.reset_cfg.ddr_phy_rst_n,
            3,
            clock = self.io.clock_ddr_o)
        self.io.reset_ddr_mc_o /= async_dff(
            ~self.io.crg_ctrl.reset_cfg.ddr_mc_rst_n,
            3,
            clock = self.io.clock_ddr_o)

        #usb rest: TBD, same as core
        self.io.reset_usb_o /= async_dff(
            ~reset_core_cnt_reach | (~self.io.reset_n),
            3,
            clock = self.io.clock_usb_ref_o)


    def gen_pll_sim(self):
        #core ref: 200MHz
        cdv_ref = clock_divider_sim('cdv_ref')
        cdv_ref.io.clock_ref /= self.io.clock
        cdv_ref.io.div /= 1
        self.io.clock_ref_o /= cdv_ref.io.clock_out

        #core clock: 1GHz
        cdv_core_pre = clock_divider_sim('cdv_core_pre')
        cdv_core_pre.io.clock_ref /= self.io.clock
        cdv_core_pre.io.div /= self.io.crg_ctrl.core_pll_cfg.div_r
        pll_core = pll_sim('pll_core')
        pll_core.io.clock_ref /= cdv_core_pre.io.clock_out
        pll_core.io.bypass /= self.io.crg_ctrl.core_pll_cfg.bypass
        pll_core.io.mul /= self.io.crg_ctrl.core_pll_cfg.mul
        cdv_core_post = clock_divider_sim('cdv_core_post')
        cdv_core_post.io.clock_ref /= pll_core.io.clock_out
        cdv_core_post.io.div /= self.io.crg_ctrl.core_pll_cfg.div_q
        self.io.crg_ctrl.core_pll_lock /= pll_core.io.lock
        self.io.clock_core_o /= cdv_core_post.io.clock_out

        #eth clock: 125MHz
        cdv_eth_pre = clock_divider_sim('cdv_eth_pre')
        cdv_eth_pre.io.clock_ref /= self.io.clock
        cdv_eth_pre.io.div /= self.io.crg_ctrl.eth_pll_cfg.div_r
        pll_eth = pll_sim('pll_eth')
        pll_eth.io.clock_ref /= cdv_eth_pre.io.clock_out
        pll_eth.io.bypass /= self.io.crg_ctrl.eth_pll_cfg.bypass
        pll_eth.io.mul /= self.io.crg_ctrl.eth_pll_cfg.mul
        cdv_eth_post = clock_divider_sim('cdv_eth_post')
        cdv_eth_post.io.clock_ref /= pll_eth.io.clock_out
        cdv_eth_post.io.div /= self.io.crg_ctrl.eth_pll_cfg.div_q
        self.io.crg_ctrl.eth_pll_lock /= pll_eth.io.lock
        self.io.clock_eth_o /= cdv_eth_post.io.clock_out & self.io.crg_ctrl.eth_pll_cfg.en

        #ddr clock: 400MHz - 800MHz
        cdv_ddr_pre = clock_divider_sim('cdv_ddr_pre')
        cdv_ddr_pre.io.clock_ref /= self.io.clock
        cdv_ddr_pre.io.div /= self.io.crg_ctrl.ddr_pll_cfg.div_r
        pll_ddr = pll_sim('pll_ddr')
        pll_ddr.io.clock_ref /= cdv_ddr_pre.io.clock_out
        pll_ddr.io.bypass /= self.io.crg_ctrl.ddr_pll_cfg.bypass
        pll_ddr.io.mul /= self.io.crg_ctrl.ddr_pll_cfg.mul
        cdv_ddr_post = clock_divider_sim('cdv_ddr_post')
        cdv_ddr_post.io.clock_ref /= pll_ddr.io.clock_out
        cdv_ddr_post.io.div /= self.io.crg_ctrl.ddr_pll_cfg.div_q
        self.io.crg_ctrl.ddr_pll_lock /= pll_ddr.io.lock
        self.io.clock_ddr_o /= cdv_ddr_post.io.clock_out & self.io.crg_ctrl.ddr_pll_cfg.en

        #usb ref clock: 400
        cdv_usb_ref_pre = clock_divider_sim('cdv_usb_ref_pre')
        cdv_usb_ref_pre.io.clock_ref /= self.io.clock
        cdv_usb_ref_pre.io.div /= 2
        pll_usb_ref = pll_sim('pll_usb_ref')
        pll_usb_ref.io.clock_ref /= cdv_usb_ref_pre.io.clock_out
        pll_usb_ref.io.bypass /= 0
        pll_usb_ref.io.mul /= 4
        cdv_usb_ref_post = clock_divider_sim('cdv_usb_ref_post')
        cdv_usb_ref_post.io.clock_ref /= pll_usb_ref.io.clock_out
        cdv_usb_ref_post.io.div /= 1
        self.io.clock_usb_ref_o /= cdv_usb_ref_post.io.clock_out

    def gen_pll_fpga(self):
        fpga_pll = clk_wiz_0('fpga_pll')
        fpga_pll.io.reset /= ~self.io.reset_n
        fpga_pll.io.clk_in1 /= self.io.clock
        self.io.clock_ref_o /= fpga_pll.io.clk_ref
        self.io.clock_eth_o /= fpga_pll.io.clk_eth & self.io.crg_ctrl.eth_pll_cfg.en
        self.io.clock_ddr_o /= fpga_pll.io.clk_ddr & self.io.crg_ctrl.ddr_pll_cfg.en
        self.io.clock_usb_ref_o /= fpga_pll.io.clk_usb_ref
        self.io.clock_core_o /= fpga_pll.io.clk_core
        self.io.crg_ctrl.eth_pll_lock /= fpga_pll.io.locked
        self.io.crg_ctrl.ddr_pll_lock /= fpga_pll.io.locked
        self.io.crg_ctrl.core_pll_lock /= fpga_pll.io.locked
