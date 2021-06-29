import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_interfaces import zqh_tl_interface_out
from zqh_tilelink.zqh_tilelink_bundles import zqh_tl_bundle
from .zqh_axi4_parameters import zqh_axi4_base_parameter
from .zqh_axi4_bundles import zqh_axi4_aw_bundle
from .zqh_axi4_bundles import zqh_axi4_w_bundle
from .zqh_axi4_bundles import zqh_axi4_b_bundle
from .zqh_axi4_bundles import zqh_axi4_ar_bundle
from .zqh_axi4_bundles import zqh_axi4_r_bundle
from .zqh_axi4_bundles import zqh_axi4_all_channel_io

def zqh_axi4_w_2_tilelink(interface, aw, w, source, tl_param):
    interface_out = interface

    beat_put_full = 0
    strb_shift = (w.strb >> aw.addr[log2_ceil(w.p.data_w/8) - 1 : 0])
    for i in range(log2_ceil(w.p.data_w/8) + 1):
        if (i == 0):
            size_align = 1
        else:
            size_align = aw.addr[i - 1 : 0] == 0
        tmp = (aw.size == i) & (strb_shift == (2**(2**i) - 1)) & size_align
        beat_put_full = beat_put_full | tmp

    return mux(
        beat_put_full & (aw.len == 0), #only support single beat axi4 aw request
        interface_out.put(
            source,
            aw.addr,
            ((aw.len + 1) << aw.size).is_log2(),
            w.data)[1],
        interface_out.put(
            source,
            aw.addr,
            ((aw.len + 1) << aw.size).is_log2(),
            w.data,
            w.strb)[1])

def zqh_axi4_ar_2_tilelink(interface, ar, source, tl_param):
    interface_out = interface
    return interface_out.get(source, ar.addr, ((ar.len + 1) << ar.size).is_log2())[1]

def zqh_tl_2_axi4_b(tl_d, id, resp, axi4_param):
    ret = zqh_axi4_b_bundle(p = axi4_param.b)
    ret.id /= id
    ret.resp /= resp
    return ret

def zqh_tl_2_axi4_r(tl_d, id, resp, axi4_param):
    ret = zqh_axi4_r_bundle(p = axi4_param.b)
    ret.id /= id
    ret.data /= tl_d.data
    ret.resp /= resp
    ret.last /= 0 #need overwrite later
    return ret

class zqh_axi4_2_tilelink_id_buf_entry(bundle):
    def set_par(self):
        super(zqh_axi4_2_tilelink_id_buf_entry, self).set_par()
        self.p.par('id_w', None)

    def set_var(self):
        super(zqh_axi4_2_tilelink_id_buf_entry, self).set_var()
        self.var(reg_s('free'))
        self.var(reg('id', w = self.p.id_w))
        self.var(reg_r('is_aw'))

class zqh_axi4_2_tilelink_module(module):
    def set_par(self):
        super(zqh_axi4_2_tilelink_module, self).set_par()
        self.p.par('axi4_2_tilelink', None)
        self.p.par('bundle_in', None)
        self.p.par('bundle_out', None)
        self.p.par('node', None)

    def set_port(self):
        super(zqh_axi4_2_tilelink_module, self).set_port()
        self.io.var(zqh_axi4_all_channel_io('axi4_in', p = self.p.bundle_in).flip())
        self.io.var(zqh_tl_bundle('tl_out', p = self.p.bundle_out))

    def main(self):
        super(zqh_axi4_2_tilelink_module, self).main()
        interface_out = zqh_tl_interface_out(
            slave_nodes = self.p.node.get_nearest_slave_nodes(),
            bundle = self.io.tl_out.p)

        queue_aw = queue(
            'queue_aw',
            gen = zqh_axi4_aw_bundle,
            gen_p = self.io.axi4_in.p.aw,
            entries = self.p.axi4_2_tilelink.axi4_aw_q_depth)
        queue_aw.io.enq /= self.io.axi4_in.aw
        queue_w = queue(
            'queue_w',
            gen = zqh_axi4_w_bundle,
            gen_p = self.io.axi4_in.p.w,
            entries = self.p.axi4_2_tilelink.axi4_w_q_depth)
        queue_w.io.enq /= self.io.axi4_in.w
        queue_ar = queue(
            'queue_ar',
            gen = zqh_axi4_ar_bundle,
            gen_p = self.io.axi4_in.p.ar,
            entries = self.p.axi4_2_tilelink.axi4_ar_q_depth)
        queue_ar.io.enq /= self.io.axi4_in.ar

        sch_en = bits('sch_en', init = 0)
        w_ar_arbiter = rr_arbiter_ctrl(
            [queue_w.io.deq.valid, queue_ar.io.deq.valid],
            sch_en)

        axi4_id_table = vec(
            'axi4_id_table',
            gen = lambda _: zqh_axi4_2_tilelink_id_buf_entry(
                _,
                id_w = max(
                    self.io.axi4_in.aw.bits.id.get_w(),
                    self.io.axi4_in.ar.bits.id.get_w())),
            n = self.p.axi4_2_tilelink.tl_source_id_num)
        axi4_id_table_free_oh_bits = pri_lsb_enc_oh(cat_rvs(list(map(
            lambda _: axi4_id_table[_].free,
            range(self.p.axi4_2_tilelink.tl_source_id_num)))))
        axi4_id_table_free_oh = axi4_id_table_free_oh_bits.grouped()
        axi4_id_table_free_any = reduce(
            lambda x,y: x | y,
            list(map(
                lambda _: axi4_id_table[_].free,
                range(self.p.axi4_2_tilelink.tl_source_id_num))))
        axi4_sel_source = oh2bin(axi4_id_table_free_oh_bits)
        axi4_aw_id_same_stall = reduce(
            lambda x,y: x | y,
            list(map(
                lambda _: ~_.free & _.is_aw & (_.id == queue_aw.io.deq.bits.id),
                axi4_id_table)))
        axi4_ar_id_same_stall = reduce(
            lambda x,y: x | y,
            list(map(
                lambda _: ~_.free &  ~_.is_aw & (_.id == queue_ar.io.deq.bits.id),
                axi4_id_table)))


        [s_ready, s_aw, s_ar] = range(3)
        axi4_state = reg_rs('axi4_state', w = 2, rs = s_ready)
        tl_out_source = reg('tl_out_source', w = self.io.tl_out.a.bits.p.source_bits)

        with when(axi4_state == s_ready):
            with when(axi4_id_table_free_any):
                with when(queue_w.io.deq.valid & w_ar_arbiter[0] & ~axi4_aw_id_same_stall):
                    axi4_state /= s_aw
                    tl_out_source /= axi4_sel_source
                with when(queue_ar.io.deq.valid & w_ar_arbiter[1] & ~axi4_ar_id_same_stall):
                    axi4_state /= s_ar
                    tl_out_source /= axi4_sel_source
        with when(axi4_state == s_aw):
            with when(queue_w.io.deq.fire() & queue_w.io.deq.bits.last):
                axi4_state /= s_ready
        with when(axi4_state == s_ar):
            with when(queue_ar.io.deq.fire()):
                axi4_state /= s_ready

        self.io.tl_out.a.valid /= 0
        tl_out_put_req = zqh_axi4_w_2_tilelink(
            interface_out,
            queue_aw.io.deq.bits,
            queue_w.io.deq.bits,
            tl_out_source,
            self.io.tl_out.p)
        queue_w.io.deq.ready /= 0
        queue_aw.io.deq.ready /= 0
        queue_ar.io.deq.ready /= 0
        with when(axi4_state == s_aw):
            self.io.tl_out.a.valid /= queue_w.io.deq.valid
            self.io.tl_out.a.bits /= tl_out_put_req
            queue_w.io.deq.ready /= self.io.tl_out.a.ready
            queue_aw.io.deq.ready /= queue_w.io.deq.fire() & queue_w.io.deq.bits.last
            sch_en /= queue_aw.io.deq.ready

        tl_out_get_req = zqh_axi4_ar_2_tilelink(
            interface_out,
            queue_ar.io.deq.bits, 
            tl_out_source,
            self.io.tl_out.p)
        with when(axi4_state == s_ar):
            self.io.tl_out.a.valid /= queue_ar.io.deq.valid
            self.io.tl_out.a.bits /= tl_out_get_req
            queue_ar.io.deq.ready /= self.io.tl_out.a.ready
            sch_en /= self.io.tl_out.a.fire()

        tl_out_d_sop_eop = self.io.tl_out.sop_eop_d()
        tl_out_d_has_data = interface_out.has_data(self.io.tl_out.d.bits)
        with when(tl_out_d_sop_eop.eop):
            for i in range(len(axi4_id_table)):
                with when(self.io.tl_out.d.bits.source == i):
                    axi4_id_table[i].free /= 1

        tl_out_a_sop_eop = self.io.tl_out.sop_eop_a()
        with when(tl_out_a_sop_eop.sop):
            for i in range(len(axi4_id_table)):
                with when(self.io.tl_out.a.bits.source == i):
                    axi4_id_table[i].free /= 0
                    with when(axi4_state == s_aw):
                        axi4_id_table[i].id /= queue_aw.io.deq.bits.id
                        axi4_id_table[i].is_aw /= 1
                    with other():
                        axi4_id_table[i].id /= queue_ar.io.deq.bits.id
                        axi4_id_table[i].is_aw /= 0

        axi4_br_id = axi4_id_table[self.io.tl_out.d.bits.source].id
        self.io.axi4_in.b.valid /= 0
        axi4_b_bits = zqh_tl_2_axi4_b(
            self.io.tl_out.d.bits,
            axi4_br_id,
            0,
            self.io.axi4_in.p)
        self.io.axi4_in.r.valid /= 0
        axi4_r_bits = zqh_tl_2_axi4_r(
            self.io.tl_out.d.bits,
            axi4_br_id, 
            0,
            self.io.axi4_in.p)
        with when(tl_out_d_has_data):
            self.io.axi4_in.b.valid /= 0
            self.io.axi4_in.r.valid /= self.io.tl_out.d.valid
            self.io.axi4_in.r.bits /= axi4_r_bits
            self.io.axi4_in.r.bits.last /= tl_out_d_sop_eop.last
            self.io.tl_out.d.ready /= self.io.axi4_in.r.ready
        with other():
            self.io.axi4_in.b.valid /= self.io.tl_out.d.valid
            self.io.axi4_in.r.valid /= 0
            self.io.axi4_in.b.bits /= axi4_b_bits
            self.io.axi4_in.r.bits.last /= 1
            self.io.tl_out.d.ready /= self.io.axi4_in.b.ready

def zqh_axi4_2_tilelink(node, axi4_in, tl_out, p):
    axi4_2_tilelink = zqh_axi4_2_tilelink_module(
        'axi4_2_tilelink',
        axi4_2_tilelink = p,
        bundle_in = axi4_in.p,
        bundle_out = tl_out.p,
        node = node)
    axi4_2_tilelink.io.axi4_in /= axi4_in
    tl_out /= axi4_2_tilelink.io.tl_out
