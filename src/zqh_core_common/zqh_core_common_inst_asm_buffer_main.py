import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_cpu_resp
from .zqh_core_common_inst_asm_buffer_bundles import zqh_core_common_inst_asm_buffer_data
from .zqh_core_common_rvc_main import zqh_core_common_rvc_expander

class zqh_core_common_inst_asm_buffer(module):
    def set_par(self):
        super(zqh_core_common_inst_asm_buffer, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_port(self):
        super(zqh_core_common_inst_asm_buffer, self).set_port()
        self.io.var(ready_valid('ifu_resp', gen = zqh_core_common_ifu_cpu_resp).flip())
        self.io.var(ready_valid('out', gen = zqh_core_common_inst_asm_buffer_data))
        self.io.var(outp('partial_valid'))
        self.io.var(inp('flush'))
        self.io.var(inp('rv64'))

    def main(self):
        super(zqh_core_common_inst_asm_buffer, self).main()

        inst_buffer = zqh_core_common_inst_asm_buffer_data('inst_buffer').as_reg()
        inst_buffer_in = zqh_core_common_inst_asm_buffer_data(
            'inst_buffer_in',
            init = inst_buffer)
        inst_buffer /= inst_buffer_in
        inst_buffer_bypass = bits('inst_buffer_bypass')
        inst_buffer_valid = reg_r('inst_buffer_valid')
        inst_buffer_partial = reg_r('inst_buffer_partial')
        inst_idx_reg = reg_r('inst_idx_reg')
        inst_idx = mux(self.io.ifu_resp.bits.pc[1], 1, inst_idx_reg)
        inst_pc = cat([self.io.ifu_resp.bits.pc[self.p.vaddr_bits - 1 : 2], inst_idx, 0])
        inst_w = self.io.ifu_resp.bits.inst
        inst_hw = mux(
            inst_idx,
            self.io.ifu_resp.bits.inst[31:16],
            self.io.ifu_resp.bits.inst[15:0])
        inst_hw_iv = sel_bin(inst_idx, self.io.ifu_resp.bits.iv.grouped())
        inst_rvc_code = inst_hw[1:0]
        inst_is_rvc = ~inst_buffer_partial & (inst_rvc_code != 3)
        inst_taken = (
            sel_bin(inst_idx, self.io.ifu_resp.bits.taken.grouped()) 
            if (self.p.use_btb) else 0)
        inst_btb_hit = (
            sel_bin(inst_idx, self.io.ifu_resp.bits.btb_hit.grouped()) 
            if (self.p.use_btb) else 0)
        inst_bht_info = self.io.ifu_resp.bits.bht_info if (self.p.use_bht) else 0

        if (self.p.isa_c):
            expander = zqh_core_common_rvc_expander('expander')
            expander.io.inst_in /= inst_hw
            expander.io.rv64 /= self.io.rv64
            expand_inst = mux(inst_is_rvc, expander.io.inst_out, inst_w)
        else:
            expand_inst = inst_w

        inst_buffer_bypass /= (
            ~inst_buffer_valid & 
            ~inst_buffer_partial & 
            ~(~inst_is_rvc & inst_idx & inst_hw_iv))

        with when(self.io.flush):
            inst_buffer_valid /= 0
            inst_buffer_partial /= 0
            inst_idx_reg /= 0
        with elsewhen((~inst_buffer_valid | self.io.out.ready) & self.io.ifu_resp.valid):
            with when(inst_hw_iv):
                push_buffer = ~inst_buffer_bypass | ~self.io.out.ready
                with when(inst_is_rvc):
                    inst_buffer_valid /= push_buffer
                    inst_buffer_in.inst /= expand_inst
                    inst_buffer_in.btb_hit /= inst_btb_hit
                    inst_buffer_in.taken /= inst_taken
                    inst_buffer_in.bht_info /= inst_bht_info
                    inst_buffer_in.rvc /= 1
                    inst_buffer_in.pc /= inst_pc
                    inst_buffer_in.xcpt /= self.io.ifu_resp.bits.xcpt
                    inst_idx_reg /= ~inst_idx
                with elsewhen(inst_buffer_partial):
                    inst_buffer_partial /= 0
                    inst_buffer_valid /= push_buffer
                    inst_buffer_in.inst[31:16] /= expand_inst[15:0]
                    inst_buffer_in.btb_hit /= inst_btb_hit
                    inst_buffer_in.taken /= inst_taken
                    inst_buffer_in.bht_info /= inst_bht_info
                    inst_buffer_in.rvc /= 0
                    inst_buffer_in.xcpt /= (
                        self.io.ifu_resp.bits.xcpt.pack() | 
                        inst_buffer.xcpt.pack())
                    inst_idx_reg /= 1
                with elsewhen(inst_idx == 0):
                    inst_buffer_valid /= push_buffer
                    inst_buffer_in.inst /= expand_inst
                    inst_buffer_in.btb_hit /= inst_btb_hit
                    inst_buffer_in.taken /= inst_taken
                    inst_buffer_in.bht_info /= inst_bht_info
                    inst_buffer_in.rvc /= 0
                    inst_buffer_in.pc /= inst_pc
                    inst_buffer_in.xcpt /= self.io.ifu_resp.bits.xcpt
                    inst_idx_reg /= 0
                with other():
                    inst_buffer_partial /= 1
                    inst_buffer_valid /= 0
                    inst_buffer_in.inst[15:0] /= expand_inst[31:16]
                    inst_buffer_in.btb_hit /= inst_btb_hit
                    inst_buffer_in.taken /= inst_taken
                    inst_buffer_in.bht_info /= inst_bht_info
                    inst_buffer_in.rvc /= 0
                    inst_buffer_in.pc /= inst_pc
                    inst_buffer_in.xcpt /= self.io.ifu_resp.bits.xcpt
                    inst_idx_reg /= 0
            with other():
                inst_buffer_partial /= 0
                inst_buffer_valid /= 0
                inst_idx_reg /= 0
        with elsewhen(self.io.out.fire()):
            inst_buffer_valid /= 0

        with when(inst_buffer_bypass):
            self.io.out.valid /= self.io.ifu_resp.valid & inst_hw_iv
            self.io.out.bits.inst /= expand_inst
            self.io.out.bits.btb_hit /= inst_btb_hit
            self.io.out.bits.taken /= inst_taken
            self.io.out.bits.bht_info /= inst_bht_info
            self.io.out.bits.rvc /= inst_is_rvc
            self.io.out.bits.pc /= mux(inst_is_rvc, inst_pc, self.io.ifu_resp.bits.pc)
            self.io.out.bits.xcpt /= self.io.ifu_resp.bits.xcpt
        with other():
            self.io.out.valid /= inst_buffer_valid
            self.io.out.bits /= inst_buffer

        self.io.partial_valid /= inst_buffer_partial

        self.io.ifu_resp.ready /= 0
        with when(~inst_buffer_valid | self.io.out.ready):
            with when((inst_is_rvc & inst_idx) | #2nd half of ifu_resp is rvc
                      (~inst_is_rvc & ~inst_buffer_partial) | #no half inst buffered in inst_buffer
                      (~inst_hw_iv & inst_idx)): #2nd half of inst_resp is not valid(rvc/not rvc). need drop it
                self.io.ifu_resp.ready /= 1
