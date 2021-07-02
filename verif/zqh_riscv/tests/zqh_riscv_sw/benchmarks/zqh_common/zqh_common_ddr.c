#ifndef __ZQH_COMMON_DDR_C
#define __ZQH_COMMON_DDR_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

int ddr_rd_all1_check() {
    uint32_t * mem_ptr_32 = DDR_MEM_BASE;
    uint32_t rd_data;
    uint64_t size;//byte
    int check_pass;
    size = 64;
    check_pass = 1;

    //flush address
    for (int i = 0; i < size/4; i++) {
        //*DC_L1_FLUSH_IO_ADDR(0) = mem_ptr_32 + i;
        dc_l1_flush(mem_ptr_32 + i);
    }

    //read out, need refill from ddr
    for (int i = 0; i < size/4; i++) {
        rd_data = *(mem_ptr_32 + i);
        printf("ddr_rd_all1_scan[%x] rd data = %8x\n", (mem_ptr_32 + i), rd_data);
        if (rd_data != 0xffffffff) {
            check_pass = 0;
        }
    }
    return check_pass;

}

int ddr_wr_rd_check(uint32_t size, uint32_t print) {
    uint32_t *mem_ptr_32 = DDR_MEM_BASE;
    uint32_t expect_data;
    uint32_t wr_data;
    uint32_t rd_data;
    int check_pass;
    check_pass = 1;

    //modify ddr mem data, one cacheline
    for (uint32_t i = 0; i < size/4; i++) {
        wr_data = 0x5500aa00 + i + (i << 16);
        *(mem_ptr_32 + i) = wr_data;
        if ((i & 0x003fffff) == 0) {
            printf("write address(%8x) = %8x done\n", (mem_ptr_32 + i), wr_data);
        }
    }

    //flush cacheline into DDR
    for (uint32_t i = 0; i < size/4; i++) {
        //*DC_L1_FLUSH_IO_ADDR(0) = mem_ptr_32 + i;
        dc_l1_flush(mem_ptr_32 + i);
        if ((i & 0x003fffff) == 0) {
            printf("flush address(%8x) done\n", mem_ptr_32 + i);
        }
    }

    //read out from ddr and compare
    for (uint32_t i = 0; i < size/4; i++) {
        rd_data = *(mem_ptr_32 + i);
        expect_data = 0x5500aa00 + i + (i << 16);
        if ((i & 0x003fffff) == 0) {
            printf("read address(%8x) = %8x done\n", (mem_ptr_32 + i), rd_data);
        }
        if (print) {
            printf("mem_ptr_32[%x] post rd data = %8x\n", (mem_ptr_32 + i), rd_data);
        }
        if (rd_data != expect_data) {
            check_pass = 0;
        }
    }
    return check_pass;
}

void ddr_phy_delay_cfg(uint32_t wr_dqs_delay, uint32_t wr_dq_delay, uint32_t rd_dqs_delay) {
    for (int slice_cnt = 0; slice_cnt < DDR_MC_SLICE_NUM; slice_cnt++) {
        *DDR_MC_PHY_DS_CFG_REG(4+slice_cnt*8) = (rd_dqs_delay << 16) | (wr_dq_delay << 8) | wr_dqs_delay;
    }
}

#define DDR_TN_WR_DQS 0
#define DDR_TN_WR_DQ 1
#define DDR_TN_RD_DQS 2
void ddr3_training_delay(int mode, int v0, int v1, int v2) {
    uint64_t * ddr_mem_ptr_64 = DDR_MEM_BASE;
    uint32_t * ddr_mem_ptr_32 = DDR_MEM_BASE;
    uint32_t ddr_wr_size = 128;//in byte

    uint32_t wr_dqs_delay = 0;
    uint32_t wr_dq_delay = 0;
    uint32_t rd_dqs_delay = 0;

    for (int dly_cnt = 0; dly_cnt < 32; dly_cnt++) {
        if (mode == DDR_TN_WR_DQS) {
            wr_dqs_delay = dly_cnt << 3;
            wr_dq_delay = v1;
            rd_dqs_delay = v2;
        }
        else if (mode == DDR_TN_WR_DQ) {
            wr_dqs_delay = v0;
            wr_dq_delay = dly_cnt << 3;
            rd_dqs_delay = v2;
        }
        else {
            wr_dqs_delay = v0;
            wr_dq_delay = v1;
            rd_dqs_delay = dly_cnt << 3;
        }

        printf("dly_cnt = %0x\n", dly_cnt);
        printf("wr_dqs_delay = %0x\n", wr_dqs_delay);
        printf("wr_dq_delay = %0x\n", wr_dq_delay);
        printf("rd_dqs_delay = %0x\n", rd_dqs_delay);
        ddr_phy_delay_cfg(wr_dqs_delay, wr_dq_delay, rd_dqs_delay);
        delay_ms(500);

        if (ddr_wr_rd_check(64, 1)) {
            printf("ddr_wr_rd_check pass. rd_dqs_delay = %0x, wr_dq_delay = %0x\n", rd_dqs_delay, wr_dq_delay);
        }
        //if (ddr_rd_all1_check()) {
        //    printf("ddr_rd_all1_check pass. rd_dqs_delay = %0x, wr_dq_delay = %0x\n", rd_dqs_delay, wr_dq_delay);
        //}
    }
}

#endif
