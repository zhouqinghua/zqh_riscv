#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"

uintptr_t __attribute__((weak)) handle_trap(uintptr_t cause, uintptr_t epc, uintptr_t regs[32])
{
}


void delay_sw(int a) {
    for (int i = 0; i < a; i ++) {
        asm volatile ("nop");
    }
}

//in 50MHz clock
//in ms: a = 1000 means 1 second
void delay_ms(uint32_t a) {
    for (uint32_t i = 0; i < a; i++) {
        for (uint32_t j = 0; j < 9375; j++) {
            asm volatile ("nop");
        }
    }
}

int pll_init() {
    //*CRG_CTRL_CORE_PLL_CFG = 0x01010a02;//1GHz
    *CRG_CTRL_CORE_PLL_CFG = 0x01010104;//50MHz as FPGA's
    while(1) {
        if ((*CRG_CTRL_CORE_PLL_CFG & 0x80000000) != 0) {
            *CRG_CTRL_CORE_PLL_CFG = *CRG_CTRL_CORE_PLL_CFG & 0xfeffffff;//disable bypass
            break;
        }
    }
    #ifdef HAS_ETH
    *CRG_CTRL_ETH_PLL_CFG = 0x03010508;
    while(1) {
        if ((*CRG_CTRL_ETH_PLL_CFG & 0x80000000) != 0) {
            *CRG_CTRL_ETH_PLL_CFG = *CRG_CTRL_ETH_PLL_CFG & 0xfeffffff;//disable bypass
            *CRG_CTRL_ETH_PLL_CFG = *CRG_CTRL_ETH_PLL_CFG | 0x02000000;//set en
            //*CRG_CTRL_RESET_CFG = *CRG_CTRL_RESET_CFG | 0x20; //dereset eth
            break;
        }
    }
    #endif
    #ifdef HAS_DDR
    uint32_t ddr_pll_mul;
    #if (DDR_SPEED == 1600)
        ddr_pll_mul = 8;
    #elif (DDR_SPEED == 800)
        ddr_pll_mul = 4;
    #endif
    //tmp *CRG_CTRL_DDR_PLL_CFG = 0x03010802;
    *CRG_CTRL_DDR_PLL_CFG = 0x03010002 | (ddr_pll_mul << 8);
    while(1) {
        if ((*CRG_CTRL_DDR_PLL_CFG & 0x80000000) != 0) {
            *CRG_CTRL_DDR_PLL_CFG = *CRG_CTRL_DDR_PLL_CFG & 0xfeffffff;//disable bypass
            *CRG_CTRL_DDR_PLL_CFG = *CRG_CTRL_DDR_PLL_CFG | 0x02000000;//set en
            *CRG_CTRL_RESET_CFG = *CRG_CTRL_RESET_CFG | 0x09; //dereset ddr_phy and ddr_mc
            break;
        }
    }
    #endif
}

size_t strlen(const char *s)
{
  const char *p = s;
  while (*p)
    p++;
  return p - s;
}

void uart0_tx_char(char ch) {
    while(((*UART0_TXDATA) & 0x80000000) != 0);
    *UART0_TXDATA = ch;
}

char uart0_rx_char() {
    uint32_t rxdata;
    rxdata = *UART0_RXDATA;
    while((rxdata & 0x80000000) != 0){
        rxdata = *UART0_RXDATA;
    }
    return rxdata;
}

const char i2a_tab[16] = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};
char* my_itoa_32(uint32_t a, char *buf) {
    uint32_t len;
    len = 8;
    for (int i = 0; i < len; i++) {
        buf[len - 1 - i] = i2a_tab[(a >> (i*4))%16];
    }
    buf[len] = 0;
    return buf;
}


void simple_print_str(char *str) {
    int len;

    len = strlen(str);
    for (int i = 0; i< len; i++) {
        simple_print_char(str[i]);
    }
}

char* simple_uart0_get_str(char *buf) {
    char tmp_str;
    uint32_t idx;
    uint32_t done;
    idx = 0;
    done = 0;
    while(done == 0) {
        tmp_str = uart0_rx_char();
        //string to long, force to enter char
        if (idx > 80) {
            tmp_str = '\n';
        }

        if (tmp_str == '\n') {
            done = 1;
        }
        buf[idx] = tmp_str;
        //simple_print_str("get one char\n");
        //simple_print_char(tmp_str);
        idx ++;
    }
    buf[idx] = 0;
    return buf;
}

uint32_t uint_max(uint32_t a, uint32_t b) {
    return (a > b) ? a : b;
}


__thread char str_buf[100];
const uint8_t mr0_cas_table[15] = {0x0,0x0,0x0,0x0,0x0,0x2,0x4,0x6,0x8,0xa,0xc,0xe,0x1,0x3,0x5};
const uint8_t mr0_wr_table[17] = {0x0,0x0,0x0,0x0,0x0,0x1,0x2,0x3,0x4,0x0,0x5,0x0,0x6,0x0,0x7,0x0,0x0};
int ddr_init() {
    uint32_t dll_off;
    uint32_t ddr_real_freq;
    uint32_t wr_dqs_dll_delay;
    uint32_t wr_dq_dll_delay;
    uint32_t rd_dqs_dll_delay;
    uint32_t tck;
    uint32_t tras;
    uint32_t trc;
    uint32_t trcd;
    uint32_t trp;
    uint32_t tcke;
    uint32_t cl;
    uint32_t trrd;
    uint32_t tfaw;
    uint32_t twr;
    uint32_t tccd;
    uint32_t bstlen;
    uint32_t trfc_min;
    uint32_t trfc_max;
    uint32_t tref;
    uint32_t tdll;
    uint32_t tzqinit;
    uint32_t tzqcl;
    uint32_t tzqcs;
    uint32_t trtp;
    uint32_t tmrd;
    uint32_t twtr;
    uint32_t tmod;
    uint32_t tras_max;
    uint32_t cwl; //min 5, max 10
    uint32_t al;
    uint32_t wl;
    uint32_t rl;
    uint32_t mr0,mr1,mr2,mr3;
    uint32_t mr1_al;
    uint32_t mr1_rtt_nom;
    uint32_t mr2_cwl;
    uint32_t mr2_rtt_wr;

    dll_off = 0;

    //real ddr speed in fpga
    ddr_real_freq = 100;//100MHz

    if (dll_off) {
        wr_dqs_dll_delay = 0x00;
        wr_dq_dll_delay = 0x40;
        rd_dqs_dll_delay = 0xc8;
    }
    else {
        wr_dqs_dll_delay = 0x00;
        wr_dq_dll_delay = 0x40;
        rd_dqs_dll_delay = 0x40;
    }

    //
    //initial ddr
    *DDR_MC_CTRL_CFG_REG(0) = 0x600;//clean start, use DDR3

    //config ddr_phy's ac regs
    *DDR_MC_PHY_AC_CFG_REG(0) = 0;
    *DDR_MC_PHY_AC_CFG_REG(1) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(2) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(3) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(4) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(5) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(6) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(7) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(8) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(9) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(10) = 0; //TBD
    *DDR_MC_PHY_AC_CFG_REG(11) = 0; //TBD

    //config ddr_phy's data slice regs
    for (int i = 0; i < DDR_MC_SLICE_NUM; i++) {
        *DDR_MC_PHY_DS_CFG_REG(0+i*8) = 0x00000027;
        *DDR_MC_PHY_DS_CFG_REG(1+i*8) = 0x00000027;
        *DDR_MC_PHY_DS_CFG_REG(2+i*8) = 0x00000000;
        *DDR_MC_PHY_DS_CFG_REG(3+i*8) = 0x000000ff;//dll_master_ctrl
        //tmp *DDR_MC_PHY_DS_CFG_REG(4+i*8) = 0x0040c080;//dll_slave_ctrl
        //*DDR_MC_PHY_DS_CFG_REG(4+i*8) = 0x00404000;//dll_slave_ctrl, @ddr 1600
        *DDR_MC_PHY_DS_CFG_REG(4+i*8) = (rd_dqs_dll_delay << 16) | (wr_dq_dll_delay << 8) | wr_dqs_dll_delay;//dll_slave_ctrl, @100MHz
        *DDR_MC_PHY_DS_CFG_REG(5+i*8) = 0x00000000;
        *DDR_MC_PHY_DS_CFG_REG(6+i*8) = 0x00000000;
        *DDR_MC_PHY_DS_CFG_REG(7+i*8) = 0x00000000;
    }

   simple_print_str("ddr_init step 0\n");



    #if (DDR_SPEED == 1600)
        tck = 1250;//ps
        cwl = 8;
    #elif (DDR_SPEED == 800)
        tck = 2500;//ps
        cwl = 5;
    #endif
    if (dll_off == 1) {
        cwl = 6;
    }

    #ifdef DDR_PHY_X8
        #if (DDR_SPEED == 1600)
            trrd = 5;
            tfaw = 24;
        #elif (DDR_SPEED == 800)
            trrd = 4;
            tfaw = 16;
        #endif
    #endif
    #ifdef DDR_PHY_X16
        #if (DDR_SPEED == 1600)
            trrd = 6;
            tfaw = 32;
        #elif (DDR_SPEED == 800)
            trrd = 4;
            tfaw = 20;
        #endif
    #endif

    #if (DDR_SPEED == 1600)
        tras = 28;
        trc = 39;
        trcd = 11;
        trp = 11;
        tcke = 4;
        cl = 11;
        tref = 6250;

        tref = tref/(1600/(ddr_real_freq*2));
    #elif (DDR_SPEED == 800)
        tras = 15;
        trc = 21;
        trcd = 6;
        trp = 6;
        tcke = 3;
        cl = 6;
        tref = 6250/2;

        tref = tref/(800/(ddr_real_freq*2));
    #endif




    twr = (15000/tck) + (((15000%tck) != 0) ? 1:0);
    tccd = 4;
    bstlen = 3;
    trfc_min = 260000/tck;
    trfc_max = 70200000/tck;
    tdll = 512;
    tzqinit = 512;
    tzqcl = 256;
    tzqcs = 64;
    trtp = uint_max(7500/tck, 4);
    tmrd = 4;
    twtr = 7500/tck;
    tmod = uint_max(15000/tck, 12);
    tras_max = 0x60e9/tck;
    mr2_cwl = cwl - 5;
    mr1_al = 2;
    if (mr1_al == 0) {
        al = 0;
    }
    else {
        al = cl - mr1_al;
    }
    wl = cwl + al;
    rl = cl + al;
    if (dll_off) {
        mr1_rtt_nom = 0;
        mr2_rtt_wr = 0;
    }
    else {
        mr1_rtt_nom = 1;
        mr2_rtt_wr = 1;
    }

    mr0 = (mr0_wr_table[twr] << 9) | (1 << 8) | ((mr0_cas_table[cl] >> 1) << 4) | (1 << 3) | ((mr0_cas_table[cl] & 1) << 2) | 0;//0x0d78;
    mr1 = (((mr1_rtt_nom >> 2) & 1) << 9) | (((mr1_rtt_nom >> 1) & 1) << 6) | (mr1_al << 3) | ((mr1_rtt_nom & 1) << 2) | (1 << 1) | dll_off;//0x0016;
    mr2 = (mr2_rtt_wr << 9) | (0 << 8) | (0 << 7) | (0 << 6) | (mr2_cwl << 3) | 0;//0x0218;
    mr3 = 0;


    uint32_t rdlat_adj;
    uint32_t twrlat_adj;
    uint32_t tdfi_ctrl_delay;
    uint32_t tphy_wrdata;
    if (dll_off) {
        rdlat_adj = rl - 1;
    }
    else {
        rdlat_adj = rl;
    }

    twrlat_adj = wl;

    //tmp test
    //twrlat_adj = twrlat_adj + 1;
    
    tdfi_ctrl_delay = 2;
    tphy_wrdata = 1;

    uint32_t odt_en, todth_rd, todth_wr, todtl_2cmd;
    if (dll_off) {
        odt_en = 0;
    }
    else {
        odt_en = 1;
    }
    todth_rd = 4;
    todth_wr = 6;
    todtl_2cmd = 0;

    uint32_t dll_rst_adj_dly, dll_rst_delay;
    dll_rst_adj_dly=10;
    dll_rst_delay=10;

    uint32_t trst_n, tcke_inactive;
    uint32_t txsnr;
    #ifdef IMP_MODE_SIM
    trst_n = 200;//trst_n, simulation need less
    tcke_inactive = 500;//tcke_inactive, simulation need less
    #else
    trst_n = 200000;
    tcke_inactive = 500000;
    #endif
    txsnr = 300;


    *DDR_MC_CTRL_CFG_REG(18) = (trp << 16) | (bstlen << 8) | (twr + trp);//trp_ab = trp = 11, bstlen = 3(burst 8), tdal = twr + trp
    *DDR_MC_CTRL_CFG_REG(51) = 0xffffffff;//interrupt disable
    *DDR_MC_CTRL_CFG_REG(136) = 0xffffffff;//set int_ack to clean int_status
    *DDR_MC_CTRL_CFG_REG(20) = (tref << 16) | (trfc_min + 1);//tref = 6250, trfc = > min and < max
    *DDR_MC_CTRL_CFG_REG(19) = 1 << 24;//tref_enable
    *DDR_MC_CTRL_CFG_REG(11) = (cl << 25) | (0 << 24) | tdll;//cas latency = 11, tdll = 512. cas_lat[0] is harf cycle increase flag, cas_lat[31:25] is latency
    *DDR_MC_CTRL_CFG_REG(12) = (tccd << 24) | (0 << 16) | (al << 8) | wl;//tccd = 4, tbst_int_interval = 0, additive latency = 9, wrlat = 17
    *DDR_MC_CTRL_CFG_REG(26) = mr0 << 8;//mr0
    *DDR_MC_CTRL_CFG_REG(27) = (mr2 << 16) | mr1;//mr2, mr1
    *DDR_MC_CTRL_CFG_REG(28) = mr3 << 16;//mr3
    *DDR_MC_CTRL_CFG_REG(17) = (0 << 8) | twr;//ap, twr
    *DDR_MC_CTRL_CFG_REG(8) = trst_n;//trst_n, simulation need less
    *DDR_MC_CTRL_CFG_REG(9) = tcke_inactive;//tcke_inactive, simulation need less
    *DDR_MC_CTRL_CFG_REG(23) = txsnr;//txsnr
    *DDR_MC_CTRL_CFG_REG(37) = (tzqinit << 8) | 0;//tzqinit = zqcl * 2
    *DDR_MC_CTRL_CFG_REG(38) = (tzqcs << 16) | tzqcl;//tzqcs, tzqcl
    *DDR_MC_CTRL_CFG_REG(14) = (tmrd << 24) | (trtp << 16) | (tfaw << 8) | trp;//tmrd, trtp, tfaw = 24, trp
    *DDR_MC_CTRL_CFG_REG(16) = trcd << 24;//trcd
    *DDR_MC_CTRL_CFG_REG(13) = (twtr << 24) | (tras << 16) | (trc << 8) | trrd;//twtr, tras_min = 28, trc, trrd
    *DDR_MC_CTRL_CFG_REG(15) = (tras_max << 8) | tmod;//tras_max=0x1ffff, tmod
    *DDR_MC_CTRL_CFG_REG(112) = (tdfi_ctrl_delay << 16) | (twrlat_adj << 8) | rdlat_adj;//tdfi_ctrl_delay = 2, twrlat_adj = 17, rdlat_adj = 20
    *DDR_MC_CTRL_CFG_REG(128) = tphy_wrdata;//tphy_wrdata= 1
    *DDR_MC_CTRL_CFG_REG(68) = (odt_en << 24) | (todth_rd << 16) | (todth_wr << 8) | todtl_2cmd;//odt_en = 1, todth_rd = 4, todth_wr = 6, todtl_2cmd = 0
    *DDR_MC_CTRL_CFG_REG(105) = (dll_rst_adj_dly << 16) | dll_rst_delay;//dll_rst_adj_dly=10, dll_rst_delay=10

    //ddr_mc initial start
    *DDR_MC_CTRL_CFG_REG(0) = *DDR_MC_CTRL_CFG_REG(0) | 0x1;//set start

    simple_print_str("ddr_init step 1\n");

    //wait cke_status cke = 1
    uint32_t ddr_mc_reg;
    while(1) {
        ddr_mc_reg = *DDR_MC_CTRL_CFG_REG(104);
        if (((*DDR_MC_CTRL_CFG_REG(104)) & 0x0100) != 0) {
            delay_sw(300);//wait txpr ddr cycle
            simple_print_str("ddr_mc cke_status done\n");
            #ifndef IMP_MODE_SIM
            delay_ms(2000);
            #endif
            break;
        }
        else {
            delay_sw(300);//wait txpr ddr cycle
            simple_print_str("ddr_mc cke_status is:\n");
            simple_print_str(my_itoa_32(ddr_mc_reg, str_buf));
            simple_print_str("\n");
        }
    }

    //trigger mr0/1/2/3 write
    *DDR_MC_CTRL_CFG_REG(25) = 0x03020000;//all chip select, write mr0/1/2/3

   simple_print_str("ddr_init step 2\n");
    //wait mrs done
    while(1) {
        if (((*DDR_MC_CTRL_CFG_REG(49)) & 0x00020000) != 0) {
            simple_print_str("ddr_mc mrs done\n");
            #ifndef IMP_MODE_SIM
            delay_ms(1000);
            #endif
            break;
        }
    }

   simple_print_str("ddr_init step 3\n");
    while(1) {
        if ((*DDR_MC_CTRL_CFG_REG(49) & 0x10) != 0) {
            simple_print_str("ddr_mc init completed\n");
            #ifndef IMP_MODE_SIM
            delay_ms(1000);
            #endif
            break;
        }
    }


    //enable ap
    *DDR_MC_AP_CFG_REG(0) = 0xc0000000;//
    *DDR_MC_AP_CFG_REG(1) = 0x80000000;//enable
}


void simple_print_char(char ch) {
    //user uart
    #if PRINT_USE_UART == 1
        //while(((*UART0_TXDATA) & 0x80000000) != 0);
        //*UART0_TXDATA = ch;
        uart0_tx_char(ch);
    //use print_monitor
    #else
        *PRINT_PTR_HART(0) = ch;
    #endif

}

void uart0_init() {
    //gpio hw iof enable
    *GPIO_IOF_EN(0) = *GPIO_IOF_EN(0) | 0x3;

    *UART0_TXCTRL = 1;//enable tx, nstop = 0(1 stop bit)
    //*UART0_TXCTRL = 0;//disable tx
    //*UART0_TXCTRL = 3;//enable tx, nstop = 1(2 stop bit)
    //*UART0_TXCTRL = 0x5; //parity odd check
    //*UART0_TXCTRL = 0x9; //parity even check
    //*UART0_TXCTRL = 0xd; //parity bit force to 0
    //*UART0_TXDATA = 0;
    *UART0_RXCTRL = 1;//enable rx
    //*UART0_RXCTRL = 0;//disable rx
    //*UART0_RXCTRL = 0x5; //parity odd check
    *UART0_RXDATA = 0;
    *UART0_IE     = 0;
    //*UART0_DIV    = 2; //speedup simulation, use fastest speed
    *UART0_DIV    = 53; //57600 baud ratio @ 50MHz clock(FPGA)
}

void hw_init() {
    if (read_csr(mhartid) == 0) {
        pll_init();
        uart0_init();
        #ifdef HAS_DDR
        ddr_init();
        #endif
    }
    else {
        while(1);
    }
}

uint32_t load_img() {
    simple_print_str("bootloader start!\n");

    //simulation use this
    #ifdef IMP_MODE_SIM
    __asm__ __volatile__ ("fence.i");
    return MAIN_MEM_BASE;
    #endif


    delay_ms(2000);


    //char str_buf[100];
    //access sec_ctrl_info
    //get each section's info
    uint32_t *sec_ctrl_info_ptr;
    uint32_t sec_ctrl_info_num;
    //sec_ctrl_info's start address in flash
    //last 512 byte at the end of bootloader's 8KB space
    sec_ctrl_info_ptr = ((uint32_t *) 0x20001e00);
    sec_ctrl_info_num = *sec_ctrl_info_ptr;

    simple_print_str("sec_ctrl_info_num = 0x");
    simple_print_str(my_itoa_32(sec_ctrl_info_num, str_buf));
    simple_print_str("\n");

    uint32_t program_start_address;
    program_start_address = *(sec_ctrl_info_ptr + 1);
    simple_print_str("program_start_address = 0x");
    simple_print_str(my_itoa_32(program_start_address, str_buf));
    simple_print_str("\n");

    //print sec_ctrl_info
    //1st part is sec_ctrl_info_num
    //2nd part is program_start_address
    //3rd part is each section's info
    //each section info has 4 32bit info:
    //0: type
    //1: source address base
    //2: dest address base
    //3: length
    for (int i = 0; i < (sec_ctrl_info_num*4 + 2); i++) {
        simple_print_str("sec_ctrl_info[0x");
        simple_print_str(my_itoa_32(i, str_buf));
        simple_print_str("] = 0x");

        simple_print_str(my_itoa_32(*(sec_ctrl_info_ptr + i), str_buf));
        simple_print_str("\n");
    }

    //load main_img from flash to sram
    uint32_t sec_offset;
    //sec_type. 0: read only, 1: read write, need initial, 2: read write, no initial(clean to zero)
    uint32_t sec_type;
    uint32_t sec_source_addr;
    uint32_t sec_dest_addr;
    uint32_t sec_len;
    uint8_t *source_ptr_base;
    uint8_t *dest_ptr_base;
    uint8_t dest_data;
    uint8_t source_data;
    simple_print_str("load main_img from flash to sram\n");
    //delay_ms(2000);
    for (int i = 0; i < sec_ctrl_info_num; i++) {
        simple_print_str("load section[0x");
        simple_print_str(my_itoa_32(i, str_buf));
        simple_print_str("]\n");

        //jump 1st and 2nd part
        sec_offset = 2 + i*4;
        sec_type = *(sec_ctrl_info_ptr + sec_offset + 0);
        sec_source_addr = *(sec_ctrl_info_ptr + sec_offset + 1);
        sec_dest_addr = *(sec_ctrl_info_ptr + sec_offset + 2);
        sec_len = *(sec_ctrl_info_ptr + sec_offset + 3);

        simple_print_str("sec_type = 0x");
        simple_print_str(my_itoa_32(sec_type, str_buf));
        simple_print_str("\n");

        simple_print_str("sec_source_addr = 0x");
        simple_print_str(my_itoa_32(sec_source_addr, str_buf));
        simple_print_str("\n");

        simple_print_str("sec_dest_addr = 0x");
        simple_print_str(my_itoa_32(sec_dest_addr, str_buf));
        simple_print_str("\n");

        simple_print_str("sec_len = 0x");
        simple_print_str(my_itoa_32(sec_len, str_buf));
        simple_print_str("\n");
        //delay_ms(2000);

        source_ptr_base = (uint8_t *)sec_source_addr;
        dest_ptr_base = (uint8_t *)sec_dest_addr;

        if ((dest_ptr_base >= 0x20000000) && (dest_ptr_base <= 0x2fffffff)) {
            simple_print_str("jump flash xip space\n");
        }
        else {
            for (int j = 0; j < sec_len; j++) {
                if ((sec_type == 0) || (sec_type == 1)) {
                    source_data = *(source_ptr_base + j);
                }
                else {
                    source_data = 0;
                }
                *(dest_ptr_base + j) = source_data;

                ////if (i == 7) {
                ////if (dest_ptr_base + j == 0x40000000) {
                //    simple_print_str("load from address 0x");
                //    simple_print_str(my_itoa_32(source_ptr_base + j, str_buf));
                //    simple_print_str(" to 0x");
                //    simple_print_str(my_itoa_32(dest_ptr_base + j, str_buf));
                //    simple_print_str("\n");
                //    simple_print_str("load data = 0x");
                //    simple_print_str(my_itoa_32(source_data, str_buf));
                //    simple_print_str("\n");
                ////}
            }
        }
    }

    //verify main_img load data's correction
    for (int i = 0; i < sec_ctrl_info_num; i++) {
        simple_print_str("verify section[0x");
        simple_print_str(my_itoa_32(i, str_buf));
        simple_print_str("]\n");
        //delay_ms(2000);

        //jump 1st and 2nd part
        sec_offset = 2 + i*4;
        sec_type = *(sec_ctrl_info_ptr + sec_offset + 0);
        sec_source_addr = *(sec_ctrl_info_ptr + sec_offset + 1);
        sec_dest_addr = *(sec_ctrl_info_ptr + sec_offset + 2);
        sec_len = *(sec_ctrl_info_ptr + sec_offset + 3);

        source_ptr_base = (uint8_t *)sec_source_addr;
        dest_ptr_base = (uint8_t *)sec_dest_addr;
        if ((dest_ptr_base >= 0x20000000) && (dest_ptr_base <= 0x2fffffff)) {
            simple_print_str("jump flash xip space\n");
        }
        else {
            for (int j = 0; j < sec_len; j++) {
                dest_data = *(dest_ptr_base + j);
                if ((sec_type == 0) || (sec_type == 1)) {
                    source_data = *(source_ptr_base + j);
                }
                else {
                    source_data = 0;
                }

                if (dest_data != source_data) {
                    simple_print_str("verify fail:\n");
                    simple_print_str("dest_addr[0x");
                    simple_print_str(my_itoa_32(dest_ptr_base + j, str_buf));
                    simple_print_str("]'s data 0x");
                    simple_print_str(my_itoa_32(dest_data, str_buf));
                    simple_print_str(" != ");
                    simple_print_str("source_addr[0x");
                    simple_print_str(my_itoa_32(source_ptr_base + j, str_buf));
                    simple_print_str("]'s data 0x");
                    simple_print_str(my_itoa_32(source_data, str_buf));
                    simple_print_str("\n");
                    while(1);
                }
            }
        }
    }
    simple_print_str("bootloader done!\n");
    delay_ms(2000);


//tmp    //uart rx test
//tmp    for (int i = 0; i < 10; i++) {
//tmp        simple_print_str("uart rx test 0x");
//tmp        simple_print_str(my_itoa_32(i, str_buf));
//tmp        simple_print_str("\n");
//tmp        simple_uart0_get_str(str_buf);
//tmp        //replay the get string
//tmp        simple_print_str(str_buf);
//tmp    }

    //flush all dirty data from data cache
    __asm__ __volatile__ ("fence.i");
    return program_start_address;
//tmp    while(1);
    
//tmp    while(1) {
//tmp        simple_uart0_get_str(str_buf);
//tmp        //replay the get string
//tmp        //simple_print_str(str_buf);
//tmp    }
}

uint32_t boot_init()
{
    uint32_t ret_v;
    //init_tls();
    hw_init();
    ret_v = load_img();
    return ret_v;
}
