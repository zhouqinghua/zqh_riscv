from phgl_imp import *
from .zqh_crg_ctrl_parameters import zqh_crg_ctrl_parameter
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_crg_ctrl_bundles import *

class zqh_crg_ctrl(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_crg_ctrl, self).set_par()
        self.p = zqh_crg_ctrl_parameter()

    def gen_node_tree(self):
        super(zqh_crg_ctrl, self).gen_node_tree()
        self.gen_node_slave(
            'crg_ctrl_slave',
            tl_type = 'tl_uh', 
            bundle_p = self.p.gen_tl_bundle_p())
        self.p.crg_ctrl_slave.print_up()
        self.p.crg_ctrl_slave.print_address_space()

    def set_port(self):
        super(zqh_crg_ctrl, self).set_port()
        self.io.var(inp('clock_ref'))
        self.io.var(inp('reset_por'))
        self.io.var(zqh_crg_ctrl_cfg_io('cfg'))

    def main(self):
        super(zqh_crg_ctrl, self).main()
        self.gen_node_interface('crg_ctrl_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        clock_ref_offset = 0x00
        core_pll_offset = 0x04
        eth_pll_offset = 0x08
        ddr_pll_offset = 0x0c
        reset_offsest = 0x10

        #{{{
        crg_cfg_mem_wr_valid = bits('crg_cfg_mem_wr_valid', init = 0)
        crg_cfg_mem_wr_data  = bits('crg_cfg_mem_wr_data', w = 32, init = 0)
        crg_cfg_mem_rd_valid = bits('crg_cfg_mem_rd_valid', init = 0)
        crg_cfg_mem_rd_data  = bits('crg_cfg_mem_rd_data', w = 32, init = 0)
        crg_cfg_mem_address  = bits('crg_cfg_mem_address', w = 32, init = 0)

        req_ready = bits('req_ready', init = 1)
        wr_resp_valid = bits('wr_resp_valid', init = 0)
        rd_resp_valid = bits('rd_resp_valid', init = 0)
        def func_reg_write(reg_ptr, fire, address, size, wdata, mask_bit,
            wr_valid = None, wr_data = None, access_address = None):
            with when(fire):
                wr_valid /= 1
                access_address /= address
            wr_data /= wdata
            return (req_ready, wr_resp_valid)
        def func_reg_read(reg_ptr, fire, address, size, mask_bit,
            rd_valid = None, rd_data = None, access_address = None):
            with when(fire):
                rd_valid /= 1
                access_address /= address
            return (req_ready, rd_resp_valid, rd_data.pack())
        def wr_process_gen(wr_valid, wr_data):
            return lambda a0, a1, a2, a3, a4, a5: func_reg_write(
                a0, a1, a2, a3, a4, a5, wr_valid, wr_data, crg_cfg_mem_address)
        def rd_process_gen(rd_valid, rd_data):
            return lambda a0, a1, a2, a3, a4: func_reg_read(
                a0, a1, a2, a3, a4, rd_valid, rd_data, crg_cfg_mem_address)
        self.cfg_reg(csr_reg_group(
            'crg_cfg_mem', 
            offset = 0x000, 
            size = 4, 
            mem_size = 2**12, 
            fields_desc = [
                csr_reg_field_desc(
                    'data', access = 'VOL', width = 32,
                    write = wr_process_gen(crg_cfg_mem_wr_valid, crg_cfg_mem_wr_data),
                    read = rd_process_gen(crg_cfg_mem_rd_valid, crg_cfg_mem_rd_data))]))
        #}}}


        #tile clock domain -> clock_ref domian sync
        req_sync = async_ready_valid('req_sync',
            gen = lambda _: bits(_, w = 41)) #[wr_rd_flag, address, data]
        req_sync.io.enq_clock /= self.io.clock
        req_sync.io.enq_reset /= self.io.reset
        req_sync.io.deq_clock /= self.io.clock_ref
        req_sync.io.deq_reset /= self.io.reset_por
        req_sync.io.deq.ready /= 1

        #clock_ref domian -> tile clock domain sync
        resp_sync = async_ready_valid('resp_sync',
            gen = lambda _: bits(_, w = 33)) #[wr_rd_flag, data]
        resp_sync.io.enq_clock /= self.io.clock_ref
        resp_sync.io.enq_reset /= self.io.reset_por
        resp_sync.io.deq_clock /= self.io.clock
        resp_sync.io.deq_reset /= self.io.reset
        resp_sync.io.deq.ready /= 1


        #
        #tile clock domain action
        #{{{
        #request
        req_sync.io.enq.valid /= crg_cfg_mem_wr_valid | crg_cfg_mem_rd_valid
        req_sync.io.enq.bits /= cat([
            crg_cfg_mem_wr_valid,
            crg_cfg_mem_address[7:0],
            crg_cfg_mem_wr_data])
        req_ready /= req_sync.io.enq.ready

        #response
        crg_cfg_mem_rd_data /= resp_sync.io.deq.bits[31:0]
        wr_resp_valid /= resp_sync.io.deq.fire() & resp_sync.io.deq.bits[32]
        rd_resp_valid /= resp_sync.io.deq.fire() & ~resp_sync.io.deq.bits[32]
        #}}}


        #
        #clock_ref domain action
        #{{{
        clock_ref_cfg_reg = reg_r(
            'clock_ref_cfg_reg',
            w = 32,
            clock = self.io.clock_ref,
            reset = self.io.reset_por)

        core_pll_cfg_reg = zqh_crg_ctrl_core_pll_cfg('core_pll_cfg_reg').as_reg(
            tp = 'reg_rs',
            clock = self.io.clock_ref,
            reset = self.io.reset_por)
        core_pll_cfg_reg.div_r.rs_vl = value(1, w = 8)
        core_pll_cfg_reg.mul.rs_vl = value(1, w = 8)
        core_pll_cfg_reg.div_q.rs_vl = value(1, w = 8)
        core_pll_cfg_reg.bypass.rs_vl = value(1, w = 1)
        core_pll_lock_reg = reg_r(
            'core_pll_lock_reg',
            clock = self.io.clock_ref, 
            reset = self.io.reset_por)

        eth_pll_cfg_reg = zqh_crg_ctrl_eth_pll_cfg('eth_pll_cfg_reg').as_reg(
            tp = 'reg_rs',
            clock = self.io.clock_ref,
            reset = self.io.reset_por)
        eth_pll_cfg_reg.div_r.rs_vl = value(1, w = 8)
        eth_pll_cfg_reg.mul.rs_vl = value(1, w = 8)
        eth_pll_cfg_reg.div_q.rs_vl = value(1, w = 8)
        eth_pll_cfg_reg.bypass.rs_vl = value(1, w = 1)
        eth_pll_cfg_reg.en.rs_vl = value(1, w = 1)
        eth_pll_lock_reg = reg_r(
            'eth_pll_lock_reg', 
            clock = self.io.clock_ref,
            reset = self.io.reset_por)

        ddr_pll_cfg_reg = zqh_crg_ctrl_ddr_pll_cfg('ddr_pll_cfg_reg').as_reg(
            tp = 'reg_rs',
            clock = self.io.clock_ref,
            reset = self.io.reset_por)
        ddr_pll_cfg_reg.div_r.rs_vl = value(1, w = 8)
        ddr_pll_cfg_reg.mul.rs_vl = value(1, w = 8)
        ddr_pll_cfg_reg.div_q.rs_vl = value(1, w = 8)
        ddr_pll_cfg_reg.bypass.rs_vl = value(1, w = 1)
        ddr_pll_cfg_reg.en.rs_vl = value(1, w = 1)
        ddr_pll_lock_reg = reg_r(
            'ddr_pll_lock_reg', 
            clock = self.io.clock_ref,
            reset = self.io.reset_por)

        reset_cfg_reg = zqh_crg_ctrl_reset_cfg('reset_cfg_reg').as_reg(
            tp = 'reg_r',
            clock = self.io.clock_ref,
            reset = self.io.reset_por)

        crg_cfg_mem_reg_wr_flag = reg_r(
            'crg_cfg_mem_reg_wr_flag', 
            clock = self.io.clock_ref, 
            reset = self.io.reset_por)
        crg_cfg_mem_reg_rd_flag = reg_r(
            'crg_cfg_mem_reg_rd_flag', 
            clock = self.io.clock_ref, 
            reset = self.io.reset_por)
        crg_cfg_mem_reg_address = reg(
            'crg_cfg_mem_reg_address', 
            w = 8, 
            clock = self.io.clock_ref, 
            reset = self.io.reset_por)

        with when(req_sync.io.deq.fire()):
            address = req_sync.io.deq.bits[39:32]
            is_wr = req_sync.io.deq.bits[40]
            crg_cfg_mem_reg_wr_flag /= is_wr
            crg_cfg_mem_reg_rd_flag /= ~is_wr
            crg_cfg_mem_reg_address /= address
            with when(is_wr):
                with when(address == clock_ref_offset):
                    clock_ref_cfg_reg /= req_sync.io.deq.bits[31:0]
                with when(address == core_pll_offset):
                    core_pll_cfg_reg /= req_sync.io.deq.bits[31:0]
                with when(address == eth_pll_offset):
                    eth_pll_cfg_reg /= req_sync.io.deq.bits[31:0]
                with when(address == ddr_pll_offset):
                    ddr_pll_cfg_reg /= req_sync.io.deq.bits[31:0]
                with when(address == reset_offsest):
                    reset_cfg_reg /= req_sync.io.deq.bits[31:0]

        resp_sync.io.enq.valid /= crg_cfg_mem_reg_wr_flag | crg_cfg_mem_reg_rd_flag
        resp_sync.io.enq.bits /= cat([
            crg_cfg_mem_reg_wr_flag,
            sel_map(
                crg_cfg_mem_reg_address,
                [
                    (clock_ref_offset, clock_ref_cfg_reg.pack().u_ext(32)),
                    (
                        core_pll_offset,
                        cat([core_pll_lock_reg, core_pll_cfg_reg.pack().u_ext(31)])),
                    (
                        eth_pll_offset,
                        cat([eth_pll_lock_reg, eth_pll_cfg_reg.pack().u_ext(31)])),
                    (
                        ddr_pll_offset, 
                        cat([ddr_pll_lock_reg, ddr_pll_cfg_reg.pack().u_ext(31)])),
                    (reset_offsest, reset_cfg_reg.pack().u_ext(32))])])

        with when(resp_sync.io.enq.fire()):
            crg_cfg_mem_reg_wr_flag /= 0
            crg_cfg_mem_reg_rd_flag /= 0
        #}}}


        self.io.cfg.clock_ref_cfg /= clock_ref_cfg_reg
        self.io.cfg.core_pll_cfg /= core_pll_cfg_reg
        self.io.cfg.eth_pll_cfg /= eth_pll_cfg_reg
        self.io.cfg.ddr_pll_cfg /= ddr_pll_cfg_reg
        self.io.cfg.reset_cfg /= reset_cfg_reg
        core_pll_lock_reg /= self.io.cfg.core_pll_lock
        eth_pll_lock_reg /= self.io.cfg.eth_pll_lock
        ddr_pll_lock_reg /= self.io.cfg.ddr_pll_lock
