from phgl_imp import *

class zqh_full_chip_common_parameter(parameter):
    def set_par(self):
        super(zqh_full_chip_common_parameter, self).set_par()
        self.par('imp_mode','sim')#sim/fpga/asic
