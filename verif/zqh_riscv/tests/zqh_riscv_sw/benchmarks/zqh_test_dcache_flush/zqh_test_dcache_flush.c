#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"
#include "zqh_common_atomic.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();

    volatile uint8_t * c_addr = TL_SRAM_MEM_BASE;
    uint32_t cnt;
    printf_zqh("dcache flush test start\n");

    cnt = 8;
    //modify cache address
    for (int i = 0; i < cnt; i++) {
        *(c_addr + i) = i;
        printf_zqh("pre write[%0d] = 0x%x\n", i, i);
    }

    //flush dcache address
    for (int i = 0; i < cnt; i++) {
        dc_l1_flush(c_addr + i);
        printf_zqh("dcache flush 0x%x done\n", c_addr + i);
    }

    for (int i = 0; i < cnt; i++) {
        *(c_addr + i) = i;
        printf_zqh("post read[%0d] = 0x%x\n", i, *(c_addr + i));
    }

    printf_zqh("dcache flush test end\n");

    //post_stop(0x01);
    return 0;
}
