onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate /Testbench/DUT/S
add wave -noupdate /Testbench/DUT/C
add wave -noupdate /Testbench/DUT/Vcc
add wave -noupdate /Testbench/DUT/HOLD_DQ3
add wave -noupdate /Testbench/DUT/Vpp_W_DQ2
add wave -noupdate /Testbench/DUT/DQ1
add wave -noupdate /Testbench/DUT/DQ0
add wave -noupdate -radix ascii /Testbench/DUT/cmdRecName
add wave -noupdate -radix hexadecimal /Testbench/DUT/ck_count
add wave -noupdate -radix ascii /Testbench/DUT/protocol
add wave -noupdate -radix ascii /Testbench/DUT/prog/oldOperation
add wave -noupdate -radix ascii /Testbench/DUT/prog/operation
add wave -noupdate -radix ascii /Testbench/DUT/cmdRecName
add wave -noupdate -radix hexadecimal /Testbench/DUT/ck_count
add wave -noupdate -radix ascii /Testbench/DUT/protocol
add wave -noupdate -radix ascii /Testbench/DUT/prog/oldOperation
add wave -noupdate -radix ascii /Testbench/DUT/prog/operation
add wave -noupdate -radix hexadecimal /Testbench/DUT/cmd
add wave -noupdate /Testbench/DUT/cmdLatched
add wave -noupdate /Testbench/DUT/addrLatched
add wave -noupdate /Testbench/DUT/dataLatched
add wave -noupdate /Testbench/DUT/dummyLatched
add wave -noupdate /Testbench/DUT/codeRecognized
add wave -noupdate /Testbench/DUT/seqRecognized
add wave -noupdate /Testbench/DUT/startCUIdec
add wave -noupdate /Testbench/DUT/sendToBus
add wave -noupdate /Testbench/DUT/read/enable
add wave -noupdate /Testbench/DUT/Debug/x1
add wave -noupdate /Testbench/tasks/send_data/i
add wave -noupdate /Testbench/tasks/send_data/data
add wave -noupdate -radix hexadecimal /Testbench/DUT/data
add wave -noupdate -radix hexadecimal /Testbench/DUT/readAddr
add wave -noupdate -radix hexadecimal /Testbench/DUT/dataOut
add wave -noupdate -radix hexadecimal /Testbench/tasks/num_addr_bytes
add wave -noupdate -radix ascii /Testbench/DUT/latchingMode
add wave -noupdate -radix hexadecimal /Testbench/DUT/addrLatch
add wave -noupdate /Testbench/DUT/iCmd
add wave -noupdate /Testbench/DUT/iAddr
add wave -noupdate /Testbench/DUT/iData
add wave -noupdate /Testbench/DUT/iDummy
add wave -noupdate /Testbench/DUT/busy
add wave -noupdate /Testbench/DUT/die_active
add wave -noupdate /Testbench/DUT/rdeasystacken
add wave -noupdate /Testbench/DUT/lock/sectLockReg
add wave -noupdate -radix hexadecimal /Testbench/DUT/addr
add wave -noupdate /Testbench/DUT/Debug/x4
add wave -noupdate /Testbench/DUT/lock/nSector
add wave -noupdate /Testbench/DUT/lock/nLockedSector
add wave -noupdate /Testbench/DUT/lock/nLockedSector
add wave -noupdate /Testbench/DUT/lock/lock_by_SR
add wave -noupdate /Testbench/DUT/lock/LockReg_WL
add wave -noupdate /Testbench/DUT/lock/LockReg_LD
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {314588705259 fs} 0} {{Cursor 2} {1956793333 fs} 0}
quietly wave cursor active 2
configure wave -namecolwidth 284
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 3
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ns
update
WaveRestoreZoom {596568909 fs} {3256779246 fs}
