####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/CSR.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_core_common_csr_bundles import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter

class zqh_core_common_csr_file(module):
    def set_par(self):
        super(zqh_core_common_csr_file, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_port(self):
        super(zqh_core_common_csr_file, self).set_port()
        self.io = zqh_core_common_csr_file_io('io')

    def main(self):
        super(zqh_core_common_csr_file, self).main()
        reset_mstatus = zqh_core_common_csr_mstatus('reset_mstatus', init = 0)
        reset_mstatus.mpp /= PRV_CONSTS.M()
        reset_mstatus.prv /= PRV_CONSTS.M()
        reg_mstatus = zqh_core_common_csr_mstatus(
            'reg_mstatus').as_reg(tp = 'reg_rs', rs = reset_mstatus)
  
        new_prv = bits('new_prv', w = reg_mstatus.prv.get_w(), init = reg_mstatus.prv)
        reg_mstatus.prv /= self.legalizePrivilege(new_prv)

        reset_dcsr = zqh_core_common_csr_dcsr('reset_dcsr', init = 0)
        reset_dcsr.xdebugver /= 1
        reset_dcsr.prv /= PRV_CONSTS.M()
        reg_dcsr = zqh_core_common_csr_dcsr('reg_dcsr').as_reg(next = reset_dcsr)
  
        sup = zqh_core_common_csr_mip('sup')
        sup.usip /= 0
        sup.ssip /= self.p.use_vm
        sup.hsip /= 0
        sup.msip /= 1
        sup.utip /= 0
        sup.stip /= self.p.use_vm
        sup.htip /= 0
        sup.mtip /= 1
        sup.ueip /= 0
        sup.seip /= self.p.use_vm
        sup.heip /= 0
        sup.meip /= 1
        sup.rocc /= self.p.isa_custom
        sup.zero1 /= 0
        sup.debug /= 0
        sup.zero2 /= 0
        for i in sup.lip:
            i /= 1
        supported_high_interrupts = 0
  
        del_ = zqh_core_common_csr_mip('del_', init = sup)
        del_.msip /= 0
        del_.mtip /= 0
        del_.meip /= 0
        (self.supported_interrupts, delegable_interrupts) = (
            sup.pack() | supported_high_interrupts,
            del_.pack())

        delegable_exceptions = sum(list(map(lambda i: 1<< i, [
            CS_CONSTS.misaligned_fetch,
            CS_CONSTS.fetch_page_fault,
            CS_CONSTS.breakpoint,
            CS_CONSTS.load_page_fault,
            CS_CONSTS.store_page_fault,
            CS_CONSTS.user_ecall])))
  
        reg_debug = reg_r('reg_debug')
        reg_dpc = reg('reg_dpc', w = self.p.vaddr_bits)
        reg_dscratch = reg('reg_dscratch', w = self.p.xlen)
        reg_singleStepped = reg('reg_singleStepped')
  
        reg_tselect = reg('reg_tselect', w = log2_up(self.p.csr_num_breakpoints))
        reg_bp = list(map(
            lambda i: zqh_core_common_csr_bp('reg_bp_'+str(i)).as_reg(tp = 'reg_r'), 
            range(1 << log2_up(self.p.csr_num_breakpoints))))
  
        reg_mie = reg('reg_mie', w = self.p.xlen)
        reg_mideleg = reg_r('reg_mideleg', w = self.p.xlen)
        reg_medeleg = reg_r('reg_medeleg', w = self.p.xlen)
        reg_mip = zqh_core_common_csr_mip('reg_mip').as_reg()
        reg_mepc = reg('reg_mepc', w = self.p.vaddr_bits)
        reg_mcause = reg('reg_mcause', w = self.p.xlen)
        reg_mbadaddr = reg('reg_mbadaddr', w = self.p.vaddr_bits)
        reg_mscratch = reg('reg_mscratch', w = self.p.xlen)
        reg_mtvec = reg_r('reg_mtvec', w = self.p.xlen)
        reg_mcounteren = reg('reg_mcounteren', w = 32)
        reg_scounteren = reg('reg_scounteren', w = 32)
        delegable_counters = (1 << (self.p.csr_num_perf_counters + CSR_CONSTS.firstHPM)) - 1
  
        reg_sepc = reg('reg_sepc', w = self.p.vaddr_bits)
        reg_scause = reg('reg_scause', w = self.p.xlen)
        reg_sbadaddr = reg('reg_sbadaddr', w = self.p.vaddr_bits)
        reg_sscratch = reg('reg_sscratch', w = self.p.xlen)
        reg_stvec = reg('reg_stvec', w = self.p.vaddr_bits)
        reg_satp = zqh_core_common_csr_satp('reg_satp').as_reg()
        reg_wfi = reg_r('reg_wfi')
  
        reg_fflags = reg('reg_fflags', w = 5)
        reg_frm = reg('reg_frm', w = 3)
  
        reg_instret = reg_r('reg_instret', w = 64)
        reg_instret /= reg_instret + self.io.retire
        reg_cycle = reg_r('reg_cycle', w = 64)
        reg_cycle /= reg_cycle + 1
        reg_hpmevent = list(map(lambda c: reg_r(w = self.p.xlen), self.io.counters))
        for (c, e) in zip(self.io.counters, reg_hpmevent):
            c.event_sel /= e
        reg_hpmcounter = list(map(
            lambda c: reg_r(
                'reg_hpmcounter_'+str(
                    CSR_CONSTS.firstHPM + 
                    list(self.io.counters).index(c)), 
                w = CSR_CONSTS.hpmWidth),
            self.io.counters))
        for i in range(len(self.io.counters)):
            with when(self.io.counters[i].inc):
                reg_hpmcounter[i] /= reg_hpmcounter[i] + 1
  
        mip = zqh_core_common_csr_mip('mip', init=reg_mip)
        for i in mip.lip:
            mip.lip[i] /= self.io.interrupts.lip[i]
        mip.mtip /= self.io.interrupts.mtip
        mip.msip /= self.io.interrupts.msip
        mip.meip /= self.io.interrupts.meip
        ## seip is the OR of reg_mip.seip and the actual line from the PLIC
        if (self.p.use_vm):
            for i in [self.io.interrupts.seip]:
                mip.seip /= reg_mip.seip | reg(next = i)
        mip.rocc /= self.io.rocc_interrupt
        read_mip = mip.pack() & self.supported_interrupts
  
        pending_interrupts = read_mip & reg_mie
        d_interrupts = self.io.interrupts.debug << CSR_CONSTS.debugIntCause()
        m_interrupts = mux(
            (reg_mstatus.prv <= PRV_CONSTS.S()) | reg_mstatus.mie,
            ~(~pending_interrupts | reg_mideleg),
            0)
        s_interrupts = mux(
            (reg_mstatus.prv < PRV_CONSTS.S()) | 
                (((reg_mstatus.prv == PRV_CONSTS.S()) & reg_mstatus.sie)),
            pending_interrupts & reg_mideleg,
            0)
        (anyInterrupt, whichInterrupt) = self.chooseInterrupt([
            s_interrupts, m_interrupts, d_interrupts])
        interruptMSB = 1 << (self.p.xlen-1)
        interruptCause = interruptMSB + whichInterrupt
        self.io.interrupt /= (((anyInterrupt & ~self.io.singleStep) | reg_singleStepped) &
            ~reg_debug)
        self.io.interrupt_cause /= interruptCause
        for i in range(self.p.csr_num_breakpoints):
            self.io.bp[i] /= reg_bp[i]
  
        isaMaskString = \
            ("M" if (self.p.isa_m) else "") + \
            ("A" if (self.p.isa_a) else "") + \
            ("F" if (self.p.flen >= 32) else "") + \
            ("D" if (self.p.flen >= 64) else "") + \
            ("C" if (self.p.isa_c) else "") + \
            ("X" if (self.p.isa_custom) else "")
        isaString =  \
             "I" + isaMaskString + \
            ("S" if (self.p.use_vm) else "") + \
            ("U" if (self.p.use_user_vm) else "")
        isaMax = (
            ((log2_ceil(self.p.xlen) - 4) << (self.p.xlen-2)) | 
            self.isaStringToMask(isaString))
        self.reg_misa = reg_rs('reg_misa', w = self.p.xlen, rs = isaMax)
        read_mstatus = self.io.status.pack()[self.p.xlen-1:0]
  
        read_mapping = {
            CSRA_CONSTS.tselect : reg_tselect,
            CSRA_CONSTS.tdata1 : sel_bin(
                reg_tselect,
                map(lambda x: x.control.pack(), reg_bp)),
            CSRA_CONSTS.tdata2 : sel_bin(
                reg_tselect,
                map(lambda x: x.address.s_ext(self.p.xlen), reg_bp)),
            CSRA_CONSTS.mimpid : value(0),
            CSRA_CONSTS.marchid : value(0),
            CSRA_CONSTS.mvendorid : value(0),
            CSRA_CONSTS.misa : self.reg_misa,
            CSRA_CONSTS.mstatus : read_mstatus,
            CSRA_CONSTS.mtvec : reg_mtvec,
            CSRA_CONSTS.mip : read_mip,
            CSRA_CONSTS.mie : reg_mie,
            CSRA_CONSTS.mscratch : reg_mscratch,
            CSRA_CONSTS.mepc : self.readEPC(reg_mepc).s_ext(self.p.xlen),
            CSRA_CONSTS.mbadaddr : reg_mbadaddr.s_ext(self.p.xlen),
            CSRA_CONSTS.mcause : reg_mcause,
            CSRA_CONSTS.mhartid : self.io.hartid}
  
        debug_csrs = {
            CSRA_CONSTS.dcsr : reg_dcsr.pack(),
            CSRA_CONSTS.dpc : self.readEPC(reg_dpc).s_ext(self.p.xlen),
            CSRA_CONSTS.dscratch : reg_dscratch}
  
        fp_csrs = {
            CSRA_CONSTS.fflags : reg_fflags,
            CSRA_CONSTS.frm : reg_frm,
            CSRA_CONSTS.fcsr : cat([reg_frm, reg_fflags])}
  
        if (self.p.use_debug):
            read_mapping.update(debug_csrs)
  
        if (self.p.isa_f):
            read_mapping.update(fp_csrs)
  
        if (self.p.csr_have_basic_counters):
            read_mapping.update({CSRA_CONSTS.mcycle : reg_cycle})
            read_mapping.update({CSRA_CONSTS.minstret : reg_instret})
  
            for ((e, c), i) in zip(
                zip(
                    pad_to(reg_hpmevent, CSR_CONSTS.nHPM, 0),
                    pad_to(map(lambda _: _, reg_hpmcounter), CSR_CONSTS.nHPM, 0)),
                range(CSR_CONSTS.nHPM)):
                read_mapping.update({(i + CSR_CONSTS.firstHPE) : e}) ## mhpmeventN
                read_mapping.update({(i + CSR_CONSTS.firstMHPC) : c}) ## mhpmcounterN
                if (self.p.use_user_vm):
                    read_mapping.update({(i + CSR_CONSTS.firstHPC) : c}) ## hpmcounterN
                if (self.p.xlen == 32):
                    read_mapping.update({(i + CSR_CONSTS.firstMHPCH) : c}) ## mhpmcounterNh
                    if (self.p.use_user_vm):
                        read_mapping.update({(i + CSR_CONSTS.firstHPCH) : c}) ## hpmcounterNh
  
            if (self.p.use_user_vm):
                read_mapping.update({CSRA_CONSTS.mcounteren : reg_mcounteren})
                read_mapping.update({CSRA_CONSTS.cycle : reg_cycle})
                read_mapping.update({CSRA_CONSTS.instret : reg_instret})
  
            if (self.p.xlen == 32):
                read_mapping.update({CSRA_CONSTS.mcycleh : (reg_cycle >> 32)})
                read_mapping.update({CSRA_CONSTS.minstreth : (reg_instret >> 32)})
                if (self.p.use_user_vm):
                    read_mapping.update({CSRA_CONSTS.cycleh : (reg_cycle >> 32)})
                    read_mapping.update({CSRA_CONSTS.instreth : (reg_instret >> 32)})
  
        if (self.p.use_vm):
            read_sie = reg_mie & reg_mideleg
            read_sip = read_mip & reg_mideleg
            read_sstatus = zqh_core_common_csr_mstatus(init = 0)
            read_sstatus.sd /= self.io.status.sd
            read_sstatus.uxl /= self.io.status.uxl
            read_sstatus.sd_rv32 /= self.io.status.sd_rv32
            read_sstatus.mxr /= self.io.status.mxr
            read_sstatus.sum /= self.io.status.sum
            read_sstatus.xs /= self.io.status.xs
            read_sstatus.fs /= self.io.status.fs
            read_sstatus.spp /= self.io.status.spp
            read_sstatus.spie /= self.io.status.spie
            read_sstatus.sie /= self.io.status.sie
  
            read_mapping.update({CSRA_CONSTS.sstatus : 
                read_sstatus.pack()[self.p.xlen-1:0]})
            read_mapping.update({CSRA_CONSTS.sip : read_sip})
            read_mapping.update({CSRA_CONSTS.sie : read_sie})
            read_mapping.update({CSRA_CONSTS.sscratch : reg_sscratch})
            read_mapping.update({CSRA_CONSTS.scause : reg_scause})
            read_mapping.update({CSRA_CONSTS.sbadaddr : reg_sbadaddr.s_ext(self.p.xlen)})
            read_mapping.update({CSRA_CONSTS.satp : reg_satp.pack()})
            read_mapping.update({CSRA_CONSTS.sepc : 
                self.readEPC(reg_sepc).s_ext(self.p.xlen)})
            read_mapping.update({CSRA_CONSTS.stvec : reg_stvec.s_ext(self.p.xlen)})
            read_mapping.update({CSRA_CONSTS.scounteren : reg_scounteren})
            read_mapping.update({CSRA_CONSTS.mideleg : reg_mideleg})
            read_mapping.update({CSRA_CONSTS.medeleg : reg_medeleg})
  
        self.decoded_addr = dict(zip(
            read_mapping.keys(),
            map(lambda k: self.io.rw.addr == k, read_mapping.keys())))
        wdata = self.readModifyWriteCSR(self.io.rw.cmd, self.io.rw.rdata, self.io.rw.wdata)
  
        system_insn = self.io.rw.cmd == CSR_CONSTS.I()
        insn_ecall = system_insn & self.io.rw.addr.match_any([CSR_CONSTS.SYSTEM_ECALL()])
        insn_ebreak = system_insn & self.io.rw.addr.match_any([CSR_CONSTS.SYSTEM_EBREAK()])
        insn_mret = system_insn & (
            (self.io.rw.addr.match_any([CSR_CONSTS.SYSTEM_MRET()])) |
            (self.io.rw.addr.match_any([CSR_CONSTS.SYSTEM_DRET()])
                if (self.p.use_debug) else 0) |
            (self.io.rw.addr.match_any([
                CSR_CONSTS.SYSTEM_SRET(),
                CSR_CONSTS.SYSTEM_SFENCE_VMA()]) if (self.p.use_vm) else 0))
        insn_wfi = system_insn & self.io.rw.addr.match_any([CSR_CONSTS.SYSTEM_WFI()])
        insn_sfence = system_insn & (self.io.rw.addr.match_any([
            CSR_CONSTS.SYSTEM_SFENCE_VMA()]) if (self.p.use_vm) else 0)
  
        for io_dec in self.io.decode:
            is_call = io_dec.csr == CSR_CONSTS.SYSTEM_ECALL()
            is_break = io_dec.csr == CSR_CONSTS.SYSTEM_EBREAK()
            is_mret = io_dec.csr == CSR_CONSTS.SYSTEM_MRET()
            is_wfi = io_dec.csr == CSR_CONSTS.SYSTEM_WFI()
            is_sfence = io_dec.csr == CSR_CONSTS.SYSTEM_SFENCE_VMA()
            def decodeAny(m):
                return reduce(lambda x, y: x | y, map(lambda k: io_dec.csr == k, m.keys()))
            allow_wfi = (
                (self.p.use_vm == 0) | 
                (reg_mstatus.prv > PRV_CONSTS.S()) | 
                ~reg_mstatus.tw)
            allow_sfence_vma = (
                (self.p.use_vm == 0) | 
                (reg_mstatus.prv > PRV_CONSTS.S()) | 
                ~reg_mstatus.tvm)
            allow_sret = (
                (self.p.use_vm == 0) | 
                (reg_mstatus.prv > PRV_CONSTS.S()) | 
                ~reg_mstatus.tsr)
            counter_addr = io_dec.csr[log2_ceil(reg_mcounteren.get_w())-1: 0]
            allow_counter = (
                (reg_mstatus.prv > PRV_CONSTS.S()) | 
                reg_mcounteren[counter_addr]) & (
                    (reg_mstatus.prv >= PRV_CONSTS.S()) | 
                    reg_scounteren[counter_addr])
            io_dec.fp_illegal /= (self.io.status.fs == 0) | ~self.reg_misa[ord('f')-ord('a')]
            io_dec.fp_csr /=  self.p.isa_f & io_dec.csr.match_any(fp_csrs.keys())
            io_dec.rocc_illegal /= (
                (self.io.status.xs == 0) | 
                ~self.reg_misa[ord('x')-ord('a')])
            io_dec.read_illegal /= (
                (reg_mstatus.prv < io_dec.csr[9:8]) |
                ~decodeAny(read_mapping) |
                (io_dec.csr == CSRA_CONSTS.satp & ~allow_sfence_vma) |
                ((
                    (
                        (io_dec.csr >= CSR_CONSTS.firstCtr) & 
                        (io_dec.csr < (CSR_CONSTS.firstCtr + CSR_CONSTS.nCtr))) | 
                    (
                        (io_dec.csr >= CSR_CONSTS.firstCtrH) & 
                        (io_dec.csr < (CSR_CONSTS.firstCtrH + CSR_CONSTS.nCtr)))) & 
                    ~allow_counter) |
                ((self.p.use_debug) & decodeAny(debug_csrs) & ~reg_debug) |
                (io_dec.fp_csr & io_dec.fp_illegal))
            io_dec.write_illegal /= io_dec.csr[11:10].r_and()
            io_dec.write_flush /= ~(
                (
                    (io_dec.csr >= CSRA_CONSTS.mscratch) & 
                    (io_dec.csr <= CSRA_CONSTS.mbadaddr)) | 
                (
                    (io_dec.csr >= CSRA_CONSTS.sscratch) & 
                    (io_dec.csr <= CSRA_CONSTS.sbadaddr)))
            io_dec.system_illegal /= (
                (reg_mstatus.prv < io_dec.csr[9:8]) |
                (is_wfi & ~allow_wfi) |
                (is_mret & ~allow_sret) |
                (is_sfence & ~allow_sfence_vma))
  
        cause = mux(
            insn_ecall,
            reg_mstatus.prv + CS_CONSTS.user_ecall,
            mux(insn_ebreak, CS_CONSTS.breakpoint, self.io.cause))
        cause_lsbs = cause[self.io.trace[0].cause.get_w()-1: 0]
        causeIsDebugInt = cause[self.p.xlen-1] & (cause_lsbs == CSR_CONSTS.debugIntCause())
        causeIsDebugTrigger = (
            ~cause[self.p.xlen-1] & 
            (cause_lsbs == CSR_CONSTS.debugTriggerCause()))
        causeIsDebugBreak = (
            ~cause[self.p.xlen-1] & 
            insn_ebreak & 
            cat([
                reg_dcsr.ebreakm,
                reg_dcsr.ebreakh,
                reg_dcsr.ebreaks,
                reg_dcsr.ebreaku])[reg_mstatus.prv])
        trapToDebug = self.p.use_debug & (
            reg_singleStepped | 
            causeIsDebugInt | 
            causeIsDebugTrigger | 
            causeIsDebugBreak | 
            reg_debug)
        debugTVec = mux(reg_debug, mux(insn_ebreak, 0x800, 0x808), 0x800)
        delegate = (
            self.p.use_vm & 
            (reg_mstatus.prv <= PRV_CONSTS.S()) & 
            mux(
                cause[self.p.xlen-1],
                reg_mideleg[cause_lsbs],
                reg_medeleg[cause_lsbs]))
        mtvecInterruptAlign = log2_ceil(zqh_core_common_csr_mip().get_w())
  
        base = mux(delegate, reg_stvec.s_ext(self.p.vaddr_bits), reg_mtvec)
        interruptOffset = cause[mtvecInterruptAlign-1: 0] << 2
        interruptVec = cat([base >> (mtvecInterruptAlign + 2), interruptOffset])
        doVector = (
            base[0] & 
            cause[cause.get_w()-1] & 
            ((cause_lsbs >> mtvecInterruptAlign) == 0))
        notDebugTVec = mux(doVector, interruptVec, base)
  
        tvec = mux(trapToDebug, debugTVec, notDebugTVec)
        self.io.evec /= tvec
        self.io.eret /= insn_ecall | insn_ebreak | insn_mret
        self.io.singleStep /= reg_dcsr.step & ~reg_debug
        self.io.status /= reg_mstatus
        self.io.status.sd /= self.io.status.fs.r_and() | self.io.status.xs.r_and()
        self.io.status.debug /= reg_debug
        self.io.status.isa /= self.reg_misa
        self.io.status.rv64 /= self.reg_misa.msb(2) == CSR_CONSTS.XL_64()
        self.io.status.uxl /= (log2_ceil(self.p.xlen) - 4) if (self.p.use_user_vm) else 0
        self.io.status.sxl /= (log2_ceil(self.p.xlen) - 4) if (self.p.use_vm) else 0
        self.io.status.dprv /= reg(
            w = max(reg_mstatus.mpp.get_w(), reg_mstatus.prv.get_w()),
            next = mux(reg_mstatus.mprv & ~reg_debug, reg_mstatus.mpp, reg_mstatus.prv)) 
        if (self.p.xlen == 32):
            self.io.status.sd_rv32 /= self.io.status.sd
  
        exception = insn_ecall | insn_ebreak | self.io.exception
        vassert(
            count_ones([insn_mret, insn_ecall, insn_ebreak, self.io.exception]) <= 1,
            "these conditions must be mutually exclusive")
  
        with when (insn_wfi & ~self.io.singleStep & ~reg_debug):
            reg_wfi /= 1
  
        with when (pending_interrupts.r_or() | exception | self.io.interrupts.debug):
            reg_wfi /= 0
  
        with when (self.io.retire[0] | exception):
            reg_singleStepped /= 1
        with when (~self.io.singleStep):
            reg_singleStepped /= 0
        vassert(~self.io.singleStep | (self.io.retire <= 1))
        vassert(~reg_singleStepped | (self.io.retire == 0))
  
        epc = self.formEPC(self.io.pc)
  
        with when (exception):
            with when (trapToDebug):
                with when (~reg_debug):
                    reg_debug /= 1
                    reg_dpc /= epc
                    reg_dcsr.cause /= mux(
                        reg_singleStepped,
                        4,
                        mux(causeIsDebugInt, 3, mux(causeIsDebugTrigger, 2, 1)))
                    reg_dcsr.prv /= self.trimPrivilege(reg_mstatus.prv)
                    new_prv /= PRV_CONSTS.M()
            with elsewhen (delegate):
                reg_sepc /= epc
                reg_scause /= cause
                reg_sbadaddr /= self.io.tval
                reg_mstatus.spie /= reg_mstatus.sie
                reg_mstatus.spp /= reg_mstatus.prv
                reg_mstatus.sie /= 0
                new_prv /= PRV_CONSTS.S()
            with other():
                reg_mepc /= epc
                reg_mcause /= cause
                reg_mbadaddr /= self.io.tval
                reg_mstatus.mpie /= reg_mstatus.mie
                reg_mstatus.mpp /= self.trimPrivilege(reg_mstatus.prv)
                reg_mstatus.mie /= 0
                new_prv /= PRV_CONSTS.M()
  
        with when (insn_mret):
            with when (self.p.use_vm & ~self.io.rw.addr[9]):
                reg_mstatus.sie /= reg_mstatus.spie
                reg_mstatus.spie /= 1
                reg_mstatus.spp /= PRV_CONSTS.U()
                new_prv /= reg_mstatus.spp
                self.io.evec /= self.readEPC(reg_sepc)
            with elsewhen (self.p.use_debug & self.io.rw.addr[10]):
                new_prv /= reg_dcsr.prv
                reg_debug /= 0
                self.io.evec /= self.readEPC(reg_dpc)
            with other():
                reg_mstatus.mie /= reg_mstatus.mpie
                reg_mstatus.mpie /= 1
                reg_mstatus.mpp /= self.legalizePrivilege(PRV_CONSTS.U())
                new_prv /= reg_mstatus.mpp
                self.io.evec /= self.readEPC(reg_mepc)
  
        self.io.time /= reg_cycle
        self.io.csr_stall /= reg_wfi
  
        self.io.rw.rdata /= sel_oh(
            map(
                lambda k: self.decoded_addr[k],
                read_mapping.keys()),
            read_mapping.values())
  
        self.io.fcsr_rm /= reg_frm
        with when (self.io.fcsr_flags.valid):
            reg_fflags /= reg_fflags | self.io.fcsr_flags.bits
  
        with when (self.io.rw.cmd.match_any([
            CSR_CONSTS.S(),
            CSR_CONSTS.C(),
            CSR_CONSTS.W()])):
            with when (self.decoded_addr[CSRA_CONSTS.mstatus]):
                new_mstatus = zqh_core_common_csr_mstatus(init = wdata)
                reg_mstatus.mie /= new_mstatus.mie
                reg_mstatus.mpie /= new_mstatus.mpie
  
                if (self.p.use_user_vm):
                    reg_mstatus.mprv /= new_mstatus.mprv
                    reg_mstatus.mpp /= self.legalizePrivilege(new_mstatus.mpp)
                    if (self.p.use_vm):
                        reg_mstatus.mxr /= new_mstatus.mxr
                        reg_mstatus.sum /= new_mstatus.sum
                        reg_mstatus.spp /= new_mstatus.spp
                        reg_mstatus.spie /= new_mstatus.spie
                        reg_mstatus.sie /= new_mstatus.sie
                        reg_mstatus.tw /= new_mstatus.tw
                        reg_mstatus.tvm /= new_mstatus.tvm
                        reg_mstatus.tsr /= new_mstatus.tsr
  
                if (self.p.use_vm or self.p.isa_f):
                    reg_mstatus.fs /= self.formFS(new_mstatus.fs)
                if (self.p.isa_custom):
                    reg_mstatus.xs /= new_mstatus.xs.r_or().rep(2)
            with when (self.decoded_addr[CSRA_CONSTS.misa]):
                if (self.p.csr_misa_wr_en):
                    isa_wdata = bits(w = self.reg_misa.get_w(), init = wdata)
                    #isa.d must be cleard when isa.f is cleared
                    with when(~wdata[ord('f')-ord('a')]):
                        isa_wdata[ord('d')-ord('a')] /= 0
                    with when(
                        (self.p.isa_c == 0) | 
                        (~self.io.pc[1] | 
                            isa_wdata[ord('c') - ord('a')])):
                        self.reg_misa /= isa_wdata
            with when (self.decoded_addr[CSRA_CONSTS.mip]):
                ## MIP should be modified based on the value in reg_mip, not the value
                ## in read_mip, since read_mip.seip is the OR of reg_mip.seip and
                ## io.interrupts.seip.  We don't want the value on the PLIC line to
                ## inadvertently be OR'd into read_mip.seip.
                new_mip = zqh_core_common_csr_mip(
                    init = self.readModifyWriteCSR(
                        self.io.rw.cmd,
                        reg_mip.pack(),
                        self.io.rw.wdata))
                if (self.p.use_vm):
                    reg_mip.ssip /= new_mip.ssip
                    reg_mip.stip /= new_mip.stip
                    reg_mip.seip /= new_mip.seip
            with when (self.decoded_addr[CSRA_CONSTS.mie]):
                reg_mie /= wdata & self.supported_interrupts
            with when (self.decoded_addr[CSRA_CONSTS.mepc]):
                reg_mepc /= self.formEPC(wdata)
            with when (self.decoded_addr[CSRA_CONSTS.mscratch]):
                reg_mscratch /= wdata
            with when (self.decoded_addr[CSRA_CONSTS.mtvec]):
                reg_mtvec /= ~(
                    ~wdata |
                    2 | 
                    mux(wdata[0], ((1 << mtvecInterruptAlign) - 1) << 2, 0)) 
            with when (self.decoded_addr[CSRA_CONSTS.mcause]):
                reg_mcause /= (
                    wdata & 
                    ((1 << (self.p.xlen-1)) + (1 << whichInterrupt.get_w()) - 1))
            with when (self.decoded_addr[CSRA_CONSTS.mbadaddr]):
                reg_mbadaddr /= wdata[self.p.vaddr_bits-1:0]
  
            for ((e, c), i) in zip(
                zip(reg_hpmevent,reg_hpmcounter),
                range(len(reg_hpmevent))):
                self.writeCounter(i + CSR_CONSTS.firstMHPC, c, wdata)
                with when (self.decoded_addr[i + CSR_CONSTS.firstHPE]):
                    e /= wdata
            if (self.p.csr_have_basic_counters):
                self.writeCounter(CSRA_CONSTS.mcycle, reg_cycle, wdata)
                self.writeCounter(CSRA_CONSTS.minstret, reg_instret, wdata)
  
            if (self.p.isa_f):
                with when (self.decoded_addr[CSRA_CONSTS.fflags]):
                    reg_fflags /= wdata
                with when (self.decoded_addr[CSRA_CONSTS.frm]):
                    reg_frm /= wdata
                with when (self.decoded_addr[CSRA_CONSTS.fcsr]):
                    reg_fflags /= wdata
                    reg_frm /= wdata >> reg_fflags.get_w()
            if (self.p.use_debug):
                with when (self.decoded_addr[CSRA_CONSTS.dcsr]):
                    new_dcsr = zqh_core_common_csr_dcsr(init = wdata)
                    reg_dcsr.step /= new_dcsr.step
                    reg_dcsr.ebreakm /= new_dcsr.ebreakm
                    if (self.p.use_vm):
                        reg_dcsr.ebreaks /= new_dcsr.ebreaks
                    if (self.p.use_user_vm):
                        reg_dcsr.ebreaku /= new_dcsr.ebreaku
                    if (self.p.use_user_vm):
                        reg_dcsr.prv /= self.legalizePrivilege(new_dcsr.prv)
                with when (self.decoded_addr[CSRA_CONSTS.dpc]):
                    reg_dpc /= self.formEPC(wdata)
                with when (self.decoded_addr[CSRA_CONSTS.dscratch]):
                    reg_dscratch /= wdata
            if (self.p.use_vm):
                with when (self.decoded_addr[CSRA_CONSTS.sstatus]):
                    new_sstatus = zqh_core_common_csr_mstatus(init = wdata)
                    reg_mstatus.sie /= new_sstatus.sie
                    reg_mstatus.spie /= new_sstatus.spie
                    reg_mstatus.spp /= new_sstatus.spp
                    reg_mstatus.mxr /= new_sstatus.mxr
                    reg_mstatus.sum /= new_sstatus.sum
                    reg_mstatus.fs /= self.formFS(new_sstatus.fs)
                    if (self.p.isa_custom):
                        reg_mstatus.xs /= new_sstatus.xs.r_or().rep(2)
                with when (self.decoded_addr[CSRA_CONSTS.sip]):
                    new_sip = zqh_core_common_csr_mip(init = wdata)
                    reg_mip.ssip /= new_sip.ssip
                with when (self.decoded_addr[CSRA_CONSTS.satp]):
                    new_satp = zqh_core_common_csr_satp(init = wdata)
                    valid_mode = new_satp.pgLevelsToMode(self.p.pgLevels)
                    with when (new_satp.mode == 0):
                        reg_satp.mode /= 0
                    with when (new_satp.mode == valid_mode):
                        reg_satp.mode /= valid_mode
                    with when ((new_satp.mode == 0) | (new_satp.mode == valid_mode)):
                        reg_satp.ppn /= new_satp.ppn[self.p.ppnBits-1:0]
                        if (self.p.asIdBits > 0):
                            reg_satp.asid /= new_satp.asid[self.p.asIdBits-1:0]
                with when (self.decoded_addr[CSRA_CONSTS.sie]):
                    reg_mie /= (reg_mie & ~reg_mideleg) | (wdata & reg_mideleg)
                with when (self.decoded_addr[CSRA_CONSTS.sscratch]):
                    reg_sscratch /= wdata
                with when (self.decoded_addr[CSRA_CONSTS.sepc]):
                    reg_sepc /= self.formEPC(wdata)
                with when (self.decoded_addr[CSRA_CONSTS.stvec]):
                    reg_stvec /= ~(
                        ~wdata |
                        2 |
                        mux(wdata[0], (((1 << mtvecInterruptAlign) - 1) << 2), 0))
                with when (self.decoded_addr[CSRA_CONSTS.scause]):
                    ##/* only implement 5 LSBs and MSB */
                    reg_scause /= wdata & ((1 << (self.p.xlen-1)) + 31) 
                with when (self.decoded_addr[CSRA_CONSTS.sbadaddr]):
                    reg_sbadaddr /= wdata[self.p.vaddr_bits-1:0]
                with when (self.decoded_addr[CSRA_CONSTS.mideleg]):
                    reg_mideleg /= wdata & delegable_interrupts
                with when (self.decoded_addr[CSRA_CONSTS.medeleg]):
                    reg_medeleg /= wdata & delegable_exceptions
                with when (self.decoded_addr[CSRA_CONSTS.scounteren]):
                    reg_scounteren /= wdata & delegable_counters
            if (self.p.use_user_vm):
                with when (self.decoded_addr[CSRA_CONSTS.mcounteren]):
                    reg_mcounteren /= wdata & delegable_counters
            if (self.p.csr_num_breakpoints > 0):
                with when (self.decoded_addr[CSRA_CONSTS.tselect]):
                    reg_tselect /= wdata
                for bp_idx in range(len(reg_bp)):
                    bp = reg_bp[bp_idx]
                    with when(reg_tselect == bp_idx):
                        with when (~bp.control.dmode | reg_debug):
                            with when (self.decoded_addr[CSRA_CONSTS.tdata1]):
                                newBPC = zqh_core_common_csr_bp_control(init = wdata)
                                dMode = newBPC.dmode & reg_debug
                                bp.control /= newBPC
                                bp.control.dmode /= dMode
                                bp.control.action /= dMode & newBPC.action
                            with when (self.decoded_addr[CSRA_CONSTS.tdata2]):
                                bp.address /= wdata
  
        if (self.p.use_vm == 0):
            reg_mideleg /= 0
            reg_medeleg /= 0
            reg_scounteren /= 0
  
        if (self.p.use_user_vm == 0):
            reg_mcounteren /= 0
  
        reg_satp.asid /= 0
        if (self.p.csr_num_breakpoints <= 1):
            reg_tselect /= 0
        if (self.p.csr_num_breakpoints >= 1):
            reg_bp[self.p.csr_num_breakpoints-1].control.chain /= 0
        for bpc in map(lambda x: x.control, reg_bp):
            bpc.ttype /= bpc.tType()
            bpc.maskmax /= bpc.maskMax()
            bpc.reserved /= 0
            bpc.zero /= 0
            bpc.h /= 0
            if (self.p.use_vm == 0):
                bpc.s /= 0
            if (self.p.use_user_vm == 0):
                bpc.u /= 0
            if (self.p.use_vm == 0 and self.p.use_user_vm == 0):
                bpc.m /= 1
        for bp in reg_bp[self.p.csr_num_breakpoints:]:
            bp /= 0
  
        for ((t, insn), i) in zip(
            zip(self.io.trace, self.io.inst),
            range(len(self.io.inst))):
            t.exception /= (self.io.retire >= i) & exception
            t.valid /= (self.io.retire > i) | t.exception
            t.insn /= insn
            t.iaddr /= self.io.pc
            t.priv /= cat([reg_debug, reg_mstatus.prv])
            t.cause /= cause
            t.interrupt /= cause[self.p.xlen-1]
            t.tval /= self.io.tval
  
    def chooseInterrupt(self, masksIn):
        nonstandard = list(range(self.supported_interrupts.get_w()-1, 11, -1))
        ## MEI, MSI, MTI, SEI, SSI, STI, UEI, USI, UTI
        standard = [11, 3, 7, 9, 1, 5, 8, 0, 4]
        priority = nonstandard + standard
        masks = list(reversed(masksIn))
        any = reduce(
            lambda a0, a1: a0 | a1,
            flatten(map(
                lambda m: map(
                    lambda i: m[i],
                    filter(lambda x: x < m.get_w(), priority)),
                masks)))
        which = sel_p_lsb(flatten(map(
            lambda m: map(
                lambda i: (m[i], i),
                filter(lambda x: x < m.get_w(), priority)),
            masks)))
        return (any, which)
   
    def readModifyWriteCSR(self, cmd, rdata, wdata):
        return (
            (mux(cmd.match_any([CSR_CONSTS.S(), CSR_CONSTS.C()]), rdata, 0) | wdata) & 
            ~mux(cmd == CSR_CONSTS.C(), wdata, 0))
  
    def legalizePrivilege(self, priv):
        if (self.p.use_vm):
            return mux(priv == PRV_CONSTS.H(), PRV_CONSTS.U(), priv)
        elif (self.p.use_user_vm):
            return (
                value(priv).to_bits()[0] 
                if (isinstance(priv, (int))) else priv[0]).rep(2)
        else:
            return PRV_CONSTS.M()
  
    def trimPrivilege(self, priv):
        if (self.p.use_vm):
            return priv
        else:
            return self.legalizePrivilege(priv)
  
    def writeCounter(self, lo, ctr, wdata):
        if (self.p.xlen == 32):
            hi = lo + CSRA_CONSTS.mcycleh - CSRA_CONSTS.mcycle
            with when (self.decoded_addr[lo]):
                ctr /= cat([ctr[ctr.get_w()-1: 32], wdata])
            with when (self.decoded_addr[hi]):
                ctr /= cat([wdata[ctr.get_w()-33: 0], ctr[31: 0]])
        else:
            with when (self.decoded_addr[lo]):
                ctr /= wdata[ctr.get_w()-1: 0]
        return ctr
    def formEPC(self, x):
        return ~(~x | (1 if (self.p.isa_c) else 3))
    def readEPC(self, x):
        return ~(~x | mux(self.reg_misa[ord('c') - ord('a')], 1, 3))
    def isaStringToMask(self, s):
        return reduce(lambda a, b: a | b, map(lambda x: 1 << (ord(x) - ord('A')), s))
    def formFS(self, fs):
        return fs.r_or().rep(2)
