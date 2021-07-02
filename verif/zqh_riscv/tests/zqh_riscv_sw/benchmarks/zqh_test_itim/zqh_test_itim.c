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
    setStats(1);

    volatile uint32_t * lock_ptr = TL_SRAM_MEM_BASE; //tl_sram
    volatile char * itim_addr = ITIM_BASE;
    volatile uint32_t * itim_amo_addr = ITIM_BASE + 8;
    volatile uint32_t * itim_io_amo_addr = ITIM_IO_BASE + 128;
    int cnt0;
    cnt0 = 5;

    printf("itim test start\n");

    if (hart_id == 0) {
        *lock_ptr = 0;
    }
    delay_zqh(100);
    *itim_addr = 0;
    *itim_amo_addr = 0x55555550;
    *itim_io_amo_addr = 0xaaaaaaa0;
    for (int i = 0; i < cnt0; i++) {
        swap32_get_lock(lock_ptr);
        printf("get lock\n");

        (*(itim_addr))++;
        printf("itim_addr[%d] = 0x%x\n", i, *(itim_addr));

        amo32_add(itim_amo_addr, 1);
        printf("itim_amo_addr[%d] = 0x%x\n", i, *(itim_amo_addr));

        amo32_add(itim_io_amo_addr, 1);
        printf("itim_io_amo_addr[%d] = 0x%x\n", i, *(itim_io_amo_addr));

        swap32_put_lock(lock_ptr);
        delay_zqh(20);
    }
    delay_zqh(200);
    printf("itim test end\n");

    setStats(0);
    return 0;
}
