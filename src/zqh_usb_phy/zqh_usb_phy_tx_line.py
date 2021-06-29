from phgl_imp import *
from .zqh_usb_phy_common_bundles import *
from .zqh_usb_phy_bundles import *
from .zqh_usb_phy_parameters import *

class zqh_usb_phy_tx_line(module):
    def set_par(self):
        super(zqh_usb_phy_tx_line, self).set_par()
        self.p = zqh_usb_phy_parameter()

    def set_port(self):
        super(zqh_usb_phy_tx_line, self).set_port()
        self.io.var(inp('cfg_tx_eop_se0_cnt', w = 4))
        self.io.var(inp('cfg_tx_eop_j_cnt', w = 4))
        self.io.var(outp('dp'))
        self.io.var(outp('dp_oe'))
        self.io.var(outp('dm'))
        self.io.var(outp('dm_oe'))
        self.io.var(ready_valid('req', zqh_usb_phy_tx_data, dw = 8).flip())

    def main(self):
        super(zqh_usb_phy_tx_line, self).main()

        (s_idle, s_sync, s_data, s_eop) = range(4)
        state = reg_rs('state', rs = s_idle, w = 3)
        bit_cnt = reg_r('bit_cnt', w = 8)
        bit_cnt_clean = bits('bit_cnt_clean', init = 0)
        sync_done = bits('sync_done', init = 0)
        eop_done = bits('eop_done', init = 0)
        stuff_insert = bits('stuff_insert', init = 0)

        with when(~stuff_insert):
            with when(bit_cnt_clean):
                bit_cnt /= 0
            with elsewhen(bit_cnt == 7):
                bit_cnt /= 0
            with other():
                bit_cnt /= bit_cnt + 1

            with when(state == s_idle):
                bit_cnt_clean /= 1
                with when(self.io.req.valid & self.io.req.bits.sync):
                    state /= s_sync
            with when(state == s_sync):
                with when(sync_done):
                    state /= s_data
                    bit_cnt_clean /= 1
            with when(state == s_data):
                with when(self.io.req.valid & self.io.req.bits.eop):
                    state /= s_eop
            with when(state == s_eop):
                with when(eop_done):
                    state /= s_idle
                    bit_cnt_clean /= 1

        line_se0_en = bits('line_se0_en', init = 0)
        line_se1_en = bits('line_se1_en', init = 0)
        line_j_en = bits('line_j_en', init = 0)
        line_k_en = bits('line_k_en', init = 0)
        dp_oe = bits('dp_oe', init = 0)
        dp_oe_reg = reg_r('dp_oe_reg', next = dp_oe)
        dp = bits('dp', init = 1)
        dp_reg = reg_r('dp_reg', next = dp)
        dm_oe = bits('dm_oe', init = 0)
        dm_oe_reg = reg_r('dm_oe_reg', next = dm_oe)
        dm = bits('dm', init = 1)
        dm_reg = reg_r('dm_reg', next = dm)
        dm_oe /= dp_oe
        dm /= ~dp
        self.io.dp_oe /= dp_oe_reg
        self.io.dp /= dp_reg
        self.io.dm_oe /= dm_oe_reg
        self.io.dm /= dm_reg
        self.io.req.ready /= 0

        bit_pre_dec = bits('bit_pre_dec', init = 1)
        bit_post_dec = bits('bit_post_dec', init = 1)
        stuff_cnt = reg_r('stuff_cnt', w = 3)
        stuff_cnt_match = bits('stuff_cnt_match')
        stuff_cnt_match /= stuff_cnt >= 6
        dp /= bit_post_dec
        with when(line_se0_en):
            dp /= 0
            dm /= 0
            stuff_cnt /= 0
        with elsewhen(line_se1_en):
            dp /= 1
            dm /= 1
            stuff_cnt /= 0
        with elsewhen(line_j_en):
            dp /= 1
            dm /= 0
            stuff_cnt /= 0
        with elsewhen(line_k_en):
            dp /= 0
            dm /= 1
            stuff_cnt /= 0
        with other():
            with when(bit_pre_dec):
                with when(stuff_cnt_match):
                    stuff_cnt /= 0
                with other():
                    stuff_cnt /= stuff_cnt + 1
            with other():
                stuff_cnt /= 0
            stuff_insert /= stuff_cnt_match

        with when(state == s_idle):
            dp_oe /= 0
            bit_pre_dec /= 1
            self.io.req.ready /= 0
            line_j_en /= 1
        with when(state == s_sync):
            dp_oe /= 1
            with when(bit_cnt == 7):
                bit_pre_dec /= 1
                self.io.req.ready /= 1
                sync_done /= 1
            with other():
                bit_pre_dec /= 0
        with when((state == s_data) & ~self.io.req.bits.eop):
            dp_oe /= 1
            bit_pre_dec /= self.io.req.bits.data[bit_cnt]
            with when(bit_cnt == 7):
                self.io.req.ready /= 1
        with when(((state == s_data) & self.io.req.bits.eop) | (state == s_eop)):
            dp_oe /= 1
            bit_pre_dec /= 0
            #tmp with when(bit_cnt == 2):
            #tmp     bit_pre_dec /= 1
            #tmp     self.io.req.ready /= 1
            #tmp     eop_done /= 1
            #tmp     line_j_en /= 1
            with when(bit_cnt < self.io.cfg_tx_eop_se0_cnt):
                line_se0_en /= 1
            with elsewhen(bit_cnt < (self.io.cfg_tx_eop_se0_cnt + self.io.cfg_tx_eop_j_cnt)):
                bit_pre_dec /= 1
                line_j_en /= 1
            with other():
                bit_pre_dec /= 1
                line_j_en /= 1
                self.io.req.ready /= 1
                eop_done /= 1

        with when(stuff_insert):
            self.io.req.ready /= 0

        #1 keep, 0 flip
        with when(~bit_pre_dec):
            bit_post_dec /= ~dp_reg
        with other():
            with when(stuff_insert):
                bit_post_dec /= ~dp_reg
            with other():
                bit_post_dec /= dp_reg
