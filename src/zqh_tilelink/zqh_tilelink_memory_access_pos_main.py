import sys
import os
from phgl_imp import *
from .zqh_tilelink_interfaces import zqh_tl_interface_in
from .zqh_tilelink_interfaces import zqh_tl_interface_out
from .zqh_tilelink_bundles import zqh_tl_bundle
from .zqh_tilelink_buffer import zqh_tl_buffer
from .zqh_tilelink_arbiter import zqh_tl_arbiter

class zqh_tilelink_memory_access_pos_tracker(module):
    def set_par(self):
        super(zqh_tilelink_memory_access_pos_tracker, self).set_par()
        self.p.par('pos', None)
        self.p.par('bundle_in', None)

    def set_port(self):
        super(zqh_tilelink_memory_access_pos_tracker, self).set_port()
        self.io.var(inp('source_id', w = log2_up(self.p.pos.num_trackers)))
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        bundle_out = type(self.p.bundle_in)()
        bundle_out.sync_all(self.p.bundle_in)
        bundle_out.update_source_bits(
            self.p.bundle_in.channel['a'].source_bits + log2_up(self.p.pos.num_trackers))
        self.io.var(zqh_tl_bundle('tl_out', p = bundle_out))

    def main(self):
        super(zqh_tilelink_memory_access_pos_tracker, self).main()
        self.io.tl_out.a /= self.io.tl_in.a
        self.io.tl_out.a.bits.source /= cat([self.io.source_id, 
            self.io.tl_in.a.bits.source])
        self.io.tl_in.d /= self.io.tl_out.d

class zqh_tilelink_memory_access_pos_module(module):
    def set_par(self):
        super(zqh_tilelink_memory_access_pos_module, self).set_par()
        self.p.par('node', None)
        self.p.par('bundle_in', None)
        self.p.par('pos', None)

    def set_port(self):
        super(zqh_tilelink_memory_access_pos_module, self).set_port()
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        bundle_out = type(self.p.bundle_in)()
        bundle_out.sync_all(self.p.bundle_in)
        bundle_out.update_source_bits(
            self.p.bundle_in.channel['a'].source_bits + log2_up(self.p.pos.num_trackers))
        self.io.var(zqh_tl_bundle('tl_out', p = bundle_out))

    def main(self):
        super(zqh_tilelink_memory_access_pos_module, self).main()
        interface_in = zqh_tl_interface_in(
            slave_nodes = self.p.node.get_nearest_slave_nodes(),
            bundle = self.io.tl_in.p)
        interface_out = zqh_tl_interface_out(
            slave_nodes = self.p.node.get_nearest_slave_nodes(),
            bundle = self.io.tl_out.p)

        line_shift = log2_ceil(self.p.pos.line_bytes)
        source_id_w = log2_up(self.p.pos.num_trackers)

        dispatch_in_buffer = []
        arb_out_buffer = []
        tracker_in = []
        tracker_out = []
        for i in range(self.p.pos.num_trackers):
            tmp_in_buf = zqh_tl_buffer(
                'dispatch_in_buffer_'+str(i),
                buf_p = self.p.pos.buf_params_in,
                tl_p = self.io.tl_in.p)
            dispatch_in_buffer.append(tmp_in_buf)
            tmp_in = self.io.tl_in.clone().as_bits()
            tmp_in /= tmp_in_buf.io.tl_out
            tracker_in.append(tmp_in)
            tmp_out = self.io.tl_out.clone().as_bits()
            tracker_out.append(tmp_out)

        assert(self.io.tl_in.p.tl_type != 'tl_c')
        assert(self.io.tl_out.p.tl_type != 'tl_c')

        tracker_a_rdys = list(map(
            lambda _: dispatch_in_buffer[_].io.tl_in.a.ready,
            range(self.p.pos.num_trackers)))
        tracker_a_rdys_oh = pri_lsb_enc_oh(cat_rvs(tracker_a_rdys))

        tl_in_a_address_line = self.io.tl_in.a.bits.address >> line_shift

        tracker_a_addr_match = list(map(
            lambda _: (
                dispatch_in_buffer[_].io.tl_out.a.valid & 
                (
                    (dispatch_in_buffer[_].io.tl_out.a.bits.address >> line_shift) == 
                    tl_in_a_address_line)),
            range(self.p.pos.num_trackers)))
        tracker_a_addr_match_any = reduce(lambda x,y: x | y, tracker_a_addr_match)

        tracker_a_sel_ptr = reg_r('tracker_a_sel_ptr', w = self.p.pos.num_trackers)
        tracker_a_sel_ptr_next = bits(
            'tracker_a_sel_ptr_next',
            w = self.p.pos.num_trackers,
            init = 0)
        tracker_a_sel_ptr_lock = reg_r('tracker_a_sel_ptr_lock')
        tl_in_a_sop_eop = self.io.tl_in.sop_eop_a()

        with when(tl_in_a_sop_eop.sop & ~tl_in_a_sop_eop.eop):
            tracker_a_sel_ptr_lock /= 1
        with when(tracker_a_sel_ptr_lock):
            with when(tl_in_a_sop_eop.eop):
                tracker_a_sel_ptr_lock /= 0

        tracker_a_sel_ptr /= tracker_a_sel_ptr_next

        with when(tracker_a_sel_ptr_lock):
            tracker_a_sel_ptr_next /= tracker_a_sel_ptr
        with other():
            with when(tracker_a_addr_match_any):
                tracker_a_sel_ptr_next /= cat_rvs(tracker_a_addr_match)
            with other():
                tracker_a_sel_ptr_next /= tracker_a_rdys_oh

        for i in range(self.p.pos.num_trackers):
            dispatch_in_buffer[i].io.tl_in.a.bits /= self.io.tl_in.a.bits
            dispatch_in_buffer[i].io.tl_in.a.valid /= (
                tracker_a_sel_ptr_next[i] & self.io.tl_in.a.valid)
        self.io.tl_in.a.ready /= reduce(
            lambda x,y: x | y, 
            list(map(
                lambda _: (
                    tracker_a_sel_ptr_next[_] & 
                    dispatch_in_buffer[_].io.tl_in.a.ready), 
                range(self.p.pos.num_trackers))))

        beatsD = list(map(
            lambda _: interface_in.num_beats(dispatch_in_buffer[_].io.tl_in.d.bits),
            range(self.p.pos.num_trackers)))
        portsD = list(map(
            lambda _: dispatch_in_buffer[_].io.tl_in.d,
            range(self.p.pos.num_trackers)))
        zqh_tl_arbiter.apply(
            zqh_tl_arbiter.roundRobin,
            self.io.tl_in.d, 
            list(zip(beatsD, portsD)))

        tracker_beatsA = list(map(
            lambda _: interface_out.num_beats(
                tracker_out[_].a.bits),
            range(self.p.pos.num_trackers)))
        tracker_portsA = list(map(
            lambda _: tracker_out[_].a,
            range(self.p.pos.num_trackers)))
        zqh_tl_arbiter.apply(
            zqh_tl_arbiter.roundRobin, 
            self.io.tl_out.a, 
            list(zip(tracker_beatsA, tracker_portsA)))

        for i in range(self.p.pos.num_trackers):
            tracker_out[i].d.bits /= self.io.tl_out.d.bits
            tracker_out[i].d.valid /= (
                self.io.tl_out.d.valid & 
                (self.io.tl_out.d.bits.source[
                    self.io.tl_out.d.bits.p.source_bits - 1 :
                    self.io.tl_out.d.bits.p.source_bits - source_id_w] == i))
        self.io.tl_out.d.ready /= reduce(
            lambda x,y: x | y,
            list(map(
                lambda _: (
                    self.io.tl_out.d.bits.source[
                        self.io.tl_out.d.bits.p.source_bits - 1 :
                        self.io.tl_out.d.bits.p.source_bits - source_id_w] == _) & 
                    tracker_out[_].d.ready,
                range(self.p.pos.num_trackers))))

        for i in range(self.p.pos.num_trackers):
            tracker = zqh_tilelink_memory_access_pos_tracker(
                'tracker_'+str(i), 
                static = 1,
                pos = self.p.pos, 
                bundle_in = self.io.tl_in.p)
            tracker.io.source_id /= i
            tracker.io.tl_in /= tracker_in[i]
            tracker_out[i] /= tracker.io.tl_out

def zqh_tilelink_memory_access_pos(node, tl_in, p):
    mem_pos = zqh_tilelink_memory_access_pos_module(
        'mem_pos', 
        node = node, 
        bundle_in = tl_in.p, 
        pos = p)
    mem_pos.io.tl_in /= tl_in
    return mem_pos.io.tl_out
