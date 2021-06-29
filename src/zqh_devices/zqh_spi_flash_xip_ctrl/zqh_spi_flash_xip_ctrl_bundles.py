import sys
import os
from phgl_imp import *

class zqh_spi_flash_xip_req(bundle):
    def set_par(self):
        super(zqh_spi_flash_xip_req, self).set_par()

    def set_var(self):
        super(zqh_spi_flash_xip_req, self).set_var()
        self.var(bits('addr', w = 32))
        self.var(bits('size', w = 4))

class zqh_spi_flash_xip_resp(bundle):
    def set_par(self):
        super(zqh_spi_flash_xip_resp, self).set_par()

    def set_var(self):
        super(zqh_spi_flash_xip_resp, self).set_var()
        self.var(bits('data', w = 8))

class zqh_spi_flash_xip_io(bundle):
    def set_par(self):
        super(zqh_spi_flash_xip_io, self).set_par()

    def set_var(self):
        super(zqh_spi_flash_xip_io, self).set_var()
        self.var(ready_valid('req', gen = zqh_spi_flash_xip_req))
        self.var(ready_valid('resp', gen = zqh_spi_flash_xip_resp).flip())
