from phgl_imp import *
from .zqh_ddr_phy_parameters import zqh_ddr_phy_parameter

class zqh_ddr_phy_reg_io(csr_reg_io):
    def set_par(self):
        super(zqh_ddr_phy_reg_io, self).set_par()
        self.p.par('addr_bits', 12)
        self.p.par('data_bits', 32)

class zqh_ddr_phy_dfi_control_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dfi_control_io, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_dfi_control_io, self).set_var()
        self.var(inp('address', w = self.p.addr_bits))
        self.var(inp('bank', w = self.p.ba_bits))
        self.var(inp('ras_n'))
        self.var(inp('cas_n'))
        self.var(inp('we_n'))
        self.var(inp('cs_n'))
        self.var(inp('cke'))
        self.var(inp('odt'))
        self.var(inp('reset_n'))

class zqh_ddr_phy_dfi_wrdata_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dfi_wrdata_io, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_dfi_wrdata_io, self).set_var()
        self.var(inp('wrdata_en', self.p.slice_num))
        self.var(inp('wrdata', w = self.p.xn * self.p.slice_num * 2))
        self.var(inp('wrdata_cs'))
        self.var(inp('wrdata_mask', w = (self.p.xn * self.p.slice_num * 2)//8))

class zqh_ddr_phy_dfi_rddata_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dfi_rddata_io, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_dfi_rddata_io, self).set_var()
        self.var(inp('rddata_en', w = self.p.slice_num))
        self.var(outp('rddata', w = self.p.xn * self.p.slice_num * 2))
        self.var(outp('rddata_valid'))

class zqh_ddr_phy_dfi_update_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dfi_update_io, self).set_par()

    def set_var(self):
        super(zqh_ddr_phy_dfi_update_io, self).set_var()
        self.var(inp('ctrlupd_req'))
        self.var(outp('ctrlupd_ack'))
        self.var(outp('phyupd_req'))
        self.var(outp('phyupd_type', w = 2))
        self.var(inp('phyupd_ack'))

class zqh_ddr_phy_dfi_status_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dfi_status_io, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_dfi_status_io, self).set_var()
        self.var(inp('data_byte_disable', w = self.p.slice_num))
        self.var(inp('dram_clk_disable'))
        self.var(inp('init_start'))
        self.var(outp('init_complete'))
        self.var(inp('freq_ratio'))
        self.var(inp('parity_in'))
        self.var(outp('parity_error'))

class zqh_ddr_phy_dfi_training_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dfi_training_io, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_dfi_training_io, self).set_var()
        self.var(outp('rdlvl_resp'))
        self.var(inp('rdlvl_load'))
        self.var(inp('rdlvl_cs_n'))
        self.var(outp('rdlvl_mode'))
        self.var(outp('rdlvl_req'))
        self.var(inp('rdlvl_en'))
        self.var(inp('rdlvl_edge'))
        self.var(vec('rdlvl_delay', gen = inp, n = self.p.slice_num, w = 16))
        self.var(outp('rdlvl_gate_mode'))
        self.var(outp('rdlvl_gate_req'))
        self.var(inp('rdlvl_gate_en'))
        self.var(vec('rdlvl_gate_delay', gen = inp, n = self.p.slice_num, w = 16))

        self.var(outp('wrlvl_mode'))
        self.var(outp('wrlvl_resp'))
        self.var(inp('wrlvl_load'))
        self.var(inp('wrlvl_cs_n'))
        self.var(inp('wrlvl_strobe'))
        self.var(outp('wrlvl_req'))
        self.var(inp('wrlvl_en'))
        self.var(vec('wrlvl_delay', gen = inp, n = self.p.slice_num, w = 16))

class zqh_ddr_phy_dfi_lp_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dfi_lp_io, self).set_par()

    def set_var(self):
        super(zqh_ddr_phy_dfi_lp_io, self).set_var()
        self.var(inp('lp_req'))
        self.var(inp('lp_wakeup'))
        self.var(outp('lp_ack'))

class zqh_ddr_phy_dfi_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dfi_io, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_dfi_io, self).set_var()
        self.var(zqh_ddr_phy_dfi_control_io('control'))
        self.var(zqh_ddr_phy_dfi_wrdata_io('wrdata'))
        self.var(zqh_ddr_phy_dfi_rddata_io('rddata'))
        self.var(zqh_ddr_phy_dfi_update_io('update'))
        self.var(zqh_ddr_phy_dfi_status_io('status'))
        self.var(zqh_ddr_phy_dfi_training_io('training'))
        self.var(zqh_ddr_phy_dfi_lp_io('lp'))
        self.var(inp('dll_rst_n'))

class zqh_ddr_phy_pad_ctrl_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_pad_ctrl_io, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_pad_ctrl_io, self).set_var()
        #data slice signals, each slice need one
        self.var(vec('data_oe', gen = outp, n = self.p.slice_num))
        self.var(vec('data_out', gen = outp, n = self.p.slice_num, w = self.p.xn))
        self.var(vec('ddr_open', gen = outp, n = self.p.slice_num))
        self.var(vec('ddr_open_feedback', gen = inp, n = self.p.slice_num))
        self.var(vec('dm_oe', gen = outp, n = self.p.slice_num))
        self.var(vec('dm_out', gen = outp, n = self.p.slice_num, w = self.p.dm_bits))
        self.var(vec('dqs_oe', gen = outp, n = self.p.slice_num))
        self.var(vec('write_dqs', gen = outp, n = self.p.slice_num, w = self.p.dqs_bits))
        self.var(vec('mem_data', gen = inp, n = self.p.slice_num, w = self.p.xn))
        self.var(vec('mem_dm', gen = inp, n = self.p.slice_num, w = self.p.dm_bits))
        self.var(vec('mem_dqs', gen = inp, n = self.p.slice_num, w = self.p.dqs_bits))
        self.var(vec('tsel_data', gen = outp, n = self.p.slice_num, w = 2))
        self.var(vec('tsel_dm', gen = outp, n = self.p.slice_num, w = 2))
        self.var(vec('tsel_dqs', gen = outp, n = self.p.slice_num, w = 2))

        #share address/control signals
        self.var(outp('mem_address', w = self.p.addr_bits))
        self.var(outp('mem_bank', w = self.p.ba_bits))
        self.var(outp('mem_cas_n'))
        self.var(outp('mem_cke'))
        self.var(outp('mem_clk'))
        self.var(outp('mem_cs_n'))
        self.var(outp('mem_odt'))
        self.var(outp('mem_ras_n'))
        self.var(outp('mem_reset_n'))
        self.var(outp('mem_we_n'))

class zqh_ddr_phy_dram_io(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dram_io, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_dram_io, self).set_var()
        #data slice signals, each slice need one
        self.var(vec(
            'pad_mem_data',
            gen = inout_pin_io,
            n = self.p.slice_num,
            w = self.p.xn))
        self.var(vec(
            'pad_mem_dm',
            gen = inout_pin_io,
            n = self.p.slice_num,
            w = self.p.dm_bits))
        self.var(vec(
            'pad_mem_dqs',
            gen = inout_pin_io,
            n = self.p.slice_num,
            w = self.p.dqs_bits))
        self.var(vec(
            'pad_mem_dqs_n',
            gen = inout_pin_io,
            n = self.p.slice_num,
            w = self.p.dqs_bits))

        #share address/control signals
        self.var(outp('mem_address', w = self.p.addr_bits))
        self.var(outp('mem_bank', w = self.p.ba_bits))
        self.var(outp('mem_cas_n'))
        self.var(outp('mem_cke'))
        self.var(outp('mem_clk'))
        self.var(outp('mem_clk_n'))
        self.var(outp('mem_cs_n'))
        self.var(outp('mem_odt'))
        self.var(outp('mem_ras_n'))
        self.var(outp('mem_reset_n'))
        self.var(outp('mem_we_n'))

class zqh_ddr_phy_dram_pad(bundle):
    def set_par(self):
        super(zqh_ddr_phy_dram_pad, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_var(self):
        super(zqh_ddr_phy_dram_pad, self).set_var()
        #data slice signals, each slice need one
        self.var(vec(
            'pad_mem_data',
            gen = inoutp,
            n = self.p.slice_num,
            w = self.p.xn))
        self.var(vec(
            'pad_mem_dm', 
            gen = inoutp,
            n = self.p.slice_num,
            w = self.p.dm_bits))
        self.var(vec(
            'pad_mem_dqs',
            gen = inoutp,
            n = self.p.slice_num,
            w = self.p.dqs_bits))
        self.var(vec(
            'pad_mem_dqs_n',
            gen = inoutp,
            n = self.p.slice_num, 
            w = self.p.dqs_bits))

        #share address/control signals
        self.var(outp('mem_address', w = self.p.addr_bits))
        self.var(outp('mem_bank', w = self.p.ba_bits))
        self.var(outp('mem_cas_n'))
        self.var(outp('mem_cke'))
        self.var(outp('mem_clk'))
        self.var(outp('mem_clk_n'))
        self.var(outp('mem_cs_n'))
        self.var(outp('mem_odt'))
        self.var(outp('mem_ras_n'))
        self.var(outp('mem_reset_n'))
        self.var(outp('mem_we_n'))
