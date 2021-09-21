export PROJ_ROOT=$(shell pwd)
export RISCV=$(shell pwd)/output
$(shell mkdir -p $(RISCV))
BIN_PATH:=$(addprefix $(RISCV)/bin:, $(PATH))
export PATH=$(BIN_PATH)
ncore=$(shell echo $$(($(shell nproc)/2)))

#all submodule update
subm_update:
	git submodule update --init --recursive

#build all tools
build:
	cd rocket-tools && ./build.sh && ./build-rv32ima.sh
