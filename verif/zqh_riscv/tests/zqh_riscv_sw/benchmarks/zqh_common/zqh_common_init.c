#ifndef __ZQH_COMMON_INIT_C
#define __ZQH_COMMON_INIT_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

void zqh_common_csr_cfg() {
    //csr set
    hart_id = read_csr(mhartid);
    support_vm = (read_csr(misa) >> 18) & 1;
    support_user = (read_csr(misa) >> 20) & 1;
    printf("mhartid %x\n", hart_id);

    //set timer
    //test partial write to 8B reg
    *CLINT_MTIMECMP(hart_id) = 0xffffffffffffffff; //set mtimecmp to max value
    printf("CLINT_MTIMECMP_H %x\n", *CLINT_MTIMECMP_H(hart_id));
    printf("CLINT_MTIMECMP_L %x\n", *CLINT_MTIMECMP_L(hart_id));

    //test none exist mmio address access
    *CLINT_MSIP(1) = 0;
    printf("CLINT_MSIP(1) %x\n", *CLINT_MSIP(1));

    //set plic reg
    *PLIC_PRIORITY = 0;
    //*(PLIC_PRIORITY+1) = 1;
    //*(PLIC_PRIORITY+2) = 1;
    //*(PLIC_PRIORITY+3) = 1;
    //*(PLIC_PRIORITY+4) = 1;
    //*(PLIC_PRIORITY+5) = 1;
    //*(PLIC_PRIORITY+6) = 1;
    //*(PLIC_PRIORITY+7) = 1;
    for (int i = 1; i < PLIC_INT_NUM; i++) {
        *(PLIC_PRIORITY+i) = 1;
    }
    *PLIC_THRESHOLD_M(hart_id) = 0;
    if (support_vm) {
        *PLIC_THRESHOLD_S(hart_id) = 0;
    }
    *PLIC_ENABLE_M(hart_id) = 0x00000000;//temp disable plic interrupt
    //*(PLIC_ENABLE_S + hart_id) = 0x00000004;
    //*PLIC_ENABLE_M(hart_id) = 0x00000000;
    if (support_vm) {
        *PLIC_ENABLE_S(hart_id) = 0x00000000;
    }


    //i2c reg set
    *I2C_DIV = 0x80;
    //*I2C_CONTROL = 0x5;//multi master enable, scl_stretch enable
    *I2C_CONTROL = 0x1;//multi master disable, scl_stretch enable
    //*I2C_CFG = 0x11000d;


    //plic interrupt enable
    *PLIC_ENABLE_M(hart_id) = 0xfffffffe;
    //clear all plic interrupt pending bit
    for (int i = 0; i < PLIC_INT_NUM; i++) {
        uint32_t int_id;
        int_id = *PLIC_CLAIM_COMPLETE_M(hart_id);
        printf("plic claim %0d time, int_id = %x\n", i, int_id);
        if (int_id == 0) {
            break;
        }
    }
    write_csr(mip, 0);
    write_csr(mie, MIP_MSIP | MIP_MTIP | MIP_MEIP | MIP_SSIP | MIP_STIP | MIP_SEIP);
    set_csr(mstatus, MSTATUS_MIE | MSTATUS_SIE);

    //counters
    if (support_vm || support_user) {
        write_csr(mcounteren,0);
        printf("mcounteren post initial %x\n", read_csr(mcounteren));
    }

    //hpm counters
    //{{{
    write_csr(mhpmevent3, 0x00 | (0x0000000e << 8));//load/store/amo
    write_csr(mhpmevent4, 0x00 | (0x000001c0 << 8));//branch/jal/jalr
    write_csr(mhpmevent5, 0x02 | (0x00000001 << 8));//ifu refill
    write_csr(mhpmevent6, 0x02 | (0x00000006 << 8));//lsu refill/writeback
    //}}}

}
#endif
