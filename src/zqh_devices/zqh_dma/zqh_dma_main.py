import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_xbar_parameter
from .zqh_dma_parameters import zqh_dma_parameter
from .zqh_dma_bundles import *
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS

class zqh_dma_channel(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_dma_channel, self).set_par()
        self.p = zqh_dma_parameter()

    def gen_node_tree(self):
        super(zqh_dma_channel, self).gen_node_tree()
        self.gen_node_master(
            'channel_master', 
            size_min = 0,
            size_max = 64, 
            bundle_p = self.p.gen_tl_master_bundle_p())

    def check_par(self):
        super(zqh_dma_channel, self).check_par()
        assert(
            self.p.data_buffer_entries >= 
            2**self.p.max_tl_size//self.p.channel_master.bundle_out[0].
            channel['a'].data_bits)

    def set_port(self):
        super(zqh_dma_channel, self).set_port()
        self.io.var(inp('run'))
        self.io.var(inp('rsize', w = 4))
        self.io.var(inp('wsize', w = 4))
        self.io.var(inp('order'))
        self.io.var(inp('bytes', w = 64))
        self.io.var(inp('dest', w = 64))
        self.io.var(inp('source', w = 64))

        self.io.var(outp('cur_remain_bytes', w = 64))
        self.io.var(outp('cur_dest_addr', w = 64))
        self.io.var(outp('cur_source_addr', w = 64))

        self.io.var(outp('done'))
        self.io.var(outp('error'))

    def main(self):
        super(zqh_dma_channel, self).main()
        self.gen_node_interface('channel_master')

        #source id resource management
        tl_addr_lsb_bits = log2_ceil(self.tl_out.d.bits.data.get_w()//8)
        tl_out_a_is_put = self.tl_out.a.bits.opcode.match_any([
            TMSG_CONSTS.put_full_data(),
            TMSG_CONSTS.put_partial_data()])
        tl_out_a_sop_eop = self.tl_out.sop_eop_a()
        tl_out_d_sop_eop = self.tl_out.sop_eop_d()
        tl_source_flags = vec('tl_source_flags', gen = reg_r, n = self.p.num_flights)
        tl_source_free_any = ~reduce(lambda a,b: a & b, list(tl_source_flags))
        tl_source_free_all = ~reduce(lambda a,b: a | b, list(tl_source_flags))
        tl_source = pri_lsb_enc(~cat_rvs(tl_source_flags))

        #source -> addr[lsb] map table
        #if get's size is less than one tilelink beat, need to known the byte mask
        tl_source2addr_map = vec(
            'tl_source2addr_map', 
            gen = reg, 
            n = self.p.num_flights, 
            w = tl_addr_lsb_bits)

        with when(tl_out_a_sop_eop.sop):
            tl_source_flags(self.tl_out.a.bits.source, 1)
            tl_source2addr_map(
                self.tl_out.a.bits.source,
                self.tl_out.a.bits.address[tl_addr_lsb_bits - 1 : 0])
        with when(tl_out_d_sop_eop.eop):
            tl_source_flags(self.tl_out.d.bits.source, 0)
        tl_put_lock = reg_r('tl_put_lock')
        tl_source_reg = reg('tl_source_reg', w = self.tl_out.a.bits.source.get_w())
        with when(tl_out_a_sop_eop.sop & ~tl_out_a_sop_eop.eop & tl_out_a_is_put):
            tl_put_lock /= 1
            tl_source_reg /= tl_source
        with when(tl_out_a_sop_eop.eop):
            tl_put_lock /= 0


        #get data response
        data_buffer = queue(
            'data_buffer',
            gen = lambda _: zqh_dma_data_buffer_entry(
                _,
                data_width = self.tl_out.a.bits.data.get_w(),
                size_width = self.tl_out.a.bits.size.get_w(),
                addr_width = tl_addr_lsb_bits),
            entries = self.p.data_buffer_entries)
        asm_buffer = queue(
            'asm_buffer',
            gen = lambda _: zqh_dma_asm_buffer_entry(
                _,
                data_width = self.tl_out.a.bits.data.get_w()),
            entries = self.p.asm_buffer_entries)


        (s_idle, s_transfer, s_done, s_error) = range(4)
        state = reg_rs('state', w = 3, rs = s_idle)
        get_finish = bits('get_finish', init = 0)
        put_finish = bits('put_finish', init = 0)
        get_error = reg_r('get_error')
        put_error = reg_r('put_error')

        with when(state == s_idle):
            with when(self.io.run):
                state /= s_transfer
        with when(state == s_transfer):
            with when(get_finish & put_finish):
                with when(tl_source_free_all):
                    state /= s_done
        with when(state == s_done):
            state /= s_idle


        #read requet send
        get_byte_cnt = reg_r('get_byte_cnt', w = self.io.bytes.get_w())
        get_order_block = reg_r('get_order_block')
        get_remain_bytes = self.io.bytes - get_byte_cnt
        get_req_bits_source = tl_source
        get_req_bits_addr = self.io.source + get_byte_cnt
        get_req_bits_size = self.gen_tl_out_size(
            self.io.rsize,
            get_req_bits_addr,
            get_byte_cnt,
            get_remain_bytes)
        get_req_bits = self.interface_out.get(
            get_req_bits_source, get_req_bits_addr, get_req_bits_size)[1]
        get_req = ready_valid(
            'get_req', 
            gen = type(self.tl_out.a.bits), 
            p = self.tl_out.a.bits.p).as_bits()

        get_send_valid = bits('get_send_valid', init = 0)
        get_finish /= (get_byte_cnt == self.io.bytes)
        get_req_bytes = (1 << get_req_bits_size)[self.p.max_tl_size : 0]
        get_buffer_credit = reg_rs(
            'get_buffer_credit',
            w = data_buffer.io.count.get_w(),
            rs = self.p.data_buffer_entries)
        get_num_beats = get_req_bits.num_beats(get_req_bits_size, self.p.max_tl_size)
        get_buffer_credit_enough = ~(get_buffer_credit < get_num_beats)
        get_buffer_credit_full = get_buffer_credit == self.p.data_buffer_entries
        get_en = (
            tl_source_free_any & ~get_order_block & get_buffer_credit_enough & ~tl_put_lock)
        with when(state == s_transfer):
            with when(~get_finish):
                with when(get_en):
                    get_send_valid /= 1
        get_req.valid /= get_send_valid
        get_req.bits /= get_req_bits

        with when(state == s_idle):
            with when(self.io.run):
                get_byte_cnt /= 0
                get_error /= 0
        with elsewhen(get_req.fire()):
            get_byte_cnt /= get_byte_cnt + get_req_bytes
            get_order_block /= self.io.order


        get_credit_dec = get_req.fire()
        get_credit_inc = data_buffer.io.deq.fire()
        with when(get_credit_dec & get_credit_inc):
            get_buffer_credit /= get_buffer_credit - (get_num_beats - 1)
        with elsewhen(get_credit_dec):
            get_buffer_credit /= get_buffer_credit - get_num_beats
        with elsewhen(get_credit_inc):
            get_buffer_credit /= get_buffer_credit + 1

        d_resp_has_data = self.tl_out.d.bits.opcode.match_any([
            TMSG_CONSTS.access_ack_data()])
        data_buffer.io.enq.valid /= 0
        self.tl_out.d.ready /= 1
        with when(d_resp_has_data):
            data_buffer.io.enq.valid /= self.tl_out.d.valid
            self.tl_out.d.ready /= data_buffer.io.enq.ready
        data_buffer.io.enq.bits.data /= self.tl_out.d.bits.data
        data_buffer.io.enq.bits.size /= self.tl_out.d.bits.size
        data_buffer.io.enq.bits.addr /= tl_source2addr_map[self.tl_out.d.bits.source]

        with when(tl_out_d_sop_eop.eop & d_resp_has_data):
            get_order_block /= 0


        asm_shift_cnt = reg_r('asm_shift_cnt', w = tl_addr_lsb_bits + 1)
        asm_shift_cnt_v = asm_shift_cnt[tl_addr_lsb_bits - 1 : 0]

        asm_left_data_reg = reg_r(
            'asm_left_data_reg', w = self.tl_out.a.bits.data.get_w())
        asm_left_data_byte_map_reg = reg_r(
            'asm_left_data_byte_map_reg', w = self.tl_out.a.bits.mask.get_w())

        asm_left_data_reg_group = asm_left_data_reg.grouped(8)
        asm_data_pre_shift_group = data_buffer.io.deq.bits.data.grouped(8)
        asm_extend_data_group0 = (
            list(reversed(asm_data_pre_shift_group)) + 
            list(reversed(asm_left_data_reg_group)))
        asm_extend_data_group1 = (
            list(reversed(asm_left_data_reg_group)) + 
            list(reversed(asm_data_pre_shift_group)))

        asm_left_data_byte_map_reg_group = asm_left_data_byte_map_reg.grouped()
        asm_data_byte_map_pre_shift_group = mask_gen(
            data_buffer.io.deq.bits.addr,
            data_buffer.io.deq.bits.size,
            self.tl_out.a.bits.data.get_w()//8).grouped()
        asm_extend_data_byte_map_group0 = (
            list(reversed(asm_data_byte_map_pre_shift_group)) + 
            list([0]*self.tl_out.a.bits.mask.get_w()))
        asm_extend_data_byte_map_group1 = (
            list([0]*self.tl_out.a.bits.mask.get_w()) + 
            list(reversed(asm_data_byte_map_pre_shift_group)))

        asm_data_post_shift_group = list(map(
            lambda _: mux(
                asm_left_data_byte_map_reg[_],
                asm_left_data_reg_group[_],
                sel_bin(
                    asm_shift_cnt_v,
                    asm_extend_data_group0[7 - _: 15 - _])),
            range(self.tl_out.a.bits.mask.get_w())))
        asm_left_data_reg_next_group = list(map(
            lambda _: sel_bin(
                asm_shift_cnt_v,
                asm_extend_data_group1[7 - _: 15 - _]),
            range(self.tl_out.a.bits.mask.get_w())))
        asm_data_byte_map_group = list(map(
            lambda _: sel_bin(
                asm_shift_cnt_v,
                asm_extend_data_byte_map_group0[7 - _: 15 - _]),
            range(self.tl_out.a.bits.mask.get_w())))
        asm_left_data_byte_map_reg_next_group = list(map(
            lambda _: sel_bin(
                asm_shift_cnt_v,
                asm_extend_data_byte_map_group1[7 - _: 15 - _]),
            range(self.tl_out.a.bits.mask.get_w())))

        asm_tail = bits(
            'asm_tail', 
            init = get_finish & get_buffer_credit_full & (asm_left_data_byte_map_reg != 0))
        asm_done = bits(
            'asm_done', 
            init = get_finish & get_buffer_credit_full & (asm_left_data_byte_map_reg == 0))

        asm_data_post_shift = cat_rvs(asm_data_post_shift_group)
        asm_mask_post_shift = mux(
            asm_tail,
            asm_left_data_byte_map_reg,
            cat_rvs(asm_data_byte_map_group) | asm_left_data_byte_map_reg)

        asm_buffer_enq_req = ready_valid(
            'asm_buffer_enq_req',
            gen = zqh_dma_asm_buffer_entry,
            data_width = self.tl_out.a.bits.data.get_w()).as_bits()

        with when(asm_buffer_enq_req.fire()):
            with when(asm_tail):
                asm_left_data_byte_map_reg /= 0
            with other():
                asm_left_data_byte_map_reg /= cat_rvs(asm_left_data_byte_map_reg_next_group)
            asm_left_data_reg /= cat_rvs(asm_left_data_reg_next_group)
        with elsewhen((state == s_idle) & self.io.run):
            asm_left_data_byte_map_reg /= 0
            asm_shift_cnt /= (
                self.io.dest[tl_addr_lsb_bits - 1 : 0] - 
                self.io.source[tl_addr_lsb_bits - 1 : 0])


        asm_buffer_enq_req.bits.data /= asm_data_post_shift
        asm_buffer_enq_req.bits.mask /= asm_mask_post_shift
        asm_buffer_enq_req.valid /= data_buffer.io.deq.valid | asm_tail
        data_buffer.io.deq.ready /= asm_buffer_enq_req.ready
        self.asm_buffer_enq_filter(asm_buffer_enq_req, asm_buffer.io.enq, asm_tail, asm_done)


        #put requet send
        put_byte_cnt = reg_r('put_byte_cnt', w = self.io.bytes.get_w())
        put_order_block = reg_r('put_order_block')
        put_remain_bytes = self.io.bytes - put_byte_cnt
        put_req_bits_source = mux(tl_put_lock, tl_source_reg, tl_source)
        put_req_bits_addr = self.io.dest + put_byte_cnt
        put_req_bits_size = self.gen_tl_out_size(
            self.io.wsize,
            put_req_bits_addr,
            put_byte_cnt,
            put_remain_bytes)
        put_req_bits_data = asm_buffer.io.deq.bits.data
        put_req_bits = self.interface_out.put(
            put_req_bits_source,
            put_req_bits_addr,
            put_req_bits_size,
            put_req_bits_data)[1]
        put_req = ready_valid(
            'put_req', 
            gen = type(self.tl_out.a.bits),
            p = self.tl_out.a.bits.p).as_bits()

        put_send_valid = bits('put_send_valid', init = 0)
        put_finish /= (put_byte_cnt == self.io.bytes)
        put_req_bytes = (1 << put_req_bits_size)[self.p.max_tl_size : 0]


        put_req_beat_byte_map_reg = reg_r(
            'put_req_beat_byte_map_reg',
            w = self.tl_out.a.bits.mask.get_w())
        put_req_beat_byte_map_reg_next = put_req_bits.mask | put_req_beat_byte_map_reg
        asm_buffer_beat_done = (
            (asm_buffer.io.deq.bits.mask & ~put_req_beat_byte_map_reg_next) == 0)
        with when(put_req.fire() & self.tl_out.a.fire()):
            with when(asm_buffer_beat_done):
                put_req_beat_byte_map_reg /= 0
            with other():
                put_req_beat_byte_map_reg /= put_req_beat_byte_map_reg_next
        with elsewhen((state == s_idle) & self.io.run):
            put_req_beat_byte_map_reg /= (1 << self.io.dest[tl_addr_lsb_bits - 1 : 0]) - 1

        
        asm_buffer.io.deq.ready /= 0
        put_num_beats = put_req_bits.num_beats(put_req_bits_size, self.p.max_tl_size)
        put_data_enough = ~(asm_buffer.io.count < put_num_beats)
        put_en = (tl_source_free_any & ~put_order_block & put_data_enough) | tl_put_lock
        with when(state == s_transfer):
            with when(~put_finish):
                with when(put_en):
                    put_send_valid /= asm_buffer.io.deq.valid
                    asm_buffer.io.deq.ready /= put_req.ready & asm_buffer_beat_done
        put_req.valid /= put_send_valid
        put_req.bits /= put_req_bits

        with when(state == s_idle):
            with when(self.io.run):
                put_byte_cnt /= 0
                put_error /= 0
        with elsewhen(put_req.fire()):
            with when(tl_out_a_sop_eop.eop):
                put_byte_cnt /= put_byte_cnt + put_req_bytes

            with when(tl_out_a_sop_eop.sop):
                put_order_block /= self.io.order

        with when(tl_out_d_sop_eop.eop & ~d_resp_has_data):
            put_order_block /= 0


        tl_out_arb = sp_arbiter(
            'tl_out_arb', 
            gen = type(self.tl_out.a.bits), 
            gen_p = self.tl_out.a.bits.p, 
            n = 2)
        self.tl_out.a /= tl_out_arb.io.out
        tl_out_arb.io.input[1] /= put_req
        tl_out_arb.io.input[0] /= get_req

        #set error flag
        with when(self.tl_out.d.fire()):
            with when(self.tl_out.d.bits.error):
                with when(d_resp_has_data):
                    get_error /= 1
                with other():
                    put_error /= 1


        self.io.cur_remain_bytes /= put_remain_bytes
        self.io.cur_dest_addr /= put_req_bits_addr
        self.io.cur_source_addr /= get_req_bits_addr

        self.io.done /= 0
        self.io.error /= 0
        with when(state == s_done):
            self.io.done /= 1
            self.io.error /= get_error | put_error

    #dma read/write's first fews request's size need change to fix address's boundary
    #dma read/write's last fews request's size need change to fix the tail bounday
    def gen_tl_out_size(self, exec_xsize, addr, byte_cnt, remain_bytes):
        head_fix = sel_p_lsb(
            addr[self.p.max_tl_size:0],
            range(self.p.max_tl_size + 1),
            self.p.max_tl_size)
        xsize = mux(head_fix < exec_xsize, head_fix, exec_xsize)

        xsize_bytes = (1 << xsize)[self.p.max_tl_size : 0]
        remain_bytes_none_full = remain_bytes < xsize_bytes
        tail_fix = list(map(
            lambda _: (_ < xsize) & remain_bytes[_],
            range(self.p.max_tl_size - 1, -1, -1)))
        tail_xsize = sel_p_lsb(tail_fix, list(reversed(list(range(self.p.max_tl_size)))))

        tl_size = mux(remain_bytes_none_full, tail_xsize, xsize)
        return tl_size
    
    def asm_buffer_enq_filter(self, pre_req, post_req, tail, done):
        partial_mask_reg = reg_r('partial_mask_reg', w = pre_req.bits.mask.get_w())
        partial_data_reg = reg('partial_data_reg', w = pre_req.bits.data.get_w())
        partial_data_reg_group = partial_data_reg.grouped(8)
        pre_req_data_group = pre_req.bits.data.grouped(8)

        dummy = pre_req.bits.mask == 0
        merged_mask = pre_req.bits.mask | partial_mask_reg
        mask_full = merged_mask.msb() | tail
        merged_data = cat_rvs(map(
            lambda _: mux(
                partial_mask_reg[_],
                partial_data_reg_group[_],
                pre_req_data_group[_]),
            range(pre_req.bits.mask.get_w())))

        with when(pre_req.fire()):
            with when(~mask_full):
                partial_mask_reg /= merged_mask
                partial_data_reg /= merged_data
            with other():
                partial_mask_reg /= 0
        with elsewhen(done):
            with when(post_req.fire()):
                partial_mask_reg /= 0
        
        pre_req.ready /= ~mask_full | dummy | post_req.ready

        post_req.valid /= mux(
            done,
            partial_mask_reg != 0, 
            (pre_req.valid & mask_full) & ~dummy)
        post_req.bits /= pre_req.bits
        post_req.bits.mask /= mux(done, partial_mask_reg, merged_mask)
        post_req.bits.data /= merged_data

class zqh_dma(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_dma, self).set_par()
        self.p = zqh_dma_parameter()

    def gen_node_tree(self):
        super(zqh_dma, self).gen_node_tree()
        self.gen_node_slave('dma_slave', bundle_p = self.p.gen_tl_slave_bundle_p())

        self.p.par(
            'dma_channel_masters', 
            list(map(
                lambda _: self.p.par(
                    'dma_channel_master_'+str(_), 
                    zqh_tilelink_node_master_parameter('dma_channel_master_'+str(_))),
                range(self.p.num_channels))))
        self.p.par('dma_master', zqh_tilelink_node_slave_io_parameter('dma_master'))
        self.p.par('out_bus', zqh_tilelink_node_xbar_parameter('out_bus', do_imp = 1))
        for i in range(self.p.num_channels):
            self.p.out_bus.push_up(self.p.dma_channel_masters[i])
        self.p.out_bus.push_down(self.p.dma_master)
        if (len(self.p.extern_masters) > 0):
            self.p.dma_master.push_down(self.p.extern_masters[0])

        self.p.dma_slave.print_up()
        self.p.dma_slave.print_address_space()

    def check_par(self):
        super(zqh_dma, self).check_par()

    def set_port(self):
        super(zqh_dma, self).set_port()

    def main(self):
        super(zqh_dma, self).main()

        #{{{
        def func_reg_write(
            reg_ptr,
            fire,
            address,
            size, 
            wdata,
            mask_bit,
            wr_valid = None, 
            wr_data = None):
            with when(fire):
                wr_valid /= 1
            wr_data /= wdata
            return (1, 1)
        def func_reg_read(
            reg_ptr, 
            fire, 
            address,
            size, 
            mask_bit, 
            rd_valid = None,
            rd_data = None):
            with when(fire):
                rd_valid /= 1
            return (1, 1, rd_data.pack())
        def wr_process_gen(wr_valid, wr_data):
            return lambda a0, a1, a2, a3, a4, a5: func_reg_write(
                a0, a1, a2, a3, a4, a5, wr_valid, wr_data)
        def rd_process_gen(rd_valid, rd_data):
            return lambda a0, a1, a2, a3, a4: func_reg_read(
                a0, a1, a2, a3, a4, rd_valid, rd_data)
        
        exec_bytes_rd_data = vec(
            'exec_bytes_rd_data',
            gen = bits, 
            n = self.p.num_channels,
            w = 64)
        exec_dest_rd_data = vec(
            'exec_dest_rd_data',
            gen = bits, 
            n = self.p.num_channels,
            w = 64)
        exec_source_rd_data = vec(
            'exec_source_rd_data', 
            gen = bits, 
            n = self.p.num_channels, 
            w = 64)
        run_posedge = vec(
            'run_posedge',
            gen = bits, 
            n = self.p.num_channels)
        run_posedge_dly = vec(
            'run_posedge_dly', 
            gen = lambda _: reg_r(_, next = run_posedge[_]),
            n = self.p.num_channels)
        run_repeat = vec(
            'run_repeat', 
            gen = bits, 
            n = self.p.num_channels)
        run_repeat_dly = vec(
            'run_repeat_dly', 
            gen = lambda _: reg_r(_, next = run_repeat[_]),
            n = self.p.num_channels)
        dma_channel_run = vec(
            'dma_channel_run', 
            gen = lambda _: bits(_, init = run_posedge_dly[_] | run_repeat_dly[_]),
            n = self.p.num_channels)
        dma_channel_done = vec(
            'dma_channel_done',
            gen = bits, 
            n = self.p.num_channels)
        for i in range(self.p.num_channels):
            suffix_str = '_'+str(i)
            offset_base = 0x1000 * i
            run_wr_valid = bits('run_wr_valid'+suffix_str, init = 0)
            run_wr_data = bits('run_wr_data'+suffix_str, init = 0)
            claim_wr_valid = bits('claim_wr_valid'+suffix_str, init = 0)
            claim_wr_data = bits('claim_wr_data'+suffix_str, init = 0)
            self.cfg_reg(csr_reg_group(
                'control'+suffix_str, 
                offset = 0x000 + offset_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('error', width = 1, reset = 0, comments = '''\
Indicates that a transfer error has occured since the channel was claimed.'''),
                    csr_reg_field_desc('done', width = 1, reset = 0, comments = '''\
Indicates that a transfer has completed since the channel was claimed.'''),
                    csr_reg_field_desc('reserved0', access = 'VOL', width = 2),
                    csr_reg_field_desc('error_ie', width = 1, reset = 0, comments = '''\
Setting this bit will trigger the channel’s Error interrupt upon receiving a bus error.'''),
                    csr_reg_field_desc('done_ie', width = 1, reset = 0, comments = '''\
Setting this bit will trigger the channel’s Done interrupt once a transfer is complete.'''),
                    csr_reg_field_desc('reserved1', access = 'VOL', width = 24),
                    csr_reg_field_desc('run', width = 1, reset = 0, write = wr_process_gen(run_wr_valid, run_wr_data), comments = '''\
Setting this bit starts a DMA transfer by copying the Next registers into their Exec counterparts.'''),
                    csr_reg_field_desc('claim', width = 1, reset = 0, write = wr_process_gen(claim_wr_valid, claim_wr_data), comments = '''\
Indicates that the channel is is in use. Setting this clears all of the chanel’s Next registers. This bit can only be cleared when run is low.''')]))
            rsize_wr_valid = bits('rsize_wr_valid'+suffix_str, init = 0)
            rsize_wr_data = bits('rsize_wr_data'+suffix_str, w = 4, init = 0)
            wsize_wr_valid = bits('wsize_wr_valid'+suffix_str, init = 0)
            wsize_wr_data = bits('wsize_wr_data'+suffix_str, w = 4, init = 0)
            self.cfg_reg(csr_reg_group(
                'next_config'+suffix_str, 
                offset = 0x004 + offset_base,
                size = 4,
                fields_desc = [
                    csr_reg_field_desc('rsize', width = 4, reset = 0, write = wr_process_gen(rsize_wr_valid, rsize_wr_data), comments = '''\
Base 2 Logarithm of PDMA transaction sizes;
e.g. 0 is 1 byte, 3 is 8 bytes, 5 is 32 bytes'''),
                    csr_reg_field_desc('wsize', width = 4, reset = 0, write = wr_process_gen(wsize_wr_valid, wsize_wr_data), comments = '''\
Base 2 Logarithm of PDMA transaction sizes; 
e.g. 0 is 1 byte, 3 is 8 bytes, 5 is 32 bytes'''),
                    csr_reg_field_desc('reserved0', access = 'VOL', width = 20),
                    csr_reg_field_desc('order', width = 1, reset = 0, comments = '''\
Enforces strict ordering by only allowing one of each transfer type in-flight at a time. '''),
                    csr_reg_field_desc('repeat', width = 1, reset = 0, comments = '''\
If set, the Exec registers are reloaded from the Next registers once a transfer is complete. The repeat bit must be cleared by software for the sequence to stop.'''),
                    csr_reg_field_desc('reserved1', access = 'VOL', width = 2)]))
            self.cfg_reg(csr_reg_group(
                'next_bytes'+suffix_str,
                offset = 0x008 + offset_base,
                size = 8,
                fields_desc = [
                    csr_reg_field_desc('data', width = 64, reset = 0)], comments = '''\
The read-write NextBytes register holds the number of bytes to be transferred by the channel.  The NextConfig.xsize fields are used to determine the size of the individual transactions that will be used to transfer the number of bytes specified in this register.'''))
            self.cfg_reg(csr_reg_group(
                'next_dest'+suffix_str,
                offset = 0x010 + offset_base,
                size = 8, fields_desc = [
                    csr_reg_field_desc('data', width = 64, reset = 0)], comments = '''\
The read-write NextDestination register holds the physical address of the destination for the transfer.'''))
            self.cfg_reg(csr_reg_group(
                'next_source'+suffix_str, 
                offset = 0x018 + offset_base, 
                size = 8, 
                fields_desc = [
                    csr_reg_field_desc('data', width = 64, reset = 0)], comments = '''\
The read-write NextSource register holds the physical address of the source data for the transfer.'''))

            self.cfg_reg(csr_reg_group(
                'exec_config'+suffix_str, 
                offset = 0x104 + offset_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('rsize', access = 'RO', width = 4, reset = 0),
                    csr_reg_field_desc('wsize', access = 'RO', width = 4, reset = 0),
                    csr_reg_field_desc('reserved0', access = 'VOL', width = 20),
                    csr_reg_field_desc('order', access = 'RO', width = 1, reset = 0),
                    csr_reg_field_desc('repeat', access = 'RO', width = 1, reset = 0),
                    csr_reg_field_desc('reserved1', access = 'VOL', width = 2)], comments = '''\
Each PDMA channel has a set of Exec registers which provide information on the transfer that is currently executing. These registers are read-only and initialized when Control.run is set.  Upon initialization, the Next registers are copied into the Exec registers and a transfer begins.'''))

            exec_bytes_rd_valid = bits('exec_bytes_rd_valid'+suffix_str, init = 0)
            self.cfg_reg(csr_reg_group(
                'exec_bytes'+suffix_str,
                offset = 0x108 + offset_base,
                size = 8, 
                fields_desc = [
                    csr_reg_field_desc('data', access = 'RO', width = 64, reset = 0, read = rd_process_gen(exec_bytes_rd_valid, exec_bytes_rd_data[i]))], comments = '''\
Indicates the number of bytes remaining in a transfer.'''))
            exec_dest_rd_valid = bits('exec_dest_rd_valid'+suffix_str, init = 0)
            self.cfg_reg(csr_reg_group(
                'exec_dest'+suffix_str, 
                offset = 0x110 + offset_base, 
                size = 8, 
                fields_desc = [
                    csr_reg_field_desc('data', access = 'RO', width = 64, reset = 0, read = rd_process_gen(exec_dest_rd_valid, exec_dest_rd_data[i]))], comments = '''\
Indicates the current destination address.'''))
            exec_source_rd_valid = bits('exec_source_rd_valid'+suffix_str, init = 0)
            self.cfg_reg(csr_reg_group(
                'exec_source'+suffix_str,
                offset = 0x118 + offset_base,
                size = 8,
                fields_desc = [
                    csr_reg_field_desc('data', access = 'RO', width = 64, reset = 0, read = rd_process_gen(exec_source_rd_valid, exec_source_rd_data[i]))], comments = '''\
Indicates the current source address.'''))

            run_posedge[i] /= (
                (run_wr_valid & run_wr_data) & ~self.regs['control'+suffix_str].run)

            claim_posedge = (
                (claim_wr_valid & claim_wr_data) & ~self.regs['control'+suffix_str].claim)
            with when(claim_posedge):
                self.regs['next_config'+suffix_str].rsize /= 0
                self.regs['next_config'+suffix_str].wsize /= 0
                self.regs['next_config'+suffix_str].order /= 0
                self.regs['next_config'+suffix_str].repeat /= 0
                self.regs['next_bytes'+suffix_str].data  /= 0
                self.regs['next_dest'+suffix_str].data   /= 0
                self.regs['next_source'+suffix_str].data /= 0

            run_repeat[i] /= (
                self.regs['control'+suffix_str].run & 
                self.regs['next_config'+suffix_str].repeat & 
                dma_channel_done[i])
            with when(run_posedge[i] | run_repeat[i]):
                self.regs['exec_config'+suffix_str].rsize /= self.regs['next_config'+suffix_str].rsize
                self.regs['exec_config'+suffix_str].wsize /= self.regs['next_config'+suffix_str].wsize
                self.regs['exec_config'+suffix_str].order /= self.regs['next_config'+suffix_str].order
                self.regs['exec_config'+suffix_str].repeat /= self.regs['next_config'+suffix_str].repeat

                self.regs['exec_bytes'+suffix_str].data  /= self.regs['next_bytes'+suffix_str].data
                self.regs['exec_dest'+suffix_str].data   /= self.regs['next_dest'+suffix_str].data
                self.regs['exec_source'+suffix_str].data /= self.regs['next_source'+suffix_str].data

            with when(run_wr_valid):
                self.regs['control'+suffix_str].run /= run_wr_data

            with when(claim_wr_valid):
                with when(claim_wr_data):
                    self.regs['control'+suffix_str].claim /= 1
                with other():
                    with when(self.regs['control'+suffix_str].run == 0):
                        self.regs['control'+suffix_str].claim /= 0

            with when(rsize_wr_valid):
                self.regs['next_config'+suffix_str].rsize /= mux(
                    rsize_wr_data > self.p.max_tl_size,
                    self.p.max_tl_size,
                    rsize_wr_data)
            with when(wsize_wr_valid):
                self.regs['next_config'+suffix_str].wsize /= mux(
                    wsize_wr_data > self.p.max_tl_size,
                    self.p.max_tl_size,
                    wsize_wr_data)
        #}}}

        for i in range(self.p.num_channels):
            suffix_str = '_'+str(i)
            dma_channel = zqh_dma_channel(
                'dma_channel'+suffix_str,
                static = 1,
                extern_masters = [self.p.dma_channel_masters[i]])
            dma_channel.io.run    /= dma_channel_run[i]
            dma_channel.io.rsize  /= self.regs['exec_config'+suffix_str].rsize
            dma_channel.io.wsize  /= self.regs['exec_config'+suffix_str].wsize
            dma_channel.io.order  /= self.regs['exec_config'+suffix_str].order
            dma_channel.io.bytes  /= self.regs['exec_bytes'+suffix_str].data
            dma_channel.io.dest   /= self.regs['exec_dest'+suffix_str].data
            dma_channel.io.source /= self.regs['exec_source'+suffix_str].data

            exec_bytes_rd_data[i] /= dma_channel.io.cur_remain_bytes
            exec_dest_rd_data[i] /= dma_channel.io.cur_dest_addr
            exec_source_rd_data[i] /= dma_channel.io.cur_source_addr

            dma_channel_done[i] /= dma_channel.io.done
            with when(dma_channel.io.done):
                self.regs['control'+suffix_str].done /= 1
            with when(dma_channel.io.error):
                self.regs['control'+suffix_str].error /= 1

        self.gen_node_interface('dma_slave')
        for i in range(self.p.num_channels):
            suffix_str = '_'+str(i)
            self.int_out[0][i*2] /= (
                self.regs['control'+suffix_str].done & 
                self.regs['control'+suffix_str].done_ie)
            self.int_out[0][i*2+1] /= (
                self.regs['control'+suffix_str].error & 
                self.regs['control'+suffix_str].error_ie)
