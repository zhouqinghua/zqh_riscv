import sys
import os
from phgl_imp import *
from zqh_system_common.zqh_system_common_main import zqh_system_common
from zqh_tile_r1.zqh_tile_r1_main import zqh_tile_r1

class zqh_system_r1(zqh_system_common):
    def instance_tile(self):
        return zqh_tile_r1('tile',
            extern_masters = [self.p.mem_master, self.p.mmio_master],
            extern_slaves = [self.p.tile_slave])
