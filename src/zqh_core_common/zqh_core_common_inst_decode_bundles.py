#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/Decode.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_core_common_misc import *
from zqh_common.zqh_decode_logic import zqh_decode_logic

class zqh_core_common_inst(bundle):
    def set_var(self):
        super(zqh_core_common_inst, self).set_var()
        self.var(bits('rd', w = I_CONSTS.rd_w))
        self.var(bits('rs1', w = I_CONSTS.rs1_w))
        self.var(bits('rs2', w = I_CONSTS.rs2_w))
        self.var(bits('rs3', w = I_CONSTS.rs3_w))
        self.var(bits('funct3', w = I_CONSTS.funct3_w))
        self.var(bits('funct7', w = I_CONSTS.funct7_w))
        self.var(bits('fence_succ', w = I_CONSTS.fence_succ_w))
        self.var(bits('fence_pred', w = I_CONSTS.fence_pred_w))
        self.var(bits('rl'))
        self.var(bits('aq'))

    def split(self, inst):
        self.rd     /= inst[11: 7]
        self.funct3 /= inst[14:12]
        self.rs1    /= inst[19:15]
        self.rs2    /= inst[24:20]
        self.rs3    /= inst[31:27]
        self.funct7 /= inst[31:25]
        self.fence_succ /= inst[23:20]
        self.fence_pred /= inst[27:24]
        self.rl /= inst[25]
        self.aq /= inst[26]

class zqh_core_common_inst_decode_sigs(bundle):
    def set_var(self):
        super(zqh_core_common_inst_decode_sigs, self).set_var()
        self.var(bits('legal'))
        self.var(bits('fp'))
        self.var(bits('rocc'))
        self.var(bits('branch'))
        self.var(bits('jal'))
        self.var(bits('jalr'))
        self.var(bits('rxs2'))
        self.var(bits('rxs1'))
        self.var(bits('sel_alu2', w = D_CONSTS.A2_X().get_w()))
        self.var(bits('sel_alu1', w = D_CONSTS.A1_X().get_w()))
        self.var(bits('sel_imm', w = D_CONSTS.IMM_X().get_w()))
        self.var(bits('alu_dw'))
        self.var(bits('alu_fn', w = A_CONSTS.FN_X().get_w()))
        self.var(bits('mem'))
        self.var(bits('mem_cmd', w = M_CONSTS.SZ))
        self.var(bits('mem_type', w = D_CONSTS.SZ_MT))
        self.var(bits('rfs1'))
        self.var(bits('rfs2'))
        self.var(bits('rfs3'))
        self.var(bits('wfd'))
        self.var(bits('mul'))
        self.var(bits('div'))
        self.var(bits('wxd'))
        self.var(bits('csr_cmd', w = CSR_CONSTS.SZ))
        self.var(bits('fence_i'))
        self.var(bits('fence'))
        self.var(bits('amo'))
        self.var(bits('dp'))

    def default(self):
        ##           jal                                                                 renf1             fence.i
        ##   val     | jalr                                                              | renf2           |
        ##   | fp_val| | renx2                                                           | | renf3         |
        ##   | | rocc| | | renx1     s_alu1                          mem_val             | | | wfd         | 
        ##   | | | br| | | | s_alu2  |       imm    dw     alu       | mem_cmd   mem_type| | | | mul       | 
        ##   | | | | | | | | |       |       |      |      |         | |           |     | | | | | div     | fence
        ##   | | | | | | | | |       |       |      |      |         | |           |     | | | | | | wxd   | | amo
        ##   | | | | | | | | |       |       |      |      |         | |           |     | | | | | | |     | | | dp
        return [D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.A2_X(),   D_CONSTS.A1_X(),   D_CONSTS.IMM_X(), D_CONSTS.DW_X(),  A_CONSTS.FN_X(),     D_CONSTS.N(),M_CONSTS.M_X(),        D_CONSTS.MT_X(), D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),CSR_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X()]

    def decode(self, inst, table):
        decoder = zqh_decode_logic().decode_sig_list(inst, self.default(), table)
        sigs = [
            self.legal,
            self.fp,
            self.rocc,
            self.branch,
            self.jal,
            self.jalr,
            self.rxs2,
            self.rxs1,
            self.sel_alu2,
            self.sel_alu1,
            self.sel_imm,
            self.alu_dw,
            self.alu_fn,
            self.mem,
            self.mem_cmd,
            self.mem_type,
            self.rfs1,
            self.rfs2,
            self.rfs3,
            self.wfd,
            self.mul,
            self.div,
            self.wxd,
            self.csr_cmd,
            self.fence_i,
            self.fence,
            self.amo,
            self.dp]
        for (s, d) in map(lambda x,y:(x,y), sigs, decoder):
            s /= d
        return self
