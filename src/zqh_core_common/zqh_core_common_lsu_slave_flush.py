import sys
import os
from phgl_imp import *
from .zqh_core_common_lsu_parameters import zqh_core_common_lsu_parameter
from .zqh_core_common_lsu_bundles import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_core_common_misc import M_CONSTS

class zqh_core_common_lsu_slave_flush(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_common_lsu_slave_flush, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def gen_node_tree(self):
        super(zqh_core_common_lsu_slave_flush, self).gen_node_tree()
        self.gen_node_slave('lsu_slave_flush')
        self.p.lsu_slave_flush.print_up()
        self.p.lsu_slave_flush.print_address_space()

    def set_port(self):
        super(zqh_core_common_lsu_slave_flush, self).set_port()
        self.io.var(zqh_core_common_lsu_mem_io('lsu').flip())

    def main(self):
        super(zqh_core_common_lsu_slave_flush, self).main()
        self.gen_node_interface('lsu_slave_flush')

        #define config regs
        flush_write_flag = reg_r('flush_write_flag')
        def func_flush_write(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata
                tmp = flush_write_flag
                tmp /= 1
            return (1, 1)
        def func_flush_read(reg_ptr, fire, address, size, mask_bit):
            return (1, 1, ~flush_write_flag)
        flush = self.cfg_reg(csr_reg_group(
            'flush',
            offset = 0x0000,
            size = 4,
            fields_desc = [csr_reg_field_desc('data', width = 32, write = func_flush_write, read = func_flush_read)]))


        lsu_resp_fire = self.io.lsu.resp.fire()
        lsu_resp_fire_accept = lsu_resp_fire & ~self.io.lsu.resp.bits.replay
        lsu_resp_fire_replay = lsu_resp_fire & self.io.lsu.resp.bits.replay


        (s_ready, s_req, s_wait_resp) = range(3)
        state = reg_rs('state', w = 2, rs = s_ready)

        with when(state == s_ready):
            with when (flush_write_flag):
                state /= s_req
        with when(state == s_req):
            with when(self.io.lsu.req.fire()):
                state /= s_wait_resp
        with when(state == s_wait_resp):
            with when (lsu_resp_fire_accept):
                state /= s_ready
                flush_write_flag /= 0
            with when(lsu_resp_fire_replay):
                state /= s_req

        self.io.lsu.req.valid /= state == s_req
        self.io.lsu.req.bits.cmd /= M_CONSTS.M_FLUSH_ALL()
        self.io.lsu.req.bits.type /= D_CONSTS.MT_H()
        self.io.lsu.req.bits.tag /= 0
        self.io.lsu.req.bits.addr /= self.regs['flush'].data
        self.io.lsu.req.bits.error /= 0
        self.io.lsu.req.bits.data /= 0
        self.io.lsu.req.bits.mask /= 0
        self.io.lsu.s1_kill /= 0
        self.io.lsu.s1_data.data /= 0
        self.io.lsu.s1_data.mask /= 0
