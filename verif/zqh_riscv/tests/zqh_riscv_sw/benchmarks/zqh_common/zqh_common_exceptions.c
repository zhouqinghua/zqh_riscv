#ifndef __ZQH_COMMON_EXCEPTIONS_C
#define __ZQH_COMMON_EXCEPTIONS_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

uintptr_t handle_trap(uintptr_t cause, uintptr_t epc, uintptr_t regs[32])
{
    uintptr_t ret_epc;
    volatile uint32_t int_id;
    //__asm__ __volatile__ ("fence.i");
    printf_xcpt_zqh("handle_trap do: cause = %x\n", cause);
    printf_xcpt_zqh("handle_trap do: epc = %x\n", epc);
    write_csr(mip, 0);
    if ((cause == CAUSE_USER_ECALL) ||
        (cause == CAUSE_SUPERVISOR_ECALL) ||
        (cause == CAUSE_HYPERVISOR_ECALL) ||
        (cause == CAUSE_MACHINE_ECALL)) {
        ret_epc = epc + 4;
    }
    else if (cause == CAUSE_MACHINE_SOFTWARE_INTERRUPT){
        printf_xcpt_zqh("process CAUSE_MACHINE_SOFTWARE_INTERRUPT\n");
        *CLINT_MSIP(hart_id) = 0; //clean software interrupt source
        ret_epc = epc;
    }
    else if (cause == CAUSE_MACHINE_TIMER_INTERRUPT){
        printf_xcpt_zqh("process CAUSE_MACHINE_TIMER_INTERRUPT\n");
        //*CLINT_MTIME = 0; //reset mtimer to 0
        *CLINT_MTIME_L = 0;
        *CLINT_MTIME_H = 0;
        ret_epc = epc;
    }
    else if (cause == CAUSE_MACHINE_EXTERNAL_INTERRUPT){
        printf_xcpt_zqh("process CAUSE_MACHINE_EXTERNAL_INTERRUPT\n");
        printf_xcpt_zqh("pending = %x\n", *PLIC_PENDING);
        int_id = *PLIC_CLAIM_COMPLETE_M(hart_id); //claim
        printf_xcpt_zqh("interrupt ID = %x\n", int_id);

        if ((int_id == PLIC_INT_ID_DMA_DONE(0)) | (int_id == PLIC_INT_ID_DMA_ERROR(0))) { //dma channel0
            uint32_t control = *DMA_CONTROL(0);
            printf_xcpt_zqh("DMA_CHN0 control = %x\n", control);
            if ((control & 0x40000000) != 0) {
                volatile uint8_t *dest_ptr;
                printf_xcpt_zqh("DMA_CHN0 control.done set\n");
                dest_ptr = *(DMA_NEXT_DEST(0));
                for (int i = 0; i < 8; i++) {
                    printf_xcpt_zqh("DMA_CHN0 dest[%x] = %x\n", dest_ptr+i, *(dest_ptr+i));
                }
                //clean done
                *DMA_CONTROL(0) = *DMA_CONTROL(0) & 0xbfffffff;
            }
            if ((control & 0x80000000) != 0) {
                uint8_t *dest_ptr;
                printf_xcpt_zqh("DMA_CHN0 control.error set\n");
                //clean error
                *DMA_CONTROL(0) = *DMA_CONTROL(0) & 0x7fffffff;
            }

            *(DMA_CONTROL(0)) = *(DMA_CONTROL(0)) & 0xfffffffd;//clean run, stop dma
        }
        if (int_id == PLIC_INT_ID_UART0) { //uart0
            uint32_t ip = *UART0_IP;
            printf_xcpt_zqh("UART0 ip = %x\n", ip);
            if ((ip & 0x2) != 0) {
                printf_xcpt_zqh("UART0 ip.rxwm pending\n");
                //printf_zqh("UART0 rx data: %x\n", uart0_rx());
            }
            if ((ip & 0x4) != 0) {
                uint32_t error_code = *UART0_ERROR;
                printf_zqh("UART0 data parity error. code = %d\n", error_code);
                *UART0_ERROR = 0; //clean error code
            }
        }
        if (int_id == PLIC_INT_ID_SPI0) { //spi0
            uint32_t ip = *SPI0_IP;
            printf_xcpt_zqh("SPI0 ip = %x\n", ip);
            if ((ip & 0x2) != 0) {
                printf_xcpt_zqh("SPI0 ip.rxwm pending\n");
                //printf_zqh("SPI0 rx data: %x\n", spi0_rx());
            }
        }
        if (int_id == PLIC_INT_ID_I2C) { //i2c
            uint32_t status = *I2C_STATUS;
            uint32_t cmd = *I2C_CMD;
            printf_xcpt_zqh("I2C status = %x\n", status);
            printf_xcpt_zqh("I2C cmd = %x\n", cmd);
            printf_xcpt_zqh("I2C rx data = %x\n", *I2C_DATA);

            //clean ip
            *I2C_IP = 1;
        }
        if (int_id == PLIC_INT_ID_MAC) { //mac
            uint32_t ip = *MAC_IP;
            printf_xcpt_zqh("MAC ip = %x\n", ip);
            ip = ip & *MAC_IE; //mask disabled int
            if ((ip & 0x00000001) != 0) {
                *MAC_IP = 0x00000001;
            }
            if ((ip & 0x00000002) != 0) {
                *MAC_IP = 0x00000002;
            }
            if ((ip & 0x00000004) != 0) {
                *MAC_IP = 0x00000004;
            }
            if ((ip & 0x00000008) != 0) {
                *MAC_IP = 0x00000008;
            }
            if ((ip & 0x00000010) != 0) {
                *MAC_IP = 0x00000010;
            }
            if ((ip & 0x00000020) != 0) {
                *MAC_IP = 0x00000020;
            }
            if ((ip & 0x00000040) != 0) {
                *MAC_IP = 0x00000040;
            }
            if ((ip & 0x00000080) != 0) {
                *MAC_IP = 0x00000080;
            }

        }
        *PLIC_CLAIM_COMPLETE_M(hart_id) = int_id; //complete
        ret_epc = epc;
    }
    else if (cause == CAUSE_SUPERVISOR_EXTERNAL_INTERRUPT){
        printf_xcpt_zqh("process CAUSE_SUPERVISOR_EXTERNAL_INTERRUPT\n");
        printf_xcpt_zqh("pending = %x\n", *PLIC_PENDING);
        int_id = *PLIC_CLAIM_COMPLETE_S(hart_id); //claim
        printf_xcpt_zqh("interrupt ID = %x\n", int_id);
        *PLIC_CLAIM_COMPLETE_S(hart_id) = int_id; //complete
        ret_epc = epc;
    }
    else {
        ret_epc = epc;
    }
    return ret_epc;
}

#endif
