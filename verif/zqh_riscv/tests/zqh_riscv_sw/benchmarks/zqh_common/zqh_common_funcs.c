#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <math.h>
#include "util.h"

#ifndef __ZQH_COMMON_FUNCS_C
#define __ZQH_COMMON_FUNCS_C

//to MMIO
//volatile __thread uint8_t *print_ptr = MMIO_PRINT_BASE | 0x00f0ff00;
__thread char str_zqh[100];
__thread char str_xcpt_zqh[100];
//volatile __thread uint8_t *stop_ptr = MMIO_PRINT_BASE | 0x00f0fff0;
volatile __thread char hart_id = 0;
volatile __thread char support_vm = 0;
volatile __thread char support_user = 0;

#undef putchar
int putchar(int ch)
{
    //user uart
    #if PRINT_USE_UART == 1
        while(((*UART0_TXDATA) & 0x80000000) != 0);
        *UART0_TXDATA = ch;
    //use print_monitor
    #else
        *(PRINT_PTR_HART(hart_id)) = ch;
    #endif

    return 0;
}

void printstr(char* s)
{
  int len;
  char pre_str[11] = "[riscv0]: ";
  pre_str[6] = hart_id + '0';

  len = strlen(pre_str);
  for (int i = 0; i< len; i++) {
      //*(PRINT_PTR_HART(hart_id)) = pre_str[i];
      putchar(pre_str[i]);
  }

  len = strlen(s);
  for (int i = 0; i< len; i++) {
      //*(PRINT_PTR_HART(hart_id)) = s[i];
      putchar(s[i]);
  }
}

//char* f2str(double a, char *buf)
char* f2str(float a, char *buf)
{
    char *buf_h;
    char *buf_l;
    buf_h = buf;
    int64_t a_h, a_l;
    a_h = (int64_t)a;
    sprintf(buf_h,"%d",a_h);
    buf_l = buf + strlen(buf_h);
    a_l = (int64_t)abs((a - a_h)*10000);
    sprintf(buf_l,".%04d",a_l);
    return buf;
}

#define printf_zqh(format,args...) \
        sprintf(str_zqh,format,##args); \
        printstr(str_zqh);

//exception process use this printf to avoid conflict with normal user printf
#define printf_xcpt_zqh(format,args...) \
        sprintf(str_xcpt_zqh,format,##args); \
        printstr(str_xcpt_zqh);

void delay_zqh(int a) {
    for (int i = 0; i < a; i ++) {
        asm volatile ("nop");
    }
}

//in 10MHz clock
//in ms: a = 1000 means 1 second
void delay_ms(uint32_t a) {
    for (uint32_t i = 0; i < a; i++) {
        for (uint32_t j = 0; j < 9375; j++) {
            asm volatile ("nop");
        }
    }
}

int soft_scan_eip(uint32_t * claim_ptr) {
    volatile uint32_t int_id;
    volatile uint32_t pending;
    pending = *PLIC_PENDING;
    int_id = *claim_ptr; //claim
    if (int_id != 0) {
        printf_zqh("soft_scan_eip process EXTERNAL_INTERRUPT\n");
        printf_zqh("pending = %x\n", pending);
        printf_zqh("interrupt ID = %x\n", int_id);
        *claim_ptr = int_id; //complete
        return int_id;
    }
    else {
        return 0;
    }
}

uint32_t wait_l1_dcache_flush_done() {
    uint32_t done = 0;
    while(done == 0) {
        done = *DC_L1_FLUSH_IO_ADDR(0);
        //done = *DC_L1_FLUSH_IO_ADDR(hart_id);
    }
    return done;
}

void post_stop(uint32_t code) {
    printf_zqh("mcycle %d\n", read_csr(mcycle));
    printf_zqh("minstret %d\n", read_csr(minstret));
    printf_zqh("mhpmcounter3 last %d\n", read_csr(mhpmcounter3));
    printf_zqh("mhpmcounter4 last %d\n", read_csr(mhpmcounter4));
    printf_zqh("mhpmcounter5 last %d\n", read_csr(mhpmcounter5));
    printf_zqh("mhpmcounter6 last %d\n", read_csr(mhpmcounter6));
    __sync_synchronize();
    *STOP_PTR_HART(hart_id) = code;
    while(1);
}

void dc_l1_flush(uint32_t addr) {
    *DC_L1_FLUSH_IO_ADDR(0) = addr;
    uint32_t flush_done;
    do {
        flush_done = *DC_L1_FLUSH_IO_ADDR(0);
    }
    while(flush_done == 0);
}

#endif
