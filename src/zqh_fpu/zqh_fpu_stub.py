import sys
import os
from phgl_imp import *
from .zqh_fpu_bundles import zqh_fpu_io

class zqh_fpu_stub(module):
    def set_port(self):
        super(zqh_fpu_stub, self).set_port()
        self.io = zqh_fpu_io('io')

    def main(self):
        super(zqh_fpu_stub, self).main()
        self.io.inst.ready /= 1
        self.io.fcsr_flags.valid /= 0
        self.io.fcsr_rdy /= 0
        self.io.nack_mem /= 0
        self.io.illegal_rm /= 0
        self.io.dec /= 0
        self.io.sboard_set /= 0
        self.io.sboard_clr /= 0
        self.io.sboard_clra /= 0
