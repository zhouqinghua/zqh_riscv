from phgl_imp import *
from .zqh_usb_phy_common_bundles import *
from .zqh_usb_phy_bundles import *
from .zqh_usb_phy_parameters import *
from .zqh_usb_phy_tx_line import zqh_usb_phy_tx_line
from .zqh_usb_phy_rx_line import zqh_usb_phy_rx_line
from .zqh_usb_phy_misc import *

class zqh_usb_phy(csr_module):
    def set_par(self):
        super(zqh_usb_phy, self).set_par()
        self.p = zqh_usb_phy_parameter()

    def set_port(self):
        super(zqh_usb_phy, self).set_port()
        self.io.var(inp('tx_clk'))
        self.io.var(inp('rx_clk'))
        self.io.var(zqh_usb_phy_reg_io('reg'))
        self.io.var(zqh_usb_phy_io('usb'))
        self.io.var(zqh_usb_utmi_l1('utmi', dw = 8))

    def main(self):
        super(zqh_usb_phy, self).main()
        self.reg_if = self.io.reg

        #
        #cfg regs
        #{{{
        self.cfg_reg(csr_reg_group(
            'cfg0',
            offset = 0x00,
            size = 4,
            fields_desc = [
                csr_reg_field_desc('rx_en', width = 1, reset = 0, commments = '''\
Set to 1 to enable recieve transaction.''')]))
        self.cfg_reg(csr_reg_group(
            'cfg1',
            offset = 0x04,
            size = 4,
            fields_desc = [
                csr_reg_field_desc('line_dm',  width = 1, reset = 0, comments = '''\
line force data of DM.'''),
                csr_reg_field_desc('line_dp',  width = 1, reset = 0, comments = '''\
line force data of DP.'''),
                csr_reg_field_desc('line_force',  width = 1, reset = 0, comments = '''\
Set to 1 means force usb dp/dm line to line_dp/line_dm configure data.''')]))
        self.cfg_reg(csr_reg_group(
            'cfg2',
            offset = 0x08,
            size = 4,
            fields_desc = [
                csr_reg_field_desc('tx_eop_j_cnt', width = 4, reset = 1, comments = '''\
EOP's J state bit length.'''),
                csr_reg_field_desc('tx_eop_se0_cnt', width = 4, reset = 2, comments = '''\
EOP's SE0 state bit length.''')]))
        #}}}

        self.io.utmi.CLK /= self.io.clock


        #usb rx
        rx_line_fifo = async_queue(
            'rx_line_fifo',
            gen = lambda _: zqh_usb_phy_rx_data(
                _, dw = 8),
            entries = 8)
        rx_line_fifo.io.enq_clock /= self.io.rx_clk
        rx_line_fifo.io.enq_reset /= self.io.reset
        rx_line_fifo.io.deq_clock /= self.io.clock
        rx_line_fifo.io.deq_reset /= self.io.reset

        usb_rx_line = zqh_usb_phy_rx_line('usb_rx_line')
        usb_rx_line.io.clock /= self.io.rx_clk
        usb_rx_line.io.dp /= self.io.usb.dp.input
        usb_rx_line.io.dm /= self.io.usb.dm.input
        usb_rx_line.io.rx_en /= async_dff(self.regs['cfg0'].rx_en, 2)
        rx_line_fifo.io.enq /= usb_rx_line.io.req
        self.io.utmi.RXValid /= rx_line_fifo.io.deq.valid & ~rx_line_fifo.io.deq.bits.sync & ~rx_line_fifo.io.deq.bits.eop
        self.io.utmi.RXError /= rx_line_fifo.io.deq.bits.error
        self.io.utmi.DataOut /= rx_line_fifo.io.deq.bits.data
        rx_line_fifo.io.deq.ready /= 1
        RXActive_reg = reg_r('RXActive_reg')
        with when(~self.regs['cfg0'].rx_en):
            RXActive_reg /= 0
        with elsewhen(rx_line_fifo.io.deq.fire()):
            with when(rx_line_fifo.io.deq.bits.sync):
                RXActive_reg /= 1
            with elsewhen(rx_line_fifo.io.deq.bits.eop):
                RXActive_reg /= 0
        self.io.utmi.RXActive /= RXActive_reg

        line_state_fifo = async_queue(
            'line_state_fifo',
            gen = lambda _: bits(_, w = 2),
            entries = 8)
        line_state_fifo.io.enq_clock /= self.io.rx_clk
        line_state_fifo.io.enq_reset /= self.io.reset
        line_state_fifo.io.deq_clock /= self.io.utmi.CLK
        line_state_fifo.io.deq_reset /= self.io.reset
        line_state_fifo.io.enq.valid /= 1
        line_state_fifo.io.enq.bits /= usb_rx_line.io.line_state
        line_state_fifo.io.deq.ready /= 1

        line_state_reg = reg_r(w = 2)
        with when(line_state_fifo.io.deq.fire()):
            line_state_reg /= line_state_fifo.io.deq.bits
        self.io.utmi.LineState /= line_state_reg


        #
        #connection/disconnect detect
        disconnect_se0_tick_least = 120
        connect_j_tick_least = 120
        tick_cnt = reg_r('tick_cnt', w = 24)
        HostDisconnect_reg = reg_s('HostDisconnect_reg')
        self.io.utmi.HostDisconnect /= HostDisconnect_reg
        with when(~HostDisconnect_reg):
            with when(line_state_reg == USB_PHY_CONSTS.LNST_SE0):
                with when(tick_cnt < disconnect_se0_tick_least):
                    tick_cnt /= tick_cnt + 1
                with other():
                    HostDisconnect_reg /= 1
                    tick_cnt /= 0
            with other():
                tick_cnt /= 0

        with when(HostDisconnect_reg):
            with when(line_state_reg == USB_PHY_CONSTS.LNST_J):
                with when(tick_cnt < connect_j_tick_least):
                    tick_cnt /= tick_cnt + 1
                with other():
                    HostDisconnect_reg /= 0
                    tick_cnt /= 0
            with other():
                tick_cnt /= 0


        #usb tx
        tx_line_fifo = async_queue(
            'tx_line_fifo',
            gen = lambda _: zqh_usb_phy_tx_data(
                _, dw = 8),
            entries = 8)
        tx_line_fifo.io.enq_clock /= self.io.clock
        tx_line_fifo.io.enq_reset /= self.io.reset
        tx_line_fifo.io.deq_clock /= self.io.tx_clk
        tx_line_fifo.io.deq_reset /= self.io.reset

        usb_tx_line = zqh_usb_phy_tx_line('usb_tx_line')
        usb_tx_line.io.clock /= self.io.tx_clk
        self.io.usb.dp.output /= usb_tx_line.io.dp
        self.io.usb.dp.oe /= usb_tx_line.io.dp_oe
        self.io.usb.dm.output /= usb_tx_line.io.dm
        self.io.usb.dm.oe /= usb_tx_line.io.dm_oe
        usb_tx_line.io.req /= tx_line_fifo.io.deq
        usb_tx_line.io.cfg_tx_eop_se0_cnt /= self.regs['cfg2'].tx_eop_se0_cnt
        usb_tx_line.io.cfg_tx_eop_j_cnt /= self.regs['cfg2'].tx_eop_j_cnt

        (s_tx_reset, s_tx_wait, s_tx_send_sync, s_tx_data_load, s_tx_data_wait, s_tx_send_eop) = range(6)
        tx_state = reg_rs('tx_state', w = 3, rs = s_tx_reset)

        with when(tx_state == s_tx_reset):
            tx_state /= s_tx_wait
        with when(tx_state == s_tx_wait):
            with when(self.io.utmi.TXValid):
                tx_state /= s_tx_send_sync
        with when(tx_state == s_tx_send_sync):
            with when(tx_line_fifo.io.enq.fire()):
                tx_state /= s_tx_data_load
        with when(tx_state == s_tx_data_load):
            with when(~self.io.utmi.TXValid):
                tx_state /= s_tx_send_eop
        with when(tx_state == s_tx_send_eop):
            with when(tx_line_fifo.io.enq.fire()):
                tx_state /= s_tx_wait

        self.io.utmi.TXReady /= 0
        tx_line_fifo.io.enq.valid /= 0
        tx_line_fifo.io.enq.bits.data /= self.io.utmi.DataIn
        tx_line_fifo.io.enq.bits.sync /= 0
        tx_line_fifo.io.enq.bits.eop /= 0
        with when(tx_state == s_tx_reset):
            self.io.utmi.TXReady /= 0
        with when(tx_state == s_tx_wait):
            self.io.utmi.TXReady /= 0
        with when(tx_state == s_tx_send_sync):
            self.io.utmi.TXReady /= 0
            tx_line_fifo.io.enq.valid /= 1
            tx_line_fifo.io.enq.bits.sync /= 1
            tx_line_fifo.io.enq.bits.eop /= 0
        with when(tx_state == s_tx_data_load):
            self.io.utmi.TXReady /= tx_line_fifo.io.enq.ready
            tx_line_fifo.io.enq.valid /= self.io.utmi.TXValid
            tx_line_fifo.io.enq.bits.sync /= 0
            tx_line_fifo.io.enq.bits.eop /= 0
        with when(tx_state == s_tx_send_eop):
            self.io.utmi.TXReady /= 0
            tx_line_fifo.io.enq.valid /= 1
            tx_line_fifo.io.enq.bits.sync /= 0
            tx_line_fifo.io.enq.bits.eop /= 1


        #line force process
        #such as reset devices
        with when(self.regs['cfg1'].line_force):
            self.io.usb.dp.output /= self.regs['cfg1'].line_dp
            self.io.usb.dp.oe /= 1
            self.io.usb.dm.output /= self.regs['cfg1'].line_dm
            self.io.usb.dm.oe /= 1
