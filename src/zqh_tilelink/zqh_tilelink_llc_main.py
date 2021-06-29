import sys
import os
from phgl_imp import *
from .zqh_tilelink_interfaces import zqh_tl_interface_in
from .zqh_tilelink_interfaces import zqh_tl_interface_out
from .zqh_tilelink_misc import TMSG_CONSTS
from .zqh_tilelink_misc import THT_CONSTS
from .zqh_tilelink_misc import TPM_CONSTS
from .zqh_tilelink_bundles import zqh_tl_bundle
from .zqh_tilelink_buffer import zqh_tl_buffer
from .zqh_tilelink_arbiter import zqh_tl_arbiter

class zqh_tilelink_llc_snoop_tracker(module):
    def set_par(self):
        super(zqh_tilelink_llc_snoop_tracker, self).set_par()
        self.p.par('llc', None)
        self.p.par('bundle_in', None)
        self.p.par('interface_out', None)

    def set_port(self):
        super(zqh_tilelink_llc_snoop_tracker, self).set_port()
        self.io.var(inp('source_id', w = log2_up(self.p.llc.num_trackers)))
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        bundle_out = type(self.p.bundle_in)()
        bundle_out.sync_all(self.p.bundle_in)
        bundle_out.update_source_bits(
            self.p.bundle_in.channel['a'].source_bits + log2_up(self.p.llc.num_trackers))
        self.io.var(zqh_tl_bundle('tl_out', p = bundle_out))

    def main(self):
        super(zqh_tilelink_llc_snoop_tracker, self).main()
        interfaceIn = zqh_tl_interface_in(
            slave_nodes = self.p.node.get_nearest_slave_nodes(), 
            bundle = self.p.bundle_in)

        buf_out = zqh_tl_buffer(
            'buf_out', 
            buf_p = self.p.llc.buf_params_out,
            tl_p = self.io.tl_out.p)
        self.io.tl_out /= buf_out.io.tl_out

        lineShift = log2_ceil(self.p.llc.line_bytes)
        cache_targets = self.p.llc.caches
        source_id_w = log2_up(self.p.llc.num_trackers)

        a_sop_eop = self.io.tl_in.sop_eop_a()
        a_valid = self.io.tl_in.a.valid
        a_req = self.io.tl_in.a.bits
        a_req_get_valid = a_valid & (a_req.opcode == TMSG_CONSTS.get())
        a_req_acquire_block_valid = a_valid & (a_req.opcode == TMSG_CONSTS.acquire_block())
        a_req_put_valid = a_valid & a_req.opcode.match_any([
            TMSG_CONSTS.put_full_data(), 
            TMSG_CONSTS.put_partial_data()])
        a_req_put_buf_valid = reg_r('a_req_put_buf_valid')

        c_valid = self.io.tl_in.c.valid
        c_req = self.io.tl_in.c.bits
        c_req_probe_ack_valid = c_valid & c_req.opcode.match_any([
            TMSG_CONSTS.probe_ack(), 
            TMSG_CONSTS.probe_ack_data()])
        c_req_release_valid = c_valid & c_req.opcode.match_any([
            TMSG_CONSTS.release(),
            TMSG_CONSTS.release_data()])
        c_req_has_data = interfaceIn.has_data(c_req)

        d_fire = self.io.tl_in.d.fire()
        
        mem_d_fire = buf_out.io.tl_in.d.fire()
        mem_d_source_release_flag_pos = self.p.bundle_in.channel['a'].source_bits
        mem_d_release = buf_out.io.tl_in.d.bits.source[mem_d_source_release_flag_pos]
        mem_d_has_data = self.p.interface_out.has_data(buf_out.io.tl_in.d.bits)

        (
            s_ready, s_probe_req, s_probe_req_wait_ack, s_mem_get, 
            s_mem_put, s_d_resp, s_wait_e) = range(7)
        snoop_state = reg_rs('snoop_state', rs = s_ready, w = 3)

        (s_release_ready, s_release_mem_put, s_release_d_resp) = range(3)
        release_state = reg_rs('release_state', rs = s_release_ready, w = 2)

        (
            s_probe_ack_ready, s_probe_ack, s_probe_ack_data, s_probe_ack_data_d_resp, 
            s_probe_ack_done) = range(5)
        probe_ack_state = reg_rs('probe_ack_state', rs = s_probe_ack_ready, w = 3)

        mem_a_sop_eop = buf_out.io.tl_in.sop_eop_a()
        mem_a_release = buf_out.io.tl_in.a.bits.source[mem_d_source_release_flag_pos]

        mem_get_done = buf_out.io.tl_in.a.fire() & (
            buf_out.io.tl_in.a.bits.opcode == TMSG_CONSTS.get())

        mem_d_sop_eop = buf_out.io.tl_in.sop_eop_d()

        probe_cnt = reg_r('probe_cnt', w = log2_up(len(self.p.llc.caches) + 1))
        probe_ack_cnt = reg_r('probe_ack_cnt', w = log2_up(len(self.p.llc.caches) + 1))
        probe_bitmap = cat_rvs(list(map(lambda _: _ != a_req.source, cache_targets)))
        probe_cur = reg_r('probe_cur', w = len(self.p.llc.caches))
        probe_cur_next = probe_cur & ~pri_lsb_enc_oh(probe_cur)
        probe_target = sel_p_lsb(probe_cur, cache_targets)

        probe_address = a_req.address
        probe_line = probe_address >> lineShift
        with when(snoop_state == s_ready):
            with when(a_req_get_valid | a_req_acquire_block_valid | a_req_put_valid):
                with when(probe_bitmap == 0): #no need probe
                    #wait channel c's release finish
                    with when(release_state != s_release_mem_put):
                        with when(a_req_put_valid):
                            snoop_state /= s_mem_put
                        with other():
                            snoop_state /= s_mem_get
                with other():
                    snoop_state /= s_probe_req
                    probe_cur /= probe_bitmap
                    probe_cnt /= count_ones(probe_bitmap)
                    probe_ack_cnt /= count_ones(probe_bitmap)
            a_req_put_buf_valid /= a_req_put_valid

        with when(snoop_state == s_probe_req):
            with when(self.io.tl_in.b.fire()):
                probe_cur /= probe_cur_next
                probe_cnt /= probe_cnt - 1
                with when(probe_cnt == 1):
                    snoop_state /= s_probe_req_wait_ack

        with when(snoop_state == s_probe_req_wait_ack):
            with when(probe_ack_state == s_probe_ack_done):
                with when(a_req_put_valid):
                    snoop_state /= s_mem_put
                with other():
                    snoop_state /= s_mem_get

        with when(snoop_state == s_mem_put):
            with when(mem_a_sop_eop.eop & ~mem_a_release):
                snoop_state /= s_d_resp

        with when(snoop_state == s_mem_get):
            with when(mem_get_done):
                snoop_state /= s_d_resp
        with when(snoop_state == s_d_resp):
            with when(mem_d_sop_eop.eop & ~mem_d_release):
                with when(~a_req_put_buf_valid):
                    with when(a_req.opcode == TMSG_CONSTS.acquire_block()):
                        snoop_state /= s_wait_e
                    with other():
                        snoop_state /= s_ready
                with other():
                    snoop_state /= s_ready
        with when(snoop_state == s_wait_e):
            with when(self.io.tl_in.e.fire()):
                snoop_state /= s_ready

        with when(release_state == s_release_ready):
            #wait channel a's put finish
            with when(snoop_state != s_mem_put):
                with when(c_req_release_valid):
                    release_state /= s_release_mem_put
        with when(release_state == s_release_mem_put):
            with when(mem_a_sop_eop.eop & mem_a_release):
                release_state /= s_release_d_resp
        with when(release_state == s_release_d_resp):
            with when(mem_d_fire & mem_d_release):
                release_state /= s_release_ready

        with when(probe_ack_state == s_probe_ack_ready):
            with when(c_valid):
                with when(c_req.opcode == TMSG_CONSTS.probe_ack()):
                    probe_ack_state /= s_probe_ack
                    probe_ack_cnt /= probe_ack_cnt - 1
                with when(c_req.opcode == TMSG_CONSTS.probe_ack_data()):
                    probe_ack_state /= s_probe_ack_data
                    probe_ack_cnt /= probe_ack_cnt - 1
        with when(probe_ack_state == s_probe_ack):
            with when(probe_ack_cnt == 0):
                probe_ack_state /= s_probe_ack_done
            with other():
                probe_ack_state /= s_probe_ack_ready
        with when(probe_ack_state == s_probe_ack_data):
            with when(mem_a_sop_eop.eop):
                probe_ack_state /= s_probe_ack_data_d_resp
        with when(probe_ack_state == s_probe_ack_data_d_resp):
            with when(mem_d_sop_eop.eop & ~mem_d_release):
                with when(probe_ack_cnt == 0):
                    probe_ack_state /= s_probe_ack_done
                with other():
                    probe_ack_state /= s_probe_ack_ready
        with when(probe_ack_state == s_probe_ack_done):
            probe_ack_state /= s_probe_ack_ready

        acq_perms = sel_map(a_req.param, [
          (TPM_CONSTS.n_to_b() , TPM_CONSTS.to_b()),
          (TPM_CONSTS.n_to_t() , TPM_CONSTS.to_n()),
          (TPM_CONSTS.b_to_t() , TPM_CONSTS.to_n())], TPM_CONSTS.to_n())
        probe_perms = sel_map(a_req.opcode, [
          (TMSG_CONSTS.put_full_data    (), TPM_CONSTS.to_n()),
          (TMSG_CONSTS.put_partial_data (), TPM_CONSTS.to_n()),
          (TMSG_CONSTS.arithmetic_data  (), TPM_CONSTS.to_n()),
          (TMSG_CONSTS.logical_data     (), TPM_CONSTS.to_n()),
          (TMSG_CONSTS.get              (), TPM_CONSTS.to_b()),
          (TMSG_CONSTS.hint             (), sel_map(a_req.param, [
            (THT_CONSTS.prefetch_read     (), TPM_CONSTS.to_b()),
            (THT_CONSTS.prefetch_write    (), TPM_CONSTS.to_n())], TPM_CONSTS.to_n())),
          (TMSG_CONSTS.acquire_block   (), acq_perms),
          (TMSG_CONSTS.acquire_perm    (), acq_perms)], TPM_CONSTS.to_n())

        probe_req = interfaceIn.probe(
            probe_line << lineShift, probe_target, lineShift, probe_perms)[1]
        self.io.tl_in.b.bits /= probe_req
        self.io.tl_in.b.valid /= 0
        with when(snoop_state == s_probe_req):
            self.io.tl_in.b.valid /= 1

        self.io.tl_in.a.ready /= 0
        with when(snoop_state == s_mem_put):
            self.io.tl_in.a.ready /= buf_out.io.tl_in.a.ready
        with when(snoop_state == s_d_resp):
            with when(mem_d_sop_eop.eop):
                with when(a_req_put_buf_valid):
                    self.io.tl_in.a.ready /= 0
                with other():
                    with when(
                        (a_req.opcode != TMSG_CONSTS.acquire_block()) & 
                        ~mem_d_release) :
                        self.io.tl_in.a.ready /= 1
        with when(snoop_state == s_wait_e):
            with when(self.io.tl_in.e.fire()):
                self.io.tl_in.a.ready /= 1

        buf_out.io.tl_in.a.valid /= 0

        self.io.tl_in.c.ready /= 0
        with when(probe_ack_state == s_probe_ack):
            self.io.tl_in.c.ready /= 1
        with when(
            (probe_ack_state == s_probe_ack_data) | 
            (release_state == s_release_mem_put)):
            self.io.tl_in.c.ready /= buf_out.io.tl_in.a.ready

        mem_get_req = buf_out.io.tl_in.a.bits.clone()
        mem_get_req /= a_req
        mem_get_req.opcode /= TMSG_CONSTS.get()
        mem_get_req.param /= 0
        mem_get_req.source /= cat([self.io.source_id, value(0), a_req.source])
        with when(snoop_state == s_mem_get):
            buf_out.io.tl_in.a.valid /= 1
            buf_out.io.tl_in.a.bits /= mem_get_req

        mem_put_full_req_from_c = self.p.interface_out.put(
            cat([
                self.io.source_id,
                release_state == s_release_mem_put,
                c_req.source.u_ext(a_req.source.get_w())]),
            c_req.address,
            lineShift,
            c_req.data)[1]
        mem_put_none_req_from_c = self.p.interface_out.put(
            cat([
                self.io.source_id,
                release_state == s_release_mem_put,
                c_req.source.u_ext(a_req.source.get_w())]),
            c_req.address,
            0,
            c_req.data,
            0)[1]
        with when(snoop_state == s_mem_put):
            buf_out.io.tl_in.a.valid /= self.io.tl_in.a.valid
            buf_out.io.tl_in.a.bits /= a_req
            buf_out.io.tl_in.a.bits.source /= cat([
                self.io.source_id, value(0),
                a_req.source])
        with when(
            (probe_ack_state == s_probe_ack_data) | 
            (release_state == s_release_mem_put)):
            buf_out.io.tl_in.a.valid /= self.io.tl_in.c.valid
            with when(c_req_has_data):
                buf_out.io.tl_in.a.bits /= mem_put_full_req_from_c
            with other():
                buf_out.io.tl_in.a.bits /= mem_put_none_req_from_c

        self.io.tl_in.d.valid /= 0
        self.io.tl_in.d.bits /= buf_out.io.tl_in.d.bits
        self.io.tl_in.d.bits.sink  /= cat([
            self.io.source_id,
            buf_out.io.tl_in.d.bits.sink])
        buf_out.io.tl_in.d.ready /= 0
        with when(mem_d_has_data): #a_req is acquire/get
            with when(snoop_state == s_d_resp):
                self.io.tl_in.d.valid /= buf_out.io.tl_in.d.valid
                with when(a_req.opcode == TMSG_CONSTS.acquire_block()):
                    self.io.tl_in.d.bits.opcode /= TMSG_CONSTS.grant_data()
                    self.io.tl_in.d.bits.param  /= mux(
                        a_req.param.match_any([
                            TPM_CONSTS.n_to_t(),
                            TPM_CONSTS.b_to_t()]), 
                        TPM_CONSTS.to_t(),
                        TPM_CONSTS.to_b())
                buf_out.io.tl_in.d.ready /= self.io.tl_in.d.ready
        with other():
            with when(mem_d_release): #c_req release
                with when(release_state == s_release_d_resp):
                    self.io.tl_in.d.valid /= buf_out.io.tl_in.d.valid
                    self.io.tl_in.d.bits.opcode /= TMSG_CONSTS.release_ack()
                    buf_out.io.tl_in.d.ready /= self.io.tl_in.d.ready
            with other():
                with when(a_req_put_buf_valid & (snoop_state == s_d_resp)):
                    self.io.tl_in.d.valid /= buf_out.io.tl_in.d.valid
                    buf_out.io.tl_in.d.ready /= self.io.tl_in.d.ready
                #c probe ack data write
                with when(probe_ack_state == s_probe_ack_data_d_resp):
                    self.io.tl_in.d.valid /= 0
                    buf_out.io.tl_in.d.ready /= 1
            self.io.tl_in.d.bits.param /= 0

        self.io.tl_in.e.ready /= 0
        with when (snoop_state == s_wait_e):
            self.io.tl_in.e.ready /= 1

def zqh_tilelink_llc_snoop(node, tl_in, p):
    bundle_out = type(tl_in.p.bundle_in)()
    bundle_out.sync_all(tl_in.p.bundle_in)
    bundle_out.update_source_bits(
        tl_in.p.bundle_in.channel['a'].source_bits + log2_up(p.num_trackers))

    tl_out = zqh_tl_bundle(p = bundle_out).as_bits()

    interfaceIn = zqh_tl_interface_in(bundle = tl_in.p)
    interface_out = zqh_tl_interface_out(
        slave_nodes = node.get_nearest_slave_nodes(),
        bundle = bundle_out)

    lineShift = log2_ceil(p.line_bytes)
    source_id_w = log2_up(p.num_trackers)

    dispatch_in_buffer = []
    arb_out_buffer = []
    tracker_in = []
    tracker_out = []
    for i in range(p.num_trackers):
        tmp_in_buf = zqh_tl_buffer(
            'dispatch_in_buffer_'+str(i),
            buf_p = p.buf_params_in,
            tl_p = tl_in.p)
        dispatch_in_buffer.append(tmp_in_buf)
        tmp_in = tl_in.clone().as_bits()
        tmp_in /= tmp_in_buf.io.tl_out
        tracker_in.append(tmp_in)
        tmp_out = tl_out.clone().as_bits()
        tracker_out.append(tmp_out)

    tracker_a_rdys = list(map(
        lambda _: dispatch_in_buffer[_].io.tl_in.a.ready,
        range(p.num_trackers)))
    tracker_a_rdys_oh = pri_lsb_enc_oh(cat_rvs(tracker_a_rdys))
    tracker_c_rdys = list(map(
        lambda _: dispatch_in_buffer[_].io.tl_in.c.ready,
        range(p.num_trackers)))
    tracker_c_rdys_oh = pri_lsb_enc_oh(cat_rvs(tracker_c_rdys))

    tl_in_a_address_line = tl_in.a.bits.address >> lineShift
    tl_in_c_address_line = tl_in.c.bits.address >> lineShift
    tl_in_c_probe_ack = tl_in.c.bits.opcode.match_any([
        TMSG_CONSTS.probe_ack(),
        TMSG_CONSTS.probe_ack_data()])

    tracker_a_addr_match = list(map(
        lambda _: (
            dispatch_in_buffer[_].io.tl_out.a.valid & 
            (
                (dispatch_in_buffer[_].io.tl_out.a.bits.address >> lineShift) == 
                tl_in_a_address_line)),
        range(p.num_trackers)))
    tracker_c_addr_match = list(map(
        lambda _: (
            dispatch_in_buffer[_].io.tl_out.a.valid & 
            (
                (dispatch_in_buffer[_].io.tl_out.a.bits.address >> lineShift) == 
                tl_in_c_address_line)
            & tl_in_c_probe_ack),
        range(p.num_trackers)))
    tracker_a_addr_match_any = reduce(lambda x,y: x | y, tracker_a_addr_match)
    tracker_c_addr_match_any = reduce(lambda x,y: x | y, tracker_c_addr_match)

    tracker_a_sel_ptr = reg_r('tracker_a_sel_ptr', w = p.num_trackers)
    tracker_a_sel_ptr_next = bits('tracker_a_sel_ptr_next', w = p.num_trackers, init = 0)
    tracker_a_sel_ptr_lock = reg_r('tracker_a_sel_ptr_lock')
    tracker_c_sel_ptr = reg_r('tracker_c_sel_ptr', w = p.num_trackers)
    tracker_c_sel_ptr_next = bits('tracker_c_sel_ptr_next', w = p.num_trackers, init = 0)
    tracker_c_sel_ptr_lock = reg_r('tracker_c_sel_ptr_lock')
    tl_in_a_sop_eop = tl_in.sop_eop_a()
    tl_in_c_sop_eop = tl_in.sop_eop_c()

    with when(tl_in_a_sop_eop.sop & ~tl_in_a_sop_eop.eop):
        tracker_a_sel_ptr_lock /= 1
    with when(tracker_a_sel_ptr_lock):
        with when(tl_in_a_sop_eop.eop):
            tracker_a_sel_ptr_lock /= 0

    with when(tl_in_c_sop_eop.sop & ~tl_in_c_sop_eop.eop):
        tracker_c_sel_ptr_lock /= 1
    with when(tracker_c_sel_ptr_lock):
        with when(tl_in_c_sop_eop.eop):
            tracker_c_sel_ptr_lock /= 0

    tracker_a_sel_ptr /= tracker_a_sel_ptr_next
    tracker_c_sel_ptr /= tracker_c_sel_ptr_next

    with when(tracker_a_sel_ptr_lock):
        tracker_a_sel_ptr_next /= tracker_a_sel_ptr
    with other():
        with when(tracker_a_addr_match_any):
            tracker_a_sel_ptr_next /= cat_rvs(tracker_a_addr_match)
        with other():
            tracker_a_sel_ptr_next /= tracker_a_rdys_oh

    with when(tracker_c_sel_ptr_lock):
        tracker_c_sel_ptr_next /= tracker_c_sel_ptr
    with other():
        with when(tracker_c_addr_match_any):
            tracker_c_sel_ptr_next /= cat_rvs(tracker_c_addr_match)
        with other():
            tracker_c_sel_ptr_next /= tracker_c_rdys_oh

    for i in range(p.num_trackers):
        dispatch_in_buffer[i].io.tl_in.a.bits /= tl_in.a.bits
        dispatch_in_buffer[i].io.tl_in.a.valid /= tracker_a_sel_ptr_next[i] & tl_in.a.valid
    tl_in.a.ready /= reduce(
        lambda x,y: x | y, list(map(
            lambda _: tracker_a_sel_ptr_next[_] & dispatch_in_buffer[_].io.tl_in.a.ready,
            range(p.num_trackers))))

    for i in range(p.num_trackers):
        dispatch_in_buffer[i].io.tl_in.c.bits /= tl_in.c.bits
        dispatch_in_buffer[i].io.tl_in.c.valid /= tracker_c_sel_ptr_next[i] & tl_in.c.valid
    tl_in.c.ready /= reduce(
        lambda x,y: x | y, 
        list(map(
            lambda _: tracker_c_sel_ptr_next[_] & dispatch_in_buffer[_].io.tl_in.c.ready,
            range(p.num_trackers))))

    for i in range(p.num_trackers):
        dispatch_in_buffer[i].io.tl_in.e.bits /= tl_in.e.bits
        dispatch_in_buffer[i].io.tl_in.e.valid /= (
            tl_in.e.valid & 
            (tl_in.e.bits.sink[
                tl_in.e.bits.p.sink_bits - 1 : tl_in.e.bits.p.sink_bits - source_id_w] == i))
    tl_in.e.ready /= reduce(
        lambda x,y: x | y, 
        list(map(
            lambda _: (
                tl_in.e.bits.sink[
                    tl_in.e.bits.p.sink_bits - 1 :
                    tl_in.e.bits.p.sink_bits - source_id_w] == _) & 
                dispatch_in_buffer[_].io.tl_in.e.ready,
            range(p.num_trackers))))

    beatsB = list(map(
        lambda _: interfaceIn.num_beats(dispatch_in_buffer[_].io.tl_in.b.bits),
        range(p.num_trackers)))
    portsB = list(map(
        lambda _: dispatch_in_buffer[_].io.tl_in.b,
        range(p.num_trackers)))
    zqh_tl_arbiter.apply(p.policy, tl_in.b, list(zip(beatsB, portsB)))

    beatsD = list(map(
        lambda _: interfaceIn.num_beats(dispatch_in_buffer[_].io.tl_in.d.bits),
        range(p.num_trackers)))
    portsD = list(map(
        lambda _: dispatch_in_buffer[_].io.tl_in.d,
        range(p.num_trackers)))
    zqh_tl_arbiter.apply(p.policy, tl_in.d, list(zip(beatsD, portsD)))

    tracker_beatsA = list(map(
        lambda _: interface_out.num_beats(tracker_out[_].a.bits),
        range(p.num_trackers)))
    tracker_portsA = list(map(
        lambda _: tracker_out[_].a, 
        range(p.num_trackers)))
    zqh_tl_arbiter.apply(p.policy, tl_out.a, list(zip(tracker_beatsA, tracker_portsA)))

    for i in range(p.num_trackers):
        tracker_out[i].d.bits /= tl_out.d.bits
        tracker_out[i].d.valid /= tl_out.d.valid & (
            tl_out.d.bits.source[
                tl_out.d.bits.p.source_bits - 1 :
                tl_out.d.bits.p.source_bits - source_id_w] == i)
    tl_out.d.ready /= reduce(
        lambda x,y: x|y,
        list(map(
            lambda _: (
                tl_out.d.bits.source[
                    tl_out.d.bits.p.source_bits - 1 :
                    tl_out.d.bits.p.source_bits - source_id_w] == _) & 
                tracker_out[_].d.ready,
            range(p.num_trackers))))

    for i in range(p.num_trackers):
        tracker = zqh_tilelink_llc_snoop_tracker(
            'tracker_'+str(i),
            llc = p,
            bundle_in = tl_in.p, 
            interface_out = interface_out)
        tracker.io.source_id /= i
        tracker.io.tl_in /= tracker_in[i]
        tracker_out[i] /= tracker.io.tl_out

    return tl_out
