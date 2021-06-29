#ifndef __ZQH_COMMON_UART_C
#define __ZQH_COMMON_UART_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

void uart0_tx(char *a, int len) {
    for (int i = 0; i < len; i++) {
        while(((*UART0_TXDATA) & 0x80000000) != 0);
        *UART0_TXDATA = a[i];
    }
}

void uart0_tx_flush() {
    while(((*UART0_TXDATA) & 0x80000000) != 0);
}

char uart0_rx_stall() {
    uint32_t rxdata;
    rxdata = *UART0_RXDATA;
    while((rxdata & 0x80000000) != 0){
        rxdata = *UART0_RXDATA;
    }
    return rxdata;
}

char uart0_rx() {
    uint32_t rxdata;
    rxdata = *UART0_RXDATA;
    return rxdata;
}
#endif
