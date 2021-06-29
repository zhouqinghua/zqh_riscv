import sys
import os
from phgl_imp import *
from .zqh_spi_parameters import zqh_spi_parameter
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_spi_bundles import zqh_spi_io, zqh_spi_tx_fifo_data
from .zqh_spi_misc import zqh_spi_consts
from zqh_devices.zqh_spi_flash_xip_ctrl.zqh_spi_flash_xip_ctrl_bundles import zqh_spi_flash_xip_io

class zqh_spi(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_spi, self).set_par()
        self.p = zqh_spi_parameter()

    def gen_node_tree(self):
        super(zqh_spi, self).gen_node_tree()
        self.gen_node_slave(
            'spi_slave', 
            tl_type = 'tl_uh', 
            bundle_p = self.p.gen_tl_bundle_p())
        self.p.spi_slave.print_up()
        self.p.spi_slave.print_address_space()

    def set_port(self):
        super(zqh_spi, self).set_port()
        self.io.var(zqh_spi_io('spi', cs_width = self.p.cs_width))
        if (self.p.flash_en):
            self.io.var(zqh_spi_flash_xip_io('xip').flip())

    def main(self):
        super(zqh_spi, self).main()
        self.gen_node_interface('spi_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        #{{{
        self.cfg_reg(csr_reg_group(
            'sckdiv', 
            offset = 0x000, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('div', width = self.p.div_width, reset = self.p.div_init, comments = 'Fsck = Fin/(2*(div+1))')]))
        self.cfg_reg(csr_reg_group(
            'sckmode', 
            offset = 0x004, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('pol', width = 1, reset = 0, comments = '''\
Serial clock polarity:
0 means Inactive state of SCK is logical 0
1 means Inactive state of SCK is logical 1
                    '''),
                csr_reg_field_desc('pha', width = 1, reset = 0, comments = '''\
Serial Clock Phase:
0 means Data is sampled on the leading edge of SCK and shifted on the trailing edge of SCK
1 means Data is shifted on the leading edge of SCK and sampled on the trailing edge of SCK''')]))

        csid_change = reg_r('csid_change')
        with when(csid_change): #keep one cycle and then clear
            csid_change /= 0
        def func_csid_write(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata[log2_up(self.p.cs_width) - 1:0]
                tmp = csid_change
                tmp /= reg_ptr != wdata[1:0] #new data write
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'csid', 
            offset = 0x010, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('csid', width = log2_up(self.p.cs_width), reset = 0, write = func_csid_write, comments = '''\
Chip Select ID, binary format''')]))

        csdef_change = reg_r('csdef_change')
        with when(csdef_change): #keep one cycle and then clear
            csdef_change /= 0
        def func_csdef_write(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata[self.p.cs_width - 1:0]
                tmp = csdef_change
                tmp /= sel_bin(self.regs['csid'].csid, (reg_ptr ^ wdata[self.p.cs_width - 1 : 0]).grouped()) #new data write
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'csdef', 
            offset = 0x014, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('csdef', width = self.p.cs_width, reset = (2**self.p.cs_width - 1), write = func_csdef_write, comments = '''\
Chip Select Default Value''')]))

        csmode_change = reg_r('csmode_change')
        with when(csmode_change): #keep one cycle and then clear
            csmode_change /= 0
        def func_csmode_write(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata[1:0]
                tmp = csmode_change
                tmp /= reg_ptr != wdata[1:0] #new data write
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'csmode', 
            offset = 0x018, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('mode', width = 2, reset = zqh_spi_consts.csmode_auto, write = func_csmode_write, comments = '''\
Chip select mode
0 means AUTO. Assert/de-assert CS at the beginning/end of each frame
2 means HOLD. Keep CS continuously asserted after the initial frame
3 means OFF. Disable hardware control of the CS pin
In HOLD mode, the CS pin is de-asserted only when one of the following conditions occur:
• A different value is written to csmode or csid.
• A write to csdef changes the state of the selected pin.
• Direct-mapped flash mode is enabled.''')]))
        self.cfg_reg(csr_reg_group(
            'spi_ctrl', 
            offset = 0x020, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('rx_cnt', width = 8, access = 'RO', reset = 0, comments = '''\
rx fifo's current entry number'''),
                csr_reg_field_desc('tx_cnt', width = 8, access = 'RO', reset = 0, comments = '''\
tx fifo's current entry number'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 14),
                csr_reg_field_desc('rx_flush', width = 1, reset = 0, comments = '''\
rx fifo flush'''),
                csr_reg_field_desc('tx_flush', width = 1, reset = 0, comments = '''\
tx fifo flush''')]))

        self.cfg_reg(csr_reg_group(
            'delay0', 
            offset = 0x028, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('sckcs', width = 8, reset = 1, comments = '''\
SCK to CS Delay
The sckcs field specifies the delay between the last trailing edge of SCK and the de-assertion of CS.
When sckmode:pha = 1, an additional half-period delay is implicit.'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 8),
                csr_reg_field_desc('cssck', width = 8, reset = 1, comments = '''\
CS to SCK Delay
The cssck field specifies the delay between the assertion of CS and the first leading edge of SCK.
When sckmode:pha = 0, an additional half-period delay is implicit.''')]))
        self.cfg_reg(csr_reg_group(
            'delay1', 
            offset = 0x02c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('interxfr', width = 8, reset = 0, comments = '''\
Maximum interframe delay
The interxfr field specifies the delay between two consecutive frames without de-asserting CS.
This is applicable only when sckmode is HOLD or OFF.'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 8),
                csr_reg_field_desc('intercs', width = 8, reset = 1, comments = '''\
Minimum CS inactive time
The intercs field specifies the minimum CS inactive time between de-assertion and assertion.''')]))
        self.cfg_reg(csr_reg_group(
            'fmt', 
            offset = 0x040, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('len', width = 4, reset = 8, comments = '''\
Number of bits per frame'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 12),
                csr_reg_field_desc('dir', width = 1, reset = 1 if (self.p.flash_en) else 0, comments = '''\
SPI I/O Direction
0 means Rx. For dual and quad protocols, the DQ pins are tri-stated. For the single protocol, the DQ0 pin is driven with the transmit data as normal.
1 means Tx. The receive FIFO is not populated.'''),
                csr_reg_field_desc('endian', width = 1, reset = 0, comments = '''\
SPI Endianness
0 means Transmit most-significant bit (MSB) first
1 menas Transmit least-significant bit (LSB) first'''),
                csr_reg_field_desc('proto', width = 2, reset = zqh_spi_consts.proto_single, comments = '''\
SPI Protocol
0 means Single. DQ0 (MOSI), DQ1 (MISO)
1 means Dual. DQ0, DQ1
2 means Quad. DQ0, DQ1, DQ2, DQ''')]))

        txdata_write = bits('txdata_write', init = 0)
        def func_txdata_write_data(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata[7:0]
                tmp = txdata_write
                tmp /= 1
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'txdata', 
            offset = 0x048, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('full', access = 'VOL', width = 1, comments = '''\
FIFO full flag
The full flag indicates whether the transmit FIFO is ready to accept new entries;
when set, writes to txdata are ignored.'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 23),
                csr_reg_field_desc('data', access = 'VOL', width = 8, write = func_txdata_write_data, comments = '''\
Transmit data
Writing to the txdata register loads the transmit FIFO with the value contained in the data field.
For fmt:len < 8, values should be left-aligned when fmt.endian = MSB and right-aligned when fmt.endian = LSB.''')]))

        rxdata_read = bits(init = 0)
        def func_rxdata_read_data(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                tmp = rxdata_read
                tmp /= 1
            return (1, 1, reg_ptr)
        self.cfg_reg(csr_reg_group(
            'rxdata', 
            offset = 0x04c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('empty', access = 'VOL', width = 1, comments = '''\
FIFO empty flag
The empty flag indicates whether the receive FIFO contains new entries to be read;
when set, the data field does not contain a valid frame. Writes to rxdata are ignored.'''), 
                csr_reg_field_desc('reserved', access = 'VOL', width = 23), 
                csr_reg_field_desc('data', access = 'VOL', width = 8, read = func_rxdata_read_data, comments = '''\
Received data
Reading the rxdata register dequeues a frame from the receive FIFO. 
For fmt:len < 8, values are left-aligned when fmt.endian = MSB and right-aligned when fmt.endian = LSB.''')]))
        self.cfg_reg(csr_reg_group(
            'txmark', 
            offset = 0x050, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('txmark', width = log2_ceil(self.p.tx_fifo_entries), reset = 1 if (self.p.flash_en) else 0, comments = '''\
Transmit watermark
The txmark register specifies the threshold at which the Tx FIFO watermark interrupt triggers.
fifo entry number < watermark will trigger interrupt.''')]))
        self.cfg_reg(csr_reg_group(
            'rxmark', 
            offset = 0x054, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('rxmark', width = log2_ceil(self.p.rx_fifo_entries), reset = 0, comments = '''\
Receive watermark
The rxmark register specifies the threshold at which the Rx FIFO watermark interrupt triggers.
fifo entry > watermark will trigger interrupt.''')]))

        flash_en_pos = reg_r('flash_en_pos')
        if (self.p.flash_en):
            with when(flash_en_pos): #keep one cycle and then clear
                flash_en_pos /= 0
            def func_fctrl_en_write(reg_ptr, fire, address, size, wdata, mask_bit):
                with when(fire):
                    with when(mask_bit[0]):
                        reg_ptr /= wdata[0]
                        tmp = flash_en_pos
                        tmp /= ~reg_ptr & wdata[0]
                return (1, 1)
            self.cfg_reg(csr_reg_group(
                'fctrl', 
                offset = 0x060, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('en', width = 1, reset = 1, write = func_fctrl_en_write, comments = '''\
SPI Flash Mode Select
When the en bit of the fctrl register is set, the controller enters SPI flash mode.
Accesses to the direct-mapped memory region causes the controller to automatically sequence SPI flash reads in hardware.''')]))
            self.cfg_reg(csr_reg_group(
                'ffmt', 
                offset = 0x064, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('pad_code', width = 8, reset = 0, comments = '''\
First 8 bits to transmit during dummy cycles'''), 
                    csr_reg_field_desc('cmd_code', width = 8, reset = 3, comments = '''\
Value of command byte'''), 
                    csr_reg_field_desc('reserved', access = 'VOL', width = 2), 
                    csr_reg_field_desc('data_proto', width = 2, reset = 0, comments = '''\
Protocol for receiving data bytes
same means as fmt.proto'''), 
                    csr_reg_field_desc('addr_proto', width = 2, reset = 0, comments = '''\
Protocol for transmitting address and padding
same means as fmt.proto'''), 
                    csr_reg_field_desc('cmd_proto', width = 2, reset = 0, comments = '''\
Protocol for transmitting command
same means as fmt.proto'''), 
                    csr_reg_field_desc('pad_cnt', width = 4, reset = 0, comments = '''\
Number of dummy cycles'''), 
                    csr_reg_field_desc('addr_len', width = 3, reset = 3, comments = '''\
Number of address bytes(0 to 4)'''), 
                    csr_reg_field_desc('cmd_en', width = 1, reset = 1, comments = '''\
Enable sending of command''')]))
        self.cfg_reg(csr_reg_group(
            'ie', 
            offset = 0x070, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('rxwm', width = 1, reset = 0, comments = '''\
Receive watermark enable'''), 
                csr_reg_field_desc('txwm', width = 1, reset = 0, comments = '''\
Transmit watermark enable''')]))
        self.cfg_reg(csr_reg_group(
            'ip', 
            offset = 0x074, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('rxwm', access = 'RO', width = 1, reset = 0, comments = '''\
Receive watermark pending'''),
                csr_reg_field_desc('txwm', access = 'RO', width = 1, reset = 0, comments = '''\
Transmit watermark pending''')]))
        #}}}

        baud_cnt = reg_r('baud_cnt', w = self.p.div_width)
        with when(baud_cnt >= self.regs['sckdiv'].div):
            baud_cnt /= 0
        with other():
            baud_cnt /= baud_cnt + 1
        sck_reg = reg_r('sck_reg')
        sck_flip = bits('sck_flip', init = (baud_cnt == 0))
        cs_reg = reg_s('cs_reg', w = self.p.cs_width)
        active_reg = reg_r('active_reg')
        oe_reg = reg_r('oe_reg')
        do_reg = vec('do_reg', gen = reg, n = 4)
        proto_reg = reg('proto_reg', w = 2)
        dq_input = vec('dq_input', gen = bits, n = len(self.io.spi.dq))


        #txdata fifo
        tx_fifo = queue(
            'tx_fifo', 
            gen = zqh_spi_tx_fifo_data, 
            entries = self.p.tx_fifo_entries,
            flush_en = 1)
        tx_fifo.io.flush /= self.regs['spi_ctrl'].tx_flush
        tx_fifo.io.enq.valid /= txdata_write
        tx_fifo.io.enq.bits.data /= self.regs['txdata'].data
        tx_fifo.io.enq.bits.proto /= self.regs['fmt'].proto
        tx_fifo.io.enq.bits.endian /= self.regs['fmt'].endian
        tx_fifo.io.enq.bits.dir /= self.regs['fmt'].dir
        tx_fifo.io.enq.bits.len /= self.regs['fmt'].len
        tx_fifo.io.enq.bits.csmode /= self.regs['csmode'].mode
        tx_fifo.io.enq.bits.pol /= self.regs['sckmode'].pol
        tx_fifo.io.enq.bits.pha /= self.regs['sckmode'].pha
        self.regs['txdata'].full /= ~tx_fifo.io.enq.ready
        self.regs['spi_ctrl'].tx_cnt /= tx_fifo.io.count


        (s_idle, s_cs_init, s_sample, s_shift, s_stall, s_cs_end) = range(6)
        state = reg_rs('state', w = 3, rs = s_idle)
        delay_cnt = reg_r('delay_cnt', w = 9)
        delay_cnt_reset = bits('delay_cnt_reset', init = 0)
        delay_cnt_incr = bits('delay_cnt_incr', init = 0)
        with when(delay_cnt_reset):
            delay_cnt /= 0
        with elsewhen(delay_cnt_incr):
            delay_cnt /= delay_cnt + 1
        data_bits_cnt = reg_r('data_bits_cnt', w = 3)
        data_bits_cnt_add1_proto = (data_bits_cnt + 1) << tx_fifo.io.deq.bits.proto
        data_bits_cnt_reset = bits('data_bits_cnt_reset', init = 0)
        data_bits_cnt_incr = bits('data_bits_cnt_incr', init = 0)
        with when(data_bits_cnt_reset):
            data_bits_cnt /= 0
        with elsewhen(data_bits_cnt_incr):
            data_bits_cnt /= data_bits_cnt + 1
        sample_data_reg = reg('sample_data_reg', w = 8)
        shift_data_reg = reg('shift_data_reg', w = 8)
        sck_reg_flip_en = reg_r('sck_reg_flip_en')
        rx_valid = reg_r('rx_valid')

        #when csmode = hold and cs pin in valid state,
        #cs will be updated to invalid in following conditions
        cs_hold_invalid = reg_r('cs_hold_invalid')
        with when(state == s_idle):
            cs_hold_invalid /= 0
        with other():
            with when(csmode_change | csid_change | csdef_change | flash_en_pos):
                cs_hold_invalid /= 1


        ####
        #FSM
        with when(sck_flip):
            with when(state == s_idle):
                with when(delay_cnt == (self.regs['delay1'].intercs << 1)):
                    with when(tx_fifo.io.deq.valid):
                        state /= s_cs_init
                        delay_cnt_reset /= 1
                        shift_data_reg /= tx_fifo.io.deq.bits.data
                        sck_reg_flip_en /= 0
                with other():
                    delay_cnt_incr /= 1
            with when(state == s_cs_init):
                rx_valid /= 0
                with when(delay_cnt == (self.regs['delay0'].cssck << 1)):
                    data_bits_cnt_reset /= 1
                    state /= s_shift
                    with when(~tx_fifo.io.deq.bits.pha):
                        sck_reg_flip_en /= 0
                    with other():
                        sck_reg_flip_en /= 1
                with other():
                    delay_cnt_incr /= 1
            with when(state == s_shift):
                sck_reg_flip_en /= 1
                state /= s_sample
            with when(state == s_sample):
                data_bits_cnt_incr /= 1
                with when(data_bits_cnt_add1_proto >= tx_fifo.io.deq.bits.len):
                    rx_valid /= ~tx_fifo.io.deq.bits.dir
                    delay_cnt_reset /= 1
                    with when(tx_fifo.io.deq.bits.csmode == zqh_spi_consts.csmode_auto):
                        state /= s_cs_end
                        with when(tx_fifo.io.deq.bits.pha):
                            sck_reg_flip_en /= 0
                    with other():
                        state /= s_stall
                        sck_reg_flip_en /= 0
                with other():
                    state /= s_shift
            with when(state == s_stall):
                with when(delay_cnt == (self.regs['delay1'].interxfr << 1)):
                    with when(tx_fifo.io.deq.valid):
                        rx_valid /= 0
                        data_bits_cnt_reset /= 1
                        shift_data_reg /= tx_fifo.io.deq.bits.data
                        state /= s_shift
                        sck_reg_flip_en /= 1
                    # need wait tx_fifo empty
                    with elsewhen(cs_hold_invalid & (tx_fifo.io.count == 0)):
                        state /= s_cs_end
                        delay_cnt_reset /= 1
                        cs_hold_invalid /= 0 #clear the flag
                with other():
                    delay_cnt_incr /= 1
            with when(state == s_cs_end):
                sck_reg_flip_en /= 0
                with when(delay_cnt == (self.regs['delay0'].sckcs << 1)):
                    state /= s_idle
                    delay_cnt_reset /= 1
                with other():
                    delay_cnt_incr /= 1

        #rx_data fifo
        rx_fifo = queue(
            'rx_fifo', 
            gen = lambda _: bits(_, w = 8),
            entries = self.p.rx_fifo_entries,
            flush_en = 1)
        rx_fifo.io.flush /= self.regs['spi_ctrl'].rx_flush
        rx_enq = ~reg_r(next = rx_valid) & rx_valid
        rx_fifo.io.enq.valid /= rx_enq
        rx_fifo.io.enq.bits /= sample_data_reg
        self.regs['rxdata'].data /= mux(rx_fifo.io.deq.valid, rx_fifo.io.deq.bits, 0)
        self.regs['rxdata'].empty /= ~rx_fifo.io.deq.valid
        self.regs['spi_ctrl'].rx_cnt /= rx_fifo.io.count
        rx_fifo.io.deq.ready /= rxdata_read

        tx_fifo.io.deq.ready /= 0
        with when(sck_flip):
            with when(state == s_idle):
                active_reg /= 0
            with other():
                active_reg /= 1

            with when(state == s_idle):
                sck_reg /= self.regs['sckmode'].pol
                cs_reg /= self.regs['csdef'].csdef
                oe_reg /= 0
            with elsewhen(state == s_cs_end):
                sck_reg /= self.regs['sckmode'].pol
            with other():
                with when(sck_reg_flip_en):
                    sck_reg /= ~sck_reg

                with when(self.regs['csmode'].mode == zqh_spi_consts.csmode_off):
                    cs_reg /= self.regs['csdef'].csdef
                with other():
                    cs_reg /= bin2oh(self.regs['csid'].csid) ^ self.regs['csdef'].csdef

            with when(state == s_sample):
                sample_data_reg /= sel_map(
                    tx_fifo.io.deq.bits.proto,
                    ((zqh_spi_consts.proto_single, mux(
                        tx_fifo.io.deq.bits.endian,
                        cat([dq_input[0], sample_data_reg[7:1]]),
                        cat([sample_data_reg[6:0], dq_input[0]]))),
                     (zqh_spi_consts.proto_dual  , mux(
                         tx_fifo.io.deq.bits.endian,
                         cat([dq_input[1], dq_input[0], sample_data_reg[7:2]]),
                         cat([sample_data_reg[5:0], dq_input[1], dq_input[0]]))),
                     (zqh_spi_consts.proto_quad  , mux(
                         tx_fifo.io.deq.bits.endian,
                         cat([
                             dq_input[3], 
                             dq_input[2], 
                             dq_input[1], 
                             dq_input[0], 
                             sample_data_reg[7:4]]),
                         cat([
                             sample_data_reg[3:0], 
                             dq_input[3], 
                             dq_input[2], 
                             dq_input[1], 
                             dq_input[0]])))))
            
            with when(state == s_shift):
                shift_data_reg /= sel_map(
                    tx_fifo.io.deq.bits.proto,
                    ((zqh_spi_consts.proto_single, mux(
                        tx_fifo.io.deq.bits.endian,
                        cat([value(0), shift_data_reg[7:1]]),
                        cat([shift_data_reg[6:0], value(0)]))),
                     (zqh_spi_consts.proto_dual  , mux(
                         tx_fifo.io.deq.bits.endian,
                         cat([value(0, w = 2), shift_data_reg[7:2]]),
                         cat([shift_data_reg[5:0], value(0, w = 2)]))),
                     (zqh_spi_consts.proto_quad  , mux(
                         tx_fifo.io.deq.bits.endian,
                         cat([value(0, w = 4), shift_data_reg[7:4]]),
                         cat([shift_data_reg[3:0], value(0, w = 4)])))))

                beat_slc = mux(
                    tx_fifo.io.deq.bits.endian,
                    shift_data_reg[3:0], 
                    shift_data_reg[7:4].order_invert())
                beat_slc_endian_dual = mux(
                    tx_fifo.io.deq.bits.endian, 
                    beat_slc[1:0], 
                    beat_slc[1:0].order_invert())
                beat_slc_endian_quad = mux(
                    tx_fifo.io.deq.bits.endian, 
                    beat_slc, 
                    beat_slc.order_invert())
                with when(tx_fifo.io.deq.bits.proto == zqh_spi_consts.proto_single):
                    do_reg[0] /= beat_slc[0]
                with when(tx_fifo.io.deq.bits.proto == zqh_spi_consts.proto_dual):
                    do_reg[0] /= beat_slc_endian_dual[0]
                    do_reg[1] /= beat_slc_endian_dual[1]
                with when(tx_fifo.io.deq.bits.proto == zqh_spi_consts.proto_quad):
                    do_reg[0] /= beat_slc_endian_quad[0]
                    do_reg[1] /= beat_slc_endian_quad[1]
                    do_reg[2] /= beat_slc_endian_quad[2]
                    do_reg[3] /= beat_slc_endian_quad[3]

            with when(state == s_sample):
                with when(data_bits_cnt_add1_proto >= tx_fifo.io.deq.bits.len):
                    tx_fifo.io.deq.ready /= 1

            with when(tx_fifo.io.deq.valid):
                with when(state.match_any([s_idle, s_stall])):
                    proto_reg /= tx_fifo.io.deq.bits.proto

            with when(state.match_any([s_shift, s_sample])):
                with when(tx_fifo.io.deq.bits.proto.match_any([
                    zqh_spi_consts.proto_dual,
                    zqh_spi_consts.proto_quad])):
                    oe_reg /= tx_fifo.io.deq.bits.dir
                with other():
                    oe_reg /= 0
            with when(state.match_any([s_stall])):
                oe_reg /= 0

        self.io.spi.sck /= sck_reg
        self.io.spi.cs /= cs_reg
        for i in range(len(self.io.spi.dq)):
            self.io.spi.dq[i].oe /= oe_reg
            self.io.spi.dq[i].output /= do_reg[i]

        ####
        #flash xip
        if (self.p.flash_en):
            self.flash_xip(tx_fifo, rx_fifo)

        #interrupt
        self.regs['ip'].txwm /= (tx_fifo.io.count < self.regs['txmark'].txmark)
        self.regs['ip'].rxwm /= (rx_fifo.io.count > self.regs['rxmark'].rxmark)
        self.int_out[0] /= (
            (self.regs['ie'].txwm & self.regs['ip'].txwm) | 
            (self.regs['ie'].rxwm & self.regs['ip'].rxwm))


        #overwrite pad's oe and input according proto and active
        #default value
        for i in range(len(self.io.spi.dq)):
            dq_input[i] /= self.io.spi.dq[i].input
        with when(active_reg):
            with when(proto_reg == zqh_spi_consts.proto_single):
                #no tri-state in single mode
                #dq[0] is output, dq[1] is input, dq[2:3] force to input
                for i in range(len(self.io.spi.dq)):
                    if (i == 0):
                        self.io.spi.dq[i].oe /= 1
                        dq_input[i] /= self.io.spi.dq[1].input
                    else:
                        self.io.spi.dq[i].oe /= 0
            with when(proto_reg == zqh_spi_consts.proto_dual):
                #only use dq[0:1], dq[2:3] force to input
                for i in range(len(self.io.spi.dq)):
                    if (i >= 2):
                        self.io.spi.dq[i].oe /= 0

    def flash_xip(self, tx_fifo, rx_fifo):
        flash_req_valid = reg_r('flash_req_valid')
        flash_req_size = reg('flash_req_size', w = self.io.xip.req.bits.size.get_w())
        flash_req_addr = reg('flash_req_addr', w = self.io.xip.req.bits.addr.get_w())
        with when(self.io.xip.req.fire()):
            flash_req_valid /= 1
            flash_req_size /= self.io.xip.req.bits.size
            flash_req_addr /= self.io.xip.req.bits.addr
        flash_req_len = 1 << flash_req_size
        self.io.xip.resp.valid /= 0

        (
            s_flash_idle, s_flash_cmd, s_flash_addr, s_flash_dummy, 
            s_flash_data, s_flash_resp) = range(6)
        flash_state = reg_rs('flash_state', w = 3, rs = s_flash_idle)
        flash_cnt = reg_r('flash_cnt', w = 8)
        flash_cnt_reset_0 = bits(init = 0)
        flash_cnt_reset_1 = bits(init = 0)
        flash_cnt_incr = bits(init = 0)
        flash_resp_cnt = reg_r('flash_resp_cnt', w = 8)
        with when(flash_cnt_reset_0):
            flash_cnt /= 0
        with elsewhen(flash_cnt_reset_1):
            flash_cnt /= 1
        with elsewhen(flash_cnt_incr):
            flash_cnt /= flash_cnt + 1

        with when(flash_state == s_flash_idle):
            #csmode need change to auto mode
            #program IO access mode will use hold/off mode
            #when program IO is accessing spi, xip should no go
            #software need change back csmode to auto mode when access is finished
            #when csmode is auto mode, it means spi bus is free for xip(memory map) access
            with when(self.regs['csmode'].mode == zqh_spi_consts.csmode_auto):
                with when(flash_req_valid):
                    with when(self.regs['ffmt'].cmd_en):
                        flash_state /= s_flash_cmd
                    with elsewhen(self.regs['ffmt'].addr_len != 0):
                        flash_state /= s_flash_addr
                        flash_cnt_reset_0 /= 1
                    with elsewhen(self.regs['ffmt'].pad_cnt != 0):
                        flash_state /= s_flash_dummy
                        flash_cnt_reset_1 /= 1
                    with other():
                        flash_state /= s_flash_data
                        flash_cnt_reset_1 /= 1
                        flash_resp_cnt /= 1
        with when(flash_state == s_flash_cmd):
            with when(tx_fifo.io.enq.fire()):
                with when(self.regs['ffmt'].addr_len != 0):
                    flash_state /= s_flash_addr
                    flash_cnt_reset_0 /= 1
                with elsewhen(self.regs['ffmt'].pad_cnt != 0):
                    flash_state /= s_flash_dummy
                    flash_cnt_reset_1 /= 1
                with other():
                    flash_state /= s_flash_data
                    flash_cnt_reset_1 /= 1
                    flash_resp_cnt /= 1
        with when(flash_state == s_flash_addr):
            with when(tx_fifo.io.enq.fire()):
                with when((flash_cnt + 1) == self.regs['ffmt'].addr_len):
                    with when(self.regs['ffmt'].pad_cnt != 0):
                        flash_state /= s_flash_dummy
                        flash_cnt_reset_1 /= 1
                    with other():
                        flash_state /= s_flash_data
                        flash_cnt_reset_1 /= 1
                        flash_resp_cnt /= 1
        with when(flash_state == s_flash_dummy):
            with when(tx_fifo.io.enq.fire()):
                with when(flash_cnt == self.regs['ffmt'].pad_cnt):
                    flash_state /= s_flash_data
                    flash_cnt_reset_1 /= 1
                    flash_resp_cnt /= 1
        with when(flash_state == s_flash_data):
            with when(tx_fifo.io.enq.fire()):
                with when(flash_cnt == flash_req_len):
                    flash_state /= s_flash_resp
        with when(flash_state == s_flash_resp):
            with when(rx_fifo.io.deq.fire()):
                with when(flash_resp_cnt == flash_req_len):
                    flash_state /= s_flash_idle
                    flash_req_valid /= 0

        self.io.xip.req.ready /= self.regs['fctrl'].en
        with when(flash_req_valid):
            self.io.xip.req.ready /= 0

        with when(flash_state == s_flash_addr):
            with when(tx_fifo.io.enq.fire()):
                flash_cnt_incr /= 1

        with when(flash_state == s_flash_dummy):
            with when(tx_fifo.io.enq.fire()):
                flash_cnt_incr /= 1

        with when(flash_state == s_flash_data):
            with when(tx_fifo.io.enq.fire()):
                flash_cnt_incr /= 1

        with when(flash_state.match_any([s_flash_data, s_flash_resp])):
            with when(rx_fifo.io.deq.fire()):
                flash_resp_cnt /= flash_resp_cnt + 1

        with when(flash_state == s_flash_cmd):
            tx_fifo.io.enq.valid /= 1
            tx_fifo.io.enq.bits.data /= self.regs['ffmt'].cmd_code
            tx_fifo.io.enq.bits.proto /= self.regs['ffmt'].cmd_proto
            tx_fifo.io.enq.bits.endian /= self.regs['fmt'].endian
            tx_fifo.io.enq.bits.dir /= 1
            tx_fifo.io.enq.bits.len /= 8
            tx_fifo.io.enq.bits.csmode /= zqh_spi_consts.csmode_hold
            tx_fifo.io.enq.bits.pol /= self.regs['sckmode'].pol
            tx_fifo.io.enq.bits.pha /= self.regs['sckmode'].pha
        with when(flash_state == s_flash_addr):
            tx_fifo.io.enq.valid /= 1
            flash_addr_byte = sel_map(
                self.regs['ffmt'].addr_len,
                list(map(
                    lambda _:(_, sel_bin(
                        flash_cnt[1:0],
                        list(reversed(flash_req_addr[_*8 -1 : 0].grouped(8))))),
                    range(1, 5))))
            tx_fifo.io.enq.bits.data /= flash_addr_byte
            tx_fifo.io.enq.bits.proto /= self.regs['ffmt'].addr_proto
            tx_fifo.io.enq.bits.endian /= self.regs['fmt'].endian
            tx_fifo.io.enq.bits.dir /= 1
            tx_fifo.io.enq.bits.len /= 8
            tx_fifo.io.enq.bits.csmode /= zqh_spi_consts.csmode_hold
            tx_fifo.io.enq.bits.pol /= self.regs['sckmode'].pol
            tx_fifo.io.enq.bits.pha /= self.regs['sckmode'].pha
        with when(flash_state == s_flash_dummy):
            tx_fifo.io.enq.valid /= 1
            tx_fifo.io.enq.bits.data /= self.regs['ffmt'].pad_code
            tx_fifo.io.enq.bits.proto /= self.regs['ffmt'].addr_proto
            tx_fifo.io.enq.bits.endian /= self.regs['fmt'].endian
            tx_fifo.io.enq.bits.dir /= 1
            tx_fifo.io.enq.bits.len /= 8
            tx_fifo.io.enq.bits.csmode /= zqh_spi_consts.csmode_hold
            tx_fifo.io.enq.bits.pol /= self.regs['sckmode'].pol
            tx_fifo.io.enq.bits.pha /= self.regs['sckmode'].pha
        with when(flash_state == s_flash_data):
            tx_fifo.io.enq.valid /= 1
            tx_fifo.io.enq.bits.data /= 0
            tx_fifo.io.enq.bits.proto /= self.regs['ffmt'].data_proto
            tx_fifo.io.enq.bits.endian /= self.regs['fmt'].endian
            tx_fifo.io.enq.bits.dir /= 0
            tx_fifo.io.enq.bits.len /= 8
            tx_fifo.io.enq.bits.csmode /= mux(
                flash_cnt == flash_req_len,
                zqh_spi_consts.csmode_auto, 
                zqh_spi_consts.csmode_hold)
            tx_fifo.io.enq.bits.pol /= self.regs['sckmode'].pol
            tx_fifo.io.enq.bits.pha /= self.regs['sckmode'].pha

        self.io.xip.resp.bits.data /= rx_fifo.io.deq.bits
        with when(flash_state.match_any([s_flash_data, s_flash_resp])):
            self.io.xip.resp.valid /= rx_fifo.io.deq.valid
            rx_fifo.io.deq.ready /= self.io.xip.resp.ready
