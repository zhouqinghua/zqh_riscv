import sys
import os
from phgl_imp import *
from .zqh_core_common_misc import IFU_CONSTS
from .zqh_core_common_misc import M_CONSTS
from .zqh_core_common_ifu_parameters import zqh_core_common_ifu_parameter
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_icache_io
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_slave_io
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module

class zqh_core_common_ifu_icache_itim(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_common_ifu_icache_itim, self).set_par()
        self.p = zqh_core_common_ifu_parameter()

    def gen_node_tree(self):
        super(zqh_core_common_ifu_icache_itim, self).gen_node_tree()
        self.gen_node_master(
            'icache_master',
            size_min = 0,
            size_max = 64,
            bundle_p = self.p.gen_tl_bundle_p(),
            source_id_num = 1)

    def set_port(self):
        super(zqh_core_common_ifu_icache_itim, self).set_port()
        self.io.var(zqh_core_common_ifu_icache_io('fetch'))
        if (self.p.itim_size != 0):
            vmacro('USE_ITIM')
            self.io.var(zqh_core_common_ifu_slave_io('slave'))

    def main(self):
        super(zqh_core_common_ifu_icache_itim, self).main()
        self.gen_node_interface('icache_master')
        assert(self.tl_out.a.bits.p.data_bits >= self.p.inst_bits)

        tag_ecc_code = ecc_code(self.p.tag_ecc)
        data_ecc_code = ecc_code(self.p.data_ecc)

        tag_valid_bits = vec(
            'tag_valid_bits',
            gen = lambda _: reg_r(_, w = self.p.num_ways),
            n = self.p.num_sets)

        tag_array = reg_array(
            'tag_array', 
            size = self.p.num_sets,
            #msb is tilelink error bit
            data_width = tag_ecc_code.width(self.p.tag_bits + 1) * self.p.num_ways,
            mask_width = self.p.num_ways)

        data_array = reg_array(
            'data_array',
            size = self.p.num_sets * (self.p.cache_block_size//self.row_bytes()),
            data_width = (data_ecc_code.width(self.p.inst_bits) * 
                (self.row_bits()//self.p.inst_bits)) * self.p.num_ways,
            mask_width = self.p.num_ways)


        s1_flush = bits('s1_flush', init = 0)

        uncache_invalid_s1 = bits('uncache_invalid_s1')
        uncache_invalid_s2 = bits('uncache_invalid_s2')
        uncache_invalid_last = (
            uncache_invalid_s1 
            if (self.p.mem_latency < 2) else uncache_invalid_s2)

        tag_error_invalid_s1 = bits('tag_error_invalid_s1')
        tag_error_invalid_s2 = bits('tag_error_invalid_s2')
        tag_error_invalid_last = (
            tag_error_invalid_s1 
            if (self.p.mem_latency < 2) else tag_error_invalid_s2)

        data_error_invalid_s1 = bits('data_error_invalid_s1')
        data_error_invalid_s2 = bits('data_error_invalid_s2')
        data_error_invalid_last = (
            data_error_invalid_s1 
            if (self.p.mem_latency < 2) else data_error_invalid_s2)


        ####
        #refill request pending info buffer
        pending_flags = vec(
            'pending_flags',
            gen = reg_r,
            n = self.p.num_flights)
        pending_reqs_addr = vec(
            'pending_reqs_addr',
            gen = lambda _: reg(_, w = self.p.max_addr_bits),
            n = self.p.num_flights)
        pending_reqs_way = vec(
            'pending_reqs_way',
            gen = lambda _: reg(_, w = self.p.num_ways),
            n = self.p.num_flights)
        pending_full = pending_flags.pack().r_and()
        pending_none_empty = pending_flags.pack().r_or()


        ####
        #flush all cache line
        req_cmd_flush = (
            self.io.fetch.req.fire() & 
            (self.io.fetch.req.bits.cmd == IFU_CONSTS.FLUSH()))
        flush_flag = reg_r('flush_flag')
        with when(req_cmd_flush):
            flush_flag /= 1
        with when(flush_flag & ~pending_none_empty):
            flush_flag /= 0

        req_ready = (
            ~self.tl_out.d.fire() &
            ~uncache_invalid_last &
            ~tag_error_invalid_last &
            ~data_error_invalid_last)
        self.io.fetch.req.ready /= req_ready

        ####
        #pipeline valid and fetch address
        if (self.p.itim_size != 0):
            slave_req = ready_valid(
                'slave_req',
                gen = type(self.io.slave.req.bits),
                p = self.io.slave.req.bits.p).as_bits()
            slave_req.valid /= self.io.slave.req.valid
            slave_req.bits /= self.io.slave.req.bits
            self.io.slave.req.ready /= slave_req.ready
        slave_fire = slave_req.fire() if (self.p.itim_size != 0) else 0

        valid_s0 = self.io.fetch.req.fire() | slave_fire
        valid_s1 = reg_r(next = valid_s0) & ~s1_flush & ~self.tl_out.d.fire()
        valid_s2 = reg_r('valid_s2', next = valid_s1)
        valid_last = valid_s1 if (self.p.mem_latency < 2) else valid_s2

        is_slave_req_s0 = slave_fire
        is_slave_req_s1 = reg_r('is_slave_req_s1', next = is_slave_req_s0)
        is_slave_req_s2 = reg_r('is_slave_req_s2', next = is_slave_req_s1)
        is_slave_req_last = (
            is_slave_req_s1 if (self.p.mem_latency < 2) else is_slave_req_s2)

        is_slave_rd_s0 = (
            M_CONSTS.is_read(slave_req.bits.cmd) if (self.p.itim_size != 0) else 0)
        is_slave_rd_s1 = reg('is_slave_rd_s1', next = is_slave_rd_s0) 
        is_slave_rd_s2 = reg('is_slave_rd_s2', next = is_slave_rd_s1) 
        is_slave_rd_last = is_slave_rd_s1 if (self.p.mem_latency < 2) else is_slave_rd_s2

        is_slave_wr_s0 = (
            M_CONSTS.is_write(slave_req.bits.cmd) if (self.p.itim_size != 0) else 0)
        is_slave_wr_s1 = reg('is_slave_wr_s1', next = is_slave_wr_s0) 
        is_slave_wr_s2 = reg('is_slave_wr_s2', next = is_slave_wr_s1) 
        is_slave_wr_last = (
            is_slave_wr_s1 if (self.p.mem_latency < 2) else is_slave_wr_s2)

        is_itim_ecc_correct_s0 = bits('is_itim_ecc_correct_s0', init = 0)
        is_itim_ecc_correct_s1 = reg('is_itim_ecc_correct_s1', next = is_itim_ecc_correct_s0)
        is_itim_ecc_correct_s2 = reg('is_itim_ecc_correct_s2', next = is_itim_ecc_correct_s1)
        is_itim_ecc_correct_last = (
            is_itim_ecc_correct_s1 if (self.p.mem_latency < 2) else is_itim_ecc_correct_s2)

        addr_s0 = mux(
            is_slave_req_s0,
            slave_req.bits.addr if (self.p.itim_size != 0) else 0,
            self.io.fetch.req.bits.vaddr)
        addr_s1 = reg('addr_s1', w = self.p.max_addr_bits, next = addr_s0)
        addr_s2 = reg('addr_s2', w = self.p.max_addr_bits, next = addr_s1)
        addr_last = addr_s1 if (self.p.mem_latency < 2) else addr_s2 

        req_error_s0 = mux( is_slave_req_s0, 0, self.io.fetch.req.bits.error)
        req_error_s1 = reg('req_error_s1', next = req_error_s0)
        req_error_s2 = reg('req_error_s2', next = req_error_s1)
        req_error_last = req_error_s1 if (self.p.mem_latency < 2) else req_error_s2 

        addr_idx_s0 = addr_s0[self.p.idx_bits - 1 : 0]
        addr_idx_s1 = addr_s1[self.p.idx_bits - 1 : 0]
        addr_idx_s2 = addr_s2[self.p.idx_bits - 1 : 0]

        addr_line_s0 = addr_idx_s0 >> self.p.line_off_bits
        addr_line_s1 = addr_idx_s1 >> self.p.line_off_bits
        addr_line_s2 = addr_idx_s2 >> self.p.line_off_bits
        addr_line_last = addr_line_s1  if (self.p.mem_latency < 2) else addr_line_s2

        addr_tag_s1 = addr_s1[addr_s1.get_w() - 1 : self.p.idx_bits]

        addr_cacheable_s0 = bits(
            'addr_cacheable_s0',
            init = self.interface_out.manager.address_attr_check(
                addr_s0,
                lambda _: _.cacheable()))
        addr_cacheable_s1 = reg('addr_cacheable_s1', next = addr_cacheable_s0)
        addr_cacheable_s2 = reg('addr_cacheable_s2', next = addr_cacheable_s1)


        ####
        #tile link d response
        (d_first, d_last, d_done, refill_cnt) = self.interface_out.count(self.tl_out.d)
        d_req_addr = sel_bin(self.tl_out.d.bits.source, pending_reqs_addr)
        d_req_way = sel_bin(self.tl_out.d.bits.source, pending_reqs_way)
        d_req_addr_tag = d_req_addr[d_req_addr.get_w() - 1 : self.p.idx_bits]
        d_req_addr_idx = d_req_addr[self.p.idx_bits - 1 : 0]
        d_req_addr_line = d_req_addr_idx >> self.p.line_off_bits
        d_req_addr_data_base = (
            d_req_addr_line << log2_ceil(self.p.cache_block_size//self.row_bytes()))
        with when (self.tl_out.d.fire() & d_last):
            pending_flags(self.tl_out.d.bits.source, 0)


        ####
        #cache tag_array access control
        tag_array_ren = valid_s0
        tag_array_wen = self.tl_out.d.fire() & d_last
        tag_array_addr = mux(tag_array_wen, d_req_addr_line, addr_line_s0)
        tag_array_wmask = d_req_way
        tag_array_wdata = tag_ecc_code.encode(
            cat([self.tl_out.d.bits.error, d_req_addr_tag])).rep(self.p.num_ways)

        tag_array.io.en /= tag_array_ren | tag_array_wen
        tag_array.io.wmode /= tag_array_wen
        tag_array.io.addr /= tag_array_addr
        tag_array.io.wmask /= tag_array_wmask
        tag_array.io.wdata /= tag_array_wdata

        tag_array_rdata_grp = tag_array.io.rdata.grouped(
            tag_ecc_code.width(self.p.tag_bits + 1))
        tag_array_rdata_grp_decode = map(
            lambda _: tag_ecc_code.decode(_),
            tag_array_rdata_grp)

        tag_valid_s0 = cat([1, tag_valid_bits[tag_array_addr]])
        tag_valid_s1 = reg(
            w = self.p.num_ways + 1,
            next = tag_valid_s0) & ~flush_flag.rep(self.p.num_ways + 1)
        tag_valid_s2 = reg(
            'tag_valid_s2',
            w = self.p.num_ways + 1,
            next = tag_valid_s1) & ~flush_flag.rep(self.p.num_ways + 1)

        tag_match_itim_s1 = (
            0 
            if (self.p.itim_size == 0) else (
                (addr_s1 >= self.p.itim_base) & 
                (addr_s1 < (self.p.itim_base + self.p.itim_size))))

        tag_cmp_s1 = (
            tag_valid_s1 &
            cat([
                tag_match_itim_s1,
                cat_rvs(map(
                    lambda _: _[self.p.tag_bits - 1 : 0] == addr_tag_s1,
                    tag_array_rdata_grp))]))
        tag_cmp_s2 = reg('tag_cmp_s2', w = self.p.num_ways + 1, next = tag_cmp_s1)
        tag_cmp_last = tag_cmp_s1 if (self.p.mem_latency < 2) else tag_cmp_s2

        tag_tl_error_s1 = tag_valid_s1 & cat([
            0,
            cat_rvs(map(lambda _: _[self.p.tag_bits], tag_array_rdata_grp))])
        tag_tl_error_s2 = reg(
            'tag_tl_error_s2',
            w = self.p.num_ways + 1,
            next = tag_tl_error_s1)

        tag_error_s1 = (
            tag_valid_s1 & 
            cat([
                0, 
                cat_rvs(map(lambda _: _.error(), tag_array_rdata_grp_decode))]))
        tag_error_s2 = reg('tag_error_s2', w = self.p.num_ways + 1, next = tag_error_s1)

        tag_error_any_s1 = tag_error_s1.r_or()
        tag_error_any_s2 = tag_error_s2.r_or()

        tag_hit_any_s1 = tag_cmp_s1.r_or() & ~tag_error_any_s1
        tag_hit_any_s2 = tag_cmp_s2.r_or() & ~tag_error_any_s2

        tl_error_s1 = tag_tl_error_s1.r_or()
        tl_error_s2 = tag_tl_error_s2.r_or()
        tl_error_last = tl_error_s1 if (self.p.mem_latency < 2) else tl_error_s2

        miss_s1 = valid_s1 & ~tag_hit_any_s1
        miss_s2 = valid_s2 & ~tag_hit_any_s2
        miss_last = miss_s1 if (self.p.mem_latency < 2) else miss_s2

        tag_error_invalid_s1 /= valid_s1 & tag_error_any_s1
        tag_error_invalid_s2 /= valid_s2 & tag_error_any_s2


        ####
        #tag_valid_bits set or clear
        #dtim hit's data ecc error no need clean tag_bits
        with when(
            (self.tl_out.d.fire() & (d_first | d_last)) |
            uncache_invalid_last |
            tag_error_invalid_last |
            (data_error_invalid_last & ~tag_cmp_last[self.p.num_ways])):
            flush_mask = ~flush_flag.rep(self.p.num_ways)
            addr = mux(
                uncache_invalid_last | tag_error_invalid_last | data_error_invalid_last,
                addr_line_last,
                tag_array_addr)
            for i in range(self.p.num_sets):
                vb_d_last = tag_valid_bits[i] | d_req_way
                vb_d_first = tag_valid_bits[i] & ~d_req_way
                vb_d = mux(d_last, vb_d_last, vb_d_first)
                with when(addr == i):
                    #tag/data ecc error will invalid all way's valid bit
                    with when(tag_error_invalid_last | data_error_invalid_last):
                        tag_valid_bits[i] /= 0
                    with other():
                        tag_valid_bits[i] /= mux(uncache_invalid_last, 0, vb_d) & flush_mask
        with when(req_cmd_flush):
            tag_valid_bits /= 0


        ####
        #cache data_array control
        data_array_wen = self.tl_out.d.fire()
        data_array_addr = mux(
            self.tl_out.d.fire(),
            d_req_addr_data_base | refill_cnt,
            addr_s0 >> self.row_off_bits())
        data_array_wmask = d_req_way
        data_array_wdata = cat_rvs(
            map(
                lambda _: data_ecc_code.encode(_),
                self.tl_out.d.bits.data.grouped(self.p.inst_bits))).rep(self.p.num_ways)

        data_array.io.en /= valid_s0 | data_array_wen
        data_array.io.wmode /= data_array_wen
        data_array.io.addr /= data_array_addr
        data_array.io.wmask /= data_array_wmask
        data_array.io.wdata /= data_array_wdata

        #itim_data_array control
        if (self.p.itim_size != 0):
            vmacro('ITIM_SIZE', self.p.itim_size)
            itim_array = reg_array(
                'itim_array',
                size = self.p.itim_size//self.row_bytes(),
                data_width = data_ecc_code.width(
                    self.p.inst_bits) * (self.row_bits()//self.p.inst_bits),
                mask_width = 1
                )

            itim_array_wen = valid_s0 & is_slave_req_s0 & is_slave_wr_s0
            itim_array_addr = addr_s0 >> self.row_off_bits()
            itim_array_wdata = cat_rvs(
                map(
                    lambda _: data_ecc_code.encode(_),
                    slave_req.bits.data.grouped(self.p.inst_bits))).rep(self.p.num_ways)

            itim_array.io.en /= valid_s0
            itim_array.io.wmode /= itim_array_wen
            itim_array.io.addr /= itim_array_addr
            itim_array.io.wmask /= 1
            itim_array.io.wdata /= itim_array_wdata

        rdata_sel_s1 = sel_oh(
            tag_cmp_s1,
            data_array.io.rdata.grouped(
                data_ecc_code.width(self.p.inst_bits) * 
                (self.row_bits()//self.p.inst_bits)) + [
                    itim_array.io.rdata if (self.p.itim_size != 0) else 0])
        rdata_sel_s2 = reg('rdata_sel_s2', w = rdata_sel_s1.get_w(), next = rdata_sel_s1)
        rdata_sel_last = rdata_sel_s1 if (self.p.mem_latency < 2) else rdata_sel_s2

        rdata_inst_sel_s1 = sel_bin(
            addr_s1[self.row_off_bits() - 1 : self.p.inst_off_bits],
            rdata_sel_s1.grouped(data_ecc_code.width(self.p.inst_bits)))
        rdata_inst_sel_s2 = reg(
            'rdata_inst_sel_s2',
            w = rdata_inst_sel_s1.get_w(),
            next = rdata_inst_sel_s1)
        rdata_inst_sel_last = (rdata_inst_sel_s1
            if (self.p.mem_latency < 2) else rdata_inst_sel_s2)

        data_decode = data_ecc_code.decode(rdata_inst_sel_s1)

        data_error_s1 = (
            tag_cmp_s1.r_or() & 
            data_decode.error() & 
            (~is_slave_req_s1 | is_slave_rd_s1))
        data_error_s2 = reg('data_error_s2', next = data_error_s1)
        data_error_last = data_error_s1 if (self.p.mem_latency < 2) else data_error_s2

        data_error_correctable_s1 = (
            tag_cmp_s1.r_or() & 
            data_decode.correctable & 
            (~is_slave_req_s1 | is_slave_rd_s1))
        data_error_correctable_s2 = reg(
            'data_error_correctable_s2',
            next = data_error_correctable_s1)
        data_error_correctable_last = (
            data_error_correctable_s1 
            if (self.p.mem_latency < 2) else data_error_correctable_s2)

        data_error_invalid_s1 /= valid_s1 & data_error_s1
        data_error_invalid_s2 /= valid_s2 & data_error_s2

        hit_s1 = valid_s1 & tag_hit_any_s1 & ~data_error_s1
        hit_s2 = valid_s2 & tag_hit_any_s2 & ~data_error_s2
        hit_last = hit_s1 if (self.p.mem_latency < 2) else hit_s2


        ####
        #uncacheable fetch need invalid this cache line after hit access
        uncache_invalid_s1 /= hit_s1 & ~addr_cacheable_s1 & self.p.uc_invalid_en
        uncache_invalid_s2 /= hit_s2 & ~addr_cacheable_s2 & self.p.uc_invalid_en

        s1_flush /= 0 \
            if (self.p.mem_latency < 2) else (
                (self.io.fetch.s1_kill & ~is_slave_req_s1) |
                tag_error_invalid_last |
                data_error_invalid_last |
                miss_last)

        ####
        #tile link a channel cache refill request
        a_source = pri_lsb_enc(~pending_flags.pack())
        a_refill_way = bin2oh(
            lfsr16(increment = self.tl_out.a.fire())
            [log2_up(self.p.num_ways)-1:0]) if (self.p.num_ways > 1) else 1
        with when (self.tl_out.a.fire()):
            pending_flags(a_source, 1)
            pending_reqs_addr(a_source, addr_s2)
            pending_reqs_way(a_source, a_refill_way)
        a_address = (addr_s2 >> self.p.line_off_bits) << self.p.line_off_bits
        a_size = log2_ceil(self.p.cache_block_size)
        a_get = self.interface_out.get(a_source, a_address, a_size)[1]

        self.tl_out.a.valid /= 0
        with when(miss_s2 & ~pending_full & ~flush_flag):
            self.tl_out.a.valid /= 1
        self.tl_out.a.bits /= a_get


        ####
        #blocking d.ready if following condition happen
        self.tl_out.d.ready /= \
            ~uncache_invalid_last & \
            ~tag_error_invalid_last & \
            ~data_error_invalid_last

        
        ####
        #response to ifu when cache hit
        self.io.fetch.resp.valid /= hit_last & ~is_slave_req_last
        self.io.fetch.resp.bits.inst /= rdata_inst_sel_last[self.p.inst_bits - 1 : 0]
        self.io.fetch.resp.bits.pc /= addr_last
        self.io.fetch.resp.bits.xcpt /= tl_error_last | req_error_last

        self.io.fetch.valid_s1 /= valid_s1

        

        if (self.p.itim_size != 0):
            slave_req.ready /= req_ready
            with when(slave_req.valid):
                #slave rw access has higher priority than fetch
                self.io.fetch.req.ready /= 0

            #response to ifu_slave
            self.io.slave.resp.valid /= is_slave_req_last & ~is_itim_ecc_correct_last
            self.io.slave.resp.bits.replay /= is_slave_req_last & ~hit_last
            self.io.slave.resp.bits.data /= cat_rvs(map(
                lambda _: _[self.p.inst_bits - 1 : 0],
                rdata_sel_last.grouped(data_ecc_code.width(self.p.inst_bits))))

            
            ####
            #itim memory ecc correction
            itim_ecc_error_1b_s1 = tag_cmp_s1[self.p.num_ways] & data_error_correctable_s1
            itim_ecc_error_1b_s2 = tag_cmp_s2[self.p.num_ways] & data_error_correctable_s2
            itim_ecc_error_1b_last = (
                itim_ecc_error_1b_s1 if (self.p.mem_latency < 2) else itim_ecc_error_1b_s2)

            ecc_correct_req = ready_valid(
                'ecc_correct_req',
                gen = type(self.io.slave.req.bits),
                p = self.io.slave.req.bits.p).as_bits()
            ecc_correct_buf_valid = reg_r('ecc_correct_buf_valid')
            ecc_correct_buf = self.io.slave.req.bits.clone('correct_buf').as_reg()
            with when(valid_last & itim_ecc_error_1b_last):
                ecc_correct_buf_valid /= 1
                ecc_correct_buf.addr /= addr_last
                ecc_correct_buf.cmd /= M_CONSTS.M_XWR()
                ecc_correct_buf.typ /= log2_ceil(self.row_bytes())
                ecc_correct_buf.data /= cat_rvs(map(
                    lambda _: data_ecc_code.decode(_).post_correct,
                    rdata_sel_last.grouped(data_ecc_code.width(self.p.inst_bits))))
                ecc_correct_buf.mask /= bits(init = 1).rep(self.row_bytes())
            with elsewhen(ecc_correct_req.fire()):
                ecc_correct_buf_valid /= 0


            ecc_correct_req.valid /= ecc_correct_buf_valid
            ecc_correct_req.bits /= ecc_correct_buf
            ecc_correct_req.ready /= slave_req.ready
            with when(ecc_correct_req.valid):
                self.io.slave.req.ready /= 0
                slave_req.valid /= 1
                slave_req.bits /= ecc_correct_req.bits
            is_itim_ecc_correct_s0 /= ecc_correct_req.fire()

        ####
        #hpm events
        a_sop_eop = self.tl_out.sop_eop_a()
        self.io.fetch.events.refill /= self.tl_out.a.fire() & a_sop_eop.eop

    def row_bits(self):
        return self.tl_out.a.bits.p.data_bits

    def row_bytes(self):
        return self.row_bits()//8

    def row_off_bits(self):
        return log2_up(self.row_bytes())
