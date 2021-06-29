import sys
import os
from phgl_imp import *
from zqh_devices.zqh_gpio.zqh_gpio_bundles import zqh_gpio_pad
#tmp from zqh_devices.zqh_uart.zqh_uart_bundles import zqh_uart_pad
from zqh_devices.zqh_spi.zqh_spi_bundles import zqh_spi_pad
from zqh_devices.zqh_spi.zqh_spi_misc import zqh_spi_consts
#tmp from zqh_devices.zqh_pwm.zqh_pwm_bundles import zqh_pwm_pad
#tmp from zqh_devices.zqh_i2c.zqh_i2c_master_bundles import zqh_i2c_master_pad
#tmp from zqh_devices.zqh_eth_mac.zqh_eth_mac_bundles import zqh_eth_mac_phy_gmii_smi_pad
from zqh_jtag.zqh_jtag_bundles import JTAG_pad
from zqh_crg.zqh_crg_main import zqh_crg
from zqh_ddr_phy.zqh_ddr_phy_bundles import zqh_ddr_phy_dram_pad
from .zqh_full_chip_common_parameters import zqh_full_chip_common_parameter
#tmp from zqh_usb_phy.zqh_usb_phy_bundles import zqh_usb_phy_pad

class zqh_full_chip_common(module):
    def set_par(self):
        super(zqh_full_chip_common, self).set_par()
        self.p = zqh_full_chip_common_parameter()
    
    def set_port(self):
        super(zqh_full_chip_common, self).set_port()
        self.no_crg()

        self.io.var(inp('clock_rtc'))
        self.io.var(inp_diff_pair('clock_diff'))
        self.io.var(inp('reset_n'))
        #tmp self.io.var(zqh_uart_pad('uart0'))
        #tmp self.io.var(zqh_i2c_master_pad('i2c'))
        self.io.var(JTAG_pad('jtag'))
        self.io.var(inp('boot_mode', w = 2))

    def main(self):
        super(zqh_full_chip_common, self).main()

        self.system = self.instance_system()

        crg = zqh_crg('crg', imp_mode = self.p.imp_mode)
        #tmp crg.io.clock /= self.io.clock_diff.sig_p
        #tmp crg.io.reset_n /= self.io.reset_n
        #tmp crg.io.clock_rtc_i /= self.io.clock_rtc
        crg.io.crg_ctrl /= self.system.io.crg_ctrl

        #usb
        #tmp self.io.var(zqh_usb_phy_pad('usb_host', p = self.system.io.usb_host.p))
        #tmp self.io.var(zqh_usb_phy_pad('usb_device', p = self.system.io.usb_device.p))
        #tmp bind_pad(self.io.usb_host, self.system.io.usb_host)
        #tmp bind_pad(self.io.usb_device, self.system.io.usb_device)
        self.system.io.clock_usb_ref /= crg.io.clock_usb_ref_o
        self.system.io.reset_usb /= crg.io.reset_usb_o


        #crg pad bind
        if (self.p.imp_mode == 'fpga'):
            clock_diff_pad = IBUFDS('clock_diff_pad')
            clock_diff_pad.io.I /= self.io.clock_diff.sig_p
            clock_diff_pad.io.IB /= self.io.clock_diff.sig_n
            crg.io.clock /= clock_diff_pad.io.O
        else:
            bind_pad(self.io.clock_diff, crg.io.clock)
        bind_pad(self.io.reset_n, crg.io.reset_n)
        bind_pad(self.io.clock_rtc, crg.io.clock_rtc_i)



        #clock connect
        self.system.io.clock_ref /= crg.io.clock_ref_o
        self.system.io.reset_por /= crg.io.reset_por_o
        self.system.io.clock /= crg.io.clock_core_o
        self.system.io.reset /= crg.io.reset_core_o
        if (self.system.p.has_eth):
            self.system.io.clock_eth /= crg.io.clock_eth_o
            self.system.io.reset_eth /= crg.io.reset_eth_o

            #mac phy pad bind
            #tmp self.io.var(zqh_eth_mac_phy_gmii_smi_pad('mac_phy'))
            #tmp bind_pad(self.io.mac_phy, self.system.io.mac_phy)

        if (self.system.p.has_ddr):
            self.system.io.clock_ddr /= crg.io.clock_ddr_o
            self.system.io.reset_ddr_phy /= crg.io.reset_ddr_phy_o
            self.system.io.reset_ddr_mc /= crg.io.reset_ddr_mc_o

            #ddr pad bind
            self.io.var(zqh_ddr_phy_dram_pad('ddr', p = self.system.io.ddr.p))
            bind_pad(self.io.ddr, self.system.io.ddr)

            #diff signal bind for fpga
            if (self.p.imp_mode == 'fpga'):
                ddr_clk_diff_pad = OBUFDS('ddr_clk_diff_pad')
                ddr_clk_diff_pad.io.I /= self.system.io.ddr.mem_clk
                self.io.ddr.mem_clk /= ddr_clk_diff_pad.io.O
                self.io.ddr.mem_clk_n /= ddr_clk_diff_pad.io.OB

                #bi-direction diff signal
                for i in range(len(self.system.io.ddr.pad_mem_dqs)):
                    for j in range(self.system.io.ddr.pad_mem_dqs[i].output.get_w()):
                        ddr_dqs_diff_pad = IOBUFDS('ddr_dqs_diff_pad_'+str(i)+'_'+str(j))
                        ddr_dqs_diff_pad.io.I /= self.system.io.ddr.pad_mem_dqs[i].output[j]
                        ddr_dqs_diff_pad.io.T /= ~self.system.io.ddr.pad_mem_dqs[i].oe
                        #tmp self.io.ddr.pad_mem_dqs[i][j] /= ddr_dqs_diff_pad.io.IO
                        #tmp self.io.ddr.pad_mem_dqs_n[i][j] /= ddr_dqs_diff_pad.io.IOB
                        bind_port(ddr_dqs_diff_pad.io.IO, self.io.ddr.pad_mem_dqs[i][j])
                        bind_port(ddr_dqs_diff_pad.io.IOB, self.io.ddr.pad_mem_dqs_n[i][j])
                        #tmp tran(self.io.ddr.pad_mem_dqs[i][j], ddr_dqs_diff_pad.io.IO)                        
                        #tmp tran(self.io.ddr.pad_mem_dqs_n[i][j], ddr_dqs_diff_pad.io.IOB)                        
                        self.system.io.ddr.pad_mem_dqs[i].input[j] /= ddr_dqs_diff_pad.io.O

        self.system.io.clock_rtc /= crg.io.clock_rtc_o


        #boot_mode pad bind
        bind_pad(self.io.boot_mode, self.system.io.boot_mode)

        #gpio pad bind
        self.io.var(zqh_gpio_pad('gpio0', width = self.system.io.gpio0.p.width))
        bind_pad(self.io.gpio0, self.system.io.gpio0)
        self.io.var(zqh_gpio_pad('gpio1', width = self.system.io.gpio1.p.width))
        bind_pad(self.io.gpio1, self.system.io.gpio1)

        #uart pad bind
        #tmp bind_pad(self.io.uart0, self.system.io.uart0)

        #spi pad bind
        self.io.var(zqh_spi_pad('spi0', cs_width = self.system.io.spi0.p.cs_width))
        bind_pad(self.io.spi0, self.system.io.spi0)

        #i2c pad bind
        #tmp bind_pad(self.io.i2c, self.system.io.i2c)

        #pwm pad bind
        #tmp self.io.var(zqh_pwm_pad('pwm0', ncmp = self.system.io.pwm0.p.ncmp))
        #tmp bind_pad(self.io.pwm0, self.system.io.pwm0)

        #jtag pad bind
        bind_pad(self.io.jtag, self.system.io.jtag)

        #interrupt id map report
        self.system.p.int_xbar.print_global_id_map()

    def instance_system(self):
        pass
