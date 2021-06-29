import sys
import os
from phgl_imp import *

class JtagDTMConfig(parameter):
    def set_par(self):
        super(JtagDTMConfig, self).set_par()
        self.par('idcodeVersion', 0) ## chosen by manuf.
        self.par('idcodePartNum', 0) ## Chosen by manuf.
        self.par('idcodeManufId', 0) ## Assigned by JEDEC
        ## Note: the actual manufId is passed in through a wire.
        ## Do not forget to wire up io.jtag_mfr_id through your top-level to set the
        ## mfr_id for this core.
        ## If you wish to use this field in the config, you can obtain it along
        ## the lines of p(JtagDTMKey).idcodeManufId.U(11.W).
        self.par('debugIdleCycles', 0)

#zqh TBD case object JtagDTMKey extends Field[JtagDTMConfig](new JtagDTMKeyDefault())

class JtagDTMKeyDefault(JtagDTMConfig):
    def check_par(self):
        super(JtagDTMKeyDefault, self).check_par()
        self.idcodeVersion = 0
        self.idcodePartNum = 0
        self.idcodeManufId = 0
        self.debugIdleCycles = 5 ## Reasonable guess for synchronization.


