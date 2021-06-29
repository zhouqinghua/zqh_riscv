puts "=========================================================================="

remove_design -all

set MY_DESIGN zqh_subsystem_s3
analyze -f verilog ../verif/zqh_riscv/sim/py2rtl/zqh_cfg__s3__no_dcache__icache_1way_16set__data_scratchpad_1k_zqh_test_harness.v
elaborate $MY_DESIGN
current_design $MY_DESIGN

set clk_name clock
set rst_name reset

# Define system clock period
set clk_period 150
create_clock -period $clk_period -name clock [get_ports $clk_name]

# Apply default drive strengths and typical loads
# for I/O ports
set_load 1.5 [all_outputs]
set_drive 1 [all_inputs]
#set_driving_cell -lib_cell IV [all_inputs]
set_drive 0 $clk_name

# Apply default timing constraints for modules
set_input_delay 1.2 [all_inputs] -clock $clk_name
set_output_delay 1.5 [all_outputs] -clock $clk_name
set_clock_uncertainty -setup 0.45 $clk_name

# Set operating conditions
#set_operating_conditions WCCOM

# Turn on auto wire load selection
# (library must support this feature)
#set_wire_load_model -name "10x10"
set auto_wire_load_selection true

#set_dont_touch_network [get_clocks $clk_name]
set_ideal_network [get_ports $rst_name]
#set_dont_touch [get_designs ZQH_MulDiv]

set_max_area 0 

compile
#compile_ultra -retime

redirect   -tee   -file ./output/${MY_DESIGN}_check.log {check_design}
redirect   -tee   -file ./output/${MY_DESIGN}_timing.log {report_timing -max_paths 5}
#report_timing
redirect   -tee   -file ./output/${MY_DESIGN}_area.log {report_area}
#report_area

write_file -hierarchy -format verilog -output ./output/$MY_DESIGN.v
