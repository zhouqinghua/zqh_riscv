import sys
import os
from phgl_imp import *
from zqh_tile_common.zqh_tile_common_main import zqh_tile_common
from zqh_core_e1.zqh_core_e1_wrapper_main import zqh_core_e1_wrapper

class zqh_tile_e1(zqh_tile_common):
    def instance_core_wraps(self):
        return list(map(lambda _: zqh_core_e1_wrapper('core_wrap_'+str(_),
            static = 1,
            extern_masters = [self.p.core_master[_]],
            extern_slaves = [self.p.core_slave[_]]), range(self.p.num_cores)))
