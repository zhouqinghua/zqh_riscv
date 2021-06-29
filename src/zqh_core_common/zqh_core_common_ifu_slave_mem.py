import sys
import os
from phgl_imp import *
from .zqh_core_common_ifu_parameters import zqh_core_common_ifu_parameter
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_slave_io
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_core_common.zqh_core_common_misc import M_CONSTS

class zqh_core_common_ifu_slave_mem(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_common_ifu_slave_mem, self).set_par()
        self.p = zqh_core_common_ifu_parameter()

    def gen_node_tree(self):
        super(zqh_core_common_ifu_slave_mem, self).gen_node_tree()
        self.gen_node_slave('ifu_slave_mem')

        self.p.ifu_slave_mem.print_up()
        self.p.ifu_slave_mem.print_address_space()

    def set_port(self):
        super(zqh_core_common_ifu_slave_mem, self).set_port()
        self.io.var(zqh_core_common_ifu_slave_io('ifu').flip())

    def main(self):
        super(zqh_core_common_ifu_slave_mem, self).main()
        self.gen_node_interface('ifu_slave_mem')

        core_data_size = log2_ceil(self.io.ifu.req.bits.data.get_w()//8)

        req_buf = self.tl_in[0].a.bits.clone('req_buf').as_reg()

        (s_ready, s_read, s_read_rmw, s_write, s_replay, s_done) = range(6)
        state = reg_rs('state', w = 3, rs = s_ready)
        wait_resp = reg_r('wait_resp')
        access_opcode = mux(state == s_replay, req_buf.opcode, self.tl_in[0].a.bits.opcode)
        access_size = mux(state == s_replay, req_buf.size, self.tl_in[0].a.bits.size)
        access_read = access_opcode == TMSG_CONSTS.get()
        access_write = access_opcode.match_any([
            TMSG_CONSTS.put_full_data(),
            TMSG_CONSTS.put_partial_data()])
        access_direct = (
            (access_opcode == TMSG_CONSTS.get()) | 
            (
                (access_opcode == TMSG_CONSTS.put_full_data()) & 
                (access_size > (core_data_size - 1))))

        with when(self.tl_in[0].a.fire() | (state == s_replay)):
            with when(access_read):
                state /= s_read
            with elsewhen(access_write):
                with when(access_direct):
                    state /= s_write
                with other():
                    state /= s_read_rmw
        with when(state.match_any([s_read, s_write])):
            with when (self.io.ifu.resp.fire()):
                with when(~self.io.ifu.resp.bits.replay):
                    state /= s_done
                with other():
                    state /= s_replay
        with when(state == s_read_rmw):
            with when (self.io.ifu.resp.fire()):
                with when(~self.io.ifu.resp.bits.replay):
                    state /= s_write
                with other():
                    state /= s_replay
        with when(state == s_done):
            with when (self.tl_in[0].d.fire()):
                state /= s_ready 

        with when(self.io.ifu.req.fire()):
            wait_resp /= 1
        with elsewhen(self.io.ifu.resp.fire()):
            wait_resp /= 0


        with when(self.tl_in[0].a.fire()):
            req_buf /= self.tl_in[0].a.bits
        with elsewhen(self.io.ifu.resp.fire() & ~self.io.ifu.resp.bits.replay):
            with when(state == s_read_rmw):
                req_buf.data /= cat_rvs(
                    map(
                        lambda _: mux(_[0], _[1], _[2]),
                        zip(
                            req_buf.mask.grouped(1),
                            req_buf.data.grouped(8),
                            self.io.ifu.resp.bits.data.grouped(8))))
            with other():
                req_buf.data /= self.io.ifu.resp.bits.data

        self.io.ifu.req.valid /= state.match_any([
            s_read,
            s_read_rmw,
            s_write]) & ~wait_resp
        self.tl_in[0].a.ready /= state == s_ready
        self.io.ifu.req.bits.cmd /= mux(
            state.match_any([s_read, s_read_rmw]),
            M_CONSTS.M_XRD(),
            M_CONSTS.M_XWR())
        self.io.ifu.req.bits.typ /= log2_ceil(req_buf.p.data_bits//8)
        self.io.ifu.req.bits.addr /= (
            req_buf.address[self.p.itim_addr_bits - 1 : 0] | self.p.itim_base)
        self.io.ifu.req.bits.data /= req_buf.data
        self.io.ifu.req.bits.mask /= bits(init = 1).rep(req_buf.p.data_bits//8)

        self.tl_in[0].d.valid /= state == s_done
        self.tl_in[0].d.bits /= mux(
            req_buf.opcode.match_any([
                TMSG_CONSTS.put_full_data(),
                TMSG_CONSTS.put_partial_data()]),
            self.interface_in[0].access_ack_a(req_buf),
            self.interface_in[0].access_ack_data_a(req_buf, 0))
        self.tl_in[0].d.bits.data /= req_buf.data

        with when(self.tl_in[0].a.fire()):
            vassert(self.tl_in[0].a.bits.size <= core_data_size, 'size illegal')
