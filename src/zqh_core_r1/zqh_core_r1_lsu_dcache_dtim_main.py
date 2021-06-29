import sys
import os
from phgl_imp import *
from .zqh_core_r1_lsu_parameters import *
from .zqh_core_r1_lsu_bundles import *
from zqh_core_common.zqh_core_common_lsu_parameters import zqh_core_common_lsu_parameter
from zqh_core_common.zqh_core_common_lsu_bundles import *
from zqh_tilelink.zqh_tilelink_bundles import zqh_tl_bundle_a
from zqh_tilelink.zqh_tilelink_misc import TAMO_CONSTS
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS
from zqh_tilelink.zqh_tilelink_meta_data import zqh_client_metadata
from zqh_tilelink.zqh_tilelink_meta_data import zqh_client_states
from zqh_core_common.zqh_core_common_amo_alu_main import zqh_core_common_amo_alu
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_core_common.zqh_core_common_misc import D_CONSTS
from zqh_core_common.zqh_core_common_misc import M_CONSTS
from zqh_common.zqh_replacement import zqh_random_replacement

class zqh_core_r1_lsu_dcache_dtim(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_r1_lsu_dcache_dtim, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def gen_node_tree(self):
        super(zqh_core_r1_lsu_dcache_dtim, self).gen_node_tree()
        self.gen_node_master(
            'dcache_master',
            size_min = 0,
            size_max = 64,
            bundle_p = self.p.gen_tl_bundle_p(),
            source_id_num = self.p.num_flights)

    def set_port(self):
        super(zqh_core_r1_lsu_dcache_dtim, self).set_port()
        self.io.var(zqh_core_common_lsu_mem_io('cpu'))
        self.io.var(zqh_core_common_lsu_errors_io('errors'))
        self.io.var(zqh_core_common_lsu_mem_io('slave'))

    def main(self):
        super(zqh_core_r1_lsu_dcache_dtim, self).main()
        self.gen_node_interface('dcache_master')
        assert(self.tl_out.a.bits.data.get_w() >= self.p.core_data_bits)

        self.tag_ecc = self.p.tag_code()
        self.data_ecc = self.p.data_code()
        using_rmw = self.p.data_ecc_bytes > 1 or self.p.isa_a
      
        replacer = zqh_random_replacement(ways = self.p.num_ways)

        #refill and writeback tl_a request's arbitration
        tl_arb = sp_arbiter('tl_arb', gen = type(self.tl_out.a.bits), gen_p = self.tl_out.a.bits.p, n = 2)
        self.tl_out.a /= tl_arb.io.out

        #tag_array access's arbitration
        meta_arb = sp_arbiter(
            'meta_arb',
            gen = zqh_core_r1_lsu_dcache_metadata_req,
            n = 8)
        meta_arb.io.out.ready /= 1
        tag_array = reg_array(
            'tag_array',
            o_reg = 1,
            size = self.p.num_sets,
            data_width = self.p.num_ways * self.tag_ecc.width(
                meta_arb.io.out.bits.data.get_w()),
            mask_width = self.p.num_ways)
        tag_array.io.en /= meta_arb.io.out.fire()
        tag_array.io.wmode /= meta_arb.io.out.bits.write
        tag_array.io.addr /= meta_arb.io.out.bits.addr[
            self.p.untag_bits-1: self.p.block_off_bits]
        tag_array.io.wmask /= cat_rvs(meta_arb.io.out.bits.way_en.grouped())
        tag_array.io.wdata /= self.tag_ecc.encode(
            meta_arb.io.out.bits.data.pack()).rep(self.p.num_ways)

        #data_array access's arbitration
        data_arb = sp_arbiter(
            'data_arb',
            gen = lambda _: zqh_core_r1_lsu_dcache_data_req(_, row_bytes = self.row_bytes()),
            n = 4)
        data_arb.io.out.ready /= 1


        #####
        #data_array access
        data_arrays = list(map(
            lambda _: reg_array(
                'data_arrays_'+str(_),
                o_reg = 1,
                size = self.p.num_sets * self.cache_block_beats(),
                data_width = (
                    self.p.num_ways * 
                    (self.p.word_bits // self.p.data_ecc_bits) * 
                    self.p.data_enc_bits),
                mask_width = self.p.num_ways * (self.p.word_bits // self.p.data_ecc_bits)),
            range(self.row_bytes() // self.p.word_bytes)))
        data_array_wmask = flatten(list(map(
            lambda i: list(map(
                lambda _: _ & data_arb.io.out.bits.way_en[i],
                data_arb.io.out.bits.eccMask.grouped())),
            range(self.p.num_ways))))
        data_array_wwords = self.encode_data(
            data_arb.io.out.bits.wdata[self.row_bits()-1: 0],
            data_arb.io.out.bits.poison).grouped(
                self.p.data_enc_bits * (self.p.word_bits // self.p.data_ecc_bits))
        data_array_access_en = data_arb.io.out.valid & (data_arb.io.out.bits.way_en != 0)
        for (array, i) in list(zip(data_arrays, range(len(data_arrays)))):
            data_array_valid = data_array_access_en & data_arb.io.out.bits.wordMask[i]
            data_array_wen = data_arb.io.out.bits.write
            data_array_wdata = data_array_wwords[i].grouped(self.p.data_enc_bits)
            array.io.en /= data_array_valid
            array.io.wmode /= data_array_wen
            array.io.addr /= data_arb.io.out.bits.addr >> self.row_off_bits()
            array.io.wmask /= cat_rvs(data_array_wmask)
            array.io.wdata /= cat_rvs(
                flatten(list(map(lambda _: data_array_wdata, range(self.p.num_ways)))))

        data_array_rdata = list(map(
            lambda _: list(map(
                lambda _: cat_rvs(_.grouped(self.p.word_bits // self.p.data_ecc_bits)),
                _.io.rdata.grouped(
                    (self.p.word_bits // self.p.data_ecc_bits) * self.p.data_enc_bits))),
            data_arrays))
        data_array_resp = vec(
            'data_array_resp',
            gen = bits,
            n = self.p.num_ways,
            w = data_arb.io.out.bits.wdata.get_w())
        for (resp, data) in list(zip(
            list(data_array_resp),
            list(map(list, list(zip(*data_array_rdata)))))):
            resp /= cat_rvs(data)


        tl_a_req = ready_valid(
            'tl_a_req',
            gen = type(self.tl_out.a.bits),
            p = self.tl_out.a.bits.p).as_bits()
        wb_a_req = ready_valid(
            'wb_a_req',
            gen = type(self.tl_out.a.bits),
            p = self.tl_out.a.bits.p).as_bits()
        tl_arb.io.input[0] /= wb_a_req
        tl_arb.io.input[1] /= tl_a_req

        s1_valid = reg_r('s1_valid', next=self.io.cpu.req.fire())
        s1_req = self.io.cpu.req.bits.clone('s1_req').as_reg()
        s1_paddr = s1_req.addr


        s1_hit_dtim = bits('s1_hit_dtim', init = 0)
        slave_block_cpu = bits('slave_block_cpu', init = 0)
        cpu_block_slave = bits('cpu_block_slave')
        #dtim's access control
        dtim_resp = bits(
            'dtim_resp',
            w = self.p.data_enc_bits * self.p.dtim_data_bytes // self.p.data_ecc_bytes,
            init = 0)
        if (self.p.dtim_size != 0):
            s1_hit_dtim /= (
                s1_valid & 
                (s1_paddr >= self.p.dtim_base) & 
                (s1_paddr < self.p.dtim_base + self.p.dtim_size))
            slave_ret = self.slave_dtim_access(
                s1_valid, s1_hit_dtim, cpu_block_slave, data_arb.io.out)
            slave_block_cpu /= slave_ret[0]
            dtim_resp /= slave_ret[1]
        else:
            self.io.slave.req.ready /= 0

            self.io.slave.resp.valid /= 0
            self.io.slave.resp.bits.replay /= 0
            self.io.slave.slow_kill /= 0

        s0_meta_rd = meta_arb.io.out.valid & ~meta_arb.io.out.bits.write
        flushing = reg_r('flushing')

        s1_nack = bits('s1_nack', init=0)
        s1_valid_masked = s1_valid & ~self.io.cpu.s1_kill
        s1_valid_not_nacked = s1_valid & ~s1_nack
        with when (s0_meta_rd):
            with when(~flushing):
                s1_req /= self.io.cpu.req.bits
            s1_req.addr /= meta_arb.io.out.bits.addr
        s1_is_read = M_CONSTS.is_read(s1_req.cmd)
        s1_is_write = M_CONSTS.is_write(s1_req.cmd)
        s1_is_flush = s1_req.cmd.match_any([M_CONSTS.M_FLUSH_ALL()])
        s1_is_read_write = s1_is_read | s1_is_write
        s1_is_sfence = s1_req.cmd == M_CONSTS.M_SFENCE()
        s1_flush_valid = reg('s1_flush_valid')
        s1_waw_hazard = bits('s1_waw_hazard')
        s1_meta_clk_en = s1_valid_not_nacked | s1_flush_valid

        refill_ack_wait = reg_r('refill_ack_wait')
        wb_ack_wait = reg_r('wb_ack_wait')
        [s_ready, s_wb, s_wb_meta] = range(3)
        wb_state = reg_rs('wb_state', rs = s_ready, w = 2)
        wb_state_is_ready = wb_state.match_any([s_ready])
        wb_state_is_wb = wb_state.match_any([s_wb])
        wb_state_is_wb_meta = wb_state.match_any([s_wb_meta])
        wb_way = bits('wb_way', w = self.p.num_ways, init = 0)

        uncached_source_offset = 1
        uncached_req_flags = list(map(
            lambda _: reg_r('uncached_req_flags_'+str(_)),
            range(self.p.num_flights - 1)))
        uncached_reqs = list(map(
            lambda _: zqh_core_common_lsu_mem_req('uncached_reqs_'+str(_)).as_reg(),
            range(self.p.num_flights - 1)))

        #cpu req's default ready
        self.io.cpu.req.ready /= wb_state_is_ready & ~refill_ack_wait & ~s1_nack


        s0_needs_read = self.needs_read(self.io.cpu.req.bits)
        s0_is_read = M_CONSTS.is_read(self.io.cpu.req.bits.cmd)
        data_arb.io.input[3].valid /= self.io.cpu.req.valid & s0_needs_read
        data_arb.io.input[3].bits.write /= 0
        data_arb.io.input[3].bits.addr /= self.io.cpu.req.bits.addr
        data_arb.io.input[3].bits.wordMask /= bin2oh(
            self.io.cpu.req.bits.addr[self.row_off_bits()-1:self.p.word_off_bits])
        data_arb.io.input[3].bits.way_en /= ~value(0, w = self.p.num_ways).to_bits()
        data_arb.io.input[3].bits.wdata /= 0
        data_arb.io.input[3].bits.poison /= 0
        data_arb.io.input[3].bits.eccMask /= 0
        with when (~data_arb.io.input[3].ready & s0_is_read):
            self.io.cpu.req.ready /= 0

        meta_arb.io.input[7].valid /= self.io.cpu.req.valid
        meta_arb.io.input[7].bits.write /= 0
        meta_arb.io.input[7].bits.addr /= self.io.cpu.req.bits.addr
        meta_arb.io.input[7].bits.way_en /= ~value(0, w = self.p.num_ways).to_bits()
        meta_arb.io.input[7].bits.data.coh.state /= zqh_client_states.nothing()
        meta_arb.io.input[7].bits.data.tag /= 0
        with when (~meta_arb.io.input[7].ready):
            self.io.cpu.req.ready /= 0

        with when (s1_valid & s1_is_read_write & slave_block_cpu):
            s1_nack /= 1


        s1_xcpt = self.xcpt_check(s1_req)
        s1_has_xcpt = s1_xcpt.pack().r_or()

        s1_meta = tag_array.io.rdata.grouped(
            self.tag_ecc.width(meta_arb.io.out.bits.data.get_w()))
        s1_meta_decoded = list(map(lambda _: self.tag_ecc.decode(_), s1_meta))
        s1_meta_uncorrected = list(map(
            lambda _: zqh_core_r1_lsu_dcache_metadata(
                init = self.tag_ecc.decode(s1_meta[_]).pre_correct),
            range(len(s1_meta))))
        s1_tag = s1_paddr >> self.p.untag_bits
        s1_hit_way = mux(
            s1_hit_dtim,
            value(1).to_bits() << self.p.num_ways,
            cat_rvs(map(
                lambda r: r.coh.is_valid() & (r.tag == s1_tag),
                s1_meta_uncorrected)))
        s1_hit_state = zqh_client_metadata(init = mux(
                    s1_hit_dtim,
                    zqh_client_states.dirty(),
                    reduce(
                        lambda x,y: x | y,
                        list(map(
                            lambda r: mux(
                                (r.tag == s1_tag) & ~s1_flush_valid,
                                r.coh.pack(),
                                zqh_client_states.nothing()),
                            s1_meta_uncorrected)))))
        s1_victim_way = bits(
            's1_victim_way',
            w = log2_up(self.p.num_ways),
            init = replacer.way())
        s1_victim_meta = sel_bin(s1_victim_way, s1_meta_uncorrected)
        s1_data_way = bits(
            w = self.p.num_ways + 2,
            init = mux(wb_state_is_wb, wb_way, s1_hit_way))
        s1_all_data_ways = (
            list(data_array_resp) + 
            [dtim_resp] + 
            [self.dummy_encode_data(self.tl_out.d.bits.data)])
        s1_mask = mux(
            s1_req.cmd == M_CONSTS.M_PWR(),
            self.io.cpu.s1_data.mask,
            M_CONSTS.store_mask_gen(s1_req.type, s1_req.addr, self.p.word_bytes))
        #s1_cacheable = mux(
        #    s1_hit_itim,
        #    0,
        #    self.interface_out.manager.address_attr_check(
        #        s1_req.addr,
        #        lambda _: _.cacheable()))
        s1_cacheable = self.interface_out.manager.address_attr_check(
                s1_req.addr,
                lambda _: _.cacheable())
        s1_data_clk_en = s1_valid | wb_state_is_wb | self.tl_out.d.fire()
        s1_did_read = reg_en(
            's1_did_read',
            next = data_arb.io.input[3].fire(),
            en = s0_meta_rd)

        s2_valid_pre_xcpt = reg_r(next = s1_valid_masked & ~s1_is_sfence)
        s2_valid = s2_valid_pre_xcpt
        s2_valid_masked = s2_valid & reg(next = ~s1_nack)
        s2_req = self.io.cpu.req.bits.clone().as_reg()
        s2_req_block_addr = (s2_req.addr >> self.p.block_off_bits) << self.p.block_off_bits
        s2_uncached = reg('s2_uncached')

        s2_xcpt = zqh_core_common_lsu_exceptions('s2_xcpt').as_reg(
            tp = 'reg_en',
            en = s1_meta_clk_en,
            next = s1_xcpt)
        s2_has_xcpt = reg_en(next = s1_has_xcpt, en = s1_meta_clk_en)

        with when (s1_valid_not_nacked | s1_flush_valid):
            s2_req /= s1_req
            s2_req.addr /= s1_paddr
            s2_uncached /= mux(s1_hit_dtim, 0, ~s1_cacheable)
        s2_is_read = M_CONSTS.is_read(s2_req.cmd)
        s2_is_write = M_CONSTS.is_write(s2_req.cmd)
        s2_is_readwrite = s2_is_read | s2_is_write
        s2_is_flush = s2_req.cmd.match_any([M_CONSTS.M_FLUSH_ALL()])
        s2_flush_valid_pre_tag_ecc = reg(next = s1_flush_valid)
        s2_meta_correctable_errors = cat_rvs(map(
            lambda m: reg_en(
                next = s1_meta_decoded[m].correctable & ~s1_hit_dtim,
                en = s1_meta_clk_en),
            range(len(s1_meta_decoded))))
        s2_meta_uncorrectable_errors = cat_rvs(map(
            lambda m: reg_en(
                next = s1_meta_decoded[m].uncorrectable & ~s1_hit_dtim,
                en = s1_meta_clk_en),
            range(len(s1_meta_decoded))))
        s2_meta_error_uncorrectable = s2_meta_uncorrectable_errors.r_or()
        s2_meta_corrected = list(map(
            lambda m: zqh_core_r1_lsu_dcache_metadata(
                init = reg_en(
                    w = s1_meta_decoded[m].post_correct.get_w(),
                    next = s1_meta_decoded[m].post_correct,
                    en = s1_meta_clk_en)),
            range(len(s1_meta_decoded))))
        s2_meta_error = (s2_meta_uncorrectable_errors | s2_meta_correctable_errors).r_or()
        s2_flush_valid = s2_flush_valid_pre_tag_ecc & ~s2_meta_error & ~s2_has_xcpt
        s2_data = reg_en(
            w = s1_all_data_ways[0].get_w(),
            next = sel_oh(s1_data_way, s1_all_data_ways),
            en = s1_data_clk_en)
        s2_hit_way = reg_en(
            w = s1_hit_way.get_w(),
            next = s1_hit_way,
            en = s1_valid_not_nacked)
        s2_hit_state = zqh_client_metadata('s2_hit_state').as_reg(
            tp = 'reg_en',
            en = s1_valid_not_nacked | s1_flush_valid,
            next = s1_hit_state)
        s2_waw_hazard = reg_en(
            's2_waw_hazard',
            w = s1_waw_hazard.get_w(),
            next = s1_waw_hazard,
            en = s1_valid_not_nacked)
        s2_store_merge = bits('s2_store_merge')
        s2_hit_valid = s2_hit_state.is_valid()
        s2_hit = s2_hit_state.is_valid()
        s2_new_hit_state = mux(
            M_CONSTS.is_write(s2_req.cmd),
            zqh_client_metadata(init = zqh_client_states.dirty()),
            s2_hit_state)
        s2_data_decoded = self.decode_data(s2_data)
        s2_word_idx = s2_req.addr[log2_up(self.row_bytes())-1: log2_up(self.p.word_bytes)]
        s2_did_read = reg_en(
            's2_did_read',
            w = s1_did_read.get_w(),
            next = s1_did_read,
            en = s1_valid_not_nacked)
        s2_data_error = s2_did_read & sel_bin(
            s2_word_idx,
            list(map(
                lambda _: reduce(lambda x,y: x | y, _),
                split_list(
                    list(map(lambda _: _.error(), s2_data_decoded)),
                    self.p.word_bits//self.p.data_ecc_bits))))
        s2_data_error_uncorrectable = sel_bin(
            s2_word_idx,
            list(map(
                lambda _: reduce(lambda x,y: x | y, _) ,
                split_list(
                    list(map(lambda _: _.uncorrectable, s2_data_decoded)),
                    self.p.word_bits//self.p.data_ecc_bits))))
        s2_data_corrected = cat_rvs(map(lambda _: _.post_correct, s2_data_decoded))
        s2_data_uncorrected = cat_rvs(map(lambda _: _.pre_correct, s2_data_decoded))
        s2_valid_hit_pre_data_ecc = (
            s2_valid_masked & 
            s2_is_readwrite & 
            ~s2_meta_error & 
            ~s2_has_xcpt & 
            s2_hit)
        s2_valid_data_error = s2_valid_hit_pre_data_ecc & s2_data_error & ~wb_ack_wait
        s2_valid_hit = (
            s2_valid_hit_pre_data_ecc & 
            ~s2_data_error & 
            (~s2_waw_hazard | s2_store_merge))
        s2_valid_miss = (
            s2_valid_masked & 
            s2_is_readwrite & 
            ~s2_meta_error & 
            ~s2_has_xcpt & 
            ~s2_hit & 
            ~wb_ack_wait)
        s2_valid_cached_miss = (
            s2_valid_miss & ~s2_uncached & ~cat_rvs(uncached_req_flags).r_or())
        s2_victimize = s2_valid_cached_miss | s2_valid_data_error | s2_flush_valid
        s2_valid_uncached_pending = (
            s2_valid_miss & s2_uncached & ~cat_rvs(uncached_req_flags).r_and())
        s2_victim_way = mux(
            s2_hit_valid,
            s2_hit_way,
            bin2oh(reg_en(
                w = s1_victim_way.get_w(),
                next = s1_victim_way,
                en = s1_valid_not_nacked | s1_flush_valid)))
        s2_victim_tag = mux(
            s2_valid_data_error,
            s2_req.addr >> self.p.untag_bits,
            reg_en(
                w = s1_victim_meta.tag.get_w(),
                next = s1_victim_meta.tag,
                en = s1_valid_not_nacked | s1_flush_valid))
        s2_victim_state = mux(
            s2_hit_valid,
            s2_hit_state,
            zqh_client_metadata().as_reg(
                tp = 'reg_en', 
                en = s1_valid_not_nacked | s1_flush_valid,
                next = s1_victim_meta.coh))
        s2_victim_dirty = s2_victim_state.state == zqh_client_states.dirty()
        s2_update_meta = s2_hit_state != s2_new_hit_state
        s2_hit_dtim = reg_en(next = s1_hit_dtim, en = s1_valid_not_nacked)

        s2_replay = bits('s2_replay', init = 0)
        s2_replay /= (
            s2_valid & 
            (~s2_valid_hit & ~(s2_valid_uncached_pending & tl_a_req.ready) | s2_has_xcpt))
        with when (s2_replay | (s2_valid_hit & s2_update_meta)):
            s1_nack /= 1

        s2_replay_tag = reg('s2_replay_tag', w = s1_req.tag.get_w(), next = s1_req.tag)


        ## tag updates on ECC errors
        meta_arb.io.input[1].valid /= (
            s2_meta_error & 
            (s2_valid_masked | s2_flush_valid_pre_tag_ecc))
        meta_arb.io.input[1].bits.write /= 1
        meta_arb.io.input[1].bits.way_en /= (
            s2_meta_uncorrectable_errors | 
            mux(
                s2_meta_error_uncorrectable,
                0,
                pri_lsb_enc_oh(s2_meta_correctable_errors)))
        meta_arb.io.input[1].bits.addr /= s2_req.addr
        meta_arb.io.input[1].bits.data /= sel_p_lsb(
            s2_meta_correctable_errors,
            s2_meta_corrected)
        with when (s2_meta_error_uncorrectable):
            meta_arb.io.input[1].bits.data.coh.state /= zqh_client_states.nothing()


        ## tag updates on hit/miss
        meta_arb.io.input[2].valid /= (
            (s2_valid_hit & s2_update_meta) | 
            (s2_victimize & ~s2_victim_dirty))
        meta_arb.io.input[2].bits.write /= 1
        meta_arb.io.input[2].bits.way_en /= s2_victim_way
        meta_arb.io.input[2].bits.addr /= s2_req.addr
        meta_arb.io.input[2].bits.data.coh.state /= mux(
            s2_valid_hit, 
            s2_new_hit_state.state, 
            zqh_client_states.nothing())
        meta_arb.io.input[2].bits.data.tag /= s2_req.addr >> self.p.untag_bits


        ##lr and sc
        s2_lr = self.p.isa_a & (s2_req.cmd == M_CONSTS.M_XLR())
        s2_sc = self.p.isa_a & (s2_req.cmd == M_CONSTS.M_XSC())
        lrsc_count = reg_r('lrsc_count', w = log2_ceil(self.p.lrsc_cycles))
        lrsc_valid = lrsc_count > self.p.lrsc_back_off
        lrsc_backing_off = (lrsc_count > 0) & ~lrsc_valid
        lrsc_addr = reg('lrsc_addr', w = s2_req.addr.get_w() - self.p.block_off_bits)
        lrsc_addr_match = lrsc_addr == (s2_req.addr >> self.p.block_off_bits)
        s2_sc_fail = s2_sc & ~(lrsc_valid & lrsc_addr_match)
        with when ((s2_valid_hit & s2_lr & ~refill_ack_wait) | s2_valid_cached_miss):
            lrsc_count /= mux(s2_hit, self.p.lrsc_cycles - 1, 0)
            lrsc_addr /= s2_req.addr >> self.p.block_off_bits
        with when (lrsc_count > 0):
            lrsc_count /= lrsc_count - 1
        with when (s2_valid_masked & (lrsc_count > 0)):
            lrsc_count /= 0 


        #store buffer
        pstore_any_valid = bits('pstore_any_valid')
        s2_correct = s2_data_error & ~pstore_any_valid & ~reg(next = pstore_any_valid)
        s2_valid_correct = s2_valid_hit_pre_data_ecc & s2_correct
        s2_store_valid = s2_valid_hit & s2_is_write & ~s2_sc_fail

        pstore1_cmd = reg_en(
            'pstore1_cmd',
            w = s1_req.cmd.get_w(),
            next = s1_req.cmd,
            en = s1_valid_not_nacked & s1_is_write)
        pstore1_addr = reg_en(
            'pstore1_addr',
            w = s1_paddr.get_w(),
            next = s1_paddr,
            en = s1_valid_not_nacked & s1_is_write)
        pstore1_data = reg_en(
            'pstore1_data',
            w = self.io.cpu.s1_data.data.get_w(),
            next = self.io.cpu.s1_data.data,
            en = s1_valid_not_nacked & s1_is_write)
        pstore1_way = reg_en(
            'pstore1_way',
            w = s1_hit_way.get_w(),
            next = s1_hit_way,
            en = s1_valid_not_nacked & s1_is_write)
        pstore1_mask = reg_en(
            'pstore1_mask', 
            w = s1_mask.get_w(),
            next = s1_mask, 
            en = s1_valid_not_nacked & s1_is_write)
        pstore1_storegen_data = bits(
            'pstore1_storegen_data',
            w = pstore1_data.get_w(),
            init = pstore1_data)
        pstore1_rmw = (
            using_rmw & 
            reg_en_r(
                next = self.needs_read(s1_req),
                en = s1_valid_not_nacked & s1_is_write))
        pstore1_valid = bits('pstore1_valid')
        pstore1_merge = s2_store_valid & s2_store_merge
        pstore2_valid = reg_r('pstore2_valid')
        pstore_any_valid /= pstore1_valid | pstore2_valid
        pstore_drain_structural = (
            pstore1_valid & pstore2_valid & ((s1_valid & s1_is_write) | pstore1_rmw))
        pstore_drain_opportunistic = ~(self.io.cpu.req.valid & s0_needs_read)
        pstore_drain_on_miss = (
            ~wb_state_is_ready | (s2_valid & ~s2_valid_hit & ~s2_valid_uncached_pending))
        pstore_drain = ~pstore1_merge & (
            (using_rmw & pstore_drain_structural) |
            (
                ((pstore1_valid & ~pstore1_rmw) | pstore2_valid) & 
                (pstore_drain_opportunistic | pstore_drain_on_miss)))
        pstore1_held = reg('pstore1_held')
        vassert(~s2_store_valid | ~pstore1_held)
        pstore1_held /= (
            ((s2_store_valid & ~s2_store_merge) | pstore1_held) & 
            pstore2_valid & ~pstore_drain)
        pstore1_valid /= s2_store_valid | pstore1_held
        advance_pstore1 = (
            (pstore1_valid | s2_valid_correct) & 
            (pstore2_valid == pstore_drain))
        pstore2_valid /= (pstore2_valid & ~pstore_drain) | advance_pstore1
        pstore2_addr = reg_en(
            'pstore2_addr',
            w = max(s2_req.addr.get_w(), pstore1_addr.get_w()),
            next = mux( s2_correct, s2_req.addr, pstore1_addr),
            en = advance_pstore1)
        pstore2_way = reg_en(
            'pstore2_way',
            w = max(s2_hit_way.get_w(), pstore1_way.get_w()),
            next = mux(s2_correct, s2_hit_way, pstore1_way),
            en = advance_pstore1)
        pstore2_storegen_data = cat_rvs(map(
            lambda _: reg_en(
                w = 8,
                next = pstore1_storegen_data[8*(_+1)-1: 8*_],
                en = advance_pstore1 | (pstore1_merge & pstore1_mask[_])),
            range(self.p.word_bytes)))
        pstore2_storegen_mask = reg('pstore2_storegen_mask', w = self.p.word_bytes)
        with when (advance_pstore1 | pstore1_merge):
            mergedMask = pstore1_mask | mux(pstore1_merge, pstore2_storegen_mask, 0)
            pstore2_storegen_mask /= ~mux(s2_correct, 0, ~mergedMask)
        if (self.p.data_ecc_bytes == 1):
            s2_store_merge /= 0
        else:
            word_match = (
                self.ecc_mask(pstore2_storegen_mask) | 
                ~self.ecc_mask(pstore1_mask)).r_and()
            idx_match = (
                s2_req.addr[self.p.untag_bits-1: log2_ceil(self.p.word_bytes)] == 
                pstore2_addr[self.p.untag_bits-1: log2_ceil(self.p.word_bytes)])
            tag_match = (s2_hit_way & pstore2_way).r_or()
            s2_store_merge /= pstore2_valid & word_match & idx_match & tag_match

        data_arb.io.input[0].valid /= pstore_drain
        data_arb.io.input[0].bits.write /= 1
        data_arb.io.input[0].bits.addr /= mux(pstore2_valid, pstore2_addr, pstore1_addr)
        data_arb.io.input[0].bits.way_en /= mux(pstore2_valid, pstore2_way, pstore1_way)
        data_arb.io.input[0].bits.wdata /= mux(
            pstore2_valid,
            pstore2_storegen_data,
            pstore1_data).rep(self.row_words())
        data_arb.io.input[0].bits.poison /= 0
        data_arb.io.input[0].bits.wordMask /= bin2oh(
            mux(
                pstore2_valid,
                pstore2_addr,
                pstore1_addr)[self.row_off_bits()-1:self.p.word_off_bits])
        data_arb.io.input[0].bits.eccMask /= self.ecc_mask(mux(
            pstore2_valid,
            pstore2_storegen_mask,
            pstore1_mask))


        s3_hit_dtim = reg_en(next = s2_hit_dtim, en = advance_pstore1)
        cpu_block_slave /= (
            (pstore1_valid & s2_hit_dtim) | 
            (pstore2_valid & s3_hit_dtim) | 
            (data_arb.io.input[1].fire() & (data_arb.io.input[1].bits.way_en == 0)) | 
            (data_arb.io.input[2].fire() & (data_arb.io.input[2].bits.way_en == 0)))


        #read after write hazard detect
        def s1_depends(addr, mask):
            return (
                (
                    addr[self.p.untag_bits-1: self.p.word_off_bits] == 
                    s1_req.addr[self.p.untag_bits-1: self.p.word_off_bits]) & 
                mux(
                    s1_is_write,
                    (self.ecc_byte_mask(mask) & self.ecc_byte_mask(s1_mask)).r_or(),
                    (mask & s1_mask).r_or()))

        s1_hazard = (
            (pstore1_valid & s1_depends(pstore1_addr, pstore1_mask)) | 
            (pstore2_valid & s1_depends(pstore2_addr, pstore2_storegen_mask)))
        s1_raw_hazard = s1_is_read & s1_hazard
        s1_waw_hazard /= (
            0 
            if (self.p.data_ecc_bytes == 1) else 
            (s1_is_write & (s1_hazard | (self.needs_read(s1_req) & ~s1_did_read))))

        with when (s1_valid & s1_raw_hazard):
            s1_nack /= 1


        #gen tl_a request message
        tl_a_uncached_addr = s2_req.addr
        tl_a_uncached_source = pri_lsb_enc(
            ~cat_rvs(uncached_req_flags) << uncached_source_offset)
        tl_a_uncached_size = s2_req.type[D_CONSTS.SZ_MT - 2 : 0]
        tl_a_uncached_data = pstore1_data.rep(
            self.tl_out.a.bits.data.get_w() // self.p.core_data_bits)
        tl_a_uncached_get = self.interface_out.get(
            tl_a_uncached_source,
            tl_a_uncached_addr,
            tl_a_uncached_size)[1]
        tl_a_uncached_put = self.interface_out.put(
            tl_a_uncached_source,
            tl_a_uncached_addr,
            tl_a_uncached_size,
            tl_a_uncached_data)[1]
        tl_a_cached_get = self.interface_out.get(
            value(0),
            s2_req_block_addr,
            log2_up(self.p.cache_block_size))[1]
        if (self.p.isa_a):
            tl_a_atomics = sel_map(s2_req.cmd, [
                (M_CONSTS.M_XA_SWAP() , self.interface_out.logical(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.swap())   [1]),
                (M_CONSTS.M_XA_XOR () , self.interface_out.logical(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.xor())    [1]),
                (M_CONSTS.M_XA_OR  () , self.interface_out.logical(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.orr())     [1]),
                (M_CONSTS.M_XA_AND () , self.interface_out.logical(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.andd())    [1]),
                (M_CONSTS.M_XA_ADD () , self.interface_out.arithmetic(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.add()) [1]),
                (M_CONSTS.M_XA_MIN () , self.interface_out.arithmetic(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.min()) [1]),
                (M_CONSTS.M_XA_MAX () , self.interface_out.arithmetic(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.max()) [1]),
                (M_CONSTS.M_XA_MINU() , self.interface_out.arithmetic(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.minu())[1]),
                (M_CONSTS.M_XA_MAXU() , self.interface_out.arithmetic(tl_a_uncached_source, tl_a_uncached_addr, tl_a_uncached_size, tl_a_uncached_data, TAMO_CONSTS.maxu())[1])], zqh_tl_bundle_a(p = self.interface_out.bundle.channel['a'], init = 0))
        else:
            tl_a_atomics = zqh_tl_bundle_a(
                p = self.interface_out.bundle.channel['a'], init = 0)

        tl_a_req.valid /= (
            (s2_valid_cached_miss & ~s2_victim_dirty) | 
            s2_valid_uncached_pending)
        tl_a_req.bits /= mux(
            ~s2_uncached,
            tl_a_cached_get,
            mux(
                ~s2_is_write,
                tl_a_uncached_get,
                mux(~s2_is_read, tl_a_uncached_put, tl_a_atomics)))


        #record cache/uncache tl_a request's status
        a_sel = bin2oh(tl_a_uncached_source, self.p.num_flights) >> uncached_source_offset
        with when (tl_a_req.fire()):
            with when (s2_uncached):
                for (s, (f, r)) in list(zip(
                    a_sel.grouped(),
                    (list(zip(uncached_req_flags, uncached_reqs))))):
                    with when (s):
                        f /= 1
                        r /= s2_req
            with other():
                refill_ack_wait /= 1


        #tl_d resp's decode
        (d_first, d_last, d_done, d_address_inc) = self.interface_out.addr_inc(
            self.tl_out.d)
        d_resp_is_cached = self.tl_out.d.bits.opcode.match_any([
            TMSG_CONSTS.access_ack_data()]) & (self.tl_out.d.bits.source == 0)
        d_resp_is_uncached = self.tl_out.d.bits.source != 0
        d_resp_is_uncached_data = self.tl_out.d.bits.opcode.match_any([
            TMSG_CONSTS.access_ack_data()]) & (self.tl_out.d.bits.source != 0)
        d_resp_is_wb = self.tl_out.d.bits.opcode.match_any([
            TMSG_CONSTS.access_ack()]) & (self.tl_out.d.bits.source == 0)
        d_resp_is_refill = self.tl_out.d.bits.opcode.match_any([
            TMSG_CONSTS.access_ack_data()]) & (self.tl_out.d.bits.source == 0)
        d_resp_in_progress = reg_r('d_resp_in_progress')
        with when (self.tl_out.d.fire()):
            with when (d_resp_is_cached):
                d_resp_in_progress /= 1
                vassert(refill_ack_wait, "A AccessAckData was unexpected by the dcache.")
                with when(d_last):
                    refill_ack_wait /= 0
                    d_resp_in_progress /= 0
                    replacer.miss()
            with elsewhen (d_resp_is_uncached):
                d_sel = bin2oh(
                    self.tl_out.d.bits.source,
                    self.p.num_flights) >> uncached_source_offset
                req = sel_oh(d_sel, uncached_reqs)
                for (s, f) in list(zip(d_sel.grouped(), uncached_req_flags)):
                    with when (s & d_last):
                        vassert(f, "An AccessAck was unexpected by the dcache.")
                        f /= 0
                with when (d_resp_is_uncached_data):
                    s1_data_way /= value(1).to_bits() << (self.p.num_ways + 1)
                    s2_req.cmd /= M_CONSTS.M_XRD()
                    s2_req.type /= req.type
                    s2_req.tag /= req.tag
                    s2_req.addr /= cat([
                        s1_paddr >> self.beat_off_bits(),
                        req.addr[self.beat_off_bits()-1: 0]])
            with elsewhen (d_resp_is_wb):
                vassert(wb_ack_wait, "A AccessAck was unexpected by the dcache.")
                wb_ack_wait /= 0


        #cached and miss's data refill
        data_arb.io.input[1].valid /= self.tl_out.d.valid & d_resp_is_refill
        data_arb.io.input[1].bits.write /= 1
        data_arb.io.input[1].bits.addr /= s2_req_block_addr | d_address_inc
        data_arb.io.input[1].bits.way_en /= s2_victim_way
        data_arb.io.input[1].bits.wdata /= self.tl_out.d.bits.data
        data_arb.io.input[1].bits.poison /= self.tl_out.d.bits.error
        data_arb.io.input[1].bits.wordMask /= (
            ~value(0, w = self.row_bytes() // self.p.word_bytes).to_bits())
        data_arb.io.input[1].bits.eccMask /= (
            ~value(0, w = self.p.word_bytes // self.p.data_ecc_bytes))


        #update cache's tag when refill data done
        meta_arb.io.input[3].valid /= d_resp_is_cached & d_done
        meta_arb.io.input[3].bits.write /= 1
        meta_arb.io.input[3].bits.way_en /= s2_victim_way
        meta_arb.io.input[3].bits.addr /= s2_req.addr
        meta_arb.io.input[3].bits.data.coh.state /= mux(
            M_CONSTS.is_write(s2_req.cmd),
            zqh_client_states.dirty(),
            zqh_client_states.trunk())
        meta_arb.io.input[3].bits.data.tag /= s2_req.addr >> self.p.untag_bits

        block_uncached_d_resp = reg(
            'block_uncached_d_resp',
            next = data_arb.io.out.valid)
        self.tl_out.d.ready /= 1
        with when (d_resp_is_refill & ~data_arb.io.input[1].ready):
            self.tl_out.d.ready /= 0
        with when (d_resp_is_uncached_data & (block_uncached_d_resp | s1_valid)):
            self.tl_out.d.ready /= 0
            with when (self.tl_out.d.valid):
                self.io.cpu.req.ready /= 0
                data_arb.io.input[1].valid /= 1
                data_arb.io.input[1].bits.write /= 0
                block_uncached_d_resp /= ~data_arb.io.input[1].ready

        meta_arb.io.input[6].valid /= 0


        #write back FSM
        (wb_first, wb_last, wb_done, wb_count) = self.interface_out.count(wb_a_req)
        wb_blocked = wb_a_req.valid & ~wb_a_req.ready
        s1_wb_data_valid = reg('s1_wb_data_valid', next = data_arb.io.input[2].fire())
        s2_wb_data_valid = reg(next = s1_wb_data_valid & ~wb_blocked)
        wb_data_beat = cat([value(0), wb_count]) + mux(
            wb_blocked,
            0,
            s1_wb_data_valid + cat([value(0), s2_wb_data_valid]))
        wb_data_error = reduce(
            lambda x,y: x|y, list(map(lambda _: _.error(), s2_data_decoded)))
        wb_data_uncorrectable = reduce(
            lambda x,y: x|y, list(map(lambda _: _.uncorrectable, s2_data_decoded)))

        wb_a_addr = reg(w = self.tl_out.a.bits.address.get_w())
        wb_a_req.valid /= s2_wb_data_valid
        wb_a_req.bits /= self.interface_out.put(
            0,
            wb_a_addr,
            log2_up(self.p.cache_block_size), s2_data_corrected)[1]

        #wb_state update
        with when (s2_victimize & s2_victim_dirty):
            vassert(~(s2_valid & s2_hit_valid & ~s2_data_error))
            wb_state /= s_wb
            wb_a_addr /= (
                cat([
                    s2_victim_tag,
                    s2_req.addr[self.p.untag_bits-1: self.p.block_off_bits]]) << 
                self.p.block_off_bits)
        with when (wb_state_is_wb | wb_state_is_wb_meta):
            wb_way /= s2_victim_way
            with when (wb_done):
                wb_state /= s_wb_meta 
            with when (wb_a_req.fire() & wb_first):
                wb_ack_wait /= 1
        with when (meta_arb.io.input[4].fire()):
            wb_state /= s_ready 


        #read out data_array's dirty data and write back
        data_arb.io.input[2].valid /= (
            wb_state_is_wb & (wb_data_beat < self.cache_block_beats()))
        data_arb.io.input[2].bits.write /= 0
        data_arb.io.input[2].bits.addr /= (
            wb_a_req.bits.address | 
            (wb_data_beat[log2_up(self.cache_block_beats())-1:0] << self.row_off_bits()))
        data_arb.io.input[2].bits.wordMask /= (
            ~value(0, self.row_bytes() // self.p.word_bytes).to_bits())
        data_arb.io.input[2].bits.way_en /= ~value(0, self.p.num_ways).to_bits()
        data_arb.io.input[2].bits.wdata /= 0
        data_arb.io.input[2].bits.poison /= 0
        data_arb.io.input[2].bits.eccMask /= 0

        #clean tag after writeback data is done
        meta_arb.io.input[4].valid /= wb_state_is_wb_meta
        meta_arb.io.input[4].bits.write /= 1
        meta_arb.io.input[4].bits.way_en /= wb_way
        meta_arb.io.input[4].bits.addr /= wb_a_req.bits.address
        meta_arb.io.input[4].bits.data.coh.state /= zqh_client_states.nothing()
        meta_arb.io.input[4].bits.data.tag /= wb_a_req.bits.address >> self.p.untag_bits


        #cpu's cached response
        self.io.cpu.resp.valid /= s2_valid_hit | s2_replay | (s2_valid_masked & s2_is_flush)
        self.io.cpu.resp.bits.tag /= mux(s2_replay, s2_replay_tag, s2_req.tag)
        self.io.cpu.resp.bits.type /= s2_req.type
        self.io.cpu.resp.bits.has_data /= s2_is_read
        self.io.cpu.resp.bits.replay /= s2_replay
        self.io.cpu.resp.bits.slow /= 0
        self.io.cpu.busy /= (
            s1_valid | s2_valid | refill_ack_wait | cat_rvs(uncached_req_flags).r_or())
        self.io.cpu.resp.bits.xcpt /= mux(
            s2_has_xcpt,
            s2_xcpt,
            zqh_core_common_lsu_exceptions(init = 0))

        #cpu's uncached response
        self.io.cpu.slow_kill /= self.tl_out.d.fire() & d_resp_is_uncached_data
        do_uncached_resp = reg('do_uncached_resp', next = self.io.cpu.slow_kill)
        with when (do_uncached_resp):
            vassert(~s2_valid_hit)
            self.io.cpu.resp.valid /= 1
            self.io.cpu.resp.bits.slow /= 1
            self.io.cpu.resp.bits.replay /= 0

        s2_data_word = sel_bin(
            s2_word_idx,
            map(
                lambda i: s2_data_uncorrected[self.p.word_bits+i-1:i],
                range(0, self.row_bits(), self.p.word_bits)))
        s2_data_word_corrected = sel_bin(
            s2_word_idx,
            map(
                lambda i: s2_data_corrected[self.p.word_bits+i-1:i],
                range(0, self.row_bits(), self.p.word_bits)))
        self.io.cpu.resp.bits.data /= mux(
            s2_sc_fail,
            1,
            mux(
                s2_sc,
                0,
                M_CONSTS.load_data_gen(
                    s2_req.type,
                    s2_req.addr,
                    s2_data_word,
                    self.p.word_bytes,
                    1)))
        self.io.cpu.resp.bits.data_word_bypass /= mux(
            s2_sc_fail,
            1,
            mux(
                s2_sc,
                0,
                M_CONSTS.load_data_gen(
                    s2_req.type,
                    s2_req.addr,
                    s2_data_word,
                    self.p.word_bytes,
                    4)))
        self.io.cpu.resp.bits.data_no_shift /= s2_data_word


        #atomics
        if (self.p.isa_a):
            amo_alu = zqh_core_common_amo_alu('amo_alu', width = self.p.core_data_bits)
            amo_alu.io.mask /= pstore1_mask
            amo_alu.io.cmd /= pstore1_cmd if (self.p.isa_a) else M_CONSTS.M_XWR()
            amo_alu.io.lhs /= s2_data_word
            amo_alu.io.rhs /= pstore1_data
            pstore1_storegen_data /= amo_alu.io.out
        #ecc code gen need merge operation
        elif (self.p.data_ecc_bytes > 1):
            bit_mask = pstore1_mask.rep_each_bit(8)
            pstore1_storegen_data /= (bit_mask & pstore1_data) | (~bit_mask & s2_data_word)
        else:
            vassert(~(s1_valid_masked & s1_is_read & s1_is_write))

        with when (s2_correct):
            pstore1_storegen_data /= s2_data_word_corrected 


        #cache flush. do write back if data is dirty
        flushed = reg_s('flushed')
        flush_all = reg('flush_all')
        flush_counter = reg_rs(
            'flush_counter',
            w = log2_ceil(self.p.num_sets * self.p.num_ways),
            rs = self.p.num_sets * (self.p.num_ways-1))
        flush_counter_next_add1 = flush_counter + 1
        flush_counter_next_way = flush_counter + self.p.num_sets
        flush_counter_next = mux(
            flush_all,
            flush_counter_next_add1,
            flush_counter_next_way)
        flush_done = (flush_counter_next >> log2_ceil(self.p.num_sets)) == self.p.num_ways
        with when(s2_valid_masked & s2_is_flush):
            s2_replay /= ~flushed
            with when(flushed & (s2_req.cmd == M_CONSTS.M_FLUSH())):
                flushed /= 0
            with when (~flushed):
                flushing /= ~wb_ack_wait & ~cat_rvs(uncached_req_flags).r_or()
                with when(s2_req.type == D_CONSTS.MT_B()):
                    flush_all /= 1
                with other():
                    flush_all /= 0
                    flush_counter /= (
                        (s2_req.addr >> self.p.block_off_bits)
                        [log2_ceil(self.p.num_sets) - 1 : 0].u_ext(flush_counter.get_w()))
        meta_arb.io.input[5].valid /= flushing
        meta_arb.io.input[5].bits.write /= 0
        meta_arb.io.input[5].bits.addr /= (
            flush_counter[self.p.idx_bits-1: 0] << self.p.block_off_bits)
        meta_arb.io.input[5].bits.way_en /= ~value(0, self.p.num_ways).to_bits()
        meta_arb.io.input[5].bits.data.coh.state /= zqh_client_states.nothing()
        meta_arb.io.input[5].bits.data.tag /= 0
        s1_flush_valid /= (
            meta_arb.io.input[5].fire() & 
            ~s1_flush_valid & 
            ~s2_flush_valid_pre_tag_ecc & 
            wb_state_is_ready & 
            ~wb_ack_wait)
        with when (tl_a_req.fire() & ~s2_uncached):
            flushed /= 0
        with when (flushing):
            s1_victim_way /= flush_counter >> log2_up(self.p.num_sets)
            with when (s2_flush_valid):
                flush_counter /= flush_counter_next
                with when (flush_done):
                    flushed /= 1
                    flush_counter /= 0
            with when (flushed & wb_state_is_ready & ~wb_ack_wait):
                flushing /= 0


        #power on reset. like flush but no write back
        resetting = reg_r('resetting')
        with when (reg_s(next = 0)):
            resetting /= 1
            flush_all /= 1
        meta_arb.io.input[0].valid /= resetting
        meta_arb.io.input[0].bits.addr /= meta_arb.io.input[5].bits.addr
        meta_arb.io.input[0].bits.write /= 1
        meta_arb.io.input[0].bits.way_en /= ~value(0, self.p.num_ways).to_bits()
        meta_arb.io.input[0].bits.data.coh.state /= zqh_client_states.nothing()
        meta_arb.io.input[0].bits.data.tag /= 0
        with when (resetting):
            flush_counter /= flush_counter_next
            with when (flush_done):
                resetting /= 0
                flush_counter /= 0


        #performance events
        self.io.cpu.events.refill /= self.interface_out.done(tl_a_req)
        self.io.cpu.events.write_back/= self.interface_out.done(wb_a_req)


        #memory and tl bus error report
        (data_error, data_error_uncorrectable, data_error_addr) = (
            wb_a_req.fire() & wb_state_is_wb & wb_data_error,
            wb_data_uncorrectable,
            wb_a_req.bits.address)
        (dtim_error, dtim_error_uncorrectable, dtim_error_addr) = (
            s2_valid_data_error & s2_hit_dtim,
            s2_data_error_uncorrectable & s2_hit_dtim,
            s2_req.addr) if (self.p.dtim_size != 0) else (0, 0, 0)
        error_addr = mux(
            meta_arb.io.input[1].valid,
            cat([
                meta_arb.io.input[1].bits.data.tag,
                meta_arb.io.input[1].bits.addr
                    [self.p.untag_bits-1: self.p.block_off_bits]]),
            mux(
                data_error,
                data_error_addr, 
                dtim_error_addr) >> self.p.block_off_bits) << self.p.block_off_bits
        self.io.errors.uncorrectable.valid /= (
            (meta_arb.io.input[1].valid & s2_meta_error_uncorrectable) | 
            (data_error & data_error_uncorrectable) | 
            (dtim_error & dtim_error_uncorrectable))
        self.io.errors.uncorrectable.bits /= error_addr
        self.io.errors.correctable.valid /= (
            meta_arb.io.input[1].valid | data_error | dtim_error)
        self.io.errors.correctable.bits /= error_addr
        with when(self.io.errors.uncorrectable.valid):
            self.io.errors.correctable.valid /= 0
        self.io.errors.bus.valid /= self.tl_out.d.fire() & self.tl_out.d.bits.error
        self.io.errors.bus.bits /= mux(
            d_resp_is_cached,
            s2_req.addr >> self.p.block_off_bits << self.p.block_off_bits,
            0)

    def encode_data(self, x, poison):
        return cat(list(reversed(list(map(
            lambda _: self.data_ecc.encode(_, poison if (self.data_ecc.canDetect()) else 0),
            x.grouped(self.p.data_ecc_bits))))))
    def dummy_encode_data(self, x):
        return cat(list(reversed(list(map(
            lambda _: self.data_ecc.swizzle(_),
            x.grouped(self.p.data_ecc_bits))))))
    def decode_data(self, x):
        return list(map(
            lambda _: self.data_ecc.decode(_),
            x.grouped(self.p.data_enc_bits)))
    def ecc_mask(self, byteMask):
        return cat_rvs(list(map(
            lambda _: _.r_or(),
            byteMask.grouped(self.p.data_ecc_bytes))))
    def ecc_byte_mask(self, byteMask):
        return self.ecc_mask(byteMask).rep_each_bit(self.p.data_ecc_bytes)
    def needs_read(self, req):
        return (
            M_CONSTS.is_read(req.cmd) | 
            (
                M_CONSTS.is_write(req.cmd) & 
                (
                    (req.cmd == M_CONSTS.M_PWR()) | 
                    (req.type[D_CONSTS.SZ_MT - 2 : 0] < log2_ceil(self.p.data_ecc_bytes)))))

    def slave_dtim_access(self, s1_valid, s1_hit_dtim, block_slave, cpu_access):
        vmacro('USE_DTIM')
        vmacro('DTIM_SIZE', self.p.dtim_size)
        dtim_array = reg_array(
            'dtim_array',
            o_reg = 1,
            size = self.p.dtim_size//self.p.dtim_data_bytes,
            data_width = (
                (self.p.dtim_data_bits // self.p.data_ecc_bits) * 
                self.p.data_enc_bits),
            mask_width = self.p.dtim_data_bits // self.p.data_ecc_bits)

        #slave block cpu cnt
        block_cpu = bits()
        block_cnt = reg_r('block_cnt', w = 4)
        with when(s1_valid):
            with when(block_cpu):
                with when(block_cnt != 0xf):
                    block_cnt /= block_cnt + 1
            with other():
                block_cnt /= 0
        slave_ready_stall_cnt = reg_r('slave_ready_stall_cnt', w = 4)
        slave_ready_stall_for_cpu = slave_ready_stall_cnt != 0
        with when((block_cnt == self.p.block_threshold) | slave_ready_stall_for_cpu):
            with when(slave_ready_stall_cnt == self.p.slave_ready_stall_threshold):
                slave_ready_stall_cnt /= 0
            with other():
                slave_ready_stall_cnt /= slave_ready_stall_cnt + 1


        s0_dtim_needs_read = self.io.slave.req.fire() & self.needs_read(
            self.io.slave.req.bits)
        s0_dtim_partial_ecc_wr = self.io.slave.req.fire() & M_CONSTS.is_write(
            self.io.slave.req.bits.cmd) & s0_dtim_needs_read
        s0_dtim_read = self.io.slave.req.fire() & M_CONSTS.is_read(
            self.io.slave.req.bits.cmd)
        s0_dtim_mask = mux(
            self.io.slave.req.bits.cmd == M_CONSTS.M_PWR(),
            self.io.slave.req.bits.mask,
            M_CONSTS.store_mask_gen(
                self.io.slave.req.bits.type,
                self.io.slave.req.bits.addr,
                self.p.dtim_data_bytes))

        s1_dtim_did_read = reg_r('s1_dtim_did_read', next = s0_dtim_needs_read)
        s1_dtim_partial_ecc_wr = reg_r(
            's1_dtim_partial_ecc_wr', 
            next = s0_dtim_partial_ecc_wr)
        s1_dtim_read = reg('s1_dtim_read', next = s0_dtim_read)
        s1_dtim_req = self.io.slave.req.bits.clone('s1_dtim_req').as_reg(
            next = self.io.slave.req.bits)
        s1_dtim_mask = reg(
            's1_dtim_mask',
            w = self.io.slave.req.bits.mask.get_w(),
            next = s0_dtim_mask)

        s2_dtim_did_read = reg_r('s2_dtim_did_read', next = s1_dtim_did_read)
        s2_dtim_partial_ecc_wr = reg_r(
            's2_dtim_partial_ecc_wr',
            next = s1_dtim_partial_ecc_wr)
        s2_dtim_read = reg('s2_dtim_read', next = s1_dtim_read)
        s2_dtim_req = self.io.slave.req.bits.clone('s2_dtim_req').as_reg(
            next = s1_dtim_req)
        s2_dtim_mask = reg(
            's2_dtim_mask', 
            w = self.io.slave.req.bits.mask.get_w(), 
            next = s1_dtim_mask)
        s2_dtim_data = reg(
            's2_dtim_data',
            w = dtim_array.io.rdata.get_w(),
            next = dtim_array.io.rdata)
        s2_dtim_data_decoded = self.decode_data(s2_dtim_data)
        s2_dtim_error = s2_dtim_did_read & reduce(
            lambda x,y: x | y, 
            list(map(lambda _: _.error(), s2_dtim_data_decoded)))
        s2_dtim_error_correctable = s2_dtim_did_read & reduce(
            lambda x,y: x | y,
            list(map(lambda _: _.correctable, s2_dtim_data_decoded)))
        s2_dtim_error_uncorrectable = s2_dtim_did_read & reduce(
            lambda x,y: x | y, 
            list(map(lambda _: _.uncorrectable, s2_dtim_data_decoded)))
        s2_dtim_corrected = cat(list(reversed(list(map(
            lambda _: _.post_correct, s2_dtim_data_decoded)))))
        s2_dtim_uncorrected = cat(list(reversed(list(map(
            lambda _: _.pre_correct, s2_dtim_data_decoded)))))

        s3_dtim_req = self.io.slave.req.bits.clone('s3_dtim_req').as_reg(
            next = s2_dtim_req)
        s3_dtim_error_correctable = reg_r(
            's3_dtim_error_correctable',
            next = s2_dtim_error_correctable)
        s3_dtim_corrected = reg(
            's3_dtim_corrected',
            w = s2_dtim_corrected.get_w(),
            next = s2_dtim_corrected)


        s0_dtim_valid = (
            self.io.slave.req.fire() | 
            (s2_dtim_partial_ecc_wr & ~s2_dtim_error) | 
            s3_dtim_error_correctable)
        s1_dtim_valid = reg_r('s1_dtim_valid', next = s0_dtim_valid)
        s2_dtim_valid = reg_r('s2_dtim_valid', next = s1_dtim_valid)
        
        s0_slave_fire_valid = self.io.slave.req.fire()
        s1_slave_fire_valid = reg_r('s1_slave_fire_valid', next = s0_slave_fire_valid)
        s2_slave_fire_valid = reg_r('s2_slave_fire_valid', next = s1_slave_fire_valid)

        block_cpu /= s1_hit_dtim & (
            s0_dtim_valid | 
            s1_dtim_valid | 
            s2_dtim_partial_ecc_wr | 
            s2_dtim_error_correctable | 
            s3_dtim_error_correctable)
        s2_replay = s2_slave_fire_valid & s2_dtim_error


        #slave req's ready
        self.io.slave.req.ready /= ~(
            slave_ready_stall_for_cpu | 
            block_slave | 
            s1_dtim_partial_ecc_wr | 
            s2_dtim_partial_ecc_wr | 
            s3_dtim_error_correctable)

        #resp
        self.io.slave.resp.bits.has_data /= s2_dtim_read
        self.io.slave.resp.valid /= (s2_slave_fire_valid & ~s2_dtim_error) | s2_replay
        self.io.slave.resp.bits.data_no_shift /= s2_dtim_uncorrected
        self.io.slave.resp.bits.replay /= s2_replay
        self.io.slave.slow_kill /= 0

        #dtim array access
        slave_data_req = zqh_core_r1_lsu_dtim_data_req('slave_data_req')
        slave_data_req.addr /= self.io.slave.req.bits.addr
        slave_data_req.write /= M_CONSTS.is_write(
            self.io.slave.req.bits.cmd) & ~s0_dtim_needs_read
        slave_data_req.wdata /= self.io.slave.req.bits.data
        slave_data_req.poison /= 0
        slave_data_req.eccMask /= self.ecc_mask(s0_dtim_mask)
        #ecc merge write
        with when(s2_dtim_partial_ecc_wr):
            slave_data_req.addr /= s2_dtim_req.addr
            slave_data_req.write /= 1
            slave_data_req.wdata /= cat_rvs(list(map(
                lambda _ : mux(_[0], _[1], _[2]),
                list(zip(
                    s2_dtim_mask.grouped(1),
                    s2_dtim_req.data.grouped(8), s2_dtim_uncorrected.grouped(8))))))
            slave_data_req.poison /= 0
            slave_data_req.eccMask /= ~value(
                0,
                w = slave_data_req.eccMask.get_w()).to_bits()
        # ecc correct write
        with when(s3_dtim_error_correctable):
            slave_data_req.addr /= s3_dtim_req.addr
            slave_data_req.write /= 1
            slave_data_req.wdata /= s3_dtim_corrected
            slave_data_req.poison /= 0
            slave_data_req.eccMask /= ~value(
                0, w = slave_data_req.eccMask.get_w()).to_bits()

        #
        #dtim_array access
        dtim_array_slave_sel = s0_dtim_valid | s3_dtim_error_correctable
        dtim_array_wmask = mux(
            dtim_array_slave_sel,
            slave_data_req.eccMask,
            cpu_access.bits.eccMask).grouped()
        dtim_array_wwords = self.encode_data(
            mux(
                dtim_array_slave_sel,
                slave_data_req.wdata[self.p.dtim_data_bits-1: 0],
                cpu_access.bits.wdata[self.row_bits()-1: 0]),
            mux(
                dtim_array_slave_sel,
                slave_data_req.poison,
                cpu_access.bits.poison))
        dtim_array_addr = mux(
            dtim_array_slave_sel,
            slave_data_req.addr,
            cpu_access.bits.addr) >> self.p.dtim_data_off_bits
        dtim_array_valid = mux(
            dtim_array_slave_sel,
            1,
            cpu_access.valid & (
                (cpu_access.bits.write & (cpu_access.bits.way_en == 0)) | 
                ~cpu_access.bits.write))
        dtim_array_wen = mux(
            dtim_array_slave_sel, 
            slave_data_req.write, 
            cpu_access.bits.write)
        dtim_array_wdata = dtim_array_wwords.grouped(self.p.data_enc_bits)
        dtim_array.io.en /= dtim_array_valid
        dtim_array.io.wmode /= dtim_array_wen
        dtim_array.io.addr /= dtim_array_addr
        dtim_array.io.wmask /= cat(list(reversed(dtim_array_wmask)))
        dtim_array.io.wdata /= cat_rvs(flatten(list(map(
            lambda _: dtim_array_wdata, range(1)))))
        return (block_cpu, dtim_array.io.rdata)

    def row_bits(self):
        return self.tl_out.a.bits.p.data_bits

    def row_bytes(self):
        return self.row_bits()//8
    
    def row_off_bits(self):
        return log2_up(self.row_bytes())
    
    def row_words(self):
        return self.row_bits()//self.p.word_bits
    
    def cache_block_beats(self):
        return (self.p.cache_block_size * 8) // self.row_bits()
    
    def beat_off_bits(self):
        return log2_up(self.row_bits() // 8)

    def xcpt_check(self, a):
        xcpt = zqh_core_common_lsu_exceptions(init = 0)

        is_read = M_CONSTS.is_read(a.cmd)
        is_write = M_CONSTS.is_write(a.cmd)

        xcpt.ae.ld /= a.error & is_read
        xcpt.ae.st /= a.error & is_write

        size = a.type[log2_up(log2_up(self.p.word_bytes) + 1) - 1: 0]
        ma = reduce(
            lambda a,b: a|b,
            map(
                lambda _: 0 if (_ == 0) else ((a.addr[_ - 1 : 0] != 0) & (size == _)),
                range(log2_up(self.p.word_bytes) + 1)))
        xcpt.ma.ld /= ma & is_read
        xcpt.ma.st /= ma & is_write

        return xcpt
