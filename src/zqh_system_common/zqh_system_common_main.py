import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_xbar_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_int_xbar_parameter
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module

from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_slave_parameter
from zqh_amba.zqh_tilelink_2_axi4_main import zqh_tilelink_2_axi4

from zqh_system_common.zqh_system_common_parameters import zqh_system_common_parameter
from zqh_devices.zqh_sram_control.zqh_sram_control_main import zqh_sram_control
from zqh_devices.zqh_axi4_sram_control.zqh_axi4_sram_control_main import zqh_axi4_sram_control
from zqh_devices.zqh_print_monitor.zqh_print_monitor_main import zqh_print_monitor
from zqh_devices.zqh_crg_ctrl.zqh_crg_ctrl_bundles import zqh_crg_ctrl_cfg_io
from zqh_devices.zqh_crg_ctrl.zqh_crg_ctrl_main import zqh_crg_ctrl
from zqh_devices.zqh_gpio.zqh_gpio_main import zqh_gpio
from zqh_devices.zqh_gpio.zqh_gpio_bundles import zqh_gpio_io
from zqh_devices.zqh_uart.zqh_uart_main import zqh_uart
#tmp from zqh_devices.zqh_uart.zqh_uart_bundles import zqh_uart_io
from zqh_devices.zqh_spi.zqh_spi_main import zqh_spi
from zqh_devices.zqh_spi.zqh_spi_bundles import zqh_spi_io
from zqh_devices.zqh_pwm.zqh_pwm_main import zqh_pwm
#tmp from zqh_devices.zqh_pwm.zqh_pwm_bundles import zqh_pwm_io
from zqh_devices.zqh_i2c.zqh_i2c_master_main import zqh_i2c_master
#tmp from zqh_devices.zqh_i2c.zqh_i2c_master_bundles import zqh_i2c_master_io
from zqh_devices.zqh_eth_mac.zqh_eth_mac_main import zqh_eth_mac
#tmp from zqh_devices.zqh_eth_mac.zqh_eth_mac_bundles import zqh_eth_mac_phy_gmii_smi_io
from zqh_devices.zqh_ddr_mc.zqh_ddr_mc_main import zqh_ddr_mc
from zqh_ddr_phy.zqh_ddr_phy_main import zqh_ddr_phy
from zqh_ddr_phy.zqh_ddr_phy_bundles import zqh_ddr_phy_dram_io
from zqh_devices.zqh_spi_flash_xip_ctrl.zqh_spi_flash_xip_ctrl_main import zqh_spi_flash_xip_ctrl
from zqh_jtag.zqh_jtag_bundles import JTAGIO
from zqh_devices.zqh_debug.zqh_debug_transport_main import DebugTransportModuleJTAG
from zqh_common.zqh_address_space import zqh_address_space
from zqh_common.zqh_address_space import zqh_address_attr
from zqh_common.zqh_address_space import zqh_order_type
from zqh_common.zqh_transfer_size import zqh_transfer_size
from zqh_devices.zqh_usb_ctrl.zqh_usb_ctrl_main import zqh_usb_ctrl
from zqh_usb_phy.zqh_usb_phy_main import zqh_usb_phy
#tmp from zqh_usb_phy.zqh_usb_phy_bundles import zqh_usb_phy_io
from zqh_usb_phy.zqh_usb_clk_gen import zqh_usb_clk_gen

class zqh_system_common(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_system_common, self).set_par()
        self.p = zqh_system_common_parameter()

    def gen_node_tree(self):
        super(zqh_system_common, self).gen_node_tree()
        self.p.par('mem_master', zqh_tilelink_node_master_parameter('mem_master'))
        self.p.par('mmio_master', zqh_tilelink_node_master_parameter('mmio_master'))
        self.p.par('front_master',
            zqh_tilelink_node_master_parameter('front_master',
                transfer_sizes = zqh_transfer_size(min = 0,max = 8),
                bundle_out = [self.p.gen_fbus_tl_bundle_p()],
                source_id_num = self.p.fbus.source_id_num))
        self.p.par('front_bus', zqh_tilelink_node_xbar_parameter('front_bus', do_imp = 1))
        self.p.par('mem_bus', zqh_tilelink_node_xbar_parameter('mem_bus', do_imp = 1))
        self.p.par('mmio_bus', zqh_tilelink_node_xbar_parameter(
            'mmio_bus',
            down_bus_data_bits = 32,
            do_imp = 1))

        self.p.par('tile_slave', zqh_tilelink_node_slave_parameter(
            'tile_slave', 
            address = [
                zqh_address_space(
                    base = 0x00000000, 
                    mask = 0xffffffff, 
                    attr = zqh_address_attr.DEV_RWAX,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 8)))

        self.p.par('mem_sram', zqh_tilelink_node_slave_parameter(
            'mem_sram', 
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x40000000, 
                    mask = 0x0fffffff, 
                    attr = zqh_address_attr.MEM_RWAX_C_S,
                    order_type = zqh_order_type.RO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 64)))

        if (self.p.has_axi4_sram):
            self.p.par('mem_tl2axi4', zqh_tilelink_node_slave_parameter(
                'mem_tl2axi4', 
                is_pos = 1,
                address = [
                    zqh_address_space(
                        base = 0x50000000, 
                        mask = 0x0fffffff, 
                        attr = zqh_address_attr.MEM_RWAX_C_S,
                        order_type = zqh_order_type.RO)],
                transfer_sizes = zqh_transfer_size(min = 0,max = 64),
                process = [[zqh_tilelink_2_axi4, self.p.mem_tl2axi4_params]]))

        if (self.p.has_ddr):
            self.p.par('mem_ddr', zqh_tilelink_node_slave_parameter(
                'mem_ddr', 
                buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
                is_pos = 1,
                address = [
                    zqh_address_space(
                        base = 0x80000000, 
                        mask = 0x3fffffff, 
                        attr = zqh_address_attr.MEM_RWAX_C_S,
                        order_type = zqh_order_type.RO)],
                transfer_sizes = zqh_transfer_size(min = 0,max = 64)))


        if (self.p.has_axi4_sram):
            self.p.par('mem_axi4_sram', zqh_axi4_node_slave_parameter(
                'mem_axi4_sram',
                buffer_in = self.p.buf_axi4_params if (self.p.device_has_buffer) else None,
                ))

        self.p.par('mmio_devices', zqh_tilelink_node_slave_parameter(
            'mmio_devices', 
            address = [
                zqh_address_space(
                    base = 0x10000000, 
                    mask = 0x0fffffff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0, max = 4)))
        self.p.par('mmio_devices_bus', zqh_tilelink_node_xbar_parameter(
            'mmio_devices_bus', 
            down_bus_data_bits = 32))
        self.p.par('mmio_crg_ctrl', zqh_tilelink_node_slave_parameter(
            'mmio_crg_ctrl',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x10000000, 
                    mask = 0x00000fff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_gpio0', zqh_tilelink_node_slave_parameter(
            'mmio_gpio0',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x10012000, 
                    mask = 0x00000fff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_uart0', zqh_tilelink_node_slave_parameter(
            'mmio_uart0',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x10013000, 
                    mask = 0x00000fff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_spi0', zqh_tilelink_node_slave_parameter(
            'mmio_spi0',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x10014000, 
                    mask = 0x00000fff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
             transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_pwm0', zqh_tilelink_node_slave_parameter(
            'mmio_pwm0',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x10015000, 
                    mask = 0x00000fff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_i2c', zqh_tilelink_node_slave_parameter(
            'mmio_i2c',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x10016000, 
                    mask = 0x00000fff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_gpio1', zqh_tilelink_node_slave_parameter(
            'mmio_gpio1',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x1001f000, 
                    mask = 0x00000fff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        if (self.p.has_eth):
            self.p.par('mmio_eth_mac', zqh_tilelink_node_slave_parameter(
                'mmio_eth_mac',
                buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
                is_pos = 1,
                address = [
                    zqh_address_space(
                        base = 0x10020000, 
                        mask = 0x0000ffff, 
                        attr = zqh_address_attr.DEV_RWA,
                        order_type = zqh_order_type.SO)],
                transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        if (self.p.has_ddr):
            self.p.par('mmio_ddr_mc', zqh_tilelink_node_slave_parameter(
                'mmio_ddr_mc',
                buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
                is_pos = 1,
                address = [
                    zqh_address_space(
                        base = 0x10030000, 
                        mask = 0x0000ffff, 
                        attr = zqh_address_attr.DEV_RWA,
                        order_type = zqh_order_type.SO)],
                transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_usb_ctrl_host', zqh_tilelink_node_slave_parameter(
            'mmio_usb_ctrl_host',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x10040000, 
                    mask = 0x0000ffff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_usb_ctrl_device', zqh_tilelink_node_slave_parameter(
            'mmio_usb_ctrl_device',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x10050000, 
                    mask = 0x0000ffff, 
                    attr = zqh_address_attr.DEV_RWA,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.par('mmio_sram', zqh_tilelink_node_slave_parameter(
            'mmio_sram',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x11000000,
                    mask = 0x00ffffff,
                    attr = zqh_address_attr.DEV_RWAX,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        if (self.p.has_print_monitor):
            self.p.par('mmio_print_monitor', zqh_tilelink_node_slave_parameter(
                'mmio_print_monitor',
                buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
                is_pos = 1,
                address = [
                    zqh_address_space(
                        base = 0x1f000000,
                        mask = 0x00ffffff,
                        attr = zqh_address_attr.DEV_RWA,
                        order_type = zqh_order_type.SO)],
                transfer_sizes = zqh_transfer_size(min = 0,max = 4)))

        self.p.par('mem_spi_flash_xip', zqh_tilelink_node_slave_parameter(
            'mem_spi_flash_xip',
            buffer_in = self.p.buf_params if (self.p.device_has_buffer) else None,
            is_pos = 1,
            address = [
                zqh_address_space(
                    base = 0x20000000,
                    mask = 0x0fffffff,
                    attr = zqh_address_attr.MEM_RX_C_US,
                    order_type = zqh_order_type.RO)],
            transfer_sizes = zqh_transfer_size(min = 0, max = 64)))

        self.p.front_bus.push_up(self.p.front_master)
        self.p.front_bus.push_down(self.p.tile_slave)

        self.p.mem_bus.push_up(self.p.mem_master)
        self.p.mem_bus.push_down(self.p.mem_spi_flash_xip)
        self.p.mem_bus.push_down(self.p.mem_sram)
        if (self.p.has_axi4_sram):
            self.p.mem_bus.push_down(self.p.mem_tl2axi4)
        if (self.p.has_ddr):
            self.p.mem_bus.push_down(self.p.mem_ddr)

        if (self.p.has_axi4_sram):
            self.p.mem_tl2axi4.push_down(self.p.mem_axi4_sram)

        self.p.mmio_bus.push_up(self.p.mmio_master)
        self.p.mmio_bus.push_down(self.p.mmio_devices)
        self.p.mmio_devices_bus.push_up(self.p.mmio_devices)
        self.p.mmio_devices_bus.push_down(self.p.mmio_crg_ctrl)
        self.p.mmio_devices_bus.push_down(self.p.mmio_gpio0)
        self.p.mmio_devices_bus.push_down(self.p.mmio_uart0)
        self.p.mmio_devices_bus.push_down(self.p.mmio_spi0)
        self.p.mmio_devices_bus.push_down(self.p.mmio_pwm0)
        self.p.mmio_devices_bus.push_down(self.p.mmio_i2c)
        self.p.mmio_devices_bus.push_down(self.p.mmio_gpio1)
        if (self.p.has_eth):
            self.p.mmio_devices_bus.push_down(self.p.mmio_eth_mac)
        if (self.p.has_ddr):
            self.p.mmio_devices_bus.push_down(self.p.mmio_ddr_mc)
        self.p.mmio_devices_bus.push_down(self.p.mmio_usb_ctrl_host)
        self.p.mmio_devices_bus.push_down(self.p.mmio_usb_ctrl_device)

        self.p.mmio_bus.push_down(self.p.mmio_sram)
        if (self.p.has_print_monitor):
            self.p.mmio_bus.push_down(self.p.mmio_print_monitor)

        #interrupt xbar
        self.p.par('int_xbar', zqh_tilelink_int_xbar_parameter('int_xbar'))
        self.p.int_xbar.push_down(self.p.mmio_gpio0)
        self.p.int_xbar.push_down(self.p.mmio_uart0)
        self.p.int_xbar.push_down(self.p.mmio_spi0)
        self.p.int_xbar.push_down(self.p.mmio_pwm0)
        self.p.int_xbar.push_down(self.p.mmio_i2c)
        self.p.int_xbar.push_down(self.p.mmio_gpio1)
        if (self.p.has_eth):
            self.p.int_xbar.push_down(self.p.mmio_eth_mac)
        if (self.p.has_ddr):
            self.p.int_xbar.push_down(self.p.mmio_ddr_mc)
        self.p.int_xbar.push_down(self.p.mmio_usb_ctrl_host)
        self.p.int_xbar.push_down(self.p.mmio_usb_ctrl_device)
        self.p.int_xbar.push_up(self.p.mmio_master)

    def set_port(self):
        super(zqh_system_common, self).set_port()
        self.io.var(inp('clock_ref'))
        self.io.var(inp('reset_por'))
        self.io.var(inp('clock_rtc'))
        #tmp self.io.var(zqh_uart_io('uart0'))
        self.io.var(JTAGIO('jtag').flip())
        self.io.var(inp('boot_mode', w = 2))
        self.io.var(zqh_crg_ctrl_cfg_io('crg_ctrl'))

    def main(self):
        super(zqh_system_common, self).main()
        def_u_reg_dly('#0.1')

        tile = self.instance_tile()

        mem_sram_control = zqh_sram_control(
            'mem_sram_control',
            mem_size = self.p.tl_sram_size,
            extern_slaves = [self.p.mem_sram])
        if (self.p.has_axi4_sram):
            vmacro('HAS_AXI4_SRAM')
            mem_axi4_sram_control = zqh_axi4_sram_control(
                'mem_axi4_sram_control',
                mem_size = self.p.axi4_sram_size,
                extern_slaves = [self.p.mem_axi4_sram])

        mmio_sram_control = zqh_sram_control(
            'mmio_sram_control',
            mem_size = self.p.tl_io_sram_size,
            extern_slaves = [self.p.mmio_sram])
        if (self.p.has_print_monitor):
            vmacro('HAS_PRINT_MONITOR')

            mmio_print_monitor = zqh_print_monitor(
                'mmio_print_monitor',
                extern_slaves = [self.p.mmio_print_monitor])

        mmio_crg_ctrl = zqh_crg_ctrl(
            'mmio_crg_ctrl',
            extern_slaves = [self.p.mmio_crg_ctrl])
        mmio_crg_ctrl.io.clock_ref /= self.io.clock_ref
        mmio_crg_ctrl.io.reset_por /= self.io.reset_por
        self.io.crg_ctrl /= mmio_crg_ctrl.io.cfg

        mmio_gpio0 = zqh_gpio(
            'mmio_gpio0',
            num_ports = self.p.gpio0_ports_num,
            extern_slaves = [self.p.mmio_gpio0],
            reset_sync = 0) #gpio's csr reg must use async reset
        self.io.var(zqh_gpio_io('gpio0', width = mmio_gpio0.io.gpio.p.width))
        self.io.gpio0 /= mmio_gpio0.io.gpio

        mmio_uart0 = zqh_uart(
            'mmio_uart0',
            extern_slaves = [self.p.mmio_uart0])
        #tmp self.io.uart0 /= mmio_uart0.io.uart
        gpio0_idx = 0
        mmio_gpio0.io.hw_iof.port[gpio0_idx].oe /= 1
        mmio_gpio0.io.hw_iof.port[gpio0_idx].output /= mmio_uart0.io.uart.tx
        gpio0_idx += 1
        mmio_gpio0.io.hw_iof.port[gpio0_idx].oe /= 0
        mmio_uart0.io.uart.rx /= mmio_gpio0.io.hw_iof.port[gpio0_idx].input
        gpio0_idx += 1

        mmio_spi0 = zqh_spi(
            'mmio_spi0',
            extern_slaves = [self.p.mmio_spi0])
        self.io.var(zqh_spi_io('spi0', cs_width = mmio_spi0.p.cs_width))
        self.io.spi0 /= mmio_spi0.io.spi

        mmio_pwm0 = zqh_pwm(
            'mmio_pwm0',
            extern_slaves = [self.p.mmio_pwm0])
        #tmp self.io.var(zqh_pwm_io('pwm0', ncmp = mmio_pwm0.p.ncmp))
        #tmp self.io.pwm0 /= mmio_pwm0.io.pwm
        for i in range(mmio_pwm0.p.ncmp):
            mmio_gpio0.io.hw_iof.port[gpio0_idx].oe /= 1
            mmio_gpio0.io.hw_iof.port[gpio0_idx].output /= mmio_pwm0.io.pwm.do[i]
            gpio0_idx += 1

        mmio_i2c = zqh_i2c_master(
            'mmio_i2c',
            extern_slaves = [self.p.mmio_i2c])
        #tmp self.io.var(zqh_i2c_master_io('i2c'))
        #tmp self.io.i2c /= mmio_i2c.io.i2c
        mmio_gpio0.io.hw_iof.port[gpio0_idx] /= mmio_i2c.io.i2c.scl
        gpio0_idx += 1
        mmio_gpio0.io.hw_iof.port[gpio0_idx] /= mmio_i2c.io.i2c.sda
        gpio0_idx += 1

        mmio_gpio1 = zqh_gpio(
            'mmio_gpio1',
            num_ports = self.p.gpio1_ports_num,
            extern_slaves = [self.p.mmio_gpio1],
            reset_sync = 0) #gpio's csr reg must use async reset
        self.io.var(zqh_gpio_io('gpio1', width = mmio_gpio1.io.gpio.p.width))
        self.io.gpio1 /= mmio_gpio1.io.gpio

        if (self.p.has_eth):
            vmacro('HAS_ETH')

            self.io.var(inp('clock_eth'))
            self.io.var(inp('reset_eth'))

            mmio_eth_mac = zqh_eth_mac(
                'mmio_eth_mac',
                extern_slaves = [self.p.mmio_eth_mac])
            mmio_eth_mac.io.clock_ethmac /= self.io.clock_eth
            mmio_eth_mac.io.reset_ethmac /= self.io.reset_eth

            #tmp self.io.var(zqh_eth_mac_phy_gmii_smi_io('mac_phy'))
            #tmp self.io.mac_phy /= mmio_eth_mac.io.mac_phy
            gpio1_idx = 0;
            #gmii
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].output /= mmio_eth_mac.io.mac_phy.gmii.tx.gclk
            gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 0
            mmio_eth_mac.io.mac_phy.gmii.tx.clk /= mmio_gpio1.io.hw_iof.port[gpio1_idx].input
            gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].output /= mmio_eth_mac.io.mac_phy.gmii.tx.en
            gpio1_idx += 1
            for i in range(mmio_eth_mac.io.mac_phy.gmii.tx.d.get_w()):
                mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 1
                mmio_gpio1.io.hw_iof.port[gpio1_idx].output /= mmio_eth_mac.io.mac_phy.gmii.tx.d[i]
                gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].output /= mmio_eth_mac.io.mac_phy.gmii.tx.err
            gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 0
            mmio_eth_mac.io.mac_phy.gmii.rx.clk /= mmio_gpio1.io.hw_iof.port[gpio1_idx].input
            gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 0
            mmio_eth_mac.io.mac_phy.gmii.rx.dv /= mmio_gpio1.io.hw_iof.port[gpio1_idx].input
            gpio1_idx += 1
            for i in range(mmio_eth_mac.io.mac_phy.gmii.rx.d.get_w()):
                mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 0
                mmio_eth_mac.io.mac_phy.gmii.rx.d[i] /= mmio_gpio1.io.hw_iof.port[gpio1_idx].input
                gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 0
            mmio_eth_mac.io.mac_phy.gmii.rx.err /= mmio_gpio1.io.hw_iof.port[gpio1_idx].input
            gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 0
            mmio_eth_mac.io.mac_phy.gmii.cscd.cs /= mmio_gpio1.io.hw_iof.port[gpio1_idx].input
            gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 0
            mmio_eth_mac.io.mac_phy.gmii.cscd.cd /= mmio_gpio1.io.hw_iof.port[gpio1_idx].input
            gpio1_idx += 1
            #smi
            mmio_gpio1.io.hw_iof.port[gpio1_idx ].oe /= 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx ].output /= mmio_eth_mac.io.mac_phy.smi.mdc
            gpio1_idx += 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx] /= mmio_eth_mac.io.mac_phy.smi.mdio
            gpio1_idx += 1
            #reset_n
            mmio_gpio1.io.hw_iof.port[gpio1_idx].oe /= 1
            mmio_gpio1.io.hw_iof.port[gpio1_idx].output /= mmio_eth_mac.io.mac_phy.reset_n
            gpio1_idx += 1

        if (self.p.has_ddr):
            vmacro('HAS_DDR')

            self.io.var(inp('clock_ddr'))
            self.io.var(inp('reset_ddr_phy'))
            self.io.var(inp('reset_ddr_mc'))

            mmio_ddr_mc = zqh_ddr_mc(
                'mmio_ddr_mc',
                extern_slaves = [self.p.mmio_ddr_mc, self.p.mem_ddr])
            mmio_ddr_mc.io.clock_ddr /= self.io.clock_ddr
            mmio_ddr_mc.io.reset_ddr_mc /= self.io.reset_ddr_mc
            ddr_phy = zqh_ddr_phy('ddr_phy', imp_mode = self.p.imp_mode)
            ddr_phy.io.dll_clock_ref /= self.io.clock_ref
            ddr_phy.io.dll_reset_por /= self.io.reset_por
            ddr_phy.io.clock /= self.io.clock_ddr
            ddr_phy.io.reset /= self.io.reset_ddr_phy
            ddr_phy.io.reg /= mmio_ddr_mc.io.phy_reg
            ddr_phy.io.dfi /= mmio_ddr_mc.io.phy_dfi
            self.io.var(zqh_ddr_phy_dram_io('ddr', p = ddr_phy.io.ddr.p))
            self.io.ddr /= ddr_phy.io.ddr

            vmacro('DDR_PHY_X'+str(ddr_phy.io.ddr.p.xn))


        #
        #usb
        #{{{
        #usb tx/rx clock generate
        self.io.var(inp('clock_usb_ref'))
        self.io.var(inp('reset_usb'))
        usb_host_clk_gen = zqh_usb_clk_gen('usb_host_clk_gen')
        usb_host_clk_gen.io.clock /= self.io.clock_usb_ref
        usb_host_clk_gen.io.reset /= self.io.reset_usb
        #usb host phy
        #tmp self.io.var(zqh_usb_phy_io('usb_host'))
        usb_phy_host = zqh_usb_phy('usb_phy_host')
        usb_phy_host.io.clock /= usb_host_clk_gen.io.utmi_clock_out
        usb_phy_host.io.tx_clk /= usb_host_clk_gen.io.tx_clock_out
        usb_phy_host.io.rx_clk /= usb_host_clk_gen.io.rx_clock_out
        usb_host_clk_gen.io.div /= 33
        usb_host_clk_gen.io.din /= usb_phy_host.io.usb.dp.input
        #tmp self.io.usb_host /= usb_phy_host.io.usb
        mmio_gpio1.io.hw_iof.port[gpio1_idx] /= usb_phy_host.io.usb.dp
        gpio1_idx += 1
        mmio_gpio1.io.hw_iof.port[gpio1_idx] /= usb_phy_host.io.usb.dm
        gpio1_idx += 1

        #usb device phy
        usb_device_clk_gen = zqh_usb_clk_gen('usb_device_clk_gen')
        usb_device_clk_gen.io.clock /= self.io.clock_usb_ref
        usb_device_clk_gen.io.reset /= self.io.reset_usb
        #tmp self.io.var(zqh_usb_phy_io('usb_device'))
        usb_phy_device = zqh_usb_phy('usb_phy_device')
        usb_phy_device.io.clock /= usb_device_clk_gen.io.utmi_clock_out
        usb_phy_device.io.tx_clk /= usb_device_clk_gen.io.tx_clock_out
        usb_phy_device.io.rx_clk /= usb_device_clk_gen.io.rx_clock_out
        usb_device_clk_gen.io.div /= 33
        usb_device_clk_gen.io.din /= usb_phy_device.io.usb.dp.input
        #tmp self.io.usb_device /= usb_phy_device.io.usb
        mmio_gpio1.io.hw_iof.port[gpio1_idx] /= usb_phy_device.io.usb.dp
        gpio1_idx += 1
        mmio_gpio1.io.hw_iof.port[gpio1_idx] /= usb_phy_device.io.usb.dm
        gpio1_idx += 1

        #usb host controler
        mmio_usb_ctrl_host = zqh_usb_ctrl(
            'mmio_usb_ctrl_host',
            extern_slaves = [self.p.mmio_usb_ctrl_host])
        usb_phy_host.io.reg /= mmio_usb_ctrl_host.io.phy_reg
        usb_phy_host.io.utmi /= mmio_usb_ctrl_host.io.utmi
        usb_phy_host.io.reset /= usb_phy_host.io.utmi.Reset

        #usb device controler
        mmio_usb_ctrl_device = zqh_usb_ctrl(
            'mmio_usb_ctrl_device',
            extern_slaves = [self.p.mmio_usb_ctrl_device])
        usb_phy_device.io.reg /= mmio_usb_ctrl_device.io.phy_reg
        usb_phy_device.io.utmi /= mmio_usb_ctrl_device.io.utmi
        usb_phy_device.io.reset /= usb_phy_device.io.utmi.Reset
        #}}}


        mem_spi_flash_xip = zqh_spi_flash_xip_ctrl(
            'mem_spi_flash_xip',
            extern_slaves = [self.p.mem_spi_flash_xip])
        mmio_spi0.io.xip /= mem_spi_flash_xip.io.spi_xip

        tile.io.boot_mode /= self.io.boot_mode

        #debug interface bind
        tile.io.debug.debugUnavail /= 0
        tile.io.reset /= self.io.reset | tile.io.debug.ndreset

        dtm = DebugTransportModuleJTAG(
            'dtm',
            dumy = self.p.debug_dumy,
            debugAddrBits = tile.io.dmi.dmi.p.nDMIAddrSize)
        dtm.io.jtag /= self.io.jtag

        dtm.io.clock /= self.io.jtag.TCK
        dtm.io.jtag_reset /= self.io.reset
        dtm.io.jtag_mfr_id /= 0
        dtm.io.reset /= dtm.io.fsmReset

        tile.io.dmi.dmi /= dtm.io.dmi
        tile.io.dmi.dmiClock /= self.io.jtag.TCK
        tile.io.dmi.dmiReset /= dtm.io.fsmReset

        tile.io.clock_rtc /= self.io.clock_rtc
        
    def instance_tile(self):
        pass
