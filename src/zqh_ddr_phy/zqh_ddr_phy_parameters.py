from phgl_imp import *

class zqh_ddr_phy_parameter(parameter):
    def set_par(self):
        super(zqh_ddr_phy_parameter, self).set_par()
        self.par('imp_mode', 'sim')
        self.par('slice_num', 2)
        #self.par('speed_bin', 'sg125')
        self.par('speed_bin', 'sg25')
        self.par('size', 'den4096Mb')
        self.par('xn', 16)

        self.par('t_ctrl_delay', 2)
        self.par('t_wr_dqs_delay', 3)
        self.par('t_wr_dq_delay', 2)
        self.par('t_rd_dqs_delay', 3)
        self.par('t_rd_dq_delay', 1)
        self.par('t_phy_rdlat', 5)

    def check_par(self):
        super(zqh_ddr_phy_parameter, self).check_par()
        self.par('cs_bits',1)
        self.par('ba_bits',3)
        if (self.size == 'den1024Mb'):
            if (self.xn == 4):
                self.par('dm_bits'  ,       1)
                self.par('addr_bits',      14)
                self.par('row_bits' ,      14)
                self.par('col_bits' ,      11)
                self.par('dq_bits'  ,       4)
                self.par('dqs_bits' ,       1)
            elif (self.xn == 8):
                self.par('dm_bits'   ,       1)
                self.par('addr_bits' ,      14)
                self.par('row_bits'  ,      14)
                self.par('col_bits'  ,      10)
                self.par('dq_bits'   ,       8)
                self.par('dqs_bits'  ,       1)
            elif (self.xn == 16):
                self.par('dm_bits'   ,       2)
                self.par('addr_bits' ,      13)
                self.par('row_bits'  ,      13)
                self.par('col_bits'  ,      10)
                self.par('dq_bits'   ,      16)
                self.par('dqs_bits'  ,       2)
            else:
                assert(0)
        elif (self.size == 'den2048Mb'):
            if (self.xn == 4):
                self.par('dm_bits'   ,       1)
                self.par('addr_bits' ,      15)
                self.par('row_bits'  ,      15)
                self.par('col_bits'  ,      11)
                self.par('dq_bits'   ,       4)
                self.par('dqs_bits'  ,       1)
            elif (self.xn == 8):
                self.par('dm_bits'   ,       1)
                self.par('addr_bits' ,      15)
                self.par('row_bits'  ,      15)
                self.par('col_bits'  ,      10)
                self.par('dq_bits'   ,       8)
                self.par('dqs_bits'  ,       1)
            elif (self.xn == 16):
                self.par('dm_bits'   ,       2)
                self.par('addr_bits' ,      14)
                self.par('row_bits'  ,      14)
                self.par('col_bits'  ,      10)
                self.par('dq_bits'   ,      16)
                self.par('dqs_bits'  ,       2)
            else:
                assert(0)
        elif (self.size == 'den4096Mb'):
            if (self.xn == 4):
                self.par('dm_bits'   ,       1)
                self.par('addr_bits' ,      16)
                self.par('row_bits'  ,      16)
                self.par('col_bits'  ,      11)
                self.par('dq_bits'   ,       4)
                self.par('dqs_bits'  ,       1)
            elif (self.xn == 8):
                self.par('dm_bits'   ,       1)
                self.par('addr_bits' ,      16)
                self.par('row_bits'  ,      16)
                self.par('col_bits'  ,      10)
                self.par('dq_bits'   ,       8)
                self.par('dqs_bits'  ,       1)
            elif (self.xn == 16):
                self.par('dm_bits'   ,       2)
                self.par('addr_bits' ,      15)
                self.par('row_bits'  ,      15)
                self.par('col_bits'  ,      10)
                self.par('dq_bits'   ,      16)
                self.par('dqs_bits'  ,       2)
            else:
                assert(0)
        elif (self.size == 'den8192Mb'):
            if (self.xn == 4):
                self.par('dm_bits'   ,       1)
                self.par('addr_bits' ,      16)
                self.par('row_bits'  ,      16)
                self.par('col_bits'  ,      14)
                self.par('dq_bits'   ,       4)
                self.par('dqs_bits'  ,       1)
            elif (self.xn == 8):
                self.par('dm_bits'   ,       1)
                self.par('addr_bits' ,      16)
                self.par('row_bits'  ,      16)
                self.par('col_bits'  ,      11)
                self.par('dq_bits'   ,       8)
                self.par('dqs_bits'  ,       1)
            elif (self.xn == 16):
                self.par('dm_bits'   ,       2)
                self.par('addr_bits' ,      16)
                self.par('row_bits'  ,      16)
                self.par('col_bits'  ,      10)
                self.par('dq_bits'   ,      16)
                self.par('dqs_bits'  ,       2)
            else:
                assert(0)

