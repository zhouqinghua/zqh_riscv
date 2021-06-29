import sys
import os
from phgl_imp import *
from zqh_common.zqh_replacement import zqh_pseudo_lru
from .zqh_core_common_btb_parameters import zqh_core_common_btb_parameter
from .zqh_core_common_btb_bundles import *
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_cpu_req
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_cpu_resp
from .zqh_core_common_misc import I_CONSTS
from .zqh_core_common_misc import CFI_CONSTS
from .zqh_core_common_misc import IMM_GEN
from .zqh_core_common_misc import IFU_CONSTS

class zqh_core_common_btb(module):
    def set_par(self):
        super(zqh_core_common_btb, self).set_par()
        self.p = zqh_core_common_btb_parameter()

    def set_port(self):
        super(zqh_core_common_btb, self).set_port()
        self.io.var(valid('lookup_req', gen = zqh_core_common_btb_req).flip())
        self.io.var(valid('lookup_resp', gen = zqh_core_common_btb_resp))
        self.io.var(valid('btb_update', gen = zqh_core_common_btb_update).flip())

    def main(self):
        super(zqh_core_common_btb, self).main()
        max_fetch_width = 2 if (self.p.isa_c) else 1
        replace = zqh_pseudo_lru(n = self.p.num_entries)


        cam_valids = vec(
            'cam_valids',
            gen = reg_r,
            n = self.p.num_entries)
        cam_entries = vec(
            'cam_entries',
            gen = lambda _: zqh_core_common_btb_cam_entry(_).as_reg(),
            n = self.p.num_entries)
        tgt_entries = vec(
            'tgt_entries',
            gen = lambda _: zqh_core_common_btb_tgt_entry(_).as_reg(),
            n = self.p.num_entries)


        ####
        #btb update control
        cam_update_match_map = cat_rvs(map(
            lambda _: cam_valids[_] & (cam_entries[_].pc == self.io.btb_update.bits.pc),
            range(self.p.num_entries)))
        cam_update_match_any = cam_update_match_map.r_or()
        cam_update_replace_map = bin2oh(replace.replace(), w = self.p.num_entries)
        cam_update_map = mux(
            cam_update_match_any,
            cam_update_match_map,
            cam_update_replace_map)
        cam_update_addr = oh2bin(cam_update_map)

        with when(self.io.btb_update.valid):
            for i in range(self.p.num_entries):
                with when(cam_update_map[i]):
                    cam_valids[i] /= 1
                    cam_entries[i].pc /= self.io.btb_update.bits.pc
                    cam_entries[i].rvc /= (
                        self.io.btb_update.bits.rvc if (self.p.isa_c) else 0)
                    cam_entries[i].rvi_half /= (
                        self.io.btb_update.bits.rvi_half  if (self.p.isa_c) else 0)
                    cam_entries[i].cfi_type /= self.io.btb_update.bits.cfi_type
                    cam_entries[i].taken /= self.io.btb_update.bits.taken

                    #only update target talbe when taken happen
                    with when(self.io.btb_update.bits.taken):
                        tgt_entries[i].tgt /= self.io.btb_update.bits.tgt


        ####
        #btb lookup control from ifu's fetch request
        cam_lookup_msb_map = cat_rvs(
            map(
                lambda _: cam_valids[_] & (
                    (cam_entries[_].pc >> 2)  == (self.io.lookup_req.bits.pc >> 2)),
                range(self.p.num_entries)))
        cam_lookup_lsb_map = cat_rvs(
            map(
                lambda _: 
                    (cam_entries[_].pc[1:0]  == self.io.lookup_req.bits.pc[1:0])
                    if (self.p.isa_c) else 1,
                range(self.p.num_entries)))
        cam_lookup_entry_lsb_w_map = cat_rvs(
            map(lambda _: cam_entries[_].pc[1:0]  == 0,
                range(self.p.num_entries)))
        cam_lookup_entry_lsb_h_map = cat_rvs(
            map(lambda _: (cam_entries[_].pc[1:0]  == 2) if (self.p.isa_c) else 0,
                range(self.p.num_entries)))
        cam_lookup_msb_entry_lsb_w_map = cat_rvs(
            map(lambda _: cam_lookup_msb_map[_] & cam_lookup_entry_lsb_w_map[_],
                range(self.p.num_entries)))
        cam_lookup_msb_entry_lsb_h_map = cat_rvs(
            map(lambda _: cam_lookup_msb_map[_] & cam_lookup_entry_lsb_h_map[_],
                range(self.p.num_entries)))
        cam_lookup_msb_entry_lsb_w_any = cam_lookup_msb_entry_lsb_w_map.r_or()
        cam_lookup_msb_entry_lsb_h_any = cam_lookup_msb_entry_lsb_h_map.r_or()

        cam_sel_msb_entry_lsb_w_rvc = sel_oh(
            cam_lookup_msb_entry_lsb_w_map,
            map(lambda _: _.rvc, list(cam_entries)))
        cam_sel_msb_entry_lsb_h_rvc = sel_oh(
            cam_lookup_msb_entry_lsb_h_map,
            map(lambda _: _.rvc, list(cam_entries)))

        cam_sel_msb_entry_lsb_w_half = sel_oh(
            cam_lookup_msb_entry_lsb_w_map,
            map(lambda _: _.rvi_half, list(cam_entries)))

        cam_sel_msb_entry_lsb_w_cfi_type = sel_oh(
            cam_lookup_msb_entry_lsb_w_map,
            map(lambda _: _.cfi_type, list(cam_entries)))
        cam_sel_msb_entry_lsb_h_cfi_type = sel_oh(
            cam_lookup_msb_entry_lsb_h_map,
            map(lambda _: _.cfi_type, list(cam_entries)))

        cam_sel_msb_entry_lsb_w_taken = sel_oh(
            cam_lookup_msb_entry_lsb_w_map,
            map(lambda _: _.taken, list(cam_entries)))
        cam_sel_msb_entry_lsb_h_taken = sel_oh(
            cam_lookup_msb_entry_lsb_h_map,
            map(lambda _: _.taken, list(cam_entries)))

        bht_sel_msb_entry_lsb_w_taken = mux(
            ~self.io.lookup_req.bits.bht_info.taken(),
            0,
            cam_sel_msb_entry_lsb_w_taken)
        bht_sel_msb_entry_lsb_h_taken = mux(
            ~self.io.lookup_req.bits.bht_info.taken(),
            0,
            cam_sel_msb_entry_lsb_h_taken)

        cam_sel_msb_entry_lsb_w_last_taken = (
            (cam_sel_msb_entry_lsb_w_cfi_type != CFI_CONSTS.branch()) |
            (bht_sel_msb_entry_lsb_w_taken 
                if (self.p.use_bht) else cam_sel_msb_entry_lsb_w_taken))
        cam_sel_msb_entry_lsb_h_last_taken = (
            (cam_sel_msb_entry_lsb_h_cfi_type != CFI_CONSTS.branch()) |
            (bht_sel_msb_entry_lsb_h_taken
                if (self.p.use_bht) else cam_sel_msb_entry_lsb_h_taken))


        pre_cond_msb_entry_lsb_w_rvc = (
            (cam_lookup_msb_entry_lsb_w_any & cam_sel_msb_entry_lsb_w_rvc) 
                if (self.p.isa_c) else 0)
        pre_cond_msb_entry_lsb_w_rvi = (
            cam_lookup_msb_entry_lsb_w_any &
            ~cam_sel_msb_entry_lsb_w_rvc)
        pre_cond_msb_entry_lsb_h_rvc = (
            (cam_lookup_msb_entry_lsb_h_any & cam_sel_msb_entry_lsb_h_rvc) 
                if (self.p.isa_c) else 0)
        pre_cond_msb_entry_lsb_h_rvi = (
            (cam_lookup_msb_entry_lsb_h_any & ~cam_sel_msb_entry_lsb_h_rvc)
                if (self.p.isa_c) else 0)

        pre_cond_msb_entry_lsb_w_rvc_last_taken = (
            pre_cond_msb_entry_lsb_w_rvc & 
            cam_sel_msb_entry_lsb_w_last_taken)
        pre_cond_msb_entry_lsb_w_rvi_last_taken = (
            pre_cond_msb_entry_lsb_w_rvi &
            cam_sel_msb_entry_lsb_w_last_taken)
        pre_cond_msb_entry_lsb_h_rvc_last_taken = (
            pre_cond_msb_entry_lsb_h_rvc & 
            cam_sel_msb_entry_lsb_h_last_taken)
        pre_cond_msb_entry_lsb_h_rvi_last_taken = (
            pre_cond_msb_entry_lsb_h_rvi & 
            cam_sel_msb_entry_lsb_h_last_taken)

        #this condition should not happen
        vassert(
            ~(self.io.lookup_req.valid & pre_cond_msb_entry_lsb_h_rvi_last_taken),
            name = 'pre_cond_msb_entry_lsb_h_rvi_last_taken')


        ####
        #cam lookup response
        self.io.lookup_resp.valid /= self.io.lookup_req.valid
        cam_iv = bits(w = 2, init = 0b11)
        cam_taken = bits(w = 2, init = 0)
        cam_hit = bits(w = 2, init = 0)
        with when(~self.io.lookup_req.bits.pc[1] | ~self.io.lookup_req.bits.redirect):
            cam_iv[0] /= 1
            cam_hit[0] /= pre_cond_msb_entry_lsb_w_rvc | pre_cond_msb_entry_lsb_w_rvi
            cam_taken[0] /= (
                pre_cond_msb_entry_lsb_w_rvc_last_taken |
                pre_cond_msb_entry_lsb_w_rvi_last_taken)
            if (self.p.isa_c):
                with when(
                    pre_cond_msb_entry_lsb_w_rvc_last_taken |
                    (pre_cond_msb_entry_lsb_w_rvi_last_taken & 
                        cam_sel_msb_entry_lsb_w_half)):
                    cam_iv[1] /= 0
        if (self.p.isa_c):
            cam_hit[1] /= pre_cond_msb_entry_lsb_h_rvc
            cam_taken[1] /= pre_cond_msb_entry_lsb_h_rvc_last_taken
            tgt_entry_sel_map = mux(
                cam_taken[0],
                cam_lookup_msb_entry_lsb_w_map,
                cam_lookup_msb_entry_lsb_h_map)
        else:
            tgt_entry_sel_map = cam_lookup_msb_entry_lsb_w_map
        tgt_entry_sel = sel_oh(tgt_entry_sel_map, list(tgt_entries))

        self.io.lookup_resp.bits.tgt /= tgt_entry_sel.tgt
        self.io.lookup_resp.bits.hit /= cam_hit
        self.io.lookup_resp.bits.taken /= cam_taken
        self.io.lookup_resp.bits.iv /= cam_iv


        ####
        #entry lru update
        with when(self.io.btb_update.valid):
            replace.access(cam_update_addr)
        with elsewhen(self.io.lookup_resp.valid):
            for i in range(self.io.lookup_resp.bits.taken.get_w()):
                with when(
                    self.io.lookup_resp.bits.taken[i] & 
                    self.io.lookup_resp.bits.iv[i]):
                    replace.access(oh2bin(tgt_entry_sel_map))


        #coverge
        vcover(
            self.io.lookup_req.valid & pre_cond_msb_entry_lsb_w_rvc_last_taken,
            name = 'pre_cond_msb_entry_lsb_w_rvc_last_taken')
        vcover(
            self.io.lookup_req.valid & pre_cond_msb_entry_lsb_w_rvi_last_taken,
            name = 'pre_cond_msb_entry_lsb_w_rvi_last_taken')
        vcover(
            self.io.lookup_req.valid & pre_cond_msb_entry_lsb_h_rvc_last_taken,
            name = 'pre_cond_msb_entry_lsb_h_rvc_last_taken')
