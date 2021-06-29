import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS
from .zqh_axi4_sram_control_parameters import zqh_axi4_sram_control_parameter

class zqh_axi4_sram_control(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_axi4_sram_control, self).set_par()
        self.p = zqh_axi4_sram_control_parameter()

    def gen_node_tree(self):
        super(zqh_axi4_sram_control, self).gen_node_tree()
        self.gen_axi4_node_slave('sram_control_slave')
        self.p.sram_control_slave.print_up()
        self.p.sram_control_slave.print_address_space()

    def set_port(self):
        super(zqh_axi4_sram_control, self).set_port()

    def main(self):
        super(zqh_axi4_sram_control, self).main()
        self.gen_axi4_node_interface('sram_control_slave')

        assert(self.axi4_in.w.bits.data.get_w() >= 32)

        req_buf_aw = queue(
            'req_buf_aw', 
            gen = type(self.axi4_in.aw.bits),
            gen_p = self.axi4_in.aw.bits.p,
            entries = self.p.buf_params_in['aw'].depth, 
            data_bypass = self.p.buf_params_in['aw'].data_bypass,
            ready_bypass = self.p.buf_params_in['aw'].ready_bypass)
        req_buf_ar = queue(
            'req_buf_ar',
            gen = type(self.axi4_in.ar.bits),
            gen_p = self.axi4_in.ar.bits.p,
            entries = self.p.buf_params_in['ar'].depth,
            data_bypass = self.p.buf_params_in['ar'].data_bypass,
            ready_bypass = self.p.buf_params_in['ar'].ready_bypass)
        req_buf_w = queue(
            'req_buf_w', 
            gen = type(self.axi4_in.w.bits), 
            gen_p = self.axi4_in.w.bits.p, 
            entries = self.p.buf_params_in['w'].depth, 
            data_bypass = self.p.buf_params_in['w'].data_bypass, 
            ready_bypass = self.p.buf_params_in['w'].ready_bypass)
        resp_buf_b = queue(
            'resp_buf_b', 
            gen = type(self.axi4_in.b.bits),
            gen_p = self.axi4_in.b.bits.p, 
            entries = self.p.buf_params_in['b'].depth, 
            data_bypass = self.p.buf_params_in['b'].data_bypass, 
            ready_bypass = self.p.buf_params_in['b'].ready_bypass)
        resp_buf_r = queue(
            'resp_buf_r', 
            gen = type(self.axi4_in.r.bits),
            gen_p = self.axi4_in.r.bits.p,
            entries = self.p.buf_params_in['r'].depth, 
            data_bypass = self.p.buf_params_in['r'].data_bypass,
            ready_bypass = self.p.buf_params_in['r'].ready_bypass)

        req_buf_aw.io.enq /= self.axi4_in.aw
        req_buf_ar.io.enq /= self.axi4_in.ar
        req_buf_w.io.enq /= self.axi4_in.w
        self.axi4_in.b /= resp_buf_b.io.deq
        self.axi4_in.r /= resp_buf_r.io.deq

        b_resp_buf_has_space = resp_buf_b.p.entries - resp_buf_b.io.count > 2
        r_resp_buf_has_space = resp_buf_r.p.entries - resp_buf_r.io.count > 2

        aw_req = req_buf_aw.io.deq
        ar_req = req_buf_ar.io.deq
        w_req = req_buf_w.io.deq
        b_resp = resp_buf_b.io.enq
        r_resp = resp_buf_r.io.enq

        (s_ready, s_get, s_put, s_resp) = range(4)
        state = reg_rs('state', w = 2, rs = s_ready)
        access_cnt = reg_r(
            'access_cnt', 
            w = max(aw_req.bits.len.get_w(), ar_req.bits.len.get_w()))
        access_cnt_max = mux(aw_req.valid, aw_req.bits.len, ar_req.bits.len)
        access_cnt_reach_max = access_cnt == access_cnt_max
        with when(state == s_ready):
            with when(aw_req.valid):
                state /= s_put
            with elsewhen(ar_req.valid):
                state /= s_get
            access_cnt /= 0
        with when(state == s_get):
            with when(r_resp_buf_has_space):
                with when(access_cnt_reach_max):
                    state /= s_resp
                with other():
                    access_cnt /= access_cnt + 1
        with when(state == s_put):
            with when(b_resp_buf_has_space):
                with when(w_req.valid):
                    with when(access_cnt_reach_max):
                        state /= s_resp
                    with other():
                        access_cnt /= access_cnt + 1
        with when(state == s_resp):
            with when(b_resp.fire() | r_resp.fire()):
                state /= s_ready

        vmacro(self.name+'_MEM_SIZE', self.p.mem_size)
        data_array = reg_array('data_array',
            size = self.p.mem_size//(self.axi4_in.w.bits.data.get_w()//8),
            data_width = (
                (self.axi4_in.w.bits.data.get_w() // self.p.data_ecc_bits) * 
                self.p.data_enc_bits),
            mask_width = self.axi4_in.w.bits.data.get_w() // self.p.data_ecc_bits)
        data_array_wen = (state == s_put) & b_resp_buf_has_space & w_req.valid
        data_array_ren = (state == s_get) & r_resp_buf_has_space
        data_array_base_addr = mux(
            aw_req.valid, 
            aw_req.bits.addr, ar_req.bits.addr) >> log2_ceil(
                self.axi4_in.w.bits.data.get_w()//8)
        data_array_addr = data_array_base_addr[
            log2_ceil(self.p.mem_size//(self.axi4_in.w.bits.data.get_w()//8)) - 1 : 0] + access_cnt
        data_array_wmask = w_req.bits.strb
        data_array_wdata = w_req.bits.data

        data_array.io.en /= data_array_wen | data_array_ren
        data_array.io.wmode /= data_array_wen
        data_array.io.addr /= data_array_addr
        data_array.io.wmask /= data_array_wmask
        data_array.io.wdata /= data_array_wdata
        data_array_rdata = data_array.io.rdata

        aw_req.ready /= 0
        ar_req.ready /= 0
        w_req.ready /= 0
        with when(state == s_get):
            with when(r_resp_buf_has_space):
                with when(access_cnt_reach_max):
                    ar_req.ready /= 1
        with when(state == s_put):
            with when(b_resp_buf_has_space):
                w_req.ready /= 1
                with when(access_cnt_reach_max):
                    aw_req.ready /= 1

        data_array_ren_s1 = reg_r(next = data_array_ren)
        data_array_wen_s1 = reg_r(next = data_array_wen)
        access_cnt_reach_max_s1 = reg(next = access_cnt_reach_max)
        req_id_s1 = reg(
            w = max(aw_req.bits.id.get_w(), ar_req.bits.id.get_w()),
            next = mux(aw_req.valid, aw_req.bits.id, ar_req.bits.id))
        aw_has_user = aw_req.bits.p.user_w is not None
        ar_has_user = ar_req.bits.p.user_w is not None
        if (aw_has_user and not ar_has_user):
            req_user_s1 = reg(w = aw_req.bits.user.get_w(), next = aw_req.bits.user)
        elif (not aw_has_user and ar_has_user):
            req_user_s1 = reg(w = ar_req.bits.user.get_w(), next = ar_req.bits.user)
        elif (aw_has_user and ar_has_user):
            req_user_s1 = reg(
                w = max(ar_req.bits.user.get_w(), aw_req.bits.user.get_w()),
                next = mux(aw_req.valid, aw_req.bits.user, ar_req.bits.user))
        
        b_resp.valid /= 0
        r_resp.valid /= 0
        with when(data_array_ren_s1):
            r_resp.valid /= 1
        r_resp.bits.id /= req_id_s1
        r_resp.bits.data /= data_array_rdata
        r_resp.bits.resp /= 0
        r_resp.bits.last /= access_cnt_reach_max_s1
        if (ar_has_user):
            r_resp.bits.user /= req_user_s1

        with when(data_array_wen_s1 & access_cnt_reach_max_s1):
            b_resp.valid /= 1
        b_resp.bits.id /= req_id_s1
        b_resp.bits.resp /= 0
        if (aw_has_user):
            b_resp.bits.user /= req_user_s1
