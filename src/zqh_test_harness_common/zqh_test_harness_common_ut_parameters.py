from phgl_imp import *

class zqh_test_harness_common_ut_parameter(unit_test_parameter):
    def set_par(self):
        super(zqh_test_harness_common_ut_parameter, self).set_par()
        self.timeout = 20000000
        self.clock_gen = 0
        self.reset_gen = 0
        self.par('use_jtag', 1)
        self.par('jtag_type', 'sv')
