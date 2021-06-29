####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/AMOALU.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_core_common_misc import *

class zqh_core_common_amo_alu(module):
    def set_par(self):
        super(zqh_core_common_amo_alu, self).set_par()
        self.p.par('width', None)

    def set_port(self):
        super(zqh_core_common_amo_alu, self).set_port()
        assert(self.p.width == 32 or self.p.width == 64)
        self.io.var(inp('mask', w = self.p.width//8))
        self.io.var(inp('cmd', w = M_CONSTS.SZ))
        self.io.var(inp('lhs', w = self.p.width))
        self.io.var(inp('rhs', w = self.p.width))
        self.io.var(outp('out', w = self.p.width))

    def main(self):
        super(zqh_core_common_amo_alu, self).main()
        cmd_max = (
            (self.io.cmd == M_CONSTS.M_XA_MAX()) | 
            (self.io.cmd == M_CONSTS.M_XA_MAXU()))
        cmd_min = (
            (self.io.cmd == M_CONSTS.M_XA_MIN()) |
            (self.io.cmd == M_CONSTS.M_XA_MINU()))
        cmd_add = self.io.cmd == M_CONSTS.M_XA_ADD()
        cmd_logic_and = (
            (self.io.cmd == M_CONSTS.M_XA_OR()) |
            (self.io.cmd == M_CONSTS.M_XA_AND()))
        cmd_logic_xor = (
            (self.io.cmd == M_CONSTS.M_XA_XOR()) |
            (self.io.cmd == M_CONSTS.M_XA_OR()))

        if (self.p.width == 32):
            adder_out = self.io.lhs + self.io.rhs
        else:
            mask = ~value(0,64).to_bits() ^ (~self.io.mask[3] << 31)
            adder_out = (self.io.lhs & mask) + (self.io.rhs & mask)

        mask = M_CONSTS.M_XA_MIN().to_bits() ^ M_CONSTS.M_XA_MINU().to_bits()
        sgned = (self.io.cmd & mask) == (M_CONSTS.M_XA_MIN() & mask)

        if (self.p.width == 32):
            less = mux(
                self.io.lhs[31] == self.io.rhs[31],
                self.io.lhs < self.io.rhs,
                mux(sgned, self.io.lhs[31], self.io.rhs[31]))
        else:
            msb_lhs = mux(~self.io.mask[4], self.io.lhs[31], self.io.lhs[63])
            msb_rhs = mux(~self.io.mask[4], self.io.rhs[31], self.io.rhs[63])
            lt_lo = self.io.lhs[31:0] < self.io.rhs[31:0]
            lt_hi = self.io.lhs[63:32] < self.io.rhs[63:32]
            eq_hi = self.io.lhs[63:32] == self.io.rhs[63:32]
            lt = mux(self.io.mask[4] & self.io.mask[3], lt_hi | (eq_hi & lt_lo),
                mux(self.io.mask[4], lt_hi, lt_lo))
            less = mux(msb_lhs == msb_rhs, lt, mux(sgned, msb_lhs, msb_rhs))

        minmax = mux(
            mux(less, cmd_min, cmd_max),
            self.io.lhs,
            self.io.rhs)
        logic = mux(
            cmd_logic_and,
            self.io.lhs & self.io.rhs, 0) | mux(
                cmd_logic_xor,
                self.io.lhs ^ self.io.rhs,
                0)
        out = mux(
            cmd_add,
            adder_out,
            mux(
                cmd_logic_and | cmd_logic_xor,
                logic,
                minmax))

        wmask = self.io.mask.rep_each_bit(8)
        self.io.out /= (wmask & out) | (~wmask & self.io.lhs)
