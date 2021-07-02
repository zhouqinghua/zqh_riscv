############## NET - IOSTANDARD ######################
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
#############SPI Configurate Setting##################
set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]
set_property CONFIG_MODE SPIx4 [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]


##############reference clock and reset define#################
create_clock -period 5.000 [get_ports io_clock_diff_sig_p]
set_property PACKAGE_PIN R4 [get_ports io_clock_diff_sig_p]
set_property IOSTANDARD DIFF_SSTL15 [get_ports io_clock_diff_sig_p]
set_property IOSTANDARD LVCMOS15 [get_ports io_reset_n]
set_property PACKAGE_PIN T6 [get_ports io_reset_n]


# rtc clock TBD
create_clock -period 1000.000 -name io_clock_rtc [get_ports io_clock_rtc]


#uart
set_property PACKAGE_PIN Y11 [get_ports io_gpio0_port_0]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_0]
set_property PACKAGE_PIN Y12 [get_ports io_gpio0_port_1]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_1]

#i2c bus
set_property PACKAGE_PIN V19 [get_ports io_gpio0_port_6]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_6]
set_property PACKAGE_PIN V18 [get_ports io_gpio0_port_7]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_7]


# io_boot_mode
set_property PACKAGE_PIN K14 [get_ports {io_boot_mode[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {io_boot_mode[0]}]
set_property PACKAGE_PIN K13 [get_ports {io_boot_mode[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {io_boot_mode[1]}]


#gpio
#key(on board)
set_property PACKAGE_PIN B18 [get_ports io_gpio0_port_8]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_8]
set_property PACKAGE_PIN B17 [get_ports io_gpio0_port_9]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_9]
set_property PACKAGE_PIN A16 [get_ports io_gpio0_port_10]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_10]
set_property PACKAGE_PIN A15 [get_ports io_gpio0_port_11]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_11]

#gpio(off board J5)
set_property PACKAGE_PIN AB15 [get_ports io_gpio0_port_12]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_12]
set_property PACKAGE_PIN AA15 [get_ports io_gpio0_port_13]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_13]
set_property PACKAGE_PIN AA14 [get_ports io_gpio0_port_14]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_14]
set_property PACKAGE_PIN Y13 [get_ports io_gpio0_port_15]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_15]
set_property PACKAGE_PIN AB17 [get_ports io_gpio0_port_16]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_16]
set_property PACKAGE_PIN AB16 [get_ports io_gpio0_port_17]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_17]
set_property PACKAGE_PIN AA16 [get_ports io_gpio0_port_18]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_18]
set_property PACKAGE_PIN Y16 [get_ports io_gpio0_port_19]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_19]
set_property PACKAGE_PIN AB12 [get_ports io_gpio0_port_20]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_20]
set_property PACKAGE_PIN AB11 [get_ports io_gpio0_port_21]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_21]
set_property PACKAGE_PIN Y14 [get_ports io_gpio0_port_22]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_22]
set_property PACKAGE_PIN W14 [get_ports io_gpio0_port_23]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_23]
set_property PACKAGE_PIN C19 [get_ports io_gpio0_port_24]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_24]
set_property PACKAGE_PIN C18 [get_ports io_gpio0_port_25]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_25]
set_property PACKAGE_PIN F14 [get_ports io_gpio0_port_26]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_26]
set_property PACKAGE_PIN F13 [get_ports io_gpio0_port_27]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_27]
set_property PACKAGE_PIN E14 [get_ports io_gpio0_port_28]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_28]
set_property PACKAGE_PIN E13 [get_ports io_gpio0_port_29]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_29]
set_property PACKAGE_PIN D15 [get_ports io_gpio0_port_30]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_30]
set_property PACKAGE_PIN D14 [get_ports io_gpio0_port_31]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_31]



#spi flash
set_property PACKAGE_PIN H14 [get_ports {io_spi0_cs[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {io_spi0_cs[0]}]
set_property PACKAGE_PIN J14 [get_ports {io_spi0_cs[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {io_spi0_cs[1]}]
set_property PACKAGE_PIN H15 [get_ports {io_spi0_cs[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {io_spi0_cs[2]}]
set_property PACKAGE_PIN J15 [get_ports {io_spi0_cs[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {io_spi0_cs[3]}]
set_property PACKAGE_PIN G13 [get_ports io_spi0_sck]
set_property IOSTANDARD LVCMOS33 [get_ports io_spi0_sck]
set_property PACKAGE_PIN H13 [get_ports io_spi0_dq_0]
set_property IOSTANDARD LVCMOS33 [get_ports io_spi0_dq_0]
set_property PACKAGE_PIN J21 [get_ports io_spi0_dq_1]
set_property IOSTANDARD LVCMOS33 [get_ports io_spi0_dq_1]
set_property PACKAGE_PIN J20 [get_ports io_spi0_dq_2]
set_property IOSTANDARD LVCMOS33 [get_ports io_spi0_dq_2]
set_property PACKAGE_PIN G16 [get_ports io_spi0_dq_3]
set_property IOSTANDARD LVCMOS33 [get_ports io_spi0_dq_3]


#pwm(4 led lights on board)
set_property PACKAGE_PIN C17 [get_ports io_gpio0_port_2]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_2]
set_property PACKAGE_PIN D17 [get_ports io_gpio0_port_3]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_3]
set_property PACKAGE_PIN V20 [get_ports io_gpio0_port_4]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_4]
set_property PACKAGE_PIN U20 [get_ports io_gpio0_port_5]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio0_port_5]


#jtag
create_clock -period 200.000 -name jtag_tck [get_ports io_jtag_TCK]
set_property PACKAGE_PIN A21 [get_ports io_jtag_TCK]
set_property IOSTANDARD LVCMOS33 [get_ports io_jtag_TCK]
set_property PACKAGE_PIN B21 [get_ports io_jtag_TMS]
set_property IOSTANDARD LVCMOS33 [get_ports io_jtag_TMS]
set_property PACKAGE_PIN M17 [get_ports io_jtag_TDI]
set_property IOSTANDARD LVCMOS33 [get_ports io_jtag_TDI]
set_property PACKAGE_PIN F21 [get_ports io_jtag_TDO]
set_property IOSTANDARD LVCMOS33 [get_ports io_jtag_TDO]

#set_property PULLUP true [get_ports io_jtag_TCK]
#set_property PULLUP true [get_ports io_jtag_TMS]
#set_property PULLUP true [get_ports io_jtag_TDI]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets io_jtag_TCK_IBUF]



##eth phy tx
####create_clock -period 40.000 -name eth_phy_tx_clk [get_ports io_gpio1_port_1]
set_property PACKAGE_PIN L18 [get_ports io_gpio1_port_0]
set_property PACKAGE_PIN J17 [get_ports io_gpio1_port_1]
set_property PACKAGE_PIN M16 [get_ports io_gpio1_port_2]
set_property PACKAGE_PIN M15 [get_ports io_gpio1_port_3]
set_property PACKAGE_PIN L14 [get_ports io_gpio1_port_4]
set_property PACKAGE_PIN K16 [get_ports io_gpio1_port_5]
set_property PACKAGE_PIN L16 [get_ports io_gpio1_port_6]
set_property PACKAGE_PIN K17 [get_ports io_gpio1_port_7]
set_property PACKAGE_PIN L20 [get_ports io_gpio1_port_8]
set_property PACKAGE_PIN L19 [get_ports io_gpio1_port_9]
set_property PACKAGE_PIN L13 [get_ports io_gpio1_port_10]
set_property PACKAGE_PIN M13 [get_ports io_gpio1_port_11]

set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_0]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_1]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_2]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_3]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_4]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_5]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_6]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_7]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_8]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_9]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_10]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_11]

#eth phy rx
create_clock -period 8.000 -name eth_phy_rx_clk [get_ports io_gpio1_port_12]
set_property PACKAGE_PIN K18 [get_ports io_gpio1_port_12]
set_property PACKAGE_PIN M22 [get_ports io_gpio1_port_13]
set_property PACKAGE_PIN N22 [get_ports io_gpio1_port_14]
set_property PACKAGE_PIN H18 [get_ports io_gpio1_port_15]
set_property PACKAGE_PIN H17 [get_ports io_gpio1_port_16]
set_property PACKAGE_PIN K19 [get_ports io_gpio1_port_17]
set_property PACKAGE_PIN M21 [get_ports io_gpio1_port_18]
set_property PACKAGE_PIN L21 [get_ports io_gpio1_port_19]
set_property PACKAGE_PIN N20 [get_ports io_gpio1_port_20]
set_property PACKAGE_PIN M20 [get_ports io_gpio1_port_21]
set_property PACKAGE_PIN N19 [get_ports io_gpio1_port_22]
set_property PACKAGE_PIN M18 [get_ports io_gpio1_port_23]
set_property PACKAGE_PIN N18 [get_ports io_gpio1_port_24]

set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_12]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_13]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_14]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_15]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_16]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_17]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_18]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_19]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_20]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_21]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_22]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_23]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_24]

#eth smi
set_property PACKAGE_PIN W10 [get_ports io_gpio1_port_25]
set_property PACKAGE_PIN V10 [get_ports io_gpio1_port_26]
set_property PACKAGE_PIN L15 [get_ports io_gpio1_port_27]
set_property PULLUP true [get_ports io_gpio1_port_25]
set_property SLEW SLOW [get_ports io_gpio1_port_26]
set_property PULLUP true [get_ports io_gpio1_port_26]

set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_25]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_26]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_27]


#usb host
create_clock -period 50.000 -name usb_host_utmi_clk [get_pins system/usb_host_clk_gen/utmi_clk_reg_o_reg/Q]
create_clock -period 12.0 -name usb_host_tx_line_clk [get_pins system/usb_host_clk_gen/tx_clk_reg_o_reg/Q]
create_clock -period 12.0 -name usb_host_rx_line_clk [get_pins system/usb_host_clk_gen/rx_clk_reg_o_reg/Q]
set_property PACKAGE_PIN H22 [get_ports io_gpio1_port_28]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_28]
set_property PACKAGE_PIN J22 [get_ports io_gpio1_port_29]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_29]


#usb device
create_clock -period 50.000 -name usb_device_utmi_clk [get_pins system/usb_device_clk_gen/utmi_clk_reg_o_reg/Q]
create_clock -period 12.0 -name usb_device_tx_line_clk [get_pins system/usb_device_clk_gen/tx_clk_reg_o_reg/Q]
create_clock -period 12.0 -name usb_device_rx_line_clk [get_pins system/usb_device_clk_gen/rx_clk_reg_o_reg/Q]
set_property PACKAGE_PIN G22 [get_ports io_gpio1_port_30]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_30]
set_property PACKAGE_PIN G21 [get_ports io_gpio1_port_31]
set_property IOSTANDARD LVCMOS33 [get_ports io_gpio1_port_31]





#ddr3 pin map constrain
#source ddr3_pin.xdc

#ddr3 dqs clock
#create_clock -period 10.000 -name ddr_clock_dqs_0_0 [get_ports {io_ddr_pad_mem_dqs_0[0]  }]
#create_clock -period 10.000 -name ddr_clock_dqs_0_1 [get_ports {io_ddr_pad_mem_dqs_0[1]  }]
#create_clock -period 10.000 -name ddr_clock_dqs_1_0 [get_ports {io_ddr_pad_mem_dqs_1[0]  }]
#create_clock -period 10.000 -name ddr_clock_dqs_1_1 [get_ports {io_ddr_pad_mem_dqs_1[1]  }]

##ddr3 ck/ck_n to chip
#create_generated_clock -name ddr_chip_clk -source [get_pins crg/fpga_pll/inst/clk_ddr] -divide_by 1 [get_ports io_ddr_mem_clk] 

##cmd and address pad
#set cac_setup 0.75
#set cac_hold -0.75
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_ras_n]
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_ras_n]
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_cas_n] 
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_cas_n]
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_we_n] 
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_we_n]
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_reset_n] 
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_reset_n]
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_cke] 
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_cke]
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_odt] 
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_odt]
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_cs_n] 
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_cs_n]
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_address[*]] 
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_address[*]]
#set_output_delay -clock ddr_chip_clk -max $cac_setup [get_ports io_ddr_mem_bank[*]] 
#set_output_delay -clock ddr_chip_clk -min $cac_hold  [get_ports io_ddr_mem_bank[*]]

##output dqs pad
#create_generated_clock -name dqs0_0 -source [get_pins crg/fpga_pll/inst/clk_ddr] -edges {1 2 3} -edge_shift {0 0 0} [get_ports {io_ddr_pad_mem_dqs_0[0]}]
#create_generated_clock -name dqs0_1 -source [get_pins crg/fpga_pll/inst/clk_ddr] -edges {1 2 3} -edge_shift {0 0 0} [get_ports {io_ddr_pad_mem_dqs_0[1]}]
#create_generated_clock -name dqs1_0 -source [get_pins crg/fpga_pll/inst/clk_ddr] -edges {1 2 3} -edge_shift {0 0 0} [get_ports {io_ddr_pad_mem_dqs_1[0]}]
#create_generated_clock -name dqs1_1 -source [get_pins crg/fpga_pll/inst/clk_ddr] -edges {1 2 3} -edge_shift {0 0 0} [get_ports {io_ddr_pad_mem_dqs_1[1]}]

##output dq/dm pad
#set dq2dqs_out_rise_setup 0.25
#set dq2dqs_out_fall_setup 0.4
#set dq2dqs_out_rise_hold -0.15
#set dq2dqs_out_fall_hold -0.12
#set_output_delay -clock dqs0_0 -max $dq2dqs_out_rise_setup -rise [get_ports io_ddr_pad_mem_data_0[*]]
#set_output_delay -clock dqs0_0 -max $dq2dqs_out_fall_setup -fall [get_ports io_ddr_pad_mem_data_0[*]]
#set_output_delay -clock dqs0_0 -min $dq2dqs_out_rise_hold  -rise [get_ports io_ddr_pad_mem_data_0[*]]
#set_output_delay -clock dqs0_0 -min $dq2dqs_out_fall_hold  -fall [get_ports io_ddr_pad_mem_data_0[*]]
#set_output_delay -clock dqs1_0 -max $dq2dqs_out_rise_setup -rise [get_ports io_ddr_pad_mem_data_1[*]]
#set_output_delay -clock dqs1_0 -max $dq2dqs_out_fall_setup -fall [get_ports io_ddr_pad_mem_data_1[*]]
#set_output_delay -clock dqs1_0 -min $dq2dqs_out_rise_hold  -rise [get_ports io_ddr_pad_mem_data_1[*]]
#set_output_delay -clock dqs1_0 -min $dq2dqs_out_fall_hold  -fall [get_ports io_ddr_pad_mem_data_1[*]]

#set_output_delay -clock dqs0_0 -max $dq2dqs_out_rise_setup -rise [get_ports io_ddr_pad_mem_dm_0[*]]
#set_output_delay -clock dqs0_0 -max $dq2dqs_out_fall_setup -fall [get_ports io_ddr_pad_mem_dm_0[*]]
#set_output_delay -clock dqs0_0 -min $dq2dqs_out_rise_hold  -rise [get_ports io_ddr_pad_mem_dm_0[*]]
#set_output_delay -clock dqs0_0 -min $dq2dqs_out_fall_hold  -fall [get_ports io_ddr_pad_mem_dm_0[*]]
#set_output_delay -clock dqs1_0 -max $dq2dqs_out_rise_setup -rise [get_ports io_ddr_pad_mem_dm_1[*]]
#set_output_delay -clock dqs1_0 -max $dq2dqs_out_fall_setup -fall [get_ports io_ddr_pad_mem_dm_1[*]]
#set_output_delay -clock dqs1_0 -min $dq2dqs_out_rise_hold  -rise [get_ports io_ddr_pad_mem_dm_1[*]]
#set_output_delay -clock dqs1_0 -min $dq2dqs_out_fall_hold  -fall [get_ports io_ddr_pad_mem_dm_1[*]]


##input dq pad
#set dq2dqs_in_rise_setup 0.4
#set dq2dqs_in_fall_setup 0.35
#set dq2dqs_in_rise_hold -0.4
#set dq2dqs_in_fall_hold -0.35
#set_input_delay -clock dqs0_0 -max $dq2dqs_in_rise_setup [get_ports io_ddr_pad_mem_data_0[*]]
#set_input_delay -clock dqs0_0 -max $dq2dqs_in_fall_setup -clock_fall [get_ports io_ddr_pad_mem_data_0[*]]
#set_input_delay -clock dqs0_0 -min $dq2dqs_in_rise_hold  [get_ports io_ddr_pad_mem_data_0[*]]
#set_input_delay -clock dqs0_0 -min $dq2dqs_in_fall_hold  -clock_fall [get_ports io_ddr_pad_mem_data_0[*]]
#set_input_delay -clock dqs1_0 -max $dq2dqs_in_rise_setup [get_ports io_ddr_pad_mem_data_1[*]]
#set_input_delay -clock dqs1_0 -max $dq2dqs_in_fall_setup -clock_fall [get_ports io_ddr_pad_mem_data_1[*]]
#set_input_delay -clock dqs1_0 -min $dq2dqs_in_rise_hold  [get_ports io_ddr_pad_mem_data_1[*]]
#set_input_delay -clock dqs1_0 -min $dq2dqs_in_fall_hold  -clock_fall [get_ports io_ddr_pad_mem_data_1[*]]




#clock cross asynchronous constrain
#clocks:
#crg/fpga_pll/inst/clk_in1
#clkfbout_clk_wiz_0
#clk_ref_clk_wiz_0
#clk_core_clk_wiz_0
#io_clock_diff_sig_p
#io_clock_rtc
#io_jtag_TCK
#set_clock_groups -group clk_ref_clk_wiz_0 -group clk_core_clk_wiz_0 -asynchronous
set_clock_groups -asynchronous \
-group [get_clocks -include_generated_clocks clk_core_clk_wiz_0] \
-group [get_clocks -include_generated_clocks clk_ref_clk_wiz_0] \
-group [get_clocks -include_generated_clocks clk_eth_clk_wiz_0] \
-group [get_clocks -include_generated_clocks clk_ddr_clk_wiz_0] \
-group [get_clocks -include_generated_clocks clk_usb_ref_clk_wiz_0] \
-group [get_clocks -include_generated_clocks jtag_tck] \
-group [get_clocks -include_generated_clocks eth_phy_rx_clk] \
-group [get_clocks -include_generated_clocks usb_host_utmi_clk] \
-group [get_clocks -include_generated_clocks usb_host_tx_line_clk] \
-group [get_clocks -include_generated_clocks usb_host_rx_line_clk] \
-group [get_clocks -include_generated_clocks usb_device_utmi_clk] \
-group [get_clocks -include_generated_clocks usb_device_tx_line_clk] \
-group [get_clocks -include_generated_clocks usb_device_rx_line_clk]




#-group [get_clocks {ddr_clock_dqs_0_0 ddr_clock_dqs_0_1 ddr_clock_dqs_1_0 ddr_clock_dqs_1_1}]


#set_clock_groups #-group [get_clocks -include_generated_clocks clk_eth_clk_wiz_0] #-group [get_clocks -include_generated_clocks eth_phy_tx_clk] #-logically_exclusive


set_property INTERNAL_VREF 0.75 [get_iobanks 34]
