from phgl_imp import *

class SimJTAG(module):
    def set_par(self):
        super(SimJTAG, self).set_par()
        self.pm.vuser  = [
            ('inc' , '../../common/resources/vsrc/SimJTAG.v')]

        self.p.par('TICK_DELAY', 0, vinst = 1)

    def set_port(self):
        super(SimJTAG, self).set_port()
        self.no_crg()

        self.io.var(inp('clock')),
        self.io.var(inp('reset')),
        
        self.io.var(inp('enable')),
        self.io.var(inp('init_done')),

        self.io.var(outp('jtag_TCK')),
        self.io.var(outp('jtag_TMS')),
        self.io.var(outp('jtag_TDI')),
        self.io.var(outp('jtag_TRSTn')),

        self.io.var(inp('jtag_TDO_data')),
        self.io.var(inp('jtag_TDO_driven')),
               
        self.io.var(outp('exit', w = 32))
