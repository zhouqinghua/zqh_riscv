####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/Multiplier.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_core_common_misc import *

class zqh_core_common_multiplier_req(bundle):
    def set_par(self):
        super(zqh_core_common_multiplier_req, self).set_par()
        self.p.par('data_bits', 0)
        self.p.par('tag_bits', 0)

    def set_var(self):
        super(zqh_core_common_multiplier_req, self).set_var()
        self.var(bits('fn', w = A_CONSTS.SZ))
        self.var(bits('dw', w = D_CONSTS.SZ_DW))
        self.var(bits('in1', w = self.p.data_bits))
        self.var(bits('in2', w = self.p.data_bits))
        self.var(bits('tag', w = self.p.tag_bits))

class zqh_core_common_multiplier_resp(bundle):
    def set_par(self):
        super(zqh_core_common_multiplier_resp, self).set_par()
        self.p.par('data_bits', 0)
        self.p.par('tag_bits', 0)

    def set_var(self):
        self.var(bits('data', w = self.p.data_bits))
        self.var(bits('tag', w = self.p.tag_bits))

class zqh_core_common_multiplier_io(bundle):
    def set_par(self):
        super(zqh_core_common_multiplier_io, self).set_par()
        self.p.par('data_bits', 0)
        self.p.par('tag_bits', 0)

    def set_var(self):
        super(zqh_core_common_multiplier_io, self).set_var()
        self.var(ready_valid(
            'req',
            gen = zqh_core_common_multiplier_req, 
            data_bits = self.p.data_bits,
            tag_bits = self.p.tag_bits).flip())
        self.var(inp('kill'))
        self.var(ready_valid(
            'resp', 
            gen = zqh_core_common_multiplier_resp,
            data_bits = self.p.data_bits,
            tag_bits = self.p.tag_bits))
