import sys
import os
from phgl_imp import *

class zqh_transfer_size(parameter):
    def set_par(self):
        super(zqh_transfer_size, self).set_par()
        self.par('min', 0)
        self.par('max', 0)

    def post_par(self):
        super(zqh_transfer_size, self).post_par()
        assert(self.min <= self.max)
        assert(self.min >= 0 and self.max >= 0)
        assert(self.max == 0 or is_pow_of_2(self.max))
        assert(self.min == 0 or is_pow_of_2(self.min))
        assert(self.max == 0 or self.min != 0)
