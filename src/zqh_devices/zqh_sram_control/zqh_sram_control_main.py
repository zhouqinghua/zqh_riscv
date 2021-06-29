import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS
from .zqh_sram_control_parameters import zqh_sram_control_parameter

class zqh_sram_control(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_sram_control, self).set_par()
        self.p = zqh_sram_control_parameter('p')

    def gen_node_tree(self):
        super(zqh_sram_control, self).gen_node_tree()
        self.gen_node_slave('sram_control_slave', tl_type = 'tl_uh')
        self.p.sram_control_slave.print_up()
        self.p.sram_control_slave.print_address_space()

    def set_port(self):
        super(zqh_sram_control, self).set_port()

    def main(self):
        super(zqh_sram_control, self).main()
        self.gen_node_interface('sram_control_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        req_buf_a = queue(
            'req_buf_a', 
            gen = type(self.tl_in[0].a.bits), 
            gen_p = self.tl_in[0].p.channel['a'], 
            entries = self.p.req_buf_entries)
        resp_buf_d = queue(
            'resp_buf_d', 
            gen = type(self.tl_in[0].d.bits), 
            gen_p = self.tl_in[0].p.channel['d'], 
            entries = self.p.resp_buf_entries)

        req_buf_a.io.enq /= self.tl_in[0].a
        self.tl_in[0].d /= resp_buf_d.io.deq

        resp_buf_has_space = resp_buf_d.p.entries - resp_buf_d.io.count > 2

        req = req_buf_a.io.deq
        resp = resp_buf_d.io.enq

        req_is_get = req.bits.opcode.match_any([TMSG_CONSTS.get()])
        req_is_put = req.bits.opcode.match_any([
            TMSG_CONSTS.put_full_data(),
            TMSG_CONSTS.put_partial_data()])

        
        (s_ready, s_get, s_put, s_resp) = range(4)
        state = reg_rs('state', w = 2, rs = s_ready)
        no_burst = req.bits.size < (log2_ceil(self.tl_in[0].a.bits.p.data_bits//8) + 1)
        access_cnt = reg_r('access_cnt', w = 8)
        access_cnt_max = mux(
            no_burst,
            0,
            (1 << (req.bits.size - log2_ceil(self.tl_in[0].a.bits.p.data_bits//8))) - 1)
        access_cnt_reach_max = access_cnt == access_cnt_max
        with when(state == s_ready):
            with when(req.valid):
                with when(req_is_get):
                    state /= s_get
                with when(req_is_put):
                    state /= s_put
                access_cnt /= 0
        with when(state == s_get):
            with when(resp_buf_has_space):
                with when(access_cnt_reach_max):
                    state /= s_resp
                with other():
                    access_cnt /= access_cnt + 1
        with when(state == s_put):
            with when(resp_buf_has_space):
                with when(req.valid):
                    with when(access_cnt_reach_max):
                        state /= s_resp
                    with other():
                        access_cnt /= access_cnt + 1
        with when(state == s_resp):
            with when(resp.fire()):
                state /= s_ready

        vmacro(self.name+'_MEM_SIZE', self.p.mem_size)
        data_array = reg_array('data_array',
            size = self.p.mem_size//(self.tl_in[0].a.bits.p.data_bits//8),
            data_width = (
                (self.tl_in[0].a.bits.p.data_bits // self.p.data_ecc_bits) * 
                self.p.data_enc_bits),
            mask_width = self.tl_in[0].a.bits.p.data_bits // self.p.data_ecc_bits)
        data_array_wen = (state == s_put) & resp_buf_has_space & req.valid
        data_array_ren = (state == s_get) & resp_buf_has_space
        data_array_base_addr = (
            req.bits.address >> log2_ceil(self.tl_in[0].a.bits.p.data_bits//8))
        data_array_addr = (
            data_array_base_addr[
                log2_ceil(self.p.mem_size//(self.tl_in[0].a.bits.p.data_bits//8)) - 1 : 0] + 
            access_cnt)
        data_array_wmask = req.bits.mask
        data_array_wdata = req.bits.data

        data_array.io.en /= data_array_wen | data_array_ren
        data_array.io.wmode /= data_array_wen
        data_array.io.addr /= data_array_addr
        data_array.io.wmask /= data_array_wmask
        data_array.io.wdata /= data_array_wdata
        data_array_rdata = data_array.io.rdata

        req.ready /= 0
        with when(state == s_get):
            with when(resp_buf_has_space):
                with when(access_cnt_reach_max):
                    req.ready /= 1
        with when(state == s_put):
            with when(resp_buf_has_space):
                req.ready /= 1

        data_array_ren_s1 = reg_r(next = data_array_ren)
        data_array_wen_s1 = reg_r(next = data_array_wen)
        access_cnt_reach_max_s1 = reg(next = access_cnt_reach_max)
        req_source_s1 = reg(w = req.bits.source.get_w(), next = req.bits.source)
        req_size_s1 = reg(w = req.bits.size.get_w(), next = req.bits.size)
        resp.valid /= 0
        get_resp = self.interface_in[0].access_ack_data(
            req_source_s1,
            req_size_s1,
            data_array_rdata)
        put_resp = self.interface_in[0].access_ack(
            req_source_s1,
            req_size_s1)
        with when(data_array_ren_s1):
            resp.valid /= 1
            resp.bits /= get_resp
        with when(data_array_wen_s1 & access_cnt_reach_max_s1):
            resp.valid /= 1
            resp.bits /= put_resp
