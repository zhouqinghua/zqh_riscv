import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_spi_flash_xip_ctrl_parameters import *
from .zqh_spi_flash_xip_ctrl_bundles import *

class zqh_spi_flash_xip_ctrl(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_spi_flash_xip_ctrl, self).set_par()
        self.p = zqh_spi_flash_xip_ctrl_parameter()

    def gen_node_tree(self):
        super(zqh_spi_flash_xip_ctrl, self).gen_node_tree()
        self.gen_node_slave('spi_flash_slave', tl_type = 'tl_uh')
        self.p.spi_flash_slave.print_up()
        self.p.spi_flash_slave.print_address_space()

    def set_port(self):
        super(zqh_spi_flash_xip_ctrl, self).set_port()
        self.io.var(zqh_spi_flash_xip_io('spi_xip'))

    def main(self):
        super(zqh_spi_flash_xip_ctrl, self).main()
        self.gen_node_interface('spi_flash_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        a_req_reg = self.tl_in[0].a.bits.clone().as_reg()
        with when(self.tl_in[0].a.fire()):
            a_req_reg  /= self.tl_in[0].a.bits
        spi_req_len = 1 << a_req_reg.size


        (s_idle, s_req, s_resp, s_d_resp) = range(4)
        spi_state = reg_rs('spi_state', w = 3, rs = s_idle)
        spi_resp_cnt = reg_r('spi_resp_cnt', w = 8)
        d_resp_sop_eop = self.tl_in[0].sop_eop_d()

        with when(spi_state == s_idle):
            with when(self.tl_in[0].a.fire()):
                spi_state /= s_req
        with when(spi_state == s_req):
            with when(self.io.spi_xip.req.fire()):
                spi_state /= s_resp
                spi_resp_cnt /= 1
        with when(spi_state == s_resp):
            with when(self.io.spi_xip.resp.fire()):
                with when(spi_resp_cnt == spi_req_len):
                    spi_state /= s_d_resp
        with when(spi_state == s_d_resp):
            with when(self.tl_in[0].d.fire() & d_resp_sop_eop.eop):
                spi_state /= s_idle


        self.tl_in[0].a.ready /= 0
        with when(spi_state == s_idle):
            self.tl_in[0].a.ready /= 1

        self.io.spi_xip.req.valid /= 0
        self.io.spi_xip.req.bits.size /= a_req_reg.size
        self.io.spi_xip.req.bits.addr /= a_req_reg.address
        with when(spi_state == s_req):
            self.io.spi_xip.req.valid /= 1

        with when(spi_state == s_resp):
            with when(self.io.spi_xip.resp.fire()):
                spi_resp_cnt /= spi_resp_cnt + 1


        d_data_bytes = self.tl_in[0].d.bits.data.get_w()//8

        self.tl_in[0].d.valid /= 0
        d_resp_data_buf_valid = reg_r('d_resp_data_buf_valid')
        d_resp_data_buf = vec(
            'd_resp_data_buf', 
            gen = lambda _: reg(_, w = 8), 
            n = d_data_bytes)
        d_resp_bits = self.interface_in[0].access_ack_data_a(
            a_req_reg, 
            d_resp_data_buf.pack())
        self.tl_in[0].d.bits /= d_resp_bits
        self.tl_in[0].d.valid /= d_resp_data_buf_valid
        with when(spi_state == s_resp):
            with when(self.io.spi_xip.resp.fire()):
                with when(
                    (spi_resp_cnt == spi_req_len) | 
                    (spi_resp_cnt[log2_ceil(d_data_bytes) - 1 : 0] == 0)):
                    d_resp_data_buf_valid /= 1

                d_resp_data_buf(
                    (
                        spi_resp_cnt - 1 + 
                        a_req_reg.address[log2_ceil(d_data_bytes) - 1 : 0])[
                            log2_ceil(d_data_bytes) - 1 : 0],
                    self.io.spi_xip.resp.bits.data)

        with when(self.tl_in[0].d.fire()):
            d_resp_data_buf_valid /= 0

        self.io.spi_xip.resp.ready /= ~d_resp_data_buf_valid
