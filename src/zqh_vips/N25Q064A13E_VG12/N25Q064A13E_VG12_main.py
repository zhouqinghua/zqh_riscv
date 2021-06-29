from phgl_imp import *

class N25Qxxx(module):
    def set_par(self):
        super(N25Qxxx, self).set_par()
        self.pm.vuser  = [
            ('inc' , '../../common/vips/N25Q064A13E_VG12/code/N25Qxxx.v')]
        #tmp self.p.par('tSE', 1, vinst = 1)
        #tmp self.p.par('tBE', 1, vinst = 1)
        #tmp self.p.par('tDE', 1, vinst = 1)
        #tmp self.p.par('tSSE', 1, vinst = 1)
        #tmp self.p.par('t32SSE', 1, vinst = 1)
        #tmp self.p.par('tSE_latency', 1, vinst = 1)
        #tmp self.p.par('tSSE_latency', 1, vinst = 1)

    def set_port(self):
        super(N25Qxxx, self).set_port()
        self.no_crg()

        self.io.var(inp('S'))
        self.io.var(inp('C_'))
        self.io.var(inoutp('HOLD_DQ3'))
        self.io.var(inoutp('DQ0'))
        self.io.var(inoutp('DQ1'))
        self.io.var(inp('Vcc', w = 32))
        self.io.var(inoutp('Vpp_W_DQ2'))
