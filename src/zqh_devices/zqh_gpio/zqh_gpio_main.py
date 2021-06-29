import sys
import os
from phgl_imp import *
from .zqh_gpio_parameters import zqh_gpio_parameter
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_gpio_bundles import *

class zqh_gpio(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_gpio, self).set_par()
        self.p = zqh_gpio_parameter()

    def gen_node_tree(self):
        super(zqh_gpio, self).gen_node_tree()
        self.gen_node_slave(
            'gpio_slave', 
            tl_type = 'tl_uh',
            bundle_p = self.p.gen_tl_bundle_p())
        self.p.gpio_slave.print_up()
        self.p.gpio_slave.print_address_space()

    def set_port(self):
        super(zqh_gpio, self).set_port()
        self.io.var(zqh_gpio_io('gpio', width = self.p.num_ports))
        self.io.var(zqh_gpio_hw_iof_io('hw_iof', width = self.p.num_ports))

    def main(self):
        super(zqh_gpio, self).main()
        self.gen_node_interface('gpio_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)
        vmacro(self.name+'_NUM_PORTS', self.p.num_ports)

        #{{{
        self.cfg_reg(csr_reg_group(
            'input_val', 
            offset = 0x000, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
pin input value'''))
        self.cfg_reg(csr_reg_group(
            'input_en', 
            offset = 0x004, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
 pin input enable'''))
        self.cfg_reg(csr_reg_group(
            'output_en', 
            offset = 0x008, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
 pin output enable'''))
        self.cfg_reg(csr_reg_group(
            'output_val', 
            offset = 0x00c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
pin output value'''))
        self.cfg_reg(csr_reg_group(
            'pue', 
            offset = 0x010, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
internal pull-up enable'''))
        self.cfg_reg(csr_reg_group(
            'ds', 
            offset = 0x014, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
Pin Drive Strength'''))
        self.cfg_reg(csr_reg_group(
            'rise_ie', 
            offset = 0x018, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
rise interrupt enable'''))
        self.cfg_reg(csr_reg_group(
            'rise_ip', 
            offset = 0x01c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', wr_action = 'ONE_TO_CLEAR', width = self.p.num_ports, reset = 0)], comments = '''\
rise interrupt pending'''))
        self.cfg_reg(csr_reg_group(
            'fall_ie', 
            offset = 0x020, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
fall interrupt enable'''))
        self.cfg_reg(csr_reg_group(
            'fall_ip', 
            offset = 0x024, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', wr_action = 'ONE_TO_CLEAR', width = self.p.num_ports, reset = 0)], comments = '''\
fall interrupt pending'''))
        self.cfg_reg(csr_reg_group(
            'high_ie', 
            offset = 0x028, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
high interrupt enable'''))
        self.cfg_reg(csr_reg_group(
            'high_ip', 
            offset = 0x02c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', wr_action = 'ONE_TO_CLEAR', width = self.p.num_ports, reset = 0)], comments = '''\
high interrupt pending'''))
        self.cfg_reg(csr_reg_group(
            'low_ie', 
            offset = 0x030, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
low interrupt enable'''))
        self.cfg_reg(csr_reg_group(
            'low_ip', 
            offset = 0x034, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', wr_action = 'ONE_TO_CLEAR', width = self.p.num_ports, reset = 0)], comments = '''\
low interrupt pending'''))
        self.cfg_reg(csr_reg_group(
            'iof_en', 
            offset = 0x038, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
HW I/O Function enable'''))
        self.cfg_reg(csr_reg_group(
            'iof_sel', 
            offset = 0x03c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
HW I/O Function select'''))
        self.cfg_reg(csr_reg_group(
            'out_xor', 
            offset = 0x040, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = self.p.num_ports, reset = 0)], comments = '''\
Output XOR (invert)'''))
        #}}}

        for i in range(self.p.num_ports):
            self.io.gpio.port[i].output /= (
                self.regs['output_val'].data[i] ^ self.regs['out_xor'].data[i])
            self.io.gpio.port[i].oe /= self.regs['output_en'].data[i]
            self.io.gpio.port[i].pue /= self.regs['pue'].data[i]
            with when(self.regs['iof_en'].data[i]):
                self.io.gpio.port[i].output /= self.io.hw_iof.port[i].output
                self.io.hw_iof.port[i].input /= self.io.gpio.port[i].input
                self.io.gpio.port[i].oe /= self.io.hw_iof.port[i].oe

        input_sync = async_dff(
            cat_rvs(map(lambda _: self.io.gpio.port[_].input, range(self.p.num_ports))),
            self.p.sync_delay)
        self.regs['input_val'].data /= input_sync & self.regs['input_en'].data

        input_rise = input_sync & ~self.regs['input_val'].data
        input_fall = ~input_sync & self.regs['input_val'].data
        input_high = input_sync & self.regs['input_val'].data
        input_low = ~input_sync & ~self.regs['input_val'].data

        for i in range(self.p.num_ints):
            with when(input_rise[i]):
                self.regs['rise_ip'].data[i] /= 1
            with when(input_fall[i]):
                self.regs['fall_ip'].data[i] /= 1
            with when(input_high[i]):
                self.regs['high_ip'].data[i] /= 1
            with when(input_low[i]):
                self.regs['low_ip'].data[i] /= 1

        for i in range(self.p.num_ints):
            self.int_out[0][i] /= (
                (self.regs['rise_ie'].data[i] & self.regs['rise_ip'].data[i]) |
                (self.regs['fall_ie'].data[i] & self.regs['fall_ip'].data[i]) |
                (self.regs['high_ie'].data[i] & self.regs['high_ip'].data[i]) |
                (self.regs['low_ie'].data[i] & self.regs['low_ip'].data[i]))
