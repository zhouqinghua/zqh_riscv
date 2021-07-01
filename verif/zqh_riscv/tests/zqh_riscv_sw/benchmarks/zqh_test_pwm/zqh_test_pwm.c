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
    //gpio hw iof enable
    *GPIO_IOF_EN(0) = *GPIO_IOF_EN(0) | 0x3c;

    //set pwm0 reg
    *PWM0_PWMCFG = 0x00000000;//initial clear
    *PWM0_PWMCOUNT = 0x00000000;
    *PWM0_PWMMAX = 0x00000fff;
    *PWM0_PWMCMP0 = 0x00000020;
    *PWM0_PWMCMP1 = 0x000000080;
    *PWM0_PWMCMP2 = 0x0000000200;
    *PWM0_PWMCMP3 = 0x0000000800;
    *PWM0_PWMCFG = 0x00001200;//cmpgang=0x0, cmpcenter=0x0, enalways=1,  deglitch=0, zerocmp=1, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x00002000;//cmpgang=0x0, cmpcenter=0x0, enoneshot=1, deglitch=0, zerocmp=0, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x00001600;//cmpgang=0x0, cmpcenter=0x0, enalways=1,  deglitch=1, zerocmp=1, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x00001200;//cmpgang=0x0, cmpcenter=0x0, enalways=1,  deglitch=0, zerocmp=1, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x00001300;//cmpgang=0x0, cmpcenter=0x0, enalways=1,  deglitch=0, zerocmp=1, sticky=1, scale=0
    //*PWM0_PWMCFG = 0x000f1000;//cmpgang=0x0, cmpcenter=0xf, enalways=1,  deglitch=0, zerocmp=0, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x000f1000;//cmpgang=0x0, cmpcenter=0xf, enalways=1,  deglitch=0, zerocmp=0, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x000f1400;//cmpgang=0x0, cmpcenter=0xf, enalways=1,  deglitch=1, zerocmp=0, sticky=0, scale=0
    //*PWM0_PWMCFG = 0x07001200;//cmpgang=0x2, cmpcenter=0x0, enalways=1,  deglitch=0, zerocmp=1, sticky=0, scale=0
    //printf_zqh("PWM0_PWMCFG %x\n", *PWM0_PWMCFG);
 
    //
    //pwm test
    //{{{
    printf_zqh("pwm test start\n");
    delay_zqh(3000);

    printf_zqh("pwm test end\n");
    //}}}


    //post_stop(0x01);
    return 0;
}
