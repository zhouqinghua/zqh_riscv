import sys
import os
from phgl_imp import *
from .zqh_rocc_main import zqh_rocc_base_module

class zqh_rocc_stub(zqh_rocc_base_module):

    def main(self):
        super(zqh_rocc_stub, self).main()
        self.io.cmd.ready /= 0
        self.io.resp.valid /= 0
        self.io.resp.bits /= 0
        self.io.mem.req.valid /= 0
        self.io.mem.req.bits /= 0
        self.io.mem.s1_kill /= 0
        self.io.busy /= 0
        self.io.interrupt /= 0
