####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/Multiplier.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_core_common_multiplier_bundles import *
from .zqh_core_common_multiplier_parameters import zqh_core_common_multiplier_parameter

class zqh_core_common_multiplier(module):
    def set_par(self):
        super(zqh_core_common_multiplier, self).set_par()
        self.p.par('cfg', zqh_core_common_multiplier_parameter())
        self.p.par('width', 0)
        self.p.par('tag_bits', 0)

    def set_port(self):
        super(zqh_core_common_multiplier, self).set_port()
        self.io = zqh_core_common_multiplier_io(
            'io',
            data_bits = self.p.width,
            tag_bits = self.p.tag_bits)

    def main(self):
        super(zqh_core_common_multiplier, self).main()
        self.ww = self.io.req.bits.in1.get_w()
        mulw = (
            (self.ww + self.p.cfg.mul_unroll - 1) // 
            self.p.cfg.mul_unroll) * self.p.cfg.mul_unroll
        fastMulW = (
            ((self.ww//2) > self.p.cfg.mul_unroll) & 
            (self.ww % (2*self.p.cfg.mul_unroll) == 0))
 
        (
            s_ready, s_neg_inputs, s_mul, s_div, 
            s_dummy, s_neg_output, s_done_mul, s_done_div) = range(8)
        state = reg_rs('state', rs=s_ready, w = 3)
 
        req = zqh_core_common_multiplier_req('req', p = self.io.req.bits.p).as_reg()
        cout_w = log2_ceil(max((self.ww//self.p.cfg.div_unroll + 1),
            mulw//self.p.cfg.mul_unroll))
        count = reg('count', w = cout_w)
        neg_out = reg('neg_out')
        isHi = reg('isHi')
        resHi = reg('resHi')
        divisor = reg('divisor', w = self.ww+1) ## div only needs w bits
        remainder = reg('remainder', w = 2*mulw+2) ## div only needs 2*w+1 bits

        cmdMul = self.io.req.bits.fn.match_any([
            A_CONSTS.FN_MUL(),
            A_CONSTS.FN_MULH(),
            A_CONSTS.FN_MULHU(),
            A_CONSTS.FN_MULHSU()])
        cmdHi = (self.io.req.bits.fn.match_any([
            A_CONSTS.FN_MULH  (),
            A_CONSTS.FN_MULHU (),
            A_CONSTS.FN_MULHSU()])) | (self.io.req.bits.fn.match_any([
                A_CONSTS.FN_REM (),
                A_CONSTS.FN_REMU()]))
        lhsSigned = (self.io.req.bits.fn.match_any([
            A_CONSTS.FN_MULH(),
            A_CONSTS.FN_MULHSU()])) | (self.io.req.bits.fn.match_any([
                A_CONSTS.FN_DIV(),
                A_CONSTS.FN_REM()]))
        rhsSigned = (self.io.req.bits.fn.match_any([
            A_CONSTS.FN_MULH()])) | (self.io.req.bits.fn.match_any([
                A_CONSTS.FN_DIV(),
                A_CONSTS.FN_REM()]))

        assert(self.ww == 32 or self.ww == 64)

        (lhs_in, lhs_sign) = self.sext(
            self.io.req.bits.in1,
            self.halfWidth(self.io.req.bits),
            lhsSigned)
        (rhs_in, rhs_sign) = self.sext(
            self.io.req.bits.in2, 
            self.halfWidth(self.io.req.bits), 
            rhsSigned)
        
        subtractor = remainder[2*self.ww:self.ww] - divisor
        result = mux(resHi, remainder[2*self.ww: self.ww+1], remainder[self.ww-1: 0])
        negated_remainder = -result

        with when (state == s_neg_inputs):
            with when (remainder[self.ww-1]):
                remainder /= negated_remainder
            with when (divisor[self.ww-1]):
                divisor /= subtractor
            state /= s_div
        with when (state == s_neg_output):
          remainder /= negated_remainder
          state /= s_done_div
          resHi /= 0
        with when (state == s_mul):
            mulReg = cat([remainder[2*mulw+1:self.ww+1],remainder[self.ww-1:0]])
            mplierSign = remainder[self.ww]
            mplier = mulReg[mulw-1:0]
            accum = mulReg[2*mulw:mulw].as_sint()
            mpcand = divisor.as_sint()
            mpcand.as_sint()
            prod = cat([
                mplierSign,
                mplier[self.p.cfg.mul_unroll-1: 0]]).as_sint() * mpcand + accum
            nextMulReg = cat([prod, mplier[mulw-1: self.p.cfg.mul_unroll]])
            nextMplierSign = (count == (mulw//self.p.cfg.mul_unroll)-2) & neg_out

            eOutMask = (
                value(1 << mulw, w = mulw + 1).to_bits().as_sint() >> 
                (count * self.p.cfg.mul_unroll)[log2_up(mulw)-1:0])[mulw-1:0]
            eOut = (
                self.p.cfg.mul_early_out & 
                (count != (mulw//self.p.cfg.mul_unroll)-1) & 
                (count != 0) & 
                ~isHi & 
                ((mplier & ~eOutMask) == 0))
            eOutRes = (mulReg >> (mulw - count * self.p.cfg.mul_unroll)[log2_up(mulw)-1:0])
            nextMulReg1 = cat([
                nextMulReg[2*mulw:mulw],
                mux(eOut, eOutRes, nextMulReg)[mulw-1:0]])
            remainder /= cat([
                nextMulReg1 >> self.ww,
                nextMplierSign,
                nextMulReg1[self.ww-1:0]])

            count /= count + 1
            with when (eOut | (count == (mulw//self.p.cfg.mul_unroll)-1)):
                state /= s_done_mul
                resHi /= isHi
        with when (state == s_div):
            unrolls = []
            rem = remainder
            unrolls.append(rem)
            for i in range(self.p.cfg.div_unroll):
                ## the special case for iteration 0 is to save HW, not for correctness
                difference = (
                    subtractor if (i == 0) else rem[
                        2*self.ww:self.ww] - divisor[self.ww-1:
                        0])
                less = difference[self.ww]
                rem = cat([
                    mux(less, rem[2*self.ww-1:self.ww], difference[self.ww-1:0]),
                    rem[self.ww-1:0], ~less])
                unrolls.append(rem)
            unrolls = unrolls[1:]

            remainder /= unrolls[-1]
            with when (count == (self.ww//self.p.cfg.div_unroll)):
                state /= mux(neg_out, s_neg_output, s_done_div)
                resHi /= isHi
                if (self.ww % self.p.cfg.div_unroll < self.p.cfg.div_unroll - 1):
                    remainder /= unrolls[self.ww % self.p.cfg.div_unroll]
            count /= count + 1

            divby0 = (count == 0) & ~subtractor[self.ww]
            if (self.p.cfg.div_early_out):
                divisorMSB = divisor[self.ww-1:0].is_log2(self.ww)
                dividendMSB = remainder[self.ww-1:0].is_log2(self.ww)
                eOutPos = (
                    (self.ww-1) + divisorMSB - dividendMSB)[
                        value(self.ww - 1).get_w() - 1 : 0]
                eOutZero = divisorMSB > dividendMSB
                eOut = (
                    (count == 0) & 
                    ~divby0 & 
                    ((eOutPos >= self.p.cfg.div_unroll) | eOutZero))
                with when (eOut):
                    inc = mux(
                        eOutZero,
                        self.ww-1,
                        eOutPos) >> log2_floor(self.p.cfg.div_unroll)
                    shift = inc << log2_floor(self.p.cfg.div_unroll)
                    remainder /= remainder[self.ww-1:0] << shift
                    count /= inc
            with when (divby0 & ~isHi):
                neg_out /= 0
        with when (self.io.resp.fire() | self.io.kill):
            state /= s_ready
        with when (self.io.req.fire()):
            state /= mux(cmdMul, s_mul, mux(lhs_sign | rhs_sign, s_neg_inputs, s_div))
            isHi /= cmdHi
            resHi /= 0
            count /= mux(
                cmdMul & self.halfWidth(self.io.req.bits),
                (self.ww//self.p.cfg.mul_unroll)//2, 0) if (fastMulW) else 0
            neg_out /= mux(cmdHi, lhs_sign, lhs_sign != rhs_sign)
            divisor /= cat([rhs_sign, rhs_in])
            remainder /= lhs_in
            req /= self.io.req.bits

        outMul = (state & (s_done_mul ^ s_done_div)) == (s_done_mul & ~s_done_div)
        loOut = mux(
            fastMulW & self.halfWidth(req) & outMul,
            result[self.ww-1:self.ww//2],
            result[self.ww//2-1:0])
        hiOut = mux(
            self.halfWidth(req),
            loOut[self.ww//2-1].rep(self.ww//2),
            result[self.ww-1:self.ww//2])
        self.io.resp.bits /= req
        self.io.resp.bits.data /= cat([hiOut, loOut])
        self.io.resp.valid /= ((state == s_done_mul) | (state == s_done_div))
        self.io.req.ready /= state == s_ready

    def halfWidth(self, req):
        return (self.ww > 32) & (req.dw == D_CONSTS.DW_32())

    def sext(self, x, halfW, signed):
        sign = signed & mux(halfW, x[self.ww//2-1], x[self.ww-1])
        hi = mux(halfW, sign.rep(self.ww//2), x[self.ww-1:self.ww//2])
        return (cat([hi, x[(self.ww//2)-1:0]]), sign)

class zqh_core_common_pipelined_multiplier(module):
    def set_par(self):
        super(zqh_core_common_pipelined_multiplier, self).set_par()
        self.p.par('width', 0)
        self.p.par('latency', 0)
        self.p.par('tag_bits', 0)

    def set_port(self):
        super(zqh_core_common_pipelined_multiplier, self).set_port()
        self.io.var(valid(
            'req',
            gen = zqh_core_common_multiplier_req,
            data_bits = self.p.width,
            tag_bits = self.p.tag_bits).flip())
        self.io.var(valid(
            'resp',
            gen = zqh_core_common_multiplier_resp,
            data_bits = self.p.width,
            tag_bits = self.p.tag_bits))

    def main(self):
        super(zqh_core_common_pipelined_multiplier, self).main()
        in_ = pipe(self.io.req)

        cmdHi = in_.bits.fn.match_any([
            A_CONSTS.FN_MULH(),
            A_CONSTS.FN_MULHU(),
            A_CONSTS.FN_MULHSU()])
        lhsSigned = in_.bits.fn.match_any([
            A_CONSTS.FN_MULHU(),
            A_CONSTS.FN_MULHSU()])
        rhsSigned = in_.bits.fn.match_any([
            A_CONSTS.FN_MULHU(),
            A_CONSTS.FN_MULHSU()])
        cmdHalf = (self.p.width > 32) & (in_.bits.dw == D_CONSTS.DW_32())

        lhs = cat([lhsSigned & in_.bits.in1[self.p.width-1], in_.bits.in1]).as_sint()
        rhs = cat([rhsSigned & in_.bits.in2[self.p.width-1], in_.bits.in2]).as_sint()
        prod = lhs * rhs
        muxed = mux(
            cmdHi,
            prod[2*self.p.width-1: self.p.width],
            mux(
                cmdHalf,
                prod[(self.p.width//2)-1: 0].s_ext(self.p.width),
                prod[self.p.width-1: 0]))

        self.io.resp /= pipe(in_, self.p.latency-1)
        self.io.resp.bits.data /= pipe(muxed, self.p.latency-1)

class zqh_core_common_multiplier_stub(module):
    def set_par(self):
        super(zqh_core_common_multiplier_stub, self).set_par()
        self.p.par('cfg', zqh_core_common_multiplier_parameter())
        self.p.par('width', 0)
        self.p.par('tag_bits', 0)

    def set_port(self):
        super(zqh_core_common_multiplier_stub, self).set_port()
        self.io = zqh_core_common_multiplier_io(
            'io',
            data_bits = self.p.width,
            tag_bits = self.p.tag_bits)

    def main(self):
        super(zqh_core_common_multiplier_stub, self).main()

        self.io.req.ready /= 1
        self.io.resp.valid /= 0
        self.io.resp.bits /= 0
