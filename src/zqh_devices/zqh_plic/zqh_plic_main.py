import sys
import os
from phgl_imp import *
from .zqh_plic_misc import zqh_plic_consts
from .zqh_plic_parameters import zqh_plic_parameter
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module

class zqh_plic(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_plic, self).set_par()
        self.p = zqh_plic_parameter()

    def gen_node_tree(self):
        super(zqh_plic, self).gen_node_tree()
        self.gen_node_slave(
            'plic_slave', 
            tl_type = 'tl_uh', 
            bundle_p = self.p.gen_tl_bundle_p())
        self.p.plic_slave.print_up()
        self.p.plic_slave.print_address_space()

    def set_port(self):
        super(zqh_plic, self).set_port()

    def main(self):
        super(zqh_plic, self).main()
        self.gen_node_interface('plic_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        self.int_vec = vec('int_vec', gen = bits, n = self.p.num_devices + 1)
        self.int_vec /= 0

        #define config regs
        #priority
        priority = list(map(
            lambda _: self.cfg_reg(csr_reg_group(
                'priority_'+str(_), 
                offset = zqh_plic_consts.priorityBase + _ * zqh_plic_consts.priorityBytes, 
                size = zqh_plic_consts.priorityBytes, 
                fields_desc = [
                    csr_reg_field_desc('priority', width = self.p.priority_bits(), reset = 0, comments = '''\
0: never interrupt.
1-7: low to high priority.''')])),
            range(self.p.num_devices + 1)))

        #pending
        pending = list(map(
            lambda _: self.cfg_reg(csr_reg_group(
                'pending_'+str(_), 
                offset = zqh_plic_consts.pendingBase + _*4, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('pending', access = 'RO', width = 32, reset = 0, comments = '''\
each interrupt iD\'s pending flag.''')])),
            range((self.p.num_devices + 1 + 31)//32)))

        #enable
        enable_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) 
                    else list(map(
                        lambda _: self.cfg_reg(csr_reg_group(
                            'enable_ms_'+str(hi)+'_'+str(si)+'_'+str(_), 
                            offset = zqh_plic_consts.enableBase(hi*2+si) + _*4, 
                            size = 4, 
                            fields_desc = [
                                csr_reg_field_desc('enable', width = 32, reset = 0, comments = '''\
each interrupt source's enable.''')])),
                        range((self.p.num_devices + 1 + 31)//32))),
                range(2))),
            range(self.p.num_cores)))


        #threshold
        threshold_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) 
                    else self.cfg_reg(csr_reg_group(
                        'threshold_ms_'+str(hi)+'_'+str(si), 
                        offset = zqh_plic_consts.hartBase(hi*2+si), 
                        size = 4, 
                        fields_desc = [
                            csr_reg_field_desc('threshold', width = self.p.priority_bits(), reset = 0, comments = '''\
each core's interrupt priority threshold:
priority <= threshold will be masked.''')])),
                range(2))),
            range(self.p.num_cores)))

        #claim_complete
        bus_claiming_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    bits('bus_claiming_ms_'+str(hi)+'_'+str(si), init = 0),
                range(2))),
            range(self.p.num_cores)))
        def func_claim(reg_ptr, fire, address, size, mask_bit,
            hart_id = None, si_id = None):
            with when(fire):
                bus_claiming_ms[hart_id][si_id] /= 1
            return (1, 1, reg_ptr)
        def rd_process_gen(hart_id, si_id):
            return lambda a0, a1, a2, a3, a4: func_claim(
                a0, a1, a2, a3, a4,
                hart_id, si_id)

        bus_completing_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    bits('bus_completing_ms_'+str(hi)+'_'+str(si), init = 0),
                range(2))),
            range(self.p.num_cores)))
        bus_completing_id_1hot_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    bits(
                        'bus_completing_id_1hot_ms_'+str(hi)+'_'+str(si), 
                        w = self.p.num_devices + 1),
                range(2))),
            range(self.p.num_cores)))
        def func_complete(reg_ptr, fire, address, size, wdata, mask_bit,
            hart_id = None, si_id = None):
            with when(fire):
                bus_completing_ms[hart_id][si_id] /= 1
                bus_completing_id_1hot_ms[hart_id][si_id] /= bin2oh(
                    wdata & mask_bit, 
                    w = self.p.num_devices + 1)
            return (1, 1)
        def wr_process_gen(hart_id, si_id):
            return lambda a0, a1, a2, a3, a4, a5: func_complete(
                a0, a1, a2, a3, a4, a5,
                hart_id, si_id)

        claim_complete_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    self.cfg_reg(csr_reg_group(
                        'claim_complete_ms_'+str(hi)+'_'+str(si), 
                        offset = zqh_plic_consts.hartBase(hi*2+si) + 4, 
                        size = 4, 
                        fields_desc = [
                            csr_reg_field_desc('claim_complete', width = 32, access = 'VOL', read = rd_process_gen(hi, si), write = wr_process_gen(hi, si), comments = '''\
read this reg is claim, none zero return value menas a valid interrupt.
write this reg is complete, write data is the completed interrupt ID.''')])),
                range(2))), 
            range(self.p.num_cores)))

        all_int_in = self.int_vec
        int_ready = list(map(
            lambda _: ~pending[_//32].pending[_%32], range(self.p.num_devices + 1)))
        in_flight = list(map(
            lambda _: reg_r('in_flight_'+str(_)), range(self.p.num_devices + 1)))
        int_valid = list(map(
            lambda _: all_int_in[_] & ~in_flight[_], range(self.p.num_devices + 1)))
        int_id_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    reg_r(
                        'int_id_ms_'+str(hi)+'_'+str(si), 
                        w = log2_ceil(self.p.num_devices + 1)),
                range(2))),
            range(self.p.num_cores)))
        int_id_1hot_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    bin2oh(int_id_ms[hi][si], w = self.p.num_devices + 1),
                range(2))),
            range(self.p.num_cores)))
        int_claim_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    mux(bus_claiming_ms[hi][si], int_id_1hot_ms[hi][si], 0),
                range(2))), 
            range(self.p.num_cores)))
        int_claim_all = reduce(
            lambda a,b: list(map(lambda _: a[_] | b[_], range(self.p.num_devices + 1))),
            list(filter(lambda _: _ is not None, flatten(int_claim_ms))))
        int_complete_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    mux(bus_completing_ms[hi][si], bus_completing_id_1hot_ms[hi][si], 0),
                range(2))),
            range(self.p.num_cores)))
        int_complete_all = reduce(
            lambda a,b: list(map(lambda _: a[_] | b[_], range(self.p.num_devices + 1))),
            list(filter(lambda _: _ is not None, flatten(int_complete_ms))))

        for hi in range(self.p.num_cores):
            for si in range(2):
                if (si == 1 and self.p.use_vms[hi] == 0):
                    pass
                else:
                    claim_complete_ms[hi][si].claim_complete /= int_id_ms[hi][si]

        for i in range(self.p.num_devices + 1):
            with when(all_int_in[i] & int_ready[i]):
                in_flight[i] /= 1
            with when(int_complete_all[i]):
                in_flight[i] /= 0

        #set pending
        pending_next = list(map(
            lambda _: vec(
                'pending_next', 
                gen = lambda bi: bits(bi, init = pending[_].pending[bi]),
                n = 32),
            range((self.p.num_devices + 1 + 31)//32)))
        for i in range(self.p.num_devices + 1):
            with when(int_valid[i] | int_claim_all[i]):
                pending_next[i//32][i%32] /= ~int_claim_all[i]
        for i in range(len(pending)):
            for j in range(pending[i].get_w()):
                pending[i].pending[j] /= pending_next[i][j]

        #select int
        int_valid_prio_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    list(map(
                        lambda pi: list(map(
                            lambda _: value(0).to_bits(), 
                            range(self.p.num_devices + 1))) if (pi == 0) else 
                                list(map(
                                    lambda _: (
                                        pending[_//32].pending[_%32] & 
                                        (priority[_].priority == pi) & 
                                        enable_ms[hi][si][_//32].enable[_%32]),
                                    range(self.p.num_devices + 1))),
                        range(self.p.num_priorities() + 1))),
                range(2))),
            range(self.p.num_cores)))
        has_int_each_prio_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    list(map(
                        lambda pi: reduce(
                            lambda a, b: a | b,
                            int_valid_prio_ms[hi][si][pi]),
                        range(self.p.num_priorities() + 1))), 
                range(2))),
            range(self.p.num_cores)))
        has_int_each_prio_th_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    list(map(
                        lambda pi: (
                            has_int_each_prio_ms[hi][si][pi] & 
                            (pi > threshold_ms[hi][si].threshold)),
                        range(self.p.num_priorities() + 1))),
                range(2))),
            range(self.p.num_cores)))
        int_enc_bin_ms = list(map(
            lambda hi: list(map(
                lambda si: None if (si == 1 and self.p.use_vms[hi] == 0) else 
                    list(map(
                        lambda _: pri_lsb_enc(cat_rvs(_)), 
                        int_valid_prio_ms[hi][si])),
                range(2))),
            range(self.p.num_cores)))
        for hi in range(self.p.num_cores):
            for si in range(2):
                if (si == 1 and self.p.use_vms[hi] == 0):
                    pass
                else:
                    int_id_ms[hi][si] /= sel_p_msb(
                        has_int_each_prio_ms[hi][si],
                        int_enc_bin_ms[hi][si])

        int_id = 0
        for hi in range(len(self.int_out[0])):
            for si in range(2 if (self.p.use_vms[hi]) else 1):
                self.int_out[0][int_id] /= cat(has_int_each_prio_th_ms[hi][si]).r_or()
                int_id = int_id + 1
