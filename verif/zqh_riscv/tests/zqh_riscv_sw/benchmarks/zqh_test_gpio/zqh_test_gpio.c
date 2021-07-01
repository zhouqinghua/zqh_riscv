#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();

    //
    //gpio test
    //{{{
    //key input at gpio0[8]-gpio0[11]
    printf_zqh("gpio test start\n");
    *GPIO_INPUT_EN(0) = *GPIO_INPUT_EN(0) | 0x0f00;//key1-key4
    //output at gpio0[12]-gpio0[19]
    *GPIO_OUTPUT_EN(0) = *GPIO_OUTPUT_EN(0) | 0xff000;

    //output value
    uint32_t gpio_out_v;
    uint32_t gpio_out_bit_v;
    gpio_out_v = 0x7f;
    *GPIO_OUTPUT_VAL(0) = *GPIO_OUTPUT_VAL(0) | 0xff000;//set to 1 first(led light off)

    //read input value
    //for (int i = 0; i < 4; i++) {
    //    printf_zqh("input gpio[%0d] = %0d\n", i, ((*GPIO_INPUT_VAL(0)) >> i) & 1);
    //}
    uint32_t pwmcmp_v;
    uint32_t key1_last_v;
    uint32_t key2_last_v;
    uint32_t key_cur_v;
    while(1) {
        key1_last_v = (*GPIO_INPUT_VAL(0) >> 8) & 0x01;
        key2_last_v = (*GPIO_INPUT_VAL(0) >> 9) & 0x01;
        delay_ms(100);

        //key1 capture, 0 valid
        key_cur_v = (*GPIO_INPUT_VAL(0) >> 8) & 0x01;
        if ((key_cur_v == 0) && (key1_last_v == 1)) {
            printf_zqh("input gpio0[8] valid\n");

            //shift right output value
            gpio_out_v = (gpio_out_v >> 1) | 0x80;
            if (gpio_out_v == 0xff) {
                gpio_out_v = 0x7f;
            }
            //*GPIO_OUTPUT_VAL(0) = gpio_out_v;
            *GPIO_OUTPUT_VAL(0) = (*GPIO_OUTPUT_VAL(0) & 0xfff00fff) | (gpio_out_v << 12);
        }

        //key2 capture, 0 valid
        key_cur_v = (*GPIO_INPUT_VAL(0) >> 9) & 0x01;
        if ((key_cur_v == 0) && (key2_last_v == 1)) {
            printf_zqh("input gpio0[9] valid\n");

            //shift left output value
            gpio_out_v = ((gpio_out_v << 1) & 0xff) | 0x01;
            if (gpio_out_v == 0xff) {
                gpio_out_v = 0xfe;
            }
            //*GPIO_OUTPUT_VAL(0) = gpio_out_v;
            *GPIO_OUTPUT_VAL(0) = (*GPIO_OUTPUT_VAL(0) & 0xfff00fff) | (gpio_out_v << 12);
        }
    }

    printf_zqh("gpio test end\n");
    //}}}


    //post_stop(0x01);
    return 0;
}
