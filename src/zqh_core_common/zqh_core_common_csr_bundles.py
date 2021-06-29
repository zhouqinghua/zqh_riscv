####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/CSR.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_core_common_misc import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter
from zqh_fpu.zqh_fpu_misc import zqh_fp_constants
from .zqh_core_common_interrupts_bundles import zqh_core_common_interrupts

class zqh_core_common_csr_mstatus(bundle):
    def set_var(self):
        ## not truly part of mstatus, but convenient
        self.var(bits('debug'))
        self.var(bits('isa', w = 32))
        self.var(bits('rv64'))

        self.var(bits('dprv', w = PRV_CONSTS.SZ)) ## effective privilege for data accesses
        self.var(bits('prv', w = PRV_CONSTS.SZ)) ## not truly part of mstatus, but convenient
        self.var(bits('sd'))
        self.var(bits('zero2', w = 27))
        self.var(bits('sxl', w = 2))
        self.var(bits('uxl', w = 2))
        self.var(bits('sd_rv32'))
        self.var(bits('zero1', w = 8))
        self.var(bits('tsr'))
        self.var(bits('tw'))
        self.var(bits('tvm'))
        self.var(bits('mxr'))
        self.var(bits('sum'))
        self.var(bits('mprv'))
        self.var(bits('xs', w = 2))
        self.var(bits('fs', w = 2))
        self.var(bits('mpp', w = 2))
        self.var(bits('hpp', w = 2))
        self.var(bits('spp'))
        self.var(bits('mpie'))
        self.var(bits('hpie'))
        self.var(bits('spie'))
        self.var(bits('upie'))
        self.var(bits('mie'))
        self.var(bits('hie'))
        self.var(bits('sie'))
        self.var(bits('uie'))

class zqh_core_common_csr_dcsr(bundle):
    def set_var(self):
        super(zqh_core_common_csr_dcsr, self).set_var()
        self.var(bits('xdebugver', w = 2))
        self.var(bits('zero4', w = 2))
        self.var(bits('zero3', w = 12))
        self.var(bits('ebreakm'))
        self.var(bits('ebreakh'))
        self.var(bits('ebreaks'))
        self.var(bits('ebreaku'))
        self.var(bits('zero2'))
        self.var(bits('stopcycle'))
        self.var(bits('stoptime'))
        self.var(bits('cause', w = 3))
        self.var(bits('zero1', w = 3))
        self.var(bits('step'))
        self.var(bits('prv', w = PRV_CONSTS.SZ))

class zqh_core_common_csr_mip(bundle):
    def set_par(self):
        super(zqh_core_common_csr_mip, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_csr_mip, self).set_var()
        self.var(vec('lip', gen = bits, n = self.p.csr_num_local_interrupts))
        self.var(bits('zero2'))
        self.var(bits('debug')) ## keep in sync with CSR.debugIntCause
        self.var(bits('zero1'))
        self.var(bits('rocc'))
        self.var(bits('meip'))
        self.var(bits('heip'))
        self.var(bits('seip'))
        self.var(bits('ueip'))
        self.var(bits('mtip'))
        self.var(bits('htip'))
        self.var(bits('stip'))
        self.var(bits('utip'))
        self.var(bits('msip'))
        self.var(bits('hsip'))
        self.var(bits('ssip'))
        self.var(bits('usip'))

class zqh_core_common_csr_satp(bundle):
    def set_par(self):
        super(zqh_core_common_csr_satp, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def pgLevelsToMode(self, i):
        if ((self.p.xlen == 32) and (i == 2)):
            return 1
        elif (self.p.xlen == 64):
            if ((i >= 3) and (i <= 6)):
                return i + 5

    def set_var(self):
        super(zqh_core_common_csr_satp, self).set_var()
        if (self.p.xlen == 32):
            modeBits = 1
            maxASIdBits = 9
        elif (self.p.xlen == 64):
            modeBits = 4
            maxASIdBits = 16
        #min 4KB page
        assert(modeBits + maxASIdBits + (self.p.max_paddr_bits - 12) == self.p.xlen)
        self.var(bits('mode', w = modeBits))
        self.var(bits('asid', w = maxASIdBits))
        self.var(bits('ppn', w = self.p.max_paddr_bits - 12))#min 4KB page

class zqh_core_common_csr_traced_instruction(bundle):
    def set_par(self):
        super(zqh_core_common_csr_traced_instruction, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_csr_traced_instruction, self).set_var()
        self.var(bits('valid'))
        self.var(bits('iaddr', w = self.p.max_addr_bits))
        self.var(bits('insn', w = self.p.inst_bits))
        self.var(bits('priv', w = 3))
        self.var(bits('exception'))
        self.var(bits('interrupt'))
        self.var(bits('cause', w = log2_ceil(1 + CSR_CONSTS.busErrorIntCause())))
        self.var(bits('tval', w = max(self.p.max_addr_bits, self.p.inst_bits)))

class zqh_core_common_csr_bp_control(bundle):
    def set_par(self):
        super(zqh_core_common_csr_bp_control, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_csr_bp_control, self).set_var()
        self.var(bits('ttype', w = 4))
        self.var(bits('dmode'))
        self.var(bits('maskmax', w = 6))
        self.var(bits('reserved', w = self.p.xlen-24))
        self.var(bits('action'))
        self.var(bits('chain'))
        self.var(bits('zero', w = 2))
        self.var(bits('tmatch', w = 2))
        self.var(bits('m'))
        self.var(bits('h'))
        self.var(bits('s'))
        self.var(bits('u'))
        self.var(bits('x'))
        self.var(bits('w'))
        self.var(bits('r'))

    def tType(self):
        return 2
    def maskMax(self):
        return 4
    def enabled(self, mstatus):
        return ~mstatus.debug & cat([self.m, self.h, self.s, self.u])[mstatus.prv]

class zqh_core_common_csr_bp(bundle):
    def set_par(self):
        super(zqh_core_common_csr_bp, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_csr_bp, self).set_var()
        self.var(zqh_core_common_csr_bp_control('control'))
        self.var(bits('address', w = self.p.vaddr_bits))

    def mask(self, dummy = 0):
        tmp = []
        res = self.control.tmatch[0]
        tmp.append(res)
        for i in range(self.control.maskMax()-1):
            res = res & self.address[i]
            tmp.append(res)
        return cat_rvs(tmp)


    def pow2AddressMatch(self, x):
        return (~x | self.mask()) == (~self.address | self.mask())

    def rangeAddressMatch(self, x):
        return (x >= self.address) ^ self.control.tmatch[0]

    def addressMatch(self, x):
        return mux(
            self.control.tmatch[1],
            self.rangeAddressMatch(x),
            self.pow2AddressMatch(x))

class zqh_core_common_csr_perf_counter_io(bundle):
    def set_par(self):
        super(zqh_core_common_csr_perf_counter_io, self).set_par()
        self.p = zqh_core_common_core_parameter()
        self.var(outp('event_sel', w = self.p.xlen))
        self.var(inp('inc', w = 1))

class zqh_core_common_csr_rw_io(bundle):
    def set_par(self):
        super(zqh_core_common_csr_rw_io, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_csr_rw_io, self).set_var()
        self.var(inp('addr', w =  CSR_CONSTS.SZ_ADDR))
        self.var(inp('cmd', w = CSR_CONSTS.SZ))
        self.var(outp('rdata', w = self.p.xlen))
        self.var(inp('wdata',  w = self.p.xlen))

class zqh_core_common_csr_decode_io(bundle):
    def set_var(self):
        super(zqh_core_common_csr_decode_io, self).set_var()
        self.var(inp('csr', w = CSR_CONSTS.SZ_ADDR))
        self.var(outp('fp_illegal'))
        self.var(outp('fp_csr'))
        self.var(outp('rocc_illegal'))
        self.var(outp('read_illegal'))
        self.var(outp('write_illegal'))
        self.var(outp('write_flush'))
        self.var(outp('system_illegal'))

class zqh_core_common_csr_file_io(bundle):
    def set_par(self):
        super(zqh_core_common_csr_file_io, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_core_common_csr_file_io, self).set_var()
        self.var(zqh_core_common_interrupts('interrupts').as_input())
        self.var(inp('hartid', w = self.p.hartid_len))
        self.var(zqh_core_common_csr_rw_io('rw'))
        
        self.var(vec('decode', gen = zqh_core_common_csr_decode_io, n = 1))

        self.var(outp('csr_stall'))
        self.var(outp('eret'))
        self.var(outp('singleStep'))

        self.var(zqh_core_common_csr_mstatus('status').as_output())
        self.var(outp('evec', w = self.p.vaddr_bits))
        self.var(inp('exception'))
        self.var(inp('retire', w = 1))
        self.var(inp('cause', w = self.p.xlen))
        self.var(inp('pc', w = self.p.vaddr_bits))
        self.var(inp('tval', w = self.p.vaddr_bits))
        self.var(outp('time', w = self.p.xlen))
        self.var(outp('fcsr_rm', w = zqh_fp_constants.RM_SZ))
        self.var(valid('fcsr_flags', gen = bits, w = zqh_fp_constants.FLAGS_SZ).flip())
        self.var(inp('rocc_interrupt'))
        self.var(outp('interrupt'))
        self.var(outp('interrupt_cause', w = self.p.xlen))
        self.var(vec(
            'bp',
            gen = zqh_core_common_csr_bp,
            n = self.p.csr_num_breakpoints).as_output())
        self.var(vec(
            'counters',
            gen = zqh_core_common_csr_perf_counter_io,
            n = self.p.csr_num_perf_counters))
        self.var(vec(
            'inst',
            gen = inp,
            n = 1, w = self.p.inst_bits))
        self.var(vec(
            'trace',
            gen = zqh_core_common_csr_traced_instruction,
            n = 1).as_output())
