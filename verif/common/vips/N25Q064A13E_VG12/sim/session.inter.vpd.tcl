# Begin_DVE_Session_Save_Info
# DVE view(Wave.1 ) session
# Saved on Thu Jan 24 13:38:48 2013
# Toplevel windows open: 2
# 	TopLevel.1
# 	TopLevel.2
#   Wave.1: 28 signals
# End_DVE_Session_Save_Info

# DVE version: F-2011.12_Full64
# DVE build date: Nov 22 2011 20:55:00


#<Session mode="View" path="/nfs/fm/disks/fm_fpg_n7006/global_work/p72/evillega/DS4/bfm/N25Q/512Mb_1_8V/NU_N25Q512A11E_VG10/sim/session.inter.vpd.tcl" type="Debug">

#<Database>

#</Database>

# DVE View/pane content session: 

# Begin_DVE_Session_Save_Info (Wave.1)
# DVE wave signals session
# Saved on Thu Jan 24 13:38:48 2013
# 28 signals
# End_DVE_Session_Save_Info

# DVE version: F-2011.12_Full64
# DVE build date: Nov 22 2011 20:55:00


#Add ncecessay scopes

gui_set_time_units 1ps
set Group1 Group1
if {[gui_sg_is_group -name Group1]} {
    set Group1 [gui_sg_generate_new_name]
}

gui_sg_addsignal -group "$Group1" { {Sim:Testbench.DUT.any_die_busy} {Sim:Testbench.DUT.current_die_active} {Sim:Testbench.DUT.current_die_busy} {Sim:Testbench.DUT.C} {Sim:Testbench.DUT.S} {Sim:Testbench.DUT.Vcc} {Sim:Testbench.DUT.DQ0} {Sim:Testbench.DUT.DQ1} {Sim:Testbench.DUT.HOLD_DQ3} {Sim:Testbench.DUT.Vpp_W_DQ2} }
set Group2 Group2
if {[gui_sg_is_group -name Group2]} {
    set Group2 [gui_sg_generate_new_name]
}

gui_sg_addsignal -group "$Group2" { {Sim:Testbench.DUT.N25Q_die0.dataOut} {Sim:Testbench.DUT.N25Q_die0.C} {Sim:Testbench.DUT.N25Q_die0.DQ0} {Sim:Testbench.DUT.N25Q_die0.DQ1} {Sim:Testbench.DUT.N25Q_die0.HOLD_DQ3} {Sim:Testbench.DUT.N25Q_die0.S} {Sim:Testbench.DUT.N25Q_die0.Vcc} {Sim:Testbench.DUT.N25Q_die0.Vpp_W_DQ2} {Sim:Testbench.DUT.N25Q_die0.die_active} }
set Group3 Group3
if {[gui_sg_is_group -name Group3]} {
    set Group3 [gui_sg_generate_new_name]
}

gui_sg_addsignal -group "$Group3" { {Sim:Testbench.DUT.N25Q_die1.dataOut} {Sim:Testbench.DUT.N25Q_die1.C} {Sim:Testbench.DUT.N25Q_die1.DQ0} {Sim:Testbench.DUT.N25Q_die1.DQ1} {Sim:Testbench.DUT.N25Q_die1.HOLD_DQ3} {Sim:Testbench.DUT.N25Q_die1.S} {Sim:Testbench.DUT.N25Q_die1.Vcc} {Sim:Testbench.DUT.N25Q_die1.Vpp_W_DQ2} {Sim:Testbench.DUT.N25Q_die1.die_active} }
set Group4 Group4
if {[gui_sg_is_group -name Group4]} {
    set Group4 [gui_sg_generate_new_name]
}

gui_sg_addsignal -group "$Group4" { } 
if {![info exists useOldWindow]} { 
	set useOldWindow true
}
if {$useOldWindow && [string first "Wave" [gui_get_current_window -view]]==0} { 
	set Wave.1 [gui_get_current_window -view] 
} else {
	gui_open_window Wave
set Wave.1 [ gui_get_current_window -view ]
}
set groupExD [gui_get_pref_value -category Wave -key exclusiveSG]
gui_set_pref_value -category Wave -key exclusiveSG -value {false}
set origWaveHeight [gui_get_pref_value -category Wave -key waveRowHeight]
gui_list_set_height -id Wave -height 25
set origGroupCreationState [gui_list_create_group_when_add -wave]
gui_list_create_group_when_add -wave -disable
gui_marker_create -id ${Wave.1} C2 10667584
gui_marker_set_ref -id ${Wave.1}  C1
gui_wv_zoom_timerange -id ${Wave.1} 0 40000000
gui_list_add_group -id ${Wave.1} -after {New Group} [list $Group1]
gui_list_add_group -id ${Wave.1} -after {New Group} [list $Group2]
gui_list_add_group -id ${Wave.1} -after {New Group} [list $Group3]
gui_list_add_group -id ${Wave.1} -after {New Group} [list $Group4]
gui_list_select -id ${Wave.1} {Testbench.DUT.N25Q_die1.dataOut }
gui_seek_criteria -id ${Wave.1} {Any Edge}


gui_set_pref_value -category Wave -key exclusiveSG -value $groupExD
gui_list_set_height -id Wave -height $origWaveHeight
if {$origGroupCreationState} {
	gui_list_create_group_when_add -wave -enable
}
if { $groupExD } {
 gui_msg_report -code DVWW028
}
gui_list_set_filter -id ${Wave.1} -list { {Buffer 1} {Input 1} {Others 1} {Linkage 1} {Output 1} {Parameter 1} {All 1} {Aggregate 1} {Event 1} {Assertion 1} {Constant 1} {Interface 1} {Signal 1} {$unit 1} {Inout 1} {Variable 1} }
gui_list_set_filter -id ${Wave.1} -text {*}
gui_list_set_insertion_bar  -id ${Wave.1} -group $Group3  -item {Testbench.DUT.N25Q_die1.dataOut[7:0]} -position below

gui_marker_move -id ${Wave.1} {C1} 1530000
gui_view_scroll -id ${Wave.1} -vertical -set 118
gui_show_grid -id ${Wave.1} -enable false
#</Session>

