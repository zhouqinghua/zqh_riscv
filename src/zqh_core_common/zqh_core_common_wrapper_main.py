import sys
import os
from phgl_imp import *
from .zqh_core_common_wrapper_parameters import zqh_core_common_wrapper_parameter
from .zqh_core_common_interrupts_bundles import zqh_core_common_interrupts
from .zqh_core_common_wrapper_bundles import zqh_core_common_wrapper_driven_constants
from zqh_common.zqh_transfer_size import zqh_transfer_size
from .zqh_core_common_ifu_main import zqh_core_common_ifu
from zqh_fpu.zqh_fpu_stub import zqh_fpu_stub
from zqh_rocc.zqh_rocc_stub import zqh_rocc_stub
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_slave_io
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_xbar_parameter
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_common.zqh_address_space import zqh_address_space
from zqh_common.zqh_address_space import zqh_address_attr
from zqh_common.zqh_address_space import zqh_order_type
from zqh_tilelink.zqh_tilelink_dw_fix_main import zqh_tilelink_burst_split_fix

class zqh_core_common_wrapper(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_common_wrapper, self).set_par()
        self.p =  zqh_core_common_wrapper_parameter()

    def gen_node_tree(self):
        super(zqh_core_common_wrapper, self).gen_node_tree()
        self.p.par('lsu_master', zqh_tilelink_node_master_parameter('lsu_master'))
        self.p.par('ifu_master', zqh_tilelink_node_master_parameter('ifu_master'))

        #itim and dtim's internal access by core
        self.p.par(
            'core_inner_slave', 
            zqh_tilelink_node_slave_parameter(
                'core_inner_slave',
                is_pos = 1,
                address = [
                    zqh_address_space(
                        base = 0x60000000, 
                        mask = 0x003fffff,
                        attr = zqh_address_attr.MEM_RWAX_C_S,
                        order_type = zqh_order_type.RO)],
                transfer_sizes = zqh_transfer_size(min = 0,max = 64),
                address_mask = 0x003fffff,
                process = [[zqh_tilelink_burst_split_fix, None]]))

        self.p.par(
            'out_extern_master',
            zqh_tilelink_node_slave_io_parameter('out_extern_master'))
        self.p.par('out_bus', zqh_tilelink_node_xbar_parameter('out_bus',
            buffer_in = self.p.buf_params if (self.p.out_bus_has_buffer) else None,
            do_imp = 1))
        self.p.out_bus.push_up(self.p.lsu_master)
        self.p.out_bus.push_up(self.p.ifu_master)
        self.p.out_bus.push_down(self.p.out_extern_master)
        self.p.out_bus.push_down(self.p.core_inner_slave)
        if (len(self.p.extern_masters) > 0):
            self.p.out_extern_master.push_down(self.p.extern_masters[0])

        self.p.par(
            'in_extern_slave',
            zqh_tilelink_node_master_io_parameter(
                'in_extern_slave',
                address_mask = 0x003fffff))
        self.p.par(
            'ifu_slave', 
            zqh_tilelink_node_slave_parameter(
                'ifu_slave',
                is_pos = 1,
                address = [
                    zqh_address_space(
                        base = 0x00000000, 
                        mask = 0x001fffff, 
                        attr = zqh_address_attr.MEM_RWAX_UC,
                        order_type = zqh_order_type.SO)],
                transfer_sizes = zqh_transfer_size(min = 0,max = 8)))
        self.p.par(
            'lsu_slave', 
            zqh_tilelink_node_slave_parameter(
                'lsu_slave', 
                address = [
                    zqh_address_space(
                        base = 0x00200000, 
                        mask = 0x001fffff, 
                        attr = zqh_address_attr.MEM_RWAX_UC,
                        order_type = zqh_order_type.SO)],
                transfer_sizes = zqh_transfer_size(min = 0,max = 8)))
        if (len(self.p.extern_slaves) > 0):
            self.p.in_extern_slave.push_up(self.p.extern_slaves[0])
        self.p.par('in_bus', zqh_tilelink_node_xbar_parameter('in_bus', do_imp = 1))

        self.p.in_bus.push_up(self.p.in_extern_slave)
        self.p.in_bus.push_up(self.p.core_inner_slave)
        self.p.in_bus.push_down(self.p.ifu_slave)
        self.p.in_bus.push_down(self.p.lsu_slave)


    def set_port(self):
        super(zqh_core_common_wrapper, self).set_port()
        self.io.var(zqh_core_common_interrupts('interrupts').as_input())
        self.io.var(zqh_core_common_wrapper_driven_constants('constants'))

    def main(self):
        super(zqh_core_common_wrapper, self).main()
        core = self.instance_core()
        ifu = self.instance_ifu()
        lsu = self.instance_lsu()
        fpu = self.instance_fpu() if (core.p.isa_f) else zqh_fpu_stub('fpu')
        rocc = self.instance_rocc() if (core.p.isa_custom) else zqh_rocc_stub('rocc')

        ifu.io.cpu /= core.io.ifu
        ifu.io.reset_pc /= self.io.constants.reset_pc

        core.io.interrupts /= async_dff(self.io.interrupts, self.p.int_sync_delay)
        core.io.interrupts.debug /= async_dff(
            self.io.interrupts.debug,
            self.p.int_sync_delay)
        core.io.hartid /= self.io.constants.hartid
        core.io.reset_pc /= self.io.constants.reset_pc

        lsu.io.cpu /= core.io.lsu


        fpu.io.cp_req /= 0
        fpu.io.cp_resp.ready /= 0
        fpu.io /= core.io.fpu

        rocc.io /= core.io.rocc


    def instance_core(self):
        pass

    def instance_ifu(self):
        return zqh_core_common_ifu('ifu',
            extern_masters = [self.p.ifu_master],
            extern_slaves = [self.p.ifu_slave])

    def instance_lsu(self):
        pass
    
    def instance_fpu(self):
        pass

    def instance_rocc(self):
        pass
