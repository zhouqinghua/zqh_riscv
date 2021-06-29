from phgl_imp import *

class clk_wiz_0(module):
    def check_par(self):
        super(clk_wiz_0, self).check_par()
        self.pm.vuser  = [
            ('code', '//fpga clk_wiz_0')]

    def set_port(self):
        super(clk_wiz_0, self).set_port()
        self.no_crg()

        self.io.var(inp('reset'))
        self.io.var(inp('clk_in1'))

        self.io.var(outp('clk_ref'))
        self.io.var(outp('clk_eth'))
        self.io.var(outp('clk_ddr'))
        self.io.var(outp('clk_usb_ref'))
        self.io.var(outp('clk_core'))
        self.io.var(outp('locked'))
