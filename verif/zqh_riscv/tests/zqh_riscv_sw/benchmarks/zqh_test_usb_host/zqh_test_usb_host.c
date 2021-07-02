#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"
#include "zqh_common_usb.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();
    setStats(1);
    //gpio hw iof enable
    *GPIO_IOF_EN(1) = *GPIO_IOF_EN(1) | 0x30000000;

    printf("usb host test start\n");
    usb_host_test();
    printf("usb host test end\n");

    setStats(0);
    return 0;
}
