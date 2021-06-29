import sys
import os
from phgl_imp import *
from zqh_common.zqh_transfer_size import zqh_transfer_size
from zqh_core_common.zqh_core_common_misc import M_CONSTS
from .zqh_core_common_lsu_parameters import zqh_core_common_lsu_parameter
from .zqh_core_common_lsu_bundles import *
from .zqh_core_common_lsu_slave_mem import zqh_core_common_lsu_slave_mem
from .zqh_core_common_lsu_slave_flush import zqh_core_common_lsu_slave_flush
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_xbar_parameter
from zqh_common.zqh_address_space import zqh_address_space
from zqh_common.zqh_address_space import zqh_address_attr
from zqh_common.zqh_address_space import zqh_order_type

class zqh_core_common_lsu(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_common_lsu, self).set_par()
        self.p = zqh_core_common_lsu_parameter()

    def gen_node_tree(self):
        super(zqh_core_common_lsu, self).gen_node_tree()
        self.gen_node_master('lsu_master', bundle_p = self.p.gen_tl_bundle_p())
        self.p.par(
            'in_extern_slave',
            zqh_tilelink_node_master_io_parameter('in_extern_slave'))
        self.p.par('in_bus', zqh_tilelink_node_xbar_parameter('in_bus', do_imp = 1))

        self.p.par('mem_slave', zqh_tilelink_node_slave_parameter('mem_slave', 
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x00200000, 
                    mask = 0x000fffff, 
                    attr = zqh_address_attr.MEM_RWAX_UC,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 8)))
        self.p.par('flush_slave', zqh_tilelink_node_slave_parameter('flush_slave', 
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x00300000, 
                    mask = 0x000fffff, 
                    attr = zqh_address_attr.MEM_RWAX_UC,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 8)))

        if (len(self.p.extern_slaves) > 0):
            self.p.in_extern_slave.push_up(self.p.extern_slaves[0])
        self.p.in_bus.push_up(self.p.in_extern_slave)
        self.p.in_bus.push_down(self.p.mem_slave)
        self.p.in_bus.push_down(self.p.flush_slave)

    def set_port(self):
        super(zqh_core_common_lsu, self).set_port()
        self.io.var(zqh_core_common_lsu_mem_io('cpu'))
        self.io.var(zqh_core_common_lsu_errors_io('errors'))

    def main(self):
        super(zqh_core_common_lsu, self).main()
        mem_slave = zqh_core_common_lsu_slave_mem(
            'mem_slave',
            extern_slaves = [self.p.mem_slave])
        flush_slave = zqh_core_common_lsu_slave_flush(
            'flush_slave',
            extern_slaves = [self.p.flush_slave])
        (dcache_arb, dcache) = self.instance_dcache(mem_slave, flush_slave)

        dcache.io.cpu /= dcache_arb.io.out
        self.io.errors /= dcache.io.errors

    def instance_dcache(self, mem_slave, flush_slave):
        pass
