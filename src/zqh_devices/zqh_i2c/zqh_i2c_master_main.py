import sys
import os
from phgl_imp import *
from .zqh_i2c_master_parameters import zqh_i2c_master_parameter
from .zqh_i2c_master_misc import zqh_i2c_master_consts
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_i2c_master_bundles import zqh_i2c_master_io
from .zqh_i2c_master_bundles import zqh_i2c_master_status_bundle
from .zqh_i2c_master_bundles import zqh_i2c_master_command_bundle

class zqh_i2c_master(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_i2c_master, self).set_par()
        self.p = zqh_i2c_master_parameter()

    def gen_node_tree(self):
        super(zqh_i2c_master, self).gen_node_tree()
        self.gen_node_slave(
            'i2c_master_slave',
            tl_type = 'tl_uh', 
            bundle_p = self.p.gen_tl_bundle_p())
        self.p.i2c_master_slave.print_up()
        self.p.i2c_master_slave.print_address_space()

    def set_port(self):
        super(zqh_i2c_master, self).set_port()
        self.io.var(zqh_i2c_master_io('i2c'))

    def main(self):
        super(zqh_i2c_master, self).main()
        self.gen_node_interface('i2c_master_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        #{{{
        self.cfg_reg(csr_reg_group(
            'div', 
            offset = 0x000, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('div', width = 16, reset = 0xffff, comments = '''\
scl clock divisor. Fscl = Fin/(24*(div+1))
                        ''')]))
        self.cfg_reg(csr_reg_group(
            'control', 
            offset = 0x004, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('multi_master', width = 1, reset = 0, access = 'RW' if (self.p.multi_master_support) else 'VOL', comments = '''\
multi master arbitration enable'''),
                csr_reg_field_desc('scl_stretch_disable', width = 1, reset = 0, comments = '''\
slave stretch sck disable
this bit can only be set when all i2c slave could not stretch sck line'''),
                csr_reg_field_desc('en', width = 1, reset = 0, comments = '''\
i2c device enable''')]))
        self.cfg_reg(csr_reg_group(
            'cfg', 
            offset = 0x008, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('undef_cond_check', width = 6, reset = 0, access = 'RW' if (self.p.multi_master_support) else 'VOL', comments = '''\
when multi master is enable. this field should be set.
undefine condition will be checked and report to status reg'''), 
                csr_reg_field_desc('reserved2', access = 'VOL', width = 3), 
                csr_reg_field_desc('t_sample', width = 5, reset = 17, comments = '''\
@ t_sample, sample sda's data(input)'''), 
                csr_reg_field_desc('reserved1', access = 'VOL', width = 3), 
                csr_reg_field_desc('t_hd_dat', width = 5, reset = 0, comments = '''\
@ tick t_hd_dat, sda drive new data bit(output)'''), 
                csr_reg_field_desc('reserved0', access = 'VOL', width = 3), 
                csr_reg_field_desc('t_low', width = 5, reset = 11, comments = '''\
sck period tick from 0 to 23. period start from sck's negedge
@ tick t_low, scl change from 0 to 1
scl low time duty = (t_low + 1)/24''')]))

        sda_rx_data = reg_r(w = 8)
        def func_data_read(reg_ptr, fire, address, size, mask_bit):
            return (1, 1, sda_rx_data)
        self.cfg_reg(csr_reg_group(
            'data', 
            offset = 0x00c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 8, read = func_data_read, comments = '''\
tx or rx data:
write this reg will store the tx sda data.
read this reg will get the rx sda data.''')]))

        status_reg = zqh_i2c_master_status_bundle('status_reg').as_reg(tp = 'reg_r')
        cmd_write = reg_r()
        with when(cmd_write): #keep one cycle and then clear
            cmd_write /= 0
        def func_cmd_write(reg_ptr, fire, address, size, wdata, mask_bit):
            tmp = cmd_write
            with when(fire):
                with when(mask_bit[7:0] != 0):
                    reg_ptr /= wdata[7:0]
                    tmp /= 1

                    # new cmd write will force status.trans_progress's set
                    status_reg.trans_progress /= 1
                    status_reg.arb_lost /= 0
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'cmd', 
            offset = 0x010, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 8, reset = 0, write = func_cmd_write, comments = '''\
i2c action command bit map, 1 means valid:
[4]: ack
[3]: write
[2]: read
[1]: stop
[0]: start''')]))

        def func_status_read(reg_ptr, fire, address, size, mask_bit):
            return (1, 1, status_reg.pack())
        self.cfg_reg(csr_reg_group(
            'status', 
            offset = 0x014, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = 7, read = func_status_read, comments = '''\
i2c bus status:
[6]: trans_progress
[5:3]: reserved
[0]: arb_lost
[0]: busy
[0]: recv_ack''')]))

        self.cfg_reg(csr_reg_group(
            'ie', 
            offset = 0x018, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('en', width = 1, reset = 0, comments = '''\
interrupt enable''')]))
        self.cfg_reg(csr_reg_group(
            'ip', 
            offset = 0x01c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('valid', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
interrupt pending valid:
when status.trans_progress change from 1 to 0 or arb lost, valid bit will be set.
software write this field with 1 will clear it to 0.''')]))
        #}}}

        scl_max_time = 23
        scl_low_time = self.regs['cfg'].t_low
        sda_sample_time = self.regs['cfg'].t_sample
        sda_hold_time = self.regs['cfg'].t_hd_dat


        #scl clock cnt
        scl_cnt = reg_r('scl_cnt', w = self.regs['div'].div.get_w())
        scl_cnt_speed_up_next = bits('scl_cnt_speed_up_next', init = 0)
        if (self.p.multi_master_support):
            scl_cnt_speed_up_reg = reg_r(
                'scl_cnt_speed_up_reg',
                next = scl_cnt_speed_up_next)
            scl_cnt_speed_up_next /= scl_cnt_speed_up_reg
        with when(self.regs['control'].en):
            with when(scl_cnt >= self.regs['div'].div):
                scl_cnt /= 0
            with elsewhen(scl_cnt_speed_up_next):
                scl_cnt /= 0
            with other():
                scl_cnt /= scl_cnt + 1

        scl_tick = bits('scl_tick')
        scl_tick /= scl_cnt == 0


        #scl/sda input glitch filter and sync
        scl_input_reg_filter = reg_s('scl_input_reg_filter', w = 3)
        scl_input_reg_filter /= cat([
            scl_input_reg_filter[1:0], 
            async_dff(self.io.i2c.scl.input, self.p.sync_delay)])
        scl_input_sync = bits(
            'scl_input_sync', 
            init = count_ones_cmp(scl_input_reg_filter, 2))
        scl_input_sync_dly = reg_s('scl_input_sync_dly', next = scl_input_sync)

        sda_input_reg_filter = reg_s('sda_input_reg_filter', w = 3)
        sda_input_reg_filter /= cat([
            sda_input_reg_filter[1:0], 
            async_dff(self.io.i2c.sda.input, self.p.sync_delay)])
        sda_input_sync = bits(
            'sda_input_sync',
            init = count_ones_cmp(sda_input_reg_filter, 2))
        sda_input_sync_dly = reg_s('sda_input_sync_dly', next = sda_input_sync)

        #cmd
        cmd_reg = zqh_i2c_master_command_bundle('cmd_reg').as_reg(tp = 'reg_r')
        with when(cmd_write):
            cmd_reg /= self.regs['cmd'].data
        cmd_reg_valid = cmd_reg.start | cmd_reg.stop | cmd_reg.read | cmd_reg.write


        #FSM
        (
            s_idle, s_start, s_write, s_read, 
            s_stop, s_ack_w, s_ack_r, s_hold0, s_stop_check) = range(9)
        state = reg_rs('state', rs = s_idle, w = 4)
        data_bits_cnt = reg_r('data_bits_cnt', w = 4)
        scl_tick_cnt = reg_r('scl_tick_cnt', w = 5)
        scl_tick_cnt_add = bits('scl_tick_cnt_add', init = 0)
        sda_check = reg_r('sda_check', next = 0)
        scl_tick_cnt_reset_0 = bits('scl_tick_cnt_reset_0', init = 0)
        with when(scl_tick_cnt_add):
            with when(scl_tick_cnt == scl_max_time):
                scl_tick_cnt /= 0
            with other():
                scl_tick_cnt /= scl_tick_cnt + 1
        with when(scl_tick_cnt_reset_0):
            scl_tick_cnt /= 0
        scl_out_reg = reg_s('scl_out_reg')
        sda_out_reg = reg_s('sda_out_reg')
        sda_tx_bit = sel(data_bits_cnt, list(reversed(self.regs['data'].data.grouped())))
        sda_rx_data_bit_valid = bits('sda_rx_data_bit_valid', init = 0)
        with when(sda_rx_data_bit_valid):
            sda_rx_data /= cat([sda_rx_data[6:0], sda_input_sync])
        sda_wr_ack = reg_r('sda_wr_ack')
        sda_wr_ack_bit_valid = bits('sda_wr_ack_bit_valid', init = 0)
        with when(sda_wr_ack_bit_valid):
            sda_wr_ack /= sda_input_sync

        #slave scl stretch
        scl_stretch = bits('scl_stretch', init = 0)
        scl_out_reg_dly = reg_s('scl_out_reg_dly', next = scl_out_reg)
        scl_out_reg_posedge_flag = reg_r('scl_out_reg_posedge_flag')

        with when(scl_out_reg & ~scl_out_reg_dly):
            scl_out_reg_posedge_flag /= 1
        with when(~scl_out_reg & scl_out_reg_dly):
            scl_out_reg_posedge_flag /= 0

        with when(~self.regs['control'].scl_stretch_disable):
            with when(scl_out_reg_posedge_flag):
                with when(~scl_input_sync): #slave drive scl to 0
                    scl_stretch /= 1
                with other(): #clear flag, wait next scl posedge
                    scl_out_reg_posedge_flag /= 0

        scl_tick_gate = bits('scl_tick_gate', init = scl_tick)
        with when(scl_stretch):
            scl_tick_gate /= 0


        #scl sync
        scl_input_sync_posedge = bits(
            'scl_input_sync_posedge',
            init = scl_input_sync & ~scl_input_sync_dly)
        scl_input_sync_negedge = bits(
            'scl_input_sync_negedge',
            init = ~scl_input_sync & scl_input_sync_dly)
        if (self.p.multi_master_support):
            with when(self.regs['control'].multi_master):
                with when(scl_out_reg & ~state.match_any([s_idle])):
                    with when(scl_input_sync_negedge):
                        # if other master drive scl to low, 
                        #this master must sync it's scl counter 
                        # to speed up this master's scl low drive
                        scl_cnt_speed_up_next /= 1
                    with when(scl_tick_cnt == scl_max_time):
                        scl_cnt_speed_up_next /= 0
                with other():
                    scl_cnt_speed_up_next /= 0

        #i2c bus's start/stop condition capture(may be tiggerd by other master)
        bus_start = bits(
            'bus_start', 
            init = scl_input_sync & ~sda_input_sync & sda_input_sync_dly)
        bus_stop = bits(
            'bus_stop', 
            init = scl_input_sync & sda_input_sync & ~sda_input_sync_dly)
        with when(bus_stop):
            status_reg.busy /= 0
        with elsewhen(bus_start):
            status_reg.busy /= 1
        bus_start_reg = reg_r('bus_start_reg')
        with when(bus_start):
            bus_start_reg /= 1
        with when(scl_input_sync_negedge):
            bus_start_reg /= 0
        bus_stop_reg = reg_r('bus_stop_reg')
        with when(bus_stop):
            bus_stop_reg /= 1
        with when(scl_input_sync_negedge):
            bus_stop_reg /= 0

        #undefine condition check when multi master enable
        #m0: this master, m1: other master
        if (self.p.multi_master_support):
            undef_cond_m0_data_m1_start = bits('undef_cond_m0_data_m1_start', init = 0)
            undef_cond_m0_start_m1_data = bits('undef_cond_m0_start_m1_data', init = 0)
            undef_cond_m0_stop_m1_data = bits('undef_cond_m0_stop_m1_data', init = 0)
            undef_cond_m0_data_m1_stop = bits('undef_cond_m0_data_m1_stop', init = 0)
            undef_cond_m0_start_m1_stop = bits('undef_cond_m0_start_m1_stop', init = 0)
            undef_cond_m0_stop_m1_start = bits('undef_cond_m0_stop_m1_start', init = 0)
            with when(self.regs['control'].multi_master):
                with when(state.match_any([s_write, s_ack_w, s_read, s_ack_r])):
                    with when(bus_start):
                        undef_cond_m0_data_m1_start /= 1
                    with when(bus_stop):
                        undef_cond_m0_data_m1_stop /= 1
                with when(state.match_any([s_start])):
                    with when(bus_stop):
                        undef_cond_m0_start_m1_stop /= 1
                with when(state.match_any([s_stop])):
                    with when(bus_start):
                        undef_cond_m0_stop_m1_start /= 1
                with when(state.match_any([s_start])):
                    with when(scl_input_sync_negedge & scl_cnt_speed_up_next):
                        with when(~bus_start_reg):
                            undef_cond_m0_start_m1_data /= 1
                with when(state.match_any([s_stop_check])):
                    with when(
                        (scl_input_sync_negedge & scl_cnt_speed_up_next) | 
                        (sda_check & ~scl_cnt_speed_up_next)):
                        with when(~bus_stop_reg):
                            undef_cond_m0_stop_m1_data /= 1

                # cfg disable undefine condition check
                with when(~self.regs['cfg'].undef_cond_check[0]):
                    undef_cond_m0_start_m1_data /= 0
                with when(~self.regs['cfg'].undef_cond_check[1]):
                    undef_cond_m0_data_m1_start /= 0
                with when(~self.regs['cfg'].undef_cond_check[2]):
                    undef_cond_m0_stop_m1_data /= 0
                with when(~self.regs['cfg'].undef_cond_check[3]):
                    undef_cond_m0_data_m1_stop /= 0
                with when(~self.regs['cfg'].undef_cond_check[4]):
                    undef_cond_m0_start_m1_stop /= 0
                with when(~self.regs['cfg'].undef_cond_check[5]):
                    undef_cond_m0_stop_m1_start /= 0

        # arb_lost
        arb_lost = bits('arb_lost', init = 0)
        if (self.p.multi_master_support):
            with when(self.regs['control'].multi_master):
                with when((state == s_idle) & cmd_reg.start & status_reg.busy):
                    arb_lost /= 1
                with elsewhen(sda_check & sda_out_reg & ~sda_input_sync):
                    arb_lost /= 1
                with elsewhen(undef_cond_m0_data_m1_start | 
                              undef_cond_m0_start_m1_data | 
                              undef_cond_m0_stop_m1_data  | 
                              undef_cond_m0_data_m1_stop  | 
                              undef_cond_m0_start_m1_stop | 
                              undef_cond_m0_stop_m1_start):
                    arb_lost /= 1

        with when(arb_lost):
            status_reg.arb_lost /= 1
        with elsewhen(state == s_start):
            status_reg.arb_lost /= 0

        with when(arb_lost):
            state  /= s_idle
            scl_out_reg /= 1
            sda_out_reg /= 1
            scl_tick_cnt_reset_0 /= 1

            cmd_reg.start /= 0
            cmd_reg.stop /= 0
            cmd_reg.read /= 0
            cmd_reg.write /= 0
        with other():
            with when(scl_tick_gate):
                with when(state == s_idle):
                    scl_tick_cnt_add /= 1
                    with when(scl_tick_cnt == sda_hold_time):
                        sda_out_reg /= 1
                    with when(scl_tick_cnt == scl_max_time):
                        with when(cmd_reg.start):
                            state /= s_start
                        with elsewhen(cmd_reg.write):
                            scl_out_reg /= 0
                            state /= s_write
                        with elsewhen(cmd_reg.read):
                            scl_out_reg /= 0
                            state /= s_read
                        with elsewhen(cmd_reg.stop):
                            scl_out_reg /= 0
                            state /= s_stop

                with when(state == s_start):
                    scl_tick_cnt_add /= 1
                    if (self.p.multi_master_support):
                        with when(scl_tick_cnt == sda_sample_time - scl_low_time):
                            sda_check /= 1
                    with when(scl_tick_cnt == scl_low_time):
                        sda_out_reg /= 0
                    with when(scl_tick_cnt == scl_max_time):
                        scl_out_reg /= 0
                        data_bits_cnt /= 0
                        cmd_reg.start /= 0
                        with when(cmd_reg.write):
                            state /= s_write
                        with elsewhen(cmd_reg.read):
                            state /= s_read
                        with elsewhen(cmd_reg.stop):
                            state /= s_stop
                        with other():
                            state /= s_hold0

                with when(state == s_write):
                    scl_tick_cnt_add /= 1
                    with when(scl_tick_cnt == sda_hold_time):
                        sda_out_reg /= sda_tx_bit
                    with when(scl_tick_cnt == scl_low_time):
                        scl_out_reg /= 1
                    if (self.p.multi_master_support):
                        with when(scl_tick_cnt == sda_sample_time):
                            sda_check /= 1
                    with when(scl_tick_cnt == scl_max_time):
                        scl_out_reg /= 0
                        data_bits_cnt /= data_bits_cnt + 1
                        with when(data_bits_cnt == 7):
                            state /= s_ack_w
                            data_bits_cnt /= 0
                            cmd_reg.write /= 0
                        with other():
                            state /= s_write

                with when(state == s_ack_w):
                    scl_tick_cnt_add /= 1
                    with when(scl_tick_cnt == sda_hold_time):
                        sda_out_reg /= 1
                    with when(scl_tick_cnt == scl_low_time):
                        scl_out_reg /= 1
                    with when(scl_tick_cnt == sda_sample_time):
                        sda_wr_ack_bit_valid /= 1
                    with when(scl_tick_cnt == scl_max_time):
                        scl_out_reg /= 0
                        with when(cmd_reg.write):
                            state /= s_write
                        with elsewhen(cmd_reg.read):
                            state /= s_read
                        with elsewhen(cmd_reg.stop):
                            state /= s_stop
                        with other():
                            state /= s_hold0

                with when(state == s_read):
                    scl_tick_cnt_add /= 1
                    with when(scl_tick_cnt == sda_hold_time):
                        sda_out_reg /= 1
                    with when(scl_tick_cnt == scl_low_time):
                        scl_out_reg /= 1
                    with when(scl_tick_cnt == sda_sample_time):
                        sda_rx_data_bit_valid /= 1
                    with when(scl_tick_cnt == scl_max_time):
                        scl_out_reg /= 0
                        data_bits_cnt /= data_bits_cnt + 1
                        with when(data_bits_cnt == 7):
                            state /= s_ack_r
                            data_bits_cnt /= 0
                            cmd_reg.read /= 0
                        with other():
                            state /= s_read

                with when(state == s_ack_r):
                    scl_tick_cnt_add /= 1
                    with when(scl_tick_cnt == sda_hold_time):
                        sda_out_reg /= cmd_reg.ack
                    with when(scl_tick_cnt == scl_low_time):
                        scl_out_reg /= 1
                    with when(scl_tick_cnt == scl_max_time):
                        scl_out_reg /= 0
                        with when(cmd_reg.write):
                            state /= s_write
                        with elsewhen(cmd_reg.read):
                            state /= s_read
                        with elsewhen(cmd_reg.stop):
                            state /= s_stop
                        with other():
                            state /= s_hold0

                with when(state == s_hold0):
                    scl_tick_cnt_add /= 1
                    with when(scl_tick_cnt == sda_hold_time):
                        sda_out_reg /= 1
                    with when(scl_tick_cnt == scl_max_time):
                        with when(cmd_reg.start):
                            scl_out_reg /= 1
                            state /= s_start
                        with elsewhen(cmd_reg.write):
                            scl_out_reg /= 0
                            state /= s_write
                        with elsewhen(cmd_reg.read):
                            scl_out_reg /= 0
                            state /= s_read
                        with elsewhen(cmd_reg.stop):
                            scl_out_reg /= 0
                            state /= s_stop
                        with other():
                            state /= s_hold0

                with when(state == s_stop):
                    scl_tick_cnt_add /= 1
                    with when(scl_tick_cnt == sda_hold_time):
                        sda_out_reg /= 0
                    with when(scl_tick_cnt == scl_low_time):
                        scl_out_reg /= 1
                    with when(scl_tick_cnt == scl_max_time):
                        state /= s_idle
                        cmd_reg.stop /= 0
                        if (self.p.multi_master_support):
                            with when(self.regs['control'].multi_master):
                                state /= s_stop_check

                if (self.p.multi_master_support):
                    with when(state == s_stop_check):
                        scl_tick_cnt_add /= 1
                        with when(scl_tick_cnt == sda_hold_time):
                            sda_out_reg /= 1
                        if (self.p.multi_master_support):
                            with when(scl_tick_cnt == sda_sample_time):
                                sda_check /= 1
                        with when(scl_tick_cnt == scl_max_time):
                            state /= s_idle

        #io
        self.io.i2c.scl.output /= scl_out_reg
        self.io.i2c.scl.oe /= ~scl_out_reg
        self.io.i2c.sda.output /= sda_out_reg
        self.io.i2c.sda.oe /= ~sda_out_reg


        #status
        with when(cmd_write):
            status_reg.trans_progress /= 1
        with elsewhen(cmd_reg_valid):
            status_reg.trans_progress /= 1
        with elsewhen(~state.match_any([s_idle, s_hold0])):
            status_reg.trans_progress /= 1
        with other():
            status_reg.trans_progress /= 0

        status_reg.recv_ack /= sda_wr_ack


        #interrupt
        trans_progress_dly1 = reg_r(next = status_reg.trans_progress)
        ip_reg = reg_r('ip_reg')
        with when(~self.regs['ip'].valid):
            with when(ip_reg):
                self.regs['ip'].valid /= 1
                ip_reg /= 0
        with when((~status_reg.trans_progress & trans_progress_dly1) | arb_lost):
            ip_reg /= 1
        self.int_out[0] /= self.regs['ie'].en & self.regs['ip'].valid
