#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/tile/FPU.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_fpu_misc import zqh_fp_constants
from .zqh_fpu_parameters import zqh_fpu_parameter

class zqh_fpu_ctrl_sigs(bundle):
    def set_var(self):
        super(zqh_fpu_ctrl_sigs, self).set_var()
        self.var(bits('ldst'))
        self.var(bits('wen'))
        self.var(bits('ren1'))
        self.var(bits('ren2'))
        self.var(bits('ren3'))
        self.var(bits('swap12'))
        self.var(bits('swap23'))
        self.var(bits('singleIn'))
        self.var(bits('singleOut'))
        self.var(bits('fromint'))
        self.var(bits('toint'))
        self.var(bits('fastpipe'))
        self.var(bits('fma'))
        self.var(bits('div'))
        self.var(bits('sqrt'))
        self.var(bits('wflags'))

class zqh_fpu_lsu_resp(bundle):
    def set_par(self):
        super(zqh_fpu_lsu_resp, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_var(self):
        super(zqh_fpu_lsu_resp, self).set_var()
        self.var(bits('type', w = 3))
        self.var(bits('tag', w = 5))
        self.var(bits('data', w = self.p.flen))

class zqh_fpu_decoder_io(bundle):
    def set_var(self):
        super(zqh_fpu_decoder_io, self).set_var()
        self.var(inp('inst', w = 32))
        self.var(zqh_fpu_ctrl_sigs('sigs').as_output())

class zqh_fpu_core_io(bundle):
    def set_par(self):
        super(zqh_fpu_core_io, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_var(self):
        super(zqh_fpu_core_io, self).set_var()
        self.var(ready_valid('inst', gen = bits, w = 32).flip())
        self.var(inp('fromint_data', w = self.p.xlen))

        self.var(inp('fcsr_rm', w = zqh_fp_constants.RM_SZ))
        self.var(valid('fcsr_flags', gen = bits, w = zqh_fp_constants.FLAGS_SZ))

        self.var(valid('store_data', gen = bits, w = self.p.flen))
        self.var(valid('toint_data', gen = bits, w = self.p.xlen))

        self.var(valid('lsu_resp', gen = zqh_fpu_lsu_resp).as_input())

        self.var(outp('fcsr_rdy'))
        self.var(outp('nack_mem'))
        self.var(outp('illegal_rm'))
        self.var(inp('killx'))
        self.var(inp('killm'))
        self.var(zqh_fpu_ctrl_sigs('dec').as_output())
        self.var(outp('sboard_set'))
        self.var(outp('sboard_clr'))
        self.var(outp('sboard_clra', w = 5))

class zqh_int_to_fp_input(zqh_fpu_ctrl_sigs):
    def set_par(self):
        super(zqh_int_to_fp_input, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_var(self):
        super(zqh_int_to_fp_input, self).set_var()
        self.var(bits('rm', w = zqh_fp_constants.RM_SZ))
        self.var(bits('typ', w = 2))
        self.var(bits('in1', w = self.p.xlen))

class zqh_fp_input(zqh_fpu_ctrl_sigs):
    def set_par(self):
        super(zqh_fp_input, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_var(self):
        super(zqh_fp_input, self).set_var()
        self.var(bits('rm', w = zqh_fp_constants.RM_SZ))
        self.var(bits('fmaCmd', w = 2))
        self.var(bits('typ', w = 2))
        self.var(bits('in1', w = self.p.flen+1))
        self.var(bits('in2', w = self.p.flen+1))
        self.var(bits('in3', w = self.p.flen+1))

class zqh_fp_result(bundle):
    def set_par(self):
        super(zqh_fp_result, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_var(self):
        super(zqh_fp_result, self).set_var()
        self.var(bits('data', w = self.p.flen+1))
        self.var(bits('exc', w = zqh_fp_constants.FLAGS_SZ))

class zqh_fpu_io(zqh_fpu_core_io):
    def set_var(self):
        super(zqh_fpu_io, self).set_var()
        ##cp doesn't pay attn to kill sigs
        self.var(ready_valid('cp_req', gen = lambda _: zqh_fp_input(_)).flip())
        self.var(ready_valid('cp_resp', gen = lambda _: zqh_fp_result(_)))

class zqh_fp_to_int_io_output(bundle):
    def set_par(self):
        super(zqh_fp_to_int_io_output, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_var(self):
        super(zqh_fp_to_int_io_output, self).set_var()
        self.var(zqh_fp_input('input'))
        self.var(bits('lt'))
        self.var(bits('store', w = self.p.flen))
        self.var(bits('toint', w = self.p.xlen))
        self.var(bits('exc', w = zqh_fp_constants.FLAGS_SZ))

class zqh_fp_to_int_io(bundle):
    def set_var(self):
        super(zqh_fp_to_int_io, self).set_var()
        self.var(valid('input', gen = lambda _: zqh_fp_input(_)).flip())
        self.var(valid('output', gen = zqh_fp_to_int_io_output))

class zqh_int_to_fp_io(bundle):
    def set_var(self):
        super(zqh_int_to_fp_io, self).set_var()
        self.var(valid('input', gen = lambda _: zqh_int_to_fp_input(_)).flip())
        self.var(valid('output', gen = lambda _: zqh_fp_result(_)))

class zqh_fp_to_fp_io(bundle):
    def set_var(self):
        super(zqh_fp_to_fp_io, self).set_var()
        self.var(valid('input', gen = lambda _: zqh_fp_input(_)).flip())
        self.var(valid('output', gen = lambda _: zqh_fp_result(_)))
        self.var(inp('lt')) ## from FPToInt

class zqh_mul_add_rec_fn_pipe_io(bundle):
    def set_par(self):
        super(zqh_mul_add_rec_fn_pipe_io, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)

    def set_var(self):
        super(zqh_mul_add_rec_fn_pipe_io, self).set_var()
        self.var(inp('validin'))
        self.var(inp('op', w = 2))
        self.var(inp('a', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('b', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('c', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('roundingMode', w = 3))
        self.var(inp('detectTininess'))
        self.var(outp('output', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(outp('exceptionFlags', w = 5))
        self.var(outp('validout'))

class zqh_fpu_fma_pipe_io(bundle):
    def set_var(self):
        super(zqh_fpu_fma_pipe_io, self).set_var()
        self.var(valid('input', gen = lambda _: zqh_fp_input(_)).flip())
        self.var(valid('output', gen = lambda _: zqh_fp_result(_)))
