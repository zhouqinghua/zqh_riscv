import sys
import os
from phgl_imp import *
from .zqh_core_common_lsu_parameters import zqh_core_common_lsu_parameter
from .zqh_core_common_lsu_bundles import *
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_core_common_misc import M_CONSTS

class zqh_core_common_lsu_slave_mem(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_common_lsu_slave_mem, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def gen_node_tree(self):
        super(zqh_core_common_lsu_slave_mem, self).gen_node_tree()
        self.gen_node_slave('lsu_slave_mem')
        self.p.lsu_slave_mem.print_up()
        self.p.lsu_slave_mem.print_address_space()

    def set_port(self):
        super(zqh_core_common_lsu_slave_mem, self).set_port()
        self.io.var(zqh_core_common_lsu_mem_io('lsu').flip())

    def main(self):
        super(zqh_core_common_lsu_slave_mem, self).main()
        self.gen_node_interface('lsu_slave_mem')

        core_data_size = log2_ceil(self.io.lsu.req.bits.data.get_w()//8)
        data_split = self.tl_in[0].a.bits.data.get_w()//self.io.lsu.req.bits.data.get_w()
        address_split_l = log2_ceil(self.io.lsu.req.bits.data.get_w()//8)
        address_split_h = log2_ceil(self.tl_in[0].a.bits.data.get_w()//8) - 1

        tl_req = self.tl_in[0].a.bits.clone('tl_req').as_reg()

        lsu_resp_fire = self.io.lsu.resp.fire()
        lsu_resp_fire_accept = lsu_resp_fire & ~self.io.lsu.resp.bits.replay
        lsu_resp_fire_replay = lsu_resp_fire & self.io.lsu.resp.bits.replay

        with when (lsu_resp_fire_accept):
            tl_req.data /= self.io.lsu.resp.bits.data_no_shift
        with when (self.tl_in[0].a.fire()):
            tl_req /= self.tl_in[0].a.bits


        (s_ready, s_wait, s_replay, s_grant) = range(4)
        state = reg_rs('state', w = 2, rs = s_ready)
        with when (lsu_resp_fire_accept):
            state /= s_grant
        with when (self.tl_in[0].d.fire()):
            state /= s_ready 
        with when (lsu_resp_fire_replay):
            state /= s_replay
        with when (self.io.lsu.req.fire()):
            state /= s_wait

        ready = (state == s_ready) | self.tl_in[0].d.fire()
        self.tl_in[0].a.ready /= self.io.lsu.req.ready & ready

        a_req = mux(state == s_replay, tl_req, self.tl_in[0].a.bits)
        self.io.lsu.req.valid /= (self.tl_in[0].a.valid & ready) | (state == s_replay)
        self.io.lsu.req.bits.cmd /= sel_map(a_req.opcode, [
            (TMSG_CONSTS.put_full_data    (), M_CONSTS.M_XWR()),
            (TMSG_CONSTS.put_partial_data (), M_CONSTS.M_PWR()),
            (TMSG_CONSTS.get            (), M_CONSTS.M_XRD())])
        self.io.lsu.req.bits.type /= a_req.size
        self.io.lsu.req.bits.tag /= 0
        self.io.lsu.req.bits.addr /= (
            a_req.address[self.p.dtim_addr_bits - 1 : 0] | 
            self.p.dtim_base)
        self.io.lsu.req.bits.error /= 0
        self.io.lsu.req.bits.data /= sel_bin(
            a_req.address[address_split_h:address_split_l],
            a_req.data.grouped(self.io.lsu.req.bits.data.get_w()))
        self.io.lsu.req.bits.mask /= sel_bin(
            a_req.address[address_split_h:address_split_l],
            a_req.mask.grouped(self.io.lsu.req.bits.data.get_w()//8))
        self.io.lsu.s1_kill /= 0

        self.tl_in[0].d.valid /= lsu_resp_fire_accept | (state == s_grant)
        self.tl_in[0].d.bits /= mux(
            tl_req.opcode.match_any([
                TMSG_CONSTS.put_full_data(),
                TMSG_CONSTS.put_partial_data()]),
            self.interface_in[0].access_ack_a(tl_req),
            self.interface_in[0].access_ack_data_a(tl_req, 0))
        self.tl_in[0].d.bits.data /= mux(
            lsu_resp_fire_accept,
            self.io.lsu.resp.bits.data_no_shift,
            tl_req.data)

        with when(self.tl_in[0].a.fire()):
            vassert(self.tl_in[0].a.bits.size <= core_data_size, 'size illegal')
