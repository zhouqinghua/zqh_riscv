from phgl_imp import *
from .zqh_ddr_mc_parameters import *
from .zqh_ddr_mc_bundles import *
from zqh_ddr_phy.zqh_ddr_phy_bundles import zqh_ddr_phy_dfi_io

class zqh_ddr_mc_dfi(csr_module):
    def set_par(self):
        super(zqh_ddr_mc_dfi, self).set_par()
        self.p = zqh_ddr_mc_parameter()

    def set_port(self):
        super(zqh_ddr_mc_dfi, self).set_port()
        self.io.var(zqh_ddr_phy_dfi_io('phy_dfi').flip())
        self.io.var(csr_reg_io(
            'reg',
            addr_bits = 12,
            data_bits = 32))
        self.io.var(zqh_ddr_mc_mem_io(
            'mem',
            addr_bits = self.p.addr_bits,
            token_bits = self.p.token_bits,
            size_bits = self.p.size_bits,
            data_bits = self.p.data_bits))
        self.io.var(outp('int_flag'))

    def main(self):
        super(zqh_ddr_mc_dfi, self).main()
        self.reg_if = self.io.reg

        #cfg_regs
        #{{{
        for i in range(self.p.cfg_reg_num):
            reg_name = 'cfg_regs_'+str(i)
            reg_size = 4
            reg_offset = i*reg_size
            if (i == 0):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('version',     width = 16, reset = 0x0000, access = 'RO', comments = '''\
Holds the controller version number.'''),
                        csr_reg_field_desc('reserved1',   width = 4, access = 'VOL'),
                        csr_reg_field_desc('dram_class',  width = 4, reset = 0, comments = '''\
Defines the mode of operation of the controller.
DDR3:0x6 DDR4:0xA'''),
                        csr_reg_field_desc('reserved0',   width = 7, access = 'VOL'),
                        csr_reg_field_desc('start',       width = 1, reset = 0, comments = '''\
Initiate command processing in the controller. Set to 1 to initiate.''')]))
            elif (i == 1):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('read_data_fifo_depth',  width = 8, reset = 8, access = 'RO', comments = '''\
Reports the depth of the controller core read data queue.'''),
                        csr_reg_field_desc('max_cs_reg',            width = 8, reset = 0x2, access = 'RO', comments = '''\
Holds the maximum number of chip selects available.'''),
                        csr_reg_field_desc('max_col_reg',           width = 8, reset = 0xb, access = 'RO', comments = '''\
Holds the maximum width of column address in DRAMs.'''),
                        csr_reg_field_desc('max_row_reg',           width = 8, reset = 0x10, access = 'RO', comments = '''\
Holds the maximum width of memory address bus.''')]))
            elif (i == 2):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('async_cdc_stages',           width = 8, reset = 0, access = 'RO'),
                        csr_reg_field_desc('write_data_fifo_ptr_width',  width = 8, reset = 0, access = 'RO'),
                        csr_reg_field_desc('write_data_fifo_depth',      width = 8, reset = 8, access = 'RO'),
                        csr_reg_field_desc('read_data_fifo_ptr_width',   width = 8, reset = 0, access = 'RO')]))
            elif (i == 3):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 4):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 5):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 6):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 7):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tinit',  width = 32, reset = 0, comments = '''\
DRAM TINIT value in cycles.''')]))
            elif (i == 8):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('trst_pwron',  width = 32, reset = 0, comments = '''\
Duration of memory reset during power-on initializatio.''')]))
            elif (i == 9):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('cke_inactive',  width = 32, reset = 0, comments = '''\
Number of cycles after reset before CKE will be active.''')]))
            elif (i == 10):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tcpd',      width = 16, reset = 0, comments = '''\
DRAM TCPD value in cycles.'''),
                        csr_reg_field_desc('initaref',  width = 8, reset = 0, comments = '''\
Number of auto-refresh commands to execute during DRAM initialization.''')]))
            elif (i == 11):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('caslat_lin',   width = 6, reset = 0, comments = '''\
Sets latency from read command send to data receive from/to controller.
caslat_lin[5:1] is CAS latency. caslat_lin[0] is no used.'''),
                        csr_reg_field_desc('reserved',     width = 7, access = 'VOL'),
                        csr_reg_field_desc('no_cmd_init',  width = 1, reset = 0, comments = '''\
Disable DRAM commands until the TDLL parameter has expired during initialization. Set to 1 to disable.'''),
                        csr_reg_field_desc('tdll',         width = 16, reset = 0, comments = '''\
DRAM TDLL value in cycles.''')]))
            elif (i == 12):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tccd',               width = 8, reset = 0, comments = '''\
DRAM CAS-to-CAS value in cycles.'''),
                        csr_reg_field_desc('tbst_int_interval',  width = 8, reset = 0, comments = '''\
DRAM burst interrupt interval value in cycles.'''),
                        csr_reg_field_desc('additive_lat',       width = 8, reset = 0, comments = '''\
DRAM additive latency value in cycles.'''),
                        csr_reg_field_desc('wrlat',              width = 8, reset = 0, comments = '''\
DRAM WRLAT value in cycles.''')]))
            elif (i == 13):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('twtr',      width = 8, reset = 0, comments = '''\
DRAM TWTR value in cycles.'''),
                        csr_reg_field_desc('tras_min',  width = 8, reset = 0, comments = '''\
DRAM TRAS_MIN value in cycles.'''),
                        csr_reg_field_desc('trc',       width = 8, reset = 0, comments = '''\
DRAM TRC value in cycles.'''),
                        csr_reg_field_desc('trrd',      width = 8, reset = 0, comments = '''\
DRAM TRRD value in cycles.''')]))
            elif (i == 14):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tmrd',  width = 8, reset = 0, comments = '''\
DRAM TMRD value in cycles.'''),
                        csr_reg_field_desc('trtp',  width = 8, reset = 0, comments = '''\
DRAM TRTP value in cycles.'''),
                        csr_reg_field_desc('tfaw',  width = 8, reset = 0, comments = '''\
DRAM TFAW value in cycles.'''),
                        csr_reg_field_desc('trp',   width = 8, reset = 0, comments = '''\
DRAM TRP value in cycles.''')]))
            elif (i == 15):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tras_max',  width = 17, reset = 0, comments = '''\
DRAM TRAS_MAX value in cycles.'''),
                        csr_reg_field_desc('tmod',      width = 8, reset = 0, comments = '''\
Number of cycles after MRS command and before any other command.''')]))
            elif (i == 16):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('trcd',         width = 8, reset = 0, comments = '''\
DRAM TRCD value in cycles.'''),
                        csr_reg_field_desc('reserved',     width = 7, access = 'VOL'),
                        csr_reg_field_desc('writeinterp',  width = 1, reset = 0, comments = '''\
Allow controller to interrupt a write burst to the DRAMs with a read command. Set to 1 to allow interruption.'''),
                        csr_reg_field_desc('tckesr',       width = 8, reset = 0, comments = '''\
Minimum CKE low pulse width during a self-refresh.'''),
                        csr_reg_field_desc('tcke',         width = 8, reset = 0, comments = '''\
Minimum CKE pulse width.''')]))
            elif (i == 17):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tras_lockout',  width = 1, reset = 0, comments = '''\
Allow the controller to execute auto pre-charge commands before the TRAS_MIN parameter expires. Set to 1 to enable.'''),
                        csr_reg_field_desc('reserved1',     width = 7, access = 'VOL'),
                        csr_reg_field_desc('concurrentap',  width = 1, reset = 0, comments = '''\
Allow controller to issue commands to other banks while a bank is in auto pre-charge. Set to 1 to enable.'''),
                        csr_reg_field_desc('reserved0',     width = 7, access = 'VOL'),
                        csr_reg_field_desc('ap',            width = 1, reset = 0, comments = '''\
Enable auto pre-charge mode of controller. Set to 1 to enable.'''),
                        csr_reg_field_desc('twr',           width = 8, reset = 0, comments = '''\
DRAM TWR value in cycles.''')]))
            elif (i == 18):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('reg_dimm_enable',  width = 1, reset = 0, comments = '''\
Enable registered DIMM operation of the controller. Set to 1 to enable.'''),
                        csr_reg_field_desc('trp_ab',           width = 8, reset = 0, comments = '''\
DRAM TRP all bank value in cycles.'''),
                        csr_reg_field_desc('bstlen',           width = 8, reset = 0x2, comments = '''\
Encoded burst length sent to DRAMs during initialization. Set to 1 for BL2, set to 2 for BL4, or set to 3 for BL8.'''),
                        csr_reg_field_desc('tdal',             width = 8, reset = 0, comments = '''\
DRAM TDAL value in cycles.''')]))
            elif (i == 19):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tref_enable',        width = 1, reset = 0, comments = '''\
Issue auto-refresh commands to the DRAMs at the interval defined in the TREF parameter. Set to 1 to enable.'''),
                        csr_reg_field_desc('reserved',           width = 15, access = 'VOL'),
                        csr_reg_field_desc('arefresh',           width = 1, reset = 0, access = 'WO', comments = '''\
Initiate auto-refresh at the end of the current burst boundary. Set to 1 to trigger.'''),
                        csr_reg_field_desc('address_mirroring',  width = 8, reset = 0, comments = '''\
Indicates which chip selects support address mirroring. Bit (0) controls cs0, bit (1) controls cs1, etc. Set each bit to 1 to enable.''')]))
            elif (i == 20):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tref',  width = 16, reset = 0, comments = '''\
DRAM TREF value in cycles.'''),
                        csr_reg_field_desc('trfc',  width = 16, reset = 0, comments = '''\
DRAM TRFC value in cycles.''')]))
            elif (i == 21):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tpdex',     width = 16, reset = 0, comments = '''\
DRAM TPDEX value in cycles.'''),
                        csr_reg_field_desc('reserved',  width = 16, access = 'VOL')]))
            elif (i == 22):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('txsr',    width = 16, reset = 0, comments = '''\
DRAM TXSR value in cycles.'''),
                        csr_reg_field_desc('txpdll',  width = 16, reset = 0, comments = '''\
DRAM TXPDLL value in cycles.''')]))
            elif (i == 23):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('pwrup_srefresh_exit',  width = 1, reset = 0, comments = '''\
Allow powerup via self-refresh instead of full memory initialization.  Set to 1 to enable.'''),
                        csr_reg_field_desc('reserved',             width = 8, access = 'VOL'),
                        csr_reg_field_desc('txsnr',                width = 16, reset = 0, comments = '''\
DRAM TXSNR value in cycles.''')]))
            elif (i == 24):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('cke_delay',                 width = 8, reset = 0, comments = '''\
Additional cycles to delay CKE for status reporting.'''),
                        csr_reg_field_desc('reserved1',                 width = 7, access = 'VOL'),
                        csr_reg_field_desc('enable_quick_srefresh',     width = 1, reset = 0, comments = '''\
Allow user to interrupt memory initialization to enter self-refresh mode. Set to 1 to allow interruption.'''),
                        csr_reg_field_desc('reserved0',                 width = 7, access = 'VOL'),
                        csr_reg_field_desc('srefresh_exit_no_refresh',  width = 1, reset = 0, comments = '''\
Disables the automatic refresh request associated with self-refresh exit. Set to 1 to disable.''')]))
            elif (i == 25):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('write_modereg',  width = 26, reset = 0, comments = '''\
Write memory mode register data to the DRAMs. Bits (7:0) define the memory mode register number if bit (23) is set, bits (15:8) define the chip select if bit (24) is clear, bits (23:16) define which memory mode register/s to write, bit (24) defines whether all chip selects will be written, and bit (25) triggers the write.''')]))
            elif (i == 26):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('mr0_data_0',  width = 16, reset = 0, comments = '''\
Data to program into memory mode register 0 for chip select 0.'''),
                        csr_reg_field_desc('mrw_status',  width = 8, reset = 0, access = 'RO', comments = '''\
Write memory mode register status. Bit (0) set indicates a WRITE_MODEREG parameter programming error.''')]))
            elif (i == 27):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('mr2_data_0',  width = 16, reset = 0, comments = '''\
Data to program into memory mode register 2 for chip select 0.'''),
                        csr_reg_field_desc('mr1_data_0',  width = 16, reset = 0, comments = '''\
Data to program into memory mode register 1 for chip select 0.''')]))
            elif (i == 28):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('mr3_data_0',       width = 16, reset = 0, comments = '''\
Data to program into memory mode register 3 for chip select 0.'''),
                        csr_reg_field_desc('mrsingle_data_0',  width = 16, reset = 0, comments = '''\
Data to program into memory mode register single write to chip select 0.''')]))
            elif (i == 29):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('mr1_data_1',  width = 16, reset = 0, comments = '''\
Data to program into memory mode register 1 for chip select 1.'''),
                        csr_reg_field_desc('mr0_data_1',  width = 16, reset = 0, comments = '''\
Data to program into memory mode register 0 for chip select 1.''')]))
            elif (i == 30):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('mrsingle_data_1',  width = 16, reset = 0, comments = '''\
Data to program into memory mode register single write to chip select 1.'''),
                        csr_reg_field_desc('mr2_data_1',       width = 16, reset = 0, comments = '''\
Data to program into memory mode register 2 for chip select 1.''')]))
            elif (i == 31):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('bist_result',  width = 2, reset = 0, access = 'RO', comments = '''\
BIST operation status (pass/fail).  Bit (0) indicates data check status and bit (1) indicates address check status. Value of 1 is a passing result.'''),
                        csr_reg_field_desc('reserved',     width = 7, access = 'VOL'),
                        csr_reg_field_desc('bist_go',      width = 1, reset = 0, access = 'WO', comments = '''\
Initiate a BIST operation. Set to 1 to trigger.'''),
                        csr_reg_field_desc('mr3_data_1',   width = 16, reset = 0, comments = '''\
Data to program into memory mode register 3 for chip select 1.''')]))
            elif (i == 32):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('bist_addr_check',  width = 1, reset = 0, comments = '''\
Enable address checking with BIST operation. Set to 1 to enable.'''),
                        csr_reg_field_desc('reserved',         width = 7, access = 'VOL'),
                        csr_reg_field_desc('bist_data_check',  width = 1, reset = 0, comments = '''\
Enable data checking with BIST operation. Set to 1 to enable.'''),
                        csr_reg_field_desc('addr_space',       width = 8, reset = 0, comments = '''\
Sets the number of address bits to check during BIST operation.''')]))
            elif (i == 33):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('bist_start_address',  width = 32, reset = 0, comments = '''\
Start BIST checking at this address.''')]))
            elif (i == 34):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('bist_start_address',  width = 32, reset = 0, comments = '''\
Start BIST checking at this address.''')]))
            elif (i == 35):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('bist_data_mask',  width = 32, reset = 0, comments = '''\
Mask applied to data for BIST error checking. Bit (0) controls memory data path bit (0), bit (1) controls memory data path bit (1), etc. Set each bit to 1 to mask.''')]))
            elif (i == 36):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('bist_data_mask',  width = 32, reset = 0, comments = '''\
Mask applied to data for BIST error checking. Bit (0) controls memory data path bit (0), bit (1) controls memory data path bit (1), etc. Set each bit to 1 to mask.''')]))
            elif (i == 37):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('zqinit',           width = 16, reset = 0, comments = '''\
Number of cycles needed for a ZQINIT command.'''),
                        csr_reg_field_desc('long_count_mask',  width = 8, reset = 0, comments = '''\
Reduces the length of the long counter from 1024 cycles. The only supported values are 0x00 (1024 cycles), 0x10 (512 clocks), 0x18 (256 clocks), 0x1C (128 clocks), 0x1E (64 clocks) and 0x1F (32 clocks).''')]))
            elif (i == 38):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('zqcs',  width = 16, reset = 0, comments = '''\
Number of cycles needed for a ZQCS command.'''),
                        csr_reg_field_desc('zqcl',  width = 16, reset = 0, comments = '''\
Number of cycles needed for a ZQCL command.''')]))
            elif (i == 39):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('zq_on_sref_exit',  width = 8, reset = 0, comments = '''\
Defines the type of ZQ calibration performed at self-refresh exit. Bit (0) selects ZQCS, bit (1) selects ZQCL, bit (2) selects ZQINIT and bit (3) selects ZQRESET. Set one of these bits to 1 to enable.'''),
                        csr_reg_field_desc('zq_req',           width = 8, reset = 0, access = 'WO', comments = '''\
User request to initiate a ZQ calibration. Bit (0) controls ZQCS, bit (1) controls ZQCL, bit (2) controls ZQINIT, and bit (3) controls ZQRESET. Set one of these bits to 1 to trigger.''')]))
            elif (i == 40):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('zq_interval',  width = 31, reset = 0, comments = '''\
Number of long count sequences allowed between automatic ZQCS commands.''')]))
            elif (i == 41):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('row_diff',        width = 3, reset = 0, comments = '''\
Difference between number of address pins available and number being used.'''),
                        csr_reg_field_desc('reserved2',       width = 6, access = 'VOL'),
                        csr_reg_field_desc('bank_diff',       width = 2, reset = 0, comments = '''\
Encoded number of banks on the DRAM(s).'''),
                        csr_reg_field_desc('reserved1',       width = 7, access = 'VOL'),
                        csr_reg_field_desc('zqcs_rotate',     width = 1, reset = 0, comments = '''\
Selects whether a ZQCS command will calibrate just one chip select or all chip selects. Set to 1 for rotating CS.'''),
                        csr_reg_field_desc('reserved0',       width = 7, access = 'VOL'),
                        csr_reg_field_desc('zq_in_progress',  width = 1, reset = 0, access = 'RO', comments = '''\
Indicates that a ZQ command is currently in progress. Value of 1 indicates command in progress.''')]))
            elif (i == 42):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('command_age_count',  width = 8, reset = 0, comments = '''\
Initial value of individual command aging counters for command aging.'''),
                        csr_reg_field_desc('age_count',          width = 8, reset = 0, comments = '''\
Initial value of master aging-rate counter for command aging.'''),
                        csr_reg_field_desc('aprebit',            width = 8, reset = 0xa, comments = '''\
Location of the auto pre-charge bit in the DRAM address.'''),
                        csr_reg_field_desc('col_diff',           width = 8, reset = 0, comments = '''\
Difference between number of column pins available and number being used.''')]))
            elif (i == 43):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 44):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 45):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 46):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('burst_on_fly_bit',       width = 4, reset = 0, comments = '''\
Identifies the burst-on-fly bit in the memory mode registers.'''),
                        csr_reg_field_desc('cs_map',                 width = 8, reset = 0, comments = '''\
Defines which chip selects are active.'''),
                        csr_reg_field_desc('reserved1',              width = 6, access = 'VOL'),
                        csr_reg_field_desc('inhibit_dram_cmd',       width = 2, reset = 0, comments = '''\
Inhibit command types from being executed from the command queue. Set to 0 to enable any command, set to 1 to inhibit read/ write and bank commands, set to 2 to inhibit MRR and peripheral MRR commands, or set to 3 to inhibit MRR and read/write commands.'''),
                        csr_reg_field_desc('reserved0',              width = 7, access = 'VOL'),
                        csr_reg_field_desc('disable_rd_interleave',  width = 1, reset = 0, comments = '''\
Disable read data interleaving for commands from the same port, regardless of the requestor ID.''')]))
            elif (i == 47):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('controller_busy',  width = 1, reset = 0, comments = '''\
Indicator that the controller is processing a command. Evaluates all ports for outstanding transactions. Value of 1 indicates controller busy.'''),
                        csr_reg_field_desc('reserved1',        width = 7, access = 'VOL'),
                        csr_reg_field_desc('in_order_accept',  width = 1, reset = 0, comments = '''\
Forces the controller to accept commands in the order in which they are placed in the command queue.'''),
                        csr_reg_field_desc('q_fullness',       width = 8, reset = 0, comments = '''\
Quantity that determines command queue full.'''),
                        csr_reg_field_desc('reserved0',        width = 7, access = 'VOL'),
                        csr_reg_field_desc('reduc',            width = 1, reset = 0, comments = '''\
Enable the half datapath feature of the controller. Set to 1 to enable.''')]))
            elif (i == 48):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('ctrlupd_req_per_aref_en',  width = 1, reset = 0, comments = '''\
Enable an automatic controllerinitiated update (dfi_ctrlupd_req) after every refresh. Set to 1 to enable'''),
                        csr_reg_field_desc('reserved0',                width = 7, access = 'VOL'),
                        csr_reg_field_desc('ctrlupd_req',              width = 1, reset = 0, access = 'WO', comments = '''\
Assert the DFI controller-initiated update request signal dfi_ctrlupd_req. Set to 1 to trigger.''')]))
            elif (i == 49):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('int_status',  width = 32, reset = 0, access = 'RO', comments = '''\
Status of interrupt features in the controller.''')]))
            elif (i == 50):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 51):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('int_mask',  width = 32, reset = 0, comments = '''\
Mask for controller_int signals from the INT_STATUS parameter.''')]))
            elif (i == 52):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('out_of_range_addr',  width = 32, reset = 0, access = 'RO', comments = '''\
Address of command that caused an out-of-range interrupt.''')]))
            elif (i == 53):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('out_of_range_type',    width = 6, reset = 0, access = 'RO', comments = '''\
Type of command that caused an out-of-range interrupt.'''),
                        csr_reg_field_desc('out_of_range_length',  width = 8, reset = 0, access = 'RO', comments = '''\
Length of command that caused an out-of-range interrupt.'''),
                        csr_reg_field_desc('out_of_range_addr',    width = 8, reset = 0, access = 'RO', comments = '''\
Address of command that caused an out-of-range interrupt.''')]))
            elif (i == 54):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 55):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 56):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 57):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 58):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 59):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 60):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 61):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 62):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 63):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 64):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 65):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('port_cmd_error_addr',  width = 32, reset = 0, access = 'RO', comments = '''\
Address of command that caused the PORT command error.''')]))
            elif (i == 66):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('port_cmd_error_type',  width = 2, reset = 0, access = 'RO', comments = '''\
Type of error and access type that caused the PORT command error.'''),
                        csr_reg_field_desc('port_cmd_error_addr',  width = 8, reset = 0, access = 'RO', comments = '''\
Address of command that caused the PORT command error.''')]))
            elif (i == 67):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('odt_wr_map_cs1',  width = 8, reset = 0, comments = '''\
Determines which chip(s) will have termination when a write occurs on chip select 1. Set bit X to enable termination on csX when cs1 is performing a write.'''),
                        csr_reg_field_desc('odt_rd_map_cs1',  width = 8, reset = 0, comments = '''\
Determines which chip(s) will have termination when a read occurs on chip select 1. Set bit X to enable termination on csX when cs1 is performing a read.'''),
                        csr_reg_field_desc('odt_wr_map_cs0',  width = 8, reset = 0, comments = '''\
Determines which chip(s) will have termination when a write occurs on chip select 0. Set bit X to enable termination on csX when cs0 is performing a write.'''),
                        csr_reg_field_desc('odt_rd_map_cs0',  width = 8, reset = 0, comments = '''\
Determines which chip(s) will have termination when a read occurs on chip select 0. Set bit X to enable termination on csX when cs0 is performing a read.''')]))
            elif (i == 68):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('odt_en',      width = 1, reset = 0, comments = '''\
Enable support of DRAM ODT.  When enabled, controller will assert and de-assert ODT output to DRAM as needed.'''),
                        csr_reg_field_desc('todth_rd',    width = 8, reset = 0, comments = '''\
Defines the DRAM minimum ODT high time after an ODT assertion for a read command.'''),
                        csr_reg_field_desc('todth_wr',    width = 8, reset = 0, comments = '''\
Defines the DRAM minimum ODT high time after an ODT assertion for a write command.'''),
                        csr_reg_field_desc('todtl_2cmd',  width = 8, reset = 0, comments = '''\
Defines the DRAM delay from an ODT de-assertion to the next nonwrite, non-read command.''')]))
            elif (i == 69):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('add_odt_clk_w2r_samecs',  width = 8, reset = 0, comments = '''\
Additional delay to insert between write and read transaction types to the same chip select to meet ODT timing requirements. Any value including 0x0 supported.'''),
                        csr_reg_field_desc('add_odt_clk_r2w_samecs',  width = 8, reset = 0, comments = '''\
Additional delay to insert between read and write transaction types to the same chip select to meet ODT timing requirements.'''),
                        csr_reg_field_desc('rd_to_odth',              width = 8, reset = 0, comments = '''\
Defines the delay from a read command to ODT assertion.'''),
                        csr_reg_field_desc('wr_to_odth',              width = 8, reset = 0, comments = '''\
Defines the delay from a write command to ODT assertion.''')]))
            elif (i == 70):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('r2w_diffcs_dly',               width = 8, reset = 0x1, comments = '''\
Additional delay to insert between reads and writes to different chip selects. Program to a non-zero value.'''),
                        csr_reg_field_desc('r2r_diffcs_dly',               width = 8, reset = 0x1, comments = '''\ Additional delay to insert between reads to different chip selects.  Program to a non-zero value.'''),
                        csr_reg_field_desc('add_odt_clk_sametype_diffcs',  width = 8, reset = 0, comments = '''\
Additional delay to insert between same transaction types to different chip selects to meet ODT timing requirements.'''),
                        csr_reg_field_desc('add_odt_clk_difftype_diffcs',  width = 8, reset = 0, comments = '''\
Additional delay to insert between different transaction types to different chip selects to meet ODT timing requirements.''')]))
            elif (i == 71):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('r2w_samecs_dly',  width = 8, reset = 0x2, comments = '''\
Additional delay to insert between reads and writes to the same chip select. Program to a non-zero value.'''),
                        csr_reg_field_desc('r2r_samecs_dly',  width = 8, reset = 0x0, comments = '''\
Additional delay to insert between two reads to the same chip select.  Any value including 0x0 supported.'''),
                        csr_reg_field_desc('w2w_diffcs_dly',  width = 8, reset = 0x1, comments = '''\
Additional delay to insert between writes and writes to different chip selects. Program to a non-zero value.'''),
                        csr_reg_field_desc('w2r_diffcs_dly',  width = 8, reset = 0x1, comments = '''\
Additional delay to insert between writes and reads to different chip selects. Allowed programming dependent on memory system.''')]))
            elif (i == 72):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('ocd_adjust_pup_cs_0',  width = 8, reset = 0, comments = '''\
OCD pull-up adjust setting for DRAMs for chip select 0.'''),
                        csr_reg_field_desc('ocd_adjust_pdn_cs_0',  width = 8, reset = 0, comments = '''\
OCD pull-down adjust setting for DRAMs for chip select 0.'''),
                        csr_reg_field_desc('w2w_samecs_dly',       width = 8, reset = 0, comments = '''\
Additional delay to insert between two writes to the same chip select.  Any value including 0x0 supported.'''),
                        csr_reg_field_desc('w2r_samecs_dly',       width = 8, reset = 0, comments = '''\
Additional delay to insert between writes and reads to the same chip select.''')]))
            elif (i == 73):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 74):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 75):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 76):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 77):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 78):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 79):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 80):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 81):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 82):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 83):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 84):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 85):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 86):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 87):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 88):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 89):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 90):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 91):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 92):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 93):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 94):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 95):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 96):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 97):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 98):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 99):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 100):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 101):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 102):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 103):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 104):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('mem_rst_valid',  width = 1, reset = 0, access = 'RO', comments = '''\
Register access to mem_rst_valid signal.'''),
                        csr_reg_field_desc('cke_status',     width = 8, reset = 0, access = 'RO', comments = '''\
Register access to cke_status signal.'''),
                        csr_reg_field_desc('reserved1',      width = 8, access = 'VOL')]))
            elif (i == 105):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdfi_phy_wrlat',   width = 8, reset = 0, access = 'RO', comments = '''\
Holds the calculated DFI tPHY_WRLAT timing parameter (in DFI PHY clocks), the maximum cycles between a write command and a dfi_wrdata_en assertion.'''),
                        csr_reg_field_desc('dll_rst_adj_dly',  width = 8, reset = 0, comments = '''\
Minimum cycles after setting master delay in DLL until the DLL reset signal dll_rst_n may be asserted. If this signal is not being used by the PHY, this parameter may be ignored.'''),
                        csr_reg_field_desc('dll_rst_delay',    width = 16, reset = 0, comments = '''\
Minimum cycles required for DLL reset signal dll_rst_n to be held. If this signal is not being used by the PHY, this parameter may be ignored.''')]))
            elif (i == 106):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('dram_clk_disable',     width = 8, reset = 0, comments = '''\
Set value for the dfi_dram_clk_disable signal. Bit (0) controls cs0, bit (1) controls cs1, etc. Set each bit to 1 to disable.'''),
                        csr_reg_field_desc('tdfi_rddata_en',       width = 8, reset = 0, access = 'RO', comments = '''\
Holds the calculated DFI tRDDATA_EN timing parameter (in DFI PHY clocks), the maximum cycles between a read command and a dfi_rddata_en assertion.'''),
                        csr_reg_field_desc('tdfi_phy_rdlat',       width = 8, reset = 0x6, comments = '''\
Defines the DFI tPHY_RDLAT timing parameter (in DFI PHY clocks), the maximum cycles between a dfi_rddata_en assertion and a dfi_rddata_valid assertion.'''),
                        csr_reg_field_desc('update_error_status',  width = 8, reset = 0, access = 'RO', comments = '''\
Identifies the source of any DFI MC-initiated or PHY-initiated update errors. Value of 1 indicates a timing violation of the associated timing parameter.''')]))
            elif (i == 107):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdfi_ctrlupd_max',  width = 16, reset = 0, comments = '''\
Defines the DFI tCTRLUPD_MAX timing parameter (in DFI clocks), the maximum cycles that dfi_ctrlupd_req can be asserted. If programmed to a non-zero, a timing violation will cause an interrupt and bit (1) set in the UPDATE_ERROR_STATUS parameter.'''),
                        csr_reg_field_desc('tdfi_ctrlupd_min',  width = 8, reset = 0x4, access = 'RO', comments = '''\
Reports the DFI tCTRLUPD_MIN timing parameter (in DFI clocks), the minimum cycles that dfi_ctrlupd_req must be asserted.''')]))
            elif (i == 108):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdfi_phyupd_type1',  width = 16, reset = 0, comments = '''\
Defines the DFI tPHYUPD_TYPE1 timing parameter (in DFI clocks), the maximum cycles that dfi_phyupd_req can assert after dfi_phyupd_ack for dfi_phyupd_type 1. If programmed to a non-zero, a timing violation will cause an interrupt and bit (3) set in the UPDATE_ERROR_STATUS parameter.'''),
                        csr_reg_field_desc('tdfi_phyupd_type0',  width = 16, reset = 0, comments = '''\
Defines the DFI tPHYUPD_TYPE0 timing parameter (in DFI clocks), the maximum cycles that dfi_phyupd_req can assert after dfi_phyupd_ack for dfi_phyupd_type 0. If programmed to a non-zero, a timing violation will cause an interrupt and bit (2) set in the UPDATE_ERROR_STATUS parameter.''')]))
            elif (i == 109):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdfi_phyupd_type3',  width = 16, reset = 0, comments = '''\
Defines the DFI tPHYUPD_TYPE3 timing parameter (in DFI clocks), the maximum cycles that dfi_phyupd_req can assert after dfi_phyupd_ack for dfi_phyupd_type 3. If programmed to a non-zero, a timing violation will cause an interrupt and bit (5) set in the UPDATE_ERROR_STATUS parameter.'''),
                        csr_reg_field_desc('tdfi_phyupd_type2',  width = 16, reset = 0, comments = '''\
Defines the DFI tPHYUPD_TYPE2 timing parameter (in DFI clocks), the maximum cycles that dfi_phyupd_req can assert after dfi_phyupd_ack for dfi_phyupd_type 2. If programmed to a non-zero, a timing violation will cause an interrupt and bit (4) set in the UPDATE_ERROR_STATUS parameter.''')]))
            elif (i == 110):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdfi_phyupd_resp',  width = 16, reset = 0, comments = '''\
Defines the DFI tPHYUPD_RESP timing parameter (in DFI clocks), the maximum cycles between a dfi_phyupd_req assertion and a dfi_phyupd_ack assertion. If programmed to a non-zero, a timing violation will cause an interrupt and bit (6) set in the UPDATE_ERROR_STATUS parameter.''')]))
            elif (i == 111):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdfi_ctrlupd_interval',  width = 32, reset = 0, comments = '''\
Defines the DFI tCTRLUPD_INTERVAL timing parameter (in DFI clocks), the maximum cycles between dfi_ctrlupd_req assertions. If programmed to a non-zero, a timing violation will cause an interrupt and bit (0) set in the UPDATE_ERROR_STATUS parameter. ''')]))
            elif (i == 112):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdfi_wrlvl_en',    width = 8, reset = 0, comments = '''\
Defines the DFI tWRLVL_EN timing parameter (in DFI clocks), the minimum cycles from a dfi_wrlvl_en assertion to the first dfi_wrlvl_strobe assertion.'''),
                        csr_reg_field_desc('tdfi_ctrl_delay',  width = 8, reset = 2, comments = '''\
Defines the DFI tCTRL_DELAY timing parameter (in DFI clocks), the delay between a DFI command change and a memory command.'''),
                        csr_reg_field_desc('wrlat_adj',        width = 8, reset = 0, comments = '''\
Adjustment value for PHY write timing.'''),
                        csr_reg_field_desc('rdlat_adj',        width = 8, reset = 0, comments = '''\
Adjustment value for PHY read timing.''')]))
            elif (i == 113):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 114):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 115):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 116):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 117):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 118):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 119):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 120):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 121):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 122):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 123):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 124):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 125):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 126):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 127):
                #self.cfg_reg(csr_reg_group(
                #    reg_name,
                #    offset = reg_offset,
                #    size = reg_size,
                #    fields_desc = [
                #        csr_reg_field_desc('data',  width = 32, reset = 0)]))
                self.gen_volatile_reg(reg_name, reg_offset, reg_size)
            elif (i == 128):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tinit3',           width = 24, reset = 0, comments = '''\
DRAM TINIT3 value in cycles.'''),
                        csr_reg_field_desc('tdfi_phy_wrdata',  width = 8, reset = 0, comments = '''\
Defines the DFI tPHY_WRDATA timing parameter (in DFI PHY clocks), the maximum cycles between a dfi_wrdata_en assertion and a dfi_wrdata signal.''')]))
            elif (i == 129):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tinit4',  width = 24, reset = 0, comments = '''\
DRAM TINIT4 value in cycles.''')]))
            elif (i == 130):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('no_auto_mrr_init',  width = 1, reset = 0, comments = '''\
Disable MRR commands during initialization. Set to 1 to disable.'''),
                        csr_reg_field_desc('tinit5',            width = 24, reset = 0, comments = '''\
DRAM TINIT5 value in cycles.''')]))
            elif (i == 131):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('read_modereg',  width = 24, reset = 0, comments = '''\
Read the specified memory mode register from specified chip when start bit set. Bits (7:0) define the memory mode register and bits (15:8) define the chip select. Set bit (16) to 1 to trigger.'''),
                        csr_reg_field_desc('tmrr',          width = 8, reset = 0, comments = '''\
DRAM TMRR value in cycles.''')]))
            elif (i == 132):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('auto_tempchk_val',     width = 8, reset = 0, access = 'RO', comments = '''\
MR4 data for all chips accessed by automatic MRR commands, with 4 bits per chip select. Bits (3:0) correlate to cs0, bits (7:4) correlate to cs1, etc. Value indicates the OP7, OP2, OP1 and OP0 bits.'''),
                        csr_reg_field_desc('peripheral_mrr_data',  width = 16, reset = 0, access = 'RO', comments = '''\
Data and chip returned from memory mode register read requested by the READ_MODEREG parameter. Bits (7:0) indicate the read data and bits (15:8) indicate the chip.''')]))
            elif (i == 133):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('mr16_data_0',               width = 8, reset = 0, comments = '''\
Data to program into memory mode
register 16 for chip select 0.'''),
                        csr_reg_field_desc('mr8_data_0',                width = 8, reset = 0, access = 'RO', comments = '''\
Data read from MR8 for chip select 0.'''),
                        csr_reg_field_desc('refresh_per_auto_tempchk',  width = 16, reset = 0, comments = '''\
Number of long count sequences between automatic memory mode register read commands of MR4.''')]))
            elif (i == 134):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('mr17_data_1',  width = 8, reset = 0, comments = '''\
Data to program into memory mode register 17 for chip select 1.'''),
                        csr_reg_field_desc('mr16_data_1',  width = 8, reset = 0, comments = '''\
Data to program into memory mode register 16 for chip select 1.'''),
                        csr_reg_field_desc('mr8_data_1',   width = 8, reset = 0, access = 'RO', comments = '''\
Data read from MR8 for chip select 1.'''),
                        csr_reg_field_desc('mr17_data_0',  width = 8, reset = 0, comments = '''\
Data to program into memory mode register 17 for chip select 0.''')]))
            elif (i == 135):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('lpddr2_s4',   width = 1, reset = 0, comments = '''\
Defines the DRAM LPDDR2 device type being used. Set to 1 for LPDDR2-S4.'''),
                        csr_reg_field_desc('reserved1',   width = 7, access = 'VOL'),
                        csr_reg_field_desc('no_zq_init',  width = 1, reset = 0, comments = '''\
Disable ZQ operations during initialization. Set to 1 to disable.'''),
                        csr_reg_field_desc('reserved0',   width = 4, access = 'VOL'),
                        csr_reg_field_desc('zqreset',     width = 12, reset = 0, comments = '''\
Number of cycles needed for a ZQRESET command.''')]))
            elif (i == 136):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('int_ack',  width = 32, reset = 0, access = 'WO', comments = '''\
Clear mask of the INT_STATUS parameter.''')]))
            elif (i == 137):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('out_of_range_source_id',  width = 32, reset = 0, access = 'RO', comments = '''\
Source ID of command that caused an out-of-range interrupt.''')]))
            elif (i == 138):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdqsck_max',         width = 8, reset = 0, comments = '''\
Additional delay needed for tDQSCK.'''),
                        csr_reg_field_desc('port_cmd_error_id',  width = 24, reset = 0, access = 'RO', comments = '''\
Source ID of command that caused the PORT command error.''')]))
            elif (i == 139):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('txard',         width = 16, reset = 0, comments = '''\
DRAM TXARD value in cycles.'''),
                        csr_reg_field_desc('reserved',      width = 7, access = 'VOL'),
                        csr_reg_field_desc('en_1t_timing',  width = 1, reset = 0, comments = '''\
Enable 1T timing in a system supporting both 1T and 2T timing.  Set to 1 to enable.'''),
                        csr_reg_field_desc('tdqsck_min',    width = 8, reset = 0, comments = '''\
Additional delay needed for tDQSCK.''')]))
            elif (i == 140):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('cksre',                    width = 8, reset = 0, comments = '''\
Clock hold delay on self-refresh entry.'''),
                        csr_reg_field_desc('lowpower_refresh_enable',  width = 8, reset = 0, comments = '''\
Enable refreshes while in low power mode. Bit (0) controls cs0, bit (1) controls cs1, etc. Set each bit to 1 to disable.'''),
                        csr_reg_field_desc('txards',                   width = 16, reset = 0, comments = '''\
DRAM TXARDS value in cycles.''')]))
            elif (i == 141):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('lpi_sr_wakeup',  width = 8, reset = 0, comments = '''\
Defines the DFI tLP_WAKEUP timing parameter (in DFI clocks) to be driven when memory is in selfrefresh.'''),
                        csr_reg_field_desc('lpi_pd_wakeup',  width = 8, reset = 0, comments = '''\
Defines the DFI tLP_WAKEUP timing parameter (in DFI clocks) to be driven when memory is in power-down.'''),
                        csr_reg_field_desc('lp_cmd',         width = 8, reset = 0, access = 'WO', comments = '''\
Low power software command
request interface. Bit (0) controls
exit, bit (1) controls entry, bits (4:2)
define the low power state, bit (5)
controls memory clock gating, bit
(6) controls controller clock gating,
and bit (7) controls lock.
                                '''),
                        csr_reg_field_desc('cksrx',          width = 8, reset = 0, comments = '''\
Clock stable delay on self-refresh exit.''')]))
            elif (i == 142):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('lpi_wakeup_en',             width = 8, reset = 0, comments = '''\
Enables the various low power wakeup parameters. Bit (0) enables power-down wakeup, bit (1) enables self-refresh wakeup, bit (2) enables self-refresh with memory and controller clock gating wakeup, bit (3) is reserved and bit (4) enables the LPI timer. Set each bit to 1 to enable.'''),
                        csr_reg_field_desc('lpi_timer_wakeup',          width = 8, reset = 0, comments = '''\
Defines the DFI tLP_WAKEUP timing parameter (in DFI clocks) to be driven when the LPI timer expires.'''),
                        csr_reg_field_desc('lpi_sr_mcclk_gate_wakeup',  width = 8, reset = 0, comments = '''\
Defines the DFI tLP_WAKEUP timing parameter (in DFI clocks) to be driven when memory is in selfrefresh with memory and controller clock gating.''')]))
            elif (i == 143):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('lpi_wakeup_timeout',  width = 16, reset = 0, comments = '''\
Defines the LPI timeout time, the maximum cycles between a dfi_lp_req de-assertion and a dfi_lp_ack de-assertion. If this value is exceeded, an interrupt will occur.'''),
                        csr_reg_field_desc('lpi_timer_count',     width = 16, reset = 0, comments = '''\
Defines the LPI timer count.''')]))
            elif (i == 144):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('lp_auto_entry_en',  width = 8, reset = 0, comments = '''\
Enable auto entry into each of the low power states when the associated idle timer expires. Bit (0) controls power-down, bit (1) controls self-refresh, and bit (2) controls self-refresh with memory and controller clock gating. Set each bit to 1 to enable.'''),
                        csr_reg_field_desc('lp_arb_state',      width = 8, reset = 0, access = 'RO', comments = '''\
Reports on the state of the arbiter.  Bits (2:0) indicate which interface has control of the low power control module and bit (3) indicates if the software programmable interface has an active lock on the arbiter.  For bits (2:0), value of 0 indicates module is idle, value of 1 indicates software programmable interface is in control, value of 2 indicates external pin interface is in control, value of 3 indicates automatic interface is in control, value of 4 indicates dynamic power control per chip select interface is in control, and value of 5 indicates that the controller is in control.'''),
                        csr_reg_field_desc('lp_state',          width = 8, reset = 0, access = 'RO', comments = '''\
Low power state status parameter.  Bits (4:0) indicate the current low power state and bit (5) set indicates that status bits are valid.'''),
                        csr_reg_field_desc('tdfi_lp_resp',      width = 8, reset = 0, comments = '''\
Defines the DFI tLP_RESP timing parameter (in DFI clocks), the maximum cycles between a dfi_lp_req assertion and a dfi_lp_ack assertion.''')]))
            elif (i == 145):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('lp_auto_pd_idle',      width = 16, reset = 0, comments = '''\
Defines the idle time until the controller will place memory in active power-down.'''),
                        csr_reg_field_desc('lp_auto_mem_gate_en',  width = 8, reset = 0, comments = '''\
Enable memory clock gating when entering a low power state via the auto low power counters. Bit (0) controls power-down, and bit (1) controls self-refresh. Set each bit to 1 to enable.'''),
                        csr_reg_field_desc('lp_auto_exit_en',      width = 8, reset = 0, comments = '''\
Enable auto exit from each of the low power states when a read or write command enters the command queue. Bit (0) controls power-down, bit (1) controls selfrefresh, and bit (2) controls selfrefresh with memory and controller clock gating. Set each bit to 1 to enable.''')]))
            elif (i == 146):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('tdfi_dram_clk_enable',    width = 8, reset = 0, comments = '''\
Defines the DFI tDRAM_CLK_ENABLE timing parameter (in DFI clocks), the delay between a dfi_dram_clk_disable de-assertion and the memory clock enable.'''),
                        csr_reg_field_desc('tdfi_dram_clk_disable',   width = 8, reset = 0, comments = '''\
Defines the DFI tDRAM_CLK_DISABLE timing parameter (in DFI clocks), the delay between a dfi_dram_clock_disable assertion and the memory clock disable.'''),
                        csr_reg_field_desc('lp_auto_sr_mc_gate_idle', width = 8, reset = 0, comments = '''\
Number of long count sequences until the controller will place memory in self-refresh with controller and memory clock gating.'''),
                        csr_reg_field_desc('lp_auto_sr_idle',         width = 8, reset = 0, comments = '''\
Number of long count sequences until the controller will place memory in self-refresh.''')]))
        
        cfg_int_mask = self.regs['cfg_regs_51'].int_mask
        cfg_int_status = self.regs['cfg_regs_49'].int_status
        cfg_int_ack = self.regs['cfg_regs_136'].int_ack

        #int_status clear
        with when(cfg_int_ack != 0):
            cfg_int_status /= ~cfg_int_ack & cfg_int_status

        cfg_cke_delay = self.regs['cfg_regs_24'].cke_delay
        cfg_cke_status = self.regs['cfg_regs_104'].cke_status

        cfg_zq_in_progress = self.regs['cfg_regs_41'].zq_in_progress

        cfg_write_modereg = self.regs['cfg_regs_25'].write_modereg
        cfg_start = self.regs['cfg_regs_0'].start

        cfg_bstlen = self.regs['cfg_regs_18'].bstlen[2:0]
        cfg_dfi_bstlen = (cfg_bstlen - 1)[2:0]

        cfg_max_cs_reg = self.regs['cfg_regs_1'].max_cs_reg
        cfg_max_col_reg = self.regs['cfg_regs_1'].max_col_reg
        cfg_max_row_reg = self.regs['cfg_regs_1'].max_row_reg

        cfg_reg_dimm_enable = self.regs['cfg_regs_18'].reg_dimm_enable
        cfg_wrlat_adj = self.regs['cfg_regs_112'].wrlat_adj
        self.cfg_tdfi_phy_wrlat = self.regs['cfg_regs_105'].tdfi_phy_wrlat
        self.cfg_tdfi_phy_wrdata = self.regs['cfg_regs_128'].tdfi_phy_wrdata

        cfg_rdlat_adj = self.regs['cfg_regs_112'].rdlat_adj
        self.cfg_tdfi_rddata_en = self.regs['cfg_regs_106'].tdfi_rddata_en
        cfg_odt_en = self.regs['cfg_regs_68'].odt_en
        cfg_todth_rd = self.regs['cfg_regs_68'].todth_rd
        cfg_todth_wr = self.regs['cfg_regs_68'].todth_wr

        cfg_ap = self.regs['cfg_regs_17'].ap
        self.cfg_aprebit = self.regs['cfg_regs_42'].aprebit

        cfg_mrs = (
            self.regs['cfg_regs_26'].mr0_data_0,
            self.regs['cfg_regs_27'].mr1_data_0,
            self.regs['cfg_regs_27'].mr2_data_0,
            self.regs['cfg_regs_28'].mr3_data_0)

        cfg_ddr_bl = 1 << cfg_bstlen
        cfg_ddr_dfi_bl = cfg_ddr_bl >> 1

        cfg_tref_enable = self.regs['cfg_regs_19'].tref_enable
        cfg_arefresh = self.regs['cfg_regs_19'].arefresh
        cfg_tref = self.regs['cfg_regs_20'].tref
        cfg_trfc = self.regs['cfg_regs_20'].trfc
        cfg_tccd = self.regs['cfg_regs_12'].tccd
        cfg_cl = self.regs['cfg_regs_11'].caslat_lin >> 1
        cfg_al = self.regs['cfg_regs_12'].additive_lat
        cfg_rl = cfg_cl + cfg_al
        cfg_wl = self.regs['cfg_regs_12'].wrlat
        cfg_twr = self.regs['cfg_regs_17'].twr
        cfg_wl_bl_twr = cfg_wl + cfg_ddr_dfi_bl + cfg_twr
        cfg_cwl = cfg_mrs[2][5:3] + self.p.ddr_CWL_MIN
        cfg_trst_pwron = self.regs['cfg_regs_8'].trst_pwron
        cfg_tcke_inactive = self.regs['cfg_regs_9'].cke_inactive
        cfg_txpr = mux(
            self.regs['cfg_regs_23'].txsnr > 5,
            self.regs['cfg_regs_23'].txsnr,
            5)
        cfg_zqinit = self.regs['cfg_regs_37'].zqinit
        cfg_zqcs = self.regs['cfg_regs_38'].zqcs
        cfg_zqcl = self.regs['cfg_regs_38'].zqcl
        cfg_tmrd = self.regs['cfg_regs_14'].tmrd
        cfg_tdll = self.regs['cfg_regs_11'].tdll
        cfg_trcd = self.regs['cfg_regs_16'].trcd
        cfg_twtr = self.regs['cfg_regs_13'].twtr
        cfg_trrd = self.regs['cfg_regs_13'].trrd
        cfg_tras_min = self.regs['cfg_regs_13'].tras_min
        cfg_tras_max = self.regs['cfg_regs_15'].tras_max
        cfg_trtp = self.regs['cfg_regs_14'].trtp
        cfg_al_trtp = cfg_al + cfg_trtp
        cfg_trp = self.regs['cfg_regs_14'].trp
        cfg_tfaw = self.regs['cfg_regs_14'].tfaw
        cfg_trp_ab = self.regs['cfg_regs_18'].trp_ab
        cfg_twc2rc = cfg_wl + cfg_ddr_dfi_bl + cfg_twtr #write cmd to read cmd delay
        cfg_trc2wc = cfg_rl + cfg_tccd + 2 - cfg_wl #write cmd to read cmd delay
        cfg_dll_rst_adj_dly = self.regs['cfg_regs_105'].dll_rst_adj_dly
        cfg_dll_rst_delay = self.regs['cfg_regs_105'].dll_rst_delay
        self.cfg_odt_rd_delay = cfg_cl - cfg_cwl
        #}}}

        ####
        #common const values
        const_dfi_data_w = self.io.phy_dfi.wrdata.wrdata.get_w()
        self.const_dfi_data_bytes = const_dfi_data_w//8
        const_ddr_burst_bytes_max = (
            self.p.dfi_bl_max << log2_ceil(self.const_dfi_data_bytes))
        self.const_ddr_burst_size_max = log2_ceil(const_ddr_burst_bytes_max)
        const_ddr_data_w = const_dfi_data_w//2
        const_ddr_data_bytes = const_ddr_data_w//8
        const_ddr_col_addr_bits = self.io.phy_dfi.control.p.col_bits
        const_ddr_bank_addr_bits = self.io.phy_dfi.control.p.ba_bits
        const_ddr_row_addr_bits = self.io.phy_dfi.control.p.row_bits
        const_ddr_cs_addr_bits = self.io.phy_dfi.control.p.cs_bits
        const_max_bank_num = 2**const_ddr_bank_addr_bits
        const_queue_ll_num = const_max_bank_num//2

        ddr_burst_bytes = cfg_ddr_dfi_bl << log2_ceil(self.const_dfi_data_bytes)
        ddr_burst_size = cfg_dfi_bstlen + log2_ceil(self.const_dfi_data_bytes)

        def bank2ll_map(bank):
            return bank[log2_ceil(const_queue_ll_num) - 1 : 0];

        def get_bank_bits_from_addr(addr):
            msb = (
                const_ddr_col_addr_bits + 
                log2_ceil(const_ddr_data_bytes) + 
                const_ddr_bank_addr_bits - 
                1)
            lsb = const_ddr_col_addr_bits + log2_ceil(const_ddr_data_bytes)
            return addr[msb:lsb]

        def get_ll_bits_from_addr(addr):
            return bank2ll_map(get_bank_bits_from_addr(addr))


        #memory write/read request's header info
        #fifo to store header info, better or ddr_cmd_buffer's enqueue side's timing
        #writes' push at eop
        mem_req_cmd_fifo = queue(
            'mem_req_cmd_fifo',
            gen = lambda _: zqh_ddr_mc_mem_req_info(
                _,
                addr_bits = self.p.addr_bits,
                #tmp data_bits = self.p.data_bits,
                size_bits = self.p.size_bits,
                token_bits = self.p.token_bits),
            entries = 2)
        mem_req_cmd_fifo.io.enq.valid /= 0
        mem_req_cmd_fifo.io.deq.ready /= 0

        #memory write request's data
        mem_req_data_buffer = queue_ll(
            'mem_req_data_buffer',
            gen = lambda _: zqh_ddr_mc_mem_req_data_ll(
                _,
                data_bits = self.p.data_bits,
                bank_bits = const_ddr_bank_addr_bits),
            get_tag = lambda _: bank2ll_map(_.bank),
            ll_num = const_queue_ll_num,
            entries = self.p.req_data_buffer_entries)
        mem_req_data_buffer.io.enq.valid /= 0
        #tmp mem_req_data_buffer.io.enq.bits /= self.io.mem.req.bits
        mem_req_data_buffer.io.enq.bits.bank /= get_bank_bits_from_addr(self.io.mem.req.bits.addr)
        mem_req_data_buffer.io.enq.bits.data /= self.io.mem.req.bits.data
        for i in range(const_queue_ll_num):
            mem_req_data_buffer.io.deq[i].ready /= 0

        #memory request transacton split into cmd and data
        mem_req_cmd_fifo.io.enq.bits /= self.io.mem.req.bits
        mem_req_data_addr_bank = (
            self.io.mem.req.bits.addr >> (
                const_ddr_col_addr_bits +
                log2_ceil(const_ddr_data_bytes)))[const_ddr_bank_addr_bits -1 : 0]
        self.io.mem.req.ready /= 0
        with when(self.io.mem.req.bits.write):
            #write request should wait both mem_req_cmd_fifo and 
            #mem_req_data_buffer has space
            #if mem_req_cmd_fifo has no space, 
            #data should not send to mem_req_data_buffer
            mem_req_data_buffer.io.enq.valid /= (
                self.io.mem.req.valid & mem_req_cmd_fifo.io.enq.ready)
            mem_req_cmd_fifo.io.enq.valid /= (
                self.io.mem.req.valid &
                self.io.mem.req.bits.eop &
                mem_req_data_buffer.io.enq.ready)
            self.io.mem.req.ready /= (
                mem_req_data_buffer.io.enq.ready & mem_req_cmd_fifo.io.enq.ready)
        with other():
            mem_req_cmd_fifo.io.enq.valid /= self.io.mem.req.valid
            self.io.mem.req.ready /= mem_req_cmd_fifo.io.enq.ready

        #memory write request's response buffer
        mem_wr_resp_buffer = queue(
            'mem_wr_resp_buffer',
            gen = lambda _: zqh_ddr_mc_mem_resp(
                _,
                data_bits = self.p.data_bits,
                size_bits = self.p.size_bits,
                token_bits = self.p.token_bits,
                bank_bits = const_ddr_bank_addr_bits),
            entries = self.p.cmd_buffer_entries)
        mem_wr_resp_buffer.io.enq.valid /= 0
        mem_wr_resp_buffer.io.deq.ready /= 0
        mem_wr_resp_buffer_deq_fire_any = mem_wr_resp_buffer.io.deq.fire()

        #data response fifo for timing
        mem_rd_resp_fifo = queue(
            'mem_rd_resp_fifo',
            gen = lambda _: zqh_ddr_mc_mem_resp(
                _,
                data_bits = self.p.data_bits,
                size_bits = self.p.size_bits,
                token_bits = self.p.token_bits),
            entries = 2)

        #memory read request's response buffer
        #group in bank
        mem_rd_resp_buffer = queue_ll(
            'mem_rd_resp_buffer',
            gen = lambda _: zqh_ddr_mc_mem_resp(
                _,
                data_bits = self.p.data_bits,
                size_bits = self.p.size_bits,
                token_bits = self.p.token_bits,
                bank_bits = const_ddr_bank_addr_bits),
            get_tag = lambda _: bank2ll_map(_.bank),
            ll_num = const_queue_ll_num,
            entries = self.p.resp_data_buffer_entries)
        mem_rd_resp_buffer.io.enq.valid /= 0
        for i in range(const_queue_ll_num):
            mem_rd_resp_buffer.io.deq[i].ready /= 0

        #read response's each bank's artitriaton
        #read response has higher priority and should not have inerleave
        mem_rd_resp_buffer_arbiter_lock = reg_r('mem_rd_resp_buffer_arbiter_lock')
        mem_rd_resp_buffer_arbiter_reg = reg_r(
            'mem_rd_resp_buffer_arbiter_reg',
            w = const_queue_ll_num)
        mem_rd_resp_buffer_deq_valid_map = list(map(
            lambda _: mem_rd_resp_buffer.io.deq[_].valid,
            range(const_queue_ll_num)))
        mem_rd_resp_buffer_deq_valid_mask_map = list(map(
            lambda _: mux(
                mem_rd_resp_buffer_arbiter_lock,
                mem_rd_resp_buffer_deq_valid_map[_] & mem_rd_resp_buffer_arbiter_reg[_],
                mem_rd_resp_buffer_deq_valid_map[_]),
            range(const_queue_ll_num)))
        mem_rd_resp_buffer_deq_valid_any = reduce(
            lambda a,b:a|b, 
            mem_rd_resp_buffer_deq_valid_map)
        mem_rd_resp_buffer_deq_fire_map = list(map(
            lambda _: mem_rd_resp_buffer.io.deq[_].fire(),
            range(const_queue_ll_num)))
        mem_rd_resp_buffer_deq_fire_any = reduce(
            lambda a,b:a|b,
            mem_rd_resp_buffer_deq_fire_map)
        mem_rd_resp_buffer_arbiter_sch_en = bits(
            'mem_rd_resp_buffer_arbiter_sch_en',
            init = 0)
        mem_rd_resp_buffer_arbiter = rr_arbiter_ctrl(
            mem_rd_resp_buffer_deq_valid_mask_map,
            mem_rd_resp_buffer_arbiter_sch_en)
        mem_rd_resp_buffer_arbiter_sel = bits(
            'mem_rd_resp_buffer_arbiter_sel',
            w = const_queue_ll_num, 
            init = mem_rd_resp_buffer_arbiter)
        with when(mem_rd_resp_buffer_arbiter_lock):
            mem_rd_resp_buffer_arbiter_sel /= mem_rd_resp_buffer_arbiter_reg
            with when(
                mem_rd_resp_buffer_deq_fire_any & 
                mem_rd_resp_buffer.io.deq_dp_bits.last):
                mem_rd_resp_buffer_arbiter_lock /= 0
        with other():
            with when(
                mem_rd_resp_buffer_deq_valid_any & 
                ~mem_rd_resp_buffer.io.deq_dp_bits.last):
                mem_rd_resp_buffer_arbiter_lock /= 1
                mem_rd_resp_buffer_arbiter_reg /= mem_rd_resp_buffer_arbiter
        mem_rd_resp_buffer_arbiter_sch_en /= (
            mem_rd_resp_fifo.io.enq.ready & mem_rd_resp_buffer.io.deq_dp_bits.last)
        for i in range(const_queue_ll_num):
            mem_rd_resp_buffer.io.deq[i].ready /= (
                mem_rd_resp_buffer_arbiter_sel[i] & mem_rd_resp_fifo.io.enq.ready)

        #read's response has higher priority. TBD, change to rr_arbiter may be better
        with when(mem_rd_resp_buffer_arbiter_lock):
            mem_wr_resp_buffer.io.deq.ready /= 0
        with other():
            mem_wr_resp_buffer.io.deq.ready /= (
                ~mem_rd_resp_buffer_deq_valid_any & mem_rd_resp_fifo.io.enq.ready)


        mem_rd_resp_valid = reduce(
            lambda a,b:a|b, list(map(
                lambda _: (
                    mem_rd_resp_buffer_deq_valid_map[_] & 
                    mem_rd_resp_buffer_arbiter_sel[_]),
                range(const_queue_ll_num))))
        mem_wr_resp_valid = mem_wr_resp_buffer.io.deq.valid

        mem_rd_resp_fifo.io.enq.valid /= 0
        with when(mem_rd_resp_buffer_arbiter_lock | mem_rd_resp_valid):
            mem_rd_resp_fifo.io.enq.valid /= mem_rd_resp_valid
            mem_rd_resp_fifo.io.enq.bits /= mem_rd_resp_buffer.io.deq_dp_bits
        with other():
            mem_rd_resp_fifo.io.enq.valid /= mem_wr_resp_valid
            mem_rd_resp_fifo.io.enq.bits /= mem_wr_resp_buffer.io.deq.bits

        self.io.mem.resp /= mem_rd_resp_fifo.io.deq


        #dfi interface isolate with register
        self.phy_dfi_if_reg = zqh_ddr_phy_dfi_io('phy_dfi_if_reg').as_reg()
        self.io.phy_dfi /= self.phy_dfi_if_reg

        #refresh control
        dfi_refresh_en = reg_r('dfi_refresh_en')
        dfi_refresh_cycle_cnt = reg_r('dfi_refresh_cycle_cnt', w = 32)
        dfi_refresh_cmd_need = bits('dfi_refresh_cmd_need', init = 0)
        dfi_refresh_cmd_finish = bits('dfi_refresh_cmd_finish', init = 0)
        with when(cfg_tref_enable & dfi_refresh_en):
            with when(cfg_arefresh):
                dfi_refresh_cycle_cnt /= cfg_tref
            with elsewhen(dfi_refresh_cmd_finish):
                dfi_refresh_cycle_cnt /= 0
            with other():
                dfi_refresh_cycle_cnt /= dfi_refresh_cycle_cnt + 1
            with when(dfi_refresh_cycle_cnt > cfg_tref):
                dfi_refresh_cmd_need /= 1
        with other():
            dfi_refresh_cycle_cnt /= 0


        ####
        #ddr cmd gen, don't care timing
        #grouped in banks
        ddr_cmd_buffer = queue_ll(
            'ddr_cmd_buffer',
            gen = lambda _: zqh_ddr_mc_ddr_dfi_cmd(
                _,
                addr_bits = self.p.addr_bits,
                #tmp data_bits = self.p.data_bits,
                size_bits = self.p.size_bits,
                token_bits = self.p.token_bits),
            get_tag = lambda _: get_ll_bits_from_addr(_.addr),
            ll_num = const_queue_ll_num,
            entries = self.p.cmd_buffer_entries)
        ddr_cmd_buffer.io.enq.valid /= 0
        for i in range(const_queue_ll_num):
            ddr_cmd_buffer.io.deq[i].ready /= 0

        #the arbitrated success bank's cmd will be push into a tmp fifo
        #better for backend timming
        ddr_cmd_fifo = queue(
            'ddr_cmd_fifo',
            gen = lambda _: zqh_ddr_mc_ddr_dfi_cmd(
                _,
                addr_bits = self.p.addr_bits,
                #tmp data_bits = self.p.data_bits,
                size_bits = self.p.size_bits,
                token_bits = self.p.token_bits),
            entries = 2)
        ddr_cmd_fifo.io.enq.valid /= 0
        ddr_cmd_fifo.io.deq.ready /= 0


        mem_req_cmd_num_bytes = (1 << mem_req_cmd_fifo.io.deq.bits.size)[
            self.p.max_req_size:0]
        mem_req_cmd_size_bl_less = mem_req_cmd_fifo.io.deq.bits.size < ddr_burst_size
        mem_req_cmd_num_bytes_h = mem_req_cmd_num_bytes[
            mem_req_cmd_num_bytes.get_w() - 1 : log2_ceil(self.const_dfi_data_bytes)]
        mem_req_cmd_num_dfi_flits = mux(
            mem_req_cmd_size_bl_less,
            cfg_ddr_dfi_bl,
            mem_req_cmd_num_bytes_h)
        mem_req_cmd_addr_bl_size_mask = (
            mem_req_cmd_fifo.io.deq.bits.addr &
            ~bits(init = ddr_burst_bytes - 1, w = self.p.addr_bits))
        mem_req_cmd_addr_bank = (
            mem_req_cmd_addr_bl_size_mask >>
            (const_ddr_col_addr_bits + log2_ceil(const_ddr_data_bytes)))[
                const_ddr_bank_addr_bits -1 : 0]
        mem_req_cmd_addr_row = (
            mem_req_cmd_addr_bl_size_mask >>
            (
                const_ddr_bank_addr_bits + 
                const_ddr_col_addr_bits + 
                log2_ceil(const_ddr_data_bytes)))[const_ddr_row_addr_bits - 1 : 0]


        #each bank's status will be keeped
        (e_bank_inactive, e_bank_active) = range(2)
        ddr_bank_status = vec(
            'ddr_bank_status',
            gen = reg_rs,
            n = const_max_bank_num,
            w = 2, 
            rs = e_bank_inactive)
        ddr_bank_status_update = bits('ddr_bank_status_update', init = 0)
        ddr_bank_status_update_v = bits('ddr_bank_status_update_v', w = 2, init = 0)
        ddr_bank_status_reset_all = bits('ddr_bank_status_reset_all', init = 0)
        with when(ddr_bank_status_update):
            ddr_bank_status(mem_req_cmd_addr_bank, ddr_bank_status_update_v)
        with when(ddr_bank_status_reset_all):
            for i in range(len(ddr_bank_status)):
                ddr_bank_status[i] /= e_bank_inactive

        #each active bank's active row
        ddr_bank_row_map = vec(
            'ddr_bank_row_map', 
            gen = reg, 
            n = const_max_bank_num, 
            w = const_ddr_row_addr_bits)

        #ddr cmd generate's control FSM
        (
            s_ddr_ready, s_ddr_active_pre, s_ddr_active, s_ddr_cmd,
            s_ddr_refresh_pre, s_ddr_refresh, s_ddr_refresh_ack) = range(7)
        ddr_cmd_state = reg_rs('ddr_cmd_state', w = 3, rs = s_ddr_ready)
        ddr_cmd_num = mem_req_cmd_num_dfi_flits >> cfg_dfi_bstlen
        ddr_cmd_cnt = reg_r('ddr_cmd_cnt', w = ddr_cmd_num.get_w())
        ddr_cmd_state_active_pre_done = bits('ddr_cmd_state_active_pre_done', init = 0)
        ddr_cmd_state_active_done = bits('ddr_cmd_state_active_done', init = 0)
        ddr_cmd_state_cmd_done = bits('ddr_cmd_state_cmd_done', init = 0)
        ddr_cmd_state_refresh_pre_done = bits('ddr_cmd_state_refresh_pre_done', init = 0)
        ddr_cmd_state_refresh_done = bits('ddr_cmd_state_refresh_done', init = 0)
        ddr_cmd_state_refresh_ack_done = bits('ddr_cmd_state_refresh_ack_done', init = 0)
        ddr_cmd_last = bits('ddr_cmd_last', init = 0)
        ddr_cmd_buffer_all_empty = ddr_cmd_buffer.io.count == 0
        with when(ddr_cmd_state == s_ddr_ready):
            with when(dfi_refresh_cmd_need):
                #refresh must wait all pending cmd done
                with when(ddr_cmd_buffer_all_empty):
                    with when(cfg_ap):
                        ddr_cmd_state /= s_ddr_refresh
                    with other():
                        ddr_cmd_state /= s_ddr_refresh_pre
            with other():
                with when(mem_req_cmd_fifo.io.deq.valid):
                    with when(ddr_bank_status[mem_req_cmd_addr_bank] == e_bank_inactive):
                        ddr_cmd_state /= s_ddr_active
                    with other():
                        #same row access, no need issue active
                        with when(
                            ddr_bank_row_map[mem_req_cmd_addr_bank] == 
                            mem_req_cmd_addr_row):
                            ddr_cmd_state /= s_ddr_cmd
                            ddr_cmd_cnt /= 0
                        with other():
                            ddr_cmd_state /= s_ddr_active_pre
        with when(ddr_cmd_state == s_ddr_active_pre):
            with when(ddr_cmd_state_active_pre_done):
                ddr_cmd_state /= s_ddr_active
        with when(ddr_cmd_state == s_ddr_active):
            with when(ddr_cmd_state_active_done):
                ddr_cmd_state /= s_ddr_cmd
                ddr_cmd_cnt /= 0
        with when(ddr_cmd_state == s_ddr_cmd):
            with when(ddr_cmd_state_cmd_done):
                ddr_cmd_state /= s_ddr_ready
        with when(ddr_cmd_state == s_ddr_refresh_pre):
            with when(ddr_cmd_state_refresh_pre_done):
                ddr_cmd_state /= s_ddr_refresh
        with when(ddr_cmd_state == s_ddr_refresh):
            with when(ddr_cmd_state_refresh_done):
                ddr_cmd_state /= s_ddr_refresh_ack
        with when(ddr_cmd_state == s_ddr_refresh_ack):
            with when(ddr_cmd_state_refresh_ack_done):
                ddr_cmd_state /= s_ddr_ready


        #ddr cmd code enum
        (
            e_ddr_cmd_active, e_ddr_cmd_write, e_ddr_cmd_read, e_ddr_cmd_precharge,
            e_ddr_cmd_precharge_all, e_ddr_cmd_refresh) = range(6)
        mem_req_cmd_addr_post = bits(
            'mem_req_cmd_addr_post', 
            w = self.p.addr_bits, 
            init = mem_req_cmd_fifo.io.deq.bits.addr)
        ddr_cmd = bits('ddr_cmd', w = ddr_cmd_buffer.io.enq.bits.cmd.get_w(), init = 0)
        mem_req_cmd_addr_bank_map = bin2oh(mem_req_cmd_addr_bank)
        ddr_cmd_buffer_bank_map = bits(
            'ddr_cmd_buffer_bank_map',
            w = const_max_bank_num, 
            init = mem_req_cmd_addr_bank_map)

        ddr_cmd_buffer_enq_valid = bits('ddr_cmd_buffer_enq_valid', init = 0)
        ddr_cmd_buffer.io.enq.valid /= ddr_cmd_buffer_enq_valid
        ddr_cmd_buffer.io.enq.bits /= mem_req_cmd_fifo.io.deq.bits
        ddr_cmd_buffer.io.enq.bits.cmd /= ddr_cmd
        ddr_cmd_buffer.io.enq.bits.addr /= mem_req_cmd_addr_post
        ddr_cmd_buffer.io.enq.bits.last /= ddr_cmd_last
        with when(~mem_req_cmd_size_bl_less):
            ddr_cmd_buffer.io.enq.bits.size /= ddr_burst_size
        ddr_cmd_buffer_enq_bank_fire_any = ddr_cmd_buffer.io.enq.fire()

        with when(ddr_cmd_state == s_ddr_active_pre):
            ddr_cmd_buffer_enq_valid /= 1
            ddr_cmd /= e_ddr_cmd_precharge
            with when(ddr_cmd_buffer_enq_bank_fire_any):
                ddr_cmd_state_active_pre_done /= 1

        with when(ddr_cmd_state == s_ddr_active):
            ddr_bank_status_update /= 1
            ddr_bank_status_update_v /= e_bank_active
            ddr_bank_row_map(mem_req_cmd_addr_bank, mem_req_cmd_addr_row)
            ddr_cmd_buffer_enq_valid /= 1
            ddr_cmd /= e_ddr_cmd_active
            with when(ddr_cmd_buffer_enq_bank_fire_any):
                ddr_cmd_state_active_done /= 1

        with when(ddr_cmd_state == s_ddr_cmd):
            ddr_cmd_buffer_enq_valid /= 1
            with when(cfg_ap & (ddr_cmd_cnt == ddr_cmd_num)):
                ddr_cmd /= e_ddr_cmd_precharge
                ddr_bank_status_update /= 1
                ddr_bank_status_update_v /= e_bank_inactive
            with other():
                with when(mem_req_cmd_fifo.io.deq.bits.write):
                    ddr_cmd /= e_ddr_cmd_write
                with other():
                    ddr_cmd /= e_ddr_cmd_read
                mem_req_cmd_addr_post /= (
                    mem_req_cmd_fifo.io.deq.bits.addr + (ddr_cmd_cnt << ddr_burst_size))
            with when(ddr_cmd_buffer_enq_bank_fire_any):
                ddr_cmd_cnt /= ddr_cmd_cnt + 1
                with when(ddr_cmd_cnt == ddr_cmd_num - 1):
                    ddr_cmd_last /= 1
                    with when(~cfg_ap):
                        ddr_cmd_state_cmd_done /= 1
                with when(ddr_cmd_cnt == ddr_cmd_num):
                    ddr_cmd_state_cmd_done /= 1

        with when(ddr_cmd_state == s_ddr_refresh_pre):
            ddr_cmd_buffer_bank_map /= 1 #TBD, refresh use bank0
            mem_req_cmd_addr_post /= 0
            ddr_bank_status_reset_all /= 1
            ddr_cmd_buffer_enq_valid /= 1
            ddr_cmd /= e_ddr_cmd_precharge_all
            with when(ddr_cmd_buffer_enq_bank_fire_any):
                ddr_cmd_state_refresh_pre_done /= 1

        with when(ddr_cmd_state == s_ddr_refresh):
            ddr_cmd_buffer_bank_map /= 1 #TBD, refresh use bank0
            mem_req_cmd_addr_post /= 0
            ddr_cmd_buffer_enq_valid /= 1
            ddr_cmd /= e_ddr_cmd_refresh
            with when(ddr_cmd_buffer_enq_bank_fire_any):
                ddr_cmd_state_refresh_done /= 1

        with when(ddr_cmd_state == s_ddr_refresh_ack):
            #wait this flush cmd is accept
            with when(ddr_cmd_buffer_all_empty):
                ddr_cmd_state_refresh_ack_done /= 1
        dfi_refresh_cmd_finish /= ddr_cmd_state_refresh_ack_done

        with when(ddr_cmd_state == s_ddr_cmd):
            with when(ddr_cmd_state_cmd_done):
                mem_req_cmd_fifo.io.deq.ready /= ddr_cmd_buffer.io.enq.ready


        #ddr cmd's arbitrition and the arbitrited cmd will be push into a tmp fifo
        ddr_cmd_buffer_deq_valid_map = list(map(
            lambda _: ddr_cmd_buffer.io.deq[_].valid,
            range(const_queue_ll_num)))
        ddr_cmd_buffer_deq_valid_any = reduce(lambda a,b: a|b, ddr_cmd_buffer_deq_valid_map)
        ddr_cmd_buffer_arbiter = rr_arbiter_ctrl(
            ddr_cmd_buffer_deq_valid_map,
            ddr_cmd_fifo.io.enq.ready)
        ddr_cmd_fifo.io.enq.bits /= ddr_cmd_buffer.io.deq_dp_bits
        ddr_cmd_fifo.io.enq.valid /= ddr_cmd_buffer_deq_valid_any
        for i in range(const_queue_ll_num):
            ddr_cmd_buffer.io.deq[i].ready /= (
                ddr_cmd_buffer_arbiter[i] & ddr_cmd_fifo.io.enq.ready)

        ddr_cmd_num_bytes = (1 << ddr_cmd_fifo.io.deq.bits.size)[
            self.const_ddr_burst_size_max:0]
        ddr_cmd_num_bytes_h = ddr_cmd_num_bytes[
            ddr_cmd_num_bytes.get_w() - 1 : log2_ceil(self.const_dfi_data_bytes)]
        ddr_cmd_num_effect_flits = mux(
            ddr_cmd_fifo.io.deq.bits.size < log2_ceil(self.const_dfi_data_bytes),
            1, ddr_cmd_num_bytes_h)
        ddr_cmd_num_dfi_flits = cfg_ddr_dfi_bl

        #address split in bank, row, col
        ddr_cmd_addr_bl_size_mask = (
            ddr_cmd_fifo.io.deq.bits.addr &
            ~bits(init = ddr_burst_bytes - 1, w = self.p.addr_bits))
        ddr_cmd_addr_col = (
            ddr_cmd_addr_bl_size_mask >> 
            log2_ceil(const_ddr_data_bytes))[const_ddr_col_addr_bits -1 : 0]
        ddr_cmd_addr_bank = (
            ddr_cmd_addr_bl_size_mask >> 
            (const_ddr_col_addr_bits + log2_ceil(const_ddr_data_bytes)))[
                const_ddr_bank_addr_bits -1 : 0]
        ddr_cmd_addr_row = (
            ddr_cmd_addr_bl_size_mask >>
            (
                const_ddr_bank_addr_bits + 
                const_ddr_col_addr_bits + 
                log2_ceil(const_ddr_data_bytes)))[const_ddr_row_addr_bits - 1 : 0]


        #need keep the write cmd info after ddr write cmd send
        #after cas delay, the write data send will use the fly info
        #cmd -> cmd gap is tccd, so 8 entry depth is enough to keep tccd*8 data latency
        ddr_cmd_pipe_wr_info_fifo = queue(
            'ddr_cmd_pipe_wr_info_fifo',
            gen = lambda _: zqh_ddr_mc_mem_req_info(
                _,
                addr_bits = self.p.addr_bits,
                #tmp data_bits = self.p.data_bits,
                size_bits = self.p.size_bits,
                token_bits = self.p.token_bits),
            entries = self.p.pipe_wr_info_fifo_depth)
        ddr_cmd_pipe_wr_info_fifo.io.enq.valid /= 0
        ddr_cmd_pipe_wr_info_fifo.io.deq.ready /= 0

        #need keep the write cmd info after ddr write cmd send
        #similar as write's
        #write info and read info maybe need at same cycle for the rddata_valid's latency
        #read and write should use independence info_buffer
        ddr_cmd_pipe_rd_info_fifo = queue(
            'ddr_cmd_pipe_rd_info_fifo',
            gen = lambda _: zqh_ddr_mc_mem_req_info(
                _,
                addr_bits = self.p.addr_bits,
                #tmp data_bits = self.p.data_bits,
                size_bits = self.p.size_bits,
                token_bits = self.p.token_bits),
            entries = self.p.pipe_rd_info_fifo_depth)
        ddr_cmd_pipe_rd_info_fifo.io.enq.valid /= 0
        ddr_cmd_pipe_rd_info_fifo.io.deq.ready /= 0

        #ddr cmd decode for processing
        ddr_cmd_is_active = ddr_cmd_fifo.io.deq.bits.cmd == e_ddr_cmd_active
        ddr_cmd_is_write = ddr_cmd_fifo.io.deq.bits.cmd == e_ddr_cmd_write
        ddr_cmd_is_read = ddr_cmd_fifo.io.deq.bits.cmd == e_ddr_cmd_read
        ddr_cmd_is_precharge = ddr_cmd_fifo.io.deq.bits.cmd == e_ddr_cmd_precharge
        ddr_cmd_is_precharge_all = ddr_cmd_fifo.io.deq.bits.cmd == e_ddr_cmd_precharge_all
        ddr_cmd_is_refresh = ddr_cmd_fifo.io.deq.bits.cmd == e_ddr_cmd_refresh

        #ddr read's response must reserve engough space for it's response data
        #at the cmd sending time
        mem_rd_resp_buffer_credit = reg_rs(
            'mem_rd_resp_buffer_credit',
            w = mem_rd_resp_buffer.io.count.get_w(),
            rs = mem_rd_resp_buffer.p.entries)
        mem_rd_resp_buffer_credit_update_num = bits(
            w = mem_rd_resp_buffer_credit.get_w(),
            init = 0)
        mem_rd_resp_buffer_credit_dec = ddr_cmd_fifo.io.deq.fire() & ddr_cmd_is_read
        mem_rd_resp_buffer_dec_num = ddr_cmd_num_effect_flits.u_ext(
            mem_rd_resp_buffer_credit_update_num.get_w())
        mem_rd_resp_buffer_inc_num = 1
        mem_rd_resp_buffer_credit_update = (
            mem_rd_resp_buffer_credit_dec | mem_rd_resp_buffer_deq_fire_any)
        mem_rd_resp_buffer_credit_update_num /= mux(
                mem_rd_resp_buffer_deq_fire_any,
                1,
                0).u_ext(mem_rd_resp_buffer_credit_update_num.get_w()) - mux(
                    mem_rd_resp_buffer_credit_dec,
                    mem_rd_resp_buffer_dec_num,
                    0)
        with when(mem_rd_resp_buffer_credit_update):
            mem_rd_resp_buffer_credit /= (
                mem_rd_resp_buffer_credit + mem_rd_resp_buffer_credit_update_num)
        mem_rd_resp_buffer_credit_enough = ~(
            mem_rd_resp_buffer_credit < ddr_cmd_num_effect_flits)


        #ddr write's response must reserve engough space for it's response ack
        #at the cmd sending time
        mem_wr_resp_buffer_credit = reg_rs(
            'mem_wr_resp_buffer_credit',
            w = mem_wr_resp_buffer.io.count.get_w(),
            rs = mem_wr_resp_buffer.p.entries)
        mem_wr_resp_buffer_credit_needed = bits(init = 1) 
        mem_wr_resp_buffer_credit_update_num = bits(
            w = mem_wr_resp_buffer_credit.get_w(),
            init = 0)
        mem_wr_resp_buffer_credit_dec = (
            ddr_cmd_fifo.io.deq.fire() & (ddr_cmd_is_write & ddr_cmd_fifo.io.deq.bits.last))
        mem_wr_resp_buffer_credit_update = mem_wr_resp_buffer_credit_dec | mem_wr_resp_buffer_deq_fire_any
        mem_wr_resp_buffer_credit_update_num /= mux(
            mem_wr_resp_buffer_deq_fire_any,
            1,
            0).u_ext(mem_wr_resp_buffer_credit_update_num.get_w()) - mux(
                mem_wr_resp_buffer_credit_dec,
                1,
                0).u_ext(mem_wr_resp_buffer_credit_update_num.get_w())
        with when(mem_wr_resp_buffer_credit_update):
            mem_wr_resp_buffer_credit /= (
                mem_wr_resp_buffer_credit + mem_wr_resp_buffer_credit_update_num)
        mem_wr_resp_buffer_credit_enough = ~(
            mem_wr_resp_buffer_credit < mem_wr_resp_buffer_credit_needed)


        #active, precharge, precharge_all, refresh cmd don't need credit
        #write and read cmd need enough response credit
        ddr_cmd_active_en = ddr_cmd_fifo.io.deq.valid & ddr_cmd_is_active
        ddr_cmd_precharge_en = ddr_cmd_fifo.io.deq.valid & ddr_cmd_is_precharge
        ddr_cmd_precharge_all_en = ddr_cmd_fifo.io.deq.valid & ddr_cmd_is_precharge_all
        ddr_cmd_refresh_en = ddr_cmd_fifo.io.deq.valid & ddr_cmd_is_refresh
        ddr_cmd_wr_en = (
            ddr_cmd_fifo.io.deq.valid &
            ddr_cmd_is_write &
            mem_wr_resp_buffer_credit_enough)
        ddr_cmd_rd_en = (
            ddr_cmd_fifo.io.deq.valid &
            ddr_cmd_is_read &
            mem_rd_resp_buffer_credit_enough)


        ####
        #ddr_phy's dfi interface timing process
        #need some counters to record the delay
        #timing related
        dfi_req_rddata_burst_beat_cnt = reg_r(
            'dfi_req_rddata_burst_beat_cnt',
            w = ddr_cmd_num_dfi_flits.get_w())
        dfi_req_wrdata_burst_beat_cnt = reg_r(
            'dfi_req_wrdata_burst_beat_cnt',
            w = ddr_cmd_num_dfi_flits.get_w())
        dfi_req_cmd_read_done = bits('dfi_req_cmd_read_done', init = 0)
        dfi_req_cmd_write_done = bits('dfi_req_cmd_write_done', init = 0)
        dfi_odt_work = reg_r('dfi_odt_work')
        self.dfi_odt_mask_pipe_set = vec(
            'dfi_odt_mask_pipe_set',
            gen = bits,
            n = self.p.ddr_CL_MAX + self.p.ddr_AL_MAX + 1,
            init = 0)
        self.dfi_odt_mask_pipe = vec(
            'dfi_odt_mask_pipe',
            gen = reg_r,
            n = self.p.ddr_CL_MAX + self.p.ddr_AL_MAX + 1)
        self.dfi_rddata_en_pipe_set = vec(
            'dfi_rddata_en_pipe_set',
            gen = bits,
            n = 2*self.p.ddr_CL_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = self.io.phy_dfi.rddata.rddata_en.get_w(),
            init = 0)
        self.dfi_rddata_en_sop_eop_pipe_set = vec(
            'dfi_rddata_en_sop_eop_pipe_set',
            gen = bits,
            n = 2*self.p.ddr_CL_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = 2,
            init = 0)
        self.dfi_rddata_en_pipe = vec(
            'dfi_rddata_en_pipe',
            gen = reg_r,
            n = 2*self.p.ddr_CL_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = self.io.phy_dfi.rddata.rddata_en.get_w())
        self.dfi_rddata_en_sop_eop_pipe = vec(
            'dfi_rddata_en_sop_eop_pipe',
            gen = reg_r,
            n = 2*self.p.ddr_CL_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = 2)
        self.dfi_wrdata_en_no_latency = bits(
            'dfi_wrdata_en_no_latency',
            w = self.io.phy_dfi.wrdata.wrdata_en.get_w(),
            init = 0)
        self.dfi_wrdata_en_pipe_set = vec(
            'dfi_wrdata_en_pipe_set',
            gen = bits,
            n = 2*self.p.ddr_WR_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = self.io.phy_dfi.wrdata.wrdata_en.get_w(),
            init = 0)
        self.dfi_wrdata_en_pipe = vec(
            'dfi_wrdata_en_pipe',
            gen = reg_r,
            n = 2*self.p.ddr_WR_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = self.io.phy_dfi.wrdata.wrdata_en.get_w())
        self.dfi_wrdata_q_no_latency = bits('dfi_wrdata_q_no_latency', init = 0)
        self.dfi_wrdata_q_sop_eop_no_latency = bits(
            'dfi_wrdata_q_sop_eop_no_latency', w = 2, init = 0)
        self.dfi_wrdata_q_bank_no_latency = bits(
            'dfi_wrdata_q_bank_no_latency', w = const_ddr_bank_addr_bits, init = 0)
        self.dfi_wrdata_q_pipe_set = vec(
            'dfi_wrdata_q_pipe_set',
            gen = bits,
            n = 2*self.p.ddr_WR_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = 1, init = 0)
        self.dfi_wrdata_q_pipe = vec(
            'dfi_wrdata_q_pipe',
            gen = reg_r,
            n = 2*self.p.ddr_WR_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = 1)
        self.dfi_wrdata_q_sop_eop_pipe_set = vec(
            'dfi_wrdata_q_sop_eop_pipe_set',
            gen = bits,
            n = 2*self.p.ddr_WR_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = 2, init = 0)
        self.dfi_wrdata_q_sop_eop_pipe = vec(
            'dfi_wrdata_q_sop_eop_pipe',
            gen = reg_r,
            n = 2*self.p.ddr_WR_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = 2)
        self.dfi_wrdata_q_bank_pipe_set = vec(
            'dfi_wrdata_q_bank_pipe_set',
            gen = bits,
            n = 2*self.p.ddr_WR_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = const_ddr_bank_addr_bits, init = 0)
        self.dfi_wrdata_q_bank_pipe = vec(
            'dfi_wrdata_q_bank_pipe',
            gen = reg,
            n = 2*self.p.ddr_WR_MAX+self.p.ddr_AL_MAX+self.p.ddr_BL_MAX//2 + 1,
            w = const_ddr_bank_addr_bits)

        #ddr_phy dfi timing control FSM
        (s_phy_init       , s_phy_reset        , s_phy_cke      , s_phy_mrs,
         s_phy_zq_cal_init, s_phy_zq_cal_s     , s_phy_rdlvl    , s_phy_wrlvl,
         s_phy_ready      , s_phy_active       , s_phy_write    , s_phy_read,
         s_phy_precharge  , s_phy_precharge_all, s_phy_refresh  , s_phy_self_refresh,
         s_phy_deselect) = range(17)
        phy_state = reg_rs('phy_state', w = 5, rs = s_phy_init)
        cnt0 = reg_r('cnt0', w = 24)
        cnt0_is_0 = cnt0 == 0
        cnt0_dec_en = bits('cnt0_dec_en', init = 0)
        with when(cnt0_dec_en):
            cnt0 /= cnt0 - 1

        #cnt1's are used to record the previous completed cmd's post delay
        cnt1 = vec('cnt1', gen = reg_r, n = const_max_bank_num, w = 10)
        cnt1_sel = cnt1[ddr_cmd_addr_bank]
        cnt1_set_one = bits('cnt1_set_one', init = 0)
        cnt1_set_all = bits('cnt1_set_all', init = 0)
        cnt1_is_full = list(map(
            lambda _: cnt1[_] == value(2**cnt1[_].get_w() - 1),
            range(const_max_bank_num)))
        for i in range(const_max_bank_num):
            with when(~cnt1_is_full[i]):
                cnt1[i] /= cnt1[i] + 1
        with when(cnt1_set_one):
            cnt1(ddr_cmd_addr_bank, 2)
        with when(cnt1_set_all):
            for i in range(const_max_bank_num):
                cnt1[i] /= 2

        odth_rd_block_l = self.p.dfi_bl_max + 2
        odth_rd_block_h = self.p.dfi_bl_max + 2 + cfg_todth_rd
        odth_wr_block_l = cfg_todth_wr

        #four active window counter and block control
        faw_cnt = vec('faw_cnt', gen = reg_r, n = 4, w = cfg_tfaw.get_w())
        faw_cnt_en = vec('faw_cnt_en', gen = reg_r, n = 4, w = 1)
        faw_block = bits('faw_block', init = 0)
        faw_active_issue = bits('faw_active_issue', init = 0)

        #tras counter control
        tras_cnt = reg_r('tras_cnt', w = 8)
        tras_cnt_set = bits('tras_cnt_set', init = 0)
        tras_block = bits('tras_block', init = 0)
        with when(tras_cnt_set):
            tras_cnt /= 2
        with elsewhen(tras_cnt != (2**tras_cnt.get_w() - 1)):
            tras_cnt /= tras_cnt + 1
        tras_block /= tras_cnt < cfg_tras_min


        #record the last completed cmd of each bank
        #cmd current need wait a min latency if needed
        pre_cmd_is_active = vec('pre_cmd_is_active', gen = reg_r, n = const_max_bank_num)
        pre_cmd_is_active_set = bits('pre_cmd_is_active_set', init = 0)
        pre_cmd_is_active_clean = bits('pre_cmd_is_active_clean', init = 0)
        pre_cmd_is_active_reset_all = bits('pre_cmd_is_active_reset_all', init = 0)
        pre_cmd_is_active_any = pre_cmd_is_active.pack().r_or()
        pre_cmd_is_active_sel = pre_cmd_is_active[ddr_cmd_addr_bank]
        with when(pre_cmd_is_active_reset_all):
            for i in range(const_max_bank_num):
                pre_cmd_is_active[i] /= 0
        with elsewhen(pre_cmd_is_active_set | pre_cmd_is_active_clean):
            pre_cmd_is_active(ddr_cmd_addr_bank, pre_cmd_is_active_set)

        pre_cmd_is_write = vec('pre_cmd_is_write', gen = reg_r, n = const_max_bank_num)
        pre_cmd_is_write_set = bits('pre_cmd_is_write_set', init = 0)
        pre_cmd_is_write_clean = bits('pre_cmd_is_write_clean', init = 0)
        pre_cmd_is_write_reset_all = bits('pre_cmd_is_write_reset_all', init = 0)
        pre_cmd_is_write_any = pre_cmd_is_write.pack().r_or()
        pre_cmd_is_write_sel = pre_cmd_is_write[ddr_cmd_addr_bank]
        with when(pre_cmd_is_write_reset_all):
            for i in range(const_max_bank_num):
                pre_cmd_is_write[i] /= 0
        with elsewhen(pre_cmd_is_write_set | pre_cmd_is_write_clean):
            pre_cmd_is_write(ddr_cmd_addr_bank, pre_cmd_is_write_set)

        pre_cmd_is_read = vec('pre_cmd_is_read', gen = reg_r, n = const_max_bank_num)
        pre_cmd_is_read_set = bits('pre_cmd_is_read_set', init = 0)
        pre_cmd_is_read_clean = bits('pre_cmd_is_read_clean', init = 0)
        pre_cmd_is_read_reset_all = bits('pre_cmd_is_read_reset_all', init = 0)
        pre_cmd_is_read_any = pre_cmd_is_read.pack().r_or()
        pre_cmd_is_read_sel = pre_cmd_is_read[ddr_cmd_addr_bank]
        with when(pre_cmd_is_read_reset_all):
            for i in range(const_max_bank_num):
                pre_cmd_is_read[i] /= 0
        with elsewhen(pre_cmd_is_read_set | pre_cmd_is_read_clean):
            pre_cmd_is_read(ddr_cmd_addr_bank, pre_cmd_is_read_set)

        pre_cmd_is_precharge = vec(
            'pre_cmd_is_precharge',
            gen = reg_r, 
            n = const_max_bank_num)
        pre_cmd_is_precharge_set = bits('pre_cmd_is_precharge_set', init = 0)
        pre_cmd_is_precharge_clean = bits('pre_cmd_is_precharge_clean', init = 0)
        pre_cmd_is_precharge_reset_all = bits('pre_cmd_is_precharge_reset_all', init = 0)
        pre_cmd_is_precharge_any = pre_cmd_is_precharge.pack().r_or()
        pre_cmd_is_precharge_sel = pre_cmd_is_precharge[ddr_cmd_addr_bank]
        with when(pre_cmd_is_precharge_reset_all):
            for i in range(const_max_bank_num):
                pre_cmd_is_precharge[i] /= 0
        with elsewhen(pre_cmd_is_precharge_set | pre_cmd_is_precharge_clean):
            pre_cmd_is_precharge(ddr_cmd_addr_bank, pre_cmd_is_precharge_set)

        pre_cmd_is_precharge_all = reg_r('pre_cmd_is_precharge_all')
        pre_cmd_is_precharge_all_set = bits('pre_cmd_is_precharge_all_set', init = 0)
        pre_cmd_is_precharge_all_clean = bits('pre_cmd_is_precharge_all_clean', init = 0)
        with when(pre_cmd_is_precharge_all_set):
            pre_cmd_is_precharge_all /= 1
        with elsewhen(pre_cmd_is_precharge_all_clean):
            pre_cmd_is_precharge_all /= 0

        pre_cmd_is_refresh = reg_r('pre_cmd_is_refresh')
        pre_cmd_is_refresh_set = bits('pre_cmd_is_refresh_set', init = 0)
        pre_cmd_is_refresh_clean = bits('pre_cmd_is_refresh_clean', init = 0)
        with when(pre_cmd_is_refresh_set):
            pre_cmd_is_refresh /= 1
        with elsewhen(pre_cmd_is_refresh_clean):
            pre_cmd_is_refresh /= 0

        #FSM state done signal
        s_phy_reset_done = bits('s_phy_reset_done', init = 0)
        s_phy_cke_done = bits('s_phy_cke_done', init = 0)
        s_phy_init_done = bits('s_phy_init_done', init = 0)
        s_phy_zq_cal_init_done = bits('s_phy_zq_cal_init_done', init = 0)
        s_phy_wrlvl_done = bits('s_phy_wrlvl_done', init = 0)
        s_phy_rdlvl_done = bits('s_phy_rdlvl_done', init = 0)
        s_phy_mrs_done = bits('s_phy_mrs_done', init = 0)
        s_phy_active_done = bits('s_phy_active_done', init = 0)
        s_phy_read_done = bits('s_phy_read_done', init = 0)
        s_phy_write_done = bits('s_phy_write_done', init = 0)
        s_phy_precharge_done = bits('s_phy_precharge_done', init = 0)
        s_phy_precharge_all_done = bits('s_phy_precharge_all_done', init = 0)
        s_phy_refresh_done = bits('s_phy_refresh_done', init = 0)

        #FSM state transform control
        with when(phy_state == s_phy_init):
            with when(s_phy_init_done):
                phy_state /= s_phy_reset
        with when(phy_state == s_phy_reset):
            with when(s_phy_reset_done):
                phy_state /= s_phy_cke
        with when(phy_state == s_phy_cke):
            with when(s_phy_cke_done):
                phy_state /= s_phy_zq_cal_init
        with when(phy_state == s_phy_mrs):
            with when(s_phy_mrs_done):
                phy_state /= s_phy_wrlvl
        with when(phy_state == s_phy_zq_cal_init):
            with when(s_phy_zq_cal_init_done):
                phy_state /= s_phy_mrs
        with when(phy_state == s_phy_wrlvl):
            with when(s_phy_wrlvl_done):
                phy_state /= s_phy_rdlvl
        with when(phy_state == s_phy_rdlvl):
            with when(s_phy_rdlvl_done):
                phy_state /= s_phy_ready
                pre_cmd_is_active_reset_all /= 1
                pre_cmd_is_write_reset_all /= 1
                pre_cmd_is_read_reset_all /= 1
                pre_cmd_is_precharge_reset_all /= 1
                pre_cmd_is_precharge_clean /= 1
                pre_cmd_is_refresh_clean /= 1
        with when(phy_state == s_phy_ready):
            with when(ddr_cmd_refresh_en):
                #need wait enough time for pre precharge cmd
                with when(~(cnt1[0] < cfg_trp_ab)):
                    phy_state /= s_phy_refresh
            with elsewhen(ddr_cmd_active_en):
                with when(
                    ~faw_block & 
                    ~reduce(
                        lambda a,b: a|b, list(map(
                            lambda _: pre_cmd_is_active[_] & (cnt1[_] < cfg_trrd),
                            range(const_max_bank_num)))) &
                    ~(pre_cmd_is_precharge_sel & (cnt1_sel < cfg_trp)) &
                    ~(pre_cmd_is_precharge_all & (cnt1[0] < cfg_trp))):
                    phy_state /= s_phy_active
            with elsewhen(ddr_cmd_precharge_en):
                with when(
                    ~tras_block &
                    ~(pre_cmd_is_write_sel & (cnt1_sel < cfg_wl_bl_twr)) &
                    ~(pre_cmd_is_read_sel & (cnt1_sel < cfg_al_trtp))):
                    phy_state /= s_phy_precharge
            with elsewhen(ddr_cmd_precharge_all_en):
                with when(
                    ~tras_block &
                    ~reduce(
                        lambda a,b:a|b,
                        list(map(
                            lambda _: pre_cmd_is_write[_] & (cnt1[_] < cfg_wl_bl_twr),
                            range(const_max_bank_num)))) &
                    ~reduce(
                        lambda a,b:a|b,
                        list(map(
                            lambda _: pre_cmd_is_read[_] & (cnt1[_] < cfg_al_trtp),
                            range(const_max_bank_num))))):
                    phy_state /= s_phy_precharge_all
            with elsewhen(ddr_cmd_wr_en):
                with when(
                    ~(pre_cmd_is_active_sel & (cnt1_sel < cfg_trcd)) &
                    ~reduce(
                        lambda a,b:a|b,
                        list(map(
                            lambda _: pre_cmd_is_write[_] & (cnt1[_] < cfg_tccd),
                            range(const_max_bank_num)))) &
                    ~reduce(
                        lambda a,b:a|b,
                        list(map(
                            lambda _: pre_cmd_is_read[_] & (cnt1[_] < cfg_trc2wc),
                            range(const_max_bank_num))))):
                    phy_state /= s_phy_write
            with elsewhen(ddr_cmd_rd_en):
                #need wait at least cfg_twc2rc for previous write cmd
                with when(
                    ~(pre_cmd_is_active_sel & (cnt1_sel < cfg_trcd)) &
                    ~reduce(
                        lambda a,b:a|b,
                        list(map(
                            lambda _: pre_cmd_is_write[_] & (cnt1[_] < cfg_twc2rc),
                            range(const_max_bank_num)))) &
                    ~reduce(
                        lambda a,b: a|b,
                        list(map(
                            lambda _: pre_cmd_is_read[_] & (cnt1[_] < cfg_tccd),
                            range(const_max_bank_num)))) &
                    ~reduce(
                        lambda a,b: a|b,
                        list(map(
                            lambda _: (
                                pre_cmd_is_read[_] & 
                                (
                                    (cnt1[_] > odth_rd_block_l) & 
                                    (cnt1[_] < odth_rd_block_h))),
                            range(const_max_bank_num))))):
                    phy_state /= s_phy_read
        with when(phy_state == s_phy_active):
            with when(s_phy_active_done):
                phy_state /= s_phy_ready
                pre_cmd_is_active_set /= 1
                pre_cmd_is_write_clean /= 1
                pre_cmd_is_read_clean /= 1
                pre_cmd_is_precharge_clean /= 1
                pre_cmd_is_precharge_all_clean /= 1
                pre_cmd_is_refresh_clean /= 1
        with when(phy_state == s_phy_read):
            with when(s_phy_read_done & dfi_req_cmd_read_done):
                phy_state /= s_phy_ready
                pre_cmd_is_active_clean /= 1
                pre_cmd_is_write_clean /= 1
                pre_cmd_is_read_set /= 1
                pre_cmd_is_precharge_clean /= 1
                pre_cmd_is_precharge_all_clean /= 1
                pre_cmd_is_refresh_clean /= 1
        with when(phy_state == s_phy_write):
            with when(s_phy_write_done & dfi_req_cmd_write_done):
                phy_state /= s_phy_ready
                pre_cmd_is_active_clean /= 1
                pre_cmd_is_write_set /= 1
                pre_cmd_is_read_clean /= 1
                pre_cmd_is_precharge_clean /= 1
                pre_cmd_is_precharge_all_clean /= 1
                pre_cmd_is_refresh_clean /= 1
        with when(phy_state == s_phy_precharge):
            with when(s_phy_precharge_done):
                phy_state /= s_phy_ready
                pre_cmd_is_active_clean /= 1
                pre_cmd_is_write_clean /= 1
                pre_cmd_is_read_clean /= 1
                pre_cmd_is_precharge_set /= 1
                pre_cmd_is_precharge_all_clean /= 1
                pre_cmd_is_refresh_clean /= 1
        with when(phy_state == s_phy_precharge_all):
            with when(s_phy_precharge_all_done):
                phy_state /= s_phy_ready
                pre_cmd_is_active_reset_all /= 1
                pre_cmd_is_write_reset_all /= 1
                pre_cmd_is_read_reset_all /= 1
                pre_cmd_is_precharge_reset_all /= 1
                pre_cmd_is_precharge_all_set /= 1
                pre_cmd_is_refresh_clean /= 1
        with when(phy_state == s_phy_refresh):
            with when(s_phy_refresh_done):
                phy_state /= s_phy_ready
                pre_cmd_is_active_reset_all /= 1
                pre_cmd_is_write_reset_all /= 1
                pre_cmd_is_read_reset_all /= 1
                pre_cmd_is_precharge_reset_all /= 1
                pre_cmd_is_precharge_all_clean /= 1
                pre_cmd_is_refresh_set /= 1


        ####
        #signal control according FSM
        s_phy_init_dll_rst_n_wait = reg_r('s_phy_init_dll_rst_n_wait')
        s_phy_init_complete_wait = reg_r('s_phy_init_complete_wait')
        with when(phy_state == s_phy_init):
            dfi_refresh_en /= 0
            dfi_odt_work /= 0
            self.dfi_ac_reset()
            with when(~s_phy_init_dll_rst_n_wait):
                self.phy_dfi_if_reg.dll_rst_n /= 0

            with when(cfg_start):
                self.phy_dfi_if_reg.control.cs_n /= 0
                self.phy_dfi_if_reg.status.init_start /= 1
                with when(~s_phy_init_dll_rst_n_wait & ~s_phy_init_complete_wait):
                    s_phy_init_dll_rst_n_wait /= 1
                    cnt0 /= cfg_dll_rst_adj_dly
                with elsewhen(s_phy_init_dll_rst_n_wait & ~s_phy_init_complete_wait):
                    with when(~cnt0_is_0):
                        cnt0_dec_en /= 1
                    with other():
                        self.phy_dfi_if_reg.dll_rst_n /= 1
                        with when(self.phy_dfi_if_reg.status.init_complete):
                            s_phy_init_complete_wait /= 1
                            cnt0 /= 10
                with elsewhen(s_phy_init_dll_rst_n_wait & s_phy_init_complete_wait):
                    with when(~cnt0_is_0):
                        cnt0_dec_en /= 1
                    with other():
                        s_phy_init_dll_rst_n_wait /= 0
                        s_phy_init_complete_wait /= 0
                        s_phy_init_done /= 1
                        self.phy_dfi_if_reg.status.init_start /= 0
            with other():
                self.phy_dfi_if_reg.control.cs_n /= 1
                self.phy_dfi_if_reg.status.init_start /= 0

        s_phy_reset_assert_wait = reg_r('s_phy_reset_assert_wait')
        with when(phy_state == s_phy_reset):
            dfi_refresh_en /= 0
            dfi_odt_work /= 0
            with when(~s_phy_reset_assert_wait):
                self.dfi_ac_reset()
                s_phy_reset_assert_wait /= 1
                cnt0 /= cfg_trst_pwron
            with other():
                with when(~cnt0_is_0):
                    cnt0_dec_en /= 1
                with other():
                    s_phy_reset_assert_wait /= 0
                    s_phy_reset_done /= 1
                    self.phy_dfi_if_reg.control.reset_n /= 1

        s_phy_cke_deassert_wait = reg_r('s_phy_cke_deassert_wait')
        s_phy_cke_assert_wait = reg_r('s_phy_cke_assert_wait')
        with when(phy_state == s_phy_cke):
            dfi_refresh_en /= 0
            dfi_odt_work /= 0
            with when(~s_phy_cke_deassert_wait & ~s_phy_cke_assert_wait):
                s_phy_cke_deassert_wait /= 1
                cnt0 /= cfg_tcke_inactive
            with elsewhen(s_phy_cke_deassert_wait & ~s_phy_cke_assert_wait):
                with when(~cnt0_is_0):
                    cnt0_dec_en /= 1
                with other():
                    s_phy_cke_assert_wait /= 1
                    cnt0 /= cfg_txpr
                    self.phy_dfi_if_reg.control.cke /= 1
            with elsewhen(s_phy_cke_deassert_wait & s_phy_cke_assert_wait):
                with when(~cnt0_is_0):
                    cnt0_dec_en /= 1
                with other():
                    s_phy_cke_assert_wait /= 0
                    s_phy_cke_deassert_wait /= 0
                    s_phy_cke_done /= 1

        s_phy_mrs_reg_idx = reg_rs('s_phy_mrs_reg_idx', w = 2, rs = 3)
        s_phy_mrs_reg_wait = reg_r('s_phy_mrs_reg_wait')
        s_phy_mrs_odt_wait = reg_r('s_phy_mrs_odt_wait')
        with when(phy_state == s_phy_mrs):
            with when(
                cfg_write_modereg[25] & 
                cfg_write_modereg[24] & 
                cfg_write_modereg[17]):
                with when(~s_phy_mrs_reg_wait & ~s_phy_mrs_odt_wait):
                    dfi_refresh_en /= 0
                    dfi_odt_work /= 0
                    s_phy_mrs_reg_wait /= 1 
                    
                    with when(s_phy_mrs_reg_idx == 0):
                        s_phy_mrs_reg_idx /= 3
                        cnt0 /= cfg_tdll
                    with other():
                        s_phy_mrs_reg_idx /= s_phy_mrs_reg_idx - 1
                        cnt0 /= cfg_tmrd
                    self.dfi_mrs(s_phy_mrs_reg_idx, sel_bin(s_phy_mrs_reg_idx, cfg_mrs))
                with elsewhen(s_phy_mrs_reg_wait & ~s_phy_mrs_odt_wait):
                    self.dfi_ac_nop()
                    with when(~cnt0_is_0):
                        cnt0_dec_en /= 1
                    with other():
                        with when(s_phy_mrs_reg_idx == 3):
                            dfi_odt_work /= 1
                            s_phy_mrs_odt_wait /= 1
                            cnt0 /= 10 #TBD
                        with other():
                            s_phy_mrs_reg_wait /= 0
                with elsewhen(s_phy_mrs_reg_wait & s_phy_mrs_odt_wait):
                    self.dfi_ac_nop()
                    with when(~cnt0_is_0):
                        cnt0_dec_en /= 1
                    with other():
                        s_phy_mrs_done /= 1
                        s_phy_mrs_reg_wait /= 0
                        s_phy_mrs_odt_wait /= 0
            with other():
                self.dfi_ac_nop()

        s_phy_zq_cal_init_wait = reg_r('s_phy_zq_cal_init_wait')
        with when(phy_state == s_phy_zq_cal_init):
            dfi_refresh_en /= 0
            with when(~s_phy_zq_cal_init_wait):
                self.dfi_zq_cal(1)
                s_phy_zq_cal_init_wait /= 1
                cnt0 /= cfg_zqinit
            with other():
                self.dfi_ac_nop()
                with when(~cnt0_is_0):
                    cnt0_dec_en /= 1
                with other():
                    s_phy_zq_cal_init_wait /= 0
                    s_phy_zq_cal_init_done /= 1

        #TBD
        with when(phy_state == s_phy_wrlvl):
            dfi_refresh_en /= 0
            self.dfi_ac_nop()
            s_phy_wrlvl_done /= 1

        #TBD
        with when(phy_state == s_phy_rdlvl):
            dfi_refresh_en /= 0
            self.dfi_ac_nop()
            s_phy_rdlvl_done /= 1

        with when(phy_state == s_phy_ready):
            dfi_refresh_en /= 1
            self.dfi_ac_nop()

        with when(phy_state == s_phy_active):
            self.dfi_ac_active(ddr_cmd_addr_bank, ddr_cmd_addr_row)
            cnt0 /= 0
            s_phy_active_done /= 1
            ddr_cmd_fifo.io.deq.ready /= 1
            cnt1_set_one /= 1
            faw_active_issue /= 1
            tras_cnt_set /= 1
        #faw active counter process
        for i in range(len(faw_cnt_en)):
            with when(faw_cnt_en[i]):
                with when(faw_cnt[i] == cfg_tfaw - 1):
                    faw_cnt[i] /= 0
                    faw_cnt_en[i] /= 0
                with other():
                    faw_cnt[i] /= faw_cnt[i] + 1
        faw_cnt_valid_oh = pri_lsb_enc_oh(~faw_cnt_en.pack())
        with when(faw_active_issue):
            for i in range(len(faw_cnt_en)):
                with when(faw_cnt_valid_oh[i]):
                    faw_cnt_en[i] /= 1
        with when(faw_cnt_en.pack() == (2 ** faw_cnt_en.get_w() - 1)):
            faw_block /= 1

        with when(phy_state == s_phy_read):
            self.dfi_ac_read(ddr_cmd_addr_bank, ddr_cmd_addr_col, 0, 0)
            cnt0 /= 0
            ddr_cmd_fifo.io.deq.ready /= 1
            s_phy_read_done /= 1
            dfi_req_cmd_read_done /= 1
            cnt1_set_one /= 1
        #dfi rdata_valid process
        ddr_cmd_rddata_sop_eop_fifo = queue(
            'ddr_cmd_rddata_sop_eop_fifo',
            gen = lambda _: bits(_, w = 2),
            entries = self.p.tdfi_phy_rdlat_max)
        ddr_cmd_rddata_sop_eop_fifo.io.enq.valid /= 0
        ddr_cmd_rddata_sop_eop_fifo.io.deq.ready /= 0
        rd_data_valid_map = self.bl_flip_valid_map(
            ddr_cmd_pipe_rd_info_fifo.io.deq.bits.addr,
            ddr_cmd_pipe_rd_info_fifo.io.deq.bits.size,
            ddr_cmd_pipe_rd_info_fifo.io.deq.bits.size < ddr_burst_size)
        dfi_rddata_sop_eop = ddr_cmd_rddata_sop_eop_fifo.io.deq.bits
        #last flit
        with when(self.phy_dfi_if_reg.rddata.rddata_valid & dfi_rddata_sop_eop[1]):
            ddr_cmd_pipe_rd_info_fifo.io.deq.ready /= 1
        with when(self.phy_dfi_if_reg.rddata.rddata_valid):
            with when(dfi_req_rddata_burst_beat_cnt == cfg_ddr_dfi_bl - 1):
                dfi_req_rddata_burst_beat_cnt /= 0
            with other():
                dfi_req_rddata_burst_beat_cnt /= dfi_req_rddata_burst_beat_cnt + 1
            with when(rd_data_valid_map[dfi_req_rddata_burst_beat_cnt]):
                mem_rd_resp_buffer.io.enq.valid /= 1
            ddr_cmd_rddata_sop_eop_fifo.io.deq.ready /= 1
        #read response data flit
        mem_rd_resp_buffer.io.enq.bits.write /= ddr_cmd_pipe_rd_info_fifo.io.deq.bits.write
        mem_rd_resp_buffer.io.enq.bits.last /= 0
        mem_rd_resp_buffer.io.enq.bits.bank /= get_bank_bits_from_addr(
            ddr_cmd_pipe_rd_info_fifo.io.deq.bits.addr)
        mem_rd_resp_buffer.io.enq.bits.size /= ddr_cmd_pipe_rd_info_fifo.io.deq.bits.size
        mem_rd_resp_buffer.io.enq.bits.token /= ddr_cmd_pipe_rd_info_fifo.io.deq.bits.token
        mem_rd_resp_buffer.io.enq.bits.data /= self.phy_dfi_if_reg.rddata.rddata
        mem_rd_resp_buffer.io.enq.bits.error /= 0
        with when(ddr_cmd_pipe_rd_info_fifo.io.deq.bits.last):
            beat_cnt_shift = (1 << dfi_req_rddata_burst_beat_cnt)[self.p.dfi_bl_max - 1 : 0]
            bit_mask = beat_cnt_shift | bin2lsb1(
                dfi_req_rddata_burst_beat_cnt, 
                w = self.p.dfi_bl_max)
            #last read response data, bank arbiter will clean it's lock,
            #the following unused data will be dropped
            with when((~bit_mask & rd_data_valid_map) == 0):
                mem_rd_resp_buffer.io.enq.bits.last /= 1

        with when(phy_state == s_phy_write):
            self.dfi_ac_write(ddr_cmd_addr_bank, ddr_cmd_addr_col, 0, 0)
            cnt0 /= 0
            ddr_cmd_fifo.io.deq.ready /= 1
            s_phy_write_done /= 1
            dfi_req_cmd_write_done /= 1
            cnt1_set_one /= 1
        wr_data_valid_map = self.bl_flip_valid_map(
            ddr_cmd_pipe_wr_info_fifo.io.deq.bits.addr,
            ddr_cmd_pipe_wr_info_fifo.io.deq.bits.size,
            ddr_cmd_pipe_wr_info_fifo.io.deq.bits.size < ddr_burst_size)
        dfi_wrdata_q = self.dfi_wrdata_q_pipe[0] | self.dfi_wrdata_q_no_latency
        dfi_wrdata_q_sop_eop = mux(
            self.dfi_wrdata_q_no_latency,
            self.dfi_wrdata_q_sop_eop_no_latency,
            self.dfi_wrdata_q_sop_eop_pipe[0])
        dfi_wrdata_q_bank = mux(
            self.dfi_wrdata_q_no_latency,
            self.dfi_wrdata_q_bank_no_latency,
            self.dfi_wrdata_q_bank_pipe[0])
        with when(dfi_wrdata_q):
            with when(wr_data_valid_map[dfi_req_wrdata_burst_beat_cnt]):
                for i in range(const_queue_ll_num):
                    mem_req_data_buffer.io.deq[i].ready /= bank2ll_map(dfi_wrdata_q_bank) == i
            with when(dfi_wrdata_q_sop_eop[1]):#last flit
                ddr_cmd_pipe_wr_info_fifo.io.deq.ready /= 1
                with when(ddr_cmd_pipe_wr_info_fifo.io.deq.bits.last):
                    mem_wr_resp_buffer.io.enq.valid /= 1
        #write resp flit info
        mem_wr_resp_buffer.io.enq.bits.write /= 1
        mem_wr_resp_buffer.io.enq.bits.last /= ddr_cmd_pipe_wr_info_fifo.io.deq.bits.last
        mem_wr_resp_buffer.io.enq.bits.bank /= get_bank_bits_from_addr(
            ddr_cmd_pipe_wr_info_fifo.io.deq.bits.addr)
        mem_wr_resp_buffer.io.enq.bits.size /= ddr_cmd_pipe_wr_info_fifo.io.deq.bits.size
        mem_wr_resp_buffer.io.enq.bits.token /= ddr_cmd_pipe_wr_info_fifo.io.deq.bits.token
        mem_wr_resp_buffer.io.enq.bits.data /= 0
        mem_wr_resp_buffer.io.enq.bits.error /= 0

        with when(phy_state == s_phy_precharge):
            self.dfi_ac_precharge(ddr_cmd_addr_bank, 0)
            s_phy_precharge_done /= 1
            ddr_cmd_fifo.io.deq.ready /= 1
            cnt1_set_one /= 1

        with when(phy_state == s_phy_precharge_all):
            self.dfi_ac_precharge(ddr_cmd_addr_bank, 1)
            s_phy_precharge_all_done /= 1
            ddr_cmd_fifo.io.deq.ready /= 1
            cnt1_set_all /= 1

        s_phy_refresh_wait = reg_r('s_phy_refresh_wait')
        with when(phy_state == s_phy_refresh):
            with when(~s_phy_refresh_wait):
                self.dfi_ac_refresh()
                cnt0 /= cfg_trfc - 1
                s_phy_refresh_wait /= 1
            with other():
                self.dfi_ac_nop()
                with when(~cnt0_is_0):
                    cnt0_dec_en /= 1
                with other():
                    s_phy_refresh_wait /= 0
                    s_phy_refresh_done /= 1
                    ddr_cmd_fifo.io.deq.ready /= 1
                    cnt1_set_all /= 1

        ddr_cmd_pipe_wr_info_fifo.io.enq.bits /= ddr_cmd_fifo.io.deq.bits
        ddr_cmd_pipe_wr_info_fifo.io.enq.valid /= (
            ddr_cmd_fifo.io.deq.fire() & phy_state.match_any([s_phy_write]))

        ddr_cmd_pipe_rd_info_fifo.io.enq.bits /= ddr_cmd_fifo.io.deq.bits
        ddr_cmd_pipe_rd_info_fifo.io.enq.valid /= (
            ddr_cmd_fifo.io.deq.fire() & phy_state.match_any([s_phy_read]))
        
        #odt output control
        self.phy_dfi_if_reg.control.odt /= (
            cfg_odt_en & dfi_odt_work & ~self.dfi_odt_mask_pipe[0])
        with when(self.dfi_odt_mask_pipe.pack() != 0):
            #shift odt bit
            for i in range(len(self.dfi_odt_mask_pipe)):
                is_set = self.dfi_odt_mask_pipe_set[i]
                if (i == len(self.dfi_odt_mask_pipe) - 1):
                    cur_mask = is_set | 0
                else:
                    cur_mask = is_set | self.dfi_odt_mask_pipe[i+1]
                self.dfi_odt_mask_pipe[i] /= cur_mask

        #according read data latency, set the rddata_en at the right time slot
        dfi_rddata_en = self.dfi_rddata_en_pipe[0]
        self.phy_dfi_if_reg.rddata.rddata_en /= dfi_rddata_en
        with when(self.dfi_rddata_en_pipe.pack() != 0):
            for i in range(len(self.dfi_rddata_en_pipe)):
                is_set = self.dfi_rddata_en_pipe_set[i]
                is_sop_eop_set = self.dfi_rddata_en_sop_eop_pipe_set[i] != 0
                if (i == len(self.dfi_rddata_en_pipe) - 1):
                    cur_en = is_set | 0
                    cur_en_sop_eop = mux(
                        is_sop_eop_set,
                        self.dfi_rddata_en_sop_eop_pipe_set[i], 
                        0)
                else:
                    cur_en = is_set | self.dfi_rddata_en_pipe[i+1]
                    cur_en_sop_eop = mux(
                        is_sop_eop_set, 
                        self.dfi_rddata_en_sop_eop_pipe_set[i],
                        self.dfi_rddata_en_sop_eop_pipe[i+1])
                self.dfi_rddata_en_pipe[i] /= cur_en
                self.dfi_rddata_en_sop_eop_pipe[i] /= cur_en_sop_eop
        ddr_cmd_rddata_sop_eop_fifo.io.enq.bits /= self.dfi_rddata_en_sop_eop_pipe[0]
        with when(dfi_rddata_en != 0):
            ddr_cmd_rddata_sop_eop_fifo.io.enq.valid /= 1

        #according write data latency, set the wrdata_en at the right time slot
        dfi_wrdata_en = self.dfi_wrdata_en_pipe[0] | self.dfi_wrdata_en_no_latency
        self.phy_dfi_if_reg.wrdata.wrdata_cs /= 0
        self.phy_dfi_if_reg.wrdata.wrdata_en /= dfi_wrdata_en
        with when(self.dfi_wrdata_en_pipe.pack() != 0):
            for i in range(len(self.dfi_wrdata_en_pipe)):
                is_set = self.dfi_wrdata_en_pipe_set[i]
                if (i == len(self.dfi_wrdata_en_pipe) - 1):
                    next_en = is_set | 0
                else:
                    next_en = is_set | self.dfi_wrdata_en_pipe[i+1]
                self.dfi_wrdata_en_pipe[i] /= next_en
        #write data need set data mask if data len is less the one burst len
        dfi_wrdata_mask = self.bl_flip_wrdata_mask(
            ddr_cmd_pipe_wr_info_fifo.io.deq.bits.addr,
            ddr_cmd_pipe_wr_info_fifo.io.deq.bits.size)
        self.phy_dfi_if_reg.wrdata.wrdata /= mem_req_data_buffer.io.deq_dp_bits.data
        self.phy_dfi_if_reg.wrdata.wrdata_mask /= bits(init = 1).rep(
            self.const_dfi_data_bytes)
        with when(dfi_wrdata_q):
            with when(dfi_req_wrdata_burst_beat_cnt == cfg_ddr_dfi_bl - 1):
                dfi_req_wrdata_burst_beat_cnt /= 0
            with other():
                dfi_req_wrdata_burst_beat_cnt /= dfi_req_wrdata_burst_beat_cnt + 1

            with when(wr_data_valid_map[dfi_req_wrdata_burst_beat_cnt]):
                self.phy_dfi_if_reg.wrdata.wrdata_mask /= dfi_wrdata_mask.pack()
        with when(self.dfi_wrdata_q_pipe.pack() != 0):
            for i in range(len(self.dfi_wrdata_q_pipe)):
                is_q_set = self.dfi_wrdata_q_pipe_set[i]
                is_q_sop_eop_set = self.dfi_wrdata_q_sop_eop_pipe_set[i] != 0
                if (i == len(self.dfi_wrdata_q_pipe) - 1):
                    cur_q = is_q_set | 0
                    cur_q_sop_eop = mux(
                        is_q_sop_eop_set, 
                        self.dfi_wrdata_q_sop_eop_pipe_set[i],
                        0)
                    cur_q_bank = mux(
                        is_q_set, 
                        self.dfi_wrdata_q_bank_pipe_set[i],
                        0)
                else:
                    cur_q = is_q_set | self.dfi_wrdata_q_pipe[i+1]
                    cur_q_sop_eop = mux(
                        is_q_sop_eop_set, 
                        self.dfi_wrdata_q_sop_eop_pipe_set[i], 
                        self.dfi_wrdata_q_sop_eop_pipe[i+1])
                    cur_q_bank = mux(
                        is_q_set, 
                        self.dfi_wrdata_q_bank_pipe_set[i],
                        self.dfi_wrdata_q_bank_pipe[i+1])
                self.dfi_wrdata_q_pipe[i] /= cur_q
                self.dfi_wrdata_q_sop_eop_pipe[i] /= cur_q_sop_eop
                self.dfi_wrdata_q_bank_pipe[i] /= cur_q_bank


        ####
        #csr status report
        cfg_max_cs_reg /= const_ddr_cs_addr_bits
        cfg_max_col_reg /= const_ddr_col_addr_bits
        cfg_max_row_reg /= const_ddr_row_addr_bits
        self.cfg_tdfi_phy_wrlat /= cfg_wrlat_adj + cfg_reg_dimm_enable - 1
        self.cfg_tdfi_rddata_en /= cfg_rdlat_adj + cfg_reg_dimm_enable - 1
        cfg_cke_status /= self.phy_dfi_if_reg.control.cke
        cfg_zq_in_progress /= phy_state == s_phy_zq_cal_init


        ####
        #interrupt report
        with when(~cfg_int_status[4] & s_phy_zq_cal_init_done):
            cfg_int_status[4] /= 1
        with when(~cfg_int_status[17] & s_phy_mrs_done):
            cfg_int_status[17] /= 1
        with when(~cfg_int_status[19] & s_phy_init_done):
            cfg_int_status[19] /= 1
        self.io.int_flag /= (~cfg_int_mask & cfg_int_status).r_or()


    def dfi_ac_reset(self):
        self.phy_dfi_if_reg.control.reset_n /= 0
        self.phy_dfi_if_reg.control.cke /= 0

        self.phy_dfi_if_reg.control.ras_n /= 1
        self.phy_dfi_if_reg.control.cas_n /= 1
        self.phy_dfi_if_reg.control.we_n /= 1
        self.phy_dfi_if_reg.control.bank /= 0
        self.phy_dfi_if_reg.control.address /= 0

        self.phy_dfi_if_reg.update.ctrlupd_req /= 0
        self.phy_dfi_if_reg.update.phyupd_ack /= 0

        self.phy_dfi_if_reg.status.data_byte_disable /= 0
        self.phy_dfi_if_reg.status.dram_clk_disable /= 0
        self.phy_dfi_if_reg.status.init_start /= 0
        self.phy_dfi_if_reg.status.freq_ratio /= 0
        self.phy_dfi_if_reg.status.parity_in /= 0

        self.phy_dfi_if_reg.training.rdlvl_load /= 0
        self.phy_dfi_if_reg.training.rdlvl_cs_n /= 1
        self.phy_dfi_if_reg.training.rdlvl_en /= 0
        self.phy_dfi_if_reg.training.rdlvl_edge /= 0
        self.phy_dfi_if_reg.training.rdlvl_delay /= 0
        self.phy_dfi_if_reg.training.rdlvl_gate_en /= 0
        self.phy_dfi_if_reg.training.rdlvl_gate_delay /= 0
        self.phy_dfi_if_reg.training.wrlvl_load /= 0
        self.phy_dfi_if_reg.training.wrlvl_cs_n /= 1
        self.phy_dfi_if_reg.training.wrlvl_strobe /= 0
        self.phy_dfi_if_reg.training.wrlvl_en /= 0
        self.phy_dfi_if_reg.training.wrlvl_delay /= 0

        self.phy_dfi_if_reg.lp.lp_req /= 0
        self.phy_dfi_if_reg.lp.lp_wakeup /= 0


    def dfi_ac_nop(self):
        self.phy_dfi_if_reg.control.ras_n /= 1
        self.phy_dfi_if_reg.control.cas_n /= 1
        self.phy_dfi_if_reg.control.we_n /= 1
        self.phy_dfi_if_reg.control.bank /= 0
        self.phy_dfi_if_reg.control.address /= 0

    def dfi_zq_cal(self, do_long):
        self.phy_dfi_if_reg.control.ras_n /= 1
        self.phy_dfi_if_reg.control.cas_n /= 1
        self.phy_dfi_if_reg.control.we_n /= 0
        self.phy_dfi_if_reg.control.bank /= 0
        self.phy_dfi_if_reg.control.address /= do_long << 10

    def dfi_mrs(self, bank, address):
        self.phy_dfi_if_reg.control.ras_n /= 0
        self.phy_dfi_if_reg.control.cas_n /= 0
        self.phy_dfi_if_reg.control.we_n /= 0
        self.phy_dfi_if_reg.control.bank /= bank
        self.phy_dfi_if_reg.control.address /= address

    def dfi_ac_active(self, bank, row):
        self.phy_dfi_if_reg.control.ras_n /= 0
        self.phy_dfi_if_reg.control.cas_n /= 1
        self.phy_dfi_if_reg.control.we_n /= 1
        self.phy_dfi_if_reg.control.bank /= bank
        self.phy_dfi_if_reg.control.address /= row

    def dfi_ac_read(self, bank, col, ap, bc):
        self.phy_dfi_if_reg.control.ras_n /= 1
        self.phy_dfi_if_reg.control.cas_n /= 0
        self.phy_dfi_if_reg.control.we_n /= 1
        self.phy_dfi_if_reg.control.bank /= bank
        #set the auto precharge bit, bit position is configureable
        ap_addr = cat_rvs(map(
            lambda _: (_ == self.cfg_aprebit) & ap,
            range(self.phy_dfi_if_reg.control.address.get_w())))
        self.phy_dfi_if_reg.control.address /= col | ap_addr | (bc<<12)

        #odt delay pipe set
        for i in range(self.p.dfi_bl_max + 2):
            self.dfi_odt_mask_pipe_set(self.cfg_odt_rd_delay + i - 1, 1)
            self.dfi_odt_mask_pipe(self.cfg_odt_rd_delay + i - 1, 1) #need - 1


        #rddata_en/info delay pipe set
        for i in range(self.p.dfi_bl_max):
            sop_eop = cat([i == (self.p.dfi_bl_max - 1), i == 0])
            self.dfi_rddata_en_pipe_set(
                self.cfg_tdfi_rddata_en + i - 1,
                bits(init = 1).rep(self.io.phy_dfi.rddata.rddata_en.get_w()))
            self.dfi_rddata_en_sop_eop_pipe_set(self.cfg_tdfi_rddata_en + i - 1, sop_eop) 
            self.dfi_rddata_en_pipe(
                self.cfg_tdfi_rddata_en + i - 1,
                bits(init = 1).rep(self.io.phy_dfi.rddata.rddata_en.get_w())) #need - 1
            self.dfi_rddata_en_sop_eop_pipe(self.cfg_tdfi_rddata_en + i - 1, sop_eop)

    def dfi_ac_write(self, bank, col, ap, bc):
        self.phy_dfi_if_reg.control.ras_n /= 1
        self.phy_dfi_if_reg.control.cas_n /= 0
        self.phy_dfi_if_reg.control.we_n /= 0
        self.phy_dfi_if_reg.control.bank /= bank
        #set auto precharge bit
        ap_addr = cat_rvs(map(
            lambda _: (_ == self.cfg_aprebit) & ap,
            range(self.phy_dfi_if_reg.control.address.get_w())))
        self.phy_dfi_if_reg.control.address /= col | ap_addr | (bc<<12)

        #wrdata delay pipe set
        tdfi_phy_wrlat_add_tdfi_phy_wrdata = self.cfg_tdfi_phy_wrlat + self.cfg_tdfi_phy_wrdata
        tdfi_phy_wrlat_add_tdfi_phy_wrdata_reg = reg(next = tdfi_phy_wrlat_add_tdfi_phy_wrdata, w = tdfi_phy_wrlat_add_tdfi_phy_wrdata.get_w())
        with when(self.cfg_tdfi_phy_wrlat == 0):
            self.dfi_wrdata_en_no_latency /= bits(init = 1).rep(
                self.io.phy_dfi.wrdata.wrdata_en.get_w())
        with when(tdfi_phy_wrlat_add_tdfi_phy_wrdata_reg == 0):
            self.dfi_wrdata_q_no_latency /= 1
            self.dfi_wrdata_q_sop_eop_no_latency /= cat([0, 1])
            self.dfi_wrdata_q_bank_no_latency /= bank

        wrdata_pipe_addr_w = log2_ceil(len(self.dfi_wrdata_en_pipe_set))
        for i in range(self.p.dfi_bl_max):
            i_offset = i - 1
            offset0 = reg(next = self.cfg_tdfi_phy_wrlat + i_offset, w = wrdata_pipe_addr_w)
            offset1 = reg(next = tdfi_phy_wrlat_add_tdfi_phy_wrdata_reg + i_offset, w = wrdata_pipe_addr_w)
            with when(~((self.cfg_tdfi_phy_wrlat == 0) & (i == 0))):
                self.dfi_wrdata_en_pipe_set(
                    offset0,
                    bits(init = 1).rep(self.io.phy_dfi.wrdata.wrdata_en.get_w()))
                self.dfi_wrdata_en_pipe(
                    offset0,
                    #need - 1
                    bits(init = 1).rep(self.io.phy_dfi.wrdata.wrdata_en.get_w()))
            with when(
                ~(
                    (tdfi_phy_wrlat_add_tdfi_phy_wrdata_reg == 0) & 
                    (i == 0))):
                self.dfi_wrdata_q_pipe_set(
                    offset1,
                    1)
                self.dfi_wrdata_q_pipe(
                    offset1,
                    1) #need - 1

                sop_eop = cat([i == (self.p.dfi_bl_max - 1), i == 0])
                self.dfi_wrdata_q_sop_eop_pipe_set(
                    offset1,
                    sop_eop)
                self.dfi_wrdata_q_sop_eop_pipe(
                    offset1,
                    sop_eop)
                self.dfi_wrdata_q_bank_pipe_set(
                    offset1,
                    bank)
                self.dfi_wrdata_q_bank_pipe(
                    offset1,
                    bank)

    def dfi_ac_precharge(self, bank, ap):
        self.phy_dfi_if_reg.control.ras_n /= 0
        self.phy_dfi_if_reg.control.cas_n /= 1
        self.phy_dfi_if_reg.control.we_n /= 0
        self.phy_dfi_if_reg.control.bank /= bank
        #precharge all bit set
        ap_addr = cat_rvs(map(
            lambda _: (_ == self.cfg_aprebit) & ap,
            range(self.phy_dfi_if_reg.control.address.get_w())))
        self.phy_dfi_if_reg.control.address /= ap_addr

    def dfi_ac_refresh(self):
        self.phy_dfi_if_reg.control.ras_n /= 0
        self.phy_dfi_if_reg.control.cas_n /= 0
        self.phy_dfi_if_reg.control.we_n /= 1

    def bl_flip_valid_map(self, addr, size, bl_less):
        valid_map = vec(gen = bits, n = self.p.dfi_bl_max)
        for i in range(self.p.dfi_bl_max):
            valid_map[i] /= ~bl_less
        with when(bl_less):
            idx = addr[
                self.const_ddr_burst_size_max - 1 : log2_ceil(self.const_dfi_data_bytes)]
            for i in range(self.const_ddr_burst_size_max):
                with when(i == size):
                    for j in range(max(
                        self.p.dfi_bl_max//(2**(self.const_ddr_burst_size_max - i)),
                        1)):
                        valid_map(idx + j, 1)
        return valid_map

    def bl_flip_wrdata_mask(self, addr, size):
        #tmp mask = vec(gen = bits, n = self.const_dfi_data_bytes, init = 0)
        #tmp with when(size < log2_ceil(self.const_dfi_data_bytes)):
        #tmp     for i in range(self.const_dfi_data_bytes):
        #tmp         mask[i] /= 1
        #tmp     idx = addr[log2_ceil(self.const_dfi_data_bytes) - 1:0]
        #tmp     for i in range(log2_ceil(self.const_dfi_data_bytes)):
        #tmp         with when(i == size):
        #tmp             for j in range(2**i):
        #tmp                 mask(idx+j, 0)
        #tmp return mask

        return ~mask_gen(addr, size, self.const_dfi_data_bytes)

    def gen_volatile_reg(self, reg_name, reg_offset, reg_size):
        pass
        #self.cfg_reg(csr_reg_group(
        #    reg_name,
        #    offset = reg_offset,
        #    size = reg_size,
        #    fields_desc = [
        #        csr_reg_field_desc('data',  width = 32, reset = 0)]))

