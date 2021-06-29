import sys
import os
from phgl_imp import *
from .zqh_core_common_misc import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter

class zqh_core_common_alu(module):
    def set_par(self):
        super(zqh_core_common_alu, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_port(self):
        super(zqh_core_common_alu, self).set_port()
        self.io.var(inp('dw'))
        self.io.var(inp('op', w = A_CONSTS.SZ))
        self.io.var(inp('in1', w = self.p.xlen))
        self.io.var(inp('in2', w = self.p.xlen))
        self.io.var(outp('out', w = self.p.xlen))
        self.io.var(outp('add_out', w = self.p.xlen))
        self.io.var(outp('cmp_out'))

    def main(self):
        super(zqh_core_common_alu, self).main()
        
        ####
        #add, sub
        need_sub = self.io.op.match_any([
            A_CONSTS.FN_SUB(),
            A_CONSTS.FN_SLT(),
            A_CONSTS.FN_SGE(),
            A_CONSTS.FN_SLTU(),
            A_CONSTS.FN_SGEU()])
        in2_inv = mux(need_sub, ~self.io.in2, self.io.in2)
        add_sub = (self.io.in1 + in2_inv + need_sub)[self.p.xlen - 1 : 0]


        ####
        #logic
        logic_xor = self.io.in1 ^ self.io.in2
        logic_or = self.io.in1 | self.io.in2
        logic_and = self.io.in1 & self.io.in2


        ####
        #shift
        if (self.p.xlen == 64):
            shift_amt = cat([mux(self.io.dw, self.io.in2[5], 0),self.io.in2[4:0]])
            shift_in1 = cat([mux(
                self.io.dw,
                self.io.in1[63:32],
                mux(
                    self.io.op == A_CONSTS.FN_SRA(),
                    self.io.in1[31].rep(32),
                    value(0, w = 32))), self.io.in1[31:0]])
        else:
            shift_amt = self.io.in2[4:0]
            shift_in1 = self.io.in1
        shift_in1_sel = mux(
            self.io.op.match_any([A_CONSTS.FN_SR(), A_CONSTS.FN_SRA()]),
            shift_in1,
            shift_in1.order_invert())
        shift_r = (cat([mux(
            self.io.op == A_CONSTS.FN_SRA(),
            shift_in1_sel[self.p.xlen-1], 0),
            shift_in1_sel]).as_sint() >> shift_amt)[self.p.xlen-1:0]
        shift_l = shift_r.order_invert()


        ####
        #compare
        cmp_slt_sltu = mux(
            self.io.in1[self.p.xlen-1] == self.io.in2[self.p.xlen-1],
            add_sub[self.p.xlen-1],
            mux(
                self.io.op.match_any([A_CONSTS.FN_SLTU(), A_CONSTS.FN_SGEU()]),
                self.io.in2[self.p.xlen-1],
                self.io.in1[self.p.xlen-1]))
        cmp_sge_sgeu = ~cmp_slt_sltu
        cmp_eq = logic_xor == 0
        cmp_neq = ~cmp_eq


        ####
        #output
        last_out = sel_oh((
            (self.io.op.match_any([A_CONSTS.FN_ADD(), A_CONSTS.FN_SUB()]) , add_sub     ),
            (self.io.op.match_any([A_CONSTS.FN_XOR()])                    , logic_xor   ),
            (self.io.op.match_any([A_CONSTS.FN_OR()])                     , logic_or    ),
            (self.io.op.match_any([A_CONSTS.FN_AND()])                    , logic_and   ),
            (self.io.op.match_any([A_CONSTS.FN_SL()])                     , shift_l     ),
            (self.io.op.match_any([A_CONSTS.FN_SR(), A_CONSTS.FN_SRA()])  , shift_r     ),
            (self.io.op.match_any([A_CONSTS.FN_SLT(), A_CONSTS.FN_SLTU()]), cmp_slt_sltu),
            (self.io.op.match_any([A_CONSTS.FN_SGE(), A_CONSTS.FN_SGEU()]), cmp_sge_sgeu),
            (self.io.op.match_any([A_CONSTS.FN_SEQ()])                    , cmp_eq      ),
            (self.io.op.match_any([A_CONSTS.FN_SNE()])                    , cmp_neq     )))
        if (self.p.xlen == 64):
            self.io.out /= mux(
                self.io.dw,
                last_out,
                cat([last_out[31].rep(32), last_out[31:0]]))
        else:
            self.io.out /= last_out

        self.io.cmp_out /= sel_oh((
            (self.io.op.match_any([A_CONSTS.FN_SLT(), A_CONSTS.FN_SLTU()]), cmp_slt_sltu),
            (self.io.op.match_any([A_CONSTS.FN_SGE(), A_CONSTS.FN_SGEU()]), cmp_sge_sgeu),
            (self.io.op.match_any([A_CONSTS.FN_SEQ()])                    , cmp_eq      ),
            (self.io.op.match_any([A_CONSTS.FN_SNE()])                    , cmp_neq     )))

        self.io.add_out /= add_sub
