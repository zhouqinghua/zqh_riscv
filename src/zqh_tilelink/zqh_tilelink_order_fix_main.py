import sys
import os
from phgl_imp import *
from .zqh_tilelink_interfaces import zqh_tl_interface_in
from .zqh_tilelink_interfaces import zqh_tl_interface_out
from .zqh_tilelink_bundles import zqh_tl_bundle
from zqh_common.zqh_address_space import zqh_order_type

class zqh_tilelink_order_fix_module(module):
    def set_par(self):
        super(zqh_tilelink_order_fix_module, self).set_par()
        self.p.par('tl_order', None)
        self.p.par('bundle_in', None)
        self.p.par('node', None)

    def set_port(self):
        super(zqh_tilelink_order_fix_module, self).set_port()
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        self.io.var(zqh_tl_bundle('tl_out', p = self.p.bundle_in))

    def main(self):
        super(zqh_tilelink_order_fix_module, self).main()

        #slaves = self.p.node.get_nearest_slave_nodes()
        slaves = self.p.node.get_farest_slave_nodes()
        #tmp for i in slaves:
        #tmp     print(i.name)
        #tmp     print(len(i.address))
        #tmp     if (i.name in ('flush_slave', 'mem_slave', 'ifu_slave')):
        #tmp         print('ralative space:')
        #tmp         for j in i.address:
        #tmp             print(j.print_info())
        #tmp         print('global space:')
        #tmp         for j in i.get_global_address_space():
        #tmp             print(j.print_info())
        slave_addresses = []
        for i in range(len(slaves)):
            #tmp slave_addresses.extend(slaves[i].address)
            slave_addresses.extend(slaves[i].get_global_address_space())
        masters = self.p.node.get_root_masters()
        source_id_bases = list(map(
            lambda _: _.master2slave_source_base(self.p.node), masters))
        source_ids = []
        for i in range(len(source_id_bases)):
            for j in range(masters[i].source_id_num):
                source_ids.append(source_id_bases[i] + j)

        if (self.p.tl_order.order_mode == 'none'):
            do_stall = self.order_none_stall_check()
        elif (self.p.tl_order.order_mode == 'pos'):
            do_stall = self.order_pos_stall_check(slave_addresses, source_ids)
        elif (self.p.tl_order.order_mode == 'mem'):
            do_stall = self.order_mem_stall_check(slave_addresses, source_ids)
        elif (self.p.tl_order.order_mode == 'self'):
            do_stall = self.order_self_stall_check()
        elif (self.p.tl_order.order_mode == 'all'):
            do_stall = self.order_all_stall_check()
        else:
            assert(0), 'illegal order_mode %s' % (self.p.tl_order.order_mode)

        self.io.tl_in.a.ready /= self.io.tl_out.a.ready & ~do_stall
        self.io.tl_out.a.valid /= self.io.tl_in.a.valid & ~do_stall
        self.io.tl_out.a.bits /= self.io.tl_in.a.bits
        self.io.tl_in.d /= self.io.tl_out.d
        
        if (self.p.bundle_in.tl_type == 'tl_c'):
            self.io.tl_out.c /= self.io.tl_in.c
            self.io.tl_out.e /= self.io.tl_in.e
            self.io.tl_in.b /= self.io.tl_out.b

    def order_none_stall_check(self):
        return value(0).to_bits()

    def order_pos_stall_check(self, slave_addresses, source_ids):
        tl_in_a_source_match_oh = list(map(
            lambda _: self.io.tl_in.a.bits.source == _, source_ids))
        tl_out_d_source_match_oh = list(map(
            lambda _: self.io.tl_out.d.bits.source == _, source_ids))
        so_flags = vec('so_flags', gen = reg_r, n = len(source_ids))
        so_order_id = reg('so_order_id', w = log2_up(len(slave_addresses)))
        so_matches = list(map(
            lambda _: (
                _.contains(self.io.tl_in.a.bits.address) & 
                (_.order_type == zqh_order_type.SO)),
            slave_addresses))
        so_matches_bin = oh2bin(cat_rvs(so_matches))
        so_match_any = reduce(lambda x,y: x | y, so_matches)

        tl_out_d_sop_eop = self.io.tl_out.sop_eop_d()
        with when(tl_out_d_sop_eop.eop):
            for i in range(len(tl_out_d_source_match_oh)):
                with when(tl_out_d_source_match_oh[i]):
                    so_flags[i] /= 0

        tl_in_a_sop_eop = self.io.tl_in.sop_eop_a()
        with when(tl_in_a_sop_eop.eop):
            with when(so_match_any):
                so_order_id /= so_matches_bin
                for i in range(len(tl_in_a_source_match_oh)):
                    with when(tl_in_a_source_match_oh[i]):
                        so_flags[i] /= 1 #set(A) has higher priority than clear(D)


        has_so_penging = reduce(lambda x,y: x | y, so_flags)
        do_stall = bits('do_stall', init = 0)
        with when(so_match_any & has_so_penging):
            with when(so_matches_bin != so_order_id):
                do_stall /= 1

        return do_stall
    
    def order_mem_stall_check(self, slave_addresses, source_ids):
        tl_in_a_source_match_oh = list(map(
            lambda _: self.io.tl_in.a.bits.source == _, source_ids))
        tl_out_d_source_match_oh = list(map(
            lambda _: self.io.tl_out.d.bits.source == _, source_ids))
        so_flags = vec('so_flags', gen = reg_r, n = len(source_ids))
        so_matches = list(map(
            lambda _: (
                _.contains(self.io.tl_in.a.bits.address) & 
                (_.order_type == zqh_order_type.SO)),
            slave_addresses))
        so_match_any = reduce(lambda x,y: x | y, so_matches)

        tl_out_d_sop_eop = self.io.tl_out.sop_eop_d()
        with when(tl_out_d_sop_eop.eop):
            for i in range(len(tl_out_d_source_match_oh)):
                with when(tl_out_d_source_match_oh[i]):
                    so_flags[i] /= 0

        tl_in_a_sop_eop = self.io.tl_in.sop_eop_a()
        with when(tl_in_a_sop_eop.eop):
            with when(so_match_any):
                for i in range(len(tl_in_a_source_match_oh)):
                    with when(tl_in_a_source_match_oh[i]):
                        so_flags[i] /= 1 #set(A) has higher priority than clear(D)


        has_so_penging = reduce(lambda x,y: x | y, so_flags)
        do_stall = bits('do_stall', init = 0)
        with when(so_match_any & has_so_penging):
            do_stall /= 1

        return do_stall

    def order_self_stall_check(self):
        assert(0), "self mode don't support yet"

    def order_all_stall_check(self):
        so_flags = reg_r('so_flags')

        tl_out_d_sop_eop = self.io.tl_out.sop_eop_d()
        with when(tl_out_d_sop_eop.eop):
            so_flags /= 0

        tl_in_a_sop_eop = self.io.tl_in.sop_eop_a()
        with when(tl_in_a_sop_eop.eop):
            so_flags /= 1 #set(A) has higher priority than clear(D)

        do_stall = bits('do_stall', init = so_flags)
        return do_stall

def zqh_tilelink_order_fix(node, tl_in, p):
    tl_order_fix = zqh_tilelink_order_fix_module(
        'tl_order_fix',
        tl_order = p,
        bundle_in = tl_in.p,
        node = node)
    tl_order_fix.io.tl_in /= tl_in
    return tl_order_fix.io.tl_out
