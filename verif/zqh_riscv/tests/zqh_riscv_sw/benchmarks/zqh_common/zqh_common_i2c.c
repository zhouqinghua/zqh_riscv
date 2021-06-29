#ifndef __ZQH_COMMON_I2C_C
#define __ZQH_COMMON_I2c_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

char i2c_status_read() {
    return *I2C_STATUS;
}

void i2c_wait_no_busy() {
    char i2c_status = 0x02; 
    while((i2c_status & 0x02) != 0) {
        i2c_status = i2c_status_read();
    }
}

int i2c_arb_lost_chk() {
    char i2c_status; 

    //wait cmd finish
    i2c_wait_no_transfer_in_progress();

    i2c_status = i2c_status_read();
    //check arb_lost bit
    if ((i2c_status & 0x04) != 0) {
        return 1;
    }
    else {
        return 0;
    }
}

void i2c_cmd_start() {
    *I2C_CMD = 0x01;
    while(i2c_arb_lost_chk()) {
        *I2C_CMD = 0x01;//retry this cmd
    }
}
void i2c_cmd_start_write() {
    *I2C_CMD = 0x09;
    while(i2c_arb_lost_chk()) {
        printf_zqh("i2c arb lost, retry cmd %x\n", 0x09);
        *I2C_CMD = 0x09;//retry this cmd
    }
}
void i2c_cmd_write() {
    *I2C_CMD = 0x08;
}
void i2c_cmd_write_stop() {
    *I2C_CMD = 0x0a;
}
void i2c_cmd_start_write_stop() {
    *I2C_CMD = 0x0b;
    while(i2c_arb_lost_chk()) {
        *I2C_CMD = 0x0b;//retry this cmd
    }
}
void i2c_cmd_start_write_read_stop() {
    *I2C_CMD = 0x0f;
    while(i2c_arb_lost_chk()) {
        *I2C_CMD = 0x0f;//retry this cmd
    }
}

void i2c_cmd_start_read_ack() {
    *I2C_CMD = 0x05;
    while(i2c_arb_lost_chk()) {
        *I2C_CMD = 0x05;//retry this cmd
    }
}
void i2c_cmd_start_read_nack() {
    *I2C_CMD = 0x15;
    while(i2c_arb_lost_chk()) {
        *I2C_CMD = 0x15;//retry this cmd
    }
}
void i2c_cmd_read(int a) {
    if (a == 0) {
        *I2C_CMD = 0x04;
    }
    else {
        *I2C_CMD = 0x14;
    }
}
void i2c_cmd_read_ack() {
    *I2C_CMD = 0x04;
}
void i2c_cmd_read_nack() {
    *I2C_CMD = 0x14;
}
void i2c_cmd_read_ack_stop() {
    *I2C_CMD = 0x06;
}
void i2c_cmd_read_nack_stop() {
    *I2C_CMD = 0x16;
}

void i2c_cmd_stop() {
    *I2C_CMD = 0x02;
    while(i2c_arb_lost_chk()) {
        printf_zqh("i2c arb lost, retry cmd %x\n", 0x02);
        *I2C_CMD = 0x02;//retry this cmd
    }
}

void i2c_cmd_start_stop() {
    *I2C_CMD = 0x03;
    while(i2c_arb_lost_chk()) {
        *I2C_CMD = 0x03;//retry this cmd
    }
}


void i2c_data_write(char a) {
    *I2C_DATA = a;
}

char i2c_data_read() {
    return *I2C_DATA;
}

void i2c_wait_no_transfer_in_progress() {
    char i2c_status = 0x40; 
    while((i2c_status & 0x40) != 0) {
        i2c_status = i2c_status_read();
    }
}
#endif
