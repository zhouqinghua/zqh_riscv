import sys
import os
from phgl_imp import *
from .zqh_tilelink_misc import *

class zqh_tl_bundle_base(bundle):
    def sop_eop_com(self, a, is_1_more_flit):
        cnt_w = 2**a.bits.size.get_w() - 1
        size_cnt = (1 << a.bits.size) >> log2_ceil(a.bits.p.data_bits//8)

        req_is_1_more_flit_dly1 = reg(next = is_1_more_flit)
        fire = a.fire()
        fire_dly1 = reg_r(next = fire)
        cnt = reg_r(w = cnt_w)

        sop_eop = zqh_tl_sop_eop()
        
        req_1_flit_sop = fire & ~is_1_more_flit
        req_1_flit_eop = fire & ~is_1_more_flit

        with when(fire):
            with when(is_1_more_flit):
                with when(
                    (cnt == 0) | 
                    (fire_dly1 & req_is_1_more_flit_dly1 & (cnt == 1))):
                    cnt /= size_cnt
                with other():
                    cnt /= cnt - 1
            with other():
                cnt /= 0
        with other():
            with when(cnt == 1):
                cnt /= 0

        req_1_more_flit_sop = fire & is_1_more_flit & mux(cnt.match_any([0,1]), 1, 0)
        req_1_more_flit_eop = fire & is_1_more_flit & mux(cnt == 2, 1, 0)

        sop_eop.sop /= req_1_flit_sop | req_1_more_flit_sop
        sop_eop.eop /= req_1_flit_eop | req_1_more_flit_eop
        sop_eop.last /= mux(is_1_more_flit, mux(cnt == 2, 1, 0), 1)

        return sop_eop

    def sop_eop(self, rv):
        size_1_more_flit = rv.bits.size > log2_ceil(rv.bits.p.data_bits//8)
        if (isinstance(rv.bits, zqh_tl_bundle_a)):
            req_is_1_more_flit = rv.bits.opcode.match_any([
                TMSG_CONSTS.put_full_data(),
                TMSG_CONSTS.put_partial_data()]) & size_1_more_flit
        elif (isinstance(rv.bits, zqh_tl_bundle_c)):
            req_is_1_more_flit = rv.bits.opcode.match_any([
                TMSG_CONSTS.release_data(),
                TMSG_CONSTS.probe_ack_data()]) & size_1_more_flit
        elif (isinstance(rv.bits, zqh_tl_bundle_e)):
            req_is_1_more_flit = value(0).to_bits()
        elif (isinstance(rv.bits, zqh_tl_bundle_b)):
            req_is_1_more_flit = value(0).to_bits()
        elif (isinstance(rv.bits, zqh_tl_bundle_d)):
            req_is_1_more_flit = rv.bits.opcode.match_any([
                TMSG_CONSTS.grant_data(), 
                TMSG_CONSTS.access_ack_data()]) & size_1_more_flit
        else:
            assert(0)
        return self.sop_eop_com(rv, req_is_1_more_flit)
    
    def num_beats(self, size = None, max_size = None):
        if (size is None):
            size = self.size

        if (max_size is None):
            max_size = 2**size.get_w() - 1
        else:
            assert(isinstance(max_size, int))

        return mux(
            size < log2_ceil(self.p.data_bits//8),
            1,
            (1 << size)[max_size : 0] >> log2_ceil(self.p.data_bits//8))

class zqh_tl_bundle_a(zqh_tl_bundle_base):
    def set_var(self):
        super(zqh_tl_bundle_a, self).set_var()
        self.var(bits('opcode', w = 3))
        self.var(bits('param', w = 3))
        self.var(bits('size', w = self.p.size_bits))
        self.var(bits('source', w = self.p.source_bits))
        self.var(bits('address', w = self.p.address_bits))
        self.var(bits('mask', w = self.p.data_bits//8))
        self.var(bits('data', w = self.p.data_bits))

class zqh_tl_bundle_b(zqh_tl_bundle_base):
    def set_var(self):
        super(zqh_tl_bundle_b, self).set_var()
        self.var(bits('opcode', w = 3))
        self.var(bits('param', w = TPM_CONSTS.bd_width))
        self.var(bits('size', w = self.p.size_bits))
        self.var(bits('source', w = self.p.source_bits))
        self.var(bits('address', w = self.p.address_bits))
        self.var(bits('mask', w = self.p.data_bits//8))
        self.var(bits('data', w = self.p.data_bits))

class zqh_tl_bundle_c(zqh_tl_bundle_base):
    def set_var(self):
        super(zqh_tl_bundle_c, self).set_var()
        self.var(bits('opcode', w = 3))
        self.var(bits('param', w = TPM_CONSTS.c_width))
        self.var(bits('size', w = self.p.size_bits))
        self.var(bits('source', w = self.p.source_bits))
        self.var(bits('address', w = self.p.address_bits))
        self.var(bits('data', w = self.p.data_bits))
        self.var(bits('error'))

class zqh_tl_bundle_d(zqh_tl_bundle_base):
    def set_var(self):
        super(zqh_tl_bundle_d, self).set_var()
        self.var(bits('opcode', w = 3))
        self.var(bits('param', w = TPM_CONSTS.bd_width))
        self.var(bits('size', w = self.p.size_bits))
        self.var(bits('source', w = self.p.source_bits))
        self.var(bits('sink', w = self.p.sink_bits))
        self.var(bits('data', w = self.p.data_bits))
        self.var(bits('error'))

class zqh_tl_bundle_e(zqh_tl_bundle_base):
    def set_var(self):
        super(zqh_tl_bundle_e, self).set_var()
        self.var(bits('sink', w = self.p.sink_bits))

class zqh_tl_sop_eop(bundle):
    def set_var(self):
        super(zqh_tl_sop_eop, self).set_var()
        self.var(bits('sop'))
        self.var(bits('eop'))
        self.var(bits('last'))

class zqh_tl_bundle(zqh_tl_bundle_base):
    def set_var(self):
        super(zqh_tl_bundle, self).set_var()
        self.var(ready_valid(
            'a', 
            gen = zqh_tl_bundle_a, 
            p = self.p.channel['a']))
        if (self.p.tl_type == 'tl_c'):
            self.var(ready_valid(
                'b',
                gen = zqh_tl_bundle_b, 
                p = self.p.channel['b']).flip())
            self.var(ready_valid(
                'c', 
                gen = zqh_tl_bundle_c, 
                p = self.p.channel['c']))
        self.var(ready_valid(
            'd',
            gen = zqh_tl_bundle_d, 
            p = self.p.channel['d']).flip())
        if (self.p.tl_type == 'tl_c'):
            self.var(ready_valid(
                'e', 
                gen = zqh_tl_bundle_e,
                p = self.p.channel['e']))

    def tieoff(self):
        if (isinstance(self.a.ready, inp)):
            self.a.ready /= 0 
            if (self.p.tl_type == 'tl_c'):
                self.c.ready /= 0 
                self.e.ready /= 0 
                self.b.valid /= 0 
            self.d.valid /= 0 
        elif (isinstance(self.a.ready, outp)):
            self.a.valid /= 0 
            if (self.p.tl_type == 'tl_c'):
                self.c.valid /= 0 
                self.e.valid /= 0 
                self.b.ready /= 0 
            self.d.ready /= 0 

    def sop_eop_a(self):
        return self.sop_eop('a')

    def sop_eop_b(self):
        return self.sop_eop('b')

    def sop_eop_c(self):
        return self.sop_eop('c')

    def sop_eop_d(self):
        return self.sop_eop('d')

    def sop_eop_e(self):
        return self.sop_eop('e')

    def sop_eop(self, channel):
        sel_channel = self[channel]
        size_1_more_flit = (
            sel_channel.bits.size > 
            log2_ceil(sel_channel.bits.p.data_bits//8))
        if (channel == 'a'):
            req_is_1_more_flit = sel_channel.bits.opcode.match_any([
                TMSG_CONSTS.put_full_data(), 
                TMSG_CONSTS.put_partial_data()]) & size_1_more_flit
        elif (channel == 'c'):
            req_is_1_more_flit = sel_channel.bits.opcode.match_any([
                TMSG_CONSTS.release_data(),
                TMSG_CONSTS.probe_ack_data()]) & size_1_more_flit
        elif (channel == 'e'):
            req_is_1_more_flit = value(0).to_bits()
        elif (channel == 'b'):
            req_is_1_more_flit = value(0).to_bits()
        elif (channel == 'd'):
            req_is_1_more_flit = sel_channel.bits.opcode.match_any([
                TMSG_CONSTS.grant_data(),
                TMSG_CONSTS.access_ack_data()]) & size_1_more_flit
        else:
            assert(0)
        return self.sop_eop_com(sel_channel, req_is_1_more_flit)
