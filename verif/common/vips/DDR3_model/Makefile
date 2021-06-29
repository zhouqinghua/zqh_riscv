file_list = ./ddr3.v ./tb.v

cmp_macro = sg125 den1024Mb x8
CMP_MACRO_VCS = $(addprefix +define+, $(cmp_macro))


cmp_pvalue = MEM_BITS=12
#debug_ddr
debug_ddr = on
ifeq ($(debug_ddr),on)
    cmp_pvalue += DEBUG=1
else
    cmp_pvalue += DEBUG=0
endif
CMP_PVALUE_VCS = $(addprefix -pvalue+, $(cmp_pvalue))

incdir = ./
CMP_INCDIR_VCS = $(addprefix +incdir+, $(incdir))


#initreg = random
initreg =
CMP_INITREG = 
SIM_INITREG = 
ifneq ($(initreg), )
    CMP_INITREG = +vcs+initreg+$(initreg)
    SIM_INITREG = +vcs+initreg+$(initreg)
endif


ts = 1ns/10ps
CMP_TS_VCS = -timescale=$(ts)


cmp_log = ./cmp.log
simv_out = ./simv


PLI_OPTS = -P $(NOVAS_INST_DIR)/share/PLI/VCS/$(PLATFORM)/novas.tab \
            $(NOVAS_INST_DIR)/share/PLI/VCS/$(PLATFORM)/pli.a


CMP_OPTS_VCS = \
    -notice -line \
    +lint=all,noVCDE,noONGS,noUI,noNS,noVNGS \
   	-error=noIOPCWM \
    +v2k +vcs+lic+wait \
    -sverilog \
    $(CMP_TS_VCS) \
    $(CMP_MACRO_VCS) \
	$(CMP_PVALUE_VCS) \
    $(CMP_INCDIR_VCS) \
    $(file_list) \
    $(PLI_OPTS) \
    $(CMP_INITREG) \
    -l $(cmp_log)


seed = 1
simv_log = ./zqh_ddr3.log

SIM_PLUS = \
    +ntb_random_seed=$(seed)
maxfail = 10
SIM_OPTS_VCS = $(SIM_INITREG) -assert global_finish_maxfail=$(maxfail) -assert nopostproc 

cmp_cmd = vcs -full64 $(CMP_OPTS_VCS) -o $(simv_out) -debug_pp
sim_cmd = $(simv_out) +permissive -l $(simv_log) $(SIM_PLUS) $(SIM_OPTS_VCS) +permissive-off $(sw_elf_fn)

cmp:
	$(cmp_cmd)

sim:
	$(sim_cmd)

run: cmp sim

verdi:
	verdi -nologo $(CMP_OPTS_VCS) -debug_pp 

clean:
	rm -rf csrc simv* csrc ucli.key
