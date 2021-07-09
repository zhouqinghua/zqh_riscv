#=======================================================================
# UCB VLSI FLOW: Makefile for riscv-bmarks
#-----------------------------------------------------------------------
# Yunsup Lee (yunsup@cs.berkeley.edu)
#

#link_file=test.ld
link_file=test_sram.ld
main_mem_base = 0x80000000
ifeq ($(link_file),test_sram.ld)
    main_mem_base = 0x40002000
endif
ifeq ($(link_file),test_flash.ld)
    main_mem_base = 0x40002000
endif

print_use_uart=0
def_print_use_uart=
ifeq ($(print_use_uart),1)
    def_print_use_uart=-DPRINT_USE_UART=1
endif

#impliment mode: sim/fpga
imp_mode=sim
def_imp_mode=
ifeq ($(imp_mode),sim)
    def_imp_mode=-DIMP_MODE_SIM=1
endif

XLEN ?= 64

default: all

src_dir = .

instname = riscv-bmarks
instbasedir = $(UCB_VLSI_HOME)/install

#--------------------------------------------------------------------
# Sources
#--------------------------------------------------------------------

bmarks = \
	zqh_test0 \

#--------------------------------------------------------------------
# Build rules
#--------------------------------------------------------------------

#zqh add
MARCH ?= rv64gc
#MARCH ?= rv64g
#MARCH ?= rv64imafdc #same as rv64gc
#MARCH ?= rv32imafdc #same as rv32gc
#MARCH ?= rv32imafd #no rvc
#MARCH ?= rv64imafd #same as rv64g
#MARCH ?= rv64iafdc #no mul/div

RISCV_PREFIX ?= riscv$(XLEN)-unknown-elf-
RISCV_GCC ?= $(RISCV_PREFIX)gcc
RISCV_GCC_OPTS ?= -DPREALLOCATE=1 -DMAIN_MEM_BASE=$(main_mem_base) $(def_print_use_uart) $(def_imp_mode) -mcmodel=medany -static -std=gnu99 -O1 -ffast-math -fno-common -fno-builtin-printf -march=$(MARCH) -g
RISCV_LINK ?= $(RISCV_GCC) -T $(src_dir)/common/$(link_file) $(incs)
RISCV_LINK_OPTS ?= -static -nostdlib -nostartfiles -lm -lgcc -T $(src_dir)/common/$(link_file) -march=$(MARCH)
#zqh old RISCV_OBJDUMP ?= $(RISCV_PREFIX)objdump --disassemble-all --disassemble-zeroes --section=.text --section=.text.startup --section=.data
RISCV_OBJDUMP ?= $(RISCV_PREFIX)objdump -S --disassemble-all --disassemble-zeroes
RISCV_SIM ?= spike --isa=rv$(XLEN)gc

incs  += -I$(src_dir)/../env -I$(src_dir)/common -I$(src_dir)/zqh_common $(addprefix -I$(src_dir)/, $(bmarks))
objs  :=

define compile_template
$(1).riscv: $(wildcard $(src_dir)/$(1)/*) $(wildcard $(src_dir)/common/*) $(wildcard $(src_dir)/zqh_common/*)
	$$(RISCV_GCC) $$(incs) $$(RISCV_GCC_OPTS) -o $$@ $(wildcard $(src_dir)/$(1)/*.c) $(wildcard $(src_dir)/common/*.c) $(wildcard $(src_dir)/common/*.S) $$(RISCV_LINK_OPTS)
endef

$(foreach bmark,$(bmarks),$(eval $(call compile_template,$(bmark))))

#------------------------------------------------------------
# Build and run benchmarks on riscv simulator

bmarks_riscv_bin  = $(addsuffix .riscv,  $(bmarks))
bmarks_riscv_dump = $(addsuffix .riscv.dump, $(bmarks))
bmarks_riscv_out  = $(addsuffix .riscv.out,  $(bmarks))

$(bmarks_riscv_dump): %.riscv.dump: %.riscv
	$(RISCV_OBJDUMP) $< > $@

$(bmarks_riscv_out): %.riscv.out: %.riscv
	$(RISCV_SIM) $< > $@

riscv: $(bmarks_riscv_dump)
run: $(bmarks_riscv_out)

junk += $(bmarks_riscv_bin) $(bmarks_riscv_dump) $(bmarks_riscv_hex) $(bmarks_riscv_out)

#------------------------------------------------------------
# Default

all: riscv

#------------------------------------------------------------
# Install

date_suffix = $(shell date +%Y-%m-%d_%H-%M)
install_dir = $(instbasedir)/$(instname)-$(date_suffix)
latest_install = $(shell ls -1 -d $(instbasedir)/$(instname)* | tail -n 1)

install:
	mkdir $(install_dir)
	cp -r $(bmarks_riscv_bin) $(bmarks_riscv_dump) $(install_dir)

install-link:
	rm -rf $(instbasedir)/$(instname)
	ln -s $(latest_install) $(instbasedir)/$(instname)

#------------------------------------------------------------
# Clean up

clean:
	rm -rf $(objs) $(junk)
