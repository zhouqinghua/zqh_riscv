import sys
import os
from phgl_imp import *
from .zqh_uart_parameters import zqh_uart_parameter
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_uart_bundles import zqh_uart_io

class zqh_uart(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_uart, self).set_par()
        self.p = zqh_uart_parameter()

    def gen_node_tree(self):
        super(zqh_uart, self).gen_node_tree()
        self.gen_node_slave(
            'uart_slave', 
            tl_type = 'tl_uh', 
            bundle_p = self.p.gen_tl_bundle_p())
        self.p.uart_slave.print_up()
        self.p.uart_slave.print_address_space()

    def set_port(self):
        super(zqh_uart, self).set_port()
        self.io.var(zqh_uart_io('uart'))

    def main(self):
        super(zqh_uart, self).main()
        self.gen_node_interface('uart_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        txdata_write = bits(init = 0)
        def func_txdata_write_data(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata[7:0]
                tmp = txdata_write
                tmp /= 1
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'txdata', 
            offset = 0x000, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('full', access = 'VOL', width = 1, comments = '''\
Transmit FIFO full
The full flag indicates whether the transmit FIFO is able to accept new entries;
when set, writes to data are ignored.'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 23),
                csr_reg_field_desc('data', access = 'VOL', width = 8, write = func_txdata_write_data, comments = '''\
Transmit data
Writing to the txdata register enqueues the character contained in the data field to the transmit FIFO if the FIFO is able to accept new entries. 
Reading from txdata returns the current value of the full flag and zero in the data field.''')]))

        rxdata_read = bits(init = 0)
        def func_rxdata_read_data(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                tmp = rxdata_read
                tmp /= 1
            return (1, 1, reg_ptr)
        self.cfg_reg(csr_reg_group(
            'rxdata', 
            offset = 0x004, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('empty', access = 'VOL', width = 1, comments = '''\
Receive FIFO empty
The empty flag indicates if the receive FIFO was empty;
when set, the data field does not contain a valid character.'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 23),
                csr_reg_field_desc('data', access = 'VOL', width = 8, read = func_rxdata_read_data, comments = '''\
Received data
Reading the rxdata register dequeues a character from the receive FIFO, and returns the value in the data field.''')]))
        self.cfg_reg(csr_reg_group(
            'txctrl', 
            offset = 0x008, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('txwm_lv', width = log2_ceil(self.p.tx_fifo_entries), reset = 0, comments = '''\
Transmit watermark level'''),
                csr_reg_field_desc('reserved0', access = 'VOL', width = 11),
                csr_reg_field_desc('flush', width = 1, reset = 0, comments = '''\
fush tx fifo'''),
                csr_reg_field_desc('parity', access = 'RW' if (self.p.parity_check) else 'VOL', width = 2, reset = 0, comments = '''\
parity bit generate control:
0 means no parity
1 means odd generate
2 means even generate'''),
                csr_reg_field_desc('nstop', width = 1, reset = 0, comments = '''\
Number of stop bits
The nstop field specifies the number of stop bits: 0 for one stop bit and 1 for two stop bits.'''),
                csr_reg_field_desc('txen', width = 1, reset = 0, comments = '''\
Transmit enable''')]))
        self.cfg_reg(csr_reg_group(
            'rxctrl',
            offset = 0x00c,
            size = 4,
            fields_desc = [
                csr_reg_field_desc('rxwm_lv', width = log2_ceil(self.p.rx_fifo_entries), reset = 0, comments = '''\
Receive watermark level'''),
                csr_reg_field_desc('reserved1', access = 'VOL', width = 11),
                csr_reg_field_desc('flush', width = 1, reset = 0, comments = '''\
flush rx fifo'''),
                csr_reg_field_desc('parity', access = 'RW' if (self.p.parity_check) else 'VOL', width = 2, reset = 0, comments = '''\
parity bit check control:
0 means no check
1 means odd check
2 means even check'''),
                csr_reg_field_desc('reserved0', access = 'VOL', width = 1),
                csr_reg_field_desc('rxen', width = 1, reset = 0, comments = '''\
Receive enable''')]))
        self.cfg_reg(csr_reg_group(
            'ie', 
            offset = 0x010, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('error', width = 1, reset = 0, comments = '''\
error interrupt enable'''),
                csr_reg_field_desc('rxwm', width = 1, reset = 0, comments = '''\
tx fifo watermark interrupt enable'''),
                csr_reg_field_desc('txwm', width = 1, reset = 0, comments = '''\
tx fifo watermark interrupt enable''')]))
        self.cfg_reg(csr_reg_group(
            'ip', 
            offset = 0x014,
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('error', access = 'RO', width = 1, comments = '''\
error interrupt pending flag'''),
                csr_reg_field_desc('rxwm', access = 'RO', width = 1, comments = '''\
rx fifo watermark interrupt pending flag.
when rx fifo entries number > rxctrl.rxwm_lv, set to 1'''),
                csr_reg_field_desc('txwm', access = 'RO', width = 1, comments = '''\
tx fifo watermark interrupt pending flag.
when tx fifo entries number < txctrl.txwm_lv, set to 1''')]))
        self.cfg_reg(csr_reg_group(
            'div', 
            offset = 0x018, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('div', width = self.p.div_width, reset = self.p.div_init, comments = '''\
baudrate divisor. baudrate = Fin/(16*(div+1))''')]))
        self.cfg_reg(csr_reg_group(
            'status', 
            offset = 0x01c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('rx_cnt', access = 'RO', width = 8, reset = 0, comments = '''\
rx fifo's current entry number'''),
                csr_reg_field_desc('tx_cnt', access = 'RO', width = 8, reset = 0, comments = '''\
tx fifo's current entry number'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 5),
                csr_reg_field_desc('error_stop', width = 1, reset = 0, comments = '''\
rx stop error flag'''),
                csr_reg_field_desc('error_data', width = 1, reset = 0, comments = '''\
rx data error flag'''),
                csr_reg_field_desc('error_start', width = 1, reset = 0, comments = '''\
rx start error flag''')]))

        #baud rate divider
        baud_16x_cnt = reg_r(w = self.regs['div'].div.get_w())
        with when(self.regs['txctrl'].txen | self.regs['rxctrl'].rxen):
            with when(baud_16x_cnt >= self.regs['div'].div):
                baud_16x_cnt /= 0
            with other():
                baud_16x_cnt /= baud_16x_cnt + 1
        baud_16x_tick = bits('baud_16x_tick')
        baud_16x_tick /= baud_16x_cnt == 0


        #tx side
        #{{{
        baud_div = 15
        baud_cnt = reg_r('baud_cnt', w = 4)
        with when(self.regs['txctrl'].txen):
            with when(baud_16x_tick):
                with when(baud_cnt >= baud_div):
                    baud_cnt /= 0
                with other():
                    baud_cnt /= baud_cnt + 1

        #txdata fifo
        tx_fifo = queue(
            'tx_fifo',
            gen = lambda _: bits(_, w = 8), 
            entries = self.p.tx_fifo_entries,
            flush_en = 1)
        tx_fifo.io.flush /= self.regs['txctrl'].flush
        tx_fifo.io.enq.valid /= txdata_write
        tx_fifo.io.enq.bits /= self.regs['txdata'].data
        self.regs['txdata'].full /= ~tx_fifo.io.enq.ready
        self.regs['status'].tx_cnt /= tx_fifo.io.count

        tx_do = bits('tx_do')
        tx_do /= self.regs['txctrl'].txen & baud_16x_tick & (baud_cnt == 0)

        (s_tx_ready, s_tx_start, s_tx_data, s_tx_parity, s_tx_stop, s_tx_gap) = range(6)
        tx_state = reg_rs('tx_state', w = 3, rs = s_tx_ready)
        tx_data_cnt = reg_r(w = 4)
        tx_data_bits_num = mux(self.regs['txctrl'].parity == 0, 7, 8)
        tx_stop_cnt = reg_r(w = 2)

        with when(tx_do):
            with when(tx_state == s_tx_ready):
                with when(tx_fifo.io.deq.valid):
                    tx_state /= s_tx_start
            with when(tx_state == s_tx_start):
                tx_state /= s_tx_data
                tx_data_cnt /= 0
            with when(tx_state == s_tx_data):
                with when(tx_data_cnt == tx_data_bits_num):
                    tx_state /= s_tx_stop
                    tx_stop_cnt /= 0
                with other():
                    tx_data_cnt /= tx_data_cnt + 1
            with when(tx_state == s_tx_stop):
                with when(tx_stop_cnt == self.regs['txctrl'].nstop):
                    tx_state /= s_tx_ready
                with other():
                    tx_stop_cnt /= tx_stop_cnt + 1
            with when(tx_state == s_tx_gap):
                tx_state /= s_tx_ready

        tx_out_reg = reg_s()
        if (self.p.parity_check):
            tx_data_parity = bits(init = 0)
            with when(self.regs['txctrl'].parity == 1):
                tx_data_parity /= tx_fifo.io.deq.bits.r_xor()
            with when(self.regs['txctrl'].parity == 2):
                tx_data_parity /= ~tx_fifo.io.deq.bits.r_xor()
            tx_fifo_deq_all_data = cat([tx_data_parity, tx_fifo.io.deq.bits])
        else:
            tx_fifo_deq_all_data = tx_fifo.io.deq.bits

        with when(tx_state == s_tx_ready):
            tx_out_reg /= 1
        with when(tx_state == s_tx_start):
            tx_out_reg /= 0
        with when(tx_state == s_tx_data):
            tx_out_reg /= sel_bin(tx_data_cnt, tx_fifo_deq_all_data.grouped())
        with when(tx_state == s_tx_stop):
            tx_out_reg /= 1
        with when(tx_state == s_tx_gap):
            tx_out_reg /= 1
        self.io.uart.tx /= tx_out_reg

        #tx_fifo pop
        tx_fifo.io.deq.ready /= 0
        with when(tx_do):
            with when(tx_state == s_tx_stop):
                with when(tx_stop_cnt == self.regs['txctrl'].nstop):
                    tx_fifo.io.deq.ready /= 1

        #if txen = 0, reset FSM
        with when(~self.regs['txctrl'].txen):
            tx_state /= s_tx_ready
            baud_cnt /= 0
            tx_data_cnt /= 0
            tx_stop_cnt /= 0
            tx_out_reg /= 1

        #}}}


        #rx side
        #{{{
        rx_16x_clk = bits('rx_16x_clk')
        rx_16x_clk /= self.regs['rxctrl'].rxen & baud_16x_tick

        (s_rx_ready, s_rx_start, s_rx_data, s_rx_parity, s_rx_stop) = range(5)
        rx_state = reg_rs('rx_state', w = 3)
        rx_data_cnt = reg_r('rx_data_cnt', w = 4)
        rx_data_bits_num = mux(self.regs['rxctrl'].parity == 0, 7, 8)
        rx_sample_cnt = reg_r('rx_sample_cnt', w = 4)
        rx_sample_start = rx_sample_cnt.match_any([0])
        rx_sample_middle= rx_sample_cnt.match_any([7,8,9])
        rx_sample_stop_valid = rx_sample_cnt.match_any([10])
        rx_sample_end = rx_sample_cnt.match_any([15])
        rx_reg_sync = async_dff(self.io.uart.rx, self.p.sync_delay)
        rx_dly1 = reg()
        rx_sample_data = reg('rx_sample_data', w = 3)
        rx_vote_v = count_ones_cmp(rx_sample_data, 2)
        rx_shift_data = reg('rx_shift_data', w = 9)
        rx_has_error_start = bits('rx_has_error_start', init = 0)
        rx_has_error_data = bits('rx_has_error_data', init = 0)
        rx_has_error_stop = bits('rx_has_error_stop', init = 0)
        rx_valid = reg_r('rx_valid')

        with when(rx_16x_clk):
            rx_dly1 /= rx_reg_sync
            rx_sample_cnt /= rx_sample_cnt + 1
            with when(rx_sample_middle):
                rx_sample_data /= cat([rx_sample_data[1:0], rx_reg_sync])

            with when(rx_state == s_rx_ready):
                with when(rx_dly1 & ~rx_reg_sync):
                    rx_state /= s_rx_start
                    rx_sample_cnt /= 0
                    rx_valid /= 0
            with when(rx_state == s_rx_start):
                with when(rx_sample_end):
                    with when(~rx_vote_v):
                        rx_state /= s_rx_data
                        rx_data_cnt /= 0
                    with other(): #fake start
                        rx_state /= s_rx_ready
                        rx_has_error_start /= 1
            with when(rx_state == s_rx_data):
                with when(rx_sample_end):
                    rx_data_cnt /= rx_data_cnt + 1
                    rx_shift_data /= cat([
                        rx_vote_v,
                        rx_shift_data[rx_shift_data.get_w() - 1 : 1]])
                    with when(rx_data_cnt == rx_data_bits_num):
                        rx_state /= s_rx_stop
            with when(rx_state == s_rx_stop):
                with when(rx_sample_stop_valid):
                    rx_state /= s_rx_ready
                    with when(rx_vote_v):
                        rx_valid /= 1
                    with other(): #error stop bit
                        rx_has_error_stop /= 1

        #rx_data fifo
        rx_fifo = queue(
            'rx_fifo', 
            gen = lambda _: bits(_, w = 8), 
            entries = self.p.rx_fifo_entries,
            flush_en = 1)
        self.regs['status'].rx_cnt /= rx_fifo.io.count
        rx_fifo.io.flush /= self.regs['rxctrl'].flush
        rx_enq = ~reg_r(next = rx_valid) & rx_valid
        rx_fifo.io.enq.valid /= rx_enq
        rx_fifo.io.enq.bits /= mux(
            self.regs['rxctrl'].parity == 0,
            rx_shift_data[8:1], 
            rx_shift_data[7:0])
        self.regs['rxdata'].data /= mux(rx_fifo.io.deq.valid, rx_fifo.io.deq.bits, 0)
        self.regs['rxdata'].empty /= ~rx_fifo.io.deq.valid
        rx_fifo.io.deq.ready /= rxdata_read
        rx_data_check_error_odd = rx_shift_data.r_xor()
        rx_data_check_error_even = ~rx_data_check_error_odd
        with when(rx_enq):
            with when(
                (self.regs['rxctrl'].parity == 1) & 
                rx_data_check_error_odd): #odd check
                rx_has_error_data /= 1
            with when(
                (self.regs['rxctrl'].parity == 2) & 
                rx_data_check_error_even): #even check
                rx_has_error_data /= 1
        with when(rx_has_error_start):
            self.regs['status'].error_start /= 1
        with when(rx_has_error_data):
            self.regs['status'].error_data /= 1
        with when(rx_has_error_stop):
            self.regs['status'].error_stop /= 1

        #if rxen = 0, reset FSM
        with when(~self.regs['rxctrl'].rxen):
            rx_state /= s_rx_ready
            rx_data_cnt /= 0
            rx_sample_cnt /= 0
            rx_valid /= 0
        #}}}

        #interrupt
        self.regs['ip'].txwm /= (tx_fifo.io.count < self.regs['txctrl'].txwm_lv)
        self.regs['ip'].rxwm /= (rx_fifo.io.count > self.regs['rxctrl'].rxwm_lv)
        self.regs['ip'].error /= self.regs['status'].error_start | self.regs['status'].error_data | self.regs['status'].error_stop
        self.int_out[0] /= (
            (self.regs['ie'].txwm & self.regs['ip'].txwm) | 
            (self.regs['ie'].rxwm & self.regs['ip'].rxwm) | 
            (self.regs['ie'].error & self.regs['ip'].error))
