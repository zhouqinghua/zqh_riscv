import sys
import os
from phgl_imp import *
from zqh_vips.eth_phy_gmii.eth_phy_gmii_main import eth_phy
from zqh_vips.N25Q064A13E_VG12.N25Q064A13E_VG12_main import N25Qxxx
from zqh_vips.eeprom_24xx08H.eeprom_24LC08BH_main import M24LC08BH
from zqh_vips.SimJTAG.SimJTAG_main import SimJTAG
from zqh_vips.dmi_jtag_bfm.dmi_jtag_bfm_main import dmi_jtag_bfm
from zqh_vips.DDR3_model.DDR3_model_main import ddr3
from .zqh_test_harness_common_ut_parameters import zqh_test_harness_common_ut_parameter

class zqh_test_harness_common_ut(unit_test):
    def set_par(self):
        super(zqh_test_harness_common_ut, self).set_par()
        self.p = zqh_test_harness_common_ut_parameter()

    def check_par(self):
        super(zqh_test_harness_common_ut, self).check_par()
        self.pm.reset_name = 'reset_n' #0 valid reset
        self.pm.reset_level = 0 #0 means valid reset


    def set_port(self):
        super(zqh_test_harness_common_ut, self).set_port()
        self.io.var(inp('clock_rtc'))
        self.io.var(inp('clock_uart'))
        self.io.var(inp('clock_jtag'))

    def main(self):
        super(zqh_test_harness_common_ut, self).main()
        dut = self.instance_dut()
        dut.io.clock_rtc /= self.io.clock_rtc
        dut.io.clock_diff.sig_p /= self.io.clock
        dut.io.clock_diff.sig_n /= ~self.io.clock
        dut.io.reset_n /= self.io.reset_n


        #boot_mode
        #0: flash xip, 1: memory, 2: debug
        dut.io.boot_mode /= 0 #default


        #uart loopback: tx -> rx
        #tmp dut.io.uart0.rx /= dut.io.uart0.tx
        uart_print_monitor = uart_rx_monitor(
            'uart_print_monitor',
            print_mode = 'string',
            #div = 32 - 1,
            div = 1042 - 1,#9600 @10MHz clock
            #div = 521 - 1,#19200 @10MHz clock
            #div = 260 - 1,#38400 @10MHz clock
            parity = 0,
            sync_delay = 2)
        uart_print_monitor.io.clock /= self.io.clock_uart
        #tmp uart_print_monitor.io.rx /= dut.io.uart0.tx
        #tmp dut.io.uart0.rx /= uart_print_monitor.io.tx
        #pullup to 1 to avoid z state
        gpio0_idx = 0
        pullup(dut.io.gpio0.port[gpio0_idx])
        uart_print_monitor.io.rx /= dut.io.gpio0.port[gpio0_idx]
        gpio0_idx += 1
        pullup(dut.io.gpio0.port[gpio0_idx])
        dut.io.gpio0.port[gpio0_idx] /= uart_print_monitor.io.tx
        gpio0_idx += 1


        #eth_phy model
        if (dut.system.p.has_eth):
#tmp            pullup(dut.io.mac_phy.smi.mdio)
            eth_phy0 = eth_phy('eth_phy0')
#tmp            #tmp eth_phy0.io.m_rst_n_i /= self.io.reset_n
#tmp            eth_phy0.io.m_rst_n_i /= dut.io.mac_phy.reset_n
#tmp            # MAC TX
#tmp            dut.io.mac_phy.gmii.tx.clk /= eth_phy0.io.mtx_clk_o
#tmp            eth_phy0.io.mtx_gclk_i     /= dut.io.mac_phy.gmii.tx.gclk
#tmp            eth_phy0.io.mtxd_i         /= dut.io.mac_phy.gmii.tx.d
#tmp            eth_phy0.io.mtxen_i        /= dut.io.mac_phy.gmii.tx.en
#tmp            eth_phy0.io.mtxerr_i       /= dut.io.mac_phy.gmii.tx.err
#tmp            # MAC RX
#tmp            dut.io.mac_phy.gmii.rx.clk /= eth_phy0.io.mrx_clk_o
#tmp            dut.io.mac_phy.gmii.rx.d   /= eth_phy0.io.mrxd_o
#tmp            dut.io.mac_phy.gmii.rx.dv  /= eth_phy0.io.mrxdv_o
#tmp            dut.io.mac_phy.gmii.rx.err /= eth_phy0.io.mrxerr_o
#tmp            # cs/cd
#tmp            dut.io.mac_phy.gmii.cscd.cd /= eth_phy0.io.mcoll_o
#tmp            dut.io.mac_phy.gmii.cscd.cs /= eth_phy0.io.mcrs_o
#tmp            # GMIIM
#tmp            eth_phy0.io.mdc_i /= dut.io.mac_phy.smi.mdc
#tmp            tran(eth_phy0.io.md_io, dut.io.mac_phy.smi.mdio)

            gpio1_idx = 0;
            #gmii
            eth_phy0.io.mtx_gclk_i /= dut.io.gpio1.port[gpio1_idx]
            gpio1_idx += 1
            dut.io.gpio1.port[gpio1_idx] /= eth_phy0.io.mtx_clk_o
            gpio1_idx += 1
            eth_phy0.io.mtxen_i /= dut.io.gpio1.port[gpio1_idx]
            gpio1_idx += 1
            for i in range(eth_phy0.io.mtxd_i.get_w()):
                eth_phy0.io.mtxd_i[i] /= dut.io.gpio1.port[gpio1_idx]
                gpio1_idx += 1
            eth_phy0.io.mtxerr_i /= dut.io.gpio1.port[gpio1_idx]
            gpio1_idx += 1
            dut.io.gpio1.port[gpio1_idx] /= eth_phy0.io.mrx_clk_o
            gpio1_idx += 1
            dut.io.gpio1.port[gpio1_idx] /= eth_phy0.io.mrxdv_o
            gpio1_idx += 1
            for i in range(eth_phy0.io.mrxd_o.get_w()):
                dut.io.gpio1.port[gpio1_idx] /= eth_phy0.io.mrxd_o[i]
                gpio1_idx += 1
            dut.io.gpio1.port[gpio1_idx] /= eth_phy0.io.mrxerr_o
            gpio1_idx += 1
            dut.io.gpio1.port[gpio1_idx] /= eth_phy0.io.mcrs_o
            gpio1_idx += 1
            dut.io.gpio1.port[gpio1_idx] /= eth_phy0.io.mcoll_o
            gpio1_idx += 1
            #smi
            eth_phy0.io.mdc_i /= dut.io.gpio1.port[gpio1_idx]
            gpio1_idx += 1
            pullup(dut.io.gpio1.port[gpio1_idx])
            tran(eth_phy0.io.md_io, dut.io.gpio1.port[gpio1_idx])
            gpio1_idx += 1
            #reset_n
            eth_phy0.io.m_rst_n_i /= dut.io.gpio1.port[gpio1_idx]
            gpio1_idx += 1
            # SYSTEM
            eth_phy0.io.phy_log /= value(0x80000001, w = 32) #STDOUT

        
        #spi flash model
        pullup(dut.io.spi0.dq)
        spi_flash_N25Qxxx = N25Qxxx('spi_flash_N25Qxxx')
        spi_flash_N25Qxxx.io.S         /= dut.io.spi0.cs[0]
        spi_flash_N25Qxxx.io.C_        /= dut.io.spi0.sck
        spi_flash_N25Qxxx.io.Vcc       /= 3000
        tran(spi_flash_N25Qxxx.io.DQ0      ,  dut.io.spi0.dq[0])
        tran(spi_flash_N25Qxxx.io.DQ1      ,  dut.io.spi0.dq[1])
        tran(spi_flash_N25Qxxx.io.Vpp_W_DQ2,  dut.io.spi0.dq[2])
        tran(spi_flash_N25Qxxx.io.HOLD_DQ3 ,  dut.io.spi0.dq[3])


        #i2c eeproma model
        #tmp pullup(dut.io.i2c)
        i2c_eeprom_24xx = M24LC08BH('i2c_eeprom_24xx')
        i2c_eeprom_24xx.io.A0 /= 0
        i2c_eeprom_24xx.io.A1 /= 0
        i2c_eeprom_24xx.io.A2 /= 0
        i2c_eeprom_24xx.io.WP /= 0
        i2c_eeprom_24xx.io.RESET /= ~self.io.reset_n
        #tmp tran(i2c_eeprom_24xx.io.SDA, dut.io.i2c.sda)
        #tmp tran(i2c_eeprom_24xx.io.SCL, dut.io.i2c.scl)
        gpio0_idx = 6
        pullup(dut.io.gpio0.port[gpio0_idx])
        tran(i2c_eeprom_24xx.io.SCL, dut.io.gpio0.port[gpio0_idx])
        gpio0_idx += 1
        pullup(dut.io.gpio0.port[gpio0_idx])
        tran(i2c_eeprom_24xx.io.SDA, dut.io.gpio0.port[gpio0_idx])
        gpio0_idx += 1


        #gpio bidirection pad
        #tmp pullup(dut.io.gpio0)
        for i in range(8, dut.io.gpio0.p.width):
            pullup(dut.io.gpio0.port[i])


        #SimJTAG model
        if (self.p.use_jtag):
            vmacro('USE_JTAG')
            if (self.p.jtag_type == 'fesvr'):
                simJTAG  = SimJTAG('simJTAG')
            else:
                simJTAG  = dmi_jtag_bfm('simJTAG')
            simJTAG.io.clock /= self.io.clock
            simJTAG.io.reset /= ~self.io.reset_n
            simJTAG.io.enable /= 1
            simJTAG.io.init_done /= self.io.reset_n
            simJTAG.io.jtag_TDO_driven /= 1
            simJTAG.io.jtag_TDO_data /= dut.io.jtag.TDO
            dut.io.jtag.TCK /= simJTAG.io.jtag_TCK;
            dut.io.jtag.TMS /= simJTAG.io.jtag_TMS;
            dut.io.jtag.TDI /= simJTAG.io.jtag_TDI;
        else:
            pullup(dut.io.jtag.TCK)
            pullup(dut.io.jtag.TMS)
            pullup(dut.io.jtag.TDI)
            pullup(dut.io.jtag.TDO)
            #dut.io.jtag.TCK /= self.io.clock_jtag

        #ddr3 model
        if (dut.system.p.has_ddr):
            ddr3_chips = list(map(lambda _: ddr3(
                'ddr3_chips_'+str(_),
                speed_bin = dut.io.ddr.p.speed_bin,
                #size = 'den1024Mb',
                size = dut.io.ddr.p.size,
                xn = dut.io.ddr.p.xn), range(dut.io.ddr.p.slice_num)))
            for i in range(dut.io.ddr.p.slice_num):
                ddr3_chips[i].io.rst_n /= dut.io.ddr.mem_reset_n
                ddr3_chips[i].io.ck    /= dut.io.ddr.mem_clk
                ddr3_chips[i].io.ck_n  /= dut.io.ddr.mem_clk_n
                ddr3_chips[i].io.cke   /= dut.io.ddr.mem_cke
                ddr3_chips[i].io.cs_n  /= dut.io.ddr.mem_cs_n
                ddr3_chips[i].io.ras_n /= dut.io.ddr.mem_ras_n
                ddr3_chips[i].io.cas_n /= dut.io.ddr.mem_cas_n
                ddr3_chips[i].io.we_n  /= dut.io.ddr.mem_we_n
                ddr3_chips[i].io.ba    /= dut.io.ddr.mem_bank
                ddr3_chips[i].io.addr  /= dut.io.ddr.mem_address
                ddr3_chips[i].io.odt   /= dut.io.ddr.mem_odt

                tran(ddr3_chips[i].io.dm_tdqs , dut.io.ddr.pad_mem_dm[i])
                tran(ddr3_chips[i].io.dq      , dut.io.ddr.pad_mem_data[i])
                tran(ddr3_chips[i].io.dqs     , dut.io.ddr.pad_mem_dqs[i])
                tran(ddr3_chips[i].io.dqs_n   , dut.io.ddr.pad_mem_dqs_n[i])
        
        #usb
        pullup(dut.io.gpio1.port[gpio1_idx])
        gpio1_idx += 1
        pulldown(dut.io.gpio1.port[gpio1_idx])
        gpio1_idx += 1

        pullup(dut.io.gpio1.port[gpio1_idx])
        gpio1_idx += 1
        pulldown(dut.io.gpio1.port[gpio1_idx])
        gpio1_idx += 1

        #tmp tran(dut.io.usb_host.dp, dut.io.usb_device.dp)
        #tmp tran(dut.io.usb_host.dm, dut.io.usb_device.dm)

        #tmp #usb device model
        #tmp usb_device = usb_device_model('usb_device', MODE = 1)
        #tmp usb_device.io.Vbus /= 0
        #tmp usb_device.io.GND /= 0
        #tmp tran(usb_device.io.Dp, dut.io.usb_host.dp)
        #tmp tran(usb_device.io.Dm, dut.io.usb_host.dm)


    def instance_dut(self):
        pass
