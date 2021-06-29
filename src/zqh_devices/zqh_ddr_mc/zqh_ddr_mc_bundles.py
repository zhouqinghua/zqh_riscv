from phgl_imp import *

class zqh_ddr_mc_ctrl_reg_0(bundle):
    def set_par(self):
        super(zqh_ddr_mc_ctrl_reg_0, self).set_par()

    def set_var(self):
        super(zqh_ddr_mc_ctrl_reg_0, self).set_var()
        self.var(reg_r('dram_class', w = 4))
        self.var(bits('reserved', w = 7, init = 0))
        self.var(reg_r('start'))

class zqh_ddr_mc_ctrl_reg_19(bundle):
    def set_par(self):
        super(zqh_ddr_mc_ctrl_reg_19, self).set_par()

    def set_var(self):
        super(zqh_ddr_mc_ctrl_reg_19, self).set_var()
        self.var(reg_rs('bstlen', w = 4, rs = 2))
        self.var(bits('reserved', w = 16, init = 0))

class zqh_ddr_mc_ctrl_reg_132(bundle):
    def set_par(self):
        super(zqh_ddr_mc_ctrl_reg_132, self).set_par()

    def set_var(self):
        super(zqh_ddr_mc_ctrl_reg_132, self).set_var()
        self.var(reg_r('int_status', w = 9))

class zqh_ddr_mc_ctrl_reg_136(bundle):
    def set_par(self):
        super(zqh_ddr_mc_ctrl_reg_136, self).set_par()

    def set_var(self):
        super(zqh_ddr_mc_ctrl_reg_136, self).set_var()
        self.var(reg_s('int_mask', w = 9))

class zqh_ddr_mc_mem_req(bundle):
    def set_par(self):
        super(zqh_ddr_mc_mem_req, self).set_par()
        self.p.par('addr_bits', 32)
        self.p.par('data_bits', 64)
        self.p.par('size_bits', 1)
        self.p.par('token_bits', 1)

    def set_var(self):
        super(zqh_ddr_mc_mem_req, self).set_var()
        self.var(bits('write'))
        self.var(bits('last'))
        self.var(bits('sop'))
        self.var(bits('eop'))
        self.var(bits('size', w = self.p.size_bits))
        self.var(bits('token', w = self.p.token_bits))
        self.var(bits('addr', w = self.p.addr_bits))
        self.var(bits('data', w = self.p.data_bits))
        #tmp self.var(bits('be', w = self.p.data_bits//8))

class zqh_ddr_mc_mem_req_info(bundle):
    def set_par(self):
        super(zqh_ddr_mc_mem_req_info, self).set_par()
        self.p.par('addr_bits', 32)
        self.p.par('size_bits', 1)
        self.p.par('token_bits', 1)

    def set_var(self):
        super(zqh_ddr_mc_mem_req_info, self).set_var()
        self.var(bits('write'))
        self.var(bits('last'))
        self.var(bits('sop'))
        self.var(bits('eop'))
        self.var(bits('size', w = self.p.size_bits))
        self.var(bits('token', w = self.p.token_bits))
        self.var(bits('addr', w = self.p.addr_bits))
        #tmp self.var(bits('be', w = self.p.data_bits//8))

class zqh_ddr_mc_mem_req_data_ll(bundle):
    def set_par(self):
        super(zqh_ddr_mc_mem_req_data_ll, self).set_par()
        self.p.par('data_bits', 64)
        self.p.par('bank_bits', 3)

    def set_var(self):
        super(zqh_ddr_mc_mem_req_data_ll, self).set_var()
        self.var(bits('data', w = self.p.data_bits))
        self.var(bits('bank', w = self.p.bank_bits))

class zqh_ddr_mc_mem_resp(bundle):
    def set_par(self):
        super(zqh_ddr_mc_mem_resp, self).set_par()
        self.p.par('data_bits', 64)
        self.p.par('size_bits', 1)
        self.p.par('token_bits', 1)
        self.p.par('bank_bits', 3)

    def set_var(self):
        super(zqh_ddr_mc_mem_resp, self).set_var()
        self.var(bits('write'))
        self.var(bits('last'))
        self.var(bits('bank', w = self.p.bank_bits))
        self.var(bits('size', w = self.p.size_bits))
        self.var(bits('token', w = self.p.token_bits))
        self.var(bits('data', w = self.p.data_bits))
        self.var(bits('error'))

class zqh_ddr_mc_mem_io(bundle):
    def set_par(self):
        super(zqh_ddr_mc_mem_io, self).set_par()
        self.p.par('addr_bits', 32)
        self.p.par('data_bits', 64)
        self.p.par('size_bits', 1)
        self.p.par('token_bits', 1)

    def set_var(self):
        super(zqh_ddr_mc_mem_io, self).set_var()
        self.var(ready_valid(
            'req',
            gen = zqh_ddr_mc_mem_req, 
            addr_bits = self.p.addr_bits,
            data_bits = self.p.data_bits,
            size_bits = self.p.size_bits,
            token_bits = self.p.token_bits).flip())
        self.var(ready_valid(
            'resp',
            gen = zqh_ddr_mc_mem_resp, 
            data_bits = self.p.data_bits,
            size_bits = self.p.size_bits,
            token_bits = self.p.token_bits))

class zqh_ddr_mc_ddr_dfi_cmd(zqh_ddr_mc_mem_req_info):
    def set_par(self):
        super(zqh_ddr_mc_ddr_dfi_cmd, self).set_par()

    def set_var(self):
        super(zqh_ddr_mc_ddr_dfi_cmd, self).set_var()
        self.var(bits('cmd', w = 4))
