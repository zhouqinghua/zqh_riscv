import sys
import os
from phgl_imp import *

class zqh_axi4_2_tilelink_parameter(parameter):
    def set_par(self):
        super(zqh_axi4_2_tilelink_parameter, self).set_par()
        self.par('tl_source_id_num', 16)
        self.par('axi4_aw_q_depth', 4)
        self.par('axi4_w_q_depth', 8)
        self.par('axi4_ar_q_depth', 4)
