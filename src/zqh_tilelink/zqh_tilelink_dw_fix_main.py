import sys
import os
from phgl_imp import *
from .zqh_tilelink_interfaces import zqh_tl_interface_in
from .zqh_tilelink_interfaces import zqh_tl_interface_out
from .zqh_tilelink_bundles import zqh_tl_bundle
from .zqh_tilelink_misc import TMSG_CONSTS

class zqh_tilelink_dw_fix_burst_module(module):
    def set_par(self):
        super(zqh_tilelink_dw_fix_burst_module, self).set_par()
        self.p.par('bundle_in', None)
        self.p.par('node', None)
        self.p.par('dw_fix', 1)

    def set_port(self):
        super(zqh_tilelink_dw_fix_burst_module, self).set_port()
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        bundle_out = type(self.p.bundle_in)()
        bundle_out.sync_all(self.p.bundle_in)
        if (self.p.dw_fix):
            bundle_out.update_bus_bits(
                self.p.node.down_bus_data_bits, 
                self.p.node.down_bus_address_bits,
                self.p.node.down_bus_size_bits)
        self.io.var(zqh_tl_bundle('tl_out', p = bundle_out))

    def main(self):
        super(zqh_tilelink_dw_fix_burst_module, self).main()
        if (self.p.dw_fix):
            down_data_bits = self.p.node.down_bus_data_bits
            up_data_bits = self.p.node.up_bus_data_bits
        else:
            down_data_bits = self.p.bundle_in.channel['a'].data_bits
            up_data_bits = self.p.bundle_in.channel['a'].data_bits
        assert(up_data_bits >= down_data_bits)

        tl_in_a_is_get = self.io.tl_in.a.bits.opcode.match_any([TMSG_CONSTS.get()])
        buffer_in_a = self.io.tl_in.a.bits.clone('buffer_in_a').as_reg()
        buffer_in_a_valid = reg_r('buffer_in_a_valid')
        buffer_in_a_bypass = bits('buffer_in_a_bypass', init = 0)
        buffer_in_a_push = bits(
            'buffer_in_a_push', 
            init = self.io.tl_in.a.fire() & ~buffer_in_a_bypass)
        buffer_in_a_pop = bits('buffer_in_a_pop', init = 0)
        self.io.tl_in.a.ready /= ~buffer_in_a_valid | buffer_in_a_pop
        with when(buffer_in_a_push):
            buffer_in_a_valid /= 1
            buffer_in_a /= self.io.tl_in.a.bits
        with elsewhen(buffer_in_a_pop):
            buffer_in_a_valid /= 0
        up_req_a_valid = buffer_in_a_valid | (self.io.tl_in.a.fire() & ~buffer_in_a_bypass)
        up_req_opcode = mux(
            buffer_in_a_valid,
            buffer_in_a.opcode, 
            self.io.tl_in.a.bits.opcode)
        up_req_a_is_get = up_req_opcode.match_any([TMSG_CONSTS.get()])
        up_req_a_is_put = up_req_opcode.match_any([
            TMSG_CONSTS.put_full_data(),
            TMSG_CONSTS.put_partial_data()])

        buffer_in_d = self.io.tl_in.d.bits.clone('buffer_in_d').as_reg()
        buffer_in_d_valid = reg_r('buffer_in_d_valid')
        buffer_in_d_push = bits('buffer_in_d_push', init = 0)
        buffer_in_d_pop = bits(
            'buffer_in_d_pop',
            init = self.io.tl_in.d.fire() & buffer_in_d_valid)
        self.io.tl_out.d.ready /= (
            (~buffer_in_d_valid & self.io.tl_in.d.ready) | 
            buffer_in_d_pop)
        with when(buffer_in_d_push):
            buffer_in_d_valid /= 1
        with elsewhen(buffer_in_d_pop):
            buffer_in_d_valid /= 0


        (s_ready, s_req_rd, s_req_wr) = range(3)
        state = reg_rs('state', w = 2)
        up2down_times = up_data_bits//down_data_bits
        send_cnt_w = log2_up(up2down_times)
        send_cnt = reg_r('send_cnt', w = send_cnt_w)
        send_no_split = (
            buffer_in_a.size < 
            (log2_ceil(down_data_bits//8) + 1))
        send_cnt_max = mux(send_no_split, 0, up2down_times - 1)
        send_cnt_reach_max = send_cnt == send_cnt_max
        send_sop_eop = self.io.tl_out.sop_eop_a()


        #FSM
        with when(state == s_ready):
            with when(up_req_a_valid):
                with when(up_req_a_is_get):
                    state /= s_req_rd
                with when(up_req_a_is_put):
                    state /= s_req_wr
                send_cnt /= 0
        with when(state == s_req_rd):
            with when(self.io.tl_out.a.fire()):
                state /= s_ready
        with when(state == s_req_wr):
            with when(self.io.tl_out.a.fire()):
                with when(send_cnt_reach_max):
                    with when(send_sop_eop.eop):
                        state /= s_ready
                    with other():
                        state /= s_req_wr
                    send_cnt /= 0
                with other():
                    state /= s_req_wr
                    send_cnt /= send_cnt + 1

        #buffer a pop control
        with when(state == s_req_rd):
            with when(self.io.tl_out.a.fire()):
                buffer_in_a_pop /= 1
        with when(state == s_req_wr):
            with when(self.io.tl_out.a.fire()):
                with when(send_cnt_reach_max):
                    buffer_in_a_pop /= 1

        #buffer d push control
        tl_out_d_has_data = self.io.tl_out.d.bits.opcode == TMSG_CONSTS.access_ack_data()
        tl_out_d_burst = (
            self.io.tl_out.d.bits.size > 
            log2_ceil(down_data_bits//8))
        resp_cnt_w = log2_up(up2down_times)
        resp_cnt = reg_r('resp_cnt', w = resp_cnt_w)
        resp_cnt_max = mux(tl_out_d_burst & tl_out_d_has_data, up2down_times - 1, 0)
        resp_cnt_reach_max = resp_cnt == resp_cnt_max
        with when(self.io.tl_out.d.fire()):
            with when(resp_cnt_reach_max):
                resp_cnt /= 0
            with other():
                resp_cnt /= resp_cnt + 1
        
        d_resp_en = self.io.tl_out.d.valid & resp_cnt_reach_max
        with when(d_resp_en):
            buffer_in_d_push /= ~self.io.tl_in.d.ready

        #down node bus's request send
        send_ah = log2_ceil(up_data_bits//8) - 1
        send_al = log2_ceil(down_data_bits//8)
        if (up_data_bits == down_data_bits):
            send_data_sel = send_cnt
            send_data = buffer_in_a.data
            send_mask = buffer_in_a.mask
        else:
            send_data_sel = send_cnt + buffer_in_a.address[send_ah:send_al]
            send_data = sel_bin(
                send_data_sel, 
                buffer_in_a.data.grouped(down_data_bits))
            send_mask = sel_bin(
                send_data_sel, 
                buffer_in_a.mask.grouped(down_data_bits//8))

        with when(buffer_in_a_bypass):
            if (up_data_bits == down_data_bits):
                out_data = self.io.tl_in.a.bits.data
                out_mask = self.io.tl_in.a.bits.mask
            else:
                out_data = sel_bin(
                    self.io.tl_in.a.bits.address[send_ah:send_al],
                    self.io.tl_in.a.bits.data.grouped(down_data_bits))
                out_mask = sel_bin(
                    self.io.tl_in.a.bits.address[send_ah:send_al],
                    self.io.tl_in.a.bits.mask.grouped(down_data_bits//8))
            self.io.tl_out.a /= self.io.tl_in.a
            self.io.tl_out.a.bits.data /= out_data
            self.io.tl_out.a.bits.mask /= out_mask
        with other():
            self.io.tl_out.a.bits /= buffer_in_a
            self.io.tl_out.a.bits.data /= send_data
            self.io.tl_out.a.bits.mask /= send_mask
            self.io.tl_out.a.valid /= (
                state.match_any([s_req_rd, s_req_wr]) &
                buffer_in_a_valid)

        #down node bus's response recieve
        with when(self.io.tl_out.d.valid):
            buffer_in_d.opcode /= self.io.tl_out.d.bits.opcode
            buffer_in_d.param /= self.io.tl_out.d.bits.param
            buffer_in_d.source /= self.io.tl_out.d.bits.source
            buffer_in_d.sink /= self.io.tl_out.d.bits.sink
            buffer_in_d.error /= self.io.tl_out.d.bits.error
            buffer_in_d.size /= self.io.tl_out.d.bits.size

            #update the corespond data slice
            for i in range(up2down_times):
                with when(tl_out_d_has_data):
                    with when(~tl_out_d_burst | (resp_cnt == i)):
                        dh = (i + 1) * down_data_bits - 1
                        dl = i * down_data_bits
                        buffer_in_d.data[dh : dl] /= self.io.tl_out.d.bits.data

        #up node bus's response
        self.io.tl_in.d.bits /= mux(
            buffer_in_d_valid,
            buffer_in_d.pack(),
            buffer_in_d.pack_next())
        self.io.tl_in.d.valid /= (self.io.tl_out.d.valid & d_resp_en) | buffer_in_d_valid

class zqh_tilelink_dw_fix_no_burst_module(module):
    def set_par(self):
        super(zqh_tilelink_dw_fix_no_burst_module, self).set_par()
        self.p.par('bundle_in', None)
        self.p.par('node', None)
        self.p.par('dw_fix', 1)

    def set_port(self):
        super(zqh_tilelink_dw_fix_no_burst_module, self).set_port()
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        bundle_out = type(self.p.bundle_in)()
        bundle_out.sync_all(self.p.bundle_in)
        if (self.p.dw_fix):
            bundle_out.update_bus_bits(
                self.p.node.down_bus_data_bits,
                self.p.node.down_bus_address_bits,
                self.p.node.down_bus_size_bits)
        self.io.var(zqh_tl_bundle('tl_out', p = bundle_out))

    def main(self):
        super(zqh_tilelink_dw_fix_no_burst_module, self).main()
        if (self.p.dw_fix):
            down_data_bits = self.p.node.down_bus_data_bits
            up_data_bits = self.p.node.up_bus_data_bits
        else:
            down_data_bits = self.p.bundle_in.channel['a'].data_bits
            up_data_bits = self.p.bundle_in.channel['a'].data_bits
        assert(up_data_bits >= down_data_bits)

        master_nodes = self.p.node.get_master_nodes()
        master_size_max = max(map(lambda _: _.transfer_sizes.max, master_nodes))

        tl_in_a_sop_eop = self.io.tl_in.sop_eop_a()
        #tmp tl_in_d_sop_eop = self.io.tl_in.sop_eop_d()
        tl_out_d_sop_eop = self.io.tl_out.sop_eop_d()

        buffer_in_a = self.io.tl_in.a.bits.clone('buffer_in_a').as_reg()
        buffer_in_a_valid = reg_r('buffer_in_a_valid')
        buffer_in_a_bypass = bits('buffer_in_a_bypass', init = 0)
        buffer_in_a_sop_eop = tl_in_a_sop_eop.clone('buffer_in_a_sop_eop').as_reg()
        buffer_in_a_push = bits(
            'buffer_in_a_push', 
            init = self.io.tl_in.a.fire() 
            & ~buffer_in_a_bypass)
        buffer_in_a_pop = bits('buffer_in_a_pop', init = 0)
        self.io.tl_in.a.ready /= ~buffer_in_a_valid
        with when(buffer_in_a_push):
            buffer_in_a_valid /= 1
            buffer_in_a_sop_eop /= tl_in_a_sop_eop
            buffer_in_a /= self.io.tl_in.a.bits
        with when(buffer_in_a_pop):
            buffer_in_a_valid /= 0
        buffer_in_a_cur_size = mux(
            buffer_in_a_sop_eop.sop & buffer_in_a_sop_eop.eop,
            buffer_in_a.size,
            log2_ceil(up_data_bits//8))
        buffer_in_a_is_get = buffer_in_a.opcode.match_any([TMSG_CONSTS.get()])
        buffer_in_a_is_put = buffer_in_a.opcode.match_any([
            TMSG_CONSTS.put_full_data(),
            TMSG_CONSTS.put_partial_data()])

        buffer_in_d = self.io.tl_in.d.bits.clone('buffer_in_d').as_reg()
        buffer_in_d_valid = reg_r('buffer_in_d_valid')
        buffer_in_d_push = bits('buffer_in_d_push', init = 0)
        buffer_in_d_pop = bits('buffer_in_d_pop', init = 0)
        #tmp buffer_in_d_bypass = ~buffer_in_a_valid
        buffer_in_d_bypass = 0
        self.io.tl_out.d.ready /= ~buffer_in_d_valid
        with when(buffer_in_d_push):
            buffer_in_d_valid /= 1
        with when(buffer_in_d_pop):
            buffer_in_d_valid /= 0


        (s_ready, s_req_rd, s_req_wr, s_resp) = range(4)
        state = reg_rs('state', w = 2)
        up2down_times = up_data_bits//down_data_bits
        send_cnt_w = log2_up(up2down_times)
        send_cnt = reg_r('send_cnt', w = send_cnt_w)
        cur_size_small = (
            buffer_in_a_cur_size < 
            (log2_ceil(down_data_bits//8) + 1))
        send_cnt_max = mux(cur_size_small, 0, up2down_times - 1)
        send_cnt_reach_max = send_cnt == send_cnt_max
        burst_cnt_w = log2_up(master_size_max//(up_data_bits//8))
        burst_cnt = reg_r('burst_cnt', w = burst_cnt_w)
        burst_size_small = (
            buffer_in_a.size < 
            (log2_ceil(up_data_bits//8) + 1))
        burst_cnt_max = mux(
            burst_size_small,
            0,
            (1 << (buffer_in_a.size - log2_ceil(up_data_bits//8))) - 1)
        burst_cnt_reach_max = burst_cnt == burst_cnt_max

        #FSM
        with when(state == s_ready):
            with when(buffer_in_a_valid):
                with when(buffer_in_a_is_get):
                    state /= s_req_rd
                with when(buffer_in_a_is_put):
                    state /= s_req_wr
                send_cnt /= 0

                with when(buffer_in_a_sop_eop.sop):
                    burst_cnt /= 0
        with when(state == s_req_rd):
            with when(self.io.tl_out.a.fire()):
                state /= s_resp
        with when(state == s_req_wr):
            with when(self.io.tl_out.a.fire()):
                state /= s_resp
        with when(state == s_resp):
            with when(self.io.tl_out.d.fire()):
                with when(send_cnt_reach_max):
                    with when(burst_cnt_reach_max):
                        state /= s_ready
                    with other():
                        send_cnt /= 0
                        burst_cnt /= burst_cnt + 1

                        with when(buffer_in_a_is_get):
                            state /= s_req_rd
                        with when(buffer_in_a_is_put):
                            state /= s_req_wr
                with other():
                    send_cnt /= send_cnt + 1

                    with when(buffer_in_a_is_get):
                        state /= s_req_rd
                    with when(buffer_in_a_is_put):
                        state /= s_req_wr

        d_resp_en = (
            send_cnt_reach_max & 
            (buffer_in_a_is_get | (buffer_in_a_is_put & burst_cnt_reach_max)))

        with when(buffer_in_d_valid):
             with when(self.io.tl_in.d.fire()):
                 buffer_in_d_pop /= 1

        #tmp with when(tl_in_d_sop_eop.eop & buffer_in_a_valid):
        #tmp with when(tl_out_d_sop_eop.eop & buffer_in_a_valid):
        with when(state == s_resp):
            with when(tl_out_d_sop_eop.eop & buffer_in_a_valid):
                with when(send_cnt_reach_max):
                    with when(burst_cnt_reach_max):
                        buffer_in_a_pop /= 1

        #buffer d push control
        with when(self.io.tl_out.d.valid & d_resp_en & buffer_in_a_valid):
            buffer_in_d_push /= ~self.io.tl_in.d.ready

        buffer_in_a_cur_address = (
            buffer_in_a.address + 
            (burst_cnt << log2_ceil(up_data_bits//8)))

        #down node bus's request send
        send_size = mux(
            cur_size_small, 
            buffer_in_a_cur_size,
            log2_ceil(down_data_bits//8))
        send_ah = log2_ceil(up_data_bits//8) - 1
        send_al = log2_ceil(down_data_bits//8)
        if (up_data_bits == down_data_bits):
            send_data_sel = send_cnt
            send_data = buffer_in_a.data
            send_mask = buffer_in_a.mask
        else:
            send_data_sel = send_cnt + buffer_in_a_cur_address[send_ah:send_al]
            send_data = sel_bin(
                send_data_sel,
                buffer_in_a.data.grouped(down_data_bits))
            send_mask = sel_bin(
                send_data_sel, 
                buffer_in_a.mask.grouped(down_data_bits//8))

        with when(buffer_in_a_bypass):
            if (up_data_bits == down_data_bits):
                out_data = self.io.tl_in.a.bits.data
                out_mask = self.io.tl_in.a.bits.mask
            else:
                out_data = sel_bin(
                    self.io.tl_in.a.bits.address[send_ah:send_al],
                    self.io.tl_in.a.bits.data.grouped(down_data_bits))
                out_mask = sel_bin(
                    self.io.tl_in.a.bits.address[send_ah:send_al],
                    self.io.tl_in.a.bits.mask.grouped(down_data_bits//8))
            self.io.tl_out.a /= self.io.tl_in.a
            self.io.tl_out.a.bits.data /= out_data
            self.io.tl_out.a.bits.mask /= out_mask
        with other():
            self.io.tl_out.a.bits /= buffer_in_a
            self.io.tl_out.a.bits.data /= send_data
            self.io.tl_out.a.bits.mask /= send_mask
            self.io.tl_out.a.bits.address /= buffer_in_a_cur_address
            if (up_data_bits != down_data_bits):
                self.io.tl_out.a.bits.address[send_ah:send_al] /= send_data_sel
            self.io.tl_out.a.bits.size /= send_size
            self.io.tl_out.a.valid /= state.match_any([s_req_rd, s_req_wr])

        #down node bus's response recieve
        with when(self.io.tl_out.d.valid):
            buffer_in_d.opcode /= self.io.tl_out.d.bits.opcode
            buffer_in_d.param /= self.io.tl_out.d.bits.param
            buffer_in_d.source /= self.io.tl_out.d.bits.source
            buffer_in_d.sink /= self.io.tl_out.d.bits.sink
            buffer_in_d.error /= self.io.tl_out.d.bits.error

            #size should use request's
            buffer_in_d.size /= buffer_in_a.size

            #update the corespond data slice
            for i in range(up2down_times):
                with when(send_data_sel == i):
                    dh = (i + 1) * down_data_bits - 1
                    dl = i * down_data_bits
                    buffer_in_d.data[dh : dl] /= self.io.tl_out.d.bits.data

        #up node bus's response
        #tmp with when(buffer_in_d_bypass):
        #tmp     self.io.tl_in.d /=  self.io.tl_out.d
        #tmp     self.io.tl_in.d.bits.data /= self.io.tl_out.d.bits.data.rep(up2down_times)
        #tmp with other():
        #tmp     self.io.tl_in.d.valid /= (
        #tmp         (self.io.tl_out.d.valid & d_resp_en) | 
        #tmp         buffer_in_d_valid)
        #tmp     self.io.tl_in.d /= mux(
        #tmp         buffer_in_d_valid,
        #tmp         buffer_in_d.pack(),
        #tmp         buffer_in_d.pack_next())
        self.io.tl_in.d.valid /= (
            (self.io.tl_out.d.valid & d_resp_en) | 
            buffer_in_d_valid)
        self.io.tl_in.d /= mux(
            buffer_in_d_valid,
            buffer_in_d.pack(),
            buffer_in_d.pack_next())

def zqh_tilelink_dw_fix(node, tl_in, has_burst):
    if (has_burst):
        tl_dw_fix = zqh_tilelink_dw_fix_burst_module(
            'tl_dw_fix',
            bundle_in = tl_in.p,
            node = node)
    else:
        tl_dw_fix = zqh_tilelink_dw_fix_no_burst_module(
            'tl_dw_fix',
            bundle_in = tl_in.p,
            node = node)
    tl_dw_fix.io.tl_in /= tl_in
    return tl_dw_fix.io.tl_out

def zqh_tilelink_burst_split_fix(node, tl_in, p):
    tl_burst_fix = zqh_tilelink_dw_fix_no_burst_module(
        'tl_burst_fix',
        bundle_in = tl_in.p,
        node = node,
        dw_fix = 0)
    tl_burst_fix.io.tl_in /= tl_in
    return tl_burst_fix.io.tl_out
