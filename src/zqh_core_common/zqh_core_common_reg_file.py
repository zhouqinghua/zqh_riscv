from phgl_imp import *

class zqh_core_common_reg_file(bundle):
    def set_par(self):
        super(zqh_core_common_reg_file, self).set_par()
        self.p.par('n', 32)
        self.p.par('w', 32)
        self.p.par('bypass_en', 0)

    def set_var(self):
        super(zqh_core_common_reg_file, self).set_var()
        self.var(vec('rf', gen = lambda _: reg(_, w = self.p.w), n = self.p.n))
        if (self.p.bypass_en):
            self.var(vec('rf_wen', gen = lambda _: bits(_, init = 0), n = self.p.n))
            self.var(bits('rf_wdata', w = self.p.w, init = 0))

    def read(self, addr):
        if (self.p.bypass_en):
            return mux(self.rf_wen[addr], self.rf_wdata, self.rf[addr]) 
        else:
            return self.rf[addr]

    def write(self, en, addr, data):
        wen = en
        with when(wen):
            self.rf(addr, data)
            if (self.p.bypass_en):
                self.rf_wen(addr, 1)

        if (self.p.bypass_en):
            self.rf_wdata /= data
            self.rf_wen[0] /= 0

        #r0 fixed to zero
        self.rf[0] /= 0
