import sys
import os
import copy
import types
from phgl_imp import *
from .zqh_core_r1_core_bundles import *
from .zqh_core_r1_misc import *
from zqh_core_common.zqh_core_common_misc import D_CONSTS
from zqh_core_common.zqh_core_common_misc import M_CONSTS
from zqh_core_common.zqh_core_common_misc import A_CONSTS
from zqh_core_common.zqh_core_common_misc import IFU_CONSTS
from zqh_core_common.zqh_core_common_misc import CS_CONSTS
from zqh_core_common.zqh_core_common_misc import CSR_CONSTS
from zqh_core_common.zqh_core_common_misc import CFI_CONSTS
from zqh_core_common.zqh_core_common_misc import IMM_GEN
from zqh_core_common.zqh_core_common_inst_asm_buffer_main import zqh_core_common_inst_asm_buffer
from zqh_core_common.zqh_core_common_btb_bundles import zqh_core_common_bht_resp
from zqh_core_common.zqh_core_common_csr_main import zqh_core_common_csr_file
from zqh_core_common.zqh_core_common_breakpoint import zqh_core_common_break_point_unit
from zqh_core_common.zqh_core_common_alu_main import zqh_core_common_alu
from zqh_core_common.zqh_core_common_multiplier_main import zqh_core_common_multiplier
from zqh_core_common.zqh_core_common_multiplier_main import zqh_core_common_multiplier_stub
from .zqh_core_r1_core_parameters import zqh_core_r1_core_parameter
from zqh_rocc.zqh_rocc_bundles import zqh_rocc_instruction
from zqh_core_common.zqh_core_common_reg_file import zqh_core_common_reg_file
from zqh_core_common.zqh_core_common_inst_decode_main import *
from zqh_core_common.zqh_core_common_inst_decode_bundles import zqh_core_common_inst
from zqh_core_common.zqh_core_common_inst_decode_bundles import zqh_core_common_inst_decode_sigs

class zqh_core_r1_core(module):
    def set_par(self):
        super(zqh_core_r1_core, self).set_par()
        self.p = zqh_core_r1_core_parameter()

    def set_port(self):
        super(zqh_core_r1_core, self).set_port()
        self.io = zqh_core_r1_core_io('io')

    def main(self):
        super(zqh_core_r1_core, self).main()

        #performance counters
        def pipelineIDToWB(x):
            return reg_en(
                next = reg_en(
                    next = reg_en(
                        next = x,
                        en = ~id_kill),
                    en = ex_pc_valid),
                en = mem_pc_valid)

        perfEvents = zqh_core_r1_event_sets([
            zqh_core_r1_event_set(lambda mask,hits: mux(
                mask[0],
                wb_xcpt,
                wb_valid & pipelineIDToWB((mask & hits).r_or())), [
                ("exception", lambda : 0),
                ("load", lambda : id_inst_dec.mem & (id_inst_dec.mem_cmd == M_CONSTS.M_XRD()) & ~id_inst_dec.fp),
                ("store", lambda : id_inst_dec.mem & (id_inst_dec.mem_cmd == M_CONSTS.M_XWR()) & ~id_inst_dec.fp),
                ("amo", lambda : self.p.isa_a & id_inst_dec.mem & (M_CONSTS.is_amo(id_inst_dec.mem_cmd) | id_inst_dec.mem_cmd.match_any([M_CONSTS.M_XLR(), M_CONSTS.M_XSC()]))),
                ("system", lambda : id_inst_dec.csr_cmd != CSR_CONSTS.N()),
                ("arith", lambda : id_inst_dec.wxd & ~(id_inst_dec.jal | id_inst_dec.jalr | id_inst_dec.mem | id_inst_dec.fp | id_inst_dec.mul | id_inst_dec.div | (id_inst_dec.csr_cmd != CSR_CONSTS.N()))),
                ("branch", lambda : id_inst_dec.branch),
                ("jal", lambda : id_inst_dec.jal),
                ("jalr", lambda : id_inst_dec.jalr)]
                + ([] if (not self.p.isa_m) else [
                ("mul", lambda : id_inst_dec.mul),
                ("div", lambda : id_inst_dec.div)])
                + ([] if (not self.p.isa_f) else [
                ("fp load", lambda : id_inst_dec.fp & self.io.fpu.dec.ldst & self.io.fpu.dec.wen),
                ("fp store", lambda : id_inst_dec.fp & self.io.fpu.dec.ldst & ~self.io.fpu.dec.wen),
                ("fp add", lambda : id_inst_dec.fp & self.io.fpu.dec.fma & self.io.fpu.dec.swap23),
                ("fp mul", lambda : id_inst_dec.fp & self.io.fpu.dec.fma & ~self.io.fpu.dec.swap23 & ~self.io.fpu.dec.ren3),
                ("fp mul-add", lambda : id_inst_dec.fp & self.io.fpu.dec.fma & self.io.fpu.dec.ren3),
                ("fp div/sqrt", lambda : id_inst_dec.fp & (self.io.fpu.dec.div | self.io.fpu.dec.sqrt)),
                ("fp other", lambda : id_inst_dec.fp & ~(self.io.fpu.dec.ldst | self.io.fpu.dec.fma | self.io.fpu.dec.div | self.io.fpu.dec.sqrt))])),
            zqh_core_r1_event_set(lambda mask,hits : (mask & hits).r_or(), [
                ("load-use interlock", lambda : (id_ex_hazard & ex_inst_dec.mem) | (id_mem_hazard & mem_inst_dec.mem) | (id_wb_hazard & wb_inst_dec.mem)),
                ("long-latency interlock", lambda : id_sboard_hazard),
                ("csr interlock", lambda : (id_ex_hazard & (ex_inst_dec.csr_cmd != CSR_CONSTS.N())) | (id_mem_hazard & (mem_inst_dec.csr_cmd != CSR_CONSTS.N())) | (id_wb_hazard & (wb_inst_dec.csr_cmd != CSR_CONSTS.N()))),
                ("I$ blocked", lambda : icache_blocked),
                ("D$ blocked", lambda : id_inst_dec.mem & lsu_blocked),
                ("branch taken misprediction", lambda : mem_take_pc & mem_br_taken_misprediction),
                ("control-flow target misprediction", lambda : mem_take_pc & mem_cfi_misprediction & mem_cfi & ~mem_br_taken_misprediction & ~icache_blocked),
                ("flush", lambda : wb_reg_flush_pipe),
                ("replay", lambda : wb_replay)]
                + ([] if (not self.p.isa_m) else [
                ("mul/div interlock", lambda : (id_ex_hazard & (ex_inst_dec.mul | ex_inst_dec.div)) | (id_mem_hazard & (mem_inst_dec.mul | mem_inst_dec.div)) | (id_wb_hazard & (wb_inst_dec.mul | wb_inst_dec.div)))])
                + ([] if (not self.p.isa_f) else [
                ("fp interlock", lambda : (id_ex_hazard & ex_inst_dec.fp) | (id_mem_hazard & mem_inst_dec.fp) | (id_wb_hazard & wb_inst_dec.fp) | (id_inst_dec.fp & id_stall_fpu))])),
            zqh_core_r1_event_set(lambda mask,hits : (mask & hits).r_or(), [
                ("I$ miss", lambda : self.io.ifu.events.refill),
                ("D$ miss", lambda : self.io.lsu.events.refill),
                ("D$ write back", lambda : self.io.lsu.events.write_back)])
                ])


        decode_table = []
        if (self.p.isa_m):
            decode_table.extend(zqh_core_common_m_decode().table)
            if (self.p.xlen > 32):
                decode_table.extend(zqh_core_common_m64_decode().table)
        if (self.p.isa_a):
            decode_table.extend(zqh_core_common_a_decode().table)
            if (self.p.xlen > 32):
                decode_table.extend(zqh_core_common_a64_decode().table)
        if (self.p.flen >= 32):
            decode_table.extend(zqh_core_common_f_decode().table)
            if (self.p.xlen > 32):
                decode_table.extend(zqh_core_common_f64_decode().table)
        if (self.p.flen >= 64):
            decode_table.extend(zqh_core_common_d_decode().table)
            if (self.p.xlen > 32):
                decode_table.extend(zqh_core_common_d64_decode().table)
        if (self.p.isa_custom):
            decode_table.extend(zqh_core_common_rocc_decode().table)
        if (self.p.xlen > 32):
            decode_table.extend(zqh_core_common_i64_decode().table)
        else:
            decode_table.extend(zqh_core_common_i32_decode().table)
        if (self.p.use_vm):
            decode_table.extend(zqh_core_common_s_decode().table)
        if (self.p.use_debug):
            decode_table.extend(zqh_core_common_debug_decode().table)
        decode_table.extend(zqh_core_common_i_decode().table)


        ex_inst_dec = zqh_core_common_inst_decode_sigs('ex_inst_dec').as_reg()
        ex_reg_xcpt_interrupt  = reg('ex_reg_xcpt_interrupt')
        ex_reg_valid           = reg('ex_reg_valid')
        ex_reg_rvc             = reg('ex_reg_rvc')
        ex_reg_xcpt            = reg('ex_reg_xcpt')
        ex_reg_flush_pipe      = reg('ex_reg_flush_pipe')
        ex_reg_mem_lsu_hazard  = reg('ex_reg_mem_lsu_hazard')
        ex_reg_cause           = reg('ex_reg_cause', w = self.p.xlen)
        ex_reg_pc              = reg('ex_reg_pc', w = self.p.vaddr_bits)
        ex_reg_inst            = reg('ex_reg_inst', w = self.p.inst_bits)
        ex_reg_btb_hit         = reg('ex_reg_btb_hit')
        ex_reg_btb_taken       = reg('ex_reg_btb_taken')
        ex_reg_btb_bht_info    = zqh_core_common_bht_resp('ex_reg_btb_bht_info').as_reg()

        mem_inst_dec = zqh_core_common_inst_decode_sigs('mem_inst_dec').as_reg()
        mem_reg_xcpt_interrupt  = reg('mem_reg_xcpt_interrupt')
        mem_reg_valid           = reg('mem_reg_valid')
        mem_reg_rvc             = reg('mem_reg_rvc')
        mem_reg_xcpt            = reg('mem_reg_xcpt')
        mem_reg_replay          = reg('mem_reg_replay')
        mem_reg_flush_pipe      = reg('mem_reg_flush_pipe')
        mem_reg_cause           = reg('mem_reg_cause', w = self.p.xlen)
        mem_reg_load            = reg('mem_reg_load')
        mem_reg_store           = reg('mem_reg_store')
        mem_reg_pc              = reg('mem_reg_pc', w = self.p.vaddr_bits)
        mem_reg_inst            = reg('mem_reg_inst', w = self.p.inst_bits)
        mem_reg_wdata           = reg('mem_reg_wdata',w = self.p.xlen)
        mem_reg_rs2             = reg('mem_reg_rs2', w = self.p.xlen)
        mem_reg_br_taken        = reg('mem_reg_br_taken')
        mem_reg_btb_hit         = reg('mem_reg_btb_hit')
        mem_reg_btb_taken       = reg('mem_reg_btb_taken')
        mem_reg_btb_bht_info    = zqh_core_common_bht_resp('mem_reg_btb_bht_info').as_reg()
        mem_take_pc             = bits('mem_take_pc')

        wb_inst_dec = zqh_core_common_inst_decode_sigs('wb_inst_dec').as_reg()
        wb_reg_valid           = reg('wb_reg_valid')
        wb_reg_xcpt            = reg('wb_reg_xcpt')
        wb_reg_replay          = reg('wb_reg_replay')
        wb_reg_flush_pipe      = reg('wb_reg_flush_pipe')
        wb_reg_cause           = reg('wb_reg_cause', w = self.p.xlen)
        wb_reg_pc              = reg('wb_reg_pc', w = self.p.vaddr_bits)
        wb_reg_inst            = reg('wb_reg_inst', w = self.p.inst_bits)
        wb_reg_wdata           = reg('wb_reg_wdata', w = self.p.xlen )
        wb_reg_rs2             = reg('wb_reg_rs2', w = self.p.xlen )
        wb_take_pc             = bits('wb_take_pc')
        wb_lsu_miss            = bits('wb_lsu_miss')

        take_pc = wb_take_pc | mem_take_pc

        inst_asm_buffer = zqh_core_common_inst_asm_buffer('inst_asm_buffer')        

        rf = zqh_core_common_reg_file(
            'rf',
            n = self.p.num_gprs,
            w = self.p.xlen,
            bypass_en = 1)

        csr = zqh_core_common_csr_file('csr')

        #decode stage
        inst_asm_buffer.io.ifu_resp /= self.io.ifu.resp        
        inst_asm_buffer.io.flush /= self.io.ifu.req.valid
        inst_asm_buffer.io.rv64 /= csr.io.status.rv64

        id_inst = inst_asm_buffer.io.out.bits.inst
        id_inst_pre_dec = zqh_core_common_inst('inst_pre_dec')
        id_inst_pre_dec.split(id_inst)
        id_inst_dec = zqh_core_common_inst_decode_sigs('id_inst_dec')
        id_inst_dec.decode(id_inst, decode_table)
        with when(~csr.io.status.rv64):
            id_inst_dec.alu_dw /= 0

        id_raddr3 = id_inst_pre_dec.rs3
        id_raddr2 = id_inst_pre_dec.rs2
        id_raddr1 = id_inst_pre_dec.rs1
        id_waddr  = id_inst_pre_dec.rd
        id_amo_aq = id_inst_pre_dec.aq
        id_amo_rl = id_inst_pre_dec.rl
        id_mem_lsu_hazard = bits('id_mem_lsu_hazard')
        fence_flag = reg_r('fence_flag')
        id_ren = [id_inst_dec.rxs1, id_inst_dec.rxs2]
        id_raddr = [id_raddr1, id_raddr2]
        id_rs = list(map(lambda _: rf.read(_), id_raddr))
        id_kill = bits('id_kill')

        id_csr_en = id_inst_dec.csr_cmd.match_any([
            CSR_CONSTS.S(),
            CSR_CONSTS.C(),
            CSR_CONSTS.W()])
        id_csr_system = id_inst_dec.csr_cmd == CSR_CONSTS.I()
        id_csr_ro = id_inst_dec.csr_cmd.match_any([
            CSR_CONSTS.S(),
            CSR_CONSTS.C()]) & (id_raddr1 == value(0))
        id_csr_cmd = mux(id_csr_ro, CSR_CONSTS.R(), id_inst_dec.csr_cmd)
        id_sfence = id_inst_dec.mem & (id_inst_dec.mem_cmd == M_CONSTS.M_SFENCE())
        id_csr_flush = (
            id_sfence | 
            id_csr_system | 
            (id_csr_en & ~id_csr_ro & csr.io.decode[0].write_flush))

        id_illegal_inst = (
            ~id_inst_dec.legal | 
            ((id_inst_dec.mul | id_inst_dec.div) & ~csr.io.status.isa[ord('m')-ord('a')]) | 
            (id_inst_dec.amo & ~csr.io.status.isa[ord('a')-ord('a')]) | 
            (id_inst_dec.fp & (csr.io.decode[0].fp_illegal | self.io.fpu.illegal_rm)) | 
            (id_inst_dec.dp & ~csr.io.status.isa[ord('d')-ord('a')]) | 
            (inst_asm_buffer.io.out.bits.rvc & ~csr.io.status.isa[ord('c')-ord('a')]) | 
            (id_inst_dec.rocc & csr.io.decode[0].rocc_illegal) | 
            (id_csr_en & (
                csr.io.decode[0].read_illegal | 
                (~id_csr_ro & csr.io.decode[0].write_illegal))) | 
            (~inst_asm_buffer.io.out.bits.rvc & (
                (id_sfence | id_csr_system ) & 
                csr.io.decode[0].system_illegal)))
        id_fence_flag_next = id_inst_dec.fence | (id_inst_dec.amo & id_amo_aq)
        id_lsu_busy = self.io.lsu.busy | self.io.lsu.req.valid
        with when (~id_lsu_busy):
            fence_flag /= 0
        id_rocc_busy = self.p.isa_custom & (
            self.io.rocc.busy | 
            (ex_reg_valid & ex_inst_dec.rocc) | 
            (mem_reg_valid & mem_inst_dec.rocc) | (wb_reg_valid & wb_inst_dec.rocc))
        id_do_fence = (
            (id_rocc_busy & id_inst_dec.fence) | 
            (id_lsu_busy & (
                (id_inst_dec.amo & id_amo_rl) | 
                id_inst_dec.fence_i | 
                (fence_flag & (id_inst_dec.mem | id_inst_dec.rocc)))))

        bpu = zqh_core_common_break_point_unit('bpu')
        bpu.io.status /= csr.io.status
        bpu.io.bp /= csr.io.bp
        bpu.io.pc /= inst_asm_buffer.io.out.bits.pc
        bpu.io.ea /= mem_reg_wdata

        id_inst_xcpt = inst_asm_buffer.io.out.bits.xcpt.pack().r_or()
        (id_xcpt, id_cause) = self.checkExceptions([
            (csr.io.interrupt, csr.io.interrupt_cause),
            (bpu.io.debug_if,  CSR_CONSTS.debugTriggerCause()),
            (bpu.io.xcpt_if,   CS_CONSTS.breakpoint),
            (id_inst_xcpt,     CS_CONSTS.fetch_access),
            (id_illegal_inst,  CS_CONSTS.illegal_instruction)])


        #bypass
        ex_waddr = ex_reg_inst[11:7]
        mem_waddr = mem_reg_inst[11:7]
        wb_waddr = wb_reg_inst[11:7]
        bypass_sources = (
            (1, 0, 0),
            (
                ex_reg_valid & ex_inst_dec.wxd,
                ex_waddr,
                mem_reg_wdata),
            (
                mem_reg_valid & mem_inst_dec.wxd & ~mem_inst_dec.mem,
                mem_waddr,
                wb_reg_wdata),
            (
                mem_reg_valid & mem_inst_dec.wxd,
                mem_waddr,
                self.io.lsu.resp.bits.data[self.p.xlen-1: 0]))
        id_bypass_sources_valid = list(map(
            lambda raddr: list(map(lambda _: _[0] & (_[1] == raddr), bypass_sources)),
            id_raddr))
        bypass_data = list(map(lambda _: _[2], bypass_sources))

        #execute stage
        ex_reg_rs_bypass_valid = list(map(lambda _: reg(), range(len(id_raddr))))
        ex_reg_rs_bypass_idx = list(map(
            lambda _: reg(w = log2_ceil(len(bypass_sources))),
            range(len(id_raddr))))
        ex_reg_rs = list(map(lambda _: reg(w = self.p.xlen),range(len(id_raddr))))
        ex_rs = list(map(
            lambda _: mux(
                ex_reg_rs_bypass_valid[_], 
                sel(ex_reg_rs_bypass_idx[_], bypass_data),
                ex_reg_rs[_]),
            range(len(id_raddr))))
        ex_imm = IMM_GEN.imm_gen(ex_inst_dec.sel_imm, ex_reg_inst)
        ex_in1 = sel_map(ex_inst_dec.sel_alu1, [
            (D_CONSTS.A1_RS1(), ex_rs[0].as_sint()),
            (D_CONSTS.A1_PC(),ex_reg_pc.as_sint())], value(0, w = 2).as_sint())
        ex_in2 = sel_map(ex_inst_dec.sel_alu2, [
            (D_CONSTS.A2_RS2(), ex_rs[1].as_sint()),
            (D_CONSTS.A2_IMM(), ex_imm),
            (D_CONSTS.A2_SIZE(), mux(
                ex_reg_rvc,
                value(2, w = 3).as_sint(),
                value(4, 4).as_sint()))], value(0, w = 2).as_sint())

        alu = zqh_core_common_alu('alu')
        alu.io.dw /= ex_inst_dec.alu_dw
        alu.io.op /= ex_inst_dec.alu_fn
        alu.io.in2 /= ex_in2
        alu.io.in1 /= ex_in1

        #multiplier and divider
        if (self.p.isa_m):
            mulDiv = zqh_core_common_multiplier(
                'mulDiv',
                width = self.p.xlen,
                tag_bits = log2_up(self.p.num_gprs))
        else:
            mulDiv = zqh_core_common_multiplier_stub(
                'mulDiv',
                width = self.p.xlen,
                tag_bits = log2_up(self.p.num_gprs))
        mulDiv.io.req.valid /= ex_reg_valid & (ex_inst_dec.mul | ex_inst_dec.div)
        mulDiv.io.req.bits.dw /= ex_inst_dec.alu_dw
        mulDiv.io.req.bits.fn /= ex_inst_dec.alu_fn
        mulDiv.io.req.bits.in1 /= ex_rs[0]
        mulDiv.io.req.bits.in2 /= ex_rs[1]
        mulDiv.io.req.bits.tag /= ex_waddr

        ex_reg_valid /= ~id_kill
        ex_reg_xcpt /= ~id_kill & id_xcpt
        ex_reg_xcpt_interrupt /= ~take_pc & inst_asm_buffer.io.out.valid & csr.io.interrupt

        with when (~id_kill):
            ex_inst_dec /= id_inst_dec
            ex_reg_rvc /= inst_asm_buffer.io.out.bits.rvc
            ex_reg_btb_hit /= inst_asm_buffer.io.out.bits.btb_hit
            ex_reg_btb_taken /= inst_asm_buffer.io.out.bits.taken
            ex_reg_btb_bht_info /= inst_asm_buffer.io.out.bits.bht_info
            ex_inst_dec.csr_cmd /= id_csr_cmd
            with when (id_fence_flag_next):
                fence_flag /= 1
            with when (id_xcpt):
                ex_inst_dec.alu_fn /= A_CONSTS.FN_ADD()
                ex_inst_dec.alu_dw /= csr.io.status.rv64
                ex_inst_dec.sel_alu1 /= D_CONSTS.A1_RS1()
                ex_inst_dec.sel_alu2 /= D_CONSTS.A2_ZERO()
                with when (bpu.io.xcpt_if | id_inst_xcpt):
                    ex_inst_dec.sel_alu1 /= D_CONSTS.A1_PC()
                    ex_inst_dec.sel_alu2 /= D_CONSTS.A2_ZERO()
            ex_reg_flush_pipe /= id_inst_dec.fence_i | id_csr_flush
            ex_reg_mem_lsu_hazard /= id_mem_lsu_hazard
            with when (id_sfence):
                ex_inst_dec.mem_type /= cat([id_raddr2 != 0, id_raddr1 != 0])

            for i in range(len(id_raddr)):
                do_bypass = reduce(lambda x, y: x | y, id_bypass_sources_valid[i])
                bypass_src = pri_lsb_enc(id_bypass_sources_valid[i])
                ex_reg_rs_bypass_valid[i] /= do_bypass
                ex_reg_rs_bypass_idx[i] /= bypass_src
                with when (id_ren[i] & ~do_bypass):
                    ex_reg_rs[i] /= id_rs[i]
            with when (id_illegal_inst):
                ex_reg_rs_bypass_valid[0] /= 0
                ex_reg_rs[0] /= 0 #don't support store tval
        with when (~id_kill | csr.io.interrupt):
            ex_reg_cause /= id_cause
            ex_reg_inst /= id_inst
            ex_reg_pc /= inst_asm_buffer.io.out.bits.pc

        ex_pc_valid = ex_reg_valid | ex_reg_xcpt_interrupt
        ex_replay_no_ready = (
            (ex_inst_dec.mem & ~self.io.lsu.req.ready) | 
            ((ex_inst_dec.mul | ex_inst_dec.div) & ~mulDiv.io.req.ready))
        ex_replay_lsu_hazard = wb_lsu_miss & ex_reg_mem_lsu_hazard
        ex_replay = (ex_reg_valid & (ex_replay_no_ready | ex_replay_lsu_hazard))
        ex_kill = take_pc | ex_replay | ~ex_reg_valid

        (ex_xcpt, ex_cause) = self.checkExceptions([(
            ex_reg_xcpt_interrupt | ex_reg_xcpt,
            ex_reg_cause)])

        #memory stage
        mem_pc_valid = mem_reg_valid | mem_reg_replay | mem_reg_xcpt_interrupt
        mem_br_jal_target = (
            mem_reg_pc.as_sint() + 
            mux(
                mem_inst_dec.branch & mem_reg_br_taken,
                IMM_GEN.imm_gen(D_CONSTS.IMM_B(), mem_reg_inst),
                mux(
                    mem_inst_dec.jal, 
                    IMM_GEN.imm_gen(D_CONSTS.IMM_J(), mem_reg_inst),
                    mux(
                        mem_reg_rvc, 
                        value(2, w = 3).as_sint(), 
                        value(4, w = 4).as_sint()))))
        mem_npc = (
            mux(
                mem_inst_dec.jalr,
                mem_reg_wdata.as_sint(),
                mem_br_jal_target) & (-2)).as_uint()
        mem_wrong_npc = mux(
            ex_pc_valid,
            mem_npc != ex_reg_pc, 
            mux(
                inst_asm_buffer.io.out.valid | inst_asm_buffer.io.partial_valid,
                mem_npc != inst_asm_buffer.io.out.bits.pc,
                1))


        mem_npc_misaligned = ~csr.io.status.isa[ord('c')-ord('a')] & mem_npc[1]
        mem_wdata = mux(
            ~mem_reg_xcpt & (mem_inst_dec.jalr ^ mem_npc_misaligned),
            mem_br_jal_target,
            mem_reg_wdata.as_sint()).as_uint()
        mem_cfi = mem_inst_dec.branch | mem_inst_dec.jalr | mem_inst_dec.jal
        mem_cfi_taken = (
            (mem_inst_dec.branch & mem_reg_br_taken) | 
            mem_inst_dec.jalr | 
            mem_inst_dec.jal)
        mem_br_taken_misprediction = (
            mem_inst_dec.branch & 
            (mem_reg_br_taken != (mem_reg_btb_hit & mem_reg_btb_taken)))
        mem_br_misprediction = mem_inst_dec.branch & mem_wrong_npc
        mem_jal_misprediction = mem_inst_dec.jal & mem_wrong_npc
        mem_jalr_misprediction = mem_inst_dec.jalr & mem_wrong_npc
        mem_cfi_misprediction = (
            mem_br_misprediction | 
            mem_jal_misprediction | 
            mem_jalr_misprediction)
        mem_take_pc /= mem_reg_valid & mem_cfi_misprediction

        mem_reg_valid /= ~ex_kill
        mem_reg_replay /= ~take_pc & ex_replay
        mem_reg_xcpt /= ~ex_kill & ex_xcpt
        mem_reg_xcpt_interrupt /= ~take_pc & ex_reg_xcpt_interrupt

        with when (~(mem_reg_valid & mem_reg_flush_pipe) & ex_pc_valid):
            mem_inst_dec /= ex_inst_dec
            mem_reg_rvc /= ex_reg_rvc
            mem_reg_btb_hit /= ex_reg_btb_hit
            mem_reg_btb_taken /= ex_reg_btb_taken
            mem_reg_btb_bht_info /= ex_reg_btb_bht_info
            mem_reg_load /= ex_inst_dec.mem & M_CONSTS.is_read(ex_inst_dec.mem_cmd)
            mem_reg_store /= ex_inst_dec.mem & M_CONSTS.is_write(ex_inst_dec.mem_cmd)
            mem_reg_flush_pipe /= ex_reg_flush_pipe

            mem_reg_cause /= ex_cause
            mem_reg_inst /= ex_reg_inst
            mem_reg_pc /= ex_reg_pc

            mem_reg_wdata /= alu.io.out
            mem_reg_br_taken /= alu.io.cmp_out

            with when (ex_inst_dec.rxs2 & (ex_inst_dec.mem | ex_inst_dec.rocc)):
                typ = mux(ex_inst_dec.rocc, log2_ceil(self.p.xlen//8), ex_inst_dec.mem_type)
                mem_reg_rs2 /= M_CONSTS.store_data_gen(typ, ex_rs[1], self.p.xlen//8)
            with when (ex_inst_dec.jalr & csr.io.status.debug):
                mem_inst_dec.fence_i /= 1
                mem_reg_flush_pipe /= 1

        mem_breakpoint = (mem_reg_load & bpu.io.xcpt_ld) | (mem_reg_store & bpu.io.xcpt_st)
        mem_debug_breakpoint = (
            (mem_reg_load & bpu.io.debug_ld) | 
            (mem_reg_store & bpu.io.debug_st))
        (mem_ldst_xcpt, mem_ldst_cause) = self.checkExceptions([
            (mem_debug_breakpoint, CSR_CONSTS.debugTriggerCause()),
            (mem_breakpoint, CS_CONSTS.breakpoint)])

        (mem_xcpt, mem_cause) = self.checkExceptions([
            (mem_reg_xcpt_interrupt | mem_reg_xcpt, mem_reg_cause),
            (mem_reg_valid & mem_npc_misaligned, CS_CONSTS.misaligned_fetch),
            (mem_reg_valid & mem_ldst_xcpt, mem_ldst_cause)])

        mem_lsu_kill = mem_reg_valid & mem_inst_dec.wxd & self.io.lsu.slow_kill
        mem_fpu_kill = mem_reg_valid & mem_inst_dec.fp & self.io.fpu.nack_mem
        mem_replay  = mem_lsu_kill | mem_reg_replay | mem_fpu_kill
        mem_kill_pre = mem_lsu_kill | wb_take_pc | mem_reg_xcpt | ~mem_reg_valid
        mem_kill = mem_kill_pre | mem_xcpt | mem_fpu_kill
        mulDiv.io.kill /= mem_kill_pre & reg(next = mulDiv.io.req.fire())

        #writeback stage
        wb_reg_valid /= ~mem_kill
        wb_reg_replay /= mem_replay & ~wb_take_pc
        wb_reg_xcpt /= mem_xcpt & ~wb_take_pc
        wb_reg_flush_pipe /= ~mem_kill & mem_reg_flush_pipe
        with when (mem_pc_valid):
            wb_inst_dec /= mem_inst_dec
            wb_reg_wdata /= mux(
                ~mem_reg_xcpt & mem_inst_dec.fp & mem_inst_dec.wxd,
                self.io.fpu.toint_data.bits,
                mem_wdata)
            with when(mem_inst_dec.rocc):
                wb_reg_rs2 /= mem_reg_rs2
            wb_reg_cause /= mem_cause
            wb_reg_inst /= mem_reg_inst
            wb_reg_pc /= mem_reg_pc


        lsu_resp_fire = self.io.lsu.resp.fire()
        lsu_resp_fire_accept = lsu_resp_fire & ~self.io.lsu.resp.bits.replay
        lsu_resp_fire_replay = lsu_resp_fire & self.io.lsu.resp.bits.replay

        (wb_xcpt, wb_cause) = self.checkExceptions([
            (wb_reg_xcpt,  wb_reg_cause),
            (wb_reg_valid & wb_inst_dec.mem & lsu_resp_fire & self.io.lsu.resp.bits.xcpt.ma.st, CS_CONSTS.misaligned_store),
            (wb_reg_valid & wb_inst_dec.mem & lsu_resp_fire & self.io.lsu.resp.bits.xcpt.ma.ld, CS_CONSTS.misaligned_load),
            (wb_reg_valid & wb_inst_dec.mem & lsu_resp_fire & self.io.lsu.resp.bits.xcpt.pf.st, CS_CONSTS.store_page_fault),
            (wb_reg_valid & wb_inst_dec.mem & lsu_resp_fire & self.io.lsu.resp.bits.xcpt.pf.ld, CS_CONSTS.load_page_fault),
            (wb_reg_valid & wb_inst_dec.mem & lsu_resp_fire & self.io.lsu.resp.bits.xcpt.ae.st, CS_CONSTS.store_access),
            (wb_reg_valid & wb_inst_dec.mem & lsu_resp_fire & self.io.lsu.resp.bits.xcpt.ae.ld, CS_CONSTS.load_access)
        ])


        wb_wxd = wb_reg_valid & wb_inst_dec.wxd
        wb_set_sboard = wb_inst_dec.mul | wb_inst_dec.div | wb_lsu_miss | wb_inst_dec.rocc
        wb_replay_pre = lsu_resp_fire_replay | wb_reg_replay
        wb_replay_rocc = wb_reg_valid & wb_inst_dec.rocc & ~self.io.rocc.cmd.ready
        wb_replay = wb_replay_pre | wb_replay_rocc
        wb_take_pc /= wb_replay | wb_xcpt | csr.io.eret | wb_reg_flush_pipe

        #writeback arbitration
        lsu_resp_xpu = ~self.io.lsu.resp.bits.tag[0]
        lsu_resp_fpu =  self.io.lsu.resp.bits.tag[0]
        lsu_resp_waddr = self.io.lsu.resp.bits.tag[5: 1]
        lsu_resp_valid_has_data = lsu_resp_fire_accept & self.io.lsu.resp.bits.has_data
        lsu_resp_slow_has_data = lsu_resp_valid_has_data & self.io.lsu.resp.bits.slow

        ll_wdata = bits(
            'll_wdata',
            init = mulDiv.io.resp.bits.data,
            w = mulDiv.io.resp.bits.data.get_w())
        ll_waddr = bits(
            'll_waddr',
            init = mulDiv.io.resp.bits.tag,
            w = mulDiv.io.resp.bits.tag.get_w())
        ll_wen = bits('ll_wen', init = mulDiv.io.resp.fire())
        mulDiv.io.resp.ready /= ~wb_wxd
        self.io.rocc.resp.ready /= ~wb_wxd
        with when (self.io.rocc.resp.fire()):
            mulDiv.io.resp.ready /= 0
            ll_wdata /= self.io.rocc.resp.bits.data
            ll_waddr /= self.io.rocc.resp.bits.rd
            ll_wen /= 1
        with when (lsu_resp_slow_has_data & lsu_resp_xpu):
            mulDiv.io.resp.ready /= 0
            self.io.rocc.resp.ready /= 0
            ll_waddr /= lsu_resp_waddr
            ll_wen /= 1

        wb_lsu_miss /= wb_inst_dec.mem & ~lsu_resp_fire_accept
        wb_valid = wb_reg_valid & ~wb_replay & ~wb_xcpt
        wb_wen = wb_valid & wb_inst_dec.wxd
        rf_wen = wb_wen | ll_wen
        rf_waddr = mux(ll_wen, ll_waddr, wb_waddr)
        rf_wdata = mux(
            lsu_resp_valid_has_data & lsu_resp_xpu,
            self.io.lsu.resp.bits.data[self.p.xlen-1: 0],
            mux(
                ll_wen,
                ll_wdata,
                mux(
                    wb_inst_dec.csr_cmd != CSR_CONSTS.N(),
                    csr.io.rw.rdata,
                    wb_reg_wdata)))
        rf.write(rf_wen, rf_waddr, rf_wdata)

        csr.io.decode[0].csr /= id_inst[31:20]
        csr.io.exception /= wb_xcpt
        csr.io.cause /= wb_cause
        csr.io.retire /= wb_valid
        csr.io.inst[0] /= wb_reg_inst
        csr.io.interrupts /= self.io.interrupts
        csr.io.hartid /= self.io.hartid
        self.io.fpu.fcsr_rm /= csr.io.fcsr_rm
        csr.io.fcsr_flags /= self.io.fpu.fcsr_flags
        csr.io.rocc_interrupt /= self.io.rocc.interrupt
        csr.io.pc /= wb_reg_pc
        tval_valid = wb_xcpt & wb_cause.match_any([
            CS_CONSTS.illegal_instruction,
            CS_CONSTS.breakpoint,
            CS_CONSTS.misaligned_load,
            CS_CONSTS.misaligned_store,
            CS_CONSTS.load_access,
            CS_CONSTS.store_access,
            CS_CONSTS.fetch_access,
            CS_CONSTS.load_page_fault,
            CS_CONSTS.store_page_fault,
            CS_CONSTS.fetch_page_fault])
        csr.io.tval /= mux(tval_valid, wb_reg_wdata, 0)
        csr.io.rw.addr /= wb_reg_inst[31:20]
        csr.io.rw.cmd /= mux(wb_reg_valid, wb_inst_dec.csr_cmd, CSR_CONSTS.N())
        csr.io.rw.wdata /= wb_reg_wdata
        self.io.csr_trace /= csr.io.trace

        hazard_targets = [
            (id_inst_dec.rxs1 & (id_raddr1 != 0), id_raddr1),
            (id_inst_dec.rxs2 & (id_raddr2 != 0), id_raddr2),
            (id_inst_dec.wxd  & (id_waddr  != 0), id_waddr)]
        fp_hazard_targets = [
            (self.io.fpu.dec.ren1, id_raddr1),
            (self.io.fpu.dec.ren2, id_raddr2),
            (self.io.fpu.dec.ren3, id_raddr3),
            (self.io.fpu.dec.wen, id_waddr)]

        sboard = zqh_core_r1_scoreboard(n = self.p.num_gprs, zero = 1)
        sboard.clear(ll_wen, ll_waddr)
        id_sboard_hazard = self.checkHazards(
            hazard_targets,
            lambda rd: sboard.read(rd) & ~(ll_wen & (ll_waddr == rd)))
        sboard.set(wb_set_sboard & wb_wen, wb_waddr)

        ex_cannot_bypass = (
            (ex_inst_dec.csr_cmd != CSR_CONSTS.N()) | 
            ex_inst_dec.jalr | 
            ex_inst_dec.mem | 
            ex_inst_dec.mul | 
            ex_inst_dec.div | 
            ex_inst_dec.fp | 
            ex_inst_dec.rocc)
        data_hazard_ex = ex_inst_dec.wxd & self.checkHazards(
            hazard_targets,
            lambda _: _ == ex_waddr)
        fp_data_hazard_ex = (
            ex_inst_dec.wfd & 
            self.checkHazards(
                fp_hazard_targets,
                lambda _: _ == ex_waddr)) if (self.p.isa_f) else 0
        id_ex_hazard = (
            ex_reg_valid & ((data_hazard_ex & ex_cannot_bypass) | fp_data_hazard_ex))

        mem_cannot_bypass = (
            (mem_inst_dec.csr_cmd != CSR_CONSTS.N()) | 
            mem_inst_dec.mul | 
            mem_inst_dec.div | 
            mem_inst_dec.fp | 
            mem_inst_dec.rocc)
        data_hazard_mem = mem_inst_dec.wxd & self.checkHazards(
            hazard_targets,
            lambda _: _ == mem_waddr)
        fp_data_hazard_mem = (mem_inst_dec.wfd & self.checkHazards(
            fp_hazard_targets,
            lambda _: _ == mem_waddr)) if (self.p.isa_f) else 0
        id_mem_hazard = mem_reg_valid & (
            (data_hazard_mem & mem_cannot_bypass) | 
            fp_data_hazard_mem)
        id_mem_lsu_hazard /= mem_reg_valid & data_hazard_mem & mem_inst_dec.mem

        data_hazard_wb = wb_inst_dec.wxd & self.checkHazards(
            hazard_targets,
            lambda _: _ == wb_waddr)
        fp_data_hazard_wb = (wb_inst_dec.wfd & self.checkHazards(
            fp_hazard_targets,
            lambda _: _ == wb_waddr)) if (self.p.isa_f) else 0
        id_wb_hazard = wb_reg_valid & ((data_hazard_wb & wb_set_sboard) | fp_data_hazard_wb)

        if (self.p.isa_f):
            fp_sboard = zqh_core_r1_scoreboard(n = self.p.num_gprs)
            fp_sboard.set(
                ((wb_lsu_miss & wb_inst_dec.wfd) | self.io.fpu.sboard_set) & wb_valid,
                wb_waddr)
            fp_sboard.clear(lsu_resp_slow_has_data & lsu_resp_fpu, lsu_resp_waddr)
            fp_sboard.clear(self.io.fpu.sboard_clr, self.io.fpu.sboard_clra)

            id_stall_fpu = self.checkHazards(fp_hazard_targets, lambda _: fp_sboard.read(_))
        else:
            id_stall_fpu = 0

        lsu_blocked = reg('lsu_blocked')
        lsu_blocked /= ~self.io.lsu.req.ready & (self.io.lsu.req.valid | lsu_blocked)
        rocc_blocked = reg('rocc_blocked')
        rocc_blocked /= (
            ~wb_xcpt & 
            ~self.io.rocc.cmd.ready & 
            (self.io.rocc.cmd.valid | rocc_blocked))

        id_stall = (
            id_ex_hazard | id_mem_hazard | id_wb_hazard | id_sboard_hazard | 
            (csr.io.singleStep & (ex_reg_valid | mem_reg_valid | wb_reg_valid)) | 
            (id_csr_en & csr.io.decode[0].fp_csr & ~self.io.fpu.fcsr_rdy) | 
            (id_inst_dec.fp & id_stall_fpu) | 
            (id_inst_dec.mem & lsu_blocked) | 
            (id_inst_dec.rocc & rocc_blocked) | 
            (
                (id_inst_dec.mul | id_inst_dec.div) & 
                (
                    ~(mulDiv.io.req.ready | (mulDiv.io.resp.valid & ~wb_wxd)) | 
                    mulDiv.io.req.valid)) | 
            id_do_fence | 
            csr.io.csr_stall)
        id_kill /= ~inst_asm_buffer.io.out.valid | take_pc | id_stall | csr.io.interrupt

        ifu_flush = wb_reg_valid & wb_inst_dec.fence_i & ~lsu_resp_fire_replay
        self.io.ifu.req.valid /= take_pc | ifu_flush
        ifu_req_vaddr = mux(
            wb_xcpt | csr.io.eret,
            csr.io.evec,
            mux(wb_replay, wb_reg_pc, mem_npc))
        self.io.ifu.req.bits.vaddr /= ifu_req_vaddr
        self.io.ifu.req.bits.cmd /= mux(ifu_flush, IFU_CONSTS.FLUSH(), IFU_CONSTS.FETCH())
        self.io.ifu.req.bits.error /= (
            ifu_req_vaddr[self.p.xlen - 1 : self.p.vaddr_bits] != 
            ifu_req_vaddr[self.p.vaddr_bits - 1].rep(self.p.xlen - self.p.vaddr_bits)
            if (self.p.vaddr_bits < self.p.xlen) else 0)

        self.io.ifu.rv64 /= csr.io.status.rv64

        inst_asm_buffer.io.out.ready /= ~id_stall

        self.io.fpu.inst.valid /= ~id_kill & id_inst_dec.fp
        self.io.fpu.killx /= ex_kill
        self.io.fpu.killm /= mem_kill_pre
        self.io.fpu.inst.bits /= id_inst
        self.io.fpu.fromint_data /= ex_rs[0]
        self.io.fpu.lsu_resp.valid /= lsu_resp_valid_has_data & lsu_resp_fpu
        self.io.fpu.lsu_resp.bits.data /= self.io.lsu.resp.bits.data_word_bypass
        self.io.fpu.lsu_resp.bits.type /= self.io.lsu.resp.bits.type
        self.io.fpu.lsu_resp.bits.tag /= lsu_resp_waddr

        self.io.lsu.req.valid     /= ex_reg_valid & ex_inst_dec.mem
        self.io.lsu.req.bits.tag  /= cat([ex_waddr, ex_inst_dec.fp])
        self.io.lsu.req.bits.cmd  /= ex_inst_dec.mem_cmd
        self.io.lsu.req.bits.type /= ex_inst_dec.mem_type
        self.io.lsu.req.bits.addr /= alu.io.add_out
        self.io.lsu.req.bits.error /= (
            alu.io.add_out[self.p.xlen - 1 : self.p.vaddr_bits] != 
            alu.io.add_out[self.p.vaddr_bits - 1].rep(self.p.xlen - self.p.vaddr_bits)
            if (self.p.vaddr_bits < self.p.xlen) else 0)
        self.io.lsu.s1_data.data /= mux(
            mem_inst_dec.fp,
            self.io.fpu.store_data.bits.rep((max(self.p.xlen, self.p.flen) // self.p.flen)),
            mem_reg_rs2.rep(max(self.p.xlen, self.p.flen)//self.p.xlen))
        self.io.lsu.s1_kill /= mem_kill_pre | mem_ldst_xcpt

        self.io.rocc.cmd.valid /= wb_reg_valid & wb_inst_dec.rocc & ~wb_replay_pre
        self.io.rocc.exception /= wb_xcpt & csr.io.status.xs.r_or()
        self.io.rocc.cmd.bits.status /= csr.io.status
        self.io.rocc.cmd.bits.inst /= zqh_rocc_instruction(init = wb_reg_inst)
        self.io.rocc.cmd.bits.rs1 /= wb_reg_wdata
        self.io.rocc.cmd.bits.rs2 /= wb_reg_rs2

        #btb update
        if (self.p.use_btb):
            mem_pc_for_btb = self.pc_for_btb(mem_reg_pc, mem_reg_rvc)
            self.io.ifu.btb_update.valid /= mem_reg_valid & ~wb_take_pc & mem_cfi & mem_wrong_npc
            self.io.ifu.btb_update.bits.cfi_type /= mux(
                (mem_inst_dec.jal | mem_inst_dec.jalr) & mem_waddr.match_any([1, 5]),
                CFI_CONSTS.call(),
                mux(
                    mem_inst_dec.jalr & mem_reg_inst[19:15].match_any([1, 5]),
                    CFI_CONSTS.ret(),
                    mux(
                        mem_inst_dec.jal | mem_inst_dec.jalr, CFI_CONSTS.jump(),
                        CFI_CONSTS.branch())))
            self.io.ifu.btb_update.bits.taken /= mem_cfi_taken
            self.io.ifu.btb_update.bits.tgt /= mem_npc
            self.io.ifu.btb_update.bits.pc /= mem_pc_for_btb
            self.io.ifu.btb_update.bits.rvc /= mem_reg_rvc
            self.io.ifu.btb_update.bits.rvi_half /= mem_reg_pc[1] & ~mem_reg_rvc

            #bht update
            if (self.p.use_bht):
                self.io.ifu.bht_update.valid /= mem_reg_valid & ~wb_take_pc
                self.io.ifu.bht_update.bits.pc /= mem_pc_for_btb
                self.io.ifu.bht_update.bits.taken /= mem_reg_br_taken
                self.io.ifu.bht_update.bits.mispredict /= mem_cfi_misprediction
                self.io.ifu.bht_update.bits.branch /= mem_inst_dec.branch
                self.io.ifu.bht_update.bits.bht_info /= mem_reg_btb_bht_info


        #performance counters
        icache_blocked = ~(self.io.ifu.resp.valid | reg(next = self.io.ifu.resp.valid))
        for c in csr.io.counters:
            c.inc /= reg(next = perfEvents.evaluate(c.event_sel))

        #tmp vprintln("C%0d: %d [%d] pc=[%x] W[r%0d=%x][%d] R[r%0d=%x] R[r%0d=%x] inst=[%x] DASM(%x)", (
        #tmp      self.io.hartid, csr.io.time[31:0], csr.io.trace[0].valid & ~csr.io.trace[0].exception,
        #tmp      csr.io.trace[0].iaddr[self.p.vaddr_bits-1: 0],
        #tmp      mux(rf_wen & ~(wb_set_sboard & wb_wen), rf_waddr, 0), rf_wdata, rf_wen,
        #tmp      wb_reg_inst[19:15], reg(next=reg(next=ex_rs[0], w = ex_rs[0].get_w()), w = ex_rs[0].get_w()),
        #tmp      wb_reg_inst[24:20], reg(next=reg(next=ex_rs[1], w = ex_rs[1].get_w()), w = ex_rs[1].get_w()),
        #tmp      csr.io.trace[0].insn, csr.io.trace[0].insn))

    def checkExceptions(self, x):
        return (
            reduce(
                lambda b,c: b|c,
                list(map(lambda a:a[0], x))),
            sel_p_lsb(list(map(lambda a: a[0], x)), list(map(lambda a: a[1], x))))

    def checkHazards(self, targets, cond):
        return reduce(lambda x, y: x | y, list(map(lambda h: h[0] & cond(h[1]), targets)))
    
    def pc_for_btb(self, pc, rvc):
        return mux(pc[1] & ~rvc, pc + 2, pc)[pc.get_w() - 1 : 0] if (self.p.isa_c) else pc
