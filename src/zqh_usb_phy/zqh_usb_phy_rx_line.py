from phgl_imp import *
from .zqh_usb_phy_common_bundles import *
from .zqh_usb_phy_bundles import *
from .zqh_usb_phy_parameters import *
from .zqh_usb_phy_misc import *

class zqh_usb_phy_rx_line(module):
    def set_par(self):
        super(zqh_usb_phy_rx_line, self).set_par()
        self.p = zqh_usb_phy_parameter()

    def set_port(self):
        super(zqh_usb_phy_rx_line, self).set_port()
        self.io.var(inp('dp'))
        self.io.var(inp('dm'))
        self.io.var(valid('req', zqh_usb_phy_rx_data, dw = 8))
        self.io.var(inp('rx_en'))
        self.io.var(outp('line_state', w = 2))

    def main(self):
        super(zqh_usb_phy_rx_line, self).main()

        lnst_next = bits('lnst_next', w = 2)
        lnst = reg_r('lnst', w = 2, next = lnst_next)
        lnst_next /= lnst
        with when(~self.io.dp & ~self.io.dm):
            lnst_next /= USB_PHY_CONSTS.LNST_SE0
        with when(self.io.dp & ~self.io.dm):
            lnst_next /= USB_PHY_CONSTS.LNST_J
        with when(~self.io.dp & self.io.dm):
            lnst_next /= USB_PHY_CONSTS.LNST_K
        with when(self.io.dp & self.io.dm):
            lnst_next /= USB_PHY_CONSTS.LNST_SE1

        self.io.line_state /= lnst

        dp_dly = reg_r('dp_dly', next = self.io.dp)
        dm_dly = reg_r('dm_dly', next = self.io.dm)
        dp_pos = self.io.dp & ~dp_dly
        dp_neg = ~self.io.dp & dp_dly
        dm_pos = self.io.dm & ~dm_dly
        dm_neg = ~self.io.dm & dm_dly

        con_idle_tick_least = 30

        (s_discon, s_con, s_idle, s_sync, s_data, s_eop, s_error) = range(7)
        state = reg_rs('state', rs = s_discon, w = 3)
        bit_cnt = reg_r('bit_cnt', w = 8)
        bit_cnt_clean = bits('bit_cnt_clean', init = 0)
        tick_cnt = reg_r('tick_cnt', w = 32)
        tick_cnt_clean = bits('tick_cnt_clean', init = 0)
        tick_cnt_inc = bits('tick_cnt_inc', init = 0)
        con_start = bits('con_start', init = 0)
        con_end = bits('con_end', init = 0)
        con_fail = bits('con_fail', init = 0)
        sync_start = bits('sync_start', init = 0)
        sync_done = bits('sync_done', init = 0)
        eop_start = bits('eop_start', init = 0)
        eop_done = bits('eop_done', init = 0)
        rx_byte_reg_map = vec('rx_byte_reg_map', reg_r, n = 8)
        rx_byte_full = bits('rx_byte_full', init = 0)
        rx_byte_full_reg = reg_r('rx_byte_full_reg', next = rx_byte_full)
        rx_stuff_error_reg = reg_r('rx_stuff_error_reg')
        stuff_insert = bits('stuff_insert', init = 0)

        with when(self.io.rx_en):
            with when(bit_cnt_clean):
                bit_cnt /= 0
            with elsewhen(~stuff_insert):
                with when((state != s_sync) & (bit_cnt == 7)):
                    bit_cnt /= 0
                with other():
                    bit_cnt /= bit_cnt + 1

            with when(tick_cnt_clean):
                tick_cnt /= 0
            with elsewhen(tick_cnt_inc):
                tick_cnt /= tick_cnt + 1


            with when(state == s_discon):
                with when(con_start):
                    state /= s_con
                    tick_cnt_clean /= 1
            with when(state == s_con):
                with when(con_fail):
                    state /= s_discon
                with elsewhen(con_end):
                    state /= s_idle
            with when(state == s_idle):
                bit_cnt_clean /= 1
                with when(sync_start):
                    state /= s_sync
            with when(state == s_sync):
                with when(sync_done):
                    state /= s_data
                    bit_cnt_clean /= 1
                    rx_stuff_error_reg /= 0
                with elsewhen(bit_cnt > 3):
                    with when((lnst_next == USB_PHY_CONSTS.LNST_J) & (lnst == USB_PHY_CONSTS.LNST_K)):
                        state /= s_sync
                    with elsewhen((lnst_next == USB_PHY_CONSTS.LNST_K) & (lnst == USB_PHY_CONSTS.LNST_J)):
                        state /= s_sync
                    with other():
                        state /= s_error
                        bit_cnt_clean /= 1
            with when(state == s_data):
                with when(eop_start):
                    state /= s_eop
            with when(state == s_eop):
                with when(eop_done):
                    state /= s_idle
            with when(state == s_error):
                state /= s_idle
        with other():
            state /= s_discon
            bit_cnt /= 0
            tick_cnt /= 0

        stuff_cnt = reg_r('stuff_cnt', w = 3)
        stuff_cnt_clean = bits('stuff_cnt_clean', init = 0)
        stuff_cnt_en = bits('stuff_cnt_en', init = 0)
        stuff_cnt_match = bits('stuff_cnt_match')
        stuff_cnt_match /= stuff_cnt >= 6
        with when(state == s_discon):
            stuff_cnt_clean /= 1
        with when(state == s_idle):
            stuff_cnt_clean /= 1
        with when(state == s_sync):
            with when(bit_cnt > 3):
                stuff_cnt_en /= 1
        with when(state == s_data):
            stuff_cnt_en /= 1
        with when(state == s_eop):
            stuff_cnt_clean /= 1
        with when(state == s_error):
            stuff_cnt_clean /= 1

        with when(stuff_cnt_clean):
            stuff_cnt /= 0
        with elsewhen(stuff_cnt_en):
            with when(
                ((lnst_next == USB_PHY_CONSTS.LNST_J) & (lnst == USB_PHY_CONSTS.LNST_J)) |
                ((lnst_next == USB_PHY_CONSTS.LNST_K) & (lnst == USB_PHY_CONSTS.LNST_K))):
                stuff_cnt /= stuff_cnt + 1
            with other():
                stuff_cnt /= 0

        with when(state == s_sync):
            stuff_insert /= stuff_cnt_match
        with when(state == s_data):
            stuff_insert /= stuff_cnt_match



        self.io.req.valid /= 0
        self.io.req.bits.error /= 0
        self.io.req.bits.data /= rx_byte_reg_map.pack()
        self.io.req.bits.sync /= 0
        self.io.req.bits.eop /= 0

        rx_bit_dec = lnst_next == lnst
        with when(state == s_discon):
            with when(lnst_next == USB_PHY_CONSTS.LNST_J):
                con_start /= 1
        with when(state == s_con):
            with when(lnst_next == USB_PHY_CONSTS.LNST_J):
                tick_cnt_inc /= 1
                #state in idle at least 2.5us
                with when(tick_cnt >= con_idle_tick_least):
                    con_end /= 1
            #fake connect
            with other():
                con_fail /= 1
        with when(state == s_idle):
            with when((lnst_next == USB_PHY_CONSTS.LNST_K) & (lnst == USB_PHY_CONSTS.LNST_J)):
                sync_start /= 1
        with when(state == s_sync):
            with when(bit_cnt > 3):
                with when((lnst_next == USB_PHY_CONSTS.LNST_K) & (lnst == USB_PHY_CONSTS.LNST_K)):
                    sync_done /= 1
        with when(state == s_data):
            rx_byte_reg_map(bit_cnt, rx_bit_dec)
            with when(bit_cnt == 7):
                with when(~stuff_insert):
                    rx_byte_full /= 1

            #tmp with when((lnst_next == USB_PHY_CONSTS.LNST_SE0) & lnst.match_any([USB_PHY_CONSTS.LNST_J, USB_PHY_CONSTS.LNST_K])):
            with when(lnst_next == USB_PHY_CONSTS.LNST_SE0):
                eop_start /= 1
                rx_byte_full /= 0

            with when(stuff_insert):
                with when(rx_bit_dec):
                    rx_stuff_error_reg /= 1
        with when(state == s_eop):
            with when(lnst_next == USB_PHY_CONSTS.LNST_J):
                eop_done /= 1
            #tmp with when((lnst_next == USB_PHY_CONSTS.LNST_J) & (lnst == USB_PHY_CONSTS.LNST_SE0)):
            #tmp     eop_done /= 1

        with when(state == s_sync):
            with when(sync_done):
                self.io.req.valid /= 1
                self.io.req.bits.sync /= 1
                self.io.req.bits.eop /= 0
        with when(rx_byte_full_reg):
            self.io.req.valid /= 1
            self.io.req.bits.sync /= 0
            self.io.req.bits.eop /= 0
            self.io.req.bits.error /= rx_stuff_error_reg
        with when(state == s_eop):
            with when(eop_done):
                self.io.req.valid /= 1
                self.io.req.bits.sync /= 0
                self.io.req.bits.eop /= 1
        with when(state == s_error):
            self.io.req.bits.error /= 1
            self.io.req.bits.sync /= 0
            self.io.req.bits.eop /= 0
