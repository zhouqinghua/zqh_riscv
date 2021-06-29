import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_interfaces import zqh_tl_interface_in
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS
from zqh_tilelink.zqh_tilelink_bundles import zqh_tl_bundle
from zqh_tilelink.zqh_tilelink_atomic_transform_main import zqh_tilelink_atomic_transform
from .zqh_axi4_parameters import zqh_axi4_base_parameter
from .zqh_axi4_bundles import zqh_axi4_aw_bundle
from .zqh_axi4_bundles import zqh_axi4_w_bundle
from .zqh_axi4_bundles import zqh_axi4_ar_bundle
from .zqh_axi4_bundles import zqh_axi4_all_channel_io

def zqh_tilelink_2_axi4_aw(tl, id, lock = 0, cache = 0, prot = 1, qos = 0):
    req = zqh_axi4_aw_bundle()
    req.id /= id
    req.addr /= tl.a.bits.address
    req.len /= mux(
        tl.a.bits.size < 3,
        0,
        ((value(1) << tl.a.bits.size) >> log2_ceil(tl.a.bits.p.data_bits//8)) - 1)
    req.size /= log2_ceil(tl.a.bits.p.data_bits//8)
    req.burst /= zqh_axi4_base_parameter.burst_incr()
    req.lock /= lock
    req.cache /= cache
    req.prot /= prot
    req.qos /= qos
    return req

def zqh_tilelink_2_axi4_w(tl):
    req = zqh_axi4_w_bundle()
    req.data /= tl.a.bits.data
    req.strb /= tl.a.bits.mask
    req.last /= tl.sop_eop_a().eop
    return req

def zqh_tilelink_2_axi4_ar(tl, id, lock = 0, cache = 0, prot = 1, qos = 0):
    req = zqh_axi4_ar_bundle()
    req.id /= id
    req.addr /= tl.a.bits.address
    req.len /= mux(
        tl.a.bits.size < 3,
        0,
        ((value(1) << tl.a.bits.size) >> log2_ceil(tl.a.bits.p.data_bits//8)) - 1)
    req.size /= log2_ceil(tl.a.bits.p.data_bits//8)
    req.burst /= zqh_axi4_base_parameter.burst_incr()
    req.lock /= lock
    req.cache /= cache
    req.prot /= prot
    req.qos /= qos
    return req

class zqh_tilelink_2_axi4_source_size_buf_entry(bundle):
    def set_par(self):
        super(zqh_tilelink_2_axi4_source_size_buf_entry, self).set_par()
        self.p.par('source_bits', 1)
        self.p.par('size_bits', 1)

    def set_var(self):
        super(zqh_tilelink_2_axi4_source_size_buf_entry, self).set_var()
        self.var(reg_s('free'))
        self.var(reg('source', w = self.p.source_bits))
        self.var(reg('size', w = self.p.size_bits))

class zqh_tilelink_2_axi4_module(module):
    def set_par(self):
        super(zqh_tilelink_2_axi4_module, self).set_par()
        self.p.par('tl2axi4', None)
        self.p.par('bundle_in', None)
        self.p.par('bundle_out', None)

    def set_port(self):
        super(zqh_tilelink_2_axi4_module, self).set_port()
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        self.io.var(zqh_axi4_all_channel_io('axi4_out', p = self.p.bundle_out))

    def main(self):
        super(zqh_tilelink_2_axi4_module, self).main()
        interfaceIn = zqh_tl_interface_in(bundle = self.io.tl_in.p)

        aw_ids = range(self.p.tl2axi4.aw_id_max_num)
        ar_ids = range(self.p.tl2axi4.ar_id_max_num)

        tl_in_a_get = self.io.tl_in.a.bits.opcode == TMSG_CONSTS.get()
        tl_in_a_put = self.io.tl_in.a.bits.opcode.match_any([
            TMSG_CONSTS.put_full_data(),
            TMSG_CONSTS.put_partial_data()])
        tl_in_a_multi_flit = (
            (1 << self.io.tl_in.a.bits.size) >>
            log2_ceil(self.io.tl_in.a.bits.p.data_bits//8)) > 1
        tl_in_a_sop_eop = self.io.tl_in.sop_eop_a()

        tl_in_d_sop_eop = self.io.tl_in.sop_eop_d()

        aw_source_size_table = vec(
            'aw_source_size_table',
            gen = lambda _: zqh_tilelink_2_axi4_source_size_buf_entry(
                _,
                source_bits = self.io.tl_in.a.bits.p.source_bits,
                size_bits = self.io.tl_in.a.bits.p.size_bits),
            n = len(aw_ids))
        aw_source_size_table_free_oh_bits = pri_lsb_enc_oh(
            cat_rvs(list(map(lambda _: aw_source_size_table[_].free, aw_ids))))
        aw_source_size_table_free_oh = aw_source_size_table_free_oh_bits.grouped()
        aw_source_size_table_free_any = reduce(
            lambda x,y: x | y,
            list(map(lambda _: aw_source_size_table[_].free, aw_ids)))
        aw_id = oh2bin(aw_source_size_table_free_oh_bits)

        ar_source_size_table = vec(
            'ar_source_size_table',
            gen = lambda _: zqh_tilelink_2_axi4_source_size_buf_entry(
                _,
                source_bits = self.io.tl_in.a.bits.p.source_bits,
                size_bits = self.io.tl_in.a.bits.p.size_bits),
            n = len(ar_ids))
        ar_source_size_table_free_oh_bits = pri_lsb_enc_oh(cat_rvs(list(
            map(lambda _: ar_source_size_table[_].free, ar_ids))))
        ar_source_size_table_free_oh = ar_source_size_table_free_oh_bits.grouped()
        ar_source_size_table_free_any = reduce(
            lambda x,y: x | y,
            list(map(lambda _: ar_source_size_table[_].free, ar_ids)))
        ar_id = oh2bin(ar_source_size_table_free_oh_bits)

        [s_ready, s_aw, s_aw_no_w, s_w, s_ar] = range(5)
        axi4_state = reg_rs('axi4_state', w = 3, rs = s_ready)

        with when(axi4_state == s_ready):
            with when(self.io.tl_in.a.valid):
                with when(tl_in_a_put & aw_source_size_table_free_any):
                    axi4_state /= s_aw
                with when(tl_in_a_get & ar_source_size_table_free_any):
                    axi4_state /= s_ar

        with when(axi4_state == s_aw):
            with when(self.io.axi4_out.aw.fire()):
                #only one flit
                with when(self.io.axi4_out.w.fire() & ~tl_in_a_multi_flit):
                    axi4_state /= s_ready
                with other():
                    axi4_state /= s_w
            with other():
                with when(self.io.axi4_out.w.fire()):
                    axi4_state /= s_aw_no_w

        with when(axi4_state == s_aw_no_w):
            with when(self.io.axi4_out.aw.fire()):
                #only one flit
                with when(~tl_in_a_multi_flit):
                    axi4_state /= s_ready
                with other():
                    axi4_state /= s_w

        with when(axi4_state == s_w):
            with when(tl_in_a_sop_eop.eop):
                axi4_state /= s_ready

        with when(axi4_state == s_ar):
            with when(self.io.axi4_out.ar.fire()):
                axi4_state /= s_ready

        b_id_oh = bin2oh(self.io.axi4_out.b.bits.id)
        for i in aw_ids:
            with when(self.io.axi4_out.aw.fire() & aw_source_size_table_free_oh[i]):
                aw_source_size_table[i].free /= 0
                aw_source_size_table[i].source /= self.io.tl_in.a.bits.source
                aw_source_size_table[i].size /= self.io.tl_in.a.bits.size
            with when(self.io.axi4_out.b.fire() & b_id_oh[i]):
                aw_source_size_table[i].free /= 1
        r_id_oh = bin2oh(self.io.axi4_out.r.bits.id)
        for i in ar_ids:
            with when(self.io.axi4_out.ar.fire() & ar_source_size_table_free_oh[i]):
                ar_source_size_table[i].free /= 0
                ar_source_size_table[i].source /= self.io.tl_in.a.bits.source
                ar_source_size_table[i].size /= self.io.tl_in.a.bits.size
            with when(
                self.io.axi4_out.r.fire() & 
                r_id_oh[i] & 
                self.io.axi4_out.r.bits.last):
                ar_source_size_table[i].free /= 1


        self.io.axi4_out.aw.valid /= 0
        self.io.axi4_out.aw.bits /= zqh_tilelink_2_axi4_aw(self.io.tl_in, aw_id)
        self.io.axi4_out.w.valid /= 0
        self.io.axi4_out.w.bits /= zqh_tilelink_2_axi4_w(self.io.tl_in)
        self.io.tl_in.a.ready /= 0
        with when(axi4_state == s_aw):
            self.io.axi4_out.aw.valid /= self.io.tl_in.a.valid
            self.io.axi4_out.w.valid /= self.io.tl_in.a.valid
            self.io.tl_in.a.ready /= self.io.axi4_out.aw.ready & self.io.axi4_out.w.ready
        with when(axi4_state == s_aw_no_w):
            self.io.axi4_out.aw.valid /= self.io.tl_in.a.valid
            self.io.axi4_out.w.valid /= 0
            self.io.tl_in.a.ready /= self.io.axi4_out.aw.ready
        with when(axi4_state == s_w):
            self.io.axi4_out.aw.valid /= 0
            self.io.axi4_out.w.valid /= self.io.tl_in.a.valid
            self.io.tl_in.a.ready /= self.io.axi4_out.w.ready

        self.io.axi4_out.ar.valid /= 0
        self.io.axi4_out.ar.bits /= zqh_tilelink_2_axi4_ar(self.io.tl_in, ar_id)
        with when(axi4_state == s_ar):
            self.io.axi4_out.ar.valid /= self.io.tl_in.a.valid
            self.io.tl_in.a.ready /= self.io.axi4_out.ar.ready

        tl_in_d_lock = reg_r('tl_in_d_lock')
        with when(tl_in_d_sop_eop.sop & ~tl_in_d_sop_eop.eop):
            tl_in_d_lock /= 1
        with when(tl_in_d_lock):
            with when(tl_in_d_sop_eop.eop):
                tl_in_d_lock /= 0

        self.io.tl_in.d.valid /= 0
        self.io.axi4_out.b.ready /= self.io.tl_in.d.ready &  ~tl_in_d_lock
        self.io.axi4_out.r.ready /= self.io.tl_in.d.ready
        aw_id_entry = aw_source_size_table[self.io.axi4_out.b.bits.id]
        ar_id_entry = ar_source_size_table[self.io.axi4_out.r.bits.id]
        with when(self.io.axi4_out.b.valid & ~tl_in_d_lock):
            self.io.tl_in.d.valid /= self.io.axi4_out.b.valid
            self.io.tl_in.d.bits /= interfaceIn.access_ack(
                aw_id_entry.source,
                aw_id_entry.size)
            self.io.axi4_out.r.ready /= 0 #only accept b resp
        with other():
            with when(self.io.axi4_out.r.valid):
                self.io.tl_in.d.valid /= self.io.axi4_out.r.valid
                self.io.tl_in.d.bits /= interfaceIn.access_ack_data(
                    ar_id_entry.source,
                    ar_id_entry.size,
                    self.io.axi4_out.r.bits.data)

def zqh_tilelink_2_axi4(node, tl_in, p):
    if (p.atomic_en):
        amo_tl_out_p = type(tl_in.p)(tl_type = tl_in.p.tl_type)
        amo_tl_out_p.sync_source_bits(tl_in.p)
        amo_tl_out_p.sync_sink_bits(tl_in.p)
        #one more source bit for amo flag
        amo_tl_out_p.channel['a'].source_bits = amo_tl_out_p.channel['a'].source_bits + 1
        amo_tl_out_p.channel['b'].source_bits = amo_tl_out_p.channel['b'].source_bits + 1
        amo_tl_out_p.channel['d'].source_bits = amo_tl_out_p.channel['d'].source_bits + 1
        tl_after_amo = type(tl_in)('tl_after_amo', p = amo_tl_out_p).as_bits()
        zqh_tilelink_atomic_transform(node, tl_in, tl_after_amo, p.atomic)
    else:
        tl_after_amo = tl_in
    tl2axi4 = zqh_tilelink_2_axi4_module(
        'tl2axi4',
        tl2axi4 = p,
        bundle_in = tl_after_amo.p,
        bundle_out = node.down[0].bundle_in[0])
    tl2axi4.io.tl_in /= tl_after_amo
    return tl2axi4.io.axi4_out
