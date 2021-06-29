from phgl_imp import *

class dmi_jtag_bfm(module):
    def set_par(self):
        super(dmi_jtag_bfm, self).set_par()
        self.pm.vuser  = [
            ('inc' , '../../common/vips/dmi_jtag_bfm/dmi_jtag_bfm.sv')]

        self.p.par('TICK_DELAY', 0, vinst = 1)

    def set_port(self):
        super(dmi_jtag_bfm, self).set_port()
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
