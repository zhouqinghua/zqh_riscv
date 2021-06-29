import sys
import os
from phgl_imp import *

class zqh_tilelink_node_module_parameter(parameter):
    def set_par(self):
        super(zqh_tilelink_node_module_parameter, self).set_par()
        self.par('extern_masters', [])
        self.par('extern_slaves', [])
        self.par('is_int_sink', 0)
