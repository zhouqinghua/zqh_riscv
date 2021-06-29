import sys
import os
from phgl_imp import *

class zqh_uart_io(bundle):
    def set_var(self):
        super(zqh_uart_io, self).set_var()
        self.var(outp('tx'))
        self.var(inp('rx'))

class zqh_uart_pad(bundle):
    def set_var(self):
        super(zqh_uart_pad, self).set_var()
        self.var(outp('tx'))
        self.var(inp('rx'))
