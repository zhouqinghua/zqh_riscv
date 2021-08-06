import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_eth_mac_parameters import zqh_eth_mac_parameter
from .zqh_eth_mac_bundles import *
from .zqh_eth_mac_tx import zqh_eth_mac_tx
from .zqh_eth_mac_rx import zqh_eth_mac_rx
from .zqh_eth_mac_smi_main import zqh_eth_mac_smi

class zqh_eth_mac(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_eth_mac, self).set_par()
        self.p = zqh_eth_mac_parameter()

    def gen_node_tree(self):
        super(zqh_eth_mac, self).gen_node_tree()
        self.gen_node_slave(
            'mac_slave',
            tl_type = 'tl_uh', 
            bundle_p = self.p.gen_tl_bundle_p()) 
        self.p.mac_slave.print_up()
        self.p.mac_slave.print_address_space()

    def set_port(self):
        super(zqh_eth_mac, self).set_port()
        self.io.var(inp('clock_ethmac'))
        self.io.var(inp('reset_ethmac'))
        self.io.var(zqh_eth_mac_phy_gmii_smi_io('mac_phy'))

    def main(self):
        super(zqh_eth_mac, self).main()
        self.gen_node_interface('mac_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        #{{{
        self.cfg_reg(csr_reg_group(
            'mode', 
            offset = 0x0000, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('small_pkt_rx_en', width = 1, reset = 0, comments = '''\
Small Packets Receive  Enable
0 means Packets smaller than MINFL are ignored.
1 means Packets smaller than MINFL are accepted.'''),
                csr_reg_field_desc('pad_en', width = 1, reset = 1, comments = '''\
Padding Enabled
0 means Do not add pads to short frames.
1 means Add pads to short frames (until the minimum frame length is equal to MINFL)'''),
                csr_reg_field_desc('big_pkt_en', width = 1, reset = 0, comments = '''\
Big Packets Enable
0 means The maximum frame length is MAXFL. All additional bytes are discarded.
1 means Frames up 64 KB are transmitted'''),
                csr_reg_field_desc('crc_en', width = 1, reset = 1, comments = '''\
CRC Enable
0 means Tx MAC does not append the CRC (passed frames already contain the CRC.
1 means Tx MAC appends the CRC to every frame.'''),
                csr_reg_field_desc('reserved1', access = 'VOL', width = 2),
                csr_reg_field_desc('full_duplex', width = 1, reset = 0, comments = '''\
Full Duplex
0 means Half duplex mode.
1 means Full duplex mode'''),
                csr_reg_field_desc('abort_tx', width = 1, reset = 0, comments = '''\
0 menas MAC transmit waits for the carrier indefinitely.
1 means When the excessive deferral limit is reached, a transmit packet is aborted.'''),
                csr_reg_field_desc('backoff_en', width = 1, reset = 1, comments = '''\
Backoff Enable
0 menas Tx MAC starts retransmitting immediately after the collision
1 menas normal operation (a binary exponential backoff algorithm is used).'''),
                csr_reg_field_desc('loopback_en', width = 1, reset = 0, comments = '''\
Loopback Enable
0 menas Normal operation.
1 menas TX is looped back to the RX'''),
                csr_reg_field_desc('ipg_rx_en', width = 1, reset = 1, comments = '''\
Recieve check IPG enable
0 menas all frames are accepted regardless to the IPG
1 menas normal operation (minimum IPG is required for a frame to be accepted).'''),
                csr_reg_field_desc('chk_da_en', width = 1, reset = 1, comments = '''\
0 means check the destination address of the incoming frames.
1 means receive the frame regardless of its address.'''),
                csr_reg_field_desc('gmii_en', width = 1, reset = 0, comments = '''\
interface type with phy is MII/GMII
0 means MII interface
1 means GMII interface'''),
                csr_reg_field_desc('broad_rx_en', width = 1, reset = 1, comments = '''\
Broadcast Address Recieve Enable
0 menas receive all frames containing the broadcast address.
1 means reject all frames containing the broadcast address unless the chk_da_en bit = 0'''),
                csr_reg_field_desc('pre_en', width = 1, reset = 1, comments = '''\
Preamble code(7 bytes) Enable'''),
                csr_reg_field_desc('tx_en', width = 1, reset = 0, comments = '''\
Transmit Enable'''),
                csr_reg_field_desc('rx_en', width = 1, reset = 0, comments = '''\
Recieve Enable''')]))
        self.cfg_reg(csr_reg_group(
            'ip', 
            offset = 0x0004, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('smi_done', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
SMI command done
                        '''),
                csr_reg_field_desc('rx_bd_lack', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
rx packet is dropped due to lack off recieve BD'''),
                csr_reg_field_desc('rx_cf_done', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
recieve control frame done'''),
                csr_reg_field_desc('tx_cf_done', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
transmit control frame done'''),
                csr_reg_field_desc('rx_cpl_valid', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
recieve complete valid'''),
                csr_reg_field_desc('tx_cpl_valid', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
transmit complete valid'''),
                csr_reg_field_desc('rx_bd_done', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
recieve BD done'''),
                csr_reg_field_desc('tx_bd_done', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
transmit BD done''')], comments = '''\
interrupt pending'''))
        self.cfg_reg(csr_reg_group(
            'ie', 
            offset = 0x0008, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('smi_done', width = 1, reset = 0),
                csr_reg_field_desc('rx_bd_lack', width = 1, reset = 0),
                csr_reg_field_desc('rx_cf_done', width = 1, reset = 0),
                csr_reg_field_desc('tx_cf_done', width = 1, reset = 0),
                csr_reg_field_desc('rx_cpl_valid', width = 1, reset = 0),
                csr_reg_field_desc('tx_cpl_valid', width = 1, reset = 0),
                csr_reg_field_desc('rx_bd_done', width = 1, reset = 0),
                csr_reg_field_desc('tx_bd_done', width = 1, reset = 0)], comments = '''\
each interrupt source's enable'''))
        self.cfg_reg(csr_reg_group(
            'ipg', 
            offset = 0x000c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('ipg', width = 6, reset = 0, comments = '''\
Inter Packet Gap
Full Duplex: The recommended value is 0x15, which equals 0.96 µs IPG
(100 Mbps) or 9.6 µs (10 Mbps). The desired period in nibble times minus 6
should be written to the register.
Half Duplex: The recommended value and default is 0x12, which equals
0.96 µs IPG (100 Mbps) or 9.6 µs (10 Mbps). The desired period in nibble
times minus 3 should be written to the register.''')]))
        self.cfg_reg(csr_reg_group(
            'pkt_len', 
            offset = 0x0010, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('min_fl', width = 16, reset = 0x0040, comments = '''\
Minimum Frame Length'''),
                csr_reg_field_desc('max_fl', width = 16, reset = 0x0600, comments = '''\
Maximum Frame Length''')]))
        self.cfg_reg(csr_reg_group(
            'coll', 
            offset = 0x0014, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('max_retry', width = 4, reset = 0xf, comments = '''\
Maximum Retry
This field specifies the maximum number of consequential retransmission
attempts after the collision is detected. When the maximum number has
been reached, the Tx MAC reports an error and stops transmitting the
current packet'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 8),
                csr_reg_field_desc('late_coll_time', width = 8, reset = 0x3f, comments = '''\
Late Collisions Time
This field specifies a collision time window. A collision that occurs later than
the time window is reported as a »Late Collisions« and transmission of the
current packet is aborted.''')]))

        tx_bd_valid_write = reg_r('tx_bd_valid_write')
        with when(tx_bd_valid_write):
            tx_bd_valid_write /= 0
        def func_tx_bd_valid_write(reg_ptr, fire, address, size, wdata, mask_bit):
            tmp = tx_bd_valid_write
            with when(fire):
                with when(wdata[0] & mask_bit[0]):
                    tmp /= 1
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'tx_bd_l', 
            offset = 0x0020, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('len', width = 16, reset = 0, comments = '''\
Number of bytes associated with the BD to be transmitted'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 11),
                csr_reg_field_desc('pad', width = 1, reset = 0, comments = '''\
Generate PAD code for this BD's small packet or not
when mode.pad_en is valid, this bit control the current BD's packet's PAD generation
0: don't generate PAD code
1: generate PAD code'''),
                csr_reg_field_desc('crc', width = 1, reset = 0, comments = '''\
Generate CRC code for this BD's packet or not
when mode.crc_en is valid, this bit control the current BD's packet's CRC generation
0: don't generate CRC code
1: generate CRC code'''),
                csr_reg_field_desc('sai', width = 1, reset = 0, comments = '''\
Source MAC address Insert or not
0 means hardware will not auto insert Source MAC address
1 means hardware will auto insert Source MAC address'''),
                csr_reg_field_desc('irq', width = 1, reset = 0, comments = '''\
when this BD is done, report interrupt or not
0 means don't report interrupt
1 means report interrupt'''),
                csr_reg_field_desc('valid', access = 'VOL', width = 1, reset = 0, write = func_tx_bd_valid_write, comments = '''\
tx BD valid
for write: when this bit is set to 1, the tx BD will be pushed into tx BD fifo
for read: when this bit is 1, it means tx BD fifo can accept new BD, otherwise sw should not push new BD''')], comments = '''\
transmit BD's low part'''))
        self.cfg_reg(csr_reg_group(
            'tx_bd_h', 
            offset = 0x0024, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('ptr', width = 32, reset = 0, comments = '''\
Transmit Pointer
This is the buffer pointer when the associated frame is stored.''')], comments = '''\
transmit BD's high part'''))

        tx_cpl_read = bits('tx_cpl_read', init = 0)
        def func_tx_cpl_read(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                with when(mask_bit[0]):
                    tmp = tx_cpl_read
                    tmp /= 1
            return (1, 1, reg_ptr)
        self.cfg_reg(csr_reg_group(
            'tx_cpl', 
            offset = 0x0028, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('status', access = 'VOL', width = 31, reset = 0, comments = '''\
tx BD complete status info
status[11]  under_flow
status[10]  defer_abort
status[9]   too_long
status[8]   late_col
status[7:4] retry_cnt
status[3]   retry_limit
status[2]   defer
status[1]   cs_lost
status[0]   error'''),
                csr_reg_field_desc('valid', access = 'VOL', width = 1, reset = 0, read = func_tx_cpl_read, comments = '''\
tx BD complete valid
0 means this cpl status is not valid
1 means this cpl status is valid''')]))

        rx_bd_valid_write = reg_r('rx_bd_valid_write')
        with when(rx_bd_valid_write):
            rx_bd_valid_write /= 0
        def func_rx_bd_valid_write(reg_ptr, fire, address, size, wdata, mask_bit):
            tmp = rx_bd_valid_write
            with when(fire):
                with when(wdata[0] & mask_bit[0]):
                    tmp /= 1
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'rx_bd_l', 
            offset = 0x0030, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('irq', width = 1, reset = 0, comments = '''\
when this BD is done, report interrupt or not
0 means don't report interrupt
1 means report interrupt'''),
                csr_reg_field_desc('valid', access = 'VOL', width = 1, reset = 0, write = func_rx_bd_valid_write, comments = '''\
rx BD valid
for write: when this bit is set to 1, the rx BD will be pushed into rx BD fifo
for read: when this bit is 1, it means rx BD fifo can accept new BD, otherwise sw should not push new BD''')], comments = '''\
recieve BD's low part'''))
        self.cfg_reg(csr_reg_group(
            'rx_bd_h', 
            offset = 0x0034, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('ptr', width = 32, reset = 0, comments = '''\
Rransmit Pointer
This is the buffer pointer when the associated frame is stored.''')], comments = '''\
recieve BD's high part'''))

        rx_cpl_read = bits('rx_cpl_read', init = 0)
        def func_rx_cpl_read(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                with when(mask_bit[0]):
                    tmp = rx_cpl_read
                    tmp /= 1
            return (1, 1, reg_ptr)
        self.cfg_reg(csr_reg_group(
            'rx_cpl', 
            offset = 0x0038, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('len', access = 'VOL', width = 16, reset = 0, comments = '''\
rx packet's length'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 5),
                csr_reg_field_desc('status', access = 'VOL', width = 10, reset = 0, comments = '''\
status[9] over_flow(lack off rx BD)
status[8] pause(pause frame)
status[7] da_miss(dest address miss match)
status[6] ivs(invalid symbol)
status[5] dn(dribble nibble)
status[4] too_long
status[3] too_short
status[2] crc_err
status[1] late_col(late collision)
status[0] error( late_col or crc_err or too_long or dribble_nibble or invalid_symbol)'''),
                csr_reg_field_desc('valid', access = 'VOL', width = 1, reset = 0, read = func_rx_cpl_read, comments = '''\
for read, when valid is set, it means rx BD is completed.''')]))
        self.cfg_reg(csr_reg_group(
            'ctrl_cfg', 
            offset = 0x0040, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('tx_flow', width = 1, reset = 0, comments = '''\
Transmit Flow Control
0: PAUSE control frames are blocked.
1: PAUSE control frames are allowed to be sent.'''),
                csr_reg_field_desc('rx_flow', width = 1, reset = 0, comments = '''\
Receive Flow Control
0: Received PAUSE control frames are ignored.
1: The transmit function (Tx MAC) is blocked when a PAUSE control frame is received. This bit enables the RXC bit in the INT_SOURCE register.'''),
                csr_reg_field_desc('pass_all', width = 1, reset = 0, comments = '''\
Pass All Receive Frames
0:  Control frames are not passed to the host. RXFLOW must be set to 1 in order to use PAUSE control frames.
1:  All received frames are passed to the host.''')], comments = '''\
control frame configure reg'''))
        self.cfg_reg(csr_reg_group(
            'ctrl_tx', 
            offset = 0x0044, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('issue', width = 1, reset = 0x0, comments = '''\
Tx Pause Request
Writing 1 to this bit starts sending control frame procedure. Bit is automatically cleared to zero'''),
                csr_reg_field_desc('param', width = 16, reset = 0, comments = '''\
control frame's parameter''')]))
        self.cfg_reg(csr_reg_group(
            'mac_addr_l', 
            offset = 0x0048, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32)], comments = '''\
Ethernet MAC address's low 4 byte'''))
        self.cfg_reg(csr_reg_group(
            'mac_addr_h', 
            offset = 0x004c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 16)], comments = '''\
Ethernet MAC address's high 2 byte'''))
        self.cfg_reg(csr_reg_group(
            'hash_l', 
            offset = 0x0050, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0)], comments = '''\
multicast frame's hash filter's low 32 bit. 
when the indexed bit is 1, this multicast frame will be accept. or drop this frame
hash_index = dest MAC's crc value's high 6 bit.
when hash_index[5] is 0, hash_l will be indexed with hash_index[4:0]'''))
        self.cfg_reg(csr_reg_group(
            'hash_h', 
            offset = 0x0054, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0)], comments = '''\
multicast frame's hash filter's high 32 bit.
hash_index = dest MAC's crc value's high 6 bit.
when hash_index[5] is 1, hash_h will be indexed with hash_index[4:0]'''))

        self.cfg_reg(csr_reg_group(
            'smi_cfg', 
            offset = 0x0058, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('no_pre', width = 1, reset = 0, comments = '''\
No Preamble
0: 32-bit preamble sent
1: No preamble send'''),
                csr_reg_field_desc('clk_div', width = 8, reset = 0x64, comments = '''\
Clock Divider
The field is a host clock divider factor.
Fsmi = Fin/((clk_div+1)*4)''')]))
        self.cfg_reg(csr_reg_group(
            'smi_ctrl', 
            offset = 0x005c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('ready', width = 1, reset = 0, comments = '''\
write this bit to 1 will tigger smi read/write.
this bit will be automaticly cleared to 0 when smi read/write is finished.
sw can read this bit to check smi operation's done status.'''),
                csr_reg_field_desc('rw', width = 1, reset = 0x0, comments = '''\
smi read or write
0 means read
1 means write'''),
                csr_reg_field_desc('phy_addr', width = 5, reset = 0x0, comments = '''\
PHY Address'''),
                csr_reg_field_desc('reserved', access = 'VOL', width = 3),
                csr_reg_field_desc('reg_addr', width = 5, reset = 0x0, comments = '''\
PHY Register Addres''')]))
        self.cfg_reg(csr_reg_group(
            'smi_data', 
            offset = 0x0060, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 16)], comments = '''\
for smi write, this reg is data which will be write.
for smi read, this reg store the smi's read data.'''))

        self.cfg_reg(csr_reg_group(
            'fifo_status', 
            offset = 0x0064, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('rx_cpl_fifo_cnt', access = 'RO', width = 8, comments = '''\
rx BD complete fifo's current entry number'''),
                csr_reg_field_desc('rx_bd_fifo_cnt', access = 'RO', width = 8, comments = '''\
rx BD fifo's current entry number'''),
                csr_reg_field_desc('tx_cpl_fifo_cnt', access = 'RO', width = 8, comments = '''\
tx BD complete fifo's current entry number'''),
                csr_reg_field_desc('tx_bd_fifo_cnt', access = 'RO', width = 8, comments = '''\
tx BD fifo's current entry number''')]))

        tl_data_w = self.tl_in[0].a.bits.data.get_w()
        tx_buf_tl_access_en = bits('tx_buf_tl_access_en', init = 1)
        tx_buf_mem = reg_array(
            'tx_buf_mem', 
            size = self.p.tx_buf_size//(self.p.tx_fifo_data_width//8),
            data_width = self.p.tx_fifo_data_width,
            mask_width = self.p.tx_fifo_data_width//8,
            delay = 1
            )
        tx_buf_read = bits(init = 0)
        tx_buf_read_dly1 = reg_r(next = tx_buf_read)
        tx_buf_write = bits(init = 0)
        tx_buf_write_dly1 = reg_r(next = tx_buf_write)
        tx_buf_addr_lsb = bits(w = log2_up(self.p.tx_fifo_data_width//tl_data_w), init = 0)
        tx_buf_addr_lsb_dly1 = reg_r(
            w = log2_up(self.p.tx_fifo_data_width//tl_data_w),
            next = tx_buf_addr_lsb)
        tx_buf_mem.io.en /= 0
        tx_buf_mem.io.wmode /= 0
        tx_buf_mem.io.wmask /= 0
        def func_tx_buf_write(reg_ptr, fire, address, size, wdata, mask_bit):
            tmp_addr_lsb = tx_buf_addr_lsb
            tmp_addr_lsb /= address[(log2_ceil(self.p.tx_fifo_data_width//8) - 1):log2_ceil(tl_data_w//8)]
            with when(fire):
                tmp = tx_buf_write
                tmp /= 1
                tx_buf_mem.io.en /= 1
                tx_buf_mem.io.wmode /= 1
                tx_buf_mem.io.addr /= address >> log2_ceil(self.p.tx_fifo_data_width//8)
                tx_buf_mem.io.wdata /= wdata.rep(self.p.tx_fifo_data_width//tl_data_w)
                tx_buf_mem.io.wmask /= 0
                for i in range(self.p.tx_fifo_data_width//tl_data_w):
                    with when(tx_buf_addr_lsb == i):
                        tx_buf_mem.io.wmask[tl_data_w//8 * (i+1) - 1 : tl_data_w//8 * i] /= cat_rvs(map(lambda _: mask_bit[_*8], range(tl_data_w//8)))
            return (tx_buf_tl_access_en, 1)
        def func_tx_buf_read(reg_ptr, fire, address, size, mask_bit):
            tmp_addr_lsb = tx_buf_addr_lsb
            tmp_addr_lsb /= address[(log2_ceil(self.p.tx_fifo_data_width//8) - 1):log2_ceil(tl_data_w//8)]
            with when(fire):
                tmp = tx_buf_read
                tmp /= 1
                tx_buf_mem.io.en /= 1
                tx_buf_mem.io.wmode /= 0
                tx_buf_mem.io.addr /= address >> log2_ceil(self.p.tx_fifo_data_width//8)
            return (tx_buf_tl_access_en, tx_buf_read_dly1, sel_bin(tx_buf_addr_lsb_dly1, tx_buf_mem.io.rdata.grouped(tl_data_w)))
        self.cfg_reg(csr_reg_group(
            'tx_buf', 
            offset = 0x8000, 
            size = 4, 
            mem_size = self.p.tx_buf_size, 
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = 32, write = func_tx_buf_write, read = func_tx_buf_read)], comments = '''\
tx packet buffer's read/write port'''))

        rx_buf_tl_access_en = bits('rx_buf_tl_access_en', init = 1)
        rx_buf_mem = reg_array(
            'rx_buf_mem', 
            size = self.p.rx_buf_size//(self.p.rx_fifo_data_width//8),
            data_width = self.p.rx_fifo_data_width,
            mask_width = self.p.rx_fifo_data_width//8,
            delay = 1
            )
        rx_buf_read = bits(init = 0)
        rx_buf_read_dly1 = reg_r(next = rx_buf_read)
        rx_buf_write = bits(init = 0)
        rx_buf_write_dly1 = reg_r(next = rx_buf_write)
        rx_buf_addr_lsb = bits(w = log2_up(self.p.rx_fifo_data_width//tl_data_w), init = 0)
        rx_buf_addr_lsb_dly1 = reg_r(
            w = log2_up(self.p.rx_fifo_data_width//tl_data_w),
            next = rx_buf_addr_lsb)
        rx_buf_mem.io.en /= 0
        rx_buf_mem.io.wmode /= 0
        rx_buf_mem.io.wmask /= 0
        def func_rx_buf_write(reg_ptr, fire, address, size, wdata, mask_bit):
            tmp_addr_lsb = rx_buf_addr_lsb
            tmp_addr_lsb /= address[(log2_ceil(self.p.rx_fifo_data_width//8) - 1):log2_ceil(tl_data_w//8)]
            with when(fire):
                tmp = rx_buf_write
                tmp /= 1
                rx_buf_mem.io.en /= 1
                rx_buf_mem.io.wmode /= 1
                rx_buf_mem.io.addr /= address >> log2_ceil(self.p.rx_fifo_data_width//8)
                rx_buf_mem.io.wdata /= wdata.rep(self.p.rx_fifo_data_width//tl_data_w)
                rx_buf_mem.io.wmask /= 0
                for i in range(self.p.rx_fifo_data_width//tl_data_w):
                    with when(rx_buf_addr_lsb == i):
                        rx_buf_mem.io.wmask[tl_data_w//8 * (i+1) - 1 : tl_data_w//8 * i] /= cat_rvs(map(lambda _: mask_bit[_*8], range(tl_data_w//8)))
            return (rx_buf_tl_access_en, 1)
        def func_rx_buf_read(reg_ptr, fire, address, size, mask_bit):
            tmp_addr_lsb = rx_buf_addr_lsb
            tmp_addr_lsb /= address[(log2_ceil(self.p.rx_fifo_data_width//8) - 1):log2_ceil(tl_data_w//8)]
            with when(fire):
                tmp = rx_buf_read
                tmp /= 1
                rx_buf_mem.io.en /= 1
                rx_buf_mem.io.wmode /= 0
                rx_buf_mem.io.addr /= address >> log2_ceil(self.p.rx_fifo_data_width//8)
            return (rx_buf_tl_access_en, rx_buf_read_dly1, sel_bin(rx_buf_addr_lsb_dly1, rx_buf_mem.io.rdata.grouped(tl_data_w)))
        self.cfg_reg(csr_reg_group(
            'rx_buf', 
            offset = 0xc000, 
            size = 4, 
            mem_size = self.p.rx_buf_size, 
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = 32, write = func_rx_buf_write, read = func_rx_buf_read)], comments = '''\
rx packet buffer's read/write port'''))
        #}}}

        #tx control frame(pause)
        mac_tx_pause_da = list(reversed(value(0x0180C2000001, w = 48).to_bits().grouped(8)))
        mac_tx_pause_type_length = list(reversed(value(0x8808, w = 16).to_bits().grouped(8)))
        mac_tx_pause_code = list(reversed(value(0x0001, w = 16).to_bits().grouped(8)))
        mac_tx_pause_param = list(reversed(self.regs['ctrl_tx'].param.grouped(8)))
        mac_tx_pause_byte_array = vec(
            'mac_tx_pause_byte_array',
            gen = lambda _: bits(_, w = 8),
            n = 24)
        mac_tx_pause_word_array = vec(
            'mac_tx_pause_word_array',
            gen = lambda _: bits(_, w = self.p.tx_fifo_data_width),
            n = 6//(self.p.tx_fifo_data_width//32))
        for i in range(0, 6):
            mac_tx_pause_byte_array[i] /= mac_tx_pause_da[i]
        for i in range(6, 12):
            mac_tx_pause_byte_array[i] /= 0
        for i in range(12, 14):
            mac_tx_pause_byte_array[i] /= mac_tx_pause_type_length[i - 12]
        for i in range(14, 16):
            mac_tx_pause_byte_array[i] /= mac_tx_pause_code[i - 14]
        for i in range(16, 18):
            mac_tx_pause_byte_array[i] /= mac_tx_pause_param[i - 16]
        for i in range(18, len(mac_tx_pause_byte_array)):
            mac_tx_pause_byte_array[i] /= 0

        for i in range(len(mac_tx_pause_word_array)):
            idx = i*(self.p.tx_fifo_data_width//8)
            mac_tx_pause_word_array[i] /= cat_rvs(
                list(map(lambda _: mac_tx_pause_byte_array[idx + _], range(self.p.tx_fifo_data_width//8))))


        #tx_bd_fifo
        tx_bd_fifo = queue(
            'tx_bd_fifo',
            gen = zqh_eth_mac_tx_bd_bundle,
            entries = self.p.tx_bd_fifo_entries)
        tx_bd_fifo.io.enq.valid /= tx_bd_valid_write
        tx_bd_fifo.io.enq.bits.irq /= self.regs['tx_bd_l'].irq
        tx_bd_fifo.io.enq.bits.sai /= self.regs['tx_bd_l'].sai
        tx_bd_fifo.io.enq.bits.crc /= self.regs['tx_bd_l'].crc
        tx_bd_fifo.io.enq.bits.pad /= self.regs['tx_bd_l'].pad
        tx_bd_fifo.io.enq.bits.len /= self.regs['tx_bd_l'].len
        tx_bd_fifo.io.enq.bits.ptr /= self.regs['tx_bd_h'].ptr

        self.regs['tx_bd_l'].valid /= ~tx_bd_valid_write & tx_bd_fifo.io.enq.ready
        #need added the outstanding write request
        self.regs['fifo_status'].tx_bd_fifo_cnt /= tx_bd_fifo.io.count

        mac_tx_ctrl_frame = reg_r('mac_tx_ctrl_frame')
        with when(self.regs['ctrl_tx'].issue & self.regs['ctrl_cfg'].tx_flow):
            #wait normal packet bd is empty or the sending packet is done
            with when(~tx_bd_fifo.io.deq.valid | tx_bd_fifo.io.deq.fire()):
                mac_tx_ctrl_frame /= 1
        mac_tx_bd_with_pause_req = ready_valid(
            'mac_tx_bd_with_pause_req',
            gen = zqh_eth_mac_tx_bd_bundle).as_bits()
        with when(mac_tx_ctrl_frame):
            mac_tx_bd_with_pause_req.valid /= 1
            mac_tx_bd_with_pause_req.bits.sai /= 1
            mac_tx_bd_with_pause_req.bits.crc /= 1
            mac_tx_bd_with_pause_req.bits.pad /= 1
            mac_tx_bd_with_pause_req.bits.irq /= 1
            mac_tx_bd_with_pause_req.bits.len /= 18
            mac_tx_bd_with_pause_req.bits.ptr /= 0
            tx_bd_fifo.io.deq.ready /= 0
            with when(mac_tx_bd_with_pause_req.fire()):
                mac_tx_ctrl_frame /= 0
                self.regs['ctrl_tx'].issue /= 0
        with other():
            mac_tx_bd_with_pause_req /= tx_bd_fifo.io.deq

        #tx_cpl_fifo
        tx_cpl_fifo = queue(
            'tx_cpl_fifo', 
            gen = zqh_eth_mac_tx_cpl_status,
            entries = self.p.tx_cpl_fifo_entries)
        self.regs['tx_cpl'].valid /= tx_cpl_fifo.io.deq.valid
        with when(tx_cpl_fifo.io.deq.valid):
            self.regs['tx_cpl'].status /= tx_cpl_fifo.io.deq.bits.pack()
        with other():
            self.regs['tx_cpl'].status /= 0
        tx_cpl_fifo.io.deq.ready /= tx_cpl_read

        self.regs['fifo_status'].tx_cpl_fifo_cnt /= tx_cpl_fifo.io.count

        mac_tx_sel_clock = bits('mac_tx_sel_clock')
        mac_tx_sel_clock /= mux(
            self.regs['mode'].gmii_en,
            self.io.clock_ethmac,
            self.io.mac_phy.gmii.tx.clk)
        mac_tx_sync_reset = bits('mac_tx_sync_reset')
        mac_tx_sync_reset /= async_dff(
            self.io.reset_ethmac, 
            self.p.sync_delay, 
            clock = mac_tx_sel_clock)
        
        #tx request fifo
        mac_tx_fifo = async_queue(
            'mac_tx_fifo',
            gen = lambda _: zqh_eth_mac_tx_fifo_data_bundle(
                _, data_width = self.p.tx_fifo_data_width),
            entries = self.p.tx_fifo_entries,
            flush_en = 1)
        mac_tx_fifo.io.enq_clock /= self.io.clock
        mac_tx_fifo.io.enq_reset /= self.io.reset
        mac_tx_fifo.io.deq_clock /= mac_tx_sel_clock
        mac_tx_fifo.io.deq_reset /= mac_tx_sync_reset
        mac_tx_fifo.io.flush /= ~self.regs['mode'].tx_en

        #tx response status fifo
        mac_tx_status_fifo = async_ready_valid(
            'mac_tx_status_fifo',
            gen = zqh_eth_mac_tx_status_bundle,
            flush_en = 1)
        mac_tx_status_fifo.io.enq_clock /= mac_tx_sel_clock
        mac_tx_status_fifo.io.enq_reset /= mac_tx_sync_reset
        mac_tx_status_fifo.io.deq_clock /= self.io.clock
        mac_tx_status_fifo.io.deq_reset /= self.io.reset
        mac_tx_status_fifo.io.flush /= ~self.regs['mode'].tx_en

        mac_tx_status_fifo.io.deq.ready /= 1

        #tx fsm
        (
            s_tx_idle, s_tx_start, s_tx_body, s_tx_wait_resp, 
            s_tx_abort_ack, s_tx_retry_ack, s_tx_drop, s_tx_done) = range(8)
        mac_tx_state = reg_rs('mac_tx_state', w = 3, rs = s_tx_idle)
        mac_tx_byte_cnt_next = bits('mac_tx_byte_cnt_next', w = 16)
        mac_tx_byte_cnt = reg_r('mac_tx_byte_cnt', w = 16, next = mac_tx_byte_cnt_next)
        mac_tx_byte_cnt_next /= mac_tx_byte_cnt
        mac_tx_buf_byte_addr = bits('mac_tx_buf_byte_addr', w = 16)
        mac_tx_buf_byte_addr /= mac_tx_bd_with_pause_req.bits.ptr + mac_tx_byte_cnt
        mac_tx_end = mac_tx_byte_cnt_next >= mac_tx_bd_with_pause_req.bits.len
        mac_tx_status_retry = (
            mac_tx_status_fifo.io.deq.fire() & mac_tx_status_fifo.io.deq.bits.retry)
        mac_tx_status_abort = (
            mac_tx_status_fifo.io.deq.fire() & mac_tx_status_fifo.io.deq.bits.abort)
        mac_tx_status_done = (
            mac_tx_status_fifo.io.deq.fire() & mac_tx_status_fifo.io.deq.bits.done)
        tx_bd_status_cs_lost = reg('tx_bd_status_cs_lost')
        tx_bd_status_defer = reg('tx_bd_status_defer')
        tx_bd_status_late_col = reg('tx_bd_status_late_col')
        tx_bd_status_retry_limit = reg('tx_bd_status_retry_limit')
        tx_bd_status_retry_cnt = reg('tx_bd_status_retry_cnt', w = 4)
        tx_bd_status_too_long = reg('tx_bd_status_too_long')
        tx_bd_status_defer_abort = reg('tx_bd_status_defer_abort')
        with when(mac_tx_state == s_tx_idle):
            with when(self.regs['mode'].tx_en):
                with when(mac_tx_bd_with_pause_req.valid):
                    mac_tx_state /= s_tx_start
            mac_tx_byte_cnt_next /= 0
            tx_bd_status_late_col /= 0
        with when(mac_tx_state == s_tx_start):
            with when(mac_tx_status_abort):
                mac_tx_state /= s_tx_abort_ack
            with elsewhen(mac_tx_status_retry):
                mac_tx_state /= s_tx_retry_ack
            with elsewhen(mac_tx_fifo.io.enq.fire()):
                with when(mac_tx_end):
                    mac_tx_state /= s_tx_wait_resp
                with other():
                    mac_tx_state /= s_tx_body
        with when(mac_tx_state == s_tx_body):
            with when(mac_tx_status_abort):
                mac_tx_state /= s_tx_abort_ack
            with elsewhen(mac_tx_status_retry):
                mac_tx_state /= s_tx_retry_ack
            with elsewhen(mac_tx_fifo.io.enq.fire()):
                with when(mac_tx_end):
                    mac_tx_state /= s_tx_wait_resp
                with other():
                    mac_tx_state /= s_tx_body
        with when(mac_tx_state == s_tx_wait_resp):
            with when(mac_tx_status_abort):
                mac_tx_state /= s_tx_abort_ack
            with elsewhen(mac_tx_status_retry):
                mac_tx_state /= s_tx_retry_ack
            with elsewhen(mac_tx_status_done):
                mac_tx_state /= s_tx_done
        with when(mac_tx_state == s_tx_retry_ack):
            with when(mac_tx_fifo.io.enq.fire()):
                mac_tx_state /= s_tx_idle
        with when(mac_tx_state == s_tx_abort_ack):
            with when(mac_tx_fifo.io.enq.fire()):
                mac_tx_state /= s_tx_drop
        with when(mac_tx_state == s_tx_drop):
            mac_tx_state /= s_tx_idle
        with when(mac_tx_state == s_tx_done):
            mac_tx_state /= s_tx_idle

        mac_tx_state_is_start = mac_tx_state.match_any([s_tx_start])
        mac_tx_state_is_body = mac_tx_state.match_any([s_tx_body])
        mac_tx_state_is_data = mac_tx_state_is_start | mac_tx_state_is_body
        mac_tx_state_is_wait_resp = mac_tx_state.match_any([s_tx_wait_resp])
        mac_tx_state_is_drop = mac_tx_state.match_any([s_tx_drop])
        mac_tx_state_is_done = mac_tx_state.match_any([s_tx_done])
        mac_tx_state_is_ack = mac_tx_state.match_any([s_tx_abort_ack, s_tx_retry_ack])

        mac_tx_buf_read_dly = reg_r('mac_tx_buf_read_dly')
        #only valid 1 cycle
        with when(mac_tx_buf_read_dly):
            mac_tx_buf_read_dly /= 0
        with when(mac_tx_state_is_data & ~mac_tx_buf_read_dly & mac_tx_fifo.io.enq.ready):
            with when(~mac_tx_ctrl_frame):
                tx_buf_tl_access_en /= 0
                tx_buf_mem.io.en /= 1
                tx_buf_mem.io.wmode /= 0
                tx_buf_mem.io.wmask /= 0
                tx_buf_mem.io.addr /= mac_tx_buf_byte_addr >> log2_ceil(self.p.tx_fifo_data_width//8)
            mac_tx_buf_read_dly /= 1

        mac_tx_pause_word = mac_tx_pause_word_array[mac_tx_buf_byte_addr[log2_ceil(len(mac_tx_pause_word_array)) + log2_ceil(self.p.tx_fifo_data_width//8) - 1:log2_ceil(self.p.tx_fifo_data_width//8)]]

        with when(mac_tx_buf_read_dly & mac_tx_fifo.io.enq.fire()):
            mac_tx_byte_cnt_next /= mac_tx_byte_cnt + mux(
                mac_tx_state_is_start,
                self.p.tx_fifo_data_width//8 - mac_tx_bd_with_pause_req.bits.ptr[log2_ceil(self.p.tx_fifo_data_width//8) - 1:0],
                mux(mac_tx_state_is_body, self.p.tx_fifo_data_width//8, 0))

        with when(mac_tx_status_fifo.io.deq.fire()):
            tx_bd_status_defer_abort /= mac_tx_status_fifo.io.deq.bits.defer_abort
            tx_bd_status_too_long /= mac_tx_status_fifo.io.deq.bits.too_long
            tx_bd_status_retry_cnt /= mac_tx_status_fifo.io.deq.bits.retry_cnt
            tx_bd_status_retry_limit /= mac_tx_status_fifo.io.deq.bits.retry_limit
            tx_bd_status_cs_lost /= mac_tx_status_fifo.io.deq.bits.cs_lost
            tx_bd_status_defer /= mac_tx_status_fifo.io.deq.bits.defer

        int_tx_bd_done_reg = reg_r('int_tx_bd_done_reg')
        with when(~self.regs['ip'].tx_bd_done):
            with when(int_tx_bd_done_reg):
                self.regs['ip'].tx_bd_done /= 1
                int_tx_bd_done_reg /= 0

        int_tx_cf_done_reg = reg_r('int_tx_cf_done_reg')
        with when(~self.regs['ip'].tx_cf_done):
            with when(int_tx_cf_done_reg):
                self.regs['ip'].tx_cf_done /= 1
                int_tx_cf_done_reg /= 0


        mac_tx_bd_with_pause_req.ready /= 0
        tx_cpl_fifo.io.enq.valid /= 0
        tx_bd_status_error = (
            tx_bd_status_cs_lost | 
            tx_bd_status_late_col | 
            tx_bd_status_retry_limit | 
            tx_bd_status_defer_abort)
        with when(mac_tx_state_is_done | mac_tx_state_is_drop):
            mac_tx_bd_with_pause_req.ready /= 1
            with when(~mac_tx_ctrl_frame):
                tx_cpl_fifo.io.enq.valid /= 1
                with when(mac_tx_bd_with_pause_req.bits.irq):
                    int_tx_bd_done_reg /= 1
            with other():
                with when(
                    mac_tx_bd_with_pause_req.bits.irq & 
                    self.regs['ctrl_cfg'].rx_flow):
                    int_tx_cf_done_reg /= 1
        tx_cpl_fifo.io.enq.bits.error /= tx_bd_status_error
        tx_cpl_fifo.io.enq.bits.cs_lost /= tx_bd_status_cs_lost
        tx_cpl_fifo.io.enq.bits.defer /= tx_bd_status_defer
        tx_cpl_fifo.io.enq.bits.late_col /= tx_bd_status_late_col
        tx_cpl_fifo.io.enq.bits.retry_limit /= tx_bd_status_retry_limit
        tx_cpl_fifo.io.enq.bits.retry_cnt /= tx_bd_status_retry_cnt
        tx_cpl_fifo.io.enq.bits.too_long /= tx_bd_status_too_long
        tx_cpl_fifo.io.enq.bits.defer_abort /= tx_bd_status_defer_abort
        tx_cpl_fifo.io.enq.bits.under_flow /= 0

        self.regs['ip'].tx_cpl_valid /= tx_cpl_fifo.io.count != 0

        mac_tx_fifo.io.enq.bits.data /= mux(
            mac_tx_ctrl_frame,
            mac_tx_pause_word,
            tx_buf_mem.io.rdata)
        mac_tx_fifo.io.enq.bits.start /= mux(
            mac_tx_state_is_start,
            bin2oh(mac_tx_buf_byte_addr[log2_ceil(self.p.tx_fifo_data_width//8) - 1:0]),
            mux(mac_tx_state_is_ack, 1, 0))
        mac_tx_fifo.io.enq.bits.end /= mux(
            mac_tx_state_is_data & mac_tx_end,
            bin2oh((
                mac_tx_bd_with_pause_req.bits.len[log2_ceil(self.p.tx_fifo_data_width//8) - 1:0] + 
                mac_tx_bd_with_pause_req.bits.ptr[log2_ceil(self.p.tx_fifo_data_width//8) - 1:0] - 1)[log2_ceil(self.p.tx_fifo_data_width//8) - 1:0]),
            mux(mac_tx_state_is_ack, 1, 0))
        mac_tx_fifo.io.enq.bits.sai /= mac_tx_bd_with_pause_req.bits.sai
        mac_tx_fifo.io.enq.bits.crc /= mac_tx_bd_with_pause_req.bits.crc
        mac_tx_fifo.io.enq.bits.pad /= mac_tx_bd_with_pause_req.bits.pad
        mac_tx_fifo.io.enq.bits.ack /= mac_tx_state_is_ack

        mac_tx_fifo.io.enq.valid /= 0
        with when(mac_tx_buf_read_dly | mac_tx_state_is_ack):
            mac_tx_fifo.io.enq.valid /= 1


        ####
        #mac_tx
        mac_tx_pause_from_rx = bits('mac_tx_pause_from_rx')
        mac_tx = zqh_eth_mac_tx('mac_tx')
        mac_tx.io.clock /= mac_tx_sel_clock
        mac_tx.io.reset /= mac_tx_sync_reset
        mac_tx.io.ap_tx /= mac_tx_fifo.io.deq
        self.io.mac_phy.gmii.tx /= mac_tx.io.phy_gmii_tx
        mac_tx.io.phy_gmii_cscd /= self.io.mac_phy.gmii.cscd
        mac_tx.io.pause /= mac_tx_pause_from_rx
        mac_tx.io.cfg_reg_gmii_en/= self.regs['mode'].gmii_en
        mac_tx.io.cfg_reg_loopback_en/= self.regs['mode'].loopback_en
        mac_tx.io.cfg_reg_backoff_en /= self.regs['mode'].backoff_en
        mac_tx.io.cfg_reg_abort_tx /= self.regs['mode'].abort_tx
        mac_tx.io.cfg_reg_full_duplex /= self.regs['mode'].full_duplex
        mac_tx.io.cfg_reg_crc_en /= self.regs['mode'].crc_en
        mac_tx.io.cfg_reg_big_pkt_en /= self.regs['mode'].big_pkt_en
        mac_tx.io.cfg_reg_pad_en /= self.regs['mode'].pad_en
        mac_tx.io.cfg_reg_ipg /= self.regs['ipg'].ipg
        mac_tx.io.cfg_reg_max_retry /= self.regs['coll'].max_retry
        mac_tx.io.cfg_reg_max_fl /= self.regs['pkt_len'].max_fl
        mac_tx.io.cfg_reg_mac_addr /= cat([
            self.regs['mac_addr_h'].value,
            self.regs['mac_addr_l'].value])

        mac_tx_status_fifo.io.enq /= mac_tx.io.ap_tx_status


        #rx_bd_fifo
        rx_bd_fifo = queue(
            'rx_bd_fifo',
            gen = zqh_eth_mac_rx_bd_bundle, 
            entries = self.p.rx_bd_fifo_entries)
        rx_bd_fifo.io.enq.valid /= rx_bd_valid_write
        rx_bd_fifo.io.enq.bits.irq /= self.regs['rx_bd_l'].irq
        rx_bd_fifo.io.enq.bits.ptr /= self.regs['rx_bd_h'].ptr

        self.regs['rx_bd_l'].valid /= ~rx_bd_valid_write & rx_bd_fifo.io.enq.ready
        #need added the outstanding write request
        self.regs['fifo_status'].rx_bd_fifo_cnt /= rx_bd_fifo.io.count

        #rx_cpl_fifo
        rx_cpl_fifo = queue(
            'rx_cpl_fifo', 
            gen = zqh_eth_mac_rx_cpl_status,
            entries = self.p.rx_cpl_fifo_entries)
        self.regs['rx_cpl'].valid /= rx_cpl_fifo.io.deq.valid
        with when(rx_cpl_fifo.io.deq.valid):
            self.regs['rx_cpl'].status /= rx_cpl_fifo.io.deq.bits.pack()
            self.regs['rx_cpl'].len /= rx_cpl_fifo.io.deq.bits.len
        with other():
            self.regs['rx_cpl'].status /= 0
            self.regs['rx_cpl'].len /= 0
        rx_cpl_fifo.io.deq.ready /= rx_cpl_read

        self.regs['fifo_status'].rx_cpl_fifo_cnt /= rx_cpl_fifo.io.count

        ####
        #mac_rx
        mac_rx_sync_reset = bits('mac_rx_sync_reset')
        mac_rx_sync_reset /= async_dff(
            self.io.reset_ethmac, 
            self.p.sync_delay, 
            clock = self.io.mac_phy.gmii.rx.clk)
        #mac_rx_sync_reset /= self.io.reset_ethmac

        mac_rx = zqh_eth_mac_rx('mac_rx')
        mac_rx.io.clock /= self.io.mac_phy.gmii.rx.clk
        mac_rx.io.reset /= mac_rx_sync_reset
        mac_rx.io.phy_gmii_rx /= self.io.mac_phy.gmii.rx
        mac_rx.io.phy_gmii_cscd /= self.io.mac_phy.gmii.cscd
        mac_rx.io.transmitting /= mac_tx.io.transmitting
        mac_rx.io.cfg_reg_gmii_en /= self.regs['mode'].gmii_en
        mac_rx.io.cfg_reg_rx_en /= self.regs['mode'].rx_en
        mac_rx.io.cfg_reg_min_fl /= self.regs['pkt_len'].min_fl
        mac_rx.io.cfg_reg_max_fl /= self.regs['pkt_len'].max_fl
        mac_rx.io.cfg_reg_ipg_rx_en /= self.regs['mode'].ipg_rx_en
        mac_rx.io.cfg_reg_big_pkt_en /= self.regs['mode'].big_pkt_en
        mac_rx.io.cfg_reg_small_pkt_rx_en /= self.regs['mode'].small_pkt_rx_en
        mac_rx.io.cfg_reg_mac_addr /= cat([
            self.regs['mac_addr_h'].value, 
            self.regs['mac_addr_l'].value])
        mac_rx.io.cfg_reg_multicast_hash /= cat([
            self.regs['hash_h'].value, 
            self.regs['hash_l'].value])
        mac_rx.io.cfg_reg_chk_da_en /= self.regs['mode'].chk_da_en
        mac_rx.io.cfg_reg_bro_rx_en /= self.regs['mode'].broad_rx_en
        mac_rx.io.cfg_reg_pass_all /= self.regs['ctrl_cfg'].pass_all
        mac_rx.io.cfg_reg_rx_flow /= self.regs['ctrl_cfg'].rx_flow
        mac_rx.io.cfg_reg_full_duplex /= self.regs['mode'].full_duplex

        mac_tx_pause_from_rx /= mac_rx.io.pause

        #rx request fifo
        mac_rx_fifo = async_queue(
            'mac_rx_fifo',
            gen = lambda _: zqh_eth_mac_rx_fifo_data_bundle(
                _, data_width = self.p.rx_fifo_data_width),
            entries = self.p.rx_fifo_entries,
            flush_en = 1)
        mac_rx_fifo.io.enq_clock /= self.io.mac_phy.gmii.rx.clk
        mac_rx_fifo.io.enq_reset /= mac_rx_sync_reset
        mac_rx_fifo.io.deq_clock /= self.io.clock
        mac_rx_fifo.io.deq_reset /= self.io.reset
        mac_rx_fifo.io.flush /= ~self.regs['mode'].rx_en

        mac_rx_fifo.io.enq /= mac_rx.io.ap_rx

        #TBD mac_rx_fifo.io.deq.ready /= self.regs['mode'].rx_en & rx_bd_fifo.io.deq.valid
        mac_rx_fifo.io.deq.ready /= 1 #should not block this fifo


        #store rx data into rx_bd's memory
        (s_rx_idle, s_rx_data, s_rx_status, s_rx_done) = range(4)
        mac_rx_state = reg_rs('mac_rx_state', w = 3, rs = s_rx_idle)
        mac_rx_no_bd = reg_r('mac_rx_no_bd')
        mac_rx_byte_cnt_next = bits('mac_rx_byte_cnt_next', w = 16)
        mac_rx_byte_cnt = reg_r('mac_rx_byte_cnt', w = 16, next = mac_rx_byte_cnt_next)
        mac_rx_byte_cnt_next /= mac_rx_byte_cnt
        mac_rx_buf_byte_addr = bits('mac_rx_buf_byte_addr', w = 16)
        mac_rx_buf_byte_addr /= rx_bd_fifo.io.deq.bits.ptr + mac_rx_byte_cnt
        #mac_rx_buf_wmask = bits('mac_rx_buf_wmask', w = 4)
        #mac_rx_buf_wdata = bits('mac_rx_buf_wdata', w = 32)
        with when(mac_rx_state == s_rx_idle):
            mac_rx_byte_cnt_next /= 0
            #tmp with when(rx_bd_fifo.io.deq.valid):
            #tmp     with when(mac_rx_fifo.io.deq.fire() & mac_rx_fifo.io.deq.bits.start):
            #tmp         mac_rx_state /= s_rx_data
            with when(mac_rx_fifo.io.deq.fire() & mac_rx_fifo.io.deq.bits.start):
                mac_rx_state /= s_rx_data
                with when(~rx_bd_fifo.io.deq.valid):
                    mac_rx_no_bd /= 1
                with other():
                    mac_rx_no_bd /= 0
        with when(mac_rx_state == s_rx_data):
            with when(mac_rx_fifo.io.deq.fire() & mac_rx_fifo.io.deq.bits.is_status):
                mac_rx_state /= s_rx_status
        with when(mac_rx_state == s_rx_status):
            mac_rx_state /= s_rx_done
        with when(mac_rx_state == s_rx_done):
            mac_rx_state /= s_rx_idle

        mac_rx_state_is_data = mac_rx_state.match_any([s_rx_data])
        mac_rx_state_is_status = mac_rx_state.match_any([s_rx_status])
        rx_bd_fifo.io.deq.ready /= 0
        rx_cpl_fifo.io.enq.valid /= 0
        rx_fifo_deq_data_grouped = mac_rx_fifo.io.deq.bits.data.grouped(8)
        rx_fifo_deq_data_reg = reg(
            'rx_fifo_deq_data_reg', 
            w = mac_rx_fifo.io.deq.bits.data.get_w())
        with when(mac_rx_fifo.io.deq.fire()):
            rx_fifo_deq_data_reg /= mac_rx_fifo.io.deq.bits.data
        rx_fifo_deq_data_reg_grouped = rx_fifo_deq_data_reg.grouped(8)
        end_wmask_shift = cat_rvs(map(
            lambda _: (
                mac_rx_fifo.io.deq.bits.end << 
                rx_bd_fifo.io.deq.bits.ptr[log2_ceil(self.p.rx_fifo_data_width//8) - 1:0])[self.p.rx_fifo_data_width//8 * 2 - 2:_].r_or(), 
            range(self.p.rx_fifo_data_width//8 * 2 - 1)))
        end_wmask_tail_reg = reg('end_wmask_tail_reg', w = self.p.rx_fifo_data_width//8)
        with when(mac_rx_fifo.io.deq.fire()):
            with when(~mac_rx_fifo.io.deq.bits.is_status):
                mac_rx_byte_cnt_next /= mac_rx_byte_cnt + mux(
                    mac_rx_fifo.io.deq.bits.end != 0,
                    oh2bin(mac_rx_fifo.io.deq.bits.end << 1),
                    self.p.rx_fifo_data_width//8)

            end_wmask_tail_reg /= (end_wmask_shift >> self.p.rx_fifo_data_width//8).u_ext(self.p.rx_fifo_data_width//8)
            with when(~mac_rx_fifo.io.deq.bits.is_status):
                rx_buf_tl_access_en /= 0
                #tmp rx_buf_mem.io.en /= 1
                rx_buf_mem.io.en /= ~mac_rx_no_bd
                rx_buf_mem.io.wmode /= 1
                start_wmask = ((2**(self.p.rx_fifo_data_width//8) - 1) << rx_bd_fifo.io.deq.bits.ptr[log2_ceil(self.p.rx_fifo_data_width//8) - 1:0])[self.p.rx_fifo_data_width//8 - 1:0]
                end_wmask = end_wmask_shift[self.p.rx_fifo_data_width//8 - 1:0]
                rx_buf_mem.io.wmask /= mux(
                    mac_rx_fifo.io.deq.bits.start,
                    start_wmask,
                    mux(mac_rx_fifo.io.deq.bits.end != 0, 
                        end_wmask,
                        2**(self.p.rx_fifo_data_width//8) - 1))
            with elsewhen(end_wmask_tail_reg != 0):
                rx_buf_tl_access_en /= 0
                #tmp rx_buf_mem.io.en /= 1
                rx_buf_mem.io.en /= ~mac_rx_no_bd
                rx_buf_mem.io.wmode /= 1
                rx_buf_mem.io.wmask /= end_wmask_tail_reg
            rx_buf_mem.io.addr /= mac_rx_buf_byte_addr >> log2_ceil(self.p.rx_fifo_data_width//8)
            rx_buf_mem.io.wdata /= sel_bin(
                rx_bd_fifo.io.deq.bits.ptr[log2_ceil(self.p.rx_fifo_data_width//8) - 1:0],
                map(
                    lambda ptr: cat_rvs(
                        map(
                            lambda _: rx_fifo_deq_data_grouped[_ - ptr] 
                                if (_ >= ptr) else 
                                rx_fifo_deq_data_reg_grouped[
                                    len(rx_fifo_deq_data_grouped) - ptr + _],
                            range(len(rx_fifo_deq_data_grouped)))),
                    range(len(rx_fifo_deq_data_grouped))))

        int_rx_bd_done_reg = reg_r('int_rx_bd_done_reg')
        with when(~self.regs['ip'].rx_bd_done):
            with when(int_rx_bd_done_reg):
                self.regs['ip'].rx_bd_done /= 1
                int_rx_bd_done_reg /= 0
        int_rx_cf_done_reg = reg_r('int_rx_cf_done_reg')
        with when(~self.regs['ip'].rx_cf_done):
            with when(int_rx_cf_done_reg):
                self.regs['ip'].rx_cf_done /= 1
                int_rx_cf_done_reg /= 0

        rx_status_dec = zqh_eth_mac_rx_status_bundle(init = mac_rx_fifo.io.deq.bits.data)
        rx_status_error = (
            rx_status_dec.late_collision |
            rx_status_dec.crc_err |
            rx_status_dec.long_frame |
            rx_status_dec.dribble_nibble |
            rx_status_dec.invalid_symbol)
        with when(mac_rx_fifo.io.deq.fire()):
            with when(mac_rx_fifo.io.deq.bits.is_status):
                with when(~rx_status_dec.abort):
                    #tmp rx_bd_fifo.io.deq.ready /= 1
                    rx_bd_fifo.io.deq.ready /= ~mac_rx_no_bd
                    #tmp rx_cpl_fifo.io.enq.valid /= 1
                    rx_cpl_fifo.io.enq.valid /= ~mac_rx_no_bd
                    with when(rx_bd_fifo.io.deq.bits.irq & ~mac_rx_no_bd):
                        with when(
                            ~rx_status_dec.pause_frame | 
                            (
                                self.regs['ctrl_cfg'].pass_all & 
                                ~self.regs['ctrl_cfg'].rx_flow)):
                            int_rx_bd_done_reg /= 1
        with when(
            (mac_rx_fifo.io.deq.valid & ~mac_rx_fifo.io.deq.ready) & 
            mac_rx_fifo.io.deq.bits.start):
            self.regs['ip'].rx_bd_lack /= 1

        rx_pause_sync = async_dff(mac_rx.io.pause, self.p.sync_delay)
        rx_pause_sync_dly1 = reg(next = rx_pause_sync)
        rx_pause_sync_pos = rx_pause_sync & ~rx_pause_sync_dly1
        with when(rx_pause_sync_pos & self.regs['ctrl_cfg'].rx_flow):
            int_rx_cf_done_reg /= 1

        rx_cpl_fifo.io.enq.bits.error /= rx_status_error
        rx_cpl_fifo.io.enq.bits.late_col /= rx_status_dec.late_collision
        rx_cpl_fifo.io.enq.bits.crc_err /= rx_status_dec.crc_err
        rx_cpl_fifo.io.enq.bits.too_short /= rx_status_dec.short_frame
        rx_cpl_fifo.io.enq.bits.too_long /= rx_status_dec.long_frame
        rx_cpl_fifo.io.enq.bits.dn /= rx_status_dec.dribble_nibble
        rx_cpl_fifo.io.enq.bits.ivs /= rx_status_dec.invalid_symbol
        rx_cpl_fifo.io.enq.bits.da_miss /= rx_status_dec.da_miss
        rx_cpl_fifo.io.enq.bits.pause /= rx_status_dec.pause_frame
        rx_cpl_fifo.io.enq.bits.over_flow /= 0
        rx_cpl_fifo.io.enq.bits.len /= mac_rx_byte_cnt

        self.regs['ip'].rx_cpl_valid /= rx_cpl_fifo.io.count != 0


        ####
        #gmii management smi
        mac_smi = zqh_eth_mac_smi(
            'mac_smi', 
            clk_div_w = self.regs['smi_cfg'].clk_div.get_w())
        mac_smi.io.cfg_clk_div /= self.regs['smi_cfg'].clk_div
        mac_smi.io.cfg_no_pre /= self.regs['smi_cfg'].no_pre
        mac_smi.io.ctrl_ready /= self.regs['smi_ctrl'].ready
        mac_smi.io.ctrl_rw /= self.regs['smi_ctrl'].rw
        mac_smi.io.ctrl_phy_addr /= self.regs['smi_ctrl'].phy_addr
        mac_smi.io.ctrl_reg_addr /= self.regs['smi_ctrl'].reg_addr
        mac_smi.io.ctrl_wdata /= self.regs['smi_data'].value
        with when(mac_smi.io.ctrl_done):
            self.regs['smi_ctrl'].ready /= 0
            self.regs['ip'].smi_done /= 1
            with when(~self.regs['smi_ctrl'].rw):
                self.regs['smi_data'].value /= mac_smi.io.ctrl_rdata
        self.io.mac_phy.smi /= mac_smi.io.smi

        
        #phy reset_n signal
        self.io.mac_phy.reset_n /= ~self.io.reset_ethmac


        ####
        #interrupt
        self.int_out[0] /= (
            (self.regs['ip'].smi_done     & self.regs['ie'].smi_done    ) | 
            (self.regs['ip'].rx_bd_lack   & self.regs['ie'].rx_bd_lack  ) | 
            (self.regs['ip'].rx_cf_done   & self.regs['ie'].rx_cf_done  ) | 
            (self.regs['ip'].tx_cf_done   & self.regs['ie'].tx_cf_done  ) | 
            (self.regs['ip'].rx_cpl_valid & self.regs['ie'].rx_cpl_valid) | 
            (self.regs['ip'].tx_cpl_valid & self.regs['ie'].tx_cpl_valid) | 
            (self.regs['ip'].rx_bd_done   & self.regs['ie'].rx_bd_done  ) | 
            (self.regs['ip'].tx_bd_done   & self.regs['ie'].tx_bd_done  ))
