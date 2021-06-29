
net_sim = off
file_list = -f ./tb_all.f
cmp_net_opt = 
ifeq ($(net_sim),on)
    file_list+ = -f ./dut_netlist.f
    cmp_net_opt += +nospecify +notimingcheck
endif


cmp_macro = CLOCK_PERIOD=5.0 U_DLY_IN=0.1 U_DLY_OUT=0.1 VERBOSE
vprint = off
ifeq ($(vprint),on)
    cmp_macro += VPRINT_COND
endif
vassert = on
ifeq ($(vassert),on)
    cmp_macro += VASSERT_COND
endif
vcover = on
ifeq ($(vcover),on)
    cmp_macro += VCOVER_COND
endif
wave = fsdb
ifeq ($(wave),fsdb)
    cmp_macro += FSDB_ON
endif
ifeq ($(wave),vcd)
    cmp_macro += VCD_ON
endif
ddr_log_print = off
ifeq ($(ddr_log_print),on)
    cmp_macro += DDR_LOG_PRINT
endif
ddr_stop_on_error = on
ifeq ($(ddr_stop_on_error),on)
    cmp_macro += DDR_STOP_ON_ERROR
endif

link_file=test_sram.ld
print_use_uart=0


fesvr=off
CMP_MACRO_VCS = $(addprefix +define+, $(cmp_macro))
CMP_MACRO_IVL = $(addprefix -D , $(cmp_macro))
CMP_MACRO_NLT = +define+U_DLY_IN=0.1 +define+U_DLY_OUT=0.1 $(CMP_MACRO_VCS)

incdir = \
    ../../common/vips/N25Q064A13E_VG12 \
	../../common/vips/DDR3_model
CMP_INCDIR_VCS = $(addprefix +incdir+, $(incdir))
CMP_INCDIR_IVL = $(addprefix -I , $(incdir))


#initreg =
#initreg = random
initreg =config+random_config_file.v
CMP_INITREG = 
SIM_INITREG = 
ifneq ($(initreg), )
    CMP_INITREG = +vcs+initreg+$(initreg)
    SIM_INITREG = +vcs+initreg+$(initreg)
endif


ts = 1ns/10ps
CMP_TS_VCS = -timescale=$(ts)
CMP_TS_IVL = +timescale+$(ts) -dname


cmp_log = ./log/cmp.log
simv_out = ./simv


PLI_OPTS = -P $(NOVAS_INST_DIR)/share/PLI/VCS/$(PLATFORM)/novas.tab \
            $(NOVAS_INST_DIR)/share/PLI/VCS/$(PLATFORM)/pli.a


fesvr_csrc_path = ../../common/resources/csrc
fesvr_vsrc_path = ../../common/resources/vsrc

FESVR_CSRCS = \
    $(fesvr_csrc_path)/SimDTM.cc

socket_dtm = off
socket_bit_mode=off

#ac: abstract commond
#sba: means system bus access
dtm_mode = ac
ifeq ($(socket_dtm),on)
	ifeq ($(socket_bit_mode), on)
        FESVR_CSRCS += \
            $(fesvr_csrc_path)/remote_bitbang.cc \
		    $(fesvr_csrc_path)/SimJTAG.cc
	else
        FESVR_CSRCS += \
            $(fesvr_csrc_path)/zqh_remote_xactionbang.cc \
		    $(fesvr_csrc_path)/zqh_sim_xaction_socket_jtag.cc
	endif
else
	ifeq ($(dtm_mode), sba)
        FESVR_CSRCS += $(fesvr_csrc_path)/zqh_sim_dtm2jtag_sba.cc
	else
        FESVR_CSRCS += $(fesvr_csrc_path)/zqh_sim_dtm2jtag.cc
	endif
endif

FESVR_VSRCS = 
    #$(fesvr_vsrc_path)/SimDTM.v
    #$(fesvr_vsrc_path)/SimJTAG.v

FESVR_CC_OPTS = \
    +vc+list -CC "-I$(VCS_HOME)/include" \
    -CC "-I$(RISCV)/include" \
    -CC "-std=c++11" \
    -CC "-Wl,-rpath,$(RISCV)/lib" \
    $(RISCV)/lib/libfesvr.so \
    $(FESVR_VSRCS) $(FESVR_CSRCS)



CMP_OPTS_VCS = \
    -notice -line \
    +lint=all,noVCDE,noONGS,noUI,noNS,noVNGS,noIWU,noMSIVD,noZERO \
   	-error=noIOPCWM \
    +v2k +vcs+lic+wait \
    -sverilog \
    $(CMP_TS_VCS) \
    $(CMP_MACRO_VCS) \
    $(CMP_INCDIR_VCS) \
    $(file_list) \
    $(PLI_OPTS) \
    $(CMP_INITREG) \
    $(cmp_net_opt) \
    -l $(cmp_log)

CMP_OPTS_IVL = \
    -g2012 \
    $(CMP_TS_IVL) \
    $(CMP_MACRO_IVL) \
    $(CMP_INCDIR_IVL) \
    $(file_list) \
    $(cmp_net_opt)

ifeq ($(fesvr),on)
    CMP_OPTS_VCS += $(FESVR_CC_OPTS)
    CMP_OPTS_IVL += $(FESVR_CC_OPTS)
endif

fesvr_elf_nm=fesvr
socket_port=5900
fesvr_cmp_cmd = \
    g++ -o $(fesvr_elf_nm) \
    -std=c++11 \
    -I$(VCS_HOME)/include \
    -I$(RISCV)/include \
    -Wl,-rpath,$(RISCV)/lib
ifeq ($(socket_bit_mode),on)
    fesvr_cmp_cmd += \
        $(fesvr_csrc_path)/zqh_dmi2jtag_bit_client.cc
else
    fesvr_cmp_cmd += \
        $(fesvr_csrc_path)/zqh_dmi2jtag_xaction_client.cc
endif
fesvr_cmp_cmd += \
    -L$(RISCV)/lib \
    -lfesvr \
    -lpthread 



#gcc related options
gcc_xlen = 64#32/64
gcc_isa =gc#gc/g/imafdc/imafd/iafdc
gcc_march = rv$(gcc_xlen)$(gcc_isa)


sw_root_dir = ../tests/zqh_riscv_sw
sw_tc_grp_dir = benchmarks#isa/benchmarks
sw_tc_dir = zqh_test0#zqh_test0/rv64ui
sw_tc = p-add
ifeq ($(sw_tc_grp_dir),isa)
    sw_tc_elf = $(sw_tc_dir)-$(sw_tc)
else
    sw_tc_elf = $(sw_tc_dir).riscv
endif
sw_elf_fn = ./log/$(sw_tc_dir)/$(sw_tc_elf)
sw_hex_fn = ./log/$(sw_tc_dir)/$(sw_tc_elf).hex


seed = 1
test = zqh_riscv_sanity_test
wave_fn = ./wave/$(test)_$(sw_tc_elf)_$(seed).$(wave)
simv_log = ./log/$(test)_$(sw_tc_elf)_$(seed).log

#SIM_CC_PLUS = +permissive -q +ntb_random_seed_automatic +permissive-off +permissive +verbose +fsdbfile=./log/$(sw_tc_dir)/$(sw_tc_elf).fsdb +max-cycles=$(timeout_cycles) +permissive-off

timeout_cycles = 10000000
dump_start = 0
debug_level = ERROR
wave_dump = 1
boot_mode = 1#0: flash xip, 1: sram memory, 2: ddr memory, 3: debug
uart_lb = 0#0: no loopback, 1: loopback
eth_phy_lb = 0#0: no loopback, 1: loopback
SIM_PLUS = \
    +ntb_random_seed=$(seed) +zqh_debug_level=$(debug_level) \
    +wavefile=$(wave_fn) +wave_dump=$(wave_dump) \
    +max-cycles=$(timeout_cycles) +dump-start=$(dump_start) +zqh_test=$(test) \
   	+zqh_cpu_instr_init_file=$(sw_hex_fn).fix +zqh_cpu_data_init_file=none \
	+socket_port=$(socket_port) +boot_mode=$(boot_mode) +uart_lb=$(uart_lb) +eth_phy_lb=$(eth_phy_lb)
maxfail = 10
SIM_OPTS_VCS = $(SIM_INITREG) -assert global_finish_maxfail=$(maxfail) -assert nopostproc 
SIM_OPTS_IVL =  


# -O  option will disable python script's assert() check
#  this will improve runtime performanc
gen_rtl_bin = python3 /home/zqh/risc-v/phgl/phgl_generator.py

#core_e1
#gen_py = ../../../src/zqh_test_harness_e1/zqh_test_harness_e1_ut.py
#gen_cfgfile = ../../../src/zqh_cfgs/zqh_cfg_e1.py
#gen_cfg = zqh_cfg_e1__itim_8k__dtim_8k__lsu_num_flights_4
##gen_cfg = zqh_cfg_e1__num_cores_2__itim_8k__dtim_8k__lsu_num_flights_4
##gen_cfg = zqh_cfg_e1__num_cores_4__itim_8k__dtim_8k__lsu_num_flights_4
##gen_cfg = zqh_cfg_e1__xlen_32__itim_8k__dtim_8k__lsu_num_flights_4

#core_r1
gen_py = ../../../src/zqh_test_harness_r1/zqh_test_harness_r1_ut.py
gen_cfgfile = ../../../src/zqh_cfgs/zqh_cfg_r1.py
#gen_cfg = zqh_cfg_r1__basic
#gen_cfg = zqh_cfg_r1__no_ddr
#gen_cfg = zqh_cfg_r1__no_ddr__no_eth
gen_cfg = zqh_cfg_r1__fpga_min
#gen_cfg = zqh_cfg_r1__lsu_num_flights_4
#gen_cfg = zqh_cfg_r1__itim_8k__dtim_8k__lsu_num_flights_4
#gen_cfg = zqh_cfg_r1__num_cores_2__itim_8k__dtim_8k__lsu_num_flights_4
#gen_cfg = zqh_cfg_r1__num_cores_4__itim_8k__dtim_8k__lsu_num_flights_4
#gen_cfg = zqh_cfg_r1__xlen_32__itim_8k__dtim_8k__lsu_num_flights_4

gen_m = zqh_test_harness_ut
gen_dir = ./py2rtl


#nlint_top = zqh_test_harness
nlint_top = zqh_full_chip_e1
#22079 Constant Conditional Expression 
#22211 Signal Stuck at Logic 1 
#22213 Signal Stuck at Logic 0 
#25001 Signal with No Driver
#25003 Signal with No Load 
#22117 Synchronous or Asynchronous Reset Detected
#25009 Signal with Heavy Fan-out Loading
#22165 Signal Driven by Constant
#tmp nlint_disable_r = \
#tmp     -r 22079 \
#tmp     -r 22211 \
#tmp     -r 22213 \
#tmp     -r 25001 \
#tmp     -r 25003 \
#tmp     -r 22117 \
#tmp     -r 25009 \
#tmp     -r 22165

gen_rtl:
	$(gen_rtl_bin) -i $(gen_py) -o $(gen_dir) -m $(gen_m) --cfgfile $(gen_cfgfile) --cfg $(gen_cfg)


cmp_cmd =
sim_cmd =
ifeq ($(fesvr)_$(socket_dtm),on_on)
	#compiler fesvr first
    cmp_cmd += $(fesvr_cmp_cmd) ; 
    sim_cmd += ./$(fesvr_elf_nm) $(sw_elf_fn) $(socket_port) & 
endif


simulator = vcs#vcs/iverilog
ifeq ($(simulator),vcs)
    cmp_cmd += vcs -full64 $(CMP_OPTS_VCS) -o $(simv_out)_vcs -debug_pp
    sim_cmd += $(simv_out)_vcs +permissive -l $(simv_log) $(SIM_PLUS) $(SIM_OPTS_VCS) +permissive-off $(sw_elf_fn)
else
    ivl_cmp_cmd = iverilog $(CMP_OPTS_IVL) -o $(simv_out)_ivl 2>&1
    cmp_cmd += @echo $(ivl_cmp_cmd) > $(cmp_log); $(ivl_cmp_cmd) | tee -a $(cmp_log)
    sim_cmd += vvp -l $(simv_log) $(simv_out)_ivl +permissive $(SIM_PLUS) $(SIM_OPTS_IVL) +permissive-off $(sw_elf_fn)
endif

cmp:
	$(cmp_cmd)

sw:
	test -d ./log/$(sw_tc_dir) || mkdir ./log/$(sw_tc_dir)
	cd ./log; make -C $(sw_tc_dir) -f ../../$(sw_root_dir)/$(sw_tc_grp_dir)/Makefile src_dir=../../$(sw_root_dir)/$(sw_tc_grp_dir) bmarks=$(sw_tc_dir) link_file=$(link_file) print_use_uart=$(print_use_uart) XLEN=$(gcc_xlen) MARCH=$(gcc_march) $(sw_tc_elf).dump
	riscv$(gcc_xlen)-unknown-elf-objcopy -O verilog $(sw_elf_fn) $(sw_hex_fn)
	../../scripts/zqh_sw_hex_fix.py --hex_in=$(sw_hex_fn)
	../../scripts/zqh_elf_section_dec.py --elf_in=$(sw_elf_fn)

sim:
	$(sim_cmd)

sw_sim: sw sim

run: cmp sw_sim

fesvr_cmp:
	$(fesvr_cmp_cmd)

all: gen_rtl cmp sw_sim

verdi:
	verdi -nologo $(CMP_OPTS_VCS) -debug_pp 

nlint:
	nLint -gui -sv $(CMP_INCDIR_VCS) -f dut.f -top $(nlint_top) $(CMP_MACRO_NLT) $(nlint_disable_r)

backup:
	tar cvzf /mnt/hgfs/vmware_share/zqh_riscv.tar.gz  ../../../../zqh_riscv/ \
	--exclude=csrc \
	--exclude=log/* \
	--exclude=py2rtl/* \
	--exclude=simv* \
	--exclude=fesvr \
	--exclude=verdiLog \
	--exclude=vfastLog \
	--exclude=novas* \
	--exclude=wave/*

clean:
	rm -rf csrc simv* fesvr csrc ucli.key
