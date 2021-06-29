import sys
import os
import decimal
from phgl_imp import *
from .zqh_core_common_misc import CFI_CONSTS
from .zqh_core_common_btb_parameters import zqh_core_common_btb_parameter
from .zqh_core_common_btb_parameters import zqh_core_common_bht_parameter
from .zqh_core_common_btb_parameters import zqh_core_common_ras_parameter

class zqh_core_common_btb_update(bundle):
    def set_par(self):
        super(zqh_core_common_btb_update, self).set_par()
        self.p = zqh_core_common_btb_parameter()

    def set_var(self):
        super(zqh_core_common_btb_update,self).set_var()
        self.var(bits('pc', w = self.p.vaddr_bits))
        self.var(bits('rvc'))
        self.var(bits('rvi_half'))
        self.var(bits('tgt', w = self.p.vaddr_bits))
        self.var(bits('cfi_type', w = CFI_CONSTS.SZ))
        self.var(bits('taken'))

class zqh_core_common_btb_cam_entry(bundle):
    def set_par(self):
        super(zqh_core_common_btb_cam_entry, self).set_par()
        self.p = zqh_core_common_btb_parameter()

    def set_var(self):
        super(zqh_core_common_btb_cam_entry, self).set_var()
        self.var(bits('pc', w = self.p.vaddr_bits))
        self.var(bits('rvc'))
        self.var(bits('rvi_half')) #rvi instruction cross 4B boundary
        self.var(bits('cfi_type', w = CFI_CONSTS.SZ))
        self.var(bits('taken'))

class zqh_core_common_btb_tgt_entry(bundle):
    def set_par(self):
        super(zqh_core_common_btb_tgt_entry, self).set_par()
        self.p = zqh_core_common_btb_parameter()

    def set_var(self):
        super(zqh_core_common_btb_tgt_entry, self).set_var()
        self.var(bits('tgt', w = self.p.vaddr_bits))

class zqh_core_common_ras(bundle):
    def set_par(self):
        super(zqh_core_common_ras, self).set_par()
        self.p = zqh_core_common_ras_parameter()

    def set_var(self):
        super(zqh_core_common_ras, self).set_var()
        self.var(reg_r('cnt', w = log2_up(self.p.num_entries+1)))
        self.var(reg_r('ptr', w = log2_up(self.p.num_entries)))
        self.var(vec('mem', gen = reg, n = self.p.num_entries, w = self.p.vaddr_bits))

    def push(self, a):
        with when (self.cnt != self.p.num_entries):
            self.cnt /= self.cnt + 1 
        ptr_next = mux(self.ptr != self.p.num_entries-1, self.ptr+1, 0)
        self.mem(ptr_next, a)
        self.ptr /= ptr_next

    def pop(self):
        with when (~self.empty()):
            self.cnt /= self.cnt - 1
            self.ptr /= mux(self.ptr != 0, self.ptr-1, self.p.num_entries-1)

    def peek(self):
        return self.mem[self.ptr]

    def flush(self):
        self.cnt /= 0

    def empty(self): 
        return self.cnt == 0

class zqh_core_common_bht_resp(bundle):
    def set_par(self):
        super(zqh_core_common_bht_resp, self).set_par()
        self.p = zqh_core_common_bht_parameter()

    def set_var(self):
        super(zqh_core_common_bht_resp, self).set_var()
        self.var(bits('history', w = self.p.history_len))
        self.var(bits('cnt', w = self.p.cnt_len))

    def taken(self):
        return self.cnt.match_any(range((2**self.cnt.get_w())//2, 2**self.cnt.get_w()))

    def strongly_taken(self):
        return self.cnt == (2**self.cnt.get_w() - 1)


class zqh_core_common_bht(bundle):
    def set_par(self):
        super(zqh_core_common_bht, self).set_par()
        self.p = zqh_core_common_bht_parameter()

    def set_var(self):
        super(zqh_core_common_bht, self).set_var()
        self.var(vec(
            'cnt_table',
            gen = lambda _: reg_r(_, w = self.p.cnt_len),
            n = self.p.num_entries))
        self.var(reg_r('history_reg', w = self.p.history_len))

    def gen_table_idx(self, addr, history):
        def hashHistory(hist):
            if (self.p.history_len == self.p.history_hash_len):
                return hist 
            else:
                return crc(
                    0xf,
                    hist.order_invert(),
                    0x13,
                    4)[self.p.history_hash_len - 1 : 0]
        def hashAddr(addr):
            hi = addr >> 2
            return (
                hi[log2_ceil(self.p.num_entries)-1: 0] ^
                (hi >> log2_ceil(self.p.num_entries))[1: 0])
        return (
            hashAddr(addr) ^ 
            (hashHistory(history) << 
                (log2_up(self.p.num_entries) - self.p.history_hash_len)))

    def get_entry(self, addr):
        res = zqh_core_common_bht_resp()
        res.cnt /= self.cnt_table[self.gen_table_idx(addr, self.history_reg)]
        res.history /= self.history_reg
        return res

    def update_table(self, addr, bht_info, taken):
        self.cnt_table(
            self.gen_table_idx(addr, bht_info.history),
            self.cnt_change(bht_info.cnt, taken))

    def cnt_change(self, cnt, taken):
        if (cnt.get_w() == 1):
            return taken
        else:
            incr_v = mux(taken, 1, 2**cnt.get_w() - 1)
            cmp_v = mux(taken, 2**cnt.get_w() - 1, 0)
            return mux(cnt == cmp_v, cnt, cnt + incr_v)[cnt.get_w() - 1 : 0]

    def set_history(self, history):
        self.history_reg /= history

    def update_history(self, addr, history, taken):
        self.history_reg /= cat([taken, (history >> 1)])

    def raw_history(self, taken):
        self.history_reg /= cat([taken, (self.history_reg >> 1)])

class zqh_core_common_bht_update(bundle):
    def set_par(self):
        super(zqh_core_common_bht_update, self).set_par()
        self.p = zqh_core_common_bht_parameter()

    def set_var(self):
        super(zqh_core_common_bht_update, self).set_var()
        self.var(zqh_core_common_bht_resp('bht_info'))
        self.var(bits('pc', w = self.p.vaddr_bits))
        self.var(bits('branch'))
        self.var(bits('taken'))
        self.var(bits('mispredict'))

class zqh_core_common_btb_req(bundle):
    def set_par(self):
        super(zqh_core_common_btb_req, self).set_par()
        self.p = zqh_core_common_btb_parameter()

    def set_var(self):
        super(zqh_core_common_btb_req, self).set_var()
        self.var(bits('redirect'))
        self.var(bits('pc', w = self.p.vaddr_bits))
        self.var(zqh_core_common_bht_resp('bht_info'))

class zqh_core_common_btb_resp(bundle):
    def set_par(self):
        super(zqh_core_common_btb_resp, self).set_par()
        self.p = zqh_core_common_btb_parameter()

    def set_var(self):
        super(zqh_core_common_btb_resp,self).set_var()
        self.var(bits('cfi_type', w = CFI_CONSTS.SZ))
        self.var(bits('hit', w =  2 if (self.p.isa_c) else 1))
        self.var(bits('taken', w =  2 if (self.p.isa_c) else 1))
        self.var(bits('iv', w = 2 if (self.p.isa_c) else 1))
        self.var(bits('tgt', w = self.p.vaddr_bits))
