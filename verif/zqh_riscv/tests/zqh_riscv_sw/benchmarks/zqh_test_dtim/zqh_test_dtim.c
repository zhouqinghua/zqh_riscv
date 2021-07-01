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

    volatile uint32_t * lock_ptr = TL_SRAM_MEM_BASE; //tl_sram
    volatile char * dtim_addr = DTIM_BASE;
    volatile uint32_t * dtim_amo_addr = DTIM_BASE + 8;
    volatile uint32_t * dtim_io_amo_addr = DTIM_IO_BASE + 128;
    int cnt0;
    cnt0 = 5;

    printf_zqh("dtim test start\n");

    if (hart_id == 0) {
        *lock_ptr = 0;
    }
    delay_zqh(100);
    *dtim_addr = 0;
    *dtim_amo_addr = 0x55555500;
    *dtim_io_amo_addr = 0xaaaaaa00;
    for (int i = 0; i < cnt0; i++) {
        swap32_get_lock(lock_ptr);
        printf_zqh("get lock\n");

        (*(dtim_addr))++;
        printf_zqh("dtim_addr[%d] = 0x%x\n", i, *(dtim_addr));

        amo32_add(dtim_amo_addr, 1);
        printf_zqh("dtim_amo_addr[%d] = 0x%x\n", i, *(dtim_amo_addr));

        amo32_add(dtim_io_amo_addr, 1);
        printf_zqh("dtim_io_amo_addr[%d] = 0x%x\n", i, *(dtim_io_amo_addr));

        swap32_put_lock(lock_ptr);
        delay_zqh(20);
    }
    delay_zqh(200);
    printf_zqh("dtim test end\n");

    //post_stop(0x01);
    return 0;
}
