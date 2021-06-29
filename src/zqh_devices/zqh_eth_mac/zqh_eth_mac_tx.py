import sys
import os
from phgl_imp import *
from .zqh_eth_mac_parameters import zqh_eth_mac_parameter
from .zqh_eth_mac_bundles import *
from .zqh_eth_mac_fcs_crc import zqh_eth_mac_fcs_crc

class zqh_eth_mac_tx(module):
    def set_par(self):
        super(zqh_eth_mac_tx, self).set_par()
        self.p = zqh_eth_mac_parameter()

    def set_port(self):
        super(zqh_eth_mac_tx, self).set_port()
        self.io.var(ready_valid(
            'ap_tx', 
            gen = zqh_eth_mac_tx_fifo_data_bundle, 
            data_width = self.p.tx_fifo_data_width).flip())
        self.io.var(zqh_eth_mac_phy_gmii_tx_io('phy_gmii_tx'))
        self.io.var(zqh_eth_mac_phy_gmii_cscd_io('phy_gmii_cscd'))
        self.io.var(inp('pause'))
        self.io.var(ready_valid('ap_tx_status', gen = zqh_eth_mac_tx_status_bundle))
        self.io.var(outp('transmitting'))
        self.io.var(inp('cfg_reg_gmii_en'))
        self.io.var(inp('cfg_reg_loopback_en'))
        self.io.var(inp('cfg_reg_backoff_en'))
        self.io.var(inp('cfg_reg_abort_tx'))
        self.io.var(inp('cfg_reg_full_duplex'))
        self.io.var(inp('cfg_reg_crc_en'))
        self.io.var(inp('cfg_reg_big_pkt_en'))
        self.io.var(inp('cfg_reg_pad_en'))
        self.io.var(inp('cfg_reg_ipg', w = 6))
        self.io.var(inp('cfg_reg_max_retry', w = 4))
        self.io.var(inp('cfg_reg_max_fl', w = 16))
        self.io.var(inp('cfg_reg_mac_addr', w = 48))
        self.io.var(inp('abort'))

    def main(self):
        super(zqh_eth_mac_tx, self).main()

        ap_tx_narrow = ready_valid(
            'ap_tx_narrow', 
            gen = zqh_eth_mac_tx_fifo_data_bundle, 
            data_width = 8).as_bits()
        self.data_width_convert(self.p.tx_fifo_data_width, 8, self.io.ap_tx, ap_tx_narrow)

        cscd_cs_sync = async_dff(self.io.phy_gmii_cscd.cs, self.p.sync_delay)
        cscd_cd_sync = async_dff(self.io.phy_gmii_cscd.cd, self.p.sync_delay)
        pause_sync = async_dff(self.io.pause, self.p.sync_delay)
        abort_tx_sync = async_dff(self.io.cfg_reg_abort_tx, self.p.sync_delay)

        carrier_sense = cscd_cs_sync & ~self.io.cfg_reg_full_duplex
        collision = cscd_cd_sync & ~self.io.cfg_reg_full_duplex

        abort_tx_sync_dly1 = reg_r(next = abort_tx_sync)
        abort_tx_sync_pos = abort_tx_sync & ~abort_tx_sync_dly1

        (
            s_idle, s_ipg, s_preamble, s_data, 
            s_pad, s_fcs, s_jam, s_backoff, s_done, s_defer) = range(10)
        tx_state = reg_rs('tx_state', w = 4, rs = s_defer)
        byte_cnt = reg_r('byte_cnt', w = 16)
        byte_cnt_reset = bits(init = 0)
        byte_cnt_set_backoff = bits(init = 0)
        byte_nib = reg_r('byte_nib')
        full_byte = mux(self.io.cfg_reg_gmii_en, 1, byte_nib == 1)
        fcs_cnt = reg_r('fcs_cnt', w = 2)
        ap_tx_sai = reg('ap_tx_sai')
        ap_tx_crc = reg('ap_tx_crc')
        ap_tx_pad = reg('ap_tx_pad')
        retry_cnt = reg_r('retry_cnt', w = 4)
        backoff_time = self.random10_lfsr(retry_cnt)
        flush = reg_r('flush')
        req_blocking = flush | ~self.io.ap_tx_status.ready | pause_sync
        big_pkt_cutoff = (byte_cnt == self.io.cfg_reg_max_fl) & ~self.io.cfg_reg_big_pkt_en
        collision_reg = reg_r('collision_reg')


        ####
        #FSM control
        with when(tx_state == s_defer):
            with when(~carrier_sense):
                tx_state /= s_ipg
                byte_cnt_reset /= 1
        with when(tx_state == s_ipg):
            with when(carrier_sense):
                tx_state /= s_defer
            with elsewhen(full_byte):
                with when(byte_cnt == self.io.cfg_reg_ipg):
                    tx_state /= s_idle
        with when(tx_state == s_idle):
            with when(carrier_sense):
                tx_state /= s_defer
            with elsewhen(~req_blocking & ap_tx_narrow.valid & ap_tx_narrow.bits.start):
                tx_state /= s_preamble
                byte_cnt_reset /= 1
                byte_nib /= 0
                fcs_cnt /= 0

                ap_tx_sai /= ap_tx_narrow.bits.sai
                ap_tx_crc /= ap_tx_narrow.bits.crc
                ap_tx_pad /= ap_tx_narrow.bits.pad
        with when(tx_state == s_preamble):
            with when(full_byte & (byte_cnt[2:0] == 7)):
                with when(collision_reg):
                    tx_state /= s_jam
                    byte_cnt_reset /= 1
                with other():
                    tx_state /= s_data
                    byte_cnt_reset /= 1
        with when(tx_state == s_jam):
            with when(full_byte):
                #after preamble/sfd, send 4 byte 0x9 collision patten
                with when(byte_cnt == 3):
                    with when(self.io.cfg_reg_backoff_en):
                        tx_state /= s_backoff
                        byte_cnt_set_backoff /= 1
                    with other():
                        tx_state /= s_defer
        with when(tx_state == s_backoff):
            with when(full_byte):
                with when(byte_cnt == 0):
                    tx_state /= s_defer
        with when(tx_state == s_data):
            with when(collision_reg):
                tx_state /= s_jam
                byte_cnt_reset /= 1
            with elsewhen(full_byte):
                with when(ap_tx_narrow.valid & ap_tx_narrow.bits.end):
                    with when((byte_cnt < 59) & (self.io.cfg_reg_pad_en & ap_tx_pad)):
                        tx_state /= s_pad
                    with elsewhen(self.io.cfg_reg_crc_en & ap_tx_crc):
                        tx_state /= s_fcs
                    with other():
                        tx_state /= s_done
            with elsewhen(big_pkt_cutoff):
                tx_state /= s_defer
        with when(tx_state == s_pad):
            with when(collision_reg):
                tx_state /= s_jam
                byte_cnt_reset /= 1
            with elsewhen(full_byte):
                with when(byte_cnt == 59):
                    with when(self.io.cfg_reg_crc_en & ap_tx_crc):
                        tx_state /= s_fcs
                    with other():
                        tx_state /= s_done
        with when(tx_state == s_fcs):
            with when(collision_reg):
                tx_state /= s_jam
                byte_cnt_reset /= 1
            with elsewhen(full_byte):
                with when(fcs_cnt == 3):
                    tx_state /= s_done
            with elsewhen(big_pkt_cutoff):
                tx_state /= s_defer
        with when(tx_state == s_done):
            tx_state /= s_defer

        ####
        #counter increase according FSM
        with when(byte_cnt_reset):
            byte_cnt /= 0
        with elsewhen(byte_cnt_set_backoff):
            byte_cnt /= backoff_time
        with elsewhen(tx_state.match_any([s_preamble, s_data, s_pad, s_fcs, s_jam, s_ipg])):
            with when(full_byte):
                with when(byte_cnt != 0xffff):
                    byte_cnt /= byte_cnt + 1
        with elsewhen(tx_state == s_backoff):
            with when(full_byte):
                with when(byte_cnt != 0):
                    byte_cnt /= byte_cnt - 1

        with when(tx_state != s_idle):
            with when(~self.io.cfg_reg_gmii_en):
                byte_nib /= ~byte_nib
        with when(tx_state == s_fcs):
            with when(full_byte):
                fcs_cnt /= fcs_cnt + 1

        with when(tx_state.match_any([s_preamble, s_data, s_pad, s_fcs])):
            with when(collision):
                collision_reg /= 1
        with other():
            collision_reg /= 0

        status_cs_lost_reg = reg('status_cs_lost_reg')
        with when(tx_state == s_idle):
            status_cs_lost_reg /= 0
        with elsewhen(tx_state.match_any([s_data, s_pad, s_fcs])):
            with when(
                ~self.io.cfg_reg_full_duplex & 
                ~self.io.cfg_reg_loopback_en & 
                ~cscd_cs_sync & ~cscd_cd_sync):
                status_cs_lost_reg /= 1

        status_defer_reg = reg_r('status_defer_reg')
        with when(self.io.ap_tx_status.valid):
            status_defer_reg /= 0
        with when(tx_state == s_idle):
            with when(carrier_sense):
                #this tx req is delayed by defer
                with when(~req_blocking & ap_tx_narrow.valid):
                    status_defer_reg /= 1


        self.io.ap_tx_status.valid /= 0
        self.io.ap_tx_status.bits.retry /= 0
        self.io.ap_tx_status.bits.abort /= 0
        self.io.ap_tx_status.bits.done /= 0
        self.io.ap_tx_status.bits.retry_limit /= 0
        self.io.ap_tx_status.bits.cs_lost/= status_cs_lost_reg
        self.io.ap_tx_status.bits.defer /= status_defer_reg
        self.io.ap_tx_status.bits.retry_cnt /= retry_cnt
        self.io.ap_tx_status.bits.too_long /= 0
        self.io.ap_tx_status.bits.defer_abort /= 0
        with when(tx_state == s_done):
            retry_cnt /= 0
            self.io.ap_tx_status.valid /= 1
            self.io.ap_tx_status.bits.done /= 1
        with elsewhen(tx_state.match_any([s_preamble, s_data, s_pad, s_fcs])):
            with when(collision & ~collision_reg):
                flush /= 1
                with when(retry_cnt == self.io.cfg_reg_max_retry):
                    retry_cnt /= 0
                    self.io.ap_tx_status.valid /= 1
                    self.io.ap_tx_status.bits.abort /= 1
                    self.io.ap_tx_status.bits.retry_limit /= 1
                with other():
                    retry_cnt /= retry_cnt + 1
                    self.io.ap_tx_status.valid /= 1
                    self.io.ap_tx_status.bits.retry /= 1
            with other():
                with when(big_pkt_cutoff):
                    flush /= 1
                    retry_cnt /= 0
                    self.io.ap_tx_status.valid /= 1
                    self.io.ap_tx_status.bits.abort /= 1
                    self.io.ap_tx_status.bits.too_long /= 1
        with elsewhen(tx_state.match_any([s_defer])):
            with when(carrier_sense):
                with when(abort_tx_sync_pos):
                    with when(~req_blocking & ap_tx_narrow.valid):
                        flush /= 1
                        retry_cnt /= 0
                        self.io.ap_tx_status.valid /= 1
                        self.io.ap_tx_status.bits.abort /= 1
                        self.io.ap_tx_status.bits.defer_abort /= 1

        with when(flush):
            with when(ap_tx_narrow.fire() & ap_tx_narrow.bits.ack):
                flush /= 0


        ####
        #ap_tx_narrow's ready
        ap_tx_narrow.ready /= 0
        with when(tx_state == s_data):
            with when(full_byte):
                ap_tx_narrow.ready /= 1
        #flush all ap_tx_narrow's data untill ack
        with when(flush):
            ap_tx_narrow.ready /= 1


        ####
        #phy's tx
        self.io.phy_gmii_tx.gclk /= mux(self.io.cfg_reg_gmii_en, self.io.clock, 0)
        gmii_tx_en_reg = reg_r(next = 0)
        gmii_tx_err_reg = reg_r(next = 0)
        gmii_tx_d_reg = reg(w = self.io.phy_gmii_tx.d.get_w())
        self.io.phy_gmii_tx.en /= gmii_tx_en_reg
        self.io.phy_gmii_tx.err /= gmii_tx_err_reg
        with when(tx_state.match_any([s_preamble, s_data, s_pad, s_fcs, s_jam])):
            gmii_tx_en_reg /= 1

        with when(tx_state.match_any([s_data, s_fcs])):
            with when(~collision_reg & big_pkt_cutoff):
                gmii_tx_err_reg /= 1
            with other():
                gmii_tx_err_reg /= 0
        with other():
            gmii_tx_err_reg /= 0

        gmii_tx_byte = bits('gmii_tx_byte', w = 8, init = 0)
        with when(tx_state == s_preamble):
            with when(byte_cnt[2:0] == 7):
                gmii_tx_byte /= 0xd5
            with other():
                gmii_tx_byte /= 0x55
        with when(tx_state == s_jam):
            gmii_tx_byte /= 0x99
        with when(tx_state == s_pad):
            gmii_tx_byte /= 0x00
        with when(tx_state == s_data):
            sai_byte_map = list(map(lambda _: byte_cnt == _, range(6, 12)))
            mac_sa = list(reversed(self.io.cfg_reg_mac_addr.grouped(8)))
            with when(ap_tx_sai & reduce(lambda a,b: a | b, sai_byte_map)):
                gmii_tx_byte /= sel_oh(sai_byte_map, mac_sa)
            with other():
                gmii_tx_byte /= ap_tx_narrow.bits.data

        pre_crc_nib = mux(full_byte, gmii_tx_byte[7:4], gmii_tx_byte[3:0])
        crc_data_reg = zqh_eth_mac_fcs_crc(
                tx_state.match_any([s_idle, s_preamble]),
                0xffffffff,
                tx_state.match_any([s_data, s_pad]) & full_byte,
                gmii_tx_byte)
        gmii_tx_d_4b = mux(tx_state == s_fcs,
            sel_bin(cat([fcs_cnt, full_byte]), (~crc_data_reg).order_invert().grouped(4)),
            pre_crc_nib)
        gmii_tx_d = mux(tx_state == s_fcs,
            sel_bin(fcs_cnt, (~crc_data_reg).order_invert().grouped(8)),
            gmii_tx_byte)

        gmii_tx_d_reg /= mux(self.io.cfg_reg_gmii_en, gmii_tx_d, gmii_tx_d_4b)
        self.io.phy_gmii_tx.d /= gmii_tx_d_reg

        self.io.transmitting /= gmii_tx_en_reg

    def random10_lfsr(self, retry_cnt):
        rand_r = reg_r(w = 10)
        rand_r /= cat([rand_r[8:0], ~(rand_r[2] ^ rand_r[9])])
        return sel_map(retry_cnt,
            ((0, rand_r[0:0].u_ext(10)),
             (1, rand_r[1:0].u_ext(10)),
             (2, rand_r[2:0].u_ext(10)),
             (3, rand_r[3:0].u_ext(10)),
             (4, rand_r[4:0].u_ext(10)),
             (5, rand_r[5:0].u_ext(10)),
             (6, rand_r[6:0].u_ext(10)),
             (7, rand_r[7:0].u_ext(10)),
             (8, rand_r[8:0].u_ext(10))),
            rand_r)

    def data_width_convert(self, wide_w, narrow_w, wide_p, narrow_p):
        assert(wide_w >= narrow_w)
        assert(wide_w % 8 == 0)
        assert(narrow_w == 8)

        if (narrow_w == wide_w):
            narrow_p /= wide_p
        else:
            start_byte_map = reg_r(w = wide_p.bits.start.get_w())

            narrow_p.valid /= wide_p.valid
            narrow_p.bits.start /= 0
            narrow_p.bits.end /= 0
            narrow_p.bits.sai /= wide_p.bits.sai
            narrow_p.bits.crc /= wide_p.bits.crc
            narrow_p.bits.pad /= wide_p.bits.pad
            narrow_p.bits.ack /= wide_p.bits.ack
            narrow_data_sel = bits(w = wide_w//narrow_w, init = 0)

            with when(narrow_p.fire()):
                with when(wide_p.fire()):
                    start_byte_map /= 0
                with other():
                    start_byte_map /= narrow_data_sel << 1

            with when(wide_p.bits.start != 0):
                with when(start_byte_map == 0):
                    narrow_p.bits.start /= 1

            with when(wide_p.bits.end != 0):
                with when(narrow_data_sel == cat_rvs(wide_p.bits.end.grouped(narrow_w//8))):
                    narrow_p.bits.end /= 1

            with when(start_byte_map == 0):
                with when(wide_p.bits.start != 0):
                    narrow_data_sel /= cat_rvs(map(
                        lambda _: _.r_or(), 
                        wide_p.bits.start.grouped(narrow_w//8)))
                with other():
                    narrow_data_sel /= 1
            with other():
                narrow_data_sel /= cat_rvs(
                    map(lambda _: _.r_or(), start_byte_map.grouped(narrow_w//8)))
            narrow_p.bits.data /= sel_oh(
                narrow_data_sel, 
                wide_p.bits.data.grouped(narrow_w))

            wide_p.ready /= 0
            with when(narrow_p.ready):
                with when(narrow_data_sel == cat_rvs(wide_p.bits.end.grouped(narrow_w//8))):
                    wide_p.ready /= narrow_p.ready
                with elsewhen(narrow_data_sel.msb()):
                    wide_p.ready /= narrow_p.ready
                with other():
                    wide_p.ready /= 0
