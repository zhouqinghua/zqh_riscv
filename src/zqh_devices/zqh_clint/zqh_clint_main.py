import sys
import os
from phgl_imp import *
from .zqh_clint_parameters import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module

class zqh_clint(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_clint, self).set_par()
        self.p = zqh_clint_parameter()

    def gen_node_tree(self):
        super(zqh_clint, self).gen_node_tree()
        self.gen_node_slave(
            'clint_slave', 
            tl_type = 'tl_uh',
            bundle_p = self.p.gen_tl_bundle_p())
        self.p.clint_slave.print_up()
        self.p.clint_slave.print_address_space()

    def set_port(self):
        super(zqh_clint, self).set_port()
        self.io.var(inp('clock_rtc'))

    def main(self):
        super(zqh_clint, self).main()
        self.gen_node_interface('clint_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        #define config regs
        msip = list(map(
            lambda _: self.cfg_reg(csr_reg_group(
                'msip_'+str(_),
                offset = _ * 4, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('msip', width = 1, reset = 0)],
                comments = 'msip for core %d' % (_))),
            range(self.p.num_cores)))
        timecmp = list(map(
            lambda _: self.cfg_reg(csr_reg_group(
                'mtimecmp_'+str(_), 
                offset = 0x4000 + _ * 8,
                size = 8, 
                fields_desc = [
                    csr_reg_field_desc('mtimecmp', width = 64, reset = 0xffffffffffffffff)],
                comments = 'timer compare register of core %d' % (_))),
            range(self.p.num_cores)))
        self.cfg_reg(csr_reg_group(
            'mtime',
            offset = 0xbff8, 
            size = 8, 
            fields_desc = [
                csr_reg_field_desc('mtime', width = 64, reset = 0)],
            comments = 'timer register'))

        #clock div by 10
        div_v = 10
        div_cnt = reg_r('div_cnt', w = 8)
        with when(div_cnt == (div_v - 1)):
            div_cnt /= 0
        with other():
            div_cnt /= div_cnt + 1
        mtime_tick = div_cnt == (div_v - 1)
        with when (mtime_tick):
            self.regs['mtime'] /= self.regs['mtime'].pack() + 1

        for i in range(self.p.num_cores):
            self.int_out[0][i*2] /= msip[i].msip
            self.int_out[0][i*2+1] /= reg_r(next = self.regs['mtime'].pack() >= timecmp[i].pack())
