from phgl_imp import *

class M24LC08BH(module):
    def set_par(self):
        super(M24LC08BH, self).set_par()
        self.pm.vuser  = [
            ('inc' , '../../common/vips/24xx08H_Verilog_Model/24LC08BH.v')]

    def set_port(self):
        super(M24LC08BH, self).set_port()
        self.no_crg()

        self.io.var(inp('A0'))
        self.io.var(inp('A1'))
        self.io.var(inp('A2'))
        self.io.var(inp('WP'))
        self.io.var(inoutp('SDA'))
        self.io.var(inp('SCL'))
        self.io.var(inp('RESET'))
