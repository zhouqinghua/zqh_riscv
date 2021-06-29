import sys
import os
from phgl_imp import *
from .zqh_eth_mac_smi_bundles import *

class zqh_eth_mac_smi(module):
    def set_par(self):
        super(zqh_eth_mac_smi, self).set_par()
        self.p.par('clk_div_w', 8)

    def set_port(self):
        super(zqh_eth_mac_smi, self).set_port()
        self.io.var(zqh_eth_mac_phy_smi_io('smi'))
        self.io.var(inp('cfg_clk_div', w = self.p.clk_div_w))
        self.io.var(inp('cfg_no_pre'))
        self.io.var(inp('ctrl_ready'))
        self.io.var(inp('ctrl_rw'))
        self.io.var(inp('ctrl_phy_addr', w = 5))
        self.io.var(inp('ctrl_reg_addr', w = 5))
        self.io.var(inp('ctrl_wdata', w = 16))
        self.io.var(outp('ctrl_rdata', w = 16))
        self.io.var(outp('ctrl_done'))

    def main(self):
        super(zqh_eth_mac_smi, self).main()

        #mdc clock div
        mdc_div_cnt = reg_r('mdc_div_cnt', w = self.io.cfg_clk_div.get_w())
        with when(self.io.ctrl_ready):
            with when(mdc_div_cnt == self.io.cfg_clk_div):
                mdc_div_cnt /= 0
            with other():
                mdc_div_cnt /= mdc_div_cnt + 1
        mdc_div_flip = bits('mdc_div_flip', init = mdc_div_cnt == self.io.cfg_clk_div)
        mdc_flip_cnt = reg_r('mdc_flip_cnt', w = 2)
        smi_clk = bits('smi_clk', init = 0)
        with when(self.io.ctrl_ready):
            with when(mdc_div_flip):
                mdc_flip_cnt /= mdc_flip_cnt + 1

                with when(mdc_flip_cnt == 3):
                    smi_clk /= 1

        (
            s_smi_idle, s_smi_pre, s_smi_start, s_smi_op, 
            s_smi_addr, s_smi_ta, s_smi_data, s_smi_done) = range(8)
        smi_state = reg_rs('smi_state', w = 4, rs = s_smi_idle)
        smi_bit_cnt = reg_r('smi_bit_cnt', w = 5)
        smi_bit_cnt_reset = bits('smi_bit_cnt_reset', init = 0)
        smi_rdata_shift = reg('smi_rdata_shift', w = 16)

        self.io.ctrl_done /= 0
        with when(~self.io.ctrl_ready):
            smi_state /= s_smi_idle
            smi_bit_cnt_reset /= 1
        with elsewhen(smi_clk):
            with when(smi_state == s_smi_idle):
                smi_bit_cnt_reset /= 1
                with when(self.io.cfg_no_pre):
                    smi_state /= s_smi_start
                with other():
                    smi_state /= s_smi_pre
            with when(smi_state == s_smi_pre):
                with when(smi_bit_cnt == 31):
                    smi_state /= s_smi_start
                    smi_bit_cnt_reset /= 1
            with when(smi_state == s_smi_start):
                with when(smi_bit_cnt == 1):
                    smi_state /= s_smi_op
                    smi_bit_cnt_reset /= 1
            with when(smi_state == s_smi_op):
                with when(smi_bit_cnt == 1):
                    smi_state /= s_smi_addr
                    smi_bit_cnt_reset /= 1
            with when(smi_state == s_smi_addr):
                with when(smi_bit_cnt == 9):
                    smi_state /= s_smi_ta
                    smi_bit_cnt_reset /= 1
            with when(smi_state == s_smi_ta):
                with when(smi_bit_cnt == 1):
                    smi_state /= s_smi_data
                    smi_bit_cnt_reset /= 1
            with when(smi_state == s_smi_data):
                with when(smi_bit_cnt == 15):
                    smi_state /= s_smi_done
                    smi_bit_cnt_reset /= 1
            with when(smi_state == s_smi_done):
                with when(smi_bit_cnt == 1):
                    smi_state /= s_smi_idle
                    smi_bit_cnt_reset /= 1

            with when(smi_bit_cnt_reset):
                smi_bit_cnt /= 0
            with other():
                smi_bit_cnt /= smi_bit_cnt + 1

            with when(smi_state == s_smi_done):
                with when(smi_bit_cnt == 1):
                    self.io.ctrl_done /= 1

        self.io.ctrl_rdata /= smi_rdata_shift


        mdc_reg = reg_r('mdc_reg')
        mdio_do_reg = reg_s('mdio_do_reg')
        mdio_oe_reg = reg_r('mdio_oe_reg')
        with when(~self.io.ctrl_ready):
            mdc_reg /= 0
            mdio_oe_reg /= 0
        with elsewhen(mdc_div_flip):
            #tmp with when(~smi_state.match_any([s_smi_idle, s_smi_done])):
            with when(~smi_state.match_any([s_smi_idle])):
                with when(mdc_flip_cnt == 0):
                    mdc_reg /= 0
                with elsewhen(mdc_flip_cnt == 2):
                    with when(~((smi_state == s_smi_done) & (smi_bit_cnt == 1))):
                        mdc_reg /= 1
            with other():
                mdc_reg /= 0

            with when(smi_state == s_smi_idle):
                mdio_do_reg /= 1
                mdio_oe_reg /= 0
            with when(smi_state == s_smi_pre):
                mdio_oe_reg /= 1
                with when(mdc_flip_cnt == 0):
                    mdio_do_reg /= 1
            with when(smi_state == s_smi_start):
                mdio_oe_reg /= 1
                with when(mdc_flip_cnt == 0):
                    with when(smi_bit_cnt == 0):
                        mdio_do_reg /= 0
                    with other():
                        mdio_do_reg /= 1
            with when(smi_state == s_smi_op):
                mdio_oe_reg /= 1
                with when(mdc_flip_cnt == 0):
                    with when(smi_bit_cnt == 0):
                        mdio_do_reg /= mux(self.io.ctrl_rw, 0, 1)
                    with other():
                        mdio_do_reg /= mux(self.io.ctrl_rw, 1, 0)
            with when(smi_state == s_smi_addr):
                mdio_oe_reg /= 1
                phy_reg_addr = cat([self.io.ctrl_phy_addr, self.io.ctrl_reg_addr])
                with when(mdc_flip_cnt == 0):
                    mdio_do_reg /= sel_bin(
                        smi_bit_cnt[3:0],
                        list(reversed(phy_reg_addr.grouped())))
            with when(smi_state == s_smi_ta):
                with when(self.io.ctrl_rw):
                    mdio_oe_reg /= 1
                    with when(mdc_flip_cnt == 0):
                        with when(smi_bit_cnt == 0):
                            mdio_do_reg /= 1
                        with other():
                            mdio_do_reg /= 0
                with other():
                    mdio_oe_reg /= 0
            with when(smi_state == s_smi_data):
                with when(self.io.ctrl_rw):
                    mdio_oe_reg /= 1
                    with when(mdc_flip_cnt == 0):
                        mdio_do_reg /= sel_bin(
                            smi_bit_cnt[3:0],
                            list(reversed(self.io.ctrl_wdata.grouped())))
                with other():
                    mdio_oe_reg /= 0
                    with when(mdc_flip_cnt == 2):
                        smi_rdata_shift /= cat([smi_rdata_shift[14:0], 
                            self.io.smi.mdio.input])
            with when(smi_state == s_smi_done):
                mdio_oe_reg /= 0
                mdio_do_reg /= 1

        self.io.smi.mdc /= mdc_reg
        self.io.smi.mdio.oe /= mdio_oe_reg
        self.io.smi.mdio.output /= mdio_do_reg
