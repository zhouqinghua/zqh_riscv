from phgl_imp import *

class zqh_usb_clk_gen(module):
    def set_par(self):
        super(zqh_usb_clk_gen, self).set_par()
        self.p.par('utmi_dw', 8)

    def set_port(self):
        super(zqh_usb_clk_gen, self).set_port()
        self.io.var(inp('din'))
        self.io.var(inp('div', w = 6))
        self.io.var(outp('rx_clock_out'))
        self.io.var(outp('tx_clock_out'))
        self.io.var(outp('utmi_clock_out'))

    def main(self):
        super(zqh_usb_clk_gen, self).main()

        mid_v = reg(next = self.io.div >> 1, w = self.io.div.get_w())
        #tmp max_v = reg(next = self.io.div - 1, w = self.io.div.get_w())
        max_v_pre = reg(next = self.io.div - 2, w = self.io.div.get_w())
        #
        #rx clock recover
        #{{{
        din_dly0 = reg('din_dly0', next = self.io.din)
        din_dly1 = reg('din_dly1', next = din_dly0)
        din_pos = din_dly0 & ~din_dly1
        din_neg = ~din_dly0 & din_dly1

        rx_clk_next = bits('rx_clk_next',init = 0)
        rx_clk_reg = reg_r('rx_clk_reg', next = rx_clk_next)

        rx_cnt = reg('rx_cnt', w = self.io.div.get_w())

        rx_clk_next /= rx_clk_reg
        with when(rx_cnt == mid_v):
            rx_clk_next /= 1
        with when(rx_cnt == 0):
            rx_clk_next /= 0

        rx_cnt /= rx_cnt + 1
        rx_cnt_max_clear = reg_r('rx_cnt_max_clear', next = rx_cnt == max_v_pre)
        #tmp with when((rx_cnt == max_v) | (din_neg | din_pos)):
        with when(rx_cnt_max_clear | (din_neg | din_pos)):
            rx_cnt /= 0

        self.io.rx_clock_out /= rx_clk_reg
        #}}}


        #
        #tx clock generate
        #{{{
        tx_clk_next = bits('tx_clk_next',init = 0)
        tx_clk_reg = reg_r('tx_clk_reg', next = tx_clk_next)
        tx_cnt = reg('tx_cnt', w = self.io.div.get_w())

        tx_clk_next /= tx_clk_reg
        with when(tx_cnt == mid_v):
            tx_clk_next /= 1
        with when(tx_cnt == 0):
            tx_clk_next /= 0

        tx_cnt /= tx_cnt + 1
        tx_cnt_max_clear = reg_r('tx_cnt_max_clear', next = tx_cnt == max_v_pre)
        #tmp with when(tx_cnt == max_v):
        with when(tx_cnt_max_clear):
            tx_cnt /= 0

        self.io.tx_clock_out /= tx_clk_reg
        #}}}


        #
        #utmi clock generate
        #{{{
        if (self.p.utmi_dw == 8):
            utmi_div = 9
        elif (self.p.utmi_dw == 16):
            utmi_div = 13
        else:
            assert(0)
        utmi_mid_v = utmi_div//2
        utmi_max_v = utmi_div - 1

        utmi_clk_next = bits('utmi_clk_next',init = 0)
        utmi_clk_reg = reg_r('utmi_clk_reg', next = utmi_clk_next)
        utmi_cnt = reg('utmi_cnt', w = self.io.div.get_w())

        utmi_clk_next /= utmi_clk_reg
        with when(utmi_cnt == utmi_mid_v):
            utmi_clk_next /= 1
        with when(utmi_cnt == 0):
            utmi_clk_next /= 0

        utmi_cnt /= utmi_cnt + 1
        with when(utmi_cnt == utmi_max_v):
            utmi_cnt /= 0

        self.io.utmi_clock_out /= utmi_clk_reg
        #}}}
