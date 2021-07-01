#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"
#include "zqh_common_eth.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();
    //gpio hw iof enable
    *GPIO_IOF_EN(1) = *GPIO_IOF_EN(1) | 0x0fffffff;
    delay_ms(100);

    *CRG_CTRL_RESET_CFG = *CRG_CTRL_RESET_CFG & 0xffffffdf; //reset eth
    delay_ms(100);
    *CRG_CTRL_RESET_CFG = *CRG_CTRL_RESET_CFG | 0x20; //dereset eth
    delay_ms(100);


    //
    //mac test
    //{{{
    printf_zqh("mac test start\n");
    eth_mac_tx_rx_test();
    printf_zqh("mac test end\n");
    //}}}

    //post_stop(0x01);
    return 0;
}
