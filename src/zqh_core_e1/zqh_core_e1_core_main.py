import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_misc import *
from .zqh_core_e1_core_parameters import zqh_core_e1_core_parameter
from .zqh_core_e1_core_bundles import zqh_core_e1_core_io
from zqh_core_common.zqh_core_common_inst_asm_buffer_main import zqh_core_common_inst_asm_buffer
from zqh_core_common.zqh_core_common_alu_main import zqh_core_common_alu
from zqh_core_common.zqh_core_common_csr_main import zqh_core_common_csr_file
from zqh_core_common.zqh_core_common_breakpoint import zqh_core_common_break_point_unit
from zqh_core_common.zqh_core_common_multiplier_main import zqh_core_common_multiplier
from zqh_core_common.zqh_core_common_reg_file import zqh_core_common_reg_file
from zqh_core_common.zqh_core_common_inst_decode_main import *
from zqh_core_common.zqh_core_common_inst_decode_bundles import zqh_core_common_inst
from zqh_core_common.zqh_core_common_inst_decode_bundles import zqh_core_common_inst_decode_sigs
from zqh_core_common.zqh_core_common_lsu_bundles import zqh_core_common_lsu_exceptions

class zqh_core_e1_core(module):
    def set_par(self):
        super(zqh_core_e1_core, self).set_par()
        self.p = zqh_core_e1_core_parameter()
    
    def set_port(self):
        super(zqh_core_e1_core, self).set_port()
        self.io = zqh_core_e1_core_io('io')

    def main(self):
        super(zqh_core_e1_core, self).main()
        reseting = reg_s('reseting', next = 0)

        csr = zqh_core_common_csr_file('csr')

        lsu_req_stall = bits('lsu_req_stall', init = 0)
        lsu_resp_stall = bits('lsu_resp_stall', init = 0)
        muldiv_resp_stall = bits('muldiv_resp_stall', init = 0)
        gpr_hazard_wait = bits('gpr_hazard_wait', init = 0)
        fp_gpr_hazard_wait = bits('fp_gpr_hazard_wait', init = 0)
        muldiv_req_stall = bits('muldiv_req_stall', init = 0)
        fpu_req_stall = bits('fpu_req_stall', init = 0)
        csr_stall = bits('csr_stall', init = 0)
        fcsr_stall = bits('fcsr_stall', init = 0)
        fence_flag = reg_r('fence_flag')
        fence_stall = bits('fence_stall', init = 0)
        stall = bits('stall', init = 0)
        hazard_wait = bits('hazard_wait', init = 0)
        retire_en = bits('retire_en', init = 1)

        lsu_stall = lsu_req_stall | lsu_resp_stall
        muldiv_stall = muldiv_req_stall | muldiv_resp_stall
        stall_exclude_lsu_req = (
            lsu_resp_stall | 
            muldiv_stall | 
            fpu_req_stall | 
            csr_stall | 
            fcsr_stall | 
            fence_stall)
        stall /= (
            lsu_stall | 
            muldiv_stall | 
            fpu_req_stall | 
            csr_stall | 
            fcsr_stall | 
            fence_stall)
        hazard_wait /= gpr_hazard_wait | fp_gpr_hazard_wait
        retire_en /= ~(stall | hazard_wait)
        retire_en_exclude_lsu_req = ~(stall_exclude_lsu_req | hazard_wait)

        take_exception = bits('take_exception', init = 0)
        exception_cause  = bits('exception_cause', w = self.p.xlen)
        exception_tval = bits('exception_tval', w = self.p.xlen)
        take_eret = bits('take_eret', init = 0)
        take_flush = bits('take_flush', init = 0)


        ####
        #fetch
        inst_asm_buffer = zqh_core_common_inst_asm_buffer('inst_asm_buffer')
        inst_asm_buffer.io.ifu_resp /= self.io.ifu.resp
        inst_asm_buffer.io.out.ready /= retire_en | take_exception
        inst_asm_buffer.io.flush /= self.io.ifu.req.valid
        inst_asm_buffer.io.rv64 /= csr.io.status.rv64

        ####
        #decode
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

        pc = inst_asm_buffer.io.out.bits.pc
        inst_valid = inst_asm_buffer.io.out.valid
        inst = inst_asm_buffer.io.out.bits.inst
        inst_rvc = inst_asm_buffer.io.out.bits.rvc
        inst_pre_dec = zqh_core_common_inst('inst_pre_dec')
        inst_pre_dec.split(inst)
        inst_dec = zqh_core_common_inst_decode_sigs('inst_dec')
        inst_dec.decode(inst, decode_table)
        with when(~csr.io.status.rv64):
            inst_dec.alu_dw /= 0

        inst_csr_en = inst_dec.csr_cmd.match_any([
            CSR_CONSTS.S(),
            CSR_CONSTS.C(), 
            CSR_CONSTS.W()])
        inst_csr_ren = inst_dec.csr_cmd.match_any([
            CSR_CONSTS.S(),
            CSR_CONSTS.C()]) & (inst_pre_dec.rs1 == 0)
        inst_system = inst_dec.csr_cmd == CSR_CONSTS.I()
        inst_none_lsu_muldiv =  ~inst_dec.mem & ~inst_dec.mul & ~inst_dec.div
        inst_arith = (
            inst_dec.wxd & ~(
                inst_dec.jal | 
                inst_dec.jalr | 
                inst_dec.mem | 
                inst_dec.fp | 
                inst_dec.mul | 
                inst_dec.div | 
                (inst_dec.csr_cmd != CSR_CONSTS.N())))

        #register file
        rf = zqh_core_common_reg_file('rf', n = self.p.num_gprs, w = self.p.xlen)


        ####
        #alu operand
        op1_data_rf = rf.read(inst_pre_dec.rs1)
        op1_data_pc = pc.s_ext(self.p.xlen)
        op1_data = bits('op1_data', w = self.p.xlen, init = 0)
        with when(inst_dec.sel_alu1 == D_CONSTS.A1_RS1()):
            op1_data /= op1_data_rf
        with elsewhen(inst_dec.sel_alu1 == D_CONSTS.A1_PC()):
            op1_data /= op1_data_pc

        op2_data_rf = rf.read(inst_pre_dec.rs2)
        op2_data_size = mux(inst_rvc, 2, 4)
        op2_data_imm = self.imm_gen(inst_dec.sel_imm, inst).s_ext(self.p.xlen)
        op2_data = bits('op2_data', w = self.p.xlen, init = 0)
        with when(inst_dec.sel_alu2 == D_CONSTS.A2_RS2()):
            op2_data /= op2_data_rf
        with elsewhen(inst_dec.sel_alu2 == D_CONSTS.A2_SIZE()):
            op2_data /= op2_data_size
        with elsewhen(inst_dec.sel_alu2 == D_CONSTS.A2_IMM()):
            op2_data /= op2_data_imm

        alu = zqh_core_common_alu('alu')
        alu.io.dw /= inst_dec.alu_dw
        alu.io.op /= inst_dec.alu_fn
        alu.io.in1 /= op1_data
        alu.io.in2 /= op2_data

        #multiplier and divider
        if (self.p.isa_m):
            muldiv = zqh_core_common_multiplier(
                'muldiv',
                width = self.p.xlen,
                tag_bits = log2_up(self.p.num_gprs))
            muldiv.io.req.valid /= (
                inst_valid & 
                retire_en & 
                ~take_exception & 
                (inst_dec.mul | inst_dec.div))
            muldiv.io.req.bits.dw /= inst_dec.alu_dw
            muldiv.io.req.bits.fn /= inst_dec.alu_fn
            muldiv.io.req.bits.in1 /= op1_data_rf
            muldiv.io.req.bits.in2 /= op2_data_rf
            muldiv.io.req.bits.tag /= inst_pre_dec.rd
            muldiv.io.kill /= 0
            muldiv.io.resp.ready /= ~(
                self.io.lsu.resp.fire() &
                ~self.io.lsu.resp.bits.tag[0] &
                self.io.lsu.resp.bits.has_data)
            muldiv_req_stall /= (inst_dec.mul | inst_dec.div) & ~muldiv.io.req.ready
            muldiv_resp_stall /= (
                muldiv.io.resp.fire() & 
                (~take_exception & inst_dec.wxd & (inst_pre_dec.rd != 0)))


        #fpu interface
        if (self.p.isa_f):
            self.io.fpu.inst.valid /= inst_valid & retire_en & ~take_exception & inst_dec.fp
            self.io.fpu.killx /= 0
            self.io.fpu.killm /= 0
            self.io.fpu.inst.bits /= inst
            self.io.fpu.fromint_data /= op1_data_rf
            self.io.fpu.lsu_resp.valid /= (
                self.io.lsu.resp.fire() &
                self.io.lsu.resp.bits.has_data &
                self.io.lsu.resp.bits.tag[0])
            self.io.fpu.lsu_resp.bits.data /= self.io.lsu.resp.bits.data
            self.io.fpu.lsu_resp.bits.type /= self.io.lsu.resp.bits.type
            self.io.fpu.lsu_resp.bits.tag /= self.io.lsu.resp.bits.tag[5:1]

            fpu_req_stall /= inst_dec.fp & ~self.io.fpu.inst.ready


            ####
            #fp_gpr_sb set and clear
            fp_gpr_sb = vec('fp_gpr_sb', gen = reg_r, n = 32)
            with when(self.io.fpu.sboard_clr):
                fp_gpr_sb(self.io.fpu.sboard_clra, 0)
            with when(
                self.io.lsu.resp.fire() & 
                self.io.lsu.resp.bits.tag[0] & 
                self.io.lsu.resp.bits.has_data):
                fp_gpr_sb(self.io.lsu.resp.bits.tag[5:1], 0)
            with when(
                (self.io.lsu.req.fire() & inst_dec.fp & inst_dec.wfd) | 
                self.io.fpu.sboard_set):
                fp_gpr_sb(inst_pre_dec.rd, 1)

            #fp gpr hazard detect
            fp_gpr_hazard_wait /= (inst_dec.fp & (
                (self.io.fpu.dec.ren1 & fp_gpr_sb[inst_pre_dec.rs1]) | 
                (self.io.fpu.dec.ren2 & fp_gpr_sb[inst_pre_dec.rs2]) | 
                (self.io.fpu.dec.ren3 & fp_gpr_sb[inst_pre_dec.rs3]) |
                (self.io.fpu.dec.wen & fp_gpr_sb[inst_pre_dec.rd])))



        ####
        #lsu access contro
        #tmp self.io.lsu.req.valid /= inst_valid & retire_en & ~take_exception & inst_dec.mem
        self.io.lsu.req.valid /= inst_valid & retire_en_exclude_lsu_req & ~take_exception & inst_dec.mem
        self.io.lsu.req.bits.cmd /= inst_dec.mem_cmd
        self.io.lsu.req.bits.type /= inst_dec.mem_type
        self.io.lsu.req.bits.tag /= cat([inst_pre_dec.rd, inst_dec.fp])
        self.io.lsu.req.bits.addr /= alu.io.add_out
        self.io.lsu.req.bits.error /= (
            alu.io.add_out[
                self.p.xlen - 1 : self.p.vaddr_bits] != alu.io.add_out[
                    self.p.vaddr_bits - 1].rep(self.p.xlen - self.p.vaddr_bits)
                        if (self.p.vaddr_bits < self.p.xlen) else 0)
        self.io.lsu.req.bits.data /= mux(
            inst_dec.fp,
            self.io.fpu.store_data.bits.rep(
                (max(self.p.xlen, self.p.flen) // self.p.flen)),
            M_CONSTS.store_data_gen(
                inst_dec.mem_type,
                op2_data_rf,
                self.p.xlen//8).rep(max(self.p.xlen, self.p.flen)//self.p.xlen))

        mem_is_read = M_CONSTS.is_read(inst_dec.mem_cmd)
        mem_is_write = M_CONSTS.is_write(inst_dec.mem_cmd)

        lsu_req_stall /= inst_dec.mem & ~self.io.lsu.req.ready
        lsu_resp_stall /= (
            self.io.lsu.resp.fire() &
            ~self.io.lsu.resp.bits.tag[0] &
            self.io.lsu.resp.bits.has_data &
            (~take_exception & inst_dec.wxd & (inst_pre_dec.rd != 0)))


        ####
        #gpr hazard detect
        #used to record gpr's write pending state
        gpr_sb = vec('gpr_sb', gen = reg_r, n = self.p.num_gprs)
        gpr_hazard_wait /= (
            (inst_dec.rxs1 & gpr_sb[inst_pre_dec.rs1]) | 
            (inst_dec.rxs2 & gpr_sb[inst_pre_dec.rs2]) | 
            (inst_dec.wxd & gpr_sb[inst_pre_dec.rd]))


        ####
        #fence process
        lsu_busy = self.io.lsu.busy
        rocc_busy = self.io.rocc.busy
        with when(
            inst_valid & 
            retire_en & 
            ~take_exception & 
            (inst_dec.fence | (inst_dec.amo & inst_pre_dec.aq))):
            fence_flag /= 1
        with elsewhen(~lsu_busy):
            fence_flag /= 0
        with when(
            (rocc_busy & inst_dec.fence) |
            (
                lsu_busy & 
                (
                    (inst_dec.amo & inst_pre_dec.rl) |
                    inst_dec.fence_i |
                    (fence_flag & (inst_dec.mem | inst_dec.rocc))))):
            fence_stall /= 1


        ####
        #gpr_sb set and clear
        with when(
            (self.io.lsu.resp.fire() & 
                ~self.io.lsu.resp.bits.tag[0] & 
                self.io.lsu.resp.bits.has_data) |
            muldiv.io.resp.fire()):
            rd = mux(
                muldiv.io.resp.fire(),
                muldiv.io.resp.bits.tag[4:0],
                self.io.lsu.resp.bits.tag[5:1])
            gpr_sb(rd, 0)
        with elsewhen(self.io.lsu.req.fire() | muldiv.io.req.fire()):
            with when(inst_dec.wxd):
                gpr_sb(inst_pre_dec.rd, 1)
        gpr_sb[0] /= 0 #gpr0 force to 0


        ####
        #csr
        csr_flush = (
            (inst_dec.mem & (inst_dec.mem_cmd == M_CONSTS.M_SFENCE())) |
            inst_system |
            (inst_csr_en & ~inst_csr_ren & csr.io.decode[0].write_flush))
        take_flush /= csr_flush | inst_dec.fence_i


        ####
        #rf write back
        take_branch = inst_dec.branch & alu.io.cmp_out
        take_cfi = take_branch | inst_dec.jal | inst_dec.jalr
        pc_add_offset = pc + mux(
            inst_dec.jalr | take_flush,
            mux(inst_rvc, 2, 4), op2_data_imm)
        cfi_jump_target = mux(inst_dec.jalr, alu.io.out, pc_add_offset)
        jalr_ra = pc_add_offset
        lsu_wxd = (
            self.io.lsu.resp.fire() & 
            ~self.io.lsu.resp.bits.tag[0] & 
            self.io.lsu.resp.bits.has_data)
        muldiv_wxd = muldiv.io.resp.fire()
        csr_wxd = inst_dec.csr_cmd != CSR_CONSTS.N()
        rf_wdata = mux(
            lsu_wxd, 
            self.io.lsu.resp.bits.data, 
            mux(
                muldiv_wxd,
                muldiv.io.resp.bits.data,
                   mux(
                       csr_wxd,
                       csr.io.rw.rdata, 
                       mux(
                           inst_dec.jalr,
                           jalr_ra,
                           mux(
                               inst_dec.fp & inst_dec.wxd,
                               self.io.fpu.toint_data.bits,
                               alu.io.out)))))
        rf_rd = mux(
            lsu_wxd,
            self.io.lsu.resp.bits.tag[5:1],
            mux(muldiv_wxd, muldiv.io.resp.bits.tag[4:0], inst_pre_dec.rd))
        inst_wxd = (
            inst_valid & 
            retire_en & 
            ~take_exception & 
            inst_dec.wxd & 
            inst_none_lsu_muldiv)
        rf_wxd = inst_wxd | lsu_wxd | muldiv_wxd
        rf.write(rf_wxd, rf_rd, rf_wdata)


        ####
        #csr file control
        csr.io.decode[0].csr /= inst[31:20]
        csr.io.exception /= inst_valid & take_exception
        csr.io.cause /= exception_cause
        csr.io.retire /= inst_valid & retire_en & ~take_exception
        csr.io.inst[0] /= inst
        csr.io.interrupts /= self.io.interrupts
        csr.io.hartid /= self.io.hartid
        self.io.fpu.fcsr_rm /= csr.io.fcsr_rm
        csr.io.fcsr_flags /= self.io.fpu.fcsr_flags
        csr.io.rocc_interrupt /= 0
        csr.io.pc /= pc
        csr.io.tval /= exception_tval
        csr.io.rw.addr /= inst[31:20]
        csr.io.rw.cmd /= mux(
            inst_valid & retire_en & ~take_exception,
            mux(inst_csr_ren, CSR_CONSTS.R(), inst_dec.csr_cmd), CSR_CONSTS.N())
        csr.io.rw.wdata /= alu.io.out
        self.io.csr_trace /= csr.io.trace

        csr_stall /= csr.io.csr_stall
        fcsr_stall /= inst_csr_en & csr.io.decode[0].fp_csr & ~self.io.fpu.fcsr_rdy


        #hpm performance counter
        if (self.p.csr_num_perf_counters > 0):
            hpm_events = [
                [#set0
                    ("exception", csr.io.exception),
                    ("load",      (
                        inst_valid & 
                        self.io.lsu.req.fire() & 
                        (self.io.lsu.req.bits.cmd == M_CONSTS.M_XRD()) & 
                        ~inst_dec.fp)),
                    ("store",     (
                        inst_valid & 
                        self.io.lsu.req.fire() & 
                        (self.io.lsu.req.bits.cmd == M_CONSTS.M_XWR()) & 
                        ~inst_dec.fp)),
                    ("amo",       ((
                        inst_valid & 
                        self.io.lsu.req.fire() & 
                        M_CONSTS.is_amo(self.io.lsu.req.bits.cmd)) 
                            if (self.p.isa_a) else 0)),
                    ("system",    inst_valid & (csr.io.rw.cmd != CSR_CONSTS.N())),
                    ("arith",     inst_valid & retire_en & inst_arith),
                    ("branch",    inst_valid & retire_en & inst_dec.branch),
                    ("jal",       inst_valid & retire_en & inst_dec.jal),
                    ("jalr",      inst_valid & retire_en & inst_dec.jalr)] + (([
                    ("mul",       inst_valid & muldiv.io.req.fire() & inst_dec.mul),
                    ("div",       (inst_valid & muldiv.io.req.fire() & inst_dec.div))])
                        if (self.p.isa_m) else []),
                [#set1
                    ("branch misprediction", (
                        inst_valid & 
                        self.io.ifu.req.fire() & 
                        take_branch)),
                    ("flush",                inst_valid & retire_en & take_flush)],
                [#set2
                    ("ifu refill",     self.io.ifu.events.refill),
                    ("lsu refill",     self.io.lsu.events.refill),
                    ("lsu write back", self.io.lsu.events.write_back)]]
            for c in csr.io.counters:
                c.inc /= self.hpm_counter_inc(c.event_sel, hpm_events)


        bpu = zqh_core_common_break_point_unit('bpu')
        bpu.io.status /= csr.io.status
        bpu.io.bp /= csr.io.bp
        bpu.io.pc /= inst_asm_buffer.io.out.bits.pc
        bpu.io.ea /= alu.io.out


        
        ####
        #interrupt/exception
        exception_interrupt = csr.io.interrupt
        exception_debug_if_break_point  = bpu.io.debug_if
        exception_xcpt_if_break_point = bpu.io.xcpt_if
        exception_fetch_access = inst_asm_buffer.io.out.bits.xcpt.pack()
        exception_illegal_inst = (
            ~inst_dec.legal | 
            ((inst_dec.mul | inst_dec.div) & ~csr.io.status.isa[ord('m')-ord('a')]) | 
            (inst_dec.amo & ~csr.io.status.isa[ord('a')-ord('a')]) | \
            (inst_dec.fp & (csr.io.decode[0].fp_illegal | self.io.fpu.illegal_rm)) | 
            (inst_dec.dp & ~csr.io.status.isa[ord('d')-ord('a')]) | 
            (inst_dec.rocc & csr.io.decode[0].rocc_illegal) | 
            (
                inst_csr_en & 
                (
                    csr.io.decode[0].read_illegal | 
                    (~inst_csr_ren & csr.io.decode[0].write_illegal))) | 
            (inst_system & csr.io.decode[0].system_illegal))
        exception_id = (
            exception_interrupt |
            exception_debug_if_break_point |
            exception_xcpt_if_break_point |
            exception_fetch_access |
            exception_illegal_inst)

        exception_misaligned_fetch = (
            ~csr.io.status.isa[ord('c')-ord('a')] & 
            (take_cfi & cfi_jump_target[1] & ~hazard_wait))

        lsu_xcpt = self.lsu_xcpt_check(self.io.lsu.req.bits)
        exception_misaligned_load = (
            inst_dec.mem & 
            mem_is_read & 
            lsu_xcpt.ma.ld & 
            ~hazard_wait)
        exception_misaligned_store = (
            inst_dec.mem & 
            mem_is_write & 
            lsu_xcpt.ma.st & 
            ~hazard_wait)
        exception_load_access = inst_dec.mem & mem_is_read & lsu_xcpt.ae.ld & ~hazard_wait
        exception_store_access = inst_dec.mem & mem_is_write & lsu_xcpt.ae.st & ~hazard_wait

        exception_xcpt_ld_st_breakpoint = (
            (inst_dec.mem & mem_is_read & bpu.io.xcpt_ld) | 
            (inst_dec.mem & mem_is_write & bpu.io.xcpt_st))
        exception_debug_ld_st_breakpoint = (
            (inst_dec.mem & mem_is_read & bpu.io.debug_ld) | 
            (inst_dec.mem & mem_is_write & bpu.io.debug_st))

        #lsu ae excption is imprecise, need hold them untill inst_valid
        exception_cause_map = (
            (exception_interrupt,        csr.io.interrupt_cause),
            (exception_debug_if_break_point,         CSR_CONSTS.debugTriggerCause()),
            (exception_xcpt_if_break_point,   CS_CONSTS.breakpoint),
            (exception_fetch_access,     CS_CONSTS.fetch_access),
            (exception_illegal_inst,     CS_CONSTS.illegal_instruction),
            (exception_misaligned_fetch, CS_CONSTS.misaligned_fetch),
            (exception_misaligned_store, CS_CONSTS.misaligned_store),
            (exception_misaligned_load,  CS_CONSTS.misaligned_load),
            (exception_store_access,     CS_CONSTS.store_access),
            (exception_load_access,      CS_CONSTS.load_access),
            (exception_debug_ld_st_breakpoint, CSR_CONSTS.debugTriggerCause()),
            (exception_xcpt_ld_st_breakpoint, CS_CONSTS.breakpoint)
            )
        take_exception /= reduce(lambda a,b: a[0] | b[0], exception_cause_map)
        take_eret /= csr.io.eret
        exception_cause /= sel_p_lsb(exception_cause_map)
        exception_tval /= sel_oh(
            [exception_illegal_inst, exception_misaligned_load | exception_misaligned_store],
            [0, self.io.lsu.req.bits.addr])


        #tmp with when(retire_en):
        #tmp     with when(exception_id & ~exception_interrupt):
        #tmp         inst_dec.alu_fn /= A_CONSTS.FN_ADD()
        #tmp         inst_dec.alu_dw /= csr.io.status.rv64
        #tmp         inst_dec.sel_alu1 /= D_CONSTS.A1_RS1()
        #tmp         inst_dec.sel_alu2 /= D_CONSTS.A2_ZERO()
        #tmp         with when(exception_xcpt_if_break_point | exception_fetch_access):
        #tmp             inst_dec.sel_alu1 /= D_CONSTS.A1_PC()
        #tmp             inst_dec.sel_alu2 /= D_CONSTS.A2_ZERO()
        with when(exception_id & ~exception_interrupt):
            inst_dec.alu_fn /= A_CONSTS.FN_ADD()
            inst_dec.alu_dw /= csr.io.status.rv64
            inst_dec.sel_alu1 /= D_CONSTS.A1_RS1()
            inst_dec.sel_alu2 /= D_CONSTS.A2_ZERO()
            with when(exception_xcpt_if_break_point | exception_fetch_access):
                inst_dec.sel_alu1 /= D_CONSTS.A1_PC()
                inst_dec.sel_alu2 /= D_CONSTS.A2_ZERO()

        with when(inst_dec.jalr & csr.io.status.debug):
            inst_dec.fence_i /= 1


        ####
        #ifu cmd gen
        #pc branch/jump/exception
        #icache flush
        ifu_req_vaddr = mux(take_exception | take_eret, csr.io.evec, cfi_jump_target)
        self.io.ifu.req.bits.vaddr /= ifu_req_vaddr
        self.io.ifu.req.bits.error /= (
            ifu_req_vaddr[self.p.xlen - 1 : self.p.vaddr_bits] != ifu_req_vaddr[
                self.p.vaddr_bits - 1].rep(self.p.xlen - self.p.vaddr_bits)
                    if (self.p.vaddr_bits < self.p.xlen) else 0)
        self.io.ifu.req.valid /= 0
        self.io.ifu.req.bits.cmd /= IFU_CONSTS.FETCH()
        with when(inst_valid & ((retire_en & (take_cfi | take_eret)) | take_exception)):
            self.io.ifu.req.valid /= 1
            with when(inst_dec.fence_i):
                self.io.ifu.req.bits.cmd /= IFU_CONSTS.FLUSH()
        with elsewhen(inst_valid & retire_en & ~take_exception & take_flush):
            self.io.ifu.req.valid /= 1
            with when(inst_dec.fence_i):
                self.io.ifu.req.bits.cmd /= IFU_CONSTS.FLUSH()

        self.io.ifu.rv64 /= csr.io.status.rv64

    def imm_gen(self, sel_imm, inst):
        if isinstance(sel_imm, value):
            sel = sel_imm.to_bits()
        elif isinstance(sel_imm, int):
            sel = value(sel_imm).to_bits()
        else:
            sel = sel_imm

        imm = bits(w = 32, init = 0).to_sint()
        with when(sel == D_CONSTS.IMM_S()):
            imm /= cat([inst[31].rep(20), inst[31:25], inst[11:7]])
        with elsewhen(sel == D_CONSTS.IMM_B()):
            imm /= cat([inst[31].rep(20), inst[7], inst[30:25],
                inst[11:8], value(0, w = 1)])
        with elsewhen(sel == D_CONSTS.IMM_U()):
            imm /= cat([inst[31:12], value(0, 12)])
        with elsewhen(sel == D_CONSTS.IMM_J()):
            imm /= cat([inst[31].rep(11), inst[31], inst[19:12], inst[20],
                inst[30:21], value(0, 1)])
        with elsewhen(sel == D_CONSTS.IMM_I()):
            imm /= cat([inst[31].rep(20), inst[31:20]])
        with elsewhen(sel == D_CONSTS.IMM_Z()):
            imm /= cat([value(0, w = 27), inst[19:15]])

        return imm
    
    def hpm_counter_inc(self, event_sel, event_sets):
        assert(len(event_sets) <= (2 ** self.p.csr_event_set_id_bits))
        which_set = event_sel[log2_ceil(len(event_sets))-1: 0]
        max_size = max(map(lambda _: len(_), event_sets))
        mask = (event_sel >> self.p.csr_event_set_id_bits)[max_size - 1 : 0]
        sets = map(lambda x: (mask & cat_rvs(map(lambda _: _[1], x))).r_or(), event_sets)
        return sel_bin(which_set,sets)

    def lsu_xcpt_check(self, a):
        xcpt = zqh_core_common_lsu_exceptions(init = 0)

        is_read = M_CONSTS.is_read(a.cmd)
        is_write = M_CONSTS.is_write(a.cmd)
        is_lr_sc = a.cmd.match_any([M_CONSTS.M_XLR(), M_CONSTS.M_XSC()])

        xcpt.ae.ld /= (a.error & is_read) | is_lr_sc
        xcpt.ae.st /= (a.error & is_write) | is_lr_sc

        size = a.type[log2_up(log2_up(a.p.word_bytes) + 1) - 1: 0]
        ma = reduce(
            lambda a,b: a | b, 
            map(
                lambda _: 0 if (_ == 0) else ((a.addr[_ - 1 : 0] != 0) & (size == _)),
                range(log2_up(a.p.word_bytes) + 1)))
        xcpt.ma.ld /= ma & is_read
        xcpt.ma.st /= ma & is_write

        return xcpt
