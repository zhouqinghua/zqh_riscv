import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_ifu_bundles import zqh_core_common_ifu_cpu_io
from zqh_fpu.zqh_fpu_bundles import zqh_fpu_core_io
from zqh_rocc.zqh_rocc_bundles import zqh_rocc_core_io
from zqh_core_common.zqh_core_common_interrupts_bundles import zqh_core_common_interrupts
from zqh_core_common.zqh_core_common_btb_bundles import zqh_core_common_btb_update
from zqh_core_common.zqh_core_common_btb_bundles import zqh_core_common_bht_update
from zqh_core_common.zqh_core_common_core_bundles import zqh_core_common_core_io

class zqh_core_r1_core_io(zqh_core_common_core_io):
    pass

class zqh_core_r1_scoreboard(bundle):
    def set_par(self):
        super(zqh_core_r1_scoreboard, self).set_par()
        self.p.par('n', None)
        self.p.par('zero', 0)

    def set_var(self):
        super(zqh_core_r1_scoreboard, self).set_var()
        self.var(reg_r('_r', w = self.p.n))

        self.r = (self._r >> 1 << 1) if (self.p.zero) else self._r
        self._next = self.r
        self.ens = 0

    def set(self, en, addr):
        return self.update(en, self._next | self.mask(en, addr))

    def clear(self, en, addr):
        return self.update(en, self._next & ~self.mask(en, addr))

    def read(self, addr):
        return self.r[addr]

    def readBypassed(self, addr):
        return self._next[addr]

    def mask(self, en, addr):
        return mux(en, value(1).to_bits() << addr, 0)

    def update(self, en, update):
        self._next = update
        self.ens = self.ens | en
        with when (self.ens):
            self._r /= self._next 
