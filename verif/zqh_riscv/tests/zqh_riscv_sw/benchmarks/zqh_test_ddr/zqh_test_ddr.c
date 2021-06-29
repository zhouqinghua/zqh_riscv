#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"
#include "zqh_common_ddr.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();

    //
    //ddr mc test
    //{{{
    printf_zqh("ddr_mc test start\n");
    //training WR_DQ, wr_dqs_delay = 0x00, wr_dq_delay = ?, rd_dqs_delay = 0x40
    printf_zqh("ddr training WR_DQ delay\n");
    ddr3_training_delay(DDR_TN_WR_DQ, 0x00, 0x00, 0x40);

    printf_zqh("ddr training RD_DQS delay\n");
    //training RD_DQS, wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = ?
    ddr3_training_delay(DDR_TN_RD_DQS, 0x00, 0x40, 0x00);

    //best training resault
    //dll on mode:
    //wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = 0x40
    //dll off mode:
    //wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = 0xc8


    printf_zqh("ddr memory read write check\n");
    //ddr_phy_delay_cfg(0x00, 0x40, 0x40);//dll on
    //ddr_phy_delay_cfg(0x00, 0x40, 0xc8);//dll off
    //delay_ms(500);

    uint32_t ddr_mem_check_size;
    ddr_mem_check_size = pow(2,20);//1GB max
    if (ddr_wr_rd_check(ddr_mem_check_size, 0)) {
        printf_zqh("ddr memory check(%0d) pass\n", ddr_mem_check_size);
    }
    else {
        printf_zqh("ddr memory check(%0d) fail\n", ddr_mem_check_size);
    }

    printf_zqh("ddr_mc test end\n");
    //while(1);
    //}}}

    post_stop(0x01);
    return 0;
}
