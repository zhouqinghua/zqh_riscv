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
    setStats(1);

    uint32_t do_tranning = 0;

    //
    //ddr mc test
    //{{{
    printf("ddr_mc test start\n");
    if (do_tranning) {
        //training WR_DQ, wr_dqs_delay = 0x00, wr_dq_delay = ?, rd_dqs_delay = 0x40
        printf("ddr training WR_DQ delay\n");
        ddr3_training_delay(DDR_TN_WR_DQ, 0x00, 0x00, 0x40);

        printf("ddr training RD_DQS delay\n");
        //training RD_DQS, wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = ?
        ddr3_training_delay(DDR_TN_RD_DQS, 0x00, 0x40, 0x00);
    }

    //best training resault
    //dll on mode:
    //wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = 0x40
    //dll off mode:
    //wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = 0xc8


    printf("ddr memory read write check\n");
    //ddr_phy_delay_cfg(0x00, 0x40, 0x40);//dll on
    //ddr_phy_delay_cfg(0x00, 0x40, 0xc8);//dll off
    //delay_ms(500);

    uint32_t ddr_mem_check_size;
    ddr_mem_check_size = pow(2,8);//1GB max
    if (ddr_wr_rd_check(ddr_mem_check_size, 1)) {
        printf("ddr memory check(%0d) pass\n", ddr_mem_check_size);
    }
    else {
        printf("ddr memory check(%0d) fail\n", ddr_mem_check_size);
    }

    printf("ddr_mc test end\n");
    //while(1);
    //}}}

    setStats(0);
    return 0;
}
