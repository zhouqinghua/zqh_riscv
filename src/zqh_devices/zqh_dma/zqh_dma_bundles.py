import sys
import os
from phgl_imp import *

class zqh_dma_data_buffer_entry(bundle):
    def set_par(self):
        super(zqh_dma_data_buffer_entry, self).set_par()
        self.p.par('data_width', None)
        self.p.par('size_width', None)
        self.p.par('addr_width', None)

    def set_var(self):
        super(zqh_dma_data_buffer_entry, self).set_var()
        self.var(bits('data', w = self.p.data_width))
        self.var(bits('size', w = self.p.size_width))
        self.var(bits('addr', w = self.p.addr_width))

class zqh_dma_asm_buffer_entry(bundle):
    def set_par(self):
        super(zqh_dma_asm_buffer_entry, self).set_par()
        self.p.par('data_width', None)

    def set_var(self):
        super(zqh_dma_asm_buffer_entry, self).set_var()
        self.var(bits('data', w = self.p.data_width))
        self.var(bits('mask', w = self.p.data_width//8))
