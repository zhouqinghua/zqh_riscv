from phgl_imp import *
from .zqh_ddr_phy_bundles import *
from .zqh_ddr_phy_parameters import *

class zqh_ddr_phy_pad_ctrl(module):
    def set_par(self):
        super(zqh_ddr_phy_pad_ctrl, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_port(self):
        super(zqh_ddr_phy_pad_ctrl, self).set_port()
        self.io.var(zqh_ddr_phy_pad_ctrl_io(
            'port_ctrl', 
            slice_num = self.p.slice_num).flip())
        self.io.var(zqh_ddr_phy_dram_io(
            'port_dram',
            slice_num = self.p.slice_num))

    def main(self):
        super(zqh_ddr_phy_pad_ctrl, self).main()

        ####
        #address/control signals
        self.io.port_dram.mem_address /= self.io.port_ctrl.mem_address
        self.io.port_dram.mem_bank    /= self.io.port_ctrl.mem_bank
        self.io.port_dram.mem_cas_n   /= self.io.port_ctrl.mem_cas_n
        self.io.port_dram.mem_cke     /= self.io.port_ctrl.mem_cke
        self.io.port_dram.mem_clk     /= self.io.port_ctrl.mem_clk
        self.io.port_dram.mem_clk_n   /= ~self.io.port_ctrl.mem_clk
        self.io.port_dram.mem_cs_n    /= self.io.port_ctrl.mem_cs_n
        self.io.port_dram.mem_odt     /= self.io.port_ctrl.mem_odt
        self.io.port_dram.mem_ras_n   /= self.io.port_ctrl.mem_ras_n
        self.io.port_dram.mem_reset_n /= self.io.port_ctrl.mem_reset_n
        self.io.port_dram.mem_we_n    /= self.io.port_ctrl.mem_we_n

        ####
        #data slice signals
        for i in range(self.p.slice_num):
            self.io.port_dram.pad_mem_data[i].output  /= self.io.port_ctrl.data_out[i]
            self.io.port_dram.pad_mem_dm[i].output    /= self.io.port_ctrl.dm_out[i]
            self.io.port_dram.pad_mem_dqs[i].output   /= self.io.port_ctrl.write_dqs[i]
            self.io.port_dram.pad_mem_dqs_n[i].output /= ~self.io.port_ctrl.write_dqs[i]

            self.io.port_dram.pad_mem_data[i].oe  /= self.io.port_ctrl.data_oe[i]
            self.io.port_dram.pad_mem_dm[i].oe    /= self.io.port_ctrl.dm_oe[i]
            self.io.port_dram.pad_mem_dqs[i].oe   /= self.io.port_ctrl.dqs_oe[i]
            self.io.port_dram.pad_mem_dqs_n[i].oe /= self.io.port_ctrl.dqs_oe[i]

            self.io.port_ctrl.mem_data[i] /= self.io.port_dram.pad_mem_data[i].input
            self.io.port_ctrl.mem_dm[i]   /= self.io.port_dram.pad_mem_dm[i].input
            self.io.port_ctrl.mem_dqs[i]  /= self.io.port_dram.pad_mem_dqs[i].input
