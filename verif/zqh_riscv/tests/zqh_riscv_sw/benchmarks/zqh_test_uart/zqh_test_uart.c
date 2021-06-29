#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"
#include "zqh_common_uart.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();

    //gpio hw iof enable
    *GPIO_IOF_EN(0) = *GPIO_IOF_EN(0) | 0x3;

    //uart0 test
    //{{{
    printf_zqh("uart test start\n");
    char tx_buf[] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07};
    //char tx_buf[] = {0x00, 0x01, 0x02, 0x03};
    //char tx_buf[] = "zqh uart test\n";
    uart0_tx(tx_buf, sizeof(tx_buf));
    //tx loopback to rx
    for (int i = 0; i < sizeof(tx_buf); i++) {
        printf_zqh("uart0 rx %x\n", uart0_rx_stall());
    }
    //delay_zqh(7000);
    printf_zqh("uart test end\n");
    //}}}

    post_stop(0x01);
    return 0;
}
