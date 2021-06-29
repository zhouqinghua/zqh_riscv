import sys
import os
from phgl_imp import *
from .zqh_core_r1_core_main import zqh_core_r1_core
from zqh_fpu.zqh_fpu_main import zqh_fpu
from .zqh_core_r1_lsu_main import zqh_core_r1_lsu
from zqh_core_common.zqh_core_common_wrapper_main import zqh_core_common_wrapper

class zqh_core_r1_wrapper(zqh_core_common_wrapper):
    def instance_core(self):
        return zqh_core_r1_core('core')

    def instance_lsu(self):
        return zqh_core_r1_lsu('lsu',
            extern_masters = [self.p.lsu_master],
            extern_slaves = [self.p.lsu_slave])
    
    def instance_fpu(self):
        return zqh_fpu('fpu')
