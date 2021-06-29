#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_atomic.c"
#include "zqh_common_uart.c"
#include "zqh_common_spi.c"
#include "zqh_common_i2c.c"
#include "zqh_common_eth.c"
#include "zqh_common_usb.c"
#include "zqh_common_exceptions.c"

int main (int argc, char** argv)
{
    //volatile uint64_t * lock_ptr = 0x80200000; //cacheable memory
    //volatile uint64_t * lock_ptr = PLIC_BASE; //configure reg
    volatile uint32_t * lock_ptr = TL_SRAM_MEM_BASE; //tl_sram
    //volatile uint64_t * lock_ptr = 0x80000010; //inner itim
    //volatile uint64_t * lock_ptr = 0x08000010; //out itim
    //volatile uint64_t * lock_ptr = 0x81000010; //inner dtim
    //volatile uint64_t * lock_ptr = 0x09000010; //out dtim

    volatile uint8_t * uc_addr = MMIO_SRAM_MEM_BASE;
    //volatile uint8_t * uc_addr = 0x61000001;
    //volatile uint8_t * uc_addr = 0x60000001;
    //volatile uint8_t * uc_addr = 0x02000000;
    volatile uint8_t * c_addr = MAIN_MEM_BASE + 0x20000;
    //volatile uint8_t * axi4_c_addr = AXI_SRAM_MEM_BASE;

    //tmp volatile uint32_t *itim_addr = ITIM_BASE;
    uint32_t itim_offset = 0x00;

    //tmp volatile uint32_t *itim_io_addr = ITIM_IO_BASE;
    uint32_t itim_io_offset = 0x08;

    //tmp volatile uint32_t *dtim_addr = DTIM_BASE;
    uint32_t dtim_offset = 0x00;

    //tmp volatile uint32_t *dtim_io_addr = DTIM_IO_BASE;
    uint32_t dtim_io_offset = 0x08;
    //volatile uint8_t * dtim_addr = DTIM_BASE;
    //volatile char * dtim_addr = DTIM_BASE;
    //volatile char * dtim_addr = DTIM_BASE;
    //volatile uint64_t * clint_addr = 0x02000000;
    volatile uint32_t * plic_addr;
    char str_buf[100];
    uint32_t a,b;
    uint32_t stop_code = 0x01; //1: pass, >1: fail

//tmp    //set uart0 reg
//tmp    //printf maybe use uart, need config it first
//tmp    *UART0_TXCTRL = 1;//enable tx
//tmp    //*UART0_TXCTRL = 0;//disable tx
//tmp    //*UART0_TXCTRL = 0x5; //parity odd check
//tmp    //*UART0_TXCTRL = 0x9; //parity even check
//tmp    //*UART0_TXCTRL = 0xd; //parity bit force to 0
//tmp    //*UART0_TXDATA = 0;
//tmp    *UART0_RXCTRL = 1;//enable rx
//tmp    //*UART0_RXCTRL = 0;//disable rx
//tmp    //*UART0_RXCTRL = 0x5; //parity odd check
//tmp    *UART0_RXDATA = 0;
//tmp    *UART0_IE     = 0;
//tmp    //*UART0_DIV    = 4000 - 1; //250000 baud ratio
//tmp    //*UART0_DIV    = 542 - 1; //1843200 baud ratio
//tmp    *UART0_DIV    = 32 - 1; //speedup simulation, use fastest speed
//tmp    //printf_zqh("UART0_TXCTRL %x\n", *UART0_TXCTRL);
//tmp    //printf_zqh("UART0_TXDATA %x\n", *UART0_TXDATA);
//tmp    //printf_zqh("UART0_RXCTRL %x\n", *UART0_RXCTRL);
//tmp    //printf_zqh("UART0_RXCTRL %x\n", *UART0_RXDATA);
//tmp    //printf_zqh("UART0_IE     %x\n", *UART0_IE    );
//tmp    //printf_zqh("UART0_DIV    %x\n", *UART0_DIV   );


    //printf("zqh_test0 done\n");
    //return 0;
    
    //csr set
    hart_id = read_csr(mhartid);
    support_vm = (read_csr(misa) >> 18) & 1;
    support_user = (read_csr(misa) >> 20) & 1;
    printf_zqh("mhartid %x\n", hart_id);


    //ddr read/write simple est
    //volatile uint32_t *ddr_ptr;
    //ddr_ptr = MAIN_MEM_BASE + 0x00010000;
    //*ddr_ptr = 0x0706050403020100;
    //printf_zqh("ddr read/write test end\n");
    //while(1);

    //while(1);


//tmp a    //crg_ctrl config:pll cfg
//tmp a    //printf_zqh("clock_ref_cfg init data = %x\n", *CRG_CTRL_CLOCK_REF_CFG);
//tmp a    //printf_zqh("core_pll_cfg init data = %x\n", *CRG_CTRL_CORE_PLL_CFG);
//tmp a    //printf_zqh("eth_pll_cfg init data = %x\n", *CRG_CTRL_ETH_PLL_CFG);
//tmp a    //printf_zqh("reset_cfg init data = %x\n", *CRG_CTRL_RESET_CFG);
//tmp a    //*CRG_CTRL_CLOCK_REF_CFG = 0x11111111;
//tmp a    *CRG_CTRL_CORE_PLL_CFG = 0x01010a01;
//tmp a    while(1) {
//tmp a        if ((*CRG_CTRL_CORE_PLL_CFG & 0x80000000) != 0) {
//tmp a            printf_zqh("core_pll locked\n");
//tmp a            *CRG_CTRL_CORE_PLL_CFG = *CRG_CTRL_CORE_PLL_CFG & 0xfeffffff;//disable bypass
//tmp a            printf_zqh("core_pll clean bypass\n");
//tmp a            break;
//tmp a        }
//tmp a    }
//tmp a    *CRG_CTRL_ETH_PLL_CFG = 0x03010504;
//tmp a    while(1) {
//tmp a        if ((*CRG_CTRL_ETH_PLL_CFG & 0x80000000) != 0) {
//tmp a            printf_zqh("eth_pll locked\n");
//tmp a            *CRG_CTRL_ETH_PLL_CFG = *CRG_CTRL_ETH_PLL_CFG & 0xfeffffff;//disable bypass
//tmp a            printf_zqh("eth_pll clean bypass\n");
//tmp a            *CRG_CTRL_ETH_PLL_CFG = *CRG_CTRL_ETH_PLL_CFG | 0x02000000;//set en
//tmp a            printf_zqh("eth_pll set en\n");
//tmp a            *CRG_CTRL_RESET_CFG = *CRG_CTRL_RESET_CFG | 0x20; //dereset eth
//tmp a            printf_zqh("dereset eth\n");
//tmp a            break;
//tmp a        }
//tmp a    }
//tmp a    *CRG_CTRL_DDR_PLL_CFG = 0x03010801;
//tmp a    while(1) {
//tmp a        if ((*CRG_CTRL_DDR_PLL_CFG & 0x80000000) != 0) {
//tmp a            printf_zqh("ddr_pll locked\n");
//tmp a            *CRG_CTRL_DDR_PLL_CFG = *CRG_CTRL_DDR_PLL_CFG & 0xfeffffff;//disable bypass
//tmp a            printf_zqh("ddr_pll clean bypass\n");
//tmp a            *CRG_CTRL_DDR_PLL_CFG = *CRG_CTRL_DDR_PLL_CFG | 0x02000000;//set en
//tmp a            printf_zqh("ddr_pll set en\n");
//tmp a            *CRG_CTRL_RESET_CFG = *CRG_CTRL_RESET_CFG | 0x09; //dereset ddr_phy and ddr_mc
//tmp a            printf_zqh("dereset ddr_phy and ddr_mc\n");
//tmp a            break;
//tmp a        }
//tmp a    }
    //*CRG_CTRL_RESET_CFG = 0x22222222;
    //printf_zqh("clock_ref_cfg reg data = %x\n", *CRG_CTRL_CLOCK_REF_CFG);
    //printf_zqh("core_pll_cfg reg data = %x\n", *CRG_CTRL_CORE_PLL_CFG);
    //printf_zqh("eth_pll_cfg reg data = %x\n", *CRG_CTRL_ETH_PLL_CFG);
    //printf_zqh("reset_cfg reg data = %x\n", *CRG_CTRL_RESET_CFG);

//    //test itim read/write
//    for (int i = 0; i < 4; i++) {
//        printf_zqh("itim[%0d] pre %x\n", i, *((uint64_t *)(itim_io_addr + (0x00100000 >> 3) * hart_id)));
//        *((uint16_t *)(itim_io_addr + (0x00100000 >> 3) * hart_id) + i) = i;
//        printf_zqh("itim[%0d] pos %x\n", i, *((uint64_t *)(itim_io_addr + (0x00100000 >> 3) * hart_id)));
//    }

    //test strong order access
    //if (hart_id == 0) {
    //    while(1) {
    //        *CLINT_MTIMECMP(0) = 0xffffffffffff0000;
    //        *CLINT_MTIMECMP(0) = 0xffffffffffff0001;
    //        //*PLIC_PRIORITY = 0;
    //        *uc_addr = 0;
    //        *CLINT_MTIMECMP(0) = 0xffffffffffff0002;
    //        *CLINT_MTIMECMP(0) = 0xffffffffffff0003;
    //        //*CLINT_MTIMECMP(0) = 0xffffffffffff0004;
    //        //*CLINT_MTIMECMP(0) = 0xffffffffffff0005;
    //        //*CLINT_MTIMECMP(0) = 0xffffffffffff0006;
    //        //*CLINT_MTIMECMP(0) = 0xffffffffffff0007;
    //    }
    //}
    //else {
    //    while(1);
    //}

    //set timer
    //test partial write to 8B reg
    //*((volatile char *)CLINT_MTIMECMP) = 0x00;
    //*(((volatile char *)CLINT_MTIMECMP) + 1) = 0x11;
    //*(((volatile uint16_t *)CLINT_MTIMECMP) + 1) = 0x2222;
    //*(((volatile uint32_t *)CLINT_MTIMECMP) + 1) = 0x33333333;
    *CLINT_MTIMECMP(hart_id) = 0xffffffffffffffff; //set mtimecmp to max value
    printf_zqh("CLINT_MTIMECMP_H %x\n", *CLINT_MTIMECMP_H(hart_id));
    printf_zqh("CLINT_MTIMECMP_L %x\n", *CLINT_MTIMECMP_L(hart_id));
    //*CLINT_MTIMECMP_L(hart_id) = 0xffffffff;
    //*CLINT_MTIMECMP_H(hart_id) = 0xffffffff;

    //test none exist mmio address access
    *CLINT_MSIP(1) = 0;
    printf_zqh("CLINT_MSIP(1) %x\n", *CLINT_MSIP(1));

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


    //set spi0 reg
//tmp    *SPI0_SCKMODE = 1; //sck default0, shift -> sample. better for loopback test
//tmp    //*SPI0_CSMODE = 2; //0: auto, 1: reserved, 2: hold, 3: off
//    *SPI0_SCKMODE = 3; //spi flash can work under this mode:0/3
//tmp    *SPI0_DELAY1 = 0x00010002;
//tmp    //*SPI0_FMT = 0x00080000;//bidirection, len = 8
//tmp    *SPI0_IE      = 0; //rxwm interrupt disable

    //set pwm0 reg
    *PWM0_PWMCFG = 0x00000000;//initial clear
    *PWM0_PWMCOUNT = 0x00000000;
    //printf_zqh("PWM0_PWMCOUNT %x\n", *PWM0_PWMCOUNT);
    *PWM0_PWMMAX = 0x00000fff;
    //printf_zqh("PWM0_PWMMAX %x\n", *PWM0_PWMMAX);
    *PWM0_PWMCMP0 = 0x00000020;
    //printf_zqh("PWM0_PWMCMP0 %x\n", *PWM0_PWMCMP0);
    *PWM0_PWMCMP1 = 0x000000080;
    //printf_zqh("PWM0_PWMCMP1 %x\n", *PWM0_PWMCMP1);
    *PWM0_PWMCMP2 = 0x0000000200;
    //printf_zqh("PWM0_PWMCMP2 %x\n", *PWM0_PWMCMP2);
    *PWM0_PWMCMP3 = 0x0000000800;
    //printf_zqh("PWM0_PWMCMP3 %x\n", *PWM0_PWMCMP3);
    *PWM0_PWMCFG = 0x00001207;//cmpgang=0x0, cmpcenter=0x0, enalways=1,  deglitch=0, zerocmp=1, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x00002000;//cmpgang=0x0, cmpcenter=0x0, enoneshot=1, deglitch=0, zerocmp=0, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x00001600;//cmpgang=0x0, cmpcenter=0x0, enalways=1,  deglitch=1, zerocmp=1, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x00001200;//cmpgang=0x0, cmpcenter=0x0, enalways=1,  deglitch=0, zerocmp=1, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x00001300;//cmpgang=0x0, cmpcenter=0x0, enalways=1,  deglitch=0, zerocmp=1, sticky=1, scale=0
    //*PWM0_PWMCFG = 0x000f1000;//cmpgang=0x0, cmpcenter=0xf, enalways=1,  deglitch=0, zerocmp=0, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x000f1000;//cmpgang=0x0, cmpcenter=0xf, enalways=1,  deglitch=0, zerocmp=0, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x000f1400;//cmpgang=0x0, cmpcenter=0xf, enalways=1,  deglitch=1, zerocmp=0, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x07001200;//cmpgang=0x2, cmpcenter=0x0, enalways=1,  deglitch=0, zerocmp=1, sticky=0, scale=0
    //printf_zqh("PWM0_PWMCFG %x\n", *PWM0_PWMCFG);

    //i2c reg set
    *I2C_DIV = 0x80;
    //*I2C_CONTROL = 0x5;//multi master enable, scl_stretch enable
    *I2C_CONTROL = 0x1;//multi master disable, scl_stretch enable
    //*I2C_CFG = 0x11000d;

    //mac reg set
//tmp    printf_zqh("MAC_MODE pre: %x\n", *MAC_MODE);
//tmp    //*MAC_MODE = 0;
//tmp    *MAC_IPG = 12;
//tmp    *MAC_IE = 0xfc; //interrupt enable
    //printf_zqh("MAC_MODE post: %x\n", *MAC_MODE);
    //printf_zqh("MAC_TX_BUF pre: %x\n", *MAC_TX_BUF);
    //*MAC_TX_BUF = 0x55555555;
    //printf_zqh("MAC_TX_BUF post: %x\n", *MAC_TX_BUF);
    //printf_zqh("MAC_RX_BUF pre: %x\n", *MAC_RX_BUF);
    //*MAC_RX_BUF = 0xaaaaaaaa;
    //printf_zqh("MAC_RX_BUF post: %x\n", *MAC_RX_BUF);


    //plic interrupt enable
    *PLIC_ENABLE_M(hart_id) = 0xfffffffe;
    //clear all plic interrupt pending bit
    for (int i = 0; i < PLIC_INT_NUM; i++) {
        uint32_t int_id;
        int_id = *PLIC_CLAIM_COMPLETE_M(hart_id);
        printf_zqh("plic claim %0d time, int_id = %x\n", i, int_id);
        if (int_id == 0) {
            break;
        }
    }
    write_csr(mip, 0);
    write_csr(mie, MIP_MSIP | MIP_MTIP | MIP_MEIP | MIP_SSIP | MIP_STIP | MIP_SEIP);
    set_csr(mstatus, MSTATUS_MIE | MSTATUS_SIE);
//    //set_csr(mip, MIP_SSIP);//supervisor software interrupt

    //counters
    //printf_zqh("mcounteren pre initial %x\n", read_csr(mcounteren));
    if (support_vm || support_user) {
        write_csr(mcounteren,0);
        printf_zqh("mcounteren post initial %x\n", read_csr(mcounteren));
    }

    //hpm counters
    //{{{
//tmp    write_csr(mhpmcounter3, 0);
//tmp    write_csr(mhpmcounter4, 0);
//tmp    write_csr(mhpmcounter5, 0);
//tmp    write_csr(mhpmcounter6, 0);
//tmp    printf_zqh("mhpmcounter3 post initial %d\n", read_csr(mhpmcounter3));
//tmp    printf_zqh("mhpmcounter4 post initial %d\n", read_csr(mhpmcounter4));
//tmp    printf_zqh("mhpmcounter5 post initial %d\n", read_csr(mhpmcounter5));
//tmp    printf_zqh("mhpmcounter6 post initial %d\n", read_csr(mhpmcounter6));
    //rocket's write_csr(mhpmevent3, 0x00 | (0x0000000e << 8));//load/store/amo
    //rocket's write_csr(mhpmevent4, 0x01 | (0x000001c0 << 8));//branch/jal/jalr
    //rocket's write_csr(mhpmevent5, 0x02 | (0x00000002 << 8));//D$ miss
    //rocket's write_csr(mhpmevent6, 0x02 | (0x00000001 << 8));//I$ miss
    write_csr(mhpmevent3, 0x00 | (0x0000000e << 8));//load/store/amo
    write_csr(mhpmevent4, 0x00 | (0x000001c0 << 8));//branch/jal/jalr
    write_csr(mhpmevent5, 0x02 | (0x00000001 << 8));//ifu refill
    write_csr(mhpmevent6, 0x02 | (0x00000006 << 8));//lsu refill/writeback

    //}}}


    //asm volatile ("scall");
    //asm volatile ("wfi");
    //printf_zqh("dcsr %x\n", read_csr(dcsr));
    //write_csr(dcsr, 0);


//tmp    //
//tmp    //gpio test
//tmp    //{{{
//tmp    //key input at gpio0-gpio3
//tmp    printf_zqh("gpio test start\n");
//tmp    *GPIO_INPUT_EN(0) = 0x0f;
//tmp    //output at gpio4-gpio7
//tmp    *GPIO_OUTPUT_EN(0) = 0xf0;
//tmp
//tmp    //output value
//tmp    uint32_t gpio_out_v;
//tmp    uint32_t gpio_out_bit_v;
//tmp    gpio_out_v = 0xffffff7f;
//tmp    *GPIO_OUTPUT_VAL(0) = 0xffffffff;//set to 1 first(led light off)
//tmp
//tmp    //read input value
//tmp    //for (int i = 0; i < 4; i++) {
//tmp    //    printf_zqh("input gpio[%0d] = %0d\n", i, ((*GPIO_INPUT_VAL(0)) >> i) & 1);
//tmp    //}
//tmp    uint32_t pwmcmp_v;
//tmp    uint32_t key1_last_v;
//tmp    uint32_t key2_last_v;
//tmp    uint32_t key_cur_v;
//tmp    while(1) {
//tmp        key1_last_v = (*GPIO_INPUT_VAL(0) >> 0) & 0x01;
//tmp        key2_last_v = (*GPIO_INPUT_VAL(0) >> 1) & 0x01;
//tmp        delay_ms(100);
//tmp
//tmp        //key1 capture, 0 valid
//tmp        key_cur_v = (*GPIO_INPUT_VAL(0) >> 0) & 0x01;
//tmp        if ((key_cur_v == 0) && (key1_last_v == 1)) {
//tmp            printf_zqh("input gpio[0] valid\n");
//tmp
//tmp            //increase led1's light
//tmp            pwmcmp_v = *PWM0_PWMCMP0 * 2;
//tmp            if (pwmcmp_v <= *PWM0_PWMMAX) {
//tmp                *PWM0_PWMCMP0 = pwmcmp_v;
//tmp            }
//tmp
//tmp            //shift right output value
//tmp            gpio_out_v = (gpio_out_v >> 1) | 0xffffff0f;
//tmp            if (gpio_out_v == 0xffffffff) {
//tmp                gpio_out_v = 0xffffff7f;
//tmp            }
//tmp            *GPIO_OUTPUT_VAL(0) = gpio_out_v;
//tmp        }
//tmp
//tmp        //key2 capture, 0 valid
//tmp        key_cur_v = (*GPIO_INPUT_VAL(0) >> 1) & 0x01;
//tmp        if ((key_cur_v == 0) && (key2_last_v == 1)) {
//tmp            printf_zqh("input gpio[1] valid\n");
//tmp
//tmp            //decrease led1's light
//tmp            pwmcmp_v = *PWM0_PWMCMP0 / 2;
//tmp            if (pwmcmp_v >= 1) {
//tmp                *PWM0_PWMCMP0 = pwmcmp_v;
//tmp            }
//tmp
//tmp            //shift left output value
//tmp            gpio_out_v = (gpio_out_v << 1) | 0xffffff1f;
//tmp            if (gpio_out_v == 0xffffffff) {
//tmp                gpio_out_v = 0xffffffef;
//tmp            }
//tmp            *GPIO_OUTPUT_VAL(0) = gpio_out_v;
//tmp        }
//tmp    }
//tmp
//tmp    printf_zqh("gpio test end\n");
//tmp    //}}}



    //uart0 test
    //{{{
    //clear full flag
    //*UART0_TXDATA = 0x00;
    //*UART0_TXDATA = 0x01;
    //*UART0_TXDATA = 0x02;
    //*UART0_TXDATA = 0x03;
    //*UART0_TXDATA = 0x04;
    //*UART0_TXDATA = 0x05;
    //*UART0_TXDATA = 0x06;
    //*UART0_TXDATA = 0x07;
    //*UART0_TXDATA = 0x01;
    //*UART0_TXDATA = 0xf0;
    //*UART0_TXDATA = 0xf1;
    //char tx_buf[] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07};
    //char tx_buf[] = {0x00, 0x01, 0x02, 0x03};
    //char tx_buf[] = "zqh uart test\n";
    //uart0_tx(tx_buf, sizeof(tx_buf));
    //for (int i = 0; i < sizeof(tx_buf); i++) {
    //    printf_zqh("uart0 rx %x\n", uart0_rx_stall());
    //}
    //delay_zqh(7000);
    //}}}

//tmp    //spi0 test
//tmp    //{{{
//tmp    printf_zqh("spi0 test start\n");
//tmp    //program IO access spi norflash
//tmp    uint32_t norflash_addr = 0;
//tmp    for (int i = 0; i < 8; i++) {
//tmp        norflash_addr = i;
//tmp        printf_zqh("spi0 norflash IO read[%0d] = %x\n", i, spi0_norflash_read_1byte(norflash_addr));
//tmp    }
//tmp
//tmp    //spi norflash memory map access
//tmp    //only support read
//tmp    uint8_t *norflash_xip_ptr = (SPI_FLASH_XIP_BASE + 8);
//tmp    for (int i = 0; i < 8; i++) {
//tmp        printf_zqh("spi0 norflash memory read[%0d]: %x\n", i, *(norflash_xip_ptr + i));
//tmp    }
//tmp
//tmp    printf_zqh("spi0 test end\n");
//tmp    //}}}


//tmp    //
//tmp    //i2c test
//tmp    //{{{
//tmp    //i2c eeprom write/read
//tmp    printf_zqh("i2c eeprom access start\n");
//tmp
//tmp    for (int i = 0; i < 4; i++){
//tmp        i2c_data_write(0xa0);//page0 write
//tmp        i2c_cmd_start_write();
//tmp        i2c_wait_no_transfer_in_progress();
//tmp
//tmp        i2c_data_write(i);//memory block address
//tmp        i2c_cmd_write();
//tmp        i2c_wait_no_transfer_in_progress();
//tmp
//tmp        i2c_data_write(i);//write data
//tmp        i2c_cmd_write_stop();
//tmp        i2c_wait_no_transfer_in_progress();
//tmp
//tmp        //delay_zqh(100);//wait write action done
//tmp
//tmp        printf_zqh("i2c eeprom write adddress = %x, data = %x\n", i, i);
//tmp    }
//tmp
//tmp    for (int i = 0; i < 4; i++){
//tmp        i2c_data_write(0xa0);//page0, dummy write
//tmp        i2c_cmd_start_write();
//tmp        i2c_wait_no_transfer_in_progress();
//tmp
//tmp        i2c_data_write(i);//memory block address, dummy write
//tmp        i2c_cmd_write();
//tmp        i2c_wait_no_transfer_in_progress();
//tmp
//tmp        i2c_data_write(0xa1);//device read, page0
//tmp        i2c_cmd_start_write();
//tmp        i2c_wait_no_transfer_in_progress();
//tmp
//tmp        i2c_cmd_read_nack_stop();
//tmp        i2c_wait_no_transfer_in_progress();
//tmp
//tmp        printf_zqh("i2c eeprom read adddress = %x, data = %x\n", i, i2c_data_read());
//tmp    }
//tmp    printf_zqh("i2c eeprom access end\n");
//tmp
//tmp
//tmp    printf_zqh("i2c test end\n");
//tmp    //}}}


    //
    //mac test
//tmp    //{{{
//tmp    printf_zqh("mac test start\n");
//tmp    eth_mac_tx_rx_test();
//tmp    printf_zqh("mac test end\n");
    //}}}


    //
    //ddr mc test
    //{{{
    printf_zqh("ddr_mc test start\n");
//tmp    //training WR_DQ, wr_dqs_delay = 0x00, wr_dq_delay = ?, rd_dqs_delay = 0x40
//tmp    printf_zqh("ddr training WR_DQ delay\n");
//tmp    ddr3_training_delay(DDR_TN_WR_DQ, 0x00, 0x00, 0x40);
//tmp
//tmp    printf_zqh("ddr training RD_DQS delay\n");
//tmp    //training RD_DQS, wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = ?
//tmp    ddr3_training_delay(DDR_TN_RD_DQS, 0x00, 0x40, 0x00);

    //best training resault
    //dll on mode:
    //wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = 0x40
    //dll off mode:
    //wr_dqs_delay = 0x00, wr_dq_delay = 0x40, rd_dqs_delay = 0xc8


//tmp    printf_zqh("ddr memory read write check\n");
    //ddr_phy_delay_cfg(0x00, 0x40, 0x40);//dll on
    //ddr_phy_delay_cfg(0x00, 0x40, 0xc8);//dll off
    //delay_ms(500);

//tmp    uint32_t ddr_mem_check_size;
//tmp    ddr_mem_check_size = pow(2,20);//1GB max
//tmp    if (ddr_wr_rd_check(ddr_mem_check_size, 0)) {
//tmp        printf_zqh("ddr memory check(%0d) pass\n", ddr_mem_check_size);
//tmp    }
//tmp    else {
//tmp        printf_zqh("ddr memory check(%0d) fail\n", ddr_mem_check_size);
//tmp    }

    printf_zqh("ddr_mc test end\n");
    //while(1);
    //}}}


    //
    //dma read/write teset
    //cross: rsize, wsize, source_addr lsb, dest_addr lsb, length lsb
    //{{{
    printf_zqh("dma test start\n");
//tmp    //config reg access
//tmp    int chn = 0;
//tmp    int chn_num = 1;
//tmp    uint8_t  dma_rsize = 6;
//tmp    uint8_t  dma_wsize = 6;
//tmp    uint8_t  dma_order = 0;
//tmp    uint8_t  dma_repeat = 0;
//tmp    //uint64_t dma_source = 0x80000000;
//tmp    //uint64_t dma_source = 0x80001100;
//tmp    uint64_t dma_source = MAIN_MEM_BASE;
//tmp    //uint64_t dma_dest = 0x80100000;
//tmp    //uint64_t dma_dest = MAIN_MEM_BASE + 0x00010000;
//tmp    //uint64_t dma_dest = (MAIN_MEM_BASE + (1 << (10 + 2)) - 128);//cross 2 ddr banks
//tmp    uint64_t dma_dest = 0x80010001;
//tmp    uint32_t dma_bytes = 256;
//tmp    //uint32_t dma_bytes = 256;
//tmp    //uint32_t dma_bytes = 192;
//tmp    //uint32_t dma_bytes = 128;
//tmp    //uint32_t dma_bytes = 129;
//tmp    //uint32_t dma_bytes = 256 - 32 + 16 + 8 + 4 + 2 + 1;
//tmp    //uint32_t dma_bytes = 16 + 8 + 4 + 2 + 1;
//tmp    //uint32_t dma_bytes = 32 + 16 + 8 + 4 + 2 + 1;
//tmp    //uint32_t dma_bytes = 64;
//tmp    volatile uint32_t *dma_source_ptr;
//tmp    volatile uint32_t *dma_dest_ptr;
//tmp    uint64_t dma_source_chn_offset = dma_bytes;
//tmp    //uint64_t dma_source_chn_offset = 1 << 15;//ddr diffrent row, same bank
//tmp    //uint64_t dma_source_chn_offset = 1 << 12;//ddr same row, different bank
//tmp    //
//tmp    //uint64_t dma_dest_chn_offset = dma_bytes;
//tmp    //uint64_t dma_dest_chn_offset = 1 << 15;//ddr diffrent row, same bank
//tmp    uint64_t dma_dest_chn_offset = 1 << 12;//ddr same row, different bank
//tmp
//tmp    for (int i = 0; i < chn_num; i++) {
//tmp        chn = i;
//tmp        printf_zqh("dma channel %0d do\n", chn);
//tmp
//tmp        *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) | 0x1;//set claim
//tmp        //*(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) | 0x0c000000;//enable interrupt
//tmp        *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) | 0x00000000;//disable interrupt
//tmp
//tmp        *(DMA_NEXT_CONFIG (chn)) = (dma_rsize << 28) | (dma_wsize << 24) | (dma_order << 3) | (dma_repeat << 2);
//tmp        *(DMA_NEXT_BYTES  (chn)) = dma_bytes;
//tmp        *(DMA_NEXT_DEST   (chn)) = dma_dest + dma_dest_chn_offset * chn;
//tmp        *(DMA_NEXT_SOURCE (chn)) = dma_source + dma_source_chn_offset * chn;
//tmp
//tmp        printf_zqh("DMA_CONTROL     (%0d) post = %x\n",  chn, *(DMA_CONTROL     (chn)));
//tmp        printf_zqh("DMA_NEXT_CONFIG (%0d) post = %x\n",  chn, *(DMA_NEXT_CONFIG (chn)));
//tmp        printf_zqh("DMA_NEXT_BYTES  (%0d) post = %lx\n", chn, *(DMA_NEXT_BYTES  (chn)));
//tmp        printf_zqh("DMA_NEXT_DEST   (%0d) post = %lx\n", chn, *(DMA_NEXT_DEST   (chn)));
//tmp        printf_zqh("DMA_NEXT_SOURCE (%0d) post = %lx\n", chn, *(DMA_NEXT_SOURCE (chn)));
//tmp
//tmp
//tmp        //tmp dma_source_ptr = dma_source;
//tmp        dma_dest_ptr = dma_dest + dma_dest_chn_offset * chn;
//tmp        //tmp dma_source = dma_source + dma_bytes;
//tmp
//tmp
//tmp        //for (int j = 0; j < dma_bytes/4; j++) {
//tmp        //    printf_zqh("dma pre dest[%x] = %x\n", dma_dest_ptr + j, *(dma_dest_ptr + j));
//tmp        //}
//tmp
//tmp        //flush dest address first
//tmp        for (int j = 0; j < dma_bytes/4; j++) {
//tmp            //*DC_L1_FLUSH_IO_ADDR(0) = dma_dest_ptr + j;
//tmp            dc_l1_flush(dma_dest_ptr + j);
//tmp        }
//tmp    }
//tmp
//tmp    for (int i = 0; i < chn_num; i++) {
//tmp        chn = i;
//tmp        *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) | 0x2;//set run
//tmp    }
//tmp
//tmp    int data_print_num = 8;
//tmp    for (int i = 0; i < chn_num; i++) {
//tmp        chn = i;
//tmp        dma_dest_ptr = (dma_dest & 0xfffffffc) + dma_dest_chn_offset * chn;
//tmp        while(1) {
//tmp            //interrupt enable
//tmp            if ((*(DMA_CONTROL(chn)) & 0x0c000000) != 0) {
//tmp                //check run flag is cleared by interrupt process
//tmp                if ((*(DMA_CONTROL(chn)) & 0x2) == 0) {
//tmp                    //printf_zqh("dma channel %0d interrupt process done\n", chn);
//tmp                    for (int j = 0; j < data_print_num; j++) {
//tmp                        printf_zqh("dma channel %0d interrupt post dest[%x] = %x\n", chn, dma_dest_ptr + j, *(dma_dest_ptr + j));
//tmp                    }
//tmp                    *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) & 0xfffffffe;//clean claim, release dma
//tmp                    break;
//tmp                }
//tmp            }
//tmp            else {
//tmp                //check done/error flag
//tmp                if ((*(DMA_CONTROL(chn)) & 0xc0000000) != 0) {
//tmp                    //printf_zqh("dma channel %0d sw scan done\n", chn);
//tmp                    for (int j = 0; j < data_print_num; j++) {
//tmp                        printf_zqh("dma channel %0d sw scan post dest[%x] = %x\n", chn, dma_dest_ptr + j, *(dma_dest_ptr + j));
//tmp                    }
//tmp
//tmp                    *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) & 0xfffffffd;//clean run, stop dma
//tmp                    *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) & 0xfffffffe;//clean claim, release dma
//tmp                    break;
//tmp                }
//tmp            }
//tmp        }
//tmp        //delay_zqh(500);
//tmp    }

    printf_zqh("dma test end\n");
    //while(1);
    //}}}

    //
    //usb test
    //0: host, 1: device
    //{{{
    printf_zqh("usb test start\n");

//tmp    usb_host_test();






    //
    //usb device test
    //initial host port first
    usb_host_initial_cfg();
    uint8_t usb_device_addr;
    usb_device_addr = 0x5a;
    usb_host_emum_common(usb_device_addr);


    usb_device_initial_cfg();
    usb_device_ready_trans(1, 0, NULL, 0);
    usb_device_ready_trans(2, 0, NULL, 0);

    uint32_t debug_cnt;
    uint32_t debug_more;
    uint32_t device_int_status;
    uint32_t device_ep_status;
    uint32_t device_ctrl_transfer_stage;
    uint8_t usb_device_rx_buf[64];
    struct USB_SETUP_PACKET device_setup_pkt;
    struct USB_DEVICE_DESCRIPTOR device_device_dcp;
    struct USB_CONFIGURATION_DESCRIPTOR device_cfg_dcp;
    struct USB_CBW usb_device_cbw;
    struct USB_CSW usb_device_csw;
    usb_host_trans_data_seq = 1;
    usb_device_trans_data_seq = 1;
    debug_more = 0;
    debug_cnt = 0;

    device_ctrl_transfer_stage = 0;
    while(1) {
        //scan device_int_status
        device_int_status = usb_device_read_int_status();
        if ((device_int_status & 0x20) != 0) {
            printf_zqh("usb int status stall_sent\n");
            //delay_ms(100);
            //while(1);
            continue;
        }
        else if ((device_int_status & 0x04) != 0) {
            printf_zqh("usb int status reset_event\n");
            printf_zqh("usb device 2nd reset event found\n");
            device_ctrl_transfer_stage = 0;
            usb_device_ready_trans(0, 0, NULL, 0);
            usb_device_ready_trans(1, 0, NULL, 0);
            usb_device_ready_trans(2, 0, NULL, 0);
            continue;
        }
        else if ((device_int_status & 0x01) != 0) {
            uint32_t trans_type;
            uint32_t pkt_len;
            uint8_t device_addr;
            uint8_t ep_out_addr;
            uint8_t ep_in_addr;
            uint16_t ep_in_mps;
            uint16_t ep_out_mps;

            //control transfer's setup pkt
            if (*USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0) != 0) {
                device_ep_status = *USB_CTRL_UTMI_DEVICE_STATUS(1,0);
                *USB_CTRL_UTMI_DEVICE_STATUS(1,0) = 0;
            }
            //bulk transfer's request pkt
            else {
                device_ep_status = *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_out_addr);
                *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_out_addr) = 0;
            }

            //check ep's status
            if ((device_ep_status & 0x0001) != 0) {
                printf_zqh("device ep crc_error\n");
                while(1);
            }
            else if ((device_ep_status & 0x0008) != 0) {
                printf_zqh("device ep rx_time_out\n");
            }
            printf_zqh("usb int status trans_done\n");


            //0: setup, 1: bulk in, 2: bulk out
            trans_type = (device_ep_status >> 8) & 0x03;
            device_addr = 0x5a;//host forward port's device addr
            ep_out_addr = host_ep_dcp_out[0].bEndpointAddress & 0x0f;
            ep_in_addr = host_ep_dcp_in[0].bEndpointAddress & 0x0f;
            ep_in_mps = host_ep_dcp_in[0].wMaxPacketSize;
            ep_out_mps = host_ep_dcp_out[0].wMaxPacketSize;


            //
            //setup requset pkt
            //control transfer is statefull. has setup, data and state stages
            //0: setup stage, 1: data stage write, 2: data state read, 3: state stage write, 4: state stage read
            if (*USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0) != 0) {
                device_ctrl_transfer_stage = 0;
                //
                //setup stage
                //{{{
                if (device_ctrl_transfer_stage == 0) {
                    //usb_host_trans_data_seq = 1;
                    usb_device_trans_data_seq = 1;
                    printf_zqh("setup trans found\n");
                    //recieve setup cmd
                    pkt_len = usb_device_read_rx_data(0, &device_setup_pkt);
                    printf_zqh("setup pkt_len = %0d\n", pkt_len);
                    display_usb_setup_packet(&device_setup_pkt);

                    //read: device -> host
                    if ((device_setup_pkt.bmRequestType & 0x80) != 0) {
                        device_ctrl_transfer_stage = 2;
                    }
                    //write: host -> device
                    else {
                        device_ctrl_transfer_stage = 1;
                    }
                }
                //}}}


                //
                //data stage
                //{{{
                //read
                if (device_ctrl_transfer_stage == 2) {
                    usb_setup_pkt_copy(&host_setup_pkt, &device_setup_pkt);
                    //get descriptor xxx
                    if ((device_setup_pkt.bmRequestType == 0x80) && 
                        (device_setup_pkt.bRequest == USB_REQ_GET_DESCRIPTOR)) {
                        //forward to host port side to get descriptor
                        usb_host_tx_addr_cfg(device_addr, 0);
                        //usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);

                        if ((device_setup_pkt.wValue >> 8) == 1) {
                            usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
                            printf_zqh("get descriptor device\n");
                            usb_dcp_copy(&device_device_dcp, usb_host_rx_buf);
                            display_usb_device_dcescriptor(&device_device_dcp);
                            pkt_len = usb_host_rx_buf[0];
                            if (device_setup_pkt.wLength < pkt_len) {
                                pkt_len = device_setup_pkt.wLength;
                            }
                        }
                        else if ((device_setup_pkt.wValue >> 8) == 2) {
                            usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
                            printf_zqh("get descriptor configuration\n");
                            usb_dcp_copy(&device_cfg_dcp, usb_host_rx_buf);
                            display_usb_cfg_dcescriptor(&device_cfg_dcp);
                            pkt_len = usb_host_rx_buf[2] + (usb_host_rx_buf[3] * 256);
                            if (device_setup_pkt.wLength < pkt_len) {
                                pkt_len = device_setup_pkt.wLength;
                            }
                        }
                        else if ((device_setup_pkt.wValue >> 8) == 3) {
                            printf_zqh("get descriptor string\n");
                            debug_cnt++;
                            //tmp pkt_len = usb_host_rx_buf[0];
                            //tmp printf_zqh("string dcp len = %d\n", pkt_len);
                            //tmp printf_zqh("string idx = %d\n", device_setup_pkt.wValue & 0x00ff);
                            //tmp printf_zqh("stored dcp len = %d\n", host_str_dcp[device_setup_pkt.wValue & 0x00ff][0]);
                            //tmp if (device_setup_pkt.wLength < pkt_len) {
                            //tmp     pkt_len = device_setup_pkt.wLength;
                            //tmp }
                            //
                            pkt_len = host_str_dcp[device_setup_pkt.wValue & 0x00ff][0];
                            for (int i = 0; i < pkt_len; i++) {
                                usb_host_rx_buf[i] = host_str_dcp[device_setup_pkt.wValue & 0x00ff][i];
                            }
                            if (device_setup_pkt.wLength < pkt_len) {
                                pkt_len = device_setup_pkt.wLength;
                            }
                        }
                        else if ((device_setup_pkt.wValue >> 8) == 6) {
                            usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
                            printf_zqh("get descriptor %0x\n", device_setup_pkt.wValue >> 8);
                            pkt_len = usb_host_rx_buf[0];
                            if (device_setup_pkt.wLength < pkt_len) {
                                pkt_len = device_setup_pkt.wLength;
                            }
                            pkt_len = device_setup_pkt.wLength;
                            //for (int i = 0; i < 64; i++) {
                            //    printf_zqh("usb_host_rx_buf[%0d] = %x\n", i, usb_host_rx_buf[i]);
                            //}
                        }
                        else {
                            printf_zqh("get descriptor unknown %0x\n", device_setup_pkt.wValue >> 8);
                            while(1);
                        }
                    }
                    else {
                        printf_zqh("get unknown\n");
                        printf_zqh("setup get trans forward to host. wLength = 0x%04d\n", device_setup_pkt.wLength);
                        //forward to host port to get data
                        usb_host_tx_addr_cfg(device_addr, 0);
                        pkt_len = usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
                        if (device_setup_pkt.wLength < pkt_len) {
                            pkt_len = device_setup_pkt.wLength;
                        }
                        for (int i = 0; i < pkt_len; i++) {
                            printf_zqh("usb_host_rx_buf[%0d] = 0x%02x\n", i, usb_host_rx_buf[i]);
                        }
                    }
                    //return get data
                    uint32_t done_status;
                    done_status = usb_device_tx_data_wait(0, usb_device_trans_data_seq, usb_host_rx_buf, pkt_len);
                    //timeout
                    if ((done_status & 0x0008) != 0) {
                        device_ctrl_transfer_stage = 0;
                    }
                    else {
                        usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                        device_ctrl_transfer_stage = 4;
                    }
                }
                //write
                else if (device_ctrl_transfer_stage == 1) {
                    usb_setup_pkt_copy(&host_setup_pkt, &device_setup_pkt);

                    //set address should not forward
                    //update address after state stage
                    if ((device_setup_pkt.bmRequestType == 0x00) && 
                        (device_setup_pkt.bRequest == USB_REQ_SET_ADDRESS)) {
                        ;
                    }
                    //other set cmd need forward to host port
                    else {
                        if ((device_setup_pkt.bmRequestType == 0x00) && 
                            (device_setup_pkt.bRequest == USB_REQ_SET_CONFIGURATION)) {
                            printf_zqh("set configuration\n");
                            usb_host_tx_addr_cfg(device_addr, 0);
                            usb_host_control_set_cfg(&host_setup_pkt);
                        }
                        else if ((device_setup_pkt.bmRequestType == 0x01) && 
                            (device_setup_pkt.bRequest == USB_REQ_SET_INTERFACE)) {
                            printf_zqh("set interface\n");
                            usb_host_tx_addr_cfg(device_addr, 0);
                            usb_host_control_set_itf(&host_setup_pkt);
                        }
                        else if (device_setup_pkt.bRequest == USB_REQ_CLEAR_FEATURE) {
                            uint32_t clean_ep;
                            printf_zqh("clear feature\n");
                            clean_ep = device_setup_pkt.wIndex & 0x000f;
                            usb_host_tx_addr_cfg(device_addr, 0);
                            usb_host_control_clear_feature(&host_setup_pkt);
                            usb_host_trans_stalled = 0;//clean stall flag


                            *USB_CTRL_UTMI_DEVICE_CONTROL(1,clean_ep) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,clean_ep) & 0xffffffef;
                            *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_out_addr) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_out_addr) & 0xffffffef;
                            //*USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x20;//clean interrupt flag of stall_sent
                            //debug_more = 1;
                        }
                        else {
                            printf_zqh("set unknown\n");
                            while(1);
                        }
                        //tmp printf_zqh("setup set trans forward to host. wLength = 0x%04d\n", device_setup_pkt.wLength);
                        //tmp usb_setup_pkt_copy(&host_setup_pkt, &device_setup_pkt);
                        //tmp //forward setup pkt to host port
                        //tmp usb_host_tx_addr_cfg(device_addr, 0);
                        //tmp usb_host_trans_setup(&host_setup_pkt);
                    }
                    device_ctrl_transfer_stage = 3;
                }
                //}}}


                //
                //state stage
                //{{{
                //control read need zero len OUT trans as state
                if (device_ctrl_transfer_stage == 4) {
                    //ready to recieve zero len OUT trans
                    usb_device_rx_data_wait(0);
                    printf_zqh("zero len OUT trans pkt len = %0d\n", *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0));
                    device_ep_status = *USB_CTRL_UTMI_DEVICE_STATUS(1,0);
                    *USB_CTRL_UTMI_DEVICE_STATUS(1,0) = 0;
                    printf_zqh("device_ep_status = %0x\n", device_ep_status);

                    //timeout no need read out data
                    if ((device_ep_status & 0x0008) == 0) {
                        //read out host's zero len out trans data
                        usb_device_drop_rx_data(3, usb_device_rx_buf);
                    }
                    printf_zqh("device control transfer read done\n");

                    //ready to recieve next setup cmd
                    //usb_device_rx_data_ready(0);
                }
                //control write need zero len IN trans as state
                else if (device_ctrl_transfer_stage == 3) {
                    usb_device_tx_data_wait(0, usb_device_trans_data_seq, NULL, 0);
                    usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;

                    //set address need be complete after state stage
                    //modify device_addr as fast as possible
                    if ((device_setup_pkt.bmRequestType == 0x00) && 
                        (device_setup_pkt.bRequest == USB_REQ_SET_ADDRESS)) {
                        *USB_CTRL_UTMI_DEVICE_ADDR(1) = device_setup_pkt.wValue;
                        printf_zqh("set address to 0x%02x\n", device_setup_pkt.wValue);
                    }
                    else if (device_setup_pkt.bRequest == USB_REQ_CLEAR_FEATURE) {
                        printf_zqh("clear feature post: read out the left csw of previous stalled cbw\n");
                        usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                        pkt_len = usb_host_csw_recv(&usb_device_csw);
                        printf_zqh("pkt_len = %0d\n", pkt_len);
                        display_usb_csw(&usb_device_csw);
                        //return the csw to host
                        usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, &usb_device_csw, pkt_len);
                        usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                    }

                    printf_zqh("device control transfer write done\n");

                    //ready to recieve next setup cmd
                    //usb_device_rx_data_ready(0);
                }
                //}}}
            }
            //bulk out cbw cmd
            else if (*USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,ep_out_addr) != 0) {
//                printf_zqh("bulk out trans cbw found\n");
                //for (int i = 0; i < 4; i++) {
                //    printf_zqh("ep%0d USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT = %x\n", i, *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,i));
                //    printf_zqh("ep%0d USB_CTRL_UTMI_DEVICE_CONTROL = %x\n", i, *USB_CTRL_UTMI_DEVICE_CONTROL(1,i));
                //}
                pkt_len = usb_device_read_rx_data(ep_out_addr, &usb_device_cbw);
//                printf_zqh("bulk pkt_len = %0d\n", pkt_len);
                display_usb_cbw(&usb_device_cbw);
//                display_usb_cbw_cbwcb(&usb_device_cbw);

                //read: device -> host
                if ((usb_device_cbw.bmCBWFlag & 0x80) != 0) {
                    printf_zqh("bulk cbw read\n");

                    //forward cbw requset to host port
//                    printf_zqh("bulk cbw read req forward to host\n");
                    usb_host_tx_addr_cfg(device_addr, ep_out_addr);
                    usb_host_cbw_send(&usb_device_cbw, 0);
                    if (usb_host_trans_stalled) {
                        printf_zqh("usb_host_cbw_send has stall\n");
                    }


                    //read cbw data
                    uint32_t read_cnt;
                    if (usb_device_cbw.CBWCB[0] == USB_CBS_SCSI_OPCODE_READ_10) {
                        read_cnt = usb_device_cbw.dCBWDataTransferLength/ep_in_mps;
                    }
                    else {
                        read_cnt = 1;
                    }
                    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                    for (int i = 0; i < read_cnt; i++) {
                        pkt_len = usb_host_cbw_data_recv(usb_host_rx_buf);
                        //if (usb_host_trans_stalled) {
                        //    printf_zqh("usb_host_cbw_data_recv has stall\n");
                        //    break;
                        //}

                        //printf_zqh("round %0d's pkt_len = %0d\n", i, pkt_len);
//                        printf_zqh("round %0d\n", i);
                        //for (int j = 0; j < pkt_len; j++) {
                        //    printf_zqh("pkt[%0d] = 0x%02x\n", j, usb_host_rx_buf[j]);
                        //}
                        //return cbw data
                        //printf_zqh("return cbw data to host\n");
                        usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, usb_host_rx_buf, pkt_len);
                        usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                    }


                    //check if host port forward trans has stall or not
                    if (usb_host_trans_stalled) {
                        printf_zqh("bulk cbw data read has stall\n");
                        //send stall to next trans
                        *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_in_addr) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_in_addr) | 0x10;
                        *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_out_addr) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_out_addr) | 0x10;
                        usb_device_wait_stall_sent(ep_in_addr);
                        printf_zqh("stall_sent found 1\n");
                        //usb_device_wait_stall_sent(ep_in_addr);
                        //printf_zqh("stall_sent found 2\n");

                        //delay_ms(100);
                    }
                    else {
                        //read host port's csw
                        usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                        pkt_len = usb_host_csw_recv(&usb_device_csw);
                        display_usb_csw(&usb_device_csw);
                        if (usb_host_trans_stalled) {
                            printf_zqh("usb_host_csw_recv has stall\n");
                        }

                        //return csw
                        printf_zqh("return csw to host\n");
                        printf_zqh("pkt_len = %0d\n", pkt_len);
                        usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, &usb_device_csw, pkt_len);
                        usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                    }


                    //ready to recieve next cbw cmd
                    usb_device_rx_data_ready(ep_out_addr);

                }
                //out: host -> device
                else {
                    printf_zqh("bulk cbw write\n");
                    //forward cbw requset to host port
//                    printf_zqh("bulk cbw write req forward to host\n");
                    //printf_zqh("debug_cnt = %0d\n", debug_cnt);
                    //if (debug_cnt == 10) {
                    //    printf_zqh("usb_host_trans_data_seq = %0d\n", usb_host_trans_data_seq);
                    //    //usb_host_trans_data_seq = (usb_host_trans_data_seq + 1) & 1;
                    //    //debug_more = 1;
                    //}


                    usb_host_tx_addr_cfg(device_addr, ep_out_addr);
                    usb_host_cbw_send(&usb_device_cbw, 0);
                    if (usb_host_trans_stalled) {
                        printf_zqh("usb_host_cbw_send has stall\n");
                    }


                    //write cbw's data to meadia
                    //if (usb_device_cbw.dCBWDataTransferLength != 0) {
                    //    printf_zqh("unknown cbw write:\n");
                    //    display_usb_cbw_cbwcb(&usb_device_cbw);
                    //    while(1);
                    //}
                    uint32_t write_cnt;
                    if (usb_device_cbw.CBWCB[0] == USB_CBS_SCSI_OPCODE_TEST_UNIT_READY) {
                        printf_zqh("TEST_UNIT_READY\n");
                        write_cnt = 0;
                    }
                    else if (usb_device_cbw.CBWCB[0] == USB_CBS_SCSI_OPCODE_WRITE_10) {
                        printf_zqh("WRITE_10\n");
                        write_cnt = usb_device_cbw.dCBWDataTransferLength/ep_out_mps;
                    }
                    else {
                        printf_zqh("write other\n");
                        if (usb_device_cbw.dCBWDataTransferLength != 0) {
                            write_cnt = 1;
                        }
                        else {
                            write_cnt = 0;
                        }
                    }
                    for (int i = 0; i < write_cnt; i++) {
                        //read data from host
                        usb_device_rx_data_wait(ep_out_addr);
                        pkt_len = usb_device_read_rx_data(ep_out_addr, usb_device_rx_buf);
                        //printf_zqh("pkt_len = %0d\n", pkt_len);

                        //write data to host port
                        usb_host_tx_addr_cfg(device_addr, ep_out_addr);
                        usb_host_trans_bulk_out(usb_device_rx_buf, pkt_len, 0);
                    }
                    if (usb_host_trans_stalled) {
                        printf_zqh("usb_host_trans_bulk_out has stall\n");
                    }



                    //read host port's csw
                    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                    pkt_len = usb_host_csw_recv(&usb_device_csw);
                    display_usb_csw(&usb_device_csw);
                    if (usb_host_trans_stalled) {
                        printf_zqh("usb_host_csw_recv has stall\n");
                    }

                    //return csw
                    printf_zqh("return csw to host\n");
                    printf_zqh("pkt_len = %0d\n", pkt_len);
                    usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, &usb_device_csw, pkt_len);
                    usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;

                    //retrun data again
                    //if (debug_cnt == 10) {
                    //    printf_zqh("return data again to host\n");
                    //    //usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                    //    //pkt_len = usb_host_csw_recv(&usb_device_csw);
                    //    //display_usb_csw(&usb_device_csw);

                    //    printf_zqh("pkt_len = %0d\n", pkt_len);
                    //    usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, &usb_device_csw, pkt_len);
                    //    usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                    //    debug_cnt = 0;
                    //}

                    //ready to recieve next cbw cmd
                    usb_device_rx_data_ready(ep_out_addr);
                }
            }
            else {
                //tmp printf_zqh("ep_in fifo size = %0d\n", *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,ep_in_addr));
                //tmp printf_zqh("ep_out fifo size = %0d\n", *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,ep_out_addr));
                //tmp printf_zqh("ep0 fifo size = %0d\n", *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0));
                //tmp printf_zqh("ep_in status = %0x\n", *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_in_addr));
                //tmp printf_zqh("ep_out status = %0x\n", *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_out_addr));
                //tmp printf_zqh("ep0 status = %0x\n", *USB_CTRL_UTMI_DEVICE_STATUS(1,0));

                //tmp //clean for next time
                //tmp *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_in_addr) = 0;
                //tmp *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_out_addr) = 0;
                //tmp *USB_CTRL_UTMI_DEVICE_STATUS(1,0) = 0;

                printf_zqh("illegal trans\n");
                //while(1);
            }
        }
        //nak_sent
        else if ((device_int_status & 0x10) != 0) {
            if (debug_more) {
                printf_zqh("usb int status nak_sent\n");
                printf_zqh("device_int_status = %x\n", device_int_status);
                printf_zqh("new device int status = %x\n", *USB_CTRL_DEVICE_INTERRUPT_STATUS(1));

                //usb_device_ready_trans(1, 1, NULL, 0);
                usb_device_ready_trans(1, 1, usb_device_rx_buf, 0);

                //for (int i = 0; i < 4; i++) {
                //    printf_zqh("USB_CTRL_UTMI_DEVICE_CONTROL(1,%0d) = %x\n", i, *USB_CTRL_UTMI_DEVICE_CONTROL(1,i));
                //    printf_zqh("USB_CTRL_UTMI_DEVICE_STATUS(1,%0d) = %x\n", i, *USB_CTRL_UTMI_DEVICE_STATUS(1,i));
                //    printf_zqh("USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,%0d) = %x\n", i, *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,i));
                //    printf_zqh("USB_CTRL_DEVICE_TX_FIFO_DATA_COUNT(1,%0d) = %x\n", i, *USB_CTRL_DEVICE_TX_FIFO_DATA_COUNT(1,i));
                //}
                ////clean regs to see which ep is modified in next print
                //for (int i = 0; i < 4; i++) {
                //    *USB_CTRL_UTMI_DEVICE_STATUS(1,i) = 0xff;
                //}
            }
            continue;
        }
        //sof_recv
        else if ((device_int_status & 0x08) != 0) {
            continue;
        }
        else {
            continue;
        }
    }

    printf_zqh("usb test end\n");
    while(1);
    //}}}


    //fence.i
    //__asm__ __volatile__ ("fence.i");


    //
    //float test
    //{{{
    printf_zqh("float test start\n");
    double da, db;
    float fa, fb;
    a = 0;
    b = 10;
    fa = 100.00;
    fb = 100.00;
    da = 200.00;
    db = 200.00;

    for (int i = 0; i < 2; i++) {
        a++;
        b--;
        fa = fa + 1.971;
        fb = fb - 1.971;

        da = da + 2.971;
        db = db - 2.971;

        //printf_zqh("read_csr %x\n",read_csr(mstatus));

        printf_zqh("#####zhou do %d times!#####\n",i);
        printf_zqh("mul  a(%d) b(%d), r(%d)\n",a,b,a*b);

        printf_zqh("fmul fa(%s)\n",f2str(fa, str_buf));
        printf_zqh("fmul fb(%s)\n",f2str(fb, str_buf));
        printf_zqh("fmul r(%s)\n",f2str(fa*fb, str_buf));

        printf_zqh("fmul da(%s)\n",f2str(da, str_buf));
        printf_zqh("fmul db(%s)\n",f2str(db, str_buf));
        printf_zqh("fmul r(%s)\n",f2str(da*db, str_buf));

        printf_zqh("div  a(%d) b(%d), r(%d)\n",a*100,b,a*100/b);

        printf_zqh("fdiv fa(%s)\n",f2str(fa*100.00, str_buf));
        printf_zqh("fdiv fb(%s)\n",f2str(fb, str_buf));
        printf_zqh("fdiv r(%s)\n",f2str(fa*100.00/fb, str_buf));

        printf_zqh("fdiv da(%s)\n",f2str(da*100.00, str_buf));
        printf_zqh("fdiv db(%s)\n",f2str(db, str_buf));
        printf_zqh("fdiv r(%s)\n",f2str(da*100.00/db, str_buf));

        printf_zqh("divSqrt fa(%s)\n",f2str(fa*200.00, str_buf));
        printf_zqh("divSqrt fb(%s)\n",f2str(fb, str_buf));
        printf_zqh("divSqrt r(%s)\n",f2str(sqrt(fa*200.00), str_buf));

        printf_zqh("divSqrt da(%s)\n",f2str(da*200.00, str_buf));
        printf_zqh("divSqrt db(%s)\n",f2str(db, str_buf));
        printf_zqh("divSqrt r(%s)\n",f2str(sqrt(da*200.00), str_buf));

        //*uc_addr = i;
    }
    printf_zqh("float test end\n");
    //}}}

//    //datatimpad access test
//    //uint64_t tim_data;
//    uint64_t tim_wdata;
//    uint64_t tim_rdata;
//    for (int i = 0; i < 3; i++) {
//        tim_wdata = i;
//        //*(dtim_addr + i) = tim_wdata;
//        *(dtim_addr) = tim_wdata;
//        printf_zqh("tim[%x] write %x\n",dtim_addr, tim_wdata);
//        tim_rdata = *(dtim_addr);
//        //printf_zqh("tim[%x] write %x\n",dtim_addr + i, tim_wdata);
//        printf_zqh("tim[%x] read  %x\n",dtim_addr, tim_rdata);
//    }

//    for (int i = 0; i < 10; i++) {
//        printf_zqh("tim[%x] before add %x\n", i, *dtim_addr);
//        *dtim_addr = *dtim_addr + 1;
//        printf_zqh("tim[%x] after  add %x\n", i, *dtim_addr);
//    }
 
    //while(hart_id != 0);

    int cnt0,cnt1;
    cnt0 = 5;
    cnt1 = 3;
//    if (hart_id == 0) {
        //for (int i = 0; i < cnt0; i++) {
        //    printf_zqh("tim[%x] before add %x\n", i, *dtim_addr);
        //    *dtim_addr = *dtim_addr + 1;
        //    printf_zqh("tim[%x] after  add %x\n", i, *dtim_addr);
        //}
        //printf_zqh("tim last value %d\n", *dtim_addr);
        //if (*dtim_addr != cnt0) {
        //    stop_code = 1;
        //}

        for (int i = 0; i < cnt0; i++) {
            *uc_addr = i;
            //printf_zqh("cnt[%x] %x\n", i, i);
        }

        //*CLINT_MTIMECMP = 0x8; // set timercmp
        if (hart_id == 0) {
            *c_addr = 0;
            //*axi4_c_addr = 0;
            //(*DC_L1_FLUSH_IO_ADDR(0)) = c_addr;
            dc_l1_flush(c_addr);
            //(*DC_L1_FLUSH_IO_ADDR(0)) = axi4_c_addr;
            *lock_ptr = 0;
        }
        //(*DC_L1_FLUSH_IO_ADDR(hart_id)) = c_addr;

        //*(ITIM_ADDR(itim_offset)) = 0;
        //*(DTIM_ADDR(dtim_offset)) = 0;


        //while(*lock_ptr != 0){
        //    *lock_ptr = 0;
        //}
        //*lock_ptr = 0;
        delay_zqh(100);
        for (int i = 0; i < cnt0; i++) {
            //int sp_t_id;
            //if (hart_id == 0){
            //    sp_t_id = 1;
            //}
            //else {
            //    sp_t_id = 0;
            //}
            //printf_zqh("tim[%x] %x\n", i, *dtim_addr);

            //*dtim_addr = i;
            //*(dtim_addr + ((i * 64) >> 3)) = i;
            //*(c_addr + hart_id * 0x1000 + i * 64) = i;
            //*(dtim_io_addr + (0x00100000 >> 3) * sp_t_id) = i + 0x1000 * hart_id;
            //while(cas(lock_ptr, 0, 1));
            //cas64_get_lock(lock_ptr);
            //swap64_get_lock(lock_ptr);
            swap32_get_lock(lock_ptr);
            printf_zqh("get lock\n");
            (*c_addr)++;
            //(*axi4_c_addr)++;
            //tmp (*(itim_addr + itim_offset))++;
            //tmp (*(dtim_addr + dtim_offset))++;
            //(*(ITIM_IO_ADDR(hart_id, itim_io_offset)))++;
            //(*(DTIM_IO_ADDR(hart_id, dtim_io_offset)))++;
            //uint64_t ret_v;
            //ret_v = amo64_swap(CLINT_MTIMECMP(hart_id), 0x0000000000000001 << i);
            //ret_v = amo64_swap(c_addr, 0x0000000000000001 << i);
            //ret_v = amo64_swap(dtim_addr , 0x0000000000000001 << i);
            //printf_zqh("ret_v %x\n", ret_v);
            //printf_zqh("c_addr[%d] %x\n", i, *CLINT_MTIMECMP(hart_id));
            printf_zqh("c_addr[%d] %x\n", i, *c_addr);
            //printf_zqh("axi4_c_addr[%d] %x\n", i, *axi4_c_addr);
            //tmp printf_zqh("itim_offset[%d] %x\n", i, *(itim_addr + itim_offset));
            //tmp printf_zqh("dtim_offset[%d] %x\n", i, *(dtim_addr + dtim_offset));
            //printf_zqh("itim_io_offset[%d] %x\n", i, *(ITIM_IO_ADDR(hart_id, itim_io_offset)));
            //printf_zqh("dtim_io_offset[%d] %x\n", i, *(DTIM_IO_ADDR(hart_id, dtim_io_offset)));
            //printf_zqh("itim_offset * c_addr[%d] %x\n", i, *(ITIM_ADDR(itim_offset)) * *c_addr);
            //printf_zqh("dtim_offset * c_addr[%d] %x\n", i, *(DTIM_ADDR(dtim_offset)) * *c_addr);
            //printf_zqh("itim_offset * axi4_c_addr[%d] %x\n", i, *(ITIM_ADDR(itim_offset)) * *axi4_c_addr);
            //printf_zqh("dtim_offset * axi4_c_addr[%d] %x\n", i, *(DTIM_ADDR(dtim_offset)) * *axi4_c_addr);
            //printf_zqh("float[%d] %s\n", i, f2str(*dtim_addr + 23.12345678, str_buf));
            //printf_zqh("c_addr[%d] %x\n", i, *dtim_addr);
            //printf_zqh("c_addr[%d] %x\n", i, *c_addr);
            //printf_zqh("put lock\n");
            //while(cas(lock_ptr, 1, 0));
            //cas64_put_lock(lock_ptr);
            //swap64_put_lock(lock_ptr);
            //*DC_L1_FLUSH_IO_ADDR(0) = c_addr;
            dc_l1_flush(c_addr);
            //*DC_L1_FLUSH_IO_ADDR(0) = axi4_c_addr;
            //*DC_L1_FLUSH_IO_ADDR(hart_id) = c_addr;
            wait_l1_dcache_flush_done();
            swap32_put_lock(lock_ptr);
            delay_zqh(20);
            //soft_scan_eip(PLIC_CLAIM_COMPLETE_M(hart_id);
            //soft_scan_eip(PLIC_CLAIM_COMPLETE_S(hart_id);
            //printf_zqh("dtim_addr[%x] %x\n", i, *(dtim_addr + ((i * 64) >> 3)));
            //printf_zqh("c_addr[%x] %x\n", i, *(c_addr + hart_id * 0x1000 + i * 64));
            //printf_zqh("dtim_io_addr[%x] %x\n", i, *(dtim_io_addr + (0x00100000 >> 3) * hart_id));
            //printf_zqh("c_addr[%x] %x\n", i, *c_addr);

//tmp            //*CLINT_MSIP = i;
//tmp            *PLIC_PRIORITY         = i+0;
//tmp            *(PLIC_PRIORITY + 1)   = i+1;
//tmp            *PLIC_PENDING          = i+2;
//tmp            *PLIC_ENABLE_M         = i+3;
//tmp            *PLIC_ENABLE_S         = i+4;
//tmp            *PLIC_THRESHOLD_M      = i+5;
//tmp            *PLIC_THRESHOLD_S      = i+6;
//tmp            *PLIC_CLAIM_COMPLETE_M = i+7;
//tmp            *PLIC_CLAIM_COMPLETE_S = i+8;
//tmp            printf_zqh("PLIC_PRIORITY         %x\n", *PLIC_PRIORITY);
//tmp            printf_zqh("PLIC_PRIORITY + 1     %x\n", *(PLIC_PRIORITY + 1));
//tmp            printf_zqh("PLIC_PENDING          %x\n", *PLIC_PENDING);
//tmp            printf_zqh("PLIC_ENABLE_M         %x\n", *PLIC_ENABLE_M        );
//tmp            printf_zqh("PLIC_ENABLE_S         %x\n", *PLIC_ENABLE_S        );
//tmp            printf_zqh("PLIC_THRESHOLD_M      %x\n", *PLIC_THRESHOLD_M     );
//tmp            printf_zqh("PLIC_THRESHOLD_S      %x\n", *PLIC_THRESHOLD_S     );
//tmp            printf_zqh("PLIC_CLAIM_COMPLETE_M %x\n", *PLIC_CLAIM_COMPLETE_M);
//tmp            printf_zqh("PLIC_CLAIM_COMPLETE_S %x\n", *PLIC_CLAIM_COMPLETE_S);

        }
        delay_zqh(200);
        //printf_zqh("c_addr[%x] %x\n", cnt0, *c_addr);
//    }
//    else {
//        //for (int i = 0; i < cnt1; i++) {
//        //    printf_zqh("uc_addr[%x] before add %x\n", i, *uc_addr);
//        //    *uc_addr = *uc_addr + 1;
//
//        //    //*uc_addr = 0;
//        //    //*uc_addr = 1;
//        //    //*uc_addr = 2;
//        //    //*uc_addr = 3;
//        //    //*uc_addr = 4;
//        //    //*uc_addr = 5;
//        //    //*uc_addr = 6;
//        //    //*uc_addr = 7;
//        //    delay_zqh(100);
//        //    //printf_zqh("uc_addr[%x] after  add %x\n", i, *uc_addr);
//        //}
//        for (int i = 0; i < cnt1; i++) {
//            *uc_addr = cnt1;
//            printf_zqh("uc_addr[%x] %x\n", i, *uc_addr);
//            delay_zqh(100);
//        }
//        printf_zqh("uc_addr last value %d\n", *uc_addr);
//        //if (*uc_addr != cnt1) {
//        //    stop_code = 1;
//        //}
//    }

//    int aaa, bbb;
//    aaa = 0;
//    bbb = 0;
//
//    while(1){
//        //if (aaa%2 == 0) {
//        //    *(dtim_addr) = 0;
//        //}
//        *(dtim_addr) = 0;
//    }

    printf_zqh("mcycle %d\n", read_csr(mcycle));
    printf_zqh("minstret %d\n", read_csr(minstret));
    printf_zqh("mhpmcounter3 last %d\n", read_csr(mhpmcounter3));
    printf_zqh("mhpmcounter4 last %d\n", read_csr(mhpmcounter4));
    printf_zqh("mhpmcounter5 last %d\n", read_csr(mhpmcounter5));
    printf_zqh("mhpmcounter6 last %d\n", read_csr(mhpmcounter6));
    __sync_synchronize();
    *STOP_PTR_HART(hart_id) = stop_code;
    while(1);

    return 0;
}
