#!/bin/bash

TOP_DIR=$(\cd $(\dirname ${BASH_SOURCE:-$0})/;pwd)

export PROJ_ROOT=${TOP_DIR}
export RISCV=${PROJ_ROOT}/output
echo "PROJ_ROOT = $PROJ_ROOT"
echo "RISCV     = $RISCV"
export PATH=${RISCV}/bin:${PATH}
