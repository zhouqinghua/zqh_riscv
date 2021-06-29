import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter

class zqh_core_common_btb_parameter(zqh_core_common_core_parameter):
    def set_par(self):
        super(zqh_core_common_btb_parameter, self).set_par()
        self.par('num_entries', 16)
        self.par('num_match_bits', 14)
        self.par('num_pages', 6)

class zqh_core_common_bht_parameter(zqh_core_common_core_parameter):
    def set_par(self):
        super(zqh_core_common_bht_parameter, self).set_par()
        self.par('num_entries', 256)
        self.par('cnt_len', 1)
        self.par('history_len', 8)
        self.par('history_hash_len', 3)

class zqh_core_common_ras_parameter(zqh_core_common_core_parameter):
    def set_par(self):
        super(zqh_core_common_ras_parameter, self).set_par()
        self.par('num_entries', 8)
