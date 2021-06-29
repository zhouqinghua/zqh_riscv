import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS
from zqh_tilelink.zqh_tilelink_buffer import zqh_tl_buffer
from .zqh_print_monitor_parameters import zqh_print_monitor_parameter

class zqh_print_monitor(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_print_monitor, self).set_par()
        self.p = zqh_print_monitor_parameter('p')

    def gen_node_tree(self):
        super(zqh_print_monitor, self).gen_node_tree()
        self.gen_node_slave('print_monitor_slave', tl_type = 'tl_uh')
        self.p.print_monitor_slave.print_up()
        self.p.print_monitor_slave.print_address_space()

    def set_port(self):
        super(zqh_print_monitor, self).set_port()

    def main(self):
        super(zqh_print_monitor, self).main()
        self.gen_node_interface('print_monitor_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        req_buf = zqh_tl_buffer(
            'req_buf',
            buf_p = self.p.buf_params_in,
            tl_p = self.tl_in[0].p)
        req_buf.io.tl_in /= self.tl_in[0]
        req = req_buf.io.tl_out

        req_reg = req.a.bits.clone().as_reg()
        req_valid = req.a.valid
        req_put = req.a.bits.opcode.match_any([TMSG_CONSTS.put_full_data()])
        req_sop_eop = req.sop_eop_a()
        with when(req.a.valid):
            vassert(req.a.bits.opcode.match_any([TMSG_CONSTS.put_full_data()]))
        with when(req.a.fire()):
            vassert(req_sop_eop.sop & req_sop_eop.eop)
        resp_sop_eop = req.sop_eop_d()

        [s_ready, s_put, s_d_resp] = range(3)
        state = reg_rs('state', w = 2, rs = s_ready)
        with when(state == s_ready):
            with when(req_valid):
                with when(req_put):
                    state /= s_put
                req_reg /= req.a.bits
        with when(state == s_put):
            with when(req_sop_eop.eop):
                state /= s_d_resp
        with when(state == s_d_resp):
            with when(resp_sop_eop.eop):
                state /= s_ready
        
        
        req.a.ready /= 0
        with when(state == s_put):
            req.a.ready /= 1

        req.d.valid /= 0
        put_resp = self.interface_in[0].access_ack_a(req_reg)
        with when(state == s_d_resp):
            req.d.valid /= 1
            req.d.bits /= put_resp

        max_char_num = 100
        print_address = req_reg.address
        print_tid = print_address[19:16]
        stop_flag = vec(
            'stop_flag', 
            gen = reg_r, 
            n = 16)
        stop_code = vec(
            'stop_code', 
            gen = lambda _: reg_r(_, w = 8), 
            n = 16)
        tid_char_q = vec(
            'tid_char_q', 
            gen = lambda t: vec(
                t,
                gen = lambda _: reg_r(_, w = 8),
                n = max_char_num),
            n = 16)
        tid_char_cnt = vec(
            'tid_char_cnt',
            gen = lambda _: reg_r(_, w = 8),
            n = 16)
        print_do_valid = reg_r('print_do_valid')
        print_do_tid = reg('print_do_tid', w = 4)
        print_do_cnt = reg_r('print_do_cnt', w = 8)

        with when(print_do_valid):
            print_do_valid /= 0

        with when(state == s_put):
            with when((print_address & 0x00f0fff0) == 0x00f0ff00):
                #vprint("%c", req.a.bits.data[7:0], macro = 0)
                print_do_tid /= print_tid
                for i in range(16):
                    with when(print_tid == i):
                        tid_char_q[i](tid_char_cnt[i], req.a.bits.data[7:0])
                        with when(req.a.bits.data[7:0] == ord('\n')):
                            tid_char_cnt[i] /= 0
                            print_do_valid /= 1
                            print_do_cnt /= tid_char_cnt[i] + 1
                        with other():
                            tid_char_cnt[i] /= tid_char_cnt[i] + 1
            with when((print_address & 0x00f0fff0) == 0x00f0fff0):
                stop_flag(print_tid, 1)
                stop_code(print_tid, req.a.bits.data[7:0])
                vprint(
                    "####riscv%0d stop. return code: 'h%h####\\n",
                    (print_tid, req.a.bits.data[7:0]), macro = 0)
                #tmp vassert(req.a.bits.data[7:0] == 1, "####riscv%0d code check fail####", print_tid)

        with when(print_do_valid & ~self.io.reset):
            for i in range(16):
                with when(print_do_tid == i):
                    print_str = cat(
                        list(tid_char_q[i])) >> ((max_char_num - print_do_cnt) * 8)
                    vprint("%0s", print_str, macro = 0)
