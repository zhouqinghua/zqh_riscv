#ifndef __ZQH_COMMON_SPI_C
#define __ZQH_COMMON_SPI_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

char spi0_tx_rx_byte(char a, int rx) {
    //wait tx_fifo none full
    uint32_t txdata;
    txdata = 0x80000000;
    while((txdata & 0x80000000) != 0) {
        txdata = *SPI0_TXDATA;
    }
    *SPI0_TXDATA = a;

    //wait tx_fifo empty
    uint32_t ip;
    do {
        ip = *SPI0_IP;
        ip = ip & 0x01;
    }while(ip == 0);

    //wait rx_fifo none empty
    uint32_t rxdata = 0x80000000;
    if (rx) {
        while((rxdata & 0x80000000) != 0){
            rxdata = *SPI0_RXDATA;
        }
    }
    return rxdata;
}


uint32_t spi0_norflash_read_jedec_id() {
    uint32_t id;
    uint32_t rx_data;
    //use hold mode
    *SPI0_CSMODE = 2; //0: auto, 1: reserved, 2: hold, 3: off
    *SPI0_TXMARK = 1; //if tx_fifo is empty, ip.txwm will be valid
    *SPI0_FMT = 0x00080008; //len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    //send cmd
    spi0_tx_rx_byte(0x9f, 0);


    //recieve 3 byte data
    *SPI0_FMT = *SPI0_FMT & 0xfffffff7; //dir = 0(rx)
    id = 0;
    for (int i = 0; i < 3; i++) {
        rx_data = spi0_tx_rx_byte(0, 1);
        id = (rx_data << ((2 - i)*8)) | id;
    }

    //reset to auto mode
    *SPI0_CSMODE = 0;

    return id;
}

uint64_t spi0_norflash_read_unique_id() {
    uint64_t id;
    uint64_t rx_data;
    //use hold mode
    *SPI0_CSMODE = 2; //0: auto, 1: reserved, 2: hold, 3: off
    *SPI0_TXMARK = 1; //if tx_fifo is empty, ip.txwm will be valid
    *SPI0_FMT = 0x00080008; //len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    //send cmd
    spi0_tx_rx_byte(0x4b, 0);

    //send 4 dumy byte
    for (int i = 0; i < 4; i++) {
        spi0_tx_rx_byte(0, 0);
    }

    //recieve 8 byte data
    *SPI0_FMT = *SPI0_FMT & 0xfffffff7; //dir = 0(rx)
    id = 0;
    for (int i = 0; i < 8; i++) {
        rx_data = spi0_tx_rx_byte(0, 1);
        id = (rx_data << ((7 - i)*8)) | id;
    }

    //reset to auto mode
    *SPI0_CSMODE = 0;

    return id;
}

void spi0_norflash_write_enable() {
    //use hold mode
    *SPI0_CSMODE = 2; //0: auto, 1: reserved, 2: hold, 3: off
    *SPI0_TXMARK = 1; //if tx_fifo is empty, ip.txwm will be valid
    *SPI0_FMT = 0x00080008; //len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    //send cmd
    spi0_tx_rx_byte(0x06, 0);

    //reset to auto mode
    *SPI0_CSMODE = 0;
}

uint32_t spi0_norflash_read_sr(uint32_t num) {
    uint32_t sr;
    //use hold mode
    *SPI0_CSMODE = 2; //0: auto, 1: reserved, 2: hold, 3: off
    *SPI0_TXMARK = 1; //if tx_fifo is empty, ip.txwm will be valid
    *SPI0_FMT = 0x00080008; //len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    //send cmd
    uint8_t cmd;
    if (num == 1) {
        cmd = 0x05;
    }
    else if (num == 2) {
        cmd = 0x35;
    }
    else if (num == 3) {
        cmd = 0x15;
    }
    else {
        cmd = 0x05;
    }
    spi0_tx_rx_byte(cmd, 0);

    //recieve 1 byte data
    *SPI0_FMT = *SPI0_FMT & 0xfffffff7; //dir = 0(rx)
    sr = spi0_tx_rx_byte(0, 1);

    //reset to auto mode
    *SPI0_CSMODE = 0;

    return sr;
}

void spi0_norflash_chip_erase() {
    spi0_norflash_write_enable();

    //use hold mode
    *SPI0_CSMODE = 2; //0: auto, 1: reserved, 2: hold, 3: off
    *SPI0_TXMARK = 1; //if tx_fifo is empty, ip.txwm will be valid
    *SPI0_FMT = 0x00080008; //len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    //send cmd
    spi0_tx_rx_byte(0xc7, 0);

    //reset to auto mode
    *SPI0_CSMODE = 0;

    //wait busy clear
    uint32_t sr_busy;
    sr_busy = 1;
    while(sr_busy) {
        sr_busy = spi0_norflash_read_sr(1) & 0x01;
    }
}

void spi0_norflash_read(uint32_t addr, uint8_t *buf, uint32_t len) {
    //uint8_t rx_data;
    //use hold mode
    *SPI0_CSMODE = 2; //0: auto, 1: reserved, 2: hold, 3: off
    *SPI0_TXMARK = 1; //if tx_fifo is empty, ip.txwm will be valid
    *SPI0_FMT = 0x00080008; //len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    //send read cmd
    spi0_tx_rx_byte(0x03, 0);


    //send 3 byte address
    for (int i = 0; i < 3; i++) {
        spi0_tx_rx_byte(addr >> ((2 - i) * 8), 0);
    }

    //recieve data
    *SPI0_FMT = *SPI0_FMT & 0xfffffff7; //dir = 0(rx)
    //rx_data = spi0_tx_rx_byte(0, 1);
    for (int i = 0; i < len; i++) {
        *(buf+i) = spi0_tx_rx_byte(0, 1);
    }


    //reset to auto mode
    *SPI0_CSMODE = 0;

    //return rx_data;
}

void spi0_norflash_write(uint32_t addr, uint8_t *buf, uint32_t len) {

    spi0_norflash_write_enable();


    //use hold mode
    *SPI0_CSMODE = 2; //0: auto, 1: reserved, 2: hold, 3: off
    *SPI0_TXMARK = 1; //if tx_fifo is empty, ip.txwm will be valid
    *SPI0_FMT = 0x00080008; //len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)

    //send write cmd
    spi0_tx_rx_byte(0x02, 0);

    //send 3 byte address
    for (int i = 0; i < 3; i++) {
        spi0_tx_rx_byte(addr >> ((2 - i) * 8), 0);
    }

    //send write data
    for (int i = 0; i < len; i++) {
        spi0_tx_rx_byte(*(buf+i), 0);
    }

    //wait tx_fifo empty
    uint32_t ip = 0;
    while((ip & 0x01) == 0) {
        ip = *SPI0_IP;
    }

    //reset to auto mode
    *SPI0_CSMODE = 0;

    //wait busy clear
    uint32_t sr_busy;
    sr_busy = 1;
    while(sr_busy) {
        sr_busy = spi0_norflash_read_sr(1) & 0x01;
    }
}

void spi0_tx(char *a, int len, uint32_t fmt) {
    uint32_t txdata;

    //*SPI0_FMT = 0x00080000;
    *SPI0_FMT = fmt;
    for (int i = 0; i < len; i++) {
        txdata = *SPI0_TXDATA;
        while((txdata & 0x80000000) != 0) {
            txdata = *SPI0_TXDATA;
        }
        *SPI0_TXDATA = a[i];
    }
}

void spi0_tx_single(char *a, int len, int endian) {
    uint32_t fmt;
    if (endian) {
        fmt = 0x00080004;
    }
    else {
        fmt = 0x00080000;
    }
    spi0_tx(a, len, fmt);
}

void spi0_tx_single_big_endian(char *a, int len) {
    spi0_tx_single(a, len, 0);
}

void spi0_tx_single_little_endian(char *a, int len) {
    spi0_tx_single(a, len, 1);
}

void spi0_tx_dual(char *a, int len, int endian) {
    uint32_t fmt;
    if (endian) {
        fmt = 0x00080005;
    }
    else {
        fmt = 0x00080001;
    }
    spi0_tx(a, len, fmt);
}

void spi0_tx_dual_big_endian(char *a, int len) {
    spi0_tx_dual(a, len, 0);
}

void spi0_tx_dual_little_endian(char *a, int len) {
    spi0_tx_dual(a, len, 1);
}

void spi0_tx_quad(char *a, int len, int endian) {
    uint32_t fmt;
    if (endian) {
        fmt = 0x00080006;
    }
    else {
        fmt = 0x00080002;
    }
    spi0_tx(a, len, fmt);
}

void spi0_tx_quad_big_endian(char *a, int len) {
    spi0_tx_quad(a, len, 0);
}

void spi0_tx_quad_little_endian(char *a, int len) {
    spi0_tx_quad(a, len, 1);
}

char spi0_rx_stall() {
    uint32_t rxdata;
    rxdata = *SPI0_RXDATA;
    while((rxdata & 0x80000000) != 0){
        rxdata = *SPI0_RXDATA;
    }
    return rxdata;
}

uint32_t spi0_rx() {
    //wait rx_fifo none empty
    uint32_t rxdata = 0x80000000;
        while((rxdata & 0x80000000) != 0){
            rxdata = *SPI0_RXDATA;
        }
    return rxdata;
}
#endif
