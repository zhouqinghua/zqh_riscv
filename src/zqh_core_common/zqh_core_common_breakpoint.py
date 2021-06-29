import sys
import os
from phgl_imp import *
from .zqh_core_common_csr_bundles import zqh_core_common_csr_mstatus
from .zqh_core_common_csr_bundles import zqh_core_common_csr_bp
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter

class zqh_core_common_break_point_unit(module):
    def set_par(self):
        super(zqh_core_common_break_point_unit, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_port(self):
        super(zqh_core_common_break_point_unit, self).set_port()
        self.io.var(zqh_core_common_csr_mstatus('status').as_input())
        self.io.var(vec(
            'bp',
            gen = zqh_core_common_csr_bp,
            n = self.p.csr_num_breakpoints).as_input())
        self.io.var(inp('pc', w = self.p.vaddr_bits))
        self.io.var(inp('ea', w = self.p.vaddr_bits))
        self.io.var(outp('xcpt_if'))
        self.io.var(outp('xcpt_ld'))
        self.io.var(outp('xcpt_st'))
        self.io.var(outp('debug_if'))
        self.io.var(outp('debug_ld'))
        self.io.var(outp('debug_st'))

    def main(self):
        self.io.xcpt_if /= 0
        self.io.xcpt_ld /= 0
        self.io.xcpt_st /= 0
        self.io.debug_if /= 0
        self.io.debug_ld /= 0
        self.io.debug_st /= 0

        def func0(a, bp):
            (ri, wi, xi) = a
            en = bp.control.enabled(self.io.status)
            r = en & ri & bp.control.r & bp.addressMatch(self.io.ea)
            w = en & wi & bp.control.w & bp.addressMatch(self.io.ea)
            x = en & xi & bp.control.x & bp.addressMatch(self.io.pc)
            end = ~bp.control.chain

            with when (end & r):
                self.io.xcpt_ld /= ~bp.control.action
                self.io.debug_ld /= bp.control.action 
            with when (end & w):
                self.io.xcpt_st /= ~bp.control.action
                self.io.debug_st /= bp.control.action 
            with when (end & x):
                self.io.xcpt_if /= ~bp.control.action
                self.io.debug_if /= bp.control.action 
            return (end | r, end | w, end | x)
        reduce(func0, self.io.bp, (1,1,1))
