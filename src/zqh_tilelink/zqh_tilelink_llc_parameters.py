import sys
import os
from phgl_imp import *
from .zqh_tilelink_parameters import zqh_buffer_parameter
from .zqh_tilelink_arbiter import zqh_tl_arbiter

class zqh_tilelink_llc_parameter(parameter):
    def set_par(self):
        super(zqh_tilelink_llc_parameter, self).set_par()
        self.par('line_bytes', 64)
        self.par('num_trackers', 2)
        self.par('caches', None)
        self.par('cache_coherent', 0)
        self.par('buf_params_in', {
            'a': zqh_buffer_parameter.ready_bypass_p(1),
            'd': zqh_buffer_parameter.none_p(),
            'b': zqh_buffer_parameter.none_p(),
            'c': zqh_buffer_parameter.ready_bypass_p(1),
            'e': zqh_buffer_parameter.ready_bypass_p(1)
            })
        self.par('buf_params_out', {
            'a': zqh_buffer_parameter.none_p(),
            'd': zqh_buffer_parameter.normal_p(2) 
            })
        self.par('policy', zqh_tl_arbiter.roundRobin)
