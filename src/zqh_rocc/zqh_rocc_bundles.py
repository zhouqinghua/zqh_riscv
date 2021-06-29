import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_core_parameters import zqh_core_common_core_parameter
from zqh_core_common.zqh_core_common_csr_bundles import zqh_core_common_csr_mstatus
from zqh_core_common.zqh_core_common_lsu_bundles import zqh_core_common_lsu_mem_io

class zqh_rocc_instruction(bundle):
    def set_var(self):
        super(zqh_rocc_instruction, self).set_var()
        self.var(bits('funct', w = 7))
        self.var(bits('rs2', w = 5))
        self.var(bits('rs1', w = 5))
        self.var(bits('xd'))
        self.var(bits('xs1'))
        self.var(bits('xs2'))
        self.var(bits('rd', w = 5))
        self.var(bits('opcode', w = 7))

class zqh_rocc_command(bundle):
    def set_par(self):
        super(zqh_rocc_command, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_rocc_command, self).set_var()
        self.var(zqh_rocc_instruction('inst'))
        self.var(bits('rs1', w = self.p.xlen))
        self.var(bits('rs2', w = self.p.xlen))
        self.var(zqh_core_common_csr_mstatus('status'))

class zqh_rocc_response(bundle):
    def set_par(self):
        super(zqh_rocc_response, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_rocc_response, self).set_var()
        self.var(bits('rd', w = 5))
        self.var(bits('data', w = self.p.xlen))

class zqh_rocc_core_io(bundle):
    def set_par(self):
        super(zqh_rocc_core_io, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_var(self):
        super(zqh_rocc_core_io, self).set_var()
        self.var(ready_valid('cmd', gen = zqh_rocc_command).flip())
        self.var(ready_valid('resp', gen = zqh_rocc_response))
        self.var(zqh_core_common_lsu_mem_io('mem').flip())
        self.var(outp('busy'))
        self.var(outp('interrupt'))
        self.var(inp('exception'))
