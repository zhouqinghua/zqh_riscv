#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_exceptions.c"
#include "zqh_common_init.c"
#include "zqh_common_atomic.c"

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

    zqh_common_csr_cfg();

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

    post_stop(0x01);
    return 0;
}
