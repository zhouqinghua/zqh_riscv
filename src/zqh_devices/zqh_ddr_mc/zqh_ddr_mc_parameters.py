from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

class zqh_ddr_mc_parameter(zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_ddr_mc_parameter, self).set_par()
        self.par('sync_delay', 3)
        self.par('addr_bits', 32)
        self.par('data_bits', 64)
        self.par('token_bits', 1)
        self.par('size_bits', 1)
        self.par('req_async_fifo_depth', 8)
        self.par('resp_async_fifo_depth', 8)
        self.par('cmd_buffer_entries', 4)#max memory requeset outstanding number
        self.par('req_data_buffer_entries', 32)#max write memory requeset's data space
        self.par('resp_data_buffer_entries', 32)#max read memory requeset's data space
        self.par('pipe_wr_info_fifo_depth', 8)
        self.par('pipe_rd_info_fifo_depth', 8)

        self.par('max_req_size', 8) #max 256 bytes, TBD

        self.par('cfg_reg_num', 147)

        self.par('bstlen_max', 3)
        self.par('dfi_bl_max', (1 << self.bstlen_max) >> 1)
        self.par('tdfi_phy_rdlat_max', 64)

        self.par('ddr_CL_MIN', 5)
        self.par('ddr_CL_MAX', 20)
        self.par('ddr_AL_MAX', 2)
        self.par('ddr_BL_MAX', 8)
        self.par('ddr_BL_MIN', 4)
        self.par('ddr_WR_MIN', 5)
        self.par('ddr_WR_MAX', 16)
        self.par('ddr_CWL_MIN', 5)
        self.par('ddr_CWL_MAX', 10)

    def check_par(self):
        super(zqh_ddr_mc_parameter, self).check_par()

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_cfg_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name, int_source_bits = 1)

    def gen_mem_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name)
