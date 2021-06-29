import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_atomic_transform_parameters import zqh_tilelink_atomic_transform_parameter

class zqh_tilelink_2_axi4_parameter(parameter):
    def set_par(self):
        super(zqh_tilelink_2_axi4_parameter, self).set_par()
        self.par('aw_id_max_num', 1)
        self.par('ar_id_max_num', 1)
        self.par('atomic_en', 0)
        self.par('atomic', zqh_tilelink_atomic_transform_parameter())
