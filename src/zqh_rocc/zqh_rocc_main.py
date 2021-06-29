import sys
import os
from phgl_imp import *
from .zqh_rocc_bundles import *

class zqh_rocc_base_module(module):
    def set_par(self):
        super(zqh_rocc_base_module, self).set_par()

    def set_port(self):
        super(zqh_rocc_base_module, self).set_port()
        self.io = zqh_rocc_core_io('io');
