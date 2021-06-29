from phgl_imp import *
from .zqh_ddr_mc_parameters import *
from .zqh_ddr_mc_bundles import *
from .zqh_ddr_mc_dfi import zqh_ddr_mc_dfi
from zqh_ddr_phy.zqh_ddr_phy_bundles import zqh_ddr_phy_reg_io
from zqh_ddr_phy.zqh_ddr_phy_bundles import zqh_ddr_phy_dfi_io
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS

class zqh_ddr_mc(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_ddr_mc, self).set_par()
        self.p = zqh_ddr_mc_parameter()

    def gen_node_tree(self):
        super(zqh_ddr_mc, self).gen_node_tree()
        self.gen_node_slave(
            'ddr_mc_cfg_slave',
            bundle_p = self.p.gen_cfg_tl_bundle_p(),
            idx = 0)
        self.gen_node_slave(
            'ddr_mc_mem_slave',
            bundle_p = self.p.gen_mem_tl_bundle_p(),
            idx = 1)
        self.p.ddr_mc_cfg_slave.print_up()
        self.p.ddr_mc_cfg_slave.print_address_space()

    def set_port(self):
        super(zqh_ddr_mc, self).set_port()
        self.io.var(inp('clock_ddr'))
        self.io.var(inp('reset_ddr_mc'))
        self.io.var(zqh_ddr_phy_reg_io('phy_reg').flip())
        self.io.var(zqh_ddr_phy_dfi_io('phy_dfi').flip())

    def main(self):
        super(zqh_ddr_mc, self).main()
        self.gen_node_interface('ddr_mc_cfg_slave')
        self.gen_node_interface('ddr_mc_mem_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        #{{{
        cfg_mem_address  = bits('cfg_mem_address', w = 32, init = 0)
        cfg_mem_wr_mask  = bits('cfg_mem_wr_mask', w = 4, init = 0)
        def func_reg_write(reg_ptr, fire, address, size, wdata, mask_bit,
            wr_valid = None, wr_data = None, access_address = None, wr_mask = None,
            req_ready = None, resp_valid = None):
            with when(fire):
                wr_valid /= 1
                access_address /= address
            wr_data /= wdata
            wr_mask /= cat_rvs(map(lambda _: mask_bit[_*8], range(wr_mask.get_w())))
            return (req_ready, resp_valid)
        def func_reg_read(reg_ptr, fire, address, size, mask_bit,
            rd_valid = None, rd_data = None, access_address = None,
            req_ready = None, resp_valid = None):
            with when(fire):
                rd_valid /= 1
                access_address /= address
            return (req_ready, resp_valid, rd_data.pack())
        def wr_process_gen(wr_valid, wr_data, req_ready, resp_valid):
            return lambda a0, a1, a2, a3, a4, a5: func_reg_write(
                a0, a1, a2, a3, a4, a5,
                wr_valid, wr_data, cfg_mem_address, cfg_mem_wr_mask, req_ready, resp_valid)
        def rd_process_gen(rd_valid, rd_data, req_ready, resp_valid):
            return lambda a0, a1, a2, a3, a4: func_reg_read(
                a0, a1, a2, a3, a4,
                rd_valid, rd_data, cfg_mem_address, req_ready, resp_valid)

        #ctrl regs space: 0x0000 - 0x3fff
        ctrl_cfg_mem_wr_valid   = bits('ctrl_cfg_mem_wr_valid', init = 0)
        ctrl_cfg_mem_wr_data    = bits('ctrl_cfg_mem_wr_data', w = 32, init = 0)
        ctrl_cfg_mem_rd_valid   = bits('ctrl_cfg_mem_rd_valid', init = 0)
        ctrl_cfg_mem_rd_data    = bits('ctrl_cfg_mem_rd_data', w = 32, init = 0)
        ctrl_cfg_mem_req_ready  = bits('ctrl_cfg_mem_req_ready', init = 1)
        ctrl_cfg_mem_resp_valid = bits('ctrl_cfg_mem_resp_valid', init = 0)
        self.cfg_reg(csr_reg_group(
            'ctrl_cfg_mem',
            offset = 0x0000,
            size = 4,
            mem_size = 2**14,
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = 32,
                    write = wr_process_gen(
                        ctrl_cfg_mem_wr_valid,
                        ctrl_cfg_mem_wr_data,
                        ctrl_cfg_mem_req_ready,
                        ctrl_cfg_mem_resp_valid),
                    read = rd_process_gen(
                        ctrl_cfg_mem_rd_valid,
                        ctrl_cfg_mem_rd_data,
                        ctrl_cfg_mem_req_ready,
                        ctrl_cfg_mem_resp_valid))], comments = '''\
DDR DFI controler's configure space'''))

        #phy cfg regs space: 0x4000 - 0x7fff
        phy_cfg_mem_wr_valid = bits('phy_cfg_mem_wr_valid', init = 0)
        phy_cfg_mem_wr_data  = bits('phy_cfg_mem_wr_data', w = 32, init = 0)
        phy_cfg_mem_rd_valid = bits('phy_cfg_mem_rd_valid', init = 0)
        phy_cfg_mem_rd_data  = bits('phy_cfg_mem_rd_data', w = 32, init = 0)
        phy_cfg_mem_req_ready = bits('phy_cfg_mem_req_ready', init = 1)
        phy_cfg_mem_resp_valid = bits('phy_cfg_mem_resp_valid', init = 0)
        self.cfg_reg(csr_reg_group(
            'phy_cfg_mem',
            offset = 0x4000,
            size = 4,
            mem_size = 2**14,
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = 32,
                    write = wr_process_gen(
                        phy_cfg_mem_wr_valid,
                        phy_cfg_mem_wr_data,
                        phy_cfg_mem_req_ready,
                        phy_cfg_mem_resp_valid),
                    read = rd_process_gen(
                        phy_cfg_mem_rd_valid,
                        phy_cfg_mem_rd_data,
                        phy_cfg_mem_req_ready,
                        phy_cfg_mem_resp_valid))], comments = '''\
DDR PHY's configure space'''))

        #mc ap cfg regs space: 0x8000 - 0xffff
        self.cfg_reg(csr_reg_group('ap_cfg_address_max_l', offset = 0x8000, size = 4, fields_desc = [
            csr_reg_field_desc('addr', width = 32, reset = 0, comments = '''\
DDR memory address range's max address(low part)''')]))
        self.cfg_reg(csr_reg_group('ap_cfg_address_max_h', offset = 0x8004, size = 4, fields_desc = [
            csr_reg_field_desc('en', width = 1, reset = 0, comments = '''\
DDR MC memory access enable'''),
            csr_reg_field_desc('reserved', access = 'VOL', width = 23),
            csr_reg_field_desc('addr', width = 8, reset = 0, comments = '''\
DDR memory address range's max address(high part)''')]))
        #}}}


        ####
        #phy reg access
        phy_reg_req_fifo = async_ready_valid(
            'phy_reg_req_fifo',
            gen = type(self.io.phy_reg.req.bits),
            gen_p = self.io.phy_reg.req.bits.p)
        phy_reg_req_fifo.io.enq_clock /= self.io.clock
        phy_reg_req_fifo.io.enq_reset /= self.io.reset
        phy_reg_req_fifo.io.deq_clock /= self.io.clock_ddr
        phy_reg_req_fifo.io.deq_reset /= self.io.reset_ddr_mc
        phy_reg_req_fifo.io.enq.valid /= phy_cfg_mem_wr_valid | phy_cfg_mem_rd_valid
        phy_reg_req_fifo.io.enq.bits.write /= phy_cfg_mem_wr_valid
        phy_reg_req_fifo.io.enq.bits.addr /= cfg_mem_address
        phy_reg_req_fifo.io.enq.bits.data /= phy_cfg_mem_wr_data
        phy_reg_req_fifo.io.enq.bits.be /= cfg_mem_wr_mask
        phy_cfg_mem_req_ready /= phy_reg_req_fifo.io.enq.ready
        self.io.phy_reg.req /= phy_reg_req_fifo.io.deq

        phy_reg_resp_fifo = async_ready_valid(
            'phy_reg_resp_fifo',
            gen = type(self.io.phy_reg.resp.bits),
            gen_p = self.io.phy_reg.resp.bits.p)
        phy_reg_resp_fifo.io.enq_clock /= self.io.clock_ddr
        phy_reg_resp_fifo.io.enq_reset /= self.io.reset_ddr_mc
        phy_reg_resp_fifo.io.deq_clock /= self.io.clock
        phy_reg_resp_fifo.io.deq_reset /= self.io.reset
        phy_reg_resp_fifo.io.deq.ready /= 1
        phy_reg_resp_fifo.io.enq /= self.io.phy_reg.resp
        phy_cfg_mem_resp_valid /= phy_reg_resp_fifo.io.deq.fire()
        phy_cfg_mem_rd_data /= phy_reg_resp_fifo.io.deq.bits.data


        #phy dfi interface control
        token_bits = self.tl_in[1].a.bits.source.get_w() + self.tl_in[1].a.bits.size.get_w()
        addr_bits = self.tl_in[1].a.bits.address.get_w()
        size_bits = self.tl_in[1].a.bits.size.get_w()
        data_bits = self.tl_in[1].a.bits.data.get_w()
        dfi = zqh_ddr_mc_dfi(
            'dfi',
            addr_bits = addr_bits,
            token_bits = token_bits,
            size_bits = size_bits,
            data_bits = data_bits)
        dfi.io.clock /= self.io.clock_ddr
        dfi.io.reset /= self.io.reset_ddr_mc
        self.io.phy_dfi /= dfi.io.phy_dfi


        ####
        #ctrl reg access to dfi
        ctrl_reg_req_fifo = async_ready_valid(
            'ctrl_reg_req_fifo',
            gen = csr_reg_req,
            gen_p = dfi.io.reg.p)
        ctrl_reg_req_fifo.io.enq_clock /= self.io.clock
        ctrl_reg_req_fifo.io.enq_reset /= self.io.reset
        ctrl_reg_req_fifo.io.deq_clock /= self.io.clock_ddr
        ctrl_reg_req_fifo.io.deq_reset /= self.io.reset_ddr_mc
        ctrl_reg_req_fifo.io.enq.valid /= ctrl_cfg_mem_wr_valid | ctrl_cfg_mem_rd_valid
        ctrl_reg_req_fifo.io.enq.bits.write /= ctrl_cfg_mem_wr_valid
        ctrl_reg_req_fifo.io.enq.bits.addr /= cfg_mem_address
        ctrl_reg_req_fifo.io.enq.bits.data /= ctrl_cfg_mem_wr_data
        ctrl_reg_req_fifo.io.enq.bits.be /= cfg_mem_wr_mask
        ctrl_cfg_mem_req_ready /= ctrl_reg_req_fifo.io.enq.ready
        dfi.io.reg.req /= ctrl_reg_req_fifo.io.deq

        ctrl_reg_resp_fifo = async_ready_valid(
            'ctrl_reg_resp_fifo',
            gen = csr_reg_resp,
            gen_p = dfi.io.reg.p)
        ctrl_reg_resp_fifo.io.enq_clock /= self.io.clock_ddr
        ctrl_reg_resp_fifo.io.enq_reset /= self.io.reset_ddr_mc
        ctrl_reg_resp_fifo.io.deq_clock /= self.io.clock
        ctrl_reg_resp_fifo.io.deq_reset /= self.io.reset
        ctrl_reg_resp_fifo.io.deq.ready /= 1
        ctrl_reg_resp_fifo.io.enq /= dfi.io.reg.resp
        ctrl_cfg_mem_resp_valid /= ctrl_reg_resp_fifo.io.deq.fire()
        ctrl_cfg_mem_rd_data /= ctrl_reg_resp_fifo.io.deq.bits.data


        ####
        #ddr memory access
        sop_eop = self.tl_in[1].sop_eop_a()
        dfi_mem_req_fifo = async_queue(
            'dfi_mem_req_fifo',
            gen = lambda _: zqh_ddr_mc_mem_req(
                _,
                addr_bits = addr_bits,
                data_bits = data_bits,
                size_bits = size_bits,
                token_bits = token_bits),
            entries = self.p.req_async_fifo_depth)
        dfi_mem_req_fifo.io.enq_clock /= self.io.clock
        dfi_mem_req_fifo.io.enq_reset /= self.io.reset
        dfi_mem_req_fifo.io.deq_clock /= self.io.clock_ddr
        dfi_mem_req_fifo.io.deq_reset /= self.io.reset_ddr_mc
        dfi_mem_is_put = self.tl_in[1].a.bits.opcode.match_any([
            TMSG_CONSTS.put_full_data(), TMSG_CONSTS.put_partial_data()])
        dfi_mem_is_get =  self.tl_in[1].a.bits.opcode.match_any([TMSG_CONSTS.get()])
        dfi_mem_req_fifo.io.enq.valid /= self.tl_in[1].a.valid
        dfi_mem_req_fifo.io.enq.bits.write /= dfi_mem_is_put
        dfi_mem_req_fifo.io.enq.bits.sop /= sop_eop.sop
        dfi_mem_req_fifo.io.enq.bits.eop /= sop_eop.eop
        dfi_mem_req_fifo.io.enq.bits.size /= self.tl_in[1].a.bits.size
        dfi_mem_req_fifo.io.enq.bits.token /= cat([self.tl_in[1].a.bits.size, self.tl_in[1].a.bits.source])
        dfi_mem_req_fifo.io.enq.bits.addr /= self.tl_in[1].a.bits.address
        dfi_mem_req_fifo.io.enq.bits.data /= self.tl_in[1].a.bits.data
        #tmp dfi_mem_req_fifo.io.enq.bits.be /= self.tl_in[1].a.bits.mask
        self.tl_in[1].a.ready /= dfi_mem_req_fifo.io.enq.ready
        dfi.io.mem.req /= dfi_mem_req_fifo.io.deq

        dfi_mem_resp_fifo = async_queue(
            'dfi_mem_resp_fifo',
            gen = lambda _: zqh_ddr_mc_mem_resp(
                _,
                data_bits = data_bits,
                size_bits = size_bits,
                token_bits = token_bits),
            entries = self.p.resp_async_fifo_depth)
        dfi_mem_resp_fifo.io.enq_clock /= self.io.clock_ddr
        dfi_mem_resp_fifo.io.enq_reset /= self.io.reset_ddr_mc
        dfi_mem_resp_fifo.io.deq_clock /= self.io.clock
        dfi_mem_resp_fifo.io.deq_reset /= self.io.reset
        dfi_mem_resp_fifo.io.enq /= dfi.io.mem.resp
        get_resp = self.interface_in[1].access_ack_data(
            dfi_mem_resp_fifo.io.deq.bits.token.lsb(self.tl_in[1].a.bits.source.get_w()),
            dfi_mem_resp_fifo.io.deq.bits.token.msb(self.tl_in[1].a.bits.size.get_w()),
            dfi_mem_resp_fifo.io.deq.bits.data)
        put_resp = self.interface_in[1].access_ack(
            dfi_mem_resp_fifo.io.deq.bits.token.lsb(self.tl_in[1].a.bits.source.get_w()),
            dfi_mem_resp_fifo.io.deq.bits.token.msb(self.tl_in[1].a.bits.size.get_w()))
        self.tl_in[1].d.valid /= dfi_mem_resp_fifo.io.deq.valid
        self.tl_in[1].d.bits /= mux(
            dfi_mem_resp_fifo.io.deq.bits.write,
            put_resp,
            get_resp)
        dfi_mem_resp_fifo.io.deq.ready /= self.tl_in[1].d.ready


        ####
        #interrupt process
        self.int_out[0][0] /= dfi.io.int_flag
