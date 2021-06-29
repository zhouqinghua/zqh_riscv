import sys
import os
from phgl_imp import *
from .zqh_eth_mac_parameters import zqh_eth_mac_parameter
from .zqh_eth_mac_bundles import *
from .zqh_eth_mac_fcs_crc import zqh_eth_mac_fcs_crc

class zqh_eth_mac_rx(module):
    def set_par(self):
        super(zqh_eth_mac_rx, self).set_par()
        self.p = zqh_eth_mac_parameter()

    def set_port(self):
        super(zqh_eth_mac_rx, self).set_port()
        self.io.var(zqh_eth_mac_phy_gmii_rx_io('phy_gmii_rx'))
        self.io.var(zqh_eth_mac_phy_gmii_cscd_io('phy_gmii_cscd'))
        self.io.var(inp('transmitting'))
        self.io.var(ready_valid(
            'ap_rx', 
            gen = zqh_eth_mac_rx_fifo_data_bundle,
            data_width = self.p.rx_fifo_data_width))
        self.io.var(outp('pause'))
        self.io.var(inp('cfg_reg_gmii_en'))
        self.io.var(inp('cfg_reg_rx_en'))
        self.io.var(inp('cfg_reg_min_fl', w = 16))
        self.io.var(inp('cfg_reg_max_fl', w = 16))
        self.io.var(inp('cfg_reg_ipg_rx_en'))
        self.io.var(inp('cfg_reg_big_pkt_en'))
        self.io.var(inp('cfg_reg_small_pkt_rx_en'))
        self.io.var(inp('cfg_reg_mac_addr', w = 48))
        self.io.var(inp('cfg_reg_multicast_hash', w = 64))
        self.io.var(inp('cfg_reg_chk_da_en'))
        self.io.var(inp('cfg_reg_bro_rx_en'))
        self.io.var(inp('cfg_reg_pass_all'))
        self.io.var(inp('cfg_reg_rx_flow'))
        self.io.var(inp('cfg_reg_full_duplex'))

    def main(self):
        super(zqh_eth_mac_rx, self).main()

        ap_rx_narrow = ready_valid(
            'ap_rx_narrow', 
            gen = zqh_eth_mac_rx_fifo_data_with_status_bundle, 
            data_width = 8).as_bits()
        self.data_width_convert(8, self.p.rx_fifo_data_width, ap_rx_narrow, self.io.ap_rx)

        transmitting_sync = async_dff(
            self.io.transmitting, 
            self.p.sync_delay) & ~self.io.cfg_reg_full_duplex
        rx_en_sync = async_dff(
            self.io.cfg_reg_rx_en,
            self.p.sync_delay) #rx_en can be dynamic configure, need sync
        cscd_cd_sync = async_dff(self.io.phy_gmii_cscd.cd, self.p.sync_delay)

        #rx_dv, rx_d, rx_err delay 3 cycle
        rx_dv_dly0 = reg_r('rx_dv_dly0', next = self.io.phy_gmii_rx.dv)
        rx_err_dly0 = reg_r('rx_err_dly0', next = self.io.phy_gmii_rx.err)
        rx_d_dly0 = reg_r('rx_d_dly0', w = self.io.phy_gmii_rx.d.get_w(), next = self.io.phy_gmii_rx.d)
        rx_dv_dly1 = reg_r('rx_dv_dly1', next = rx_dv_dly0)
        rx_err_dly1 = reg_r('rx_err_dly1', next = rx_err_dly0 )
        rx_d_dly1 = reg_r('rx_d_dly1', w = self.io.phy_gmii_rx.d.get_w(), next = rx_d_dly0)
        rx_dv_dly2 = reg_r('rx_dv_dly2', next = rx_dv_dly1)
        rx_err_dly2 = reg_r('rx_err_dly2', next = rx_err_dly1 )
        rx_d_dly2 = reg_r('rx_d_dly2', w = self.io.phy_gmii_rx.d.get_w(), next = rx_d_dly1)
        rx_dv_posedge = rx_dv_dly1 & ~rx_dv_dly2

        collision = cscd_cd_sync & ~self.io.cfg_reg_full_duplex

        (s_idle, s_preamble_sfd, s_data, s_done, s_drop) = range(5)
        rx_state = reg_rs('rx_state', w = 3, rs = s_idle)
        byte_cnt = reg_r('byte_cnt', w = 16)
        byte_cnt_reset = bits(init = 0)
        byte_nib = reg_r('byte_nib')
        full_byte = mux(self.io.cfg_reg_gmii_en, 1, byte_nib == 1)
        ipg_cnt = reg_r('ipg_cnt', w = 6)
        big_pkt_cutoff = (byte_cnt == self.io.cfg_reg_max_fl) & ~self.io.cfg_reg_big_pkt_en
        preamble_match = mux(
            self.io.cfg_reg_gmii_en, 
            #tmp self.io.phy_gmii_rx.d == 0x55, 
            #tmp self.io.phy_gmii_rx.d[3:0] == 0x5)
            rx_d_dly1 == 0x55, 
            rx_d_dly1[3:0] == 0x5)
        sfd_match = mux(
            self.io.cfg_reg_gmii_en, 
            #tmp self.io.phy_gmii_rx.d == 0xd5, 
            #tmp self.io.phy_gmii_rx.d[3:0] == 0xd)
            rx_d_dly1 == 0xd5, 
            rx_d_dly1[3:0] == 0xd)

        with when(rx_state == s_idle):
            with when(rx_en_sync):
                #tmp with when(self.io.phy_gmii_rx.dv):
                with when(rx_dv_posedge):
                    with when(transmitting_sync):
                        rx_state /= s_drop
                    with elsewhen(preamble_match):
                        rx_state /= s_preamble_sfd
                        byte_nib /= 0
                        byte_cnt_reset /= 1
        with when(rx_state == s_preamble_sfd):
            with when(transmitting_sync):
                rx_state /= s_drop
            #tmp with elsewhen(self.io.phy_gmii_rx.dv):
            with elsewhen(rx_dv_dly1):
                with when(sfd_match):
                    with when((ipg_cnt == self.p.min_rx_ipg) | ~self.io.cfg_reg_ipg_rx_en):
                        rx_state /= s_data
                    with other():
                        rx_state /= s_drop
                with elsewhen(preamble_match):
                    rx_state /= s_preamble_sfd
                with other():
                    rx_state /= s_drop
            with other():
                rx_state /= s_idle
        with when(rx_state == s_data):
            #tmp with when(~self.io.phy_gmii_rx.dv):
            with when(~rx_dv_dly1):
                rx_state /= s_done
            with other():
                with when(big_pkt_cutoff):
                    rx_state /= s_drop
        with when(rx_state == s_done):
            rx_state /= s_idle
        with when(rx_state == s_drop):
            #tmp with when(~self.io.phy_gmii_rx.dv):
            with when(~rx_dv_dly1):
                rx_state /= s_idle


        with when(~rx_state.match_any([s_idle, s_preamble_sfd])):
            with when(~self.io.cfg_reg_gmii_en):
                byte_nib /= ~byte_nib
        with when(byte_cnt_reset):
            byte_cnt /= 0
        with elsewhen(rx_state == s_data):
            with when(full_byte):
                #tmp with when(self.io.phy_gmii_rx.dv):
                with when(rx_dv_dly1):
                    with when(byte_cnt != 0xffff):
                        byte_cnt /= byte_cnt + 1

        with when(rx_state.match_any([s_done, s_drop])):
            ipg_cnt /= 0
        with when(rx_state.match_any([s_idle, s_preamble_sfd])):
            with when(ipg_cnt != self.p.min_rx_ipg):
                ipg_cnt /= ipg_cnt + 1


        #tmp nib_buf = reg(w = 4, next = self.io.phy_gmii_rx.d[3:0])
        nib_buf = reg(w = 4, next = rx_d_dly1[3:0])
        phy_byte_merged = mux(
            self.io.cfg_reg_gmii_en,
            #tmp self.io.phy_gmii_rx.d,
            rx_d_dly1,
            #tmp cat([self.io.phy_gmii_rx.d[3:0], nib_buf]))
            cat([rx_d_dly1[3:0], nib_buf]))
        ap_rx_valid_reg = reg_r(next = 0)
        ap_rx_bits_start_reg = reg(next = 0)
        ap_rx_bits_end_reg = reg(next = 0)
        ap_rx_bits_is_status_reg = reg(next = 0)
        ap_rx_bits_data_reg = reg(
            w = ap_rx_narrow.bits.data.get_w(), 
            next = phy_byte_merged)

        ap_rx_narrow.valid /= ap_rx_valid_reg
        ap_rx_narrow.bits.start /= ap_rx_bits_start_reg
        ap_rx_narrow.bits.end /= ap_rx_bits_end_reg
        ap_rx_narrow.bits.is_status /= ap_rx_bits_is_status_reg
        ap_rx_narrow.bits.data /= ap_rx_bits_data_reg

        with when(rx_state == s_data):
            with when(full_byte):
                #tmp with when(self.io.phy_gmii_rx.dv):
                with when(rx_dv_dly1):
                    ap_rx_valid_reg /= 1
                with when(byte_cnt == 0):
                    ap_rx_bits_start_reg /= 1
            #tmp with when(~self.io.phy_gmii_rx.dv | big_pkt_cutoff):
            with when(~rx_dv_dly1 | big_pkt_cutoff):
                ap_rx_narrow.bits.end /= 1

        crc_data_reg = zqh_eth_mac_fcs_crc(
                rx_state.match_any([s_preamble_sfd]),
                0xffffffff,
                rx_state.match_any([s_data]) & (
                    #tmp self.io.phy_gmii_rx.dv & ~big_pkt_cutoff) & full_byte,
                    rx_dv_dly1 & ~big_pkt_cutoff) & full_byte,
                phy_byte_merged)
        crc_err_reg = reg_r('crc_err_reg')
        with when(rx_state.match_any([s_done, s_drop])):
            crc_err_reg /= crc_data_reg != 0xc704dd7b

        phy_rx_err_reg = reg_r('phy_rx_err_reg')
        phy_rx_ivs_reg = reg_r('phy_rx_ivs_reg')
        #tmp with when(self.io.phy_gmii_rx.dv & rx_en_sync):
        with when(rx_dv_dly1 & rx_en_sync):
            #tmp phy_rx_err_reg /= self.io.phy_gmii_rx.err | phy_rx_err_reg
            phy_rx_err_reg /= rx_err_dly1 | phy_rx_err_reg
            phy_rx_ivs_reg /= (
                #tmp (self.io.phy_gmii_rx.err & (self.io.phy_gmii_rx.d[3:0] == 0xe)) | 
                #tmp (self.io.phy_gmii_rx.err & (rx_d_dly1[3:0] == 0xe)) | 
                (rx_err_dly1 & (rx_d_dly1[3:0] == 0xe)) | 
                phy_rx_ivs_reg)

        #pause frame decect
        pause_frame_reg = reg_r('pause_frame_reg')
        pause_frame_type_length = value(0x8808, w = 16).to_bits()
        pause_frame_code = value(0x0001, w = 16).to_bits()
        pause_frame_para = reg('pause_frame_para', w = 16)
        with when(rx_state == s_data):
            with when(full_byte):
                with when(byte_cnt == 12):
                    pause_frame_reg /= phy_byte_merged == pause_frame_type_length[15:8]
                with when(byte_cnt == 13):
                    pause_frame_reg /= (
                        (phy_byte_merged == pause_frame_type_length[7:0]) & 
                        pause_frame_reg)
                with when(byte_cnt == 14):
                    pause_frame_reg /= (
                        (phy_byte_merged == pause_frame_code[15:8]) & 
                        pause_frame_reg)
                with when(byte_cnt == 15):
                    pause_frame_reg /= (
                        (phy_byte_merged == pause_frame_code[7:0]) & 
                        pause_frame_reg)

                with when(byte_cnt == 16):
                    pause_frame_para[15:8] /= phy_byte_merged
                with when(byte_cnt == 17):
                    pause_frame_para[7:0] /= phy_byte_merged

        #collision detect
        late_collision_happen_reg = reg_r('late_collision_happen_reg')
        with when(rx_state == s_data):
            late_collision_happen_reg /= collision | late_collision_happen_reg

        #dribble nibble detect
        dribble_nibble_reg = reg_r('dribble_nibble_reg')
        with when(rx_state == s_data):
            with when(full_byte):
                #tmp with when(~self.io.cfg_reg_gmii_en & ~self.io.phy_gmii_rx.dv):
                with when(~self.io.cfg_reg_gmii_en & ~rx_dv_dly1):
                    dribble_nibble_reg /= 1

        #dest mac address miss detect
        mac_address_unicast_match_reg = reg_r('mac_address_unicast_match_reg')
        mac_addr_unicast_group = list(reversed(self.io.cfg_reg_mac_addr.grouped(8)))
        mac_address_broadcast_match_reg = reg_r('mac_address_broadcast_match_reg')
        mac_address_multicast_match_reg = reg_r('mac_address_multicast_match_reg')
        mac_addr_pause_group = list(reversed(
            value(0x0180C2000001, w = 48).to_bits().grouped(8)))
        mac_address_pause_match_reg = reg_r('mac_address_pause_match_reg')
        mac_address_umb_match = (
            mac_address_unicast_match_reg |
            (mac_address_broadcast_match_reg & self.io.cfg_reg_bro_rx_en) |
            mac_address_multicast_match_reg)
        mac_address_miss = ~(
            mac_address_umb_match | 
            (mac_address_pause_match_reg & self.io.cfg_reg_pass_all))
        mac_address_pass2ap = mac_address_umb_match | ~self.io.cfg_reg_chk_da_en
        with when(rx_state == s_data):
            with when(full_byte):
                for i in range(6):
                    with when(byte_cnt == i):
                        mac_address_unicast_match_reg /= (
                            (phy_byte_merged == mac_addr_unicast_group[i]) & 
                            (mac_address_unicast_match_reg if (i > 0) else 1))
                        mac_address_broadcast_match_reg /= (
                            (phy_byte_merged == 0xff) & 
                            (mac_address_broadcast_match_reg if (i > 0) else 1))
                        mac_address_pause_match_reg /= (
                            (phy_byte_merged == mac_addr_pause_group[i]) & 
                            (mac_address_pause_match_reg if (i > 0) else 1))

                with when(byte_cnt == 0):
                    with when(phy_byte_merged[0]):
                        mac_address_multicast_match_reg /= 1
            with other():
                with when(byte_cnt == 6):
                    mac_address_multicast_match_reg /= (
                        self.io.cfg_reg_multicast_hash[crc_data_reg.msb(6)] & 
                        mac_address_multicast_match_reg)

        #gen rx status and send to ap
        #pack each status bit
        rx_status = zqh_eth_mac_rx_status_bundle('rx_status', init = 0)
        rx_status.abort /= (
            ~mac_address_pass2ap |
            ((byte_cnt < self.io.cfg_reg_min_fl) & ~self.io.cfg_reg_small_pkt_rx_en) |
            (phy_rx_err_reg & ~phy_rx_ivs_reg) |
            (pause_frame_reg & ~self.io.cfg_reg_pass_all))
        rx_status.crc_err /= crc_err_reg & (byte_cnt > 4)
        rx_status.invalid_symbol /= phy_rx_ivs_reg
        rx_status.short_frame /= byte_cnt < self.io.cfg_reg_min_fl
        rx_status.long_frame /= (
            (byte_cnt > self.io.cfg_reg_max_fl) & 
            ~self.io.cfg_reg_big_pkt_en) | big_pkt_cutoff
        rx_status.dribble_nibble /= dribble_nibble_reg
        rx_status.da_miss /= mac_address_miss
        rx_status.pause_frame /= pause_frame_reg
        rx_status.late_collision /= (
            late_collision_happen_reg & self.io.cfg_reg_small_pkt_rx_en)
        ap_rx_narrow.bits.status /= rx_status
        with when(full_byte):
            with when(
                (rx_state == s_done) | 
                ((rx_state == s_drop) & big_pkt_cutoff)):
                ap_rx_valid_reg /= 1
                ap_rx_bits_start_reg /= 1
                ap_rx_bits_end_reg /= 1
                ap_rx_bits_is_status_reg /= 1

        #clean status reg and prepare for next frame
        with when(
            (ap_rx_valid_reg & ap_rx_bits_is_status_reg) |
            ((rx_state == s_drop) & ~big_pkt_cutoff) |
            (rx_state == s_idle)):
            phy_rx_err_reg /= 0
            phy_rx_ivs_reg /= 0
            pause_frame_reg /= 0
            late_collision_happen_reg /= 0
            dribble_nibble_reg /= 0
            mac_address_unicast_match_reg /= 0
            mac_address_broadcast_match_reg /= 0
            mac_address_multicast_match_reg /= 0
            mac_address_pause_match_reg /= 0


        ####
        #process pause timer
        pause_valid = reg_r('pause_valid')
        pause_timer = reg_r('pause_timer', w = 16)
        pause_unit_timer = reg_r('pause_unit_timer', w = 7)
        with when(
            pause_frame_reg & 
            (mac_address_unicast_match_reg | mac_address_pause_match_reg) &
            ap_rx_valid_reg & 
            ap_rx_bits_is_status_reg & 
            self.io.cfg_reg_rx_flow):
            pause_timer /= pause_frame_para
            pause_unit_timer /= 0
        with when(pause_valid & ~transmitting_sync):
            pause_unit_timer /= pause_unit_timer + 1
            with when(pause_unit_timer.r_and()):
                with when(pause_timer != 0):
                    pause_timer /= pause_timer - 1
        with when(pause_timer == 0):
            pause_valid /= 0
        with other():
            pause_valid /= 1
        self.io.pause /= pause_valid

    def data_width_convert(self, narrow_w, wide_w, narrow_p, wide_p):
        assert(wide_w >= narrow_w)
        assert(wide_w % 8 == 0)
        assert(narrow_w == 8)

        if (wide_w == narrow_w):
            wide_p /= narrow_p
        else:
            byte_cnt = reg_r(w = log2_ceil(wide_w // narrow_w))
            byte_buf = vec(
                gen = lambda _: reg(_, w = narrow_w), 
                n = wide_w // narrow_w - 1)
            start_reg = reg_r()
            #TBD no_space = narrow_p.valid & ~narrow_p.ready
            no_space = 0
            
            narrow_p.ready /= wide_p.ready

            with when(narrow_p.fire()):
                with when(~start_reg):
                    with when(narrow_p.bits.start & ~narrow_p.bits.end):
                        start_reg /= 1
                with other():
                    with when(narrow_p.bits.end):
                        start_reg /= 0
                    with elsewhen(byte_cnt == ((wide_w // narrow_w) - 1)):
                        start_reg /= 0

            with when(narrow_p.fire()):
                with when(narrow_p.bits.end):
                    byte_cnt /= 0
                with other():
                    byte_cnt /= byte_cnt + 1

            #ap has no space to buffer max_rx's data, need reset state reg
            with when(no_space):
                byte_cnt /= 0
                start_reg /= 0

            wide_p.bits.start /= 0
            with when(narrow_p.bits.start & narrow_p.bits.end):
                wide_p.bits.start /= 1
            with elsewhen(start_reg):
                with when(narrow_p.bits.end):
                    wide_p.bits.start /= 1
                with elsewhen(byte_cnt == ((wide_w // narrow_w) - 1)):
                    wide_p.bits.start /= 1

            wide_p.bits.end /= 0
            with when(narrow_p.bits.end):
                wide_p.bits.end /= mux(narrow_p.bits.is_status,
                    1 << (wide_p.bits.end.get_w() - 1),
                    bin2oh(byte_cnt))

            wide_p.bits.is_status /= narrow_p.bits.is_status

            byte_buf(byte_cnt, narrow_p.bits.data)
            wide_data_map = list(map(
                lambda _: mux(byte_cnt == _, narrow_p.bits.data, byte_buf[_])
                    if (_ < len(byte_buf)) else narrow_p.bits.data,
                range(wide_w // narrow_w)))
            wide_p.bits.data /= mux(narrow_p.bits.is_status,
                narrow_p.bits.status.pack(),
                cat_rvs(wide_data_map))

            wide_p.valid /= 0
            with when(narrow_p.valid):
                with when(narrow_p.bits.end):
                    wide_p.valid /= 1
                with elsewhen(byte_cnt == ((wide_w // narrow_w) - 1)):
                    wide_p.valid /= 1
