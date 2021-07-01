#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"
#include "zqh_common_init.c"
#include "zqh_common_exceptions.c"

int main (int argc, char** argv)
{
    zqh_common_csr_cfg();

    //
    //dma read/write teset
    //cross: rsize, wsize, source_addr lsb, dest_addr lsb, length lsb
    //{{{
    printf_zqh("dma test start\n");
    //config reg access
    int chn = 0;
    int chn_num = 1;
    uint8_t  dma_rsize = 6;
    uint8_t  dma_wsize = 6;
    uint8_t  dma_order = 0;
    uint8_t  dma_repeat = 0;
    uint64_t dma_dest_buffer[4][32];
    //uint64_t dma_source = 0x80000000;
    //uint64_t dma_source = 0x80001100;
    uint64_t dma_source = MAIN_MEM_BASE;
    uint64_t dma_dest;
    //dma_dest = 0x80100000;
    //dma_dest = MAIN_MEM_BASE + 0x00010000;
    //dma_dest = (MAIN_MEM_BASE + (1 << (10 + 2)) - 128);//cross 2 ddr banks
    //dma_dest = 0x80010001;
    dma_dest = dma_dest_buffer[0];
    uint32_t dma_bytes = 256;
    //uint32_t dma_bytes = 256;
    //uint32_t dma_bytes = 192;
    //uint32_t dma_bytes = 128;
    //uint32_t dma_bytes = 129;
    //uint32_t dma_bytes = 256 - 32 + 16 + 8 + 4 + 2 + 1;
    //uint32_t dma_bytes = 16 + 8 + 4 + 2 + 1;
    //uint32_t dma_bytes = 32 + 16 + 8 + 4 + 2 + 1;
    //uint32_t dma_bytes = 64;
    volatile uint32_t *dma_source_ptr;
    volatile uint32_t *dma_dest_ptr;
    uint64_t dma_source_chn_offset = dma_bytes;
    //uint64_t dma_source_chn_offset = 1 << 15;//ddr diffrent row, same bank
    //uint64_t dma_source_chn_offset = 1 << 12;//ddr same row, different bank
    //
    uint64_t dma_dest_chn_offset = dma_bytes;
    //uint64_t dma_dest_chn_offset = 1 << 15;//ddr diffrent row, same bank
    //uint64_t dma_dest_chn_offset = 1 << 12;//ddr same row, different bank

    for (int i = 0; i < chn_num; i++) {
        chn = i;
        printf_zqh("dma channel %0d do\n", chn);

        *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) | 0x1;//set claim
        //*(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) | 0x0c000000;//enable interrupt
        *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) | 0x00000000;//disable interrupt

        *(DMA_NEXT_CONFIG (chn)) = (dma_rsize << 28) | (dma_wsize << 24) | (dma_order << 3) | (dma_repeat << 2);
        *(DMA_NEXT_BYTES  (chn)) = dma_bytes;
        *(DMA_NEXT_DEST   (chn)) = dma_dest + dma_dest_chn_offset * chn;
        *(DMA_NEXT_SOURCE (chn)) = dma_source + dma_source_chn_offset * chn;

        printf_zqh("DMA_CONTROL     (%0d) post = %x\n",  chn, *(DMA_CONTROL     (chn)));
        printf_zqh("DMA_NEXT_CONFIG (%0d) post = %x\n",  chn, *(DMA_NEXT_CONFIG (chn)));
        printf_zqh("DMA_NEXT_BYTES  (%0d) post = %lx\n", chn, *(DMA_NEXT_BYTES  (chn)));
        printf_zqh("DMA_NEXT_DEST   (%0d) post = %lx\n", chn, *(DMA_NEXT_DEST   (chn)));
        printf_zqh("DMA_NEXT_SOURCE (%0d) post = %lx\n", chn, *(DMA_NEXT_SOURCE (chn)));


        //tmp dma_source_ptr = dma_source;
        dma_dest_ptr = dma_dest + dma_dest_chn_offset * chn;
        //tmp dma_source = dma_source + dma_bytes;


        //for (int j = 0; j < dma_bytes/4; j++) {
        //    printf_zqh("dma pre dest[%x] = %x\n", dma_dest_ptr + j, *(dma_dest_ptr + j));
        //}

        //flush dest address first
        for (int j = 0; j < dma_bytes/4; j++) {
            //*DC_L1_FLUSH_IO_ADDR(0) = dma_dest_ptr + j;
            dc_l1_flush(dma_dest_ptr + j);
        }
    }

    for (int i = 0; i < chn_num; i++) {
        chn = i;
        *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) | 0x2;//set run
    }

    int data_print_num = 8;
    for (int i = 0; i < chn_num; i++) {
        chn = i;
        dma_dest_ptr = (dma_dest & 0xfffffffc) + dma_dest_chn_offset * chn;
        while(1) {
            //interrupt enable
            if ((*(DMA_CONTROL(chn)) & 0x0c000000) != 0) {
                //check run flag is cleared by interrupt process
                if ((*(DMA_CONTROL(chn)) & 0x2) == 0) {
                    //printf_zqh("dma channel %0d interrupt process done\n", chn);
                    for (int j = 0; j < data_print_num; j++) {
                        printf_zqh("dma channel %0d interrupt post dest[%x] = %x\n", chn, dma_dest_ptr + j, *(dma_dest_ptr + j));
                    }
                    *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) & 0xfffffffe;//clean claim, release dma
                    break;
                }
            }
            else {
                //check done/error flag
                if ((*(DMA_CONTROL(chn)) & 0xc0000000) != 0) {
                    //printf_zqh("dma channel %0d sw scan done\n", chn);
                    for (int j = 0; j < data_print_num; j++) {
                        printf_zqh("dma channel %0d sw scan post dest[%x] = %x\n", chn, dma_dest_ptr + j, *(dma_dest_ptr + j));
                    }

                    *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) & 0xfffffffd;//clean run, stop dma
                    *(DMA_CONTROL(chn)) = *(DMA_CONTROL(chn)) & 0xfffffffe;//clean claim, release dma
                    break;
                }
            }
        }
        //delay_zqh(500);
    }

    printf_zqh("dma test end\n");
    //while(1);
    //}}}

    //post_stop(0x01);
    return 0;
}
