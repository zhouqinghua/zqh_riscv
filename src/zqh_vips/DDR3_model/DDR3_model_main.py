from phgl_imp import *

class ddr3(module):
    def set_par(self):
        super(ddr3, self).set_par()
        self.p.par('speed_bin', 'sg125')
        self.p.par('size', 'den4096Mb')
        self.p.par('xn', 16)

        self.p.par('MEM_BITS', 17, vinst = 1)
        self.p.par('DEBUG', 1, vinst = 1)
        self.p.par('STOP_ON_ERROR', 1, vinst = 1)

    def check_par(self):
        super(ddr3, self).check_par()
        assert(self.p.speed_bin in (
            'sg093', 'sg107', 'sg125', 'sg15E', 
            'sg15', 'sg187E', 'sg187', 'sg25E', 'sg25'))
        self.pm.vuser  = [
            ('code', '`define %s' %(self.p.speed_bin)),
            ('code', '`define %s' %(self.p.size)),
            ('code', '`define x%0d' %(self.p.xn)),
            ('inc' , '../../common/vips/DDR3_model/ddr3.v')]

    def set_port(self):
        super(ddr3, self).set_port()
        self.no_crg()

        ba_bits          =       3
        if (self.p.size == 'den1024Mb'):
            if (self.p.xn == 4):
                dm_bits          =       1
                addr_bits        =      14
                row_bits         =      14
                col_bits         =      11
                dq_bits          =       4
                dqs_bits         =       1
            elif (self.p.xn == 8):
                dm_bits          =       1
                addr_bits        =      14
                row_bits         =      14
                col_bits         =      10
                dq_bits          =       8
                dqs_bits         =       1
            elif (self.p.xn == 16):
                dm_bits          =       2
                addr_bits        =      13
                row_bits         =      13
                col_bits         =      10
                dq_bits          =      16
                dqs_bits         =       2
            else:
                assert(0)
        elif (self.p.size == 'den2048Mb'):
            if (self.p.xn == 4):
                dm_bits          =       1
                addr_bits        =      15
                row_bits         =      15
                col_bits         =      11
                dq_bits          =       4
                dqs_bits         =       1
            elif (self.p.xn == 8):
                dm_bits          =       1
                addr_bits        =      15
                row_bits         =      15
                col_bits         =      10
                dq_bits          =       8
                dqs_bits         =       1
            elif (self.p.xn == 16):
                dm_bits          =       2
                addr_bits        =      14
                row_bits         =      14
                col_bits         =      10
                dq_bits          =      16
                dqs_bits         =       2
            else:
                assert(0)
        elif (self.p.size == 'den4096Mb'):
            if (self.p.xn == 4):
                dm_bits          =       1
                addr_bits        =      16
                row_bits         =      16
                col_bits         =      11
                dq_bits          =       4
                dqs_bits         =       1
            elif (self.p.xn == 8):
                dm_bits          =       1
                addr_bits        =      16
                row_bits         =      16
                col_bits         =      10
                dq_bits          =       8
                dqs_bits         =       1
            elif (self.p.xn == 16):
                dm_bits          =       2
                addr_bits        =      15
                row_bits         =      15
                col_bits         =      10
                dq_bits          =      16
                dqs_bits         =       2
            else:
                assert(0)
        elif (self.p.size == 'den8192Mb'):
            if (self.p.xn == 4):
                dm_bits          =       1
                addr_bits        =      16
                row_bits         =      16
                col_bits         =      14
                dq_bits          =       4
                dqs_bits         =       1
            elif (self.p.xn == 8):
                dm_bits          =       1
                addr_bits        =      16
                row_bits         =      16
                col_bits         =      11
                dq_bits          =       8
                dqs_bits         =       1
            elif (self.p.xn == 16):
                dm_bits          =       2
                addr_bits        =      16
                row_bits         =      16
                col_bits         =      10
                dq_bits          =      16
                dqs_bits         =       2
            else:
                assert(0)





        self.io.var(inp('rst_n'))
        self.io.var(inp('ck'))
        self.io.var(inp('ck_n'))
        self.io.var(inp('cke'))
        self.io.var(inp('cs_n'))
        self.io.var(inp('ras_n'))
        self.io.var(inp('cas_n'))
        self.io.var(inp('we_n'))
        self.io.var(inoutp('dm_tdqs', w = dm_bits))
        self.io.var(inp('ba', w = ba_bits))
        self.io.var(inp('addr', w = addr_bits))
        self.io.var(inoutp('dq', w = dq_bits))
        self.io.var(inoutp('dqs', w = dqs_bits))
        self.io.var(inoutp('dqs_n', w = dqs_bits))
        self.io.var(outp('tdqs_n', w = dqs_bits))
        self.io.var(inp('odt'))
