import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_lsu_parameters import zqh_core_common_lsu_parameter
from zqh_core_common.zqh_core_common_lsu_bundles import *
from zqh_core_common.zqh_core_common_misc import D_CONSTS
from zqh_core_common.zqh_core_common_misc import M_CONSTS
from zqh_core_common.zqh_core_common_amo_alu_main import zqh_core_common_amo_alu
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_tilelink.zqh_tilelink_bundles import zqh_tl_bundle_a
from zqh_tilelink.zqh_tilelink_misc import TAMO_CONSTS
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS

class zqh_core_e1_lsu_dcache_dtim(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_e1_lsu_dcache_dtim, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def gen_node_tree(self):
        super(zqh_core_e1_lsu_dcache_dtim, self).gen_node_tree()
        self.gen_node_master(
            'lsu_master',
            size_min = 0,
            size_max = 64,
            bundle_p = self.p.gen_tl_bundle_p(),
            source_id_num = self.p.num_flights)

    def set_port(self):
        super(zqh_core_e1_lsu_dcache_dtim, self).set_port()
        self.io.var(zqh_core_common_lsu_mem_io('cpu'))
        self.io.var(zqh_core_common_lsu_errors_io('errors'))

    def main(self):
        super(zqh_core_e1_lsu_dcache_dtim, self).main()
        self.gen_node_interface('lsu_master')
        assert(self.tl_out.a.bits.data.get_w() >= self.p.core_data_bits)

        data_ecc_code = ecc_code(self.p.data_ecc)
        dtim_data_all_width = (
            ((self.p.dtim_data_bits//8)//self.p.data_ecc_bytes) * 
            data_ecc_code.width(self.p.data_ecc_bytes * 8))
        dtim_wmask_width = (self.p.dtim_data_bits//8)//self.p.data_ecc_bytes

        #stage0
        cpu_req_cmd_s0 = self.io.cpu.req.bits.cmd
        cpu_req_type_s0 = self.io.cpu.req.bits.type
        cpu_req_tag_s0 = self.io.cpu.req.bits.tag
        cpu_req_addr_s0 = self.io.cpu.req.bits.addr
        cpu_req_addr_dtim_s0 = cpu_req_addr_s0[
            cpu_req_addr_s0.get_w() - 1 : log2_ceil(self.p.dtim_data_bits // 8)]
        cpu_req_data_s0 = self.io.cpu.req.bits.data
        cpu_req_mask_s0 = mux(
            cpu_req_cmd_s0 == M_CONSTS.M_PWR(),
            self.io.cpu.req.bits.mask,
            M_CONSTS.store_mask_gen(cpu_req_type_s0, cpu_req_addr_s0, self.p.word_bytes))
        cmd_is_read_s0 = M_CONSTS.is_read(cpu_req_cmd_s0)
        cmd_is_write_s0 = M_CONSTS.is_write(cpu_req_cmd_s0)
        cmd_is_flush_s0 = cpu_req_cmd_s0.match_any([M_CONSTS.M_FLUSH_ALL()])
        cmd_need_merge_s0 = (
            (self.p.data_ecc_bytes > 1) & 
            ((cpu_req_cmd_s0 == M_CONSTS.M_PWR()) | 
                (
                    cpu_req_type_s0[D_CONSTS.SZ_MT - 2 : 0] < 
                    log2_ceil(self.p.data_ecc_bytes))))
        #no dcache, so don't support lr/sc, just do nothing and report access exception
        cmd_is_lr_sc_s0 = cpu_req_cmd_s0.match_any([M_CONSTS.M_XLR(), M_CONSTS.M_XSC()])
        cmd_is_amo_s0 = M_CONSTS.is_amo(cpu_req_cmd_s0)
        do_write_s0 = (
            cmd_is_write_s0 & 
            ~cmd_need_merge_s0 & 
            ~cmd_is_amo_s0 & 
            ~cmd_is_lr_sc_s0)
        do_read_s0 = (
            cmd_is_read_s0 | 
            (cmd_is_write_s0 & cmd_need_merge_s0)) & ~cmd_is_lr_sc_s0
        cpu_req_fire_s0 = self.io.cpu.req.fire()

        #lr sc will report exception, treated as tim hit
        #tilelink extern access always tim hit
        #fence.i's flush_all will be treated as hit dtim, but no actual read/write
        hit_dtim_s0 = bits('hit_dtim_s0', init = cmd_is_lr_sc_s0 | cmd_is_flush_s0)
        if (self.p.dtim_size != 0):
            with when(
                (cpu_req_addr_s0 >= self.p.dtim_base) &
                (cpu_req_addr_s0 < self.p.dtim_base + self.p.dtim_size)):
                hit_dtim_s0 /= 1


        #stage1
        s1_clock_en = bits('s1_clock_en', init = 1)
        ecc_error_correctable = bits('ecc_error_correctable', init = 0)
        ecc_error_uncorrectable = bits('ecc_error_uncorrectable', init = 0)
        cpu_req_bits_s1 = self.io.cpu.req.bits.clone(
            'cpu_req_bits_s1').as_reg(
                tp = 'reg_en',
                next = self.io.cpu.req.bits,
                en = s1_clock_en)
        cpu_req_valid_s1 = reg_en_r(next = cpu_req_fire_s0, en = s1_clock_en)
        hit_dtim_s1 = reg_en(next = hit_dtim_s0, en = s1_clock_en)
        cpu_req_cmd_s1 = cpu_req_bits_s1.cmd
        cpu_req_type_s1 = cpu_req_bits_s1.type
        cpu_req_tag_s1 = cpu_req_bits_s1.tag
        cpu_req_addr_s1 = cpu_req_bits_s1.addr
        cpu_req_addr_dtim_s1 = cpu_req_addr_s1[
            cpu_req_addr_s1.get_w() - 1 : log2_ceil(self.p.dtim_data_bits // 8)]
        cpu_req_mask_s1 =  reg_en(
            w = cpu_req_mask_s0.get_w(),
            next = cpu_req_mask_s0,
            en = s1_clock_en)
        cpu_req_data_s1 = cpu_req_bits_s1.data
        cmd_is_read_s1 = reg_en(next = cmd_is_read_s0, en = s1_clock_en)
        cmd_is_write_s1 = reg_en(next = cmd_is_write_s0, en = s1_clock_en)
        cmd_need_merge_s1 = reg_en(next = cmd_need_merge_s0, en = s1_clock_en)
        cmd_is_lr_sc_s1 = reg_en(next = cmd_is_lr_sc_s0, en = s1_clock_en)
        cmd_is_amo_s1 = reg_en(next = cmd_is_amo_s0, en = s1_clock_en)
        do_write_s1 = reg_en(next = do_write_s0, en = s1_clock_en)
        do_read_s1 = reg_en(next = do_read_s0, en = s1_clock_en)


        ####
        #dtim merge write FSM
        #cond 1: s0 do amo read, s1 do amo write
        #cond 2: write cmd and size < data_ecc_bytes
        #cond 3: data ecc correctable write
        (
            s_dtim_wr_merge_none, s_dtim_wr_merge_raw,
            s_dtim_wr_merge_ecc, s_dtim_wr_merge_raw_ecc) = range(4)
        dtim_rw_state = reg_rs('dtim_rw_state', w = 2, rs = s_dtim_wr_merge_none)
        with when(dtim_rw_state == s_dtim_wr_merge_none):
            with when(
                cpu_req_fire_s0 & 
                hit_dtim_s0 & 
                (cmd_is_amo_s0 | (cmd_is_write_s0 & cmd_need_merge_s0)) & 
                ~cmd_is_lr_sc_s0):
                dtim_rw_state /= s_dtim_wr_merge_raw
            with when(ecc_error_correctable):
                dtim_rw_state /= s_dtim_wr_merge_ecc
        with when(dtim_rw_state == s_dtim_wr_merge_raw):
            with when(ecc_error_correctable):
                dtim_rw_state /= s_dtim_wr_merge_raw_ecc
            with other():
                dtim_rw_state /= s_dtim_wr_merge_none
        with when(dtim_rw_state == s_dtim_wr_merge_ecc):
            dtim_rw_state /= s_dtim_wr_merge_none
        with when(dtim_rw_state == s_dtim_wr_merge_raw_ecc):
            dtim_rw_state /= s_dtim_wr_merge_none

        dtim_rw_state_is_merge = dtim_rw_state.match_any([
            s_dtim_wr_merge_raw,
            s_dtim_wr_merge_ecc,
            s_dtim_wr_merge_raw_ecc])
        dtim_rw_state_is_merge_ecc = dtim_rw_state.match_any([s_dtim_wr_merge_ecc])
        dtim_rw_state_is_merge_raw_ecc = dtim_rw_state.match_any([s_dtim_wr_merge_raw_ecc])

        with when(ecc_error_correctable):
            s1_clock_en /= 0


        ####
        #lr/sc don't support in TIM mode
        self.io.cpu.resp.bits.xcpt /= 0
        

        if (self.p.dtim_size != 0):
            vmacro('USE_DTIM')
            vmacro('DTIM_SIZE', self.p.dtim_size)
            dtim_rdata_corrected_reg = reg(
                'dtim_rdata_corrected_reg',
                w = self.p.dtim_data_bits)
            dtim_ecc_error = bits('dtim_ecc_error')
            dtim_array = reg_array(
                'dtim_array', 
                size = self.p.dtim_size // self.p.dtim_data_bytes,
                data_width = dtim_data_all_width,
                mask_width = self.p.dtim_data_bits // self.p.data_ecc_bits,
                delay = 1
                )
            dtim_ren = cpu_req_fire_s0 & hit_dtim_s0 & do_read_s0
            dtim_wen = (
                (cpu_req_fire_s0 & hit_dtim_s0 & do_write_s0) | 
                (hit_dtim_s1 & dtim_rw_state_is_merge))
            dtim_array.io.en /= dtim_ren | dtim_wen
            dtim_array.io.wmode /= dtim_wen
            data_byte_mask = mux(
                dtim_rw_state_is_merge,
                cpu_req_mask_s1,
                cpu_req_mask_s0)
            dtim_array.io.wmask /= mux(
                dtim_rw_state_is_merge_ecc | dtim_rw_state_is_merge_raw_ecc,
                value((1 << dtim_wmask_width) - 1),
                cat_rvs(map(
                    lambda _: data_byte_mask[
                        (_+1)*self.p.data_ecc_bytes - 1 : _*self.p.data_ecc_bytes].r_or(),
                    range(dtim_wmask_width))))
            dtim_array.io.addr /= mux(
                dtim_rw_state_is_merge,
                cpu_req_addr_dtim_s1,
                cpu_req_addr_dtim_s0)

            dtim_rdata_dec = list(map(
                lambda _: data_ecc_code.decode(_),
                dtim_array.io.rdata.grouped(
                    data_ecc_code.width(self.p.data_ecc_bytes * 8))))
            dtim_rdata_post_dec = mux(
                dtim_rw_state_is_merge_ecc | dtim_rw_state_is_merge_raw_ecc,
                dtim_rdata_corrected_reg,
                cat_rvs(map(lambda _ : _.pre_correct, dtim_rdata_dec)))
            dtim_rdata_corrected_reg /= cat_rvs(map(lambda _ : _.post_correct, dtim_rdata_dec))
            dtim_rdata_error = reduce(
                lambda a,b: a | b, 
                list(map(lambda _ : _.error(), dtim_rdata_dec))) & ~(
                    dtim_rw_state_is_merge_ecc | 
                    dtim_rw_state_is_merge_raw_ecc)
            dtim_rdata_error_correctable = reduce(
                lambda a,b: a | b, 
                list(map(lambda _ : _.correctable, dtim_rdata_dec))) & ~(
                    dtim_rw_state_is_merge_ecc | 
                    dtim_rw_state_is_merge_raw_ecc)
            dtim_ecc_error /= (
                (cpu_req_valid_s1 & hit_dtim_s1 & do_read_s1) & 
                dtim_rdata_error)
            ecc_error_correctable /= (
                (cpu_req_valid_s1 & hit_dtim_s1 & do_read_s1) & 
                dtim_rdata_error_correctable)
            ecc_error_uncorrectable /= (
                (cpu_req_valid_s1 & hit_dtim_s1 & do_read_s1 & dtim_rdata_error) & 
                ~dtim_rdata_error_correctable)

            merge_bit_mask = cat_rvs(map(
                lambda _: data_byte_mask[_].rep(8), 
                range(data_byte_mask.get_w())))
            if (self.p.isa_a):
                amo_in_mask = data_byte_mask
                amo_in_cmd = mux(dtim_rw_state_is_merge, cpu_req_cmd_s1, cpu_req_cmd_s0)
                amo_in_lhs = dtim_rdata_post_dec
                amo_in_rhs = mux(dtim_rw_state_is_merge, cpu_req_data_s1, cpu_req_data_s0)

                amo_alu = zqh_core_common_amo_alu('amo_alu', width = self.p.core_data_bits)
                amo_alu.io.mask /= amo_in_mask
                amo_alu.io.cmd /= amo_in_cmd
                amo_alu.io.lhs /= amo_in_lhs
                amo_alu.io.rhs /= amo_in_rhs

                dtim_wdata_pre_enc = mux(
                    cmd_is_amo_s1 | ~dtim_rw_state_is_merge_ecc,
                    self.gen_merge_raw_data(
                        dtim_rdata_post_dec,
                        amo_alu.io.out,
                        merge_bit_mask),
                    dtim_rdata_corrected_reg)
            else:
                dtim_wdata_pre_enc = mux(
                    ~dtim_rw_state_is_merge_ecc, 
                    self.gen_merge_raw_data(dtim_rdata_post_dec, 
                        mux(dtim_rw_state_is_merge, cpu_req_data_s1, cpu_req_data_s0),
                        merge_bit_mask) if (self.p.data_ecc_bytes > 1) else cpu_req_data_s0,
                    dtim_rdata_corrected_reg)
            dtim_array.io.wdata /= cat_rvs(
                map(
                    lambda _: data_ecc_code.encode(_), 
                    dtim_wdata_pre_enc.grouped(self.p.data_ecc_bytes * 8)))


        pending_flags = vec('pending_flags', gen = reg_r, n = self.p.num_flights)
        pending_full = pending_flags.pack().r_and()
        pending_none_empty = pending_flags.pack().r_or()
        pending_reqs = vec(
            'pending_reqs',
            gen = lambda _: zqh_core_common_lsu_mem_req(_).as_reg(),
            n = self.p.num_flights)
        a_source = pri_lsb_enc(~pending_flags.pack())
        with when (self.tl_out.a.fire()):
            pending_flags(a_source, 1)
            pending_reqs(a_source, self.io.cpu.req.bits)

        a_address = cpu_req_addr_s0
        a_size = cpu_req_type_s0[cpu_req_type_s0.get_w() - 2: 0]
        a_data = cpu_req_data_s0.rep(
            self.tl_out.a.bits.data.get_w() // self.p.core_data_bits)
        a_get = self.interface_out.get(a_source, a_address, a_size)[1]
        a_put = self.interface_out.put(a_source, a_address, a_size, a_data)[1]
        a_atomics = sel_map(cpu_req_cmd_s0, [
            (M_CONSTS.M_XA_SWAP() , self.interface_out.logical(
                a_source,
                a_address,
                a_size,
                a_data,
                TAMO_CONSTS.swap())[1]),
            (M_CONSTS.M_XA_XOR () , self.interface_out.logical(
                a_source,
                a_address,
                a_size,
                a_data,
                TAMO_CONSTS.xor())[1]),
            (M_CONSTS.M_XA_OR  () , self.interface_out.logical(
                a_source, 
                a_address, 
                a_size, 
                a_data, 
                TAMO_CONSTS.orr())[1]),
            (M_CONSTS.M_XA_AND () , self.interface_out.logical(
                a_source, 
                a_address, 
                a_size, 
                a_data, 
                TAMO_CONSTS.andd())[1]),
            (M_CONSTS.M_XA_ADD () , self.interface_out.arithmetic(
                a_source, 
                a_address, 
                a_size, 
                a_data, 
                TAMO_CONSTS.add())[1]),
            (M_CONSTS.M_XA_MIN () , self.interface_out.arithmetic(
                a_source,
                a_address, 
                a_size, 
                a_data, 
                TAMO_CONSTS.min())[1]),
            (M_CONSTS.M_XA_MAX () , self.interface_out.arithmetic(
                a_source, 
                a_address, 
                a_size, 
                a_data, 
                TAMO_CONSTS.max())[1]),
            (M_CONSTS.M_XA_MINU() , self.interface_out.arithmetic(
                a_source,
                a_address, 
                a_size, a_data, 
                TAMO_CONSTS.minu())[1]),
            (M_CONSTS.M_XA_MAXU() , self.interface_out.arithmetic(
                a_source,
                a_address,
                a_size, 
                a_data, 
                TAMO_CONSTS.maxu())[1])]) if (self.p.isa_a) else zqh_tl_bundle_a(
                    p = self.interface_out.bundle.channel['a'],
                    init = 0)

        internal_ready = bits('internal_ready', init = 0)
        self.tl_out.a.valid /= (
            #tmp cpu_req_fire_s0 & 
            self.io.cpu.req.valid &
            internal_ready &
            (cmd_is_read_s0 | cmd_is_write_s0) & 
            ~hit_dtim_s0 & 
            ~pending_full)
        self.tl_out.a.bits /= mux(
            ~cmd_is_write_s0, 
            a_get, 
            mux(~cmd_is_read_s0, a_put, a_atomics))

        #tilelink d response
        d_resp_buf = queue(
            'd_resp_buf',
            gen = type(self.tl_out.d.bits),
            gen_p = self.tl_out.d.bits.p,
            entries = 2)
        d_resp_buf.io.enq /= self.tl_out.d
        (d_first, d_last, d_done, d_address_inc) = self.interface_out.addr_inc(d_resp_buf.io.deq)
        d_sel = bin2oh(d_resp_buf.io.deq.bits.source, self.p.num_flights)
        d_req = sel_bin(d_resp_buf.io.deq.bits.source, pending_reqs)
        with when (d_resp_buf.io.deq.fire() & d_last):
            pending_flags(d_resp_buf.io.deq.bits.source, 0)


        #cpu's response
        self.io.cpu.resp.valid /= (
            (cpu_req_valid_s1 & hit_dtim_s1 & ~ecc_error_correctable) | 
            d_resp_buf.io.deq.fire())
        load_data_gen_in_typ  = mux(
            d_resp_buf.io.deq.fire(),
            d_req.type,
            cpu_req_type_s1) if (self.p.dtim_size != 0) else d_req.type
        load_data_gen_in_addr = mux(
            d_resp_buf.io.deq.fire(),
            d_req.addr, cpu_req_addr_s1) if (self.p.dtim_size != 0) else d_req.addr
        load_data_gen_in_data = mux(
            d_resp_buf.io.deq.fire(),
            d_resp_buf.io.deq.bits.data,
            dtim_rdata_post_dec) if (self.p.dtim_size != 0) else d_resp_buf.io.deq.bits.data
        self.io.cpu.resp.bits.data /= M_CONSTS.load_data_gen(
            load_data_gen_in_typ,
            load_data_gen_in_addr,
            load_data_gen_in_data, 
            self.p.word_bytes)
        self.io.cpu.resp.bits.data_no_shift /= load_data_gen_in_data
        self.io.cpu.resp.bits.has_data /= mux(
            d_resp_buf.io.deq.fire(),
            M_CONSTS.is_read(d_req.cmd),
            cmd_is_read_s1) if (self.p.dtim_size != 0) else M_CONSTS.is_read(d_req.cmd)
        self.io.cpu.resp.bits.tag /= mux(
            d_resp_buf.io.deq.fire(),
            d_req.tag,
            cpu_req_tag_s1) if (self.p.dtim_size != 0) else d_req.tag
        self.io.cpu.resp.bits.type /= mux(
            d_resp_buf.io.deq.fire(),
            d_req.type, 
            cpu_req_type_s1) if (self.p.dtim_size != 0) else d_req.type
        self.io.cpu.resp.bits.replay /= 0
        self.io.cpu.resp.bits.slow /= mux(
            d_resp_buf.io.deq.fire(),
            1,
            0) if (self.p.dtim_size != 0) else 1


        #no space to issue tilelink request, then don't accept cpu's req
        #tl_d response back will return response to cpu, block cpu's request
        #amo's write stage need block cpu's req one cycle
        external_ready = bits('external_ready', init = 0)
        #tmp self.io.cpu.req.ready /= 0
        #tmp with when(hit_dtim_s0):
        #tmp     with when(cmd_is_flush_s0 & self.io.cpu.busy):
        #tmp         self.io.cpu.req.ready /= 0
        #tmp     with elsewhen(~d_resp_buf.io.deq.valid):
        #tmp         self.io.cpu.req.ready /= 1
        #tmp with when(~hit_dtim_s0 & ~pending_full & self.tl_out.a.ready):
        #tmp     self.io.cpu.req.ready /= 1
        #tmp with when(hit_dtim_s1 & dtim_rw_state_is_merge):
        #tmp     self.io.cpu.req.ready /= 0
        #tmp with when(~s1_clock_en):
        #tmp     self.io.cpu.req.ready /= 0

        #tmp with when(~s1_clock_en):
        #tmp     internal_ready /= 0
        #tmp     external_ready /= 0
        #tmp with elsewhen(hit_dtim_s1 & dtim_rw_state_is_merge):
        #tmp     internal_ready /= 0
        #tmp     external_ready /= 0
        #tmp with other():
        #tmp     with when(hit_dtim_s0):
        #tmp         with when(cmd_is_flush_s0 & self.io.cpu.busy):
        #tmp             internal_ready /= 0
        #tmp         with elsewhen(~d_resp_buf.io.deq.valid):
        #tmp             internal_ready /= 1
        #tmp     with other():
        #tmp         internal_ready /= 1
        #tmp         with when(~pending_full & self.tl_out.a.ready):
        #tmp             external_ready /= 1

        with when(s1_clock_en & ~(hit_dtim_s1 & dtim_rw_state_is_merge)):
            with when(hit_dtim_s0):
                with when(~(cmd_is_flush_s0 & self.io.cpu.busy) & ~d_resp_buf.io.deq.valid):
                    internal_ready /= 1
            with other():
                internal_ready /= 1
                with when(~pending_full & self.tl_out.a.ready):
                    external_ready /= 1
        self.io.cpu.req.ready /= internal_ready & (hit_dtim_s0 | external_ready)



        self.io.cpu.busy /= pending_none_empty | cpu_req_valid_s1

        d_resp_buf.io.deq.ready /= ~(cpu_req_valid_s1 & hit_dtim_s1)

        ####
        #hpm events
        a_sop_eop = self.tl_out.sop_eop_a()
        self.io.cpu.events.refill /= (
            self.tl_out.a.fire() & 
            a_sop_eop.eop & 
            self.tl_out.a.bits.opcode.match_any([TMSG_CONSTS.get()]))
        self.io.cpu.events.write_back /= (
            self.tl_out.a.fire() & 
            a_sop_eop.eop & 
            self.tl_out.a.bits.opcode.match_any([
                TMSG_CONSTS.put_full_data(), 
                TMSG_CONSTS.put_partial_data()]))

        ####
        #error report
        self.io.errors.uncorrectable.valid /= ecc_error_uncorrectable
        self.io.errors.uncorrectable.bits /= cpu_req_addr_s1

        self.io.errors.correctable.valid /= ecc_error_correctable & ~ecc_error_uncorrectable
        self.io.errors.correctable.bits /= cpu_req_addr_s1

        self.io.errors.bus.valid /= d_resp_buf.io.deq.fire() & d_resp_buf.io.deq.bits.error
        self.io.errors.bus.bits /= d_req.addr

    def gen_merge_raw_data(self, old, new, mask):
        return (~mask & old) | (mask & new)
