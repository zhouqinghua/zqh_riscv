import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_xbar_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_int_xbar_parameter
from zqh_common.zqh_address_space import zqh_address_space
from zqh_common.zqh_address_space import zqh_address_attr
from zqh_common.zqh_address_space import zqh_order_type
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_devices.zqh_debug.zqh_debug_bundles import DebugCtrlBundle
from zqh_devices.zqh_debug.zqh_debug_main import zqh_debug_module
from zqh_devices.zqh_clint.zqh_clint_main import zqh_clint
from zqh_devices.zqh_dma.zqh_dma_main import zqh_dma
from zqh_devices.zqh_plic.zqh_plic_main import zqh_plic
from zqh_devices.zqh_bootrom.zqh_bootrom_main import zqh_bootrom
from zqh_tile_common.zqh_tile_common_parameters import zqh_tile_common_parameter
from zqh_common.zqh_transfer_size import zqh_transfer_size
from zqh_tilelink.zqh_tilelink_memory_access_pos_main import zqh_tilelink_memory_access_pos
from zqh_tilelink.zqh_tilelink_atomic_transform_main import zqh_tilelink_atomic_transform
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_slave_io_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_master_io_parameter
from zqh_amba.zqh_tilelink_2_axi4_main import zqh_tilelink_2_axi4
from zqh_amba.zqh_axi4_2_tilelink_main import zqh_axi4_2_tilelink
from zqh_tilelink.zqh_tilelink_order_fix_main import zqh_tilelink_order_fix
from zqh_devices.zqh_debug.zqh_debug_bundles import ClockedDMIIO

class zqh_tile_common(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_tile_common, self).set_par()
        self.p = zqh_tile_common_parameter()

    def gen_node_tree(self):
        super(zqh_tile_common, self).gen_node_tree()
        self.p.par('core_master',
            list(map(
                lambda _: self.p.par('core_master_'+str(_),
                    zqh_tilelink_node_master_parameter(
                        'core_master_'+str(_),
                        process = [[zqh_tilelink_order_fix, self.p.tl_order_fix]])),
                range(self.p.num_cores))))
        self.p.par('dma_master', zqh_tilelink_node_master_parameter('dma_master'))
        self.p.par('debug_sb_master', zqh_tilelink_node_master_parameter('debug_sb_master'))
                
        if (self.p.sys_bus_axi4):
            self.p.par('fbus_extern_slave',
                zqh_axi4_node_master_io_parameter(
                    'fbus_extern_slave',
                    bundle_out = [self.p.gen_fbus_axi4_io_Params()]))
        else:
            self.p.par('fbus_extern_slave',
                zqh_tilelink_node_master_io_parameter(
                    'fbus_extern_slave',
                    bundle_out = [self.p.gen_fbus_tl_bundle_p()]))
        self.p.par('fbus_master',
            zqh_tilelink_node_master_parameter(
                'fbus_master',
                bundle_out = [self.p.gen_fbus_tl_bundle_p()],
                source_id_num = self.p.fbus.source_id_num,
                process = [
                    [
                        zqh_axi4_2_tilelink, 
                        self.p.fbus_axi4_2_tilelink]] if (self.p.sys_bus_axi4) else None))

        self.p.par('sbus', zqh_tilelink_node_xbar_parameter('sbus', do_imp = 1))

        self.p.par('mem_agent',
            zqh_tilelink_node_slave_parameter(
                'mem_agent',
                buffer_in = self.p.bh_buf_params if (self.p.node_has_buffer) else None,
                process = [
                    [
                        zqh_tilelink_atomic_transform,
                        self.p.tl_atomic] if (
                            self.p.support_atomic and 
                            self.p.mem_agent_do_atomic) else None],
                new_a_source_bits = (
                    1 if (
                        self.p.support_atomic and 
                        self.p.mem_agent_do_atomic) else 0) + 
                    log2_up(self.p.mem_pos.num_trackers)))
        self.p.par('core_bus', zqh_tilelink_node_xbar_parameter('core_bus'))
        self.p.par('core_ctrl_bus',
            zqh_tilelink_node_xbar_parameter('core_ctrl_bus',
                buffer_in = self.p.buf_params if (self.p.node_has_buffer) else None,
                down_bus_data_bits = 32))
        self.p.par('core_slave_bus', zqh_tilelink_node_xbar_parameter('core_slave_bus'))
        self.p.par('mbus', zqh_tilelink_node_xbar_parameter('mbus'))
        self.p.par('mmio_agent',
            zqh_tilelink_node_slave_parameter(
                'mmio_agent',
                buffer_in = self.p.buf_params if (self.p.node_has_buffer) else None,
                process = [[
                    zqh_tilelink_atomic_transform,
                    self.p.tl_atomic]] if (self.p.support_atomic) else None,
                new_a_source_bits = 1 if (self.p.support_atomic) else 0))

        #address mapping from FE310-G000.pdf
        self.p.par('core_dev_agent'   , zqh_tilelink_node_slave_parameter(
            'core_dev_agent',
            address = [
                zqh_address_space(
                    base = 0x00000000, 
                    mask = 0x0fffffff, 
                    attr = zqh_address_attr.DEV_RWAX,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 8),
            buffer_in = self.p.buf_params if (self.p.node_has_buffer) else None,
            process = [[
                zqh_tilelink_atomic_transform,
                self.p.tl_atomic]] if (self.p.support_atomic) else None,
            new_a_source_bits = 1 if (self.p.support_atomic) else 0))
        self.p.par('debug'   , zqh_tilelink_node_slave_parameter(
            'debug',
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x00000000, 
                    mask = 0x00000fff, 
                    attr = zqh_address_attr.DEV_RWAX,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('bootrom' , zqh_tilelink_node_slave_parameter(
            'bootrom', 
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x00010000,
                    mask = 0x0000ffff,
                    attr = zqh_address_attr.DEV_RWAX,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('core_inter'   , zqh_tilelink_node_slave_parameter(
            'core_inter',
            address = [
                zqh_address_space(
                    base = 0x01000000, 
                    mask = 0x00ffffff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 8)))
        self.p.par('clint'   , zqh_tilelink_node_slave_parameter(
            'clint',
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x02000000, 
                    mask = 0x0000ffff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('dma_slave'   , zqh_tilelink_node_slave_parameter(
            'dma_slave',
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x03000000, 
                    mask = 0x000fffff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('plic'    , zqh_tilelink_node_slave_parameter(
            'plic', 
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x0c000000, 
                    mask = 0x03ffffff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_devices'    , zqh_tilelink_node_slave_parameter(
            'mmio_devices', 
            address = [
                zqh_address_space( #Off-Core complex I/O
                    base = 0x10000000, 
                    mask = 0x0fffffff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 8),
            process = [[
                zqh_tilelink_2_axi4,
                self.p.mmio_tl2axi4]] if (self.p.sys_bus_axi4) else None))
        self.p.par('mem'     , zqh_tilelink_node_slave_parameter(
            'mem', 
            is_pos = 1,
            address = [
                zqh_address_space(#spi flash xip access
                    base = 0x20000000, 
                    mask = 0x1fffffff, 
                    attr = zqh_address_attr.MEM_RX_C_US,
                    order_type = zqh_order_type.RO),
                zqh_address_space(#on chip sram
                    base = 0x40000000, 
                    mask = 0x1fffffff, 
                    attr = zqh_address_attr.MEM_RWAX_C_S,
                    order_type = zqh_order_type.RO),
                zqh_address_space(#ddr memory
                    base = 0x80000000, 
                    mask = 0x7fffffff, 
                    attr = zqh_address_attr.MEM_RWAX_C_S,
                    order_type = zqh_order_type.RO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 64),
            process = [[
                zqh_tilelink_2_axi4,
                self.p.mem_tl2axi4]] if (self.p.sys_bus_axi4) else None))

        self.p.par('core_slave',  list(map(
            lambda _: self.p.par('core_slave_'+str(_),
                zqh_tilelink_node_slave_parameter(
                    'core_slave_'+str(_),
                    address = [
                        zqh_address_space(
                            base = 0x01000000 + 0x00400000 * _,
                            mask = 0x003fffff, 
                            attr = zqh_address_attr.DEV_RWAX,
                            order_type = zqh_order_type.SO)],
                    transfer_sizes = zqh_transfer_size(min = 0,max = 8))),
            range(self.p.num_cores))))

        self.p.par('error'   , zqh_tilelink_node_slave_parameter(
            'error', 
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0xe0000000, 
                    mask = 0x1fffffff, 
                    attr = zqh_address_attr.DEV_RWAX,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 64)))

        #extern master port
        if (self.p.sys_bus_axi4):
            self.p.par('mmio_extern_master' , zqh_axi4_node_slave_io_parameter(
                'mmio_extern_master'))
            self.p.par('mem_extern_master'  , zqh_axi4_node_slave_io_parameter(
                'mem_extern_master'))
        else:
            self.p.par('mmio_extern_master' , zqh_tilelink_node_slave_io_parameter(
                'mmio_extern_master'))
            self.p.par('mem_extern_master'  , zqh_tilelink_node_slave_io_parameter(
                'mem_extern_master'))

        #gen tree
        self.p.mbus.push_down(self.p.mem)
        self.p.mem.push_down(self.p.mem_extern_master)
        if (len(self.p.extern_masters) > 0):
            self.p.mem_extern_master.push_down(self.p.extern_masters[0])
            self.p.mmio_extern_master.push_down(self.p.extern_masters[1])

        self.p.mem_agent.push_down(self.p.mbus)
        self.p.sbus.push_down(self.p.mem_agent)

        self.p.core_ctrl_bus.push_down(self.p.debug)
        self.p.core_ctrl_bus.push_down(self.p.bootrom)
        self.p.core_ctrl_bus.push_down(self.p.clint)
        self.p.core_ctrl_bus.push_down(self.p.dma_slave)
        self.p.core_ctrl_bus.push_down(self.p.plic)
        self.p.sbus.push_down(self.p.core_dev_agent)
        self.p.core_bus.push_up(self.p.core_dev_agent)
        self.p.core_bus.push_down(self.p.core_ctrl_bus)
        self.p.core_bus.push_down(self.p.core_inter)

        self.p.core_slave_bus.push_up(self.p.core_inter)
        for i in range(self.p.num_cores):
            self.p.core_slave_bus.push_down(self.p.core_slave[i])

        self.p.sbus.push_down(self.p.mmio_agent)

        self.p.mmio_agent.push_down(self.p.mmio_devices)

        self.p.mmio_devices.push_down(self.p.mmio_extern_master)

        self.p.sbus.push_down(self.p.error)
        
        self.p.sbus.push_up(self.p.fbus_master)

        if (len(self.p.extern_slaves) > 0):
            self.p.fbus_extern_slave.push_up(self.p.extern_slaves[0])
        self.p.fbus_master.push_up(self.p.fbus_extern_slave)
        for i in range(self.p.num_cores):
            self.p.sbus.push_up(self.p.core_master[i])

        self.p.sbus.push_up(self.p.dma_master)
        self.p.sbus.push_up(self.p.debug_sb_master)

        #interrupt xbar
        self.p.par('int_xbar', zqh_tilelink_int_xbar_parameter('int_xbar'))
        self.p.int_xbar.push_down(self.p.dma_slave)
        self.p.int_xbar.push_up(self.p.plic)
        self.p.int_xbar.int_wire.append(([0], None))#int id 0 is always disabled

    def set_port(self):
        super(zqh_tile_common, self).set_port()
        self.io.var(ClockedDMIIO('dmi').flip())
        self.io.var(inp('boot_mode', w = 2))
        self.io.var(inp('clock_rtc'))

    def main(self):
        super(zqh_tile_common, self).main()

        #macro define for testbench
        vmacro('CORE_NUM', self.p.num_cores)
        for i in range(self.p.num_cores):
            vmacro('CORE%d_EN' % i)

        dma = zqh_dma('dma',
            extern_masters = [self.p.dma_master],
            extern_slaves = [self.p.dma_slave])

        core_wraps = self.instance_core_wraps()
        for i in range(self.p.num_cores):
            core_wraps[i].io.constants.hartid /= i
            core_wraps[i].io.constants.reset_pc /= sel_map(
                self.io.boot_mode,
                [
                    (0, self.p.bootrom.address[0].base + 0x00), #flash xip
                    (1, self.p.bootrom.address[0].base + 0x10), #on chip sram
                    (2, self.p.bootrom.address[0].base + 0x20), #DDR
                    (3, self.p.bootrom.address[0].base + 0x60), #debug space
                ],
                self.p.bootrom.address[0].base)
            core_wraps[i].io.interrupts /= 0 #initial value give 0, then overwrite

        debug = zqh_debug_module(
            'debug',
            extern_masters = [self.p.debug_sb_master],
            extern_slaves = [self.p.debug])
        debug.io.ctrl.debugUnavail /= 0
        debug.io.dmi /= self.io.dmi
        for i in range(self.p.num_cores):
            core_wraps[i].io.interrupts.debug /= debug.io.int_source[i]
        self.io.var(DebugCtrlBundle('debug', nComponents = debug.p.nComponents))
        self.io.debug /= debug.io.ctrl

        bootrom = zqh_bootrom(
            'bootrom',
            extern_slaves = [self.p.bootrom])

        clint = zqh_clint(
            'clint',
            num_cores = self.p.num_cores,
            extern_slaves = [self.p.clint])
        clint.io.clock_rtc /= self.io.clock_rtc

        for i in range(self.p.num_cores):
            core_wraps[i].io.interrupts.msip /= clint.io.int_source[i*2]
            core_wraps[i].io.interrupts.mtip /= clint.io.int_source[i*2+1]

        plic = zqh_plic(
            'plic',
            num_cores = self.p.num_cores,
            use_vms = list(map(
                lambda _: core_wraps[_].io.interrupts.p.use_vm,
                range(self.p.num_cores))),
            num_devices = self.p.num_plic_ints - 1,
            extern_slaves = [self.p.plic])
        for i in range(self.p.num_cores):
            core_wraps[i].io.interrupts.meip /= plic.io.int_source[i]


    #should be overwritten by child class
    def instance_core_wraps(self):
        pass
