#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"
#include "zqh_common_i2c.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();

    //gpio hw iof enable
    *GPIO_IOF_EN(0) = *GPIO_IOF_EN(0) | 0xc0;

    //
    //i2c test
    //{{{
    //i2c eeprom write/read
    printf_zqh("i2c eeprom access start\n");

    for (int i = 0; i < 4; i++){
        i2c_data_write(0xa0);//page0 write
        i2c_cmd_start_write();
        i2c_wait_no_transfer_in_progress();

        i2c_data_write(i);//memory block address
        i2c_cmd_write();
        i2c_wait_no_transfer_in_progress();

        i2c_data_write(i);//write data
        i2c_cmd_write_stop();
        i2c_wait_no_transfer_in_progress();

        //delay_zqh(100);//wait write action done

        printf_zqh("i2c eeprom write adddress = %x, data = %x\n", i, i);
    }

    for (int i = 0; i < 4; i++){
        i2c_data_write(0xa0);//page0, dummy write
        i2c_cmd_start_write();
        i2c_wait_no_transfer_in_progress();

        i2c_data_write(i);//memory block address, dummy write
        i2c_cmd_write();
        i2c_wait_no_transfer_in_progress();

        i2c_data_write(0xa1);//device read, page0
        i2c_cmd_start_write();
        i2c_wait_no_transfer_in_progress();

        i2c_cmd_read_nack_stop();
        i2c_wait_no_transfer_in_progress();

        printf_zqh("i2c eeprom read adddress = %x, data = %x\n", i, i2c_data_read());
    }
    printf_zqh("i2c eeprom access end\n");


    printf_zqh("i2c test end\n");
    //}}}

    //post_stop(0x01);
    return 0;
}
