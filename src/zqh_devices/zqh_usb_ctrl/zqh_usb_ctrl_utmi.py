from phgl_imp import *
from .zqh_usb_ctrl_parameters import zqh_usb_ctrl_parameter
from .zqh_usb_ctrl_bundles import *
from zqh_usb_phy.zqh_usb_phy_common_bundles import zqh_usb_utmi_l1
from .zqh_usb_ctrl_misc import *

class zqh_usb_ctrl_utmi(csr_module):
    def set_par(self):
        super(zqh_usb_ctrl_utmi, self).set_par()
        self.p = zqh_usb_ctrl_parameter()

    def set_port(self):
        super(zqh_usb_ctrl_utmi, self).set_port()
        self.io.var(csr_reg_io(
            'reg',
            addr_bits = 9,
            data_bits = 32))
        self.io.var(zqh_usb_utmi_l1('utmi', dw = 8).flip())
        self.io.var(ready_valid('host_data_tx', lambda _: zqh_usb_ctrl_utmi_tx_data(_, dw = 8)).flip())
        self.io.var(vec('device_data_tx', lambda _: ready_valid(_, lambda _: zqh_usb_ctrl_utmi_tx_data(_, dw = 8)).flip(), self.p.device_ep_num))
        self.io.var(ready_valid('data_rx', lambda _: zqh_usb_ctrl_utmi_rx_data(_, dw = 8, ep_num = self.p.device_ep_num)))
        self.io.var(inp('cfg_mode')) #0: device, 1: host
        self.io.var(inp('cfg_trans_en'))
        self.io.var(outp('host_int_trans_done'))
        self.io.var(outp('host_int_resume'))
        self.io.var(outp('host_int_con_event'))
        self.io.var(outp('host_int_discon_event'))
        self.io.var(outp('host_int_sof_sent'))
        self.io.var(outp('device_int_trans_done'))
        self.io.var(outp('device_int_resume'))
        self.io.var(outp('device_int_reset_event'))
        self.io.var(outp('device_int_sof_recv'))
        self.io.var(outp('device_int_nak_sent'))
        self.io.var(outp('device_int_stall_sent'))
        self.io.var(outp('device_int_vbus_det'))

    def main(self):
        super(zqh_usb_ctrl_utmi, self).main()

        self.reg_if = self.io.reg

        #cfg regs
        #{{{
        self.cfg_reg(csr_reg_group(
            'host_control', 
            offset = 0x000, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('out_zero_len', width = 1, reset = 0, comments = '''\
Set to 1 means current OUT TRANS is zero length pkt.'''),
                csr_reg_field_desc('trans_type', width = 2, reset = 0, comments = '''\
SETUP_TRANS = 0
IN_TRANS = 1
OUTDATA0_TRANS = 2
OUTDATA1_TRANS = 3'''),
                csr_reg_field_desc('reserved', width = 3, access = 'VOL'),
                csr_reg_field_desc('sof_en', width = 1, reset = 0, comments = '''\
setting this bit to 1 to enables automatic transmission of SOF tokens every 1mS.'''),
                csr_reg_field_desc('iso_en', width = 1, reset = 0, comments = '''\
Set to 1 to enable isochronous mode.  In isochronous mode, no acknowledgements are sent or received.'''),
                csr_reg_field_desc('preamble_en', width = 1, reset = 0, comments = '''\
Set to 1 to enable preamble.'''),
                csr_reg_field_desc('sof_sync', width = 1, reset = 0, comments = '''\
Set to 1 to syncrhonize transaction with the end of SOF transmission.Transaction will be scheduled for transmission immediately after SOF transmission.'''),
                csr_reg_field_desc('trans_req', width = 1, reset = 0, comments = '''\
Set to 0 to disable transaction. Set to 1 to enable transaction, automatically cleared when transaction complete.''')]))
        self.cfg_reg(csr_reg_group(
            'host_tx_line_control', 
            offset = 0x004, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('tx_bitstuff_enable', width = 1, reset = 0, comments = '''\
UTMI's tx_bitstuff_enable input.'''),
                csr_reg_field_desc('dischrg_vbus', width = 1, reset = 0, comments = '''\
UTMI's dischrg_vbus input.'''),
                csr_reg_field_desc('chrg_vbus', width = 1, reset = 0, comments = '''\
UTMI's chrg_vbus input.'''),
                csr_reg_field_desc('drv_vbus', width = 1, reset = 1, comments = '''\
UTMI's drv_vbus input.'''),
                csr_reg_field_desc('dm_pulldown', width = 1, reset = 1, comments = '''\
UTMI's dm_pulldown input.'''),
                csr_reg_field_desc('dp_pulldown', width = 1, reset = 1, comments = '''\
UTMI's dp_pulldown input.'''),
                csr_reg_field_desc('id_pullup', width = 1, reset = 1, comments = '''\
UTMI's id_pullup input.'''),
                csr_reg_field_desc('opmode', width = 2, reset = 0, comments = '''\
UTMI's opmode input.'''),
                csr_reg_field_desc('suspend_m', width = 1, reset = 1, comments = '''\
UTMI's suspend_m input.'''),
                csr_reg_field_desc('term_select', width = 1, reset = 1, comments = '''\
UTMI's term_select input.'''),
                csr_reg_field_desc('xcvr_select', width = 1, reset = 1, comments = '''\
UTMI's xcvr_select input.'''),
                csr_reg_field_desc('full_speed_line_rate', width = 1, reset = 0, comments = '''\
Set to 1 to enable full speed line rate of 12Mbps. Clear to 0 to enable low speed line rate of 1.5Mbps. If the host is communicating with a full speed device, then full speed line rate should be enabled. If the host is communicating with a low speed device full speed line rate should be disabled.'''),
                csr_reg_field_desc('full_speed_line_polarity', width = 1, reset = 0, comments = '''\
Set to 1 to enable full speed line polarity. That is J= differential 1, K= differential 0. 
Clear to zero to enable low speed line poarity. That is J= differential 0, K= differential 1.  
If the host is communicating with a full speed device, then full speed line polarity should be enabled. If the host is communicating with a low speed device directly then full speed line polarity should be disabled. If the host is communicating with a low speed device via a hub, then full speed line polarity should be enabled.'''),
                csr_reg_field_desc('direct_control', width = 1, reset = 0, comments = '''\
Set to 1 to allow direct control the state of the USB physical wires. Clear to 0 for normal operation.'''),
                csr_reg_field_desc('tx_line_state', width = 2, reset = 0, comments = '''\
When direct_control =1,tx_line_state directly controls the state of the USB physical wires, where;
0: SE0
1: DATA0
2: DATA1
3: reserved''')]))
        self.cfg_reg(csr_reg_group(
            'host_tx_addr', 
            offset = 0x008, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('endp', width = 4, reset = 0, comments = '''\
Endpoint address.'''),
                csr_reg_field_desc('reserved', width = 1, access = 'VOL'),
                csr_reg_field_desc('addr', width = 7, reset = 0, comments = '''\
USB Device address.''')]))
        self.cfg_reg(csr_reg_group(
            'host_tx_frame_num', 
            offset = 0x00c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 11, reset = 0, comments = '''\
the frame number used for SOF transmission.''')]))
        self.cfg_reg(csr_reg_group(
            'host_tx_sof_timer', 
            offset = 0x010, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 32, reset = 0, comments = '''\
the SOF timer used for SOF transmission. Timer is incremented
at 48MHz, thus there are 48000 ticks in a 1mS frame.''')]))
        self.cfg_reg(csr_reg_group(
            'host_rx_status', 
            offset = 0x014, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data_seq', width = 1, reset = 0, comments = '''\
If the last transaction was of type IN_TRANS, then this bit indicates the sequence number of the last receive packet. DATA0 = 0, DATA1 = 1.'''),
                csr_reg_field_desc('ack_recved', width = 1, reset = 0, comments = '''\
When set to 1, indicates ACK received from USB device.'''),
                csr_reg_field_desc('stall_recved', width = 1, reset = 0, comments = '''\
When set to 1, indicates STALL received from USB device.'''),
                csr_reg_field_desc('nak_recved', width = 1, reset = 0, comments = '''\
When set to 1, indicates NAK received from USB device.'''),
                csr_reg_field_desc('rx_time_out', width = 1, reset = 0, comments = '''\
When set to 1, indicates no response from USB device.'''),
                csr_reg_field_desc('rx_overflow', width = 1, reset = 0, comments = '''\
When set to 1, indicates insufficient free space in RX fifo to accept entire data packet.'''),
                csr_reg_field_desc('bit_stuff_error', width = 1, reset = 0, comments = '''\
When set to 1, indicates bit stuff error detected on the last transaction.'''),
                csr_reg_field_desc('crc_error', width = 1, reset = 0, comments = '''\
When set to 1, indicates CRC error detected on the last transaction.''')]))
        self.cfg_reg(csr_reg_group(
            'host_rx_pid', 
            offset = 0x018, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 8, reset = 0, commments = '''\
Packet identifier for the last packet received.''')]))
        self.cfg_reg(csr_reg_group(
            'host_rx_addr', 
            offset = 0x01c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('endp', width = 4, reset = 0, comments = '''\
End point from which the last receive packet was sent.'''),
                csr_reg_field_desc('reserved', width = 1, access = 'VOL'),
                csr_reg_field_desc('addr', width = 7, reset = 0, comments = '''\
Address from which the last receive packet was sent.''')]))
        self.cfg_reg(csr_reg_group(
            'host_connect_state', 
            offset = 0x020, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('rx_line_state', width = 2, reset = 0, comments = '''\
UTMI's rx_line_state output.''')]))
        self.cfg_reg(csr_reg_group(
            'host_trans_timeout_cnt', 
            offset = 0x024, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 16, reset = 1000, comments = '''\
host transaction timeout MAX tick value at 48MHz.''')]))
        self.cfg_reg(csr_reg_group(
            'device_tx_line_control', 
            offset = 0x100, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('opmode', width = 2, reset = 0, comments = '''\
UTMI's opmode input.'''),
                csr_reg_field_desc('suspend_m', width = 1, reset = 1, comments = '''\
UTMI's suspend_m input.'''),
                csr_reg_field_desc('term_select', width = 1, reset = 1, comments = '''\
UTMI's term_select input.'''),
                csr_reg_field_desc('xcvr_select', width = 1, reset = 1, comments = '''\
UTMI's xcvr_select input.'''),
                csr_reg_field_desc('connect_to_host', width = 1, reset = 0),
                csr_reg_field_desc('full_speed_line_rate', width = 1, reset = 0, comments = '''\
Set to 1 to enable full speed line rate of 12Mbps. Clear to 0 to enable low speed line rate of 1.5Mbps. If the host is communicating with a full speed device, then full speed line rate should be enabled. If the host is communicating with a low speed device full speed line rate should be disabled.'''),
                csr_reg_field_desc('full_speed_line_polarity', width = 1, reset = 0, comments = '''\
Set to 1 to enable full speed line polarity. That is J= differential 1, K= differential 0. 
Clear to zero to enable low speed line poarity. That is J= differential 0, K= differential 1.  
If the host is communicating with a full speed device, then full speed line polarity should be enabled. If the host is communicating with a low speed device directly then full speed line polarity should be disabled. If the host is communicating with a low speed device via a hub, then full speed line polarity should be enabled.'''),
                csr_reg_field_desc('direct_control', width = 1, reset = 0, comments = '''\
Set to 1 to allow direct control the state of the USB physical wires. Clear to 0 for normal operation.'''),
                csr_reg_field_desc('tx_line_state', width = 2, reset = 0, comments = '''\
When direct_control =1,tx_line_state directly controls the state of the USB physical wires, where;
0: SE0
1: DATA0
2: DATA1
3: reserved''')]))
        self.cfg_reg(csr_reg_group(
            'device_connect_state', 
            offset = 0x104, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('rx_line_state', width = 2, reset = 0, comments = '''\
UTMI's LineState''')]))
        self.cfg_reg(csr_reg_group(
            'device_addr', 
            offset = 0x108, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 7, reset = 0, comments = '''\
USB Device address.''')]))
        self.cfg_reg(csr_reg_group(
            'device_frame_num',
            offset = 0x110, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 11, reset = 0, comments = '''\
the frame number received in the last SOF transmission.''')]))
        self.cfg_reg(csr_reg_group(
            'device_trans_timeout_cnt', 
            offset = 0x114, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 16, reset = 1000, comments = '''\
device transaction timeout MAX tick value at 48MHz.''')]))


        device_control_reg_array = []
        device_status_reg_array = []
        for i in range(self.p.device_ep_num):
            suffix_str = '_ep' + str(i)
            addr_base = 0x140 + 8*i

            device_control_reg = self.cfg_reg(csr_reg_group(
                'device_control'+suffix_str, 
                offset = 0x000+addr_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('iso_en', width = 1, reset = 0, comments = '''\
Set to 1 to enable isochronous transfers. In isochronous mode the endpoint does not send acknowledgements, nor does it expect to receive acknowledgements.'''),
                    csr_reg_field_desc('send_stall', width = 1, reset = 0, comments = '''\
If set to 1 and endpoint is enabled, ready, and not in isochronous mode, then endpoint will send STALL in response to a host inititiated transaction.'''),
                    csr_reg_field_desc('out_data_zero_len', width = 1, reset = 0, comments = '''\
Set to 1 means the current OUT DATA trans's length is zero.'''),
                    csr_reg_field_desc('out_data_seq', width = 1, reset = 0, comments = '''\
If set to 1 then the endpoint will respond to a host IN request with a DATA1 packet, otherwise it will respond with a DATA0 packet.'''),
                    csr_reg_field_desc('ready', width = 1, reset = 0, comments = '''\
Set to 1 make the endpoint ready. If endpoint is enabled and ready then it can respond to a host inititiated transaction. Automatically cleared to 0 when transaction is complete.'''),
                    csr_reg_field_desc('en', width = 1, reset = 0, comments = '''\
Set to 1 to enable the endpoint. If endpoint is not enabled then it will not respond to any transactions.  If endpoint is enabled, not ready, and not in isochronous mode, then all transactions will be NAK'd.''')]))
            device_status_reg = self.cfg_reg(csr_reg_group(
                'device_status'+suffix_str, 
                offset = 0x004+addr_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('nak_trans_type', width = 2, reset = 0, comments = '''\
SETUP_TRANS = 0
IN_TRANS = 1
OUTDATA_TRANS = 2
This is the transaction type of the last transaction which resulted in a NAK being sent to the host.'''),
                    csr_reg_field_desc('trans_type', width = 2, reset = 0, comments = '''\
SETUP_TRANS = 0
IN_TRANS = 1
OUTDATA_TRANS = 2
This is the transaction type of the last transaction.'''),
                    csr_reg_field_desc('data_seq', width = 1, reset = 0, comments = '''\
If the last transaction was of type OUT_TRANS, then this bit indicates the sequence number of the last receive packet. DATA0 = 0, DATA1 = 1.'''),
                    csr_reg_field_desc('ack_recved', width = 1, reset = 0, comments = '''\
When set to 1, indicates ACK received from USB host.'''),
                    csr_reg_field_desc('stall_sent', width = 1, reset = 0, comments = '''\
When set to 1, indicates STALL sent to USB host.'''),
                    csr_reg_field_desc('nak_sent', width = 1, reset = 0, comments = '''\
When set to 1, indicates NAK sent to USB host.'''),
                    csr_reg_field_desc('rx_time_out', width = 1, reset = 0, comments = '''\
When set to 1, indicates no response from USB host.'''),
                    csr_reg_field_desc('rx_overflow', width = 1, reset = 0, comments = '''\
When set to 1, indicates insufficient free space in RX fifo to accept entire data packet.'''),
                    csr_reg_field_desc('bit_stuff_error', width = 1, reset = 0, comments = '''\
When set to 1, indicates bit stuff error
detected on the last transaction.'''),
                    csr_reg_field_desc('crc_error', width = 1, reset = 0, comments = '''\
When set to 1, indicates CRC error detected on the last transaction.''')]))
            device_control_reg_array.append(device_control_reg)
            device_status_reg_array.append(device_status_reg)

        device_control_reg_array_en = list(map(lambda _: _.en, device_control_reg_array))
        device_control_reg_array_ready = list(map(lambda _: _.ready, device_control_reg_array))
        device_control_reg_array_out_data_seq = list(map(lambda _: _.out_data_seq, device_control_reg_array))
        device_control_reg_array_send_stall = list(map(lambda _: _.send_stall, device_control_reg_array))
        device_control_reg_array_iso_en = list(map(lambda _: _.iso_en, device_control_reg_array))
        device_control_reg_array_out_data_zero_len = list(map(lambda _: _.out_data_zero_len, device_control_reg_array))
        device_status_reg_array_trans_type = list(map(lambda _: _.trans_type, device_status_reg_array))
        device_status_reg_array_nak_trans_type = list(map(lambda _: _.nak_trans_type, device_status_reg_array))
        device_status_reg_array_data_seq = list(map(lambda _: _.data_seq, device_status_reg_array))
        device_status_reg_array_nak_sent = list(map(lambda _: _.nak_sent, device_status_reg_array))
        device_status_reg_array_stall_sent = list(map(lambda _: _.stall_sent, device_status_reg_array))
        device_status_reg_array_ack_recved = list(map(lambda _: _.ack_recved, device_status_reg_array))
        device_status_reg_array_crc_error = list(map(lambda _: _.crc_error, device_status_reg_array))
        device_status_reg_array_rx_time_out = list(map(lambda _: _.rx_time_out, device_status_reg_array))





        #}}}

        self.regs['host_connect_state'].rx_line_state /= self.io.utmi.LineState
        self.regs['device_connect_state'].rx_line_state /= self.io.utmi.LineState
        self.io.host_data_tx.ready /= 0

        for i in range(self.p.device_ep_num):
            self.io.device_data_tx[i].ready /= 0


        #
        #host slave share
        #{{{
        (e_host_trans_setup, e_host_trans_in, e_host_trans_out0, e_host_trans_out1) = range(4)
        (e_lnst_se0, e_lnst_j, e_lnst_k, e_lnst_se1) = range(4)
        (
            e_pidl_out, e_pidl_in, e_pidl_sof, e_pidl_setup,
            e_pidl_data0, e_pidl_data1, e_pidl_ack, e_pidl_nak,
            e_pidl_stall, e_pidl_pre) = (0x1, 0x9, 0x5, 0xd, 0x3, 0xb, 0x2, 0xa, 0xe, 0xc)
        (
            e_pidh_out, e_pidh_in, e_pidh_sof, e_pidh_setup,
            e_pidh_data0, e_pidh_data1, e_pidh_ack, e_pidh_nak,
            e_pidh_stall, e_pidh_pre) = (0xe, 0x6, 0xa, 0x2, 0xc, 0x4, 0xd, 0x5, 0x1, 0x3)
        (
            e_pid_out, e_pid_in, e_pid_sof, e_pid_setup,
            e_pid_data0, e_pid_data1, e_pid_ack, e_pid_nak,
            e_pid_stall, e_pid_pre)   = (0xe1, 0x69, 0xa5, 0x2d, 0xc3, 0x4b, 0xd2, 0x5a, 0x1e, 0x3c)
        (e_device_trans_setup, e_device_trans_in, e_device_trans_out) = range(3)

        host_trans_is_setup = self.regs['host_control'].trans_type == e_host_trans_setup
        host_trans_is_in = self.regs['host_control'].trans_type == e_host_trans_in
        host_trans_is_out0 = self.regs['host_control'].trans_type == e_host_trans_out0
        host_trans_is_out1 = self.regs['host_control'].trans_type == e_host_trans_out1
        host_trans_is_out = host_trans_is_out0 | host_trans_is_out1

        tick_cnt = reg_r('tick_cnt', w = 32)
        tick_cnt_clean = bits('tick_cnt_clean', init = 0)
        tick_cnt_inc = bits('tick_cnt_inc', init = 1)
        tick_cnt_sof_match = tick_cnt >= self.regs['host_tx_sof_timer'].data
        con_end = bits('con_end', init = 0)
        con_fail = bits('con_fail', init = 0)
        pkt_tx_byte_cnt = reg_r('pkt_tx_byte_cnt', w = 16)
        pkt_tx_byte_cnt_clean = bits('pkt_tx_byte_cnt_clean', init = 0)
        pkt_tx_byte_cnt_inc = bits('pkt_tx_byte_cnt_inc', init = 0)
        pkt_rx_byte_cnt = reg_r('pkt_rx_byte_cnt', w = 16)
        pkt_rx_byte_cnt_clean = bits('pkt_rx_byte_cnt_clean', init = 0)
        pkt_rx_byte_cnt_inc = bits('pkt_rx_byte_cnt_inc', init = 0)
        pkt_trans_timeout_cnt = reg_r('pkt_trans_timeout_cnt', w = 16)
        pkt_trans_timeout_cnt_clean = bits('pkt_trans_timeout_cnt_clean', init = 0)
        pkt_trans_timeout_cnt_inc_reg = reg_r('pkt_trans_timeout_cnt_inc_reg')
        pkt_trans_timeout_cnt_match = bits('pkt_trans_timeout_cnt_match', init = 0)


        self.io.utmi.SuspendM /= mux(
            self.io.cfg_mode,
            self.regs['host_tx_line_control'].suspend_m,
            self.regs['device_tx_line_control'].suspend_m)
        self.io.utmi.XcvrSelect /= mux(
            self.io.cfg_mode,
            self.regs['host_tx_line_control'].xcvr_select,
            self.regs['device_tx_line_control'].xcvr_select)
        self.io.utmi.TermSelect /= mux(
            self.io.cfg_mode,
            self.regs['host_tx_line_control'].term_select,
            self.regs['device_tx_line_control'].term_select)
        #0: normal operation, 1: non-driving, 2: disable bit stuffing, 3: reserved
        self.io.utmi.OpMode /= mux(
            self.io.cfg_mode,
            self.regs['host_tx_line_control'].opmode,
            self.regs['device_tx_line_control'].opmode)
        self.io.utmi.IdPullup /= self.regs['host_tx_line_control'].id_pullup
        self.io.utmi.DpPulldown /= self.regs['host_tx_line_control'].dp_pulldown
        self.io.utmi.DmPulldown /= self.regs['host_tx_line_control'].dm_pulldown
        self.io.utmi.DrvVbus /= self.regs['host_tx_line_control'].drv_vbus
        self.io.utmi.ChrgVbus /= self.regs['host_tx_line_control'].chrg_vbus
        self.io.utmi.DischrgVbus /= self.regs['host_tx_line_control'].dischrg_vbus

        direct_control_sel = mux(
            self.io.cfg_mode,
            self.regs['host_tx_line_control'].direct_control,
            self.regs['device_tx_line_control'].direct_control)
        tx_line_state_sel = mux(
            self.io.cfg_mode,
            self.regs['host_tx_line_control'].tx_line_state,
            self.regs['device_tx_line_control'].tx_line_state)
        self.io.utmi.FsLsSerialMode /= 0
        self.io.utmi.Tx_Enable_N /= 1
        self.io.utmi.Tx_DAT /= 0
        self.io.utmi.Tx_SE0 /= 0
        with when(direct_control_sel):
            self.io.utmi.FsLsSerialMode /= 1
            self.io.utmi.Tx_Enable_N /= 0
            with when(tx_line_state_sel == 0b00):
                self.io.utmi.Tx_SE0 /= 1
            with when(tx_line_state_sel == 0b01):
                self.io.utmi.Tx_DAT /= 0
            with when(tx_line_state_sel == 0b10):
                self.io.utmi.Tx_DAT /= 1
        self.io.utmi.TxBitstuffEnable /= 0


        self.io.utmi.TXValid /= 0
        self.io.utmi.DataIn /= 0

        self.io.data_rx.valid /= 0
        self.io.data_rx.bits.data /= 0
        self.io.data_rx.bits.be /= 0
        self.io.data_rx.bits.ep /= 0



        utmi_rx_active_dly = reg_r('utmi_rx_active_dly', next = self.io.utmi.RXActive)
        utmi_rx_valid = self.io.utmi.RXValid & self.io.utmi.RXActive
        utmi_rx_valid_dly = reg_r('utmi_rx_valid_dly', next = utmi_rx_valid)
        utmi_rx_valid_pos = utmi_rx_valid & ~utmi_rx_valid_dly
        utmi_rx_valid_start_mask = reg_r('utmi_rx_valid_start_mask')
        utmi_rx_valid_start = utmi_rx_valid_pos & ~utmi_rx_valid_start_mask
        with when(utmi_rx_valid_start):
            utmi_rx_valid_start_mask /= 1
        with elsewhen(~self.io.utmi.RXActive):
            utmi_rx_valid_start_mask /= 0
        utmi_rx_invalid = ~self.io.utmi.RXValid & self.io.utmi.RXActive
        utmi_rx_pid_sof_found = self.io.utmi.DataOut == e_pid_sof
        utmi_rx_pid_setup_found = self.io.utmi.DataOut == e_pid_setup
        utmi_rx_pid_in_found = self.io.utmi.DataOut == e_pid_in
        utmi_rx_pid_out_found = self.io.utmi.DataOut == e_pid_out
        utmi_rx_pid_data0_found = self.io.utmi.DataOut == e_pid_data0
        utmi_rx_pid_data1_found = self.io.utmi.DataOut == e_pid_data1
        utmi_rx_pid_ack_found = self.io.utmi.DataOut == e_pid_ack
        utmi_rx_pid_nak_found = self.io.utmi.DataOut == e_pid_nak
        utmi_rx_pid_stall_found = self.io.utmi.DataOut == e_pid_stall
        utmi_rx_pid_pre_found = self.io.utmi.DataOut == e_pid_pre
        #}}}


        (
            s_discon, s_con, s_idle, 
            s_token_sof, s_token_setup, s_token_in, s_token_out,
            s_data_in, s_data_out,
            s_hdsk_in, s_hdsk_out,
            s_special, s_error) = range(13)
        utmi_state = reg_rs('utmi_state', w = 4, rs = s_discon)
        host_sof_done_pulse_reg = reg_r('host_sof_done_pulse_reg')

        host_token_sof_done = bits('host_token_sof_done', init = 0)
        host_token_setup_done = bits('host_token_setup_done', init = 0)
        host_token_in_done = bits('host_token_in_done', init = 0)
        host_token_out_done = bits('host_token_out_done', init = 0)
        host_data_in_done = bits('host_data_in_done', init = 0)
        host_data_in_nak = bits('host_data_in_nak', init = 0)
        host_data_in_stall = bits('host_data_in_stall', init = 0)
        host_data_in_timeout = bits('host_data_in_timeout', init = 0)
        host_data_out_done = bits('host_data_out_done', init = 0)
        host_hdsk_in_done = bits('host_hdsk_in_done', init = 0)
        host_hdsk_out_done = bits('host_hdsk_out_done', init = 0)
        host_hdsk_out_timeout = bits('host_hdsk_out_timeout', init = 0)


        device_token_sof_done = bits('device_token_sof_done', init = 0)
        device_token_setup_done = bits('device_token_setup_done', init = 0)
        device_token_out_done = bits('device_token_out_done', init = 0)
        device_token_in_done = bits('device_token_in_done', init = 0)
        device_data_out_done = bits('device_data_out_done', init = 0)
        device_data_out_timeout = bits('device_data_out_timeout', init = 0)
        device_data_in_done = bits('device_data_in_done', init = 0)
        device_data_in_nak = bits('device_data_in_nak', init = 0)
        device_data_in_stall = bits('device_data_in_stall', init = 0)
        device_hdsk_out_done = bits('device_hdsk_out_done', init = 0)
        device_hdsk_in_done = bits('device_hdsk_in_done', init = 0)
        device_hdsk_in_timeout = bits('device_hdsk_in_timeout', init = 0)

        device_data_seq_reg = reg_r('device_data_seq_reg')
        device_ep_ready_reg = reg_r('device_ep_ready_reg', w = self.p.device_ep_num)
        device_ep_send_stall_reg = reg_r('device_ep_send_stall_reg', w = self.p.device_ep_num)
        device_ep_iso_en_reg = reg_r('device_ep_iso_en_reg', w = self.p.device_ep_num)
        device_rx_addr_match_reg = reg_r('device_rx_addr_match_reg')
        device_rx_ep_id_reg = reg_r('device_rx_ep_id_reg', w = 4)
        device_ep_ready = sel_bin(device_rx_ep_id_reg, device_ep_ready_reg.grouped(1))
        device_ep_send_stall = sel_bin(device_rx_ep_id_reg, device_ep_send_stall_reg.grouped(1))
        device_ep_iso_en = sel_bin(device_rx_ep_id_reg, device_ep_iso_en_reg.grouped(1))
        device_data_tx_sel = sel_bin(device_rx_ep_id_reg, list(self.io.device_data_tx))
        device_ep_out_data_zero_len = sel_bin(device_rx_ep_id_reg, device_control_reg_array_out_data_zero_len)
        device_out_data_seq = sel_bin(device_rx_ep_id_reg, device_control_reg_array_out_data_seq)


        with when(utmi_state == s_discon):
            tick_cnt_clean /= 1
            with when(self.io.utmi.DpPulldown & self.io.utmi.DmPulldown & ~self.io.utmi.HostDisconnect):
                utmi_state /= s_con
        with when(utmi_state == s_con):
            with when(con_fail):
                utmi_state /= s_discon
                tick_cnt_clean /= 1
            with elsewhen(con_end):
                utmi_state /= s_idle
                tick_cnt_clean /= 1
        with when(utmi_state == s_idle):
            pkt_trans_timeout_cnt_clean /= 1
            pkt_trans_timeout_cnt_inc_reg /= 0
            pkt_tx_byte_cnt_clean /= 1
            with when(self.io.utmi.DpPulldown & self.io.utmi.DmPulldown & self.io.utmi.HostDisconnect):
                utmi_state /= s_discon
            with elsewhen(self.io.cfg_trans_en):
                with when(self.io.cfg_mode):
                    #valid one cycle
                    host_sof_done_pulse_reg /= 0

                    with when(self.regs['host_control'].sof_en & tick_cnt_sof_match):
                        utmi_state /= s_token_sof
                    with elsewhen(self.regs['host_control'].trans_req &
                        (~self.regs['host_control'].sof_sync | host_sof_done_pulse_reg)):
                        with when(host_trans_is_setup):
                            utmi_state /= s_token_setup
                        with when(host_trans_is_in):
                            utmi_state /= s_token_in
                        with when(host_trans_is_out):
                            utmi_state /= s_token_out
                with other():
                    #capture ep ready at this time
                    device_ep_ready_reg /= cat_rvs(device_control_reg_array_ready)
                    device_ep_send_stall_reg /= cat_rvs(device_control_reg_array_send_stall)
                    device_ep_iso_en_reg /= cat_rvs(device_control_reg_array_iso_en)
                    with when(utmi_rx_valid_start):
                        pkt_rx_byte_cnt_clean /= 1
                        with when(utmi_rx_pid_sof_found):
                            utmi_state /= s_token_sof
                        with when(utmi_rx_pid_setup_found):
                            utmi_state /= s_token_setup
                        with when(utmi_rx_pid_out_found):
                            utmi_state /= s_token_out
                        with when(utmi_rx_pid_in_found):
                            utmi_state /= s_token_in
        with when(utmi_state == s_token_sof):
            with when(self.io.cfg_mode):
                with when(host_token_sof_done):
                    pkt_tx_byte_cnt_clean /= 1
                    utmi_state /= s_idle
            with other():
                with when(device_token_sof_done):
                    pkt_rx_byte_cnt_clean /= 1
                    utmi_state /= s_idle
        with when(utmi_state == s_token_setup):
            with when(self.io.cfg_mode):
                with when(host_token_setup_done):
                    pkt_tx_byte_cnt_clean /= 1
                    utmi_state /= s_data_out
            with other():
                with when(device_token_setup_done):
                    with when(device_rx_addr_match_reg):
                        pkt_rx_byte_cnt_clean /= 1
                        pkt_trans_timeout_cnt_clean /= 1
                        pkt_trans_timeout_cnt_inc_reg /= 1
                        utmi_state /= s_data_out
                    with other():
                        utmi_state /= s_idle
        with when(utmi_state == s_token_in):
            with when(self.io.cfg_mode):
                with when(host_token_in_done):
                    pkt_rx_byte_cnt_clean /= 1
                    pkt_trans_timeout_cnt_clean /= 1
                    pkt_trans_timeout_cnt_inc_reg /= 1
                    utmi_state /= s_data_in
            with other():
                with when(device_token_in_done):
                    with when(device_rx_addr_match_reg):
                        pkt_tx_byte_cnt_clean /= 1
                        utmi_state /= s_data_in
                    with other():
                        utmi_state /= s_idle
        with when(utmi_state == s_token_out):
            with when(self.io.cfg_mode):
                with when(host_token_out_done):
                    pkt_tx_byte_cnt_clean /= 1
                    utmi_state /= s_data_out
            with other():
                with when(device_token_out_done):
                    with when(device_rx_addr_match_reg):
                        pkt_rx_byte_cnt_clean /= 1
                        pkt_trans_timeout_cnt_clean /= 1
                        pkt_trans_timeout_cnt_inc_reg /= 1
                        utmi_state /= s_data_out
                    with other():
                        utmi_state /= s_idle
        with when(utmi_state == s_data_in):
            with when(self.io.cfg_mode):
                with when(utmi_rx_valid_start):
                    pkt_rx_byte_cnt_clean /= 1
                with when(host_data_in_done):
                    pkt_rx_byte_cnt_clean /= 1
                    pkt_tx_byte_cnt_clean /= 1
                    utmi_state /= s_hdsk_in
                with when(host_data_in_nak):
                    utmi_state /= s_idle
                with when(host_data_in_stall):
                    utmi_state /= s_idle
                with when(host_data_in_timeout):
                    utmi_state /= s_idle
            with other():
                with when(device_data_in_done):
                    pkt_rx_byte_cnt_clean /= 1
                    pkt_trans_timeout_cnt_clean /= 1
                    pkt_trans_timeout_cnt_inc_reg /= 1
                    utmi_state /= s_hdsk_in
                with when(device_data_in_nak):
                    utmi_state /= s_idle
                with when(device_data_in_stall):
                    utmi_state /= s_idle
        with when(utmi_state == s_data_out):
            with when(self.io.cfg_mode):
                with when(host_data_out_done):
                    pkt_tx_byte_cnt_clean /= 1
                    pkt_trans_timeout_cnt_clean /= 1
                    pkt_trans_timeout_cnt_inc_reg /= 1
                    utmi_state /= s_hdsk_out
            with other():
                with when(utmi_rx_valid_start):
                    pkt_rx_byte_cnt_clean /= 1
                    with when(utmi_rx_pid_data0_found):
                        device_data_seq_reg /= 0
                    with when(utmi_rx_pid_data1_found):
                        device_data_seq_reg /= 1

                with when(device_data_out_done):
                    pkt_tx_byte_cnt_clean /= 1
                    utmi_state /= s_hdsk_out
                with when(device_data_out_timeout):
                    utmi_state /= s_idle
        with when(utmi_state == s_hdsk_in):
            with when(self.io.cfg_mode):
                with when(host_hdsk_in_done):
                    utmi_state /= s_idle
            with other():
                with when(device_hdsk_in_done):
                    utmi_state /= s_idle
                with when(device_hdsk_in_timeout):
                    utmi_state /= s_idle
        with when(utmi_state == s_hdsk_out):
            with when(self.io.cfg_mode):
                with when(host_hdsk_out_done):
                    utmi_state /= s_idle
                with when(host_hdsk_out_timeout):
                    utmi_state /= s_idle
            with other():
                with when(device_hdsk_out_done):
                    utmi_state /= s_idle


        #tick_cnt control
        with when(tick_cnt_clean):
            tick_cnt /= 0
        with elsewhen((utmi_state == s_idle) & tick_cnt_sof_match):
            tick_cnt /= 0
        with elsewhen(tick_cnt_inc):
            tick_cnt /= tick_cnt + 1

        with when(utmi_state == s_idle):
            with when(self.io.cfg_mode):
                with when(~self.regs['host_control'].sof_en):
                    tick_cnt_inc /= 0
            with other():
                tick_cnt_inc /= 0


        #connect/disconnect control
        with when(utmi_state == s_con):
            with when(self.io.utmi.LineState == e_lnst_j):
                con_end /= 1
            #fake connect
            with other():
                con_fail /= 1

        
        with when(pkt_tx_byte_cnt_clean):
            pkt_tx_byte_cnt /= 0
        with elsewhen(pkt_tx_byte_cnt_inc):
            pkt_tx_byte_cnt /= pkt_tx_byte_cnt + 1
        with when(self.io.utmi.TXValid & self.io.utmi.TXReady):
            pkt_tx_byte_cnt_inc /= 1

        with when(pkt_rx_byte_cnt_clean):
            pkt_rx_byte_cnt /= 1 #pid byte need jump
        with elsewhen(pkt_rx_byte_cnt_inc):
            pkt_rx_byte_cnt /= pkt_rx_byte_cnt + 1
        with when(utmi_rx_valid):
            pkt_rx_byte_cnt_inc /= 1

        with when(self.io.cfg_mode):
            pkt_trans_timeout_cnt_match /= pkt_trans_timeout_cnt == self.regs['host_trans_timeout_cnt'].data
        with other():
            pkt_trans_timeout_cnt_match /= pkt_trans_timeout_cnt == self.regs['device_trans_timeout_cnt'].data
        with when(pkt_trans_timeout_cnt_clean):
            pkt_trans_timeout_cnt /= 0
        with elsewhen(pkt_trans_timeout_cnt_match):
            pkt_trans_timeout_cnt /= 0
        with elsewhen(pkt_trans_timeout_cnt_inc_reg):
            pkt_trans_timeout_cnt /= pkt_trans_timeout_cnt + 1

        #token pkt send/recive
        host_token_data = vec('host_token_data', lambda _: bits(_, w = 8, init = 0), 3)
        gen_crc5_v = zqh_usb_ctrl_crc5(cat([host_token_data[2][2:0], host_token_data[1]]))
        host_token_data[2][7:3] /= ~gen_crc5_v.order_invert()
        host_token_datain_sel = host_token_data[pkt_tx_byte_cnt[1:0]]

        check_crc5_byte_init = 0x1f
        check_crc5_byte_rslt = 0x0c
        check_crc5_byte_reg = reg('check_crc5_byte_reg', w = 5)
        check_crc5_byte_pre_v = bits('check_crc5_byte_pre_v', w = 5, init = 0)
        check_crc5_byte_v = zqh_usb_ctrl_device_crc5(self.io.utmi.DataOut, check_crc5_byte_pre_v)

        device_frame_num_reg = reg_r('device_frame_num_reg', w = 11)
        device_rx_addr_reg = reg_r('device_rx_addr_reg', w = 7)
        device_rx_trans_type_reg = reg_r('device_rx_trans_type_reg', w = 2)
        device_nak_sent_reg = reg_r('device_nak_sent_reg')
        device_send_stall_reg = reg_r('device_send_stall_reg')
        with when(utmi_state == s_token_sof):
            with when(self.io.cfg_mode):
                self.io.utmi.TXValid /= 1
                self.io.utmi.DataIn /= host_token_datain_sel
                host_token_data[0] /= e_pid_sof
                host_token_data[1] /= self.regs['host_tx_frame_num'].data[7:0]
                host_token_data[2][2:0] /= self.regs['host_tx_frame_num'].data[10:8]

                with when(pkt_tx_byte_cnt == 3):
                    self.io.utmi.TXValid /= 0
                    host_token_sof_done /= 1
                    self.regs['host_tx_frame_num'].data /= self.regs['host_tx_frame_num'].data + 1
                    host_sof_done_pulse_reg /= 1
            with other():
                with when(utmi_rx_valid):
                    check_crc5_byte_reg /= check_crc5_byte_v
                    with when(pkt_rx_byte_cnt == 1):
                        check_crc5_byte_pre_v /= check_crc5_byte_init
                    with other():
                        check_crc5_byte_pre_v /= check_crc5_byte_reg

                    with when(pkt_rx_byte_cnt == 1):
                        device_frame_num_reg[7:0] /= self.io.utmi.DataOut
                    with when(pkt_rx_byte_cnt == 2):
                        device_frame_num_reg[10:8] /= self.io.utmi.DataOut[2:0]
                with when(~self.io.utmi.RXActive):
                    device_token_sof_done /= 1
                    self.regs['device_frame_num'].data /= device_frame_num_reg
                    with when(check_crc5_byte_reg != check_crc5_byte_rslt):
                        for i in range(self.p.device_ep_num):
                            device_status_reg_array_crc_error[i] /= 1
        with when((utmi_state == s_token_setup) | (utmi_state == s_token_out)):
            with when(self.io.cfg_mode):
                self.io.utmi.TXValid /= 1
                self.io.utmi.DataIn /= host_token_datain_sel
                host_token_data[0] /= mux(utmi_state == s_token_setup, e_pid_setup, e_pid_out)
                host_token_data[1] /= cat([self.regs['host_tx_addr'].endp[0], self.regs['host_tx_addr'].addr])
                host_token_data[2][2:0] /= self.regs['host_tx_addr'].endp[3:1]

                with when(pkt_tx_byte_cnt == 3):
                    self.io.utmi.TXValid /= 0
                    with when(utmi_state == s_token_setup):
                        host_token_setup_done /= 1
                    with when(utmi_state == s_token_out):
                        host_token_out_done /= 1
            with other():
                with when(utmi_rx_valid):
                    check_crc5_byte_reg /= check_crc5_byte_v
                    with when(pkt_rx_byte_cnt == 1):
                        check_crc5_byte_pre_v /= check_crc5_byte_init
                    with other():
                        check_crc5_byte_pre_v /= check_crc5_byte_reg

                    with when(pkt_rx_byte_cnt == 1):
                        device_rx_addr_reg /= self.io.utmi.DataOut[6:0]
                        device_rx_ep_id_reg[0] /= self.io.utmi.DataOut[7]
                        with when(self.io.utmi.DataOut[6:0] == self.regs['device_addr'].data):
                            device_rx_addr_match_reg /= 1
                        with other():
                            device_rx_addr_match_reg /= 0
                    with when(pkt_rx_byte_cnt == 2):
                        device_rx_ep_id_reg[3:1] /= self.io.utmi.DataOut[2:0]

                with when(~self.io.utmi.RXActive):
                    with when(utmi_state == s_token_setup):
                        device_token_setup_done /= 1
                        device_rx_trans_type_reg /= e_device_trans_setup
                    with when(utmi_state == s_token_out):
                        device_token_out_done /= 1
                        device_rx_trans_type_reg /= e_device_trans_out

                    with when(check_crc5_byte_reg != check_crc5_byte_rslt):
                        for i in range(self.p.device_ep_num):
                            with when(device_rx_ep_id_reg == i):
                                device_status_reg_array_crc_error[i] /= 1


        with when(utmi_state == s_token_in):
            with when(self.io.cfg_mode):
                self.io.utmi.TXValid /= 1
                self.io.utmi.DataIn /= host_token_datain_sel
                host_token_data[0] /= e_pid_in
                host_token_data[1] /= cat([self.regs['host_tx_addr'].endp[0], self.regs['host_tx_addr'].addr])
                host_token_data[2][2:0] /= self.regs['host_tx_addr'].endp[3:1]

                with when(pkt_tx_byte_cnt == 3):
                    self.io.utmi.TXValid /= 0
                    host_token_in_done /= 1
            with other():
                with when(utmi_rx_valid):
                    with when(pkt_rx_byte_cnt == 1):
                        with when(self.io.utmi.DataOut[6:0] == self.regs['device_addr'].data):
                            device_rx_addr_match_reg /= 1
                            device_rx_ep_id_reg[0] /= self.io.utmi.DataOut[7]
                        with other():
                            device_rx_addr_match_reg /= 0
                    with when(pkt_rx_byte_cnt == 2):
                        device_rx_ep_id_reg[3:1] /= self.io.utmi.DataOut[2:0]

                with when(~self.io.utmi.RXActive):
                    device_token_in_done /= 1
                    device_rx_trans_type_reg /= e_device_trans_in



        #data pkt send/recive

        data_tx_valid_dly = reg_r('data_tx_valid_dly')
        data_tx_crc_reg = reg_r('data_tx_crc_reg')
        data_tx_crc = bits('data_tx_crc', init = 0)
        data_tx_valid_sel = mux(self.io.cfg_mode, self.io.host_data_tx.valid, device_data_tx_sel.valid)
        data_tx_valid_dly /= data_tx_valid_sel
        data_tx_valid_neg = ~data_tx_valid_sel & data_tx_valid_dly
        with when(data_tx_valid_neg):
            data_tx_crc_reg /= 1
        data_tx_crc /= data_tx_valid_neg | data_tx_crc_reg

        data_out_datain_sel = bits('data_out_datain_sel', w = 8, init = 0)
        gen_crc16_init = 0xffff
        gen_crc16_reg = reg('gen_crc16_reg', w = 16)
        gen_crc16_send = ~gen_crc16_reg.order_invert()
        gen_crc16_v = zqh_usb_ctrl_crc16(data_out_datain_sel, gen_crc16_reg)
        gen_crc16_byte_idx = reg_r('gen_crc16_byte_idx', w = 2)
        #tmp out_zero_pkt_reg = reg_r('out_zero_pkt_reg')

        check_crc16_byte_init = 0xffff
        check_crc16_byte_rslt = 0x800d
        check_crc16_byte_reg = reg('check_crc16_byte_reg', w = 16)
        check_crc16_byte_pre_v = bits('check_crc16_byte_pre_v', w = 16, init = 0)
        check_crc16_byte_v = zqh_usb_ctrl_crc16(self.io.utmi.DataOut, check_crc16_byte_pre_v)

        with when(pkt_tx_byte_cnt == 0):
            gen_crc16_reg /= gen_crc16_init
        with other():
            with when(pkt_tx_byte_cnt_inc):
                with when(self.io.cfg_mode):
                    with when(self.io.host_data_tx.valid):
                        gen_crc16_reg /= gen_crc16_v
                with other():
                    with when(device_data_tx_sel.valid):
                        gen_crc16_reg /= gen_crc16_v
        with when(utmi_state == s_data_out):
            with when(self.io.cfg_mode):
                self.io.utmi.DataIn /= data_out_datain_sel

                #zero byte data pkt
                #tmp with when(pkt_tx_byte_cnt == 0):
                #tmp     out_zero_pkt_reg /= ~self.io.host_data_tx.valid
                #tmp with when(~self.io.host_data_tx.valid & ((pkt_tx_byte_cnt == 0) | out_zero_pkt_reg)):
                with when(self.regs['host_control'].out_zero_len):
                    self.io.utmi.TXValid /= 1
                    with when(pkt_tx_byte_cnt == 0):
                        data_out_datain_sel /= mux(
                            host_trans_is_setup | host_trans_is_out0,
                            e_pid_data0,
                            e_pid_data1)
                        gen_crc16_byte_idx /= 0
                    with other():
                        data_out_datain_sel /= 0
                        with when(pkt_tx_byte_cnt == 3):
                            self.io.utmi.TXValid /= 0
                            host_data_out_done /= 1
                with other():
                    with when(pkt_tx_byte_cnt == 0):
                        self.io.utmi.TXValid /= 1
                        data_out_datain_sel /= mux(
                            host_trans_is_setup | host_trans_is_out0,
                            e_pid_data0,
                            e_pid_data1)
                        gen_crc16_byte_idx /= 0
                    with other():
                        #tmp with when(self.io.host_data_tx.valid):
                        #tmp     self.io.utmi.TXValid /= self.io.host_data_tx.valid
                        #tmp     self.io.host_data_tx.ready /= self.io.utmi.TXReady
                        #tmp     data_out_datain_sel /= self.io.host_data_tx.bits.data
                        #tmp with other():
                        #tmp     with when(pkt_tx_byte_cnt_inc):
                        #tmp         gen_crc16_byte_idx /= gen_crc16_byte_idx + 1

                        #tmp     with when(gen_crc16_byte_idx == 0):
                        #tmp         self.io.utmi.TXValid /= 1
                        #tmp         data_out_datain_sel /= gen_crc16_send[7:0]
                        #tmp     with elsewhen(gen_crc16_byte_idx == 1):
                        #tmp         self.io.utmi.TXValid /= 1
                        #tmp         data_out_datain_sel /= gen_crc16_send[15:8]
                        #tmp     with elsewhen(gen_crc16_byte_idx == 2):
                        #tmp         self.io.utmi.TXValid /= 0
                        #tmp         host_data_out_done /= 1

                        self.io.utmi.TXValid /= self.io.host_data_tx.valid
                        self.io.host_data_tx.ready /= self.io.utmi.TXReady
                        data_out_datain_sel /= self.io.host_data_tx.bits.data
                        with when(data_tx_crc):
                            with when(pkt_tx_byte_cnt_inc):
                                gen_crc16_byte_idx /= gen_crc16_byte_idx + 1

                            with when(gen_crc16_byte_idx == 0):
                                self.io.utmi.TXValid /= 1
                                data_out_datain_sel /= gen_crc16_send[7:0]
                            with elsewhen(gen_crc16_byte_idx == 1):
                                self.io.utmi.TXValid /= 1
                                data_out_datain_sel /= gen_crc16_send[15:8]
                            with elsewhen(gen_crc16_byte_idx == 2):
                                self.io.utmi.TXValid /= 0
                                host_data_out_done /= 1

                                data_tx_crc_reg /= 0

            with other():
                with when(utmi_rx_active_dly):
                    with when(~self.io.utmi.RXActive):
                        device_data_out_done /= 1

                        with when(check_crc16_byte_reg != check_crc16_byte_rslt):
                            for i in range(self.p.device_ep_num):
                                with when(device_rx_ep_id_reg == i):
                                    device_status_reg_array_crc_error[i] /= 1

                check_crc16_byte_pre_v /= check_crc16_byte_reg

                with when(pkt_trans_timeout_cnt_match):
                    device_data_out_timeout /= 1
                    for i in range(self.p.device_ep_num):
                        with when(device_rx_ep_id_reg == i):
                            device_status_reg_array_rx_time_out[i] /= 1

                    #clean rx ep's ready
                    with when(device_ep_ready):
                        for i in range(self.p.device_ep_num):
                            with when(device_rx_ep_id_reg == i):
                                device_control_reg_array_ready[i] /= 0
                with elsewhen(utmi_rx_valid):
                    pkt_trans_timeout_cnt_inc_reg /= 0
                    with when(utmi_rx_valid_start):
                        check_crc16_byte_reg /= check_crc16_byte_init
                    with other():
                        check_crc16_byte_reg /= check_crc16_byte_v


                    #not ready ep should not recieve data
                    #setup trans should always recieve, bulk out0/1 should see ep ready
                    with when(~device_ep_send_stall):
                        self.io.data_rx.valid /= (device_rx_trans_type_reg == e_device_trans_setup) | device_ep_ready
                    self.io.data_rx.bits.data /= self.io.utmi.DataOut
                    self.io.data_rx.bits.be /= 1
                    self.io.data_rx.bits.ep /= device_rx_ep_id_reg

                    for i in range(self.p.device_ep_num):
                        with when(device_rx_ep_id_reg == i):
                            device_status_reg_array_data_seq[i] /= device_data_seq_reg

        host_data_seq_reg = reg_r('host_data_seq_reg')
        host_data_pkt_found_reg = reg_r('host_data_pkt_found_reg')
        host_data_pkt_match = bits('host_data_pkt_match', init = 0)

        with when(utmi_state == s_data_in):
            with when(self.io.cfg_mode):
                check_crc16_byte_pre_v /= check_crc16_byte_reg
                with when(pkt_trans_timeout_cnt_match):
                    host_data_in_timeout /= 1
                    host_data_pkt_found_reg /= 0
                    self.regs['host_rx_status'].rx_time_out /= 1
                    self.regs['host_control'].trans_req /= 0
                with elsewhen(utmi_rx_valid_start):
                    with when(utmi_rx_pid_data0_found):
                        host_data_seq_reg /= 0
                        host_data_pkt_found_reg /= 1
                        host_data_pkt_match /= 1
                        pkt_trans_timeout_cnt_inc_reg /= 0
                    with when(utmi_rx_pid_data1_found):
                        host_data_seq_reg /= 1
                        host_data_pkt_found_reg /= 1
                        host_data_pkt_match /= 1
                        pkt_trans_timeout_cnt_inc_reg /= 0
                    with when(utmi_rx_pid_nak_found):
                        host_data_in_nak /= 1
                        self.regs['host_rx_status'].nak_recved /= 1
                        self.regs['host_control'].trans_req /= 0
                        pkt_trans_timeout_cnt_inc_reg /= 0
                    with when(utmi_rx_pid_stall_found):
                        host_data_in_stall /= 1
                        self.regs['host_rx_status'].stall_recved /= 1
                        self.regs['host_control'].trans_req /= 0
                        pkt_trans_timeout_cnt_inc_reg /= 0

                with when(host_data_pkt_match | host_data_pkt_found_reg):
                    with when(utmi_rx_active_dly):
                        with when(~self.io.utmi.RXActive):
                            host_data_in_done /= 1
                            host_data_pkt_found_reg /= 0

                            with when(check_crc16_byte_reg != check_crc16_byte_rslt):
                                self.regs['host_rx_status'].crc_error /= 1

                    with when(utmi_rx_valid):
                        self.io.data_rx.valid /= 1
                        self.io.data_rx.bits.data /= self.io.utmi.DataOut
                        self.io.data_rx.bits.be /= 1
                        self.io.data_rx.bits.ep /= 0

                        self.regs['host_rx_status'].data_seq /= host_data_seq_reg 

                        with when(utmi_rx_valid_start):
                            check_crc16_byte_reg /= check_crc16_byte_init
                        with other():
                            check_crc16_byte_reg /= check_crc16_byte_v
            with other():
                self.io.utmi.DataIn /= data_out_datain_sel

                with when(device_ep_send_stall):
                    data_out_datain_sel /= e_pid_stall
                    with when(pkt_tx_byte_cnt == 0):
                        self.io.utmi.TXValid /= 1
                    with other():
                        self.io.utmi.TXValid /= 0
                        device_data_in_stall /= 1
                        data_tx_crc_reg /= 0
                #not ready, send nak
                with elsewhen(~device_ep_ready):
                    data_out_datain_sel /= e_pid_nak
                    with when(pkt_tx_byte_cnt == 0):
                        self.io.utmi.TXValid /= 1
                    with other():
                        self.io.utmi.TXValid /= 0
                        device_data_in_nak /= 1
                        data_tx_crc_reg /= 0
                #zero byte data pkt
                #tmp with when(pkt_tx_byte_cnt == 0):
                #tmp     out_zero_pkt_reg /= ~device_data_tx_sel.valid
                #tmp with when(~device_data_tx_sel.valid & ((pkt_tx_byte_cnt == 0) | out_zero_pkt_reg)):
                with elsewhen(device_ep_out_data_zero_len):
                    self.io.utmi.TXValid /= 1
                    with when(pkt_tx_byte_cnt == 0):
                        data_out_datain_sel /= mux(
                            device_out_data_seq,
                            e_pid_data1,
                            e_pid_data0)
                        gen_crc16_byte_idx /= 0
                    with other():
                        data_out_datain_sel /= 0
                        with when(pkt_tx_byte_cnt == 3):
                            self.io.utmi.TXValid /= 0
                            device_data_in_done /= 1
                            data_tx_crc_reg /= 0
                with other():
                    with when(pkt_tx_byte_cnt == 0):
                        self.io.utmi.TXValid /= 1
                        data_out_datain_sel /= mux(
                            device_out_data_seq,
                            e_pid_data1,
                            e_pid_data0)
                        gen_crc16_byte_idx /= 0
                    with other():
                        #tmp with when(device_data_tx_sel.valid):
                        #tmp     self.io.utmi.TXValid /= device_data_tx_sel.valid
                        #tmp     for i in range(self.p.device_ep_num):
                        #tmp         with when(device_rx_ep_id_reg == i):
                        #tmp             self.io.device_data_tx[i].ready /= self.io.utmi.TXReady
                        #tmp     data_out_datain_sel /= device_data_tx_sel.bits.data
                        #tmp with other():
                        #tmp     with when(pkt_tx_byte_cnt_inc):
                        #tmp         gen_crc16_byte_idx /= gen_crc16_byte_idx + 1

                        #tmp     with when(gen_crc16_byte_idx == 0):
                        #tmp         self.io.utmi.TXValid /= 1
                        #tmp         data_out_datain_sel /= gen_crc16_send[7:0]
                        #tmp     with elsewhen(gen_crc16_byte_idx == 1):
                        #tmp         self.io.utmi.TXValid /= 1
                        #tmp         data_out_datain_sel /= gen_crc16_send[15:8]
                        #tmp     with elsewhen(gen_crc16_byte_idx == 2):
                        #tmp         self.io.utmi.TXValid /= 0
                        #tmp         device_data_in_done /= 1

                        self.io.utmi.TXValid /= device_data_tx_sel.valid
                        for i in range(self.p.device_ep_num):
                            with when(device_rx_ep_id_reg == i):
                                self.io.device_data_tx[i].ready /= self.io.utmi.TXReady
                        data_out_datain_sel /= device_data_tx_sel.bits.data
                        with when(data_tx_crc):
                            with when(pkt_tx_byte_cnt_inc):
                                gen_crc16_byte_idx /= gen_crc16_byte_idx + 1

                            with when(gen_crc16_byte_idx == 0):
                                self.io.utmi.TXValid /= 1
                                data_out_datain_sel /= gen_crc16_send[7:0]
                            with elsewhen(gen_crc16_byte_idx == 1):
                                self.io.utmi.TXValid /= 1
                                data_out_datain_sel /= gen_crc16_send[15:8]
                            with elsewhen(gen_crc16_byte_idx == 2):
                                self.io.utmi.TXValid /= 0
                                device_data_in_done /= 1

                                data_tx_crc_reg /= 0


        #handshake pkt send
        host_hdsk_out_wait_eop = reg_r('host_hdsk_out_wait_eop')
        with when(utmi_state == s_hdsk_out):
            with when(self.io.cfg_mode):
                with when(~self.regs['host_control'].iso_en & ~host_hdsk_out_wait_eop):
                    with when(pkt_trans_timeout_cnt_match):
                        host_hdsk_out_wait_eop /= 0
                        host_hdsk_out_timeout /= 1
                        self.regs['host_rx_status'].rx_time_out /= 1
                        self.regs['host_control'].trans_req /= 0
                    with elsewhen(utmi_rx_valid_start):
                        with when(utmi_rx_pid_ack_found | utmi_rx_pid_nak_found | utmi_rx_pid_stall_found):
                            host_hdsk_out_wait_eop /= 1
                            pkt_trans_timeout_cnt_inc_reg /= 0

                        self.regs['host_rx_status'].ack_recved /= utmi_rx_pid_ack_found
                        self.regs['host_rx_status'].nak_recved /= utmi_rx_pid_nak_found
                        self.regs['host_rx_status'].stall_recved /= utmi_rx_pid_stall_found
                with other():
                    with when(self.regs['host_control'].iso_en | ~self.io.utmi.RXActive):
                        host_hdsk_out_wait_eop /= 0
                        host_hdsk_out_done /= 1
                        self.regs['host_control'].trans_req /= 0
            with other():
                with when(device_ep_send_stall & ~device_ep_iso_en):
                    self.io.utmi.DataIn /= e_pid_stall
                    device_nak_sent_reg /= 0
                    device_send_stall_reg /= 1
                with elsewhen((device_rx_trans_type_reg == e_device_trans_setup) | device_ep_ready):
                    self.io.utmi.DataIn /= e_pid_ack
                    device_nak_sent_reg /= 0
                    device_send_stall_reg /= 0
                    for i in range(self.p.device_ep_num):
                        with when(device_rx_ep_id_reg == i):
                            device_status_reg_array_trans_type[i] /= device_rx_trans_type_reg
                with other():
                    self.io.utmi.DataIn /= e_pid_nak
                    for i in range(self.p.device_ep_num):
                        with when(device_rx_ep_id_reg == i):
                            device_status_reg_array_nak_trans_type[i] /= device_rx_trans_type_reg
                    #set status's nak_sent
                    with when(~device_ep_iso_en):
                        device_nak_sent_reg /= 1
                    device_send_stall_reg /= 0
                with when(~device_ep_iso_en & (pkt_tx_byte_cnt == 0)):
                    self.io.utmi.TXValid /= 1
                with when(device_ep_iso_en | (pkt_tx_byte_cnt == 1)):
                    self.io.utmi.TXValid /= 0
                    device_hdsk_out_done /= 1
                    device_nak_sent_reg /= 0 #clean it for next
                    device_send_stall_reg /= 0

                    with when(~device_ep_iso_en & device_nak_sent_reg):
                        for i in range(self.p.device_ep_num):
                            with when(device_rx_ep_id_reg == i):
                                device_status_reg_array_nak_sent[i] /= 1

                    with when(~device_ep_iso_en & device_send_stall_reg):
                        for i in range(self.p.device_ep_num):
                            with when(device_rx_ep_id_reg == i):
                                device_status_reg_array_stall_sent[i] /= 1

                    #clean rx ep's ready
                    with when(device_ep_ready & ~device_send_stall_reg):
                        for i in range(self.p.device_ep_num):
                            with when(device_rx_ep_id_reg == i):
                                device_control_reg_array_ready[i] /= 0

        device_hdsk_in_wait_eop = reg_r('device_hdsk_in_wait_eop')
        with when(utmi_state == s_hdsk_in):
            with when(self.io.cfg_mode):
                self.io.utmi.DataIn /= e_pid_ack
                with when(~self.regs['host_control'].iso_en & pkt_tx_byte_cnt == 0):
                    self.io.utmi.TXValid /= 1
                with when(self.regs['host_control'].iso_en | (pkt_tx_byte_cnt == 1)):
                    self.io.utmi.TXValid /= 0
                    host_hdsk_in_done /= 1
                    self.regs['host_control'].trans_req /= 0
            with other():
                with when(~device_ep_iso_en & ~device_hdsk_in_wait_eop):
                    with when(pkt_trans_timeout_cnt_match):
                        device_hdsk_in_wait_eop /= 0
                        device_hdsk_in_timeout /= 1
                        for i in range(self.p.device_ep_num):
                            with when(device_rx_ep_id_reg == i):
                                device_status_reg_array_rx_time_out[i] /= 1

                        #clean rx ep's ready
                        with when(device_ep_ready):
                            for i in range(self.p.device_ep_num):
                                with when(device_rx_ep_id_reg == i):
                                    device_control_reg_array_ready[i] /= 0
                    with when(utmi_rx_valid_start):
                        with when(utmi_rx_pid_ack_found):
                            device_hdsk_in_wait_eop /= 1
                            pkt_trans_timeout_cnt_inc_reg /= 0

                            for i in range(self.p.device_ep_num):
                                with when(device_rx_ep_id_reg == i):
                                    device_status_reg_array_trans_type[i] /= device_rx_trans_type_reg
                                    device_status_reg_array_ack_recved[i] /= 1
                with other():
                    with when(device_ep_iso_en | ~self.io.utmi.RXActive):
                        device_hdsk_in_wait_eop /= 0
                        device_hdsk_in_done /= 1

                        #clean rx ep's ready
                        with when(device_ep_ready):
                            for i in range(self.p.device_ep_num):
                                with when(device_rx_ep_id_reg == i):
                                    device_control_reg_array_ready[i] /= 0


        #interrupt report
        host_int_trans_done_bit = bits('host_int_trans_done_bit', init = 0)
        host_int_resume_bit = bits('host_int_resume_bit', init = 0)
        host_int_con_event_bit = bits('host_int_con_event_bit', init = 0)
        host_int_discon_event_bit = bits('host_int_discon_event_bit', init = 0)
        host_int_sof_sent_bit = bits('host_int_sof_sent_bit', init = 0)

        trans_req_dly = reg_r('trans_req_dly', next = self.regs['host_control'].trans_req)
        HostDisconnect_dly = reg_s('HostDisconnect_dly', next = self.io.utmi.HostDisconnect)
        with when(self.io.cfg_mode):
            with when(~self.regs['host_control'].trans_req & trans_req_dly):
                host_int_trans_done_bit /= 1

            with when(utmi_state == s_con):
                with when(con_end):
                    host_int_con_event_bit /= 1

            with when(self.io.utmi.DpPulldown & self.io.utmi.DmPulldown & self.io.utmi.HostDisconnect & ~HostDisconnect_dly):
                host_int_discon_event_bit /= 1

            with when(utmi_state == s_token_sof):
                with when(host_token_sof_done):
                    host_int_sof_sent_bit /= 1

        self.io.host_int_trans_done   /= pulse_ext_h(host_int_trans_done_bit, 2)
        self.io.host_int_resume       /= pulse_ext_h(host_int_resume_bit, 2)
        self.io.host_int_con_event    /= pulse_ext_h(host_int_con_event_bit, 2)
        self.io.host_int_discon_event /= pulse_ext_h(host_int_discon_event_bit, 2)
        self.io.host_int_sof_sent     /= pulse_ext_h(host_int_sof_sent_bit, 2)


        device_int_trans_done_bit = bits('device_int_trans_done_bit',init = 0)
        device_int_resume_bit = bits('device_int_resume_bit',init = 0)
        device_int_reset_event_bit = bits('device_int_reset_event_bit',init = 0)
        device_int_sof_recv_bit = bits('device_int_sof_recv_bit',init = 0)
        device_int_nak_sent_bit = bits('device_int_nak_sent_bit',init = 0)
        device_int_stall_sent_bit = bits('device_int_stall_sent_bit',init = 0)
        device_int_vbus_det_bit = bits('device_int_vbus_det_bit',init = 0)

        device_reset_tick_least = 120
        device_line_state_cnt = reg_r('device_line_state_cnt', w = 24) 
        with when(~self.io.cfg_mode):
            with when(self.io.utmi.LineState == e_lnst_se0):
                with when(device_line_state_cnt < device_reset_tick_least):
                    device_line_state_cnt /= device_line_state_cnt + 1
            with other():
                device_line_state_cnt /= 0


            with when(utmi_state == s_token_sof):
                with when(device_token_sof_done):
                    device_int_sof_recv_bit /= 1

            with when(utmi_state == s_hdsk_out):
                with when(device_hdsk_out_done):
                    with when(device_send_stall_reg):
                        device_int_stall_sent_bit /= 1
                    with elsewhen(device_nak_sent_reg):
                        device_int_nak_sent_bit /= 1
                    with other():
                        device_int_trans_done_bit /= 1

            with when(utmi_state == s_data_out):
                with when(device_data_out_timeout):
                    device_int_trans_done_bit /= 1

            with when(utmi_state == s_hdsk_in):
                with when(device_hdsk_in_done):
                    device_int_trans_done_bit /= 1
                with when(device_hdsk_in_timeout):
                    device_int_trans_done_bit /= 1

            with when(utmi_state == s_data_in):
                with when(device_data_in_nak):
                    device_int_nak_sent_bit /= 1
                with when(device_data_in_stall):
                    device_int_stall_sent_bit /= 1

            with when(device_line_state_cnt >= device_reset_tick_least):
                device_int_reset_event_bit /= 1

        self.io.device_int_trans_done  /= pulse_ext_h(device_int_trans_done_bit , 2)
        self.io.device_int_resume      /= pulse_ext_h(device_int_resume_bit     , 2)
        self.io.device_int_reset_event /= pulse_ext_h(device_int_reset_event_bit, 2)
        self.io.device_int_sof_recv    /= pulse_ext_h(device_int_sof_recv_bit   , 2)
        self.io.device_int_nak_sent    /= pulse_ext_h(device_int_nak_sent_bit   , 2)
        self.io.device_int_stall_sent  /= pulse_ext_h(device_int_stall_sent_bit   , 2)
        self.io.device_int_vbus_det    /= pulse_ext_h(device_int_vbus_det_bit   , 2)
