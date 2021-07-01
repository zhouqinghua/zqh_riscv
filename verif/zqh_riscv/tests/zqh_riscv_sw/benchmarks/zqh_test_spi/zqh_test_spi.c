#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"
#include "zqh_common_spi.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();
    //spi0 test
    //{{{
    printf_zqh("spi0 test start\n");

    //read out jedec_id
    uint32_t jedec_id;
    jedec_id = spi0_norflash_read_jedec_id();
    printf_zqh("jedec_id = 0x%x\n", jedec_id);

    //read out unique_id
    uint64_t unique_id;
    unique_id = spi0_norflash_read_unique_id();
    printf_zqh("unique_id = 0x%lx\n", unique_id);
    //while(1);

    //chip erase
    spi0_norflash_chip_erase();
    printf_zqh("spi0_norflash_chip_erase done\n");

    //write
    uint8_t wrdata_buf[4] = {0,0,0,0};
    spi0_norflash_write(0, wrdata_buf, 4);
    printf_zqh("spi0_norflash_write done\n");

    //program IO access spi norflash
    uint32_t norflash_addr_base = 0;
    uint32_t norflash_addr;
    uint8_t rddata_buf[4];
    for (int i = 0; i < 8; i++) {
        norflash_addr = norflash_addr_base + i;
        spi0_norflash_read(norflash_addr, rddata_buf, 1);
        printf_zqh("spi0 norflash IO read[0x%x] = 0x%x\n", norflash_addr, rddata_buf[0]);
    }

    //spi norflash memory map access
    //only support read
    uint8_t *norflash_xip_ptr;
    for (int i = 0; i < 8; i++) {
        norflash_xip_ptr = SPI_FLASH_XIP_BASE + 8 + i;
        printf_zqh("spi0 norflash memory read[0x%x]: 0x%x\n", norflash_xip_ptr, *norflash_xip_ptr);
    }

    printf_zqh("spi0 test end\n");
    //}}}

    //post_stop(0x01);
    return 0;
}
