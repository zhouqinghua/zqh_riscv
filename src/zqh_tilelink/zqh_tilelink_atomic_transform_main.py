import sys
import os
from phgl_imp import *
from .zqh_tilelink_interfaces import zqh_tl_interface_in
from .zqh_tilelink_interfaces import zqh_tl_interface_out
from .zqh_tilelink_misc import TMSG_CONSTS
from .zqh_tilelink_misc import TAMO_CONSTS
from .zqh_tilelink_bundles import zqh_tl_bundle

class zqh_tilelink_atomic_transform_module(module):
    def set_par(self):
        super(zqh_tilelink_atomic_transform_module, self).set_par()
        self.p.par('node', None)
        self.p.par('bundle_in', None)
        self.p.par('amo', None)

    def set_port(self):
        super(zqh_tilelink_atomic_transform_module, self).set_port()
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        bundle_out = type(self.p.bundle_in)()
        bundle_out.sync_all(self.p.bundle_in)
        bundle_out.update_source_bits(self.p.bundle_in.channel['a'].source_bits + 1)
        self.io.var(zqh_tl_bundle('tl_out', p = bundle_out))

    def main(self):
        super(zqh_tilelink_atomic_transform_module, self).main()
        interfaceIn = zqh_tl_interface_in(
            slave_nodes = self.p.node.get_nearest_slave_nodes(),
            bundle = self.io.tl_in.p)
        interface_out = zqh_tl_interface_out(
            slave_nodes = self.p.node.get_nearest_slave_nodes(), 
            bundle = self.io.tl_out.p)

        req_buf = queue(
            'req_buf',
            gen = type(self.io.tl_in.a.bits),
            gen_p = self.io.tl_in.a.bits.p,
            entries = 2)
        req_buf.io.enq /= self.io.tl_in.a

        source_amo = self.io.tl_out.p.channel['a'].source_bits - 1

        a_valid = req_buf.io.deq.valid
        a_req = req_buf.io.deq.bits
        a_req_arithmetic_valid = a_valid & (a_req.opcode == TMSG_CONSTS.arithmetic_data())
        a_req_logical_valid = a_valid & (a_req.opcode == TMSG_CONSTS.logical_data())
        a_req_amo_valid = a_req_arithmetic_valid | a_req_logical_valid

        out_a_sop_eop = self.io.tl_out.sop_eop_a()
        out_a_amo = self.io.tl_out.a.bits.source[source_amo]
        out_d_sop_eop = self.io.tl_out.sop_eop_d()
        out_d_amo = self.io.tl_out.d.bits.source[source_amo]

        (s_ready, s_get, s_get_wait_ack, s_put, s_d_resp) = range(5)
        amo_state = reg_rs('amo_state', rs = s_ready, w = 3)
        d_resp_early_next = bits('d_resp_early_next', init = 0)
        d_resp_amo_valid = bits('d_resp_amo_valid', init = self.io.tl_out.d.valid & out_d_amo)
        # d_resp valid before or same time a_req's eop
        d_resp_early = reg_r('d_resp_early', next = d_resp_early_next)

        with when(amo_state == s_ready):
            with when(a_req_amo_valid):
                amo_state /= s_get
        with when(amo_state == s_get):
            with when(self.io.tl_out.a.fire() & out_a_amo):
                with when(out_d_sop_eop.eop & out_d_amo): # no need wait d_resp
                    amo_state /= s_put
                with other():
                    amo_state /= s_get_wait_ack
            with when(self.io.tl_out.d.fire() & out_d_amo):
                d_resp_early_next /= 1
        with when(amo_state == s_get_wait_ack):
            with when(out_d_sop_eop.eop & out_d_amo):
                amo_state /= s_put
        with when(amo_state == s_put):
            with when(out_a_sop_eop.eop & out_a_amo):
                with when(d_resp_early_next | d_resp_early): # no need wait d_resp
                    amo_state /= s_ready
                with other():
                    amo_state /= s_d_resp

            with when(out_a_sop_eop.sop & out_a_amo):
                with when(self.io.tl_out.d.fire() & out_d_amo):
                    d_resp_early_next /= 1
                with other():
                    d_resp_early_next /= 0
            with other():
                with when(self.io.tl_out.d.fire() & out_d_amo):
                    d_resp_early_next /= 1
                with other():
                    d_resp_early_next /= d_resp_early
        with when(amo_state == s_d_resp):
            with when(out_d_sop_eop.eop & out_d_amo):
                amo_state /= s_ready

        self.io.tl_out.a.valid /= req_buf.io.deq.valid
        self.io.tl_out.a.bits /= req_buf.io.deq.bits
        get_req = self.io.tl_out.a.bits.clone()
        get_req /= a_req
        get_req.opcode /= TMSG_CONSTS.get()
        get_req.source /= cat([value(1), a_req.source]) #msb set 1: means atomic
        get_req.param /= 0
        with when(a_req_amo_valid):
            self.io.tl_out.a.valid /= 0
        with when(amo_state == s_get):
            self.io.tl_out.a.valid /= 1
            self.io.tl_out.a.bits /= get_req

        get_data = reg('get_data', w = self.io.tl_out.d.bits.data.get_w())
        with when(
            (amo_state == s_get_wait_ack) | 
            ((amo_state == s_get) & d_resp_early_next)):
            with when(out_d_sop_eop.eop & out_d_amo):
                get_data /= self.io.tl_out.d.bits.data

        def zqh_tilelink_amo_alu(mask, arithmetic_valid, param, lhs, rhs):
            max_ = (
                arithmetic_valid & 
                (
                    (param == TAMO_CONSTS.max()) | 
                    (param == TAMO_CONSTS.maxu())))
            min_ = (
                arithmetic_valid & 
                (
                    (param == TAMO_CONSTS.min()) | 
                    (param == TAMO_CONSTS.minu())))
            add = arithmetic_valid & (param == TAMO_CONSTS.add())
            logic_and = (
                ~arithmetic_valid & 
                (
                    (param == TAMO_CONSTS.orr()) | 
                    (param == TAMO_CONSTS.andd())))
            logic_xor = (
                ~arithmetic_valid & 
                (
                    (param == TAMO_CONSTS.xor()) | 
                    (param == TAMO_CONSTS.orr())))
            logic_swap = ~arithmetic_valid & (param == TAMO_CONSTS.swap())
        
            if (lhs.get_w() < 64):
                adder_out = lhs + rhs
            else:
                tmp_mask = ~value(0, w = lhs.get_w()).to_bits() ^ (~mask[3] << 31)
                adder_out = (lhs & tmp_mask) + (rhs & tmp_mask)
        
            sgned = param.match_any([TAMO_CONSTS.max(), TAMO_CONSTS.min()])
        
            if (lhs.get_w() < 64):
                less = mux(lhs[31] == rhs[31], lhs < rhs, mux(sgned, lhs[31], rhs[31]))
            else:
                cmp_lhs = mux(~mask[4], lhs[31], lhs[lhs.get_w()-1])
                cmp_rhs = mux(~mask[4], rhs[31], rhs[lhs.get_w()-1])
                lt_lo = lhs[31:0] < rhs[31:0]
                lt_hi = lhs[lhs.get_w()-1:32] < rhs[lhs.get_w()-1:32]
                eq_hi = lhs[lhs.get_w()-1:32] == rhs[lhs.get_w()-1:32]
                lt = mux(mask[4] & mask[3], lt_hi | (eq_hi & lt_lo),
                    mux(mask[4], lt_hi, lt_lo))
                less = mux(cmp_lhs == cmp_rhs, lt, mux(sgned, cmp_lhs, cmp_rhs))
        
            minmax = mux(mux(less, min_, max_), lhs, rhs)
            logic = mux(logic_and, lhs & rhs, 0) | mux(logic_xor, lhs ^ rhs, 0)
            out = mux(add,adder_out, mux(logic_and | logic_xor, logic, minmax))
        
            wmask = mask.rep_each_bit(8)
            return (wmask & out) | (~wmask & lhs)
        rmw_data = zqh_tilelink_amo_alu(
            a_req.mask, 
            a_req_arithmetic_valid,
            a_req.param, 
            get_data, 
            a_req.data)
        put_req = interface_out.put(
            cat([value(1), a_req.source]),
            a_req.address,
            a_req.size, 
            rmw_data)[1]
        with when(amo_state == s_put):
            self.io.tl_out.a.valid /= 1
            self.io.tl_out.a.bits /= put_req

        self.io.tl_in.d.valid /= 0
        with when(~out_d_amo):
            self.io.tl_in.d.valid /= self.io.tl_out.d.valid
        with elsewhen(
            amo_state.match_any([s_d_resp]) | 
            #tmp ((amo_state == s_put) & (d_resp_early_next | d_resp_early))):
            ((amo_state == s_put) & (d_resp_amo_valid | d_resp_early))):
            self.io.tl_in.d.valid /= self.io.tl_out.d.valid

        self.io.tl_in.d.bits /= self.io.tl_out.d.bits
        with when((amo_state == s_d_resp) | (amo_state == s_put)):
            self.io.tl_in.d.bits.opcode /= TMSG_CONSTS.access_ack_data()
            self.io.tl_in.d.bits.data /= get_data

        req_buf.io.deq.ready /= self.io.tl_out.a.ready
        with when(a_req.opcode.match_any([
            TMSG_CONSTS.arithmetic_data(),
            TMSG_CONSTS.logical_data()])):
            req_buf.io.deq.ready /= 0
        with when((amo_state == s_d_resp) | (amo_state == s_put)):
            with when(out_d_sop_eop.eop & out_d_amo):
                req_buf.io.deq.ready /= 1
        self.io.tl_out.d.ready /= self.io.tl_in.d.ready

def zqh_tilelink_atomic_transform(node, tl_in, p):
    amo_fix = zqh_tilelink_atomic_transform_module(
        'amo_fix',
        node = node,
        bundle_in = tl_in.p,
        amo = p)
    amo_fix.io.tl_in /= tl_in
    return amo_fix.io.tl_out
