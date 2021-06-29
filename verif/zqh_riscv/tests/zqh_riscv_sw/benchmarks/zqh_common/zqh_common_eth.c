#ifndef __ZQH_COMMON_ETH_C
#define __ZQH_COMMON_ETH_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

void mac_tx_bd_done_int_process() {
    printf_xcpt_zqh("mac tx_bd_done process\n");
}

void mac_rx_bd_done_int_process() {
    printf_xcpt_zqh("mac rx_bd_done process\n");
}

void mac_tx_cpl_valid_int_process() {
    int tx_done;
    uint32_t tx_cpl;

    tx_cpl = *MAC_TX_CPL;
    tx_done = tx_cpl & 0x1;
    if (tx_done) {
        printf_xcpt_zqh("mac tx_cpl valid, cpl = %x\n", tx_cpl);
    }
    else {
        printf_xcpt_zqh("mac tx_cpl invalid, cpl = %x\n", tx_cpl);
    }
}

void mac_rx_cpl_valid_int_process() {
    int rx_done;
    uint32_t rx_cpl;

    rx_cpl = *MAC_RX_CPL;
    rx_done = rx_cpl & 0x1;
    if (rx_done) {
        printf_xcpt_zqh("mac rx_cpl valid, cpl = %x\n", rx_cpl);
        //print each rx byte
        //for (int i = 0; i < ((rx_cpl >> 16) + 3)/4; i++) {
        //    printf_xcpt_zqh("mac rx data[%02d] = %08x\n", i, *(MAC_RX_BUF + i));
        //}
    }
    else {
        printf_xcpt_zqh("mac rx_cpl invalid, cpl = %x\n", rx_cpl);
    }
}

void mac_tx_cf_done_int_process() {
    printf_xcpt_zqh("mac tx_cf_done process, ctrl_tx = %x\n", *MAC_CTRL_TX);
}

void mac_rx_cf_done_int_process() {
    printf_xcpt_zqh("mac rx_cf_done process\n");
}

void mac_rx_bd_lack_int_process() {
    printf_xcpt_zqh("mac rx_bd_lack process\n");
}

void mac_smi_done_int_process() {
    printf_xcpt_zqh("mac smi_done process\n");
}

uint32_t mac_phy_smi_read(uint8_t phy_addr, uint8_t reg_addr) {
    int mac_smi_done;

    *MAC_SMI_CTRL = 0x4000 | (phy_addr << 8) | reg_addr;
    mac_smi_done = 0;
    do {
        mac_smi_done = (*MAC_SMI_CTRL & 0x4000) == 0;
    } while(mac_smi_done == 0);
    return *MAC_SMI_DATA;
}

void mac_phy_smi_write(uint8_t phy_addr, uint8_t reg_addr, uint16_t data) {
    int mac_smi_done;

    *MAC_SMI_DATA = data;
    *MAC_SMI_CTRL = 0x6000 | (phy_addr << 8) | reg_addr;
    mac_smi_done = 0;
    do {
        mac_smi_done = (*MAC_SMI_CTRL & 0x4000) == 0;
    } while(mac_smi_done == 0);
}

void mac_phy_reset_dereset() {
    //
    //phy reset and dereset
    *CRG_CTRL_RESET_CFG = *CRG_CTRL_RESET_CFG & 0xffffffdf; //reset eth
    *CRG_CTRL_RESET_CFG = *CRG_CTRL_RESET_CFG | 0x20; //dereset eth
    delay_ms(500);
}

void mac_rx_bd_push(uint32_t rx_buf_offset) {
    int rx_bd_fifo_ready = 0;
    do {
        rx_bd_fifo_ready = *MAC_RX_BD_L & 0x1;
        if (rx_bd_fifo_ready == 0) {
            printf_zqh("mac_rx_bd_fifo %0d is not ready\n");
        }
    } while(rx_bd_fifo_ready == 0);

    //set rx_bd
    *MAC_RX_BD_H = rx_buf_offset;
    *MAC_RX_BD_L = 0x03;
}

//
//eth ARP packet
#define EPT_IP       0x0800    /* type: IP */
#define EPT_ARP      0x0806    /* type: ARP */
#define EPT_RARP     0x8035    /* type: RARP */
#define ARP_HARDWARE 0x0001    /* Dummy type for 802.3 frames */
#define ARP_REQUEST  0x0001    /* ARP request */
#define ARP_REPLY    0x0002    /* ARP reply */

struct eth_hdr 
{
    uint8_t eh_dst[6];   /* destination ethernet addrress */
    uint8_t eh_src[6];   /* source ethernet addresss */
    uint16_t eh_type;   /* ethernet pachet type */
}__attribute__((packed));

struct arp_hdr
{
    uint16_t arp_hrd;    /* format of hardware address */
    uint16_t arp_pro;    /* format of protocol address */
    uint8_t arp_hln;    /* length of hardware address */
    uint8_t arp_pln;    /* length of protocol address */
    uint16_t arp_op;     /* ARP/RARP operation */

    uint8_t arp_sha[6];    /* sender hardware address */
    uint8_t arp_spa[4];    /* sender protocol address */
    uint8_t arp_tha[6];    /* target hardware address */
    uint8_t arp_tpa[4];    /* target protocol address */
}__attribute__((packed));

struct arp_packet
{
    struct eth_hdr m_eth_hdr;
    struct arp_hdr m_arp_hdr;
}__attribute__((packed));


struct ip_hdr
  {
    uint8_t ihl:4;
    uint8_t version:4;
    uint8_t tos;
    uint16_t tot_len;
    uint16_t id;
    uint16_t frag_off:13;
    uint8_t flags:3;
    uint8_t ttl;
    uint8_t protocol;
    uint16_t checksum;
    uint8_t saddr[4];
    uint8_t daddr[4];
}__attribute__((packed));

struct ip_packet_hdr
{
    struct eth_hdr m_eth_hdr;
    struct ip_hdr m_ip_hdr;
}__attribute__((packed));

struct icmp_hdr
  {
    uint8_t type;
    uint8_t code;
    uint16_t checksum;
    uint16_t id;
    uint16_t seq_num;
}__attribute__((packed));

struct icmp_packet_hdr
{
    struct eth_hdr m_eth_hdr;
    struct ip_hdr m_ip_hdr;
    struct icmp_hdr m_icmp_hdr;
}__attribute__((packed));


struct udp_pseudo_hdr
{
    uint8_t sip[4];
    uint8_t dip[4];
    uint8_t pad;
    uint8_t protocol;
    uint16_t length;
}__attribute__((packed));

struct udp_hdr {
	uint16_t sport; 
	uint16_t dport;
	uint16_t length;
	uint16_t checksum;
}__attribute__((packed));

struct udp_packet_hdr
{
    struct eth_hdr m_eth_hdr;
    struct ip_hdr m_ip_hdr;
    struct udp_hdr m_udp_hdr;
}__attribute__((packed));

int eth_check_is_arp_pkt(uint32_t rx_buf_offset, uint8_t my_mac_address[6]) {
    struct arp_packet *rx_pkt_ptr;
    int match = 1;

    rx_pkt_ptr = (struct arp_packet *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);
    //check broadcast mac address
    uint32_t is_broadcast = 1;
    for (int i = 0; i < 6; i++) {
        if ((*rx_pkt_ptr).m_eth_hdr.eh_dst[i] != 0xff) {
            is_broadcast = 0;
            break;
        }
    }
    //check my mac address
    if (is_broadcast == 0) {
        for (int i = 0; i < 6; i++) {
            if ((*rx_pkt_ptr).m_eth_hdr.eh_dst[i] != my_mac_address[i]) {
                match = 0;
                break;
            }
        }
    }

    if (match) {
        if (((*rx_pkt_ptr).m_eth_hdr.eh_type == 0x0608) &&
            ((*rx_pkt_ptr).m_arp_hdr.arp_hrd == 0x0100) &&
            ((*rx_pkt_ptr).m_arp_hdr.arp_pro == 0x0008) &&
            ((*rx_pkt_ptr).m_arp_hdr.arp_hln == 6) &&
            ((*rx_pkt_ptr).m_arp_hdr.arp_pln == 4) && 
            (((*rx_pkt_ptr).m_arp_hdr.arp_op == 0x0100) || ((*rx_pkt_ptr).m_arp_hdr.arp_op == 0x0200))) {
            ;
        }
        else {
            match = 0;
        }
    }
    return match;
}

int eth_check_is_ip_pkt(uint32_t rx_buf_offset) {
    struct ip_packet_hdr *rx_pkt_ptr;
    int match = 0;

    rx_pkt_ptr = (struct ip_packet_hdr *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);
    if ((*rx_pkt_ptr).m_eth_hdr.eh_type == 0x0008) {
        match = 1;
    }
    return match;
}

int ip_check_is_icmp_pkt(uint32_t rx_buf_offset) {
    struct ip_packet_hdr *rx_pkt_ptr;
    int match = 0;

    rx_pkt_ptr = (struct ip_packet_hdr *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);
    if ((*rx_pkt_ptr).m_ip_hdr.protocol == 1) {
        match = 1;
    }
    return match;
}

int ip_check_is_igmp_pkt(uint32_t rx_buf_offset) {
    struct ip_packet_hdr *rx_pkt_ptr;
    int match = 0;

    rx_pkt_ptr = (struct ip_packet_hdr *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);
    if ((*rx_pkt_ptr).m_ip_hdr.protocol == 2) {
        match = 1;
    }
    return match;
}

int ip_check_is_tcp_pkt(uint32_t rx_buf_offset) {
    struct ip_packet_hdr *rx_pkt_ptr;
    int match = 0;

    rx_pkt_ptr = (struct ip_packet_hdr *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);
    if ((*rx_pkt_ptr).m_ip_hdr.protocol == 6) {
        match = 1;
    }
    return match;
}

int ip_check_is_udp_pkt(uint32_t rx_buf_offset) {
    struct ip_packet_hdr *rx_pkt_ptr;
    int match = 0;

    rx_pkt_ptr = (struct ip_packet_hdr *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);
    if ((*rx_pkt_ptr).m_ip_hdr.protocol == 17) {
        match = 1;
    }
    return match;
}

int rx_pkt_ip_cmp(uint8_t pkt_ip[4], uint8_t my_ip[4]) {
    int match = 1;
    for (int i = 0; i < 4; i++) {
        if (pkt_ip[i] != my_ip[i]) {
            match = 0;
            break;
        }
    }
    return match;
}

uint16_t checksum16_cal(uint8_t *buf_ptr, uint32_t len, uint32_t init) {
    uint32_t resault;
    uint32_t resault_h16;
    uint32_t resault_l16;
    resault = init;
    for (int i = 0; i < len/2; i++) {
        resault += (((uint32_t)buf_ptr[i*2]) << 8) | ((uint32_t)buf_ptr[i*2+1]);
    }
    //odd byte num
    if ((len%2) != 0) {
        resault += buf_ptr[len - 1];
    }
    while(1) {
        resault_h16 = resault >> 16;
        resault_l16 = resault & 0x0000ffff;
        if (resault_h16 != 0) {
            resault = resault_l16 + resault_h16;
        }
        else {
            break;
        }
    }
    return resault;
}

struct arp_packet* gen_arp_req_pkt(uint32_t tx_buf_offset, uint8_t my_mac_address[6], uint8_t my_ip_address[4], uint8_t host_ip_address[4]) {
    struct arp_packet *tx_pkt_ptr;

    tx_pkt_ptr = (struct arp_packet *) (((uint8_t *)MAC_TX_BUF) + tx_buf_offset);

    for (int i = 0; i < 42; i++) {
        //target mac address
        if (i < 6) {
            (*tx_pkt_ptr).m_eth_hdr.eh_dst[i] = 0xff;
        }
        //source mac address
        else if (i < 12) {
            (*tx_pkt_ptr).m_eth_hdr.eh_src[i - 6] = my_mac_address[i - 6];
        }
        //eth type
        else if (i < 14) {
            (*tx_pkt_ptr).m_eth_hdr.eh_type = 0x0608;
        }
        else if (i < 16) {
            (*tx_pkt_ptr).m_arp_hdr.arp_hrd = 0x0100;
        }
        else if (i < 18) {
            (*tx_pkt_ptr).m_arp_hdr.arp_pro = 0x0008;
        }
        else if (i < 19) {
            (*tx_pkt_ptr).m_arp_hdr.arp_hln = 6;
        }
        else if (i < 20) {
            (*tx_pkt_ptr).m_arp_hdr.arp_pln = 4;
        }
        else if (i < 22) {
            (*tx_pkt_ptr).m_arp_hdr.arp_op = 0x0100;
        }
        else if (i < 28) {
            (*tx_pkt_ptr).m_arp_hdr.arp_sha[i - 22] = my_mac_address[i - 22];
        }
        else if (i < 32) {
            (*tx_pkt_ptr).m_arp_hdr.arp_spa[i - 28] = my_ip_address[i - 28];
        }
        else if (i < 38) {
            (*tx_pkt_ptr).m_arp_hdr.arp_tha[i - 32] = 0xff;
        }
        else if (i < 42) {
            (*tx_pkt_ptr).m_arp_hdr.arp_tpa[i - 38] = host_ip_address[i - 38];
        }
    }

    return tx_pkt_ptr;
}

struct arp_packet* gen_arp_resp_pkt(uint32_t tx_buf_offset, uint32_t rx_buf_offset, uint8_t my_mac_address[6], uint8_t my_ip_address[4]) {
    uint8_t tx_data;
    struct arp_packet *tx_pkt_ptr;
    struct arp_packet *rx_pkt_ptr;

    tx_pkt_ptr = (struct arp_packet *) (((uint8_t *)MAC_TX_BUF) + tx_buf_offset);
    rx_pkt_ptr = (struct arp_packet *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);

    //copy request back
    for (int i = 0; i < 64; i++) {
        tx_data = *(((uint8_t *)MAC_RX_BUF) + rx_buf_offset + i);
        *(((uint8_t *)MAC_TX_BUF) + i)  = tx_data;
    }

    //change dmac
    for (int i = 0; i < 6; i++) {
        (*tx_pkt_ptr).m_eth_hdr.eh_dst[i] = (*rx_pkt_ptr).m_arp_hdr.arp_sha[i];
    }

    //change op
    (*tx_pkt_ptr).m_arp_hdr.arp_op = 0x0200;

    //insert my mac address
    for (int i = 0; i < 6; i++) {
        (*tx_pkt_ptr).m_arp_hdr.arp_sha[i] = my_mac_address[i];
    }
    //insert my ip address
    for (int i = 0; i < 4; i++) {
        (*tx_pkt_ptr).m_arp_hdr.arp_spa[i] = my_ip_address[i];
    }

    //update deset mac address
    for (int i = 0; i < 6; i++) {
        (*tx_pkt_ptr).m_arp_hdr.arp_tha[i] = (*rx_pkt_ptr).m_arp_hdr.arp_sha[i];
    }

    //update deset ip address
    for (int i = 0; i < 4; i++) {
        (*tx_pkt_ptr).m_arp_hdr.arp_tpa[i] = (*rx_pkt_ptr).m_arp_hdr.arp_spa[i];
    }

    return tx_pkt_ptr;

    ////print arp resp pkt
    //for (int i = 0; i < 60; i++) {
    //    tx_data = *(((uint8_t *)MAC_TX_BUF) + i);
    //    printf_zqh("mac arp resp pkt[%0d] = %x\n", i, tx_data);
    //}
}


struct icmp_packet_hdr* gen_icmp_resp_pkt(uint32_t len, uint32_t tx_buf_offset, uint32_t rx_buf_offset, uint8_t my_mac_address[6], uint8_t my_ip_address[4]) {
    uint8_t tx_data;
    struct icmp_packet_hdr *tx_pkt_ptr;
    struct icmp_packet_hdr *rx_pkt_ptr;

    tx_pkt_ptr = (struct icmp_packet_hdr *) (((uint8_t *)MAC_TX_BUF) + tx_buf_offset);
    rx_pkt_ptr = (struct icmp_packet_hdr *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);

    //copy request back
    for (int i = 0; i < len; i++) {
        tx_data = *(((uint8_t *)MAC_RX_BUF) + rx_buf_offset + i);
        *(((uint8_t *)MAC_TX_BUF) + i)  = tx_data;
    }

    //insert dmac
    for (int i = 0; i < 6; i++) {
        (*tx_pkt_ptr).m_eth_hdr.eh_dst[i] = (*rx_pkt_ptr).m_eth_hdr.eh_src[i];
    }

    //insert smac
    for (int i = 0; i < 6; i++) {
        (*tx_pkt_ptr).m_eth_hdr.eh_src[i] = my_mac_address[i];
    }

    //insert dest ip address
    for (int i = 0; i < 4; i++) {
        (*tx_pkt_ptr).m_ip_hdr.daddr[i] = (*rx_pkt_ptr).m_ip_hdr.saddr[i];
    }

    //insert source ip address
    for (int i = 0; i < 4; i++) {
        (*tx_pkt_ptr).m_ip_hdr.saddr[i] = my_ip_address[i];
    }

    //ip header's checksum set to 0
    (*tx_pkt_ptr).m_ip_hdr.checksum = 0;

    //change to icmp response type
    (*tx_pkt_ptr).m_icmp_hdr.type = 0;
    (*tx_pkt_ptr).m_icmp_hdr.code = 0;

    //icmp checksum set to 0
    (*tx_pkt_ptr).m_icmp_hdr.checksum = 0;
    
    ////icmp payload data set to 0
    //uint32_t data_offset;
    //data_offset = 14 + 20 + 8;
    //for (int i = data_offset; i < len; i++) {
    //    *(((uint8_t *)MAC_TX_BUF) + tx_buf_offset + i) = 0;
    //}

    //ip header's checksum calculation
    uint16_t checksum16;
    checksum16 = ~checksum16_cal(((uint8_t *)MAC_TX_BUF) + tx_buf_offset + 14, 20, 0);
    (*tx_pkt_ptr).m_ip_hdr.checksum = (checksum16 << 8) | (checksum16 >> 8);//exchange byte order
    //icmp's checksum calculation
    checksum16 = ~checksum16_cal(((uint8_t *)MAC_TX_BUF) + tx_buf_offset + 14 + 20, len - 14 - 20, 0);
    (*tx_pkt_ptr).m_icmp_hdr.checksum = (checksum16 << 8) | (checksum16 >> 8);//exchange byte order;

    return tx_pkt_ptr;
}

struct udp_packet_hdr* gen_udp_pkt(uint32_t len, uint32_t tx_buf_offset, uint16_t ip_id, uint8_t my_mac_address[6], uint8_t my_ip_address[4], uint8_t host_mac_address[6], uint8_t host_ip_address[4], uint16_t sport, uint16_t dport, uint8_t *data_buf) {
    uint8_t tx_data;
    struct udp_packet_hdr *tx_pkt_ptr;

    tx_pkt_ptr = (struct udp_packet_hdr *) (((uint8_t *)MAC_TX_BUF) + tx_buf_offset);

    //insert eth dmac
    for (int i = 0; i < 6; i++) {
        (*tx_pkt_ptr).m_eth_hdr.eh_dst[i] = host_mac_address[i];
    }

    //insert eth smac
    for (int i = 0; i < 6; i++) {
        (*tx_pkt_ptr).m_eth_hdr.eh_src[i] = my_mac_address[i];
    }

    //insert eth type
    (*tx_pkt_ptr).m_eth_hdr.eh_type = 0x0008;

    //insert ip version
    (*tx_pkt_ptr).m_ip_hdr.version = 4;

    //insert ip ihl
    (*tx_pkt_ptr).m_ip_hdr.ihl = 5;

    //insert ip tos
    (*tx_pkt_ptr).m_ip_hdr.tos = 0;

    //insert ip total lenght
    (*tx_pkt_ptr).m_ip_hdr.tot_len = ((len - 14) << 8) | ((len - 14) >> 8);//exchange byte order

    //insert ip flags
    (*tx_pkt_ptr).m_ip_hdr.flags = 0;

    //insert ip frag offset
    (*tx_pkt_ptr).m_ip_hdr.frag_off = 0;

    //insert ip id
    (*tx_pkt_ptr).m_ip_hdr.id = (ip_id << 8) | (ip_id >> 8);//exchange byte order

    //insert ip ttl
    (*tx_pkt_ptr).m_ip_hdr.ttl = 64;

    //insert ip protocol
    (*tx_pkt_ptr).m_ip_hdr.protocol = 17;

    //insert ip header's checksum set to 0
    (*tx_pkt_ptr).m_ip_hdr.checksum = 0;

    //insert ip source ip address
    for (int i = 0; i < 4; i++) {
        (*tx_pkt_ptr).m_ip_hdr.saddr[i] = my_ip_address[i];
    }

    //insert ip dest ip address
    for (int i = 0; i < 4; i++) {
        (*tx_pkt_ptr).m_ip_hdr.daddr[i] = host_ip_address[i];
    }

    //ip header's checksum calculation
    uint16_t checksum16;
    checksum16 = ~checksum16_cal(((uint8_t *)MAC_TX_BUF) + tx_buf_offset + 14, 20, 0);
    (*tx_pkt_ptr).m_ip_hdr.checksum = (checksum16 << 8) | (checksum16 >> 8);//exchange byte order


    //udp header
    uint16_t udp_data_len;
    (*tx_pkt_ptr).m_udp_hdr.sport = (sport << 8) | (sport >> 8);//exchange byte order
    (*tx_pkt_ptr).m_udp_hdr.dport = (dport << 8) | (dport >> 8);//exchange byte order
    udp_data_len = len - 14 - 20;
    (*tx_pkt_ptr).m_udp_hdr.length = (udp_data_len << 8) | (udp_data_len >> 8);//exchange byte order
    (*tx_pkt_ptr).m_udp_hdr.checksum = 0;

    //udp payload data
    uint32_t data_offset;
    data_offset = 14 + 20 + 8;
    for (int i = data_offset; i < len; i++) {
        *(((uint8_t *)MAC_TX_BUF) + tx_buf_offset + i) = data_buf[i - data_offset];
    }

    //udp checksum calculation
    struct udp_pseudo_hdr ps_hdr;
    for (int i = 0; i < 4; i++) {
        ps_hdr.sip[i] = my_ip_address[i];
        ps_hdr.dip[i] = host_ip_address[i];
    }
    ps_hdr.pad = 0;
    ps_hdr.protocol = 17;
    ps_hdr.length = (udp_data_len << 8) | (udp_data_len >> 8);//exchange byte order
    uint16_t ps_hdr_checksum;
    ps_hdr_checksum = checksum16_cal((uint8_t *)(&ps_hdr), 12, 0);
    checksum16 = ~checksum16_cal(((uint8_t *)MAC_TX_BUF) + tx_buf_offset + 14 + 20, udp_data_len, ps_hdr_checksum);
    (*tx_pkt_ptr).m_udp_hdr.checksum = (checksum16 << 8) | (checksum16 >> 8);//exchange byte order;

    return tx_pkt_ptr;
}

int send_eth_pkt(uint32_t len, uint32_t tx_buf_offset) {
    //set tx_bd
    *MAC_TX_BD_H = tx_buf_offset;
    *MAC_TX_BD_L = (len << 16) | 0x1f;
    //wait tx pkt done
    int tx_done;
    uint32_t tx_cpl;
    tx_done = 0;
    //wait mac tx send done
    while(tx_done == 0) {
        tx_cpl = *MAC_TX_CPL;
        tx_done = tx_cpl & 0x1;
    }
    printf_zqh("eth pkt send done, cpl = %x\n", tx_cpl);

    return 1;
}

//eth.arp ip.icmp ip.udp test
void eth_mac_tx_rx_test(){
    //config mac device subsystem's csr
    *MAC_MODE = *MAC_MODE | 0x00010000;//enable recieve small pkt
    *MAC_MODE = *MAC_MODE | 0x00004000;//enable tx/rx big pkt
    *MAC_MODE = *MAC_MODE & 0xffffffdf;//disable rx check dest address
    *MAC_MODE = *MAC_MODE | 0x00000010;//phy gmii interface
    *MAC_MODE = *MAC_MODE | 0x00000400;//full_duplex
    //*MAC_PKT_LEN = (*MAC_PKT_LEN & 0xffff0000) + 0x100; //max_fl change to small for test case
    //*MAC_HASH_L = 0xffffffff;//accept all multicast pkt
    //*MAC_HASH_H = 0xffffffff;
    *MAC_HASH_L = 0x00000008;//accept pause frame dest address
    *MAC_HASH_H = 0x00000000;
    *MAC_CTRL_CFG = 0x01;//enable send tx pause frame, process rx pause frame, pass all pause frame to host
    //*MAC_COLL = (*MAC_COLL & 0x0000ffff) | 0x00050000;//max retry set to 5 for fast simulation
    //*MAC_IPG = 12;
    //*MAC_MODE = *MAC_MODE | 0x3;// tx enable and rx enable
    //smi read/write
    *MAC_SMI_CFG = 0x0c8; //1.25MHz @ 1GHz, has preamble
    //*MAC_SMI_CFG = 0x11f; //speedup smi mdc for simulation, no preamble

    uint32_t mac_phy_addr = 0x01;
    uint32_t mac_phy_reg_addr;
    uint32_t mac_phy_reg_buffer[32];
    uint32_t mac_phy_reg_wdata;

    //
    //wait phy AN done
    uint32_t physr;
    uint32_t physr_link;
    uint32_t physr_speed;
    uint32_t link_ok_cnt = 0;
    while(1) {
        physr = mac_phy_smi_read(mac_phy_addr, 0x11);
        printf_zqh("mac phy physr = %x\n", physr);
        physr_link = (physr >> 10) & 0x1;
        physr_speed = (physr >> 14) & 0x3;
        if (physr_link == 1) {
            link_ok_cnt++;
            printf_zqh("mac phy link ok %0d times\n", link_ok_cnt);
            if (physr_speed == 0) {
                printf_zqh("mac phy speed is 10Mbps\n");
            }
            else if (physr_speed == 1) {
                printf_zqh("mac phy speed is 100Mbps\n");
            }
            else if (physr_speed == 2) {
                printf_zqh("mac phy speed is 1000Mbps\n");
            }
            else {
                printf_zqh("mac phy speed is Reserved\n");
            }
        }
        else {
            link_ok_cnt = 0;
        }
        if (link_ok_cnt >= 3) {
            printf_zqh("mac phy ready\n");
            break;
        }
        delay_ms(1000);
    }

    //
    //modify
    //printf_zqh("smi reg0 pre cfg = %x\n",mac_phy_smi_read(mac_phy_addr, 0));
    //mac_phy_reg_wdata = mac_phy_reg_buffer[0];
    //mac_phy_reg_wdata = mac_phy_reg_wdata & 0xffffefff;//bit12 ANE=0, disable an
    //mac_phy_reg_wdata = mac_phy_reg_wdata | 0x40;//bit6 = 1, speed = 1000MHz, gmii mode
    //mac_phy_reg_wdata = mac_phy_reg_wdata & 0xffffdfff;//bit13 = 0, speed = 1000MHz, gmii mode
    //mac_phy_reg_wdata = mac_phy_reg_wdata | 0x100;//bit8 full duplex
    //mac_phy_reg_wdata = mac_phy_reg_wdata | 0x4000;//bit14 = 1, loopback mode
    //mac_phy_smi_write(mac_phy_addr, 0, mac_phy_reg_wdata);
    //printf_zqh("smi reg0 post cfg = %x\n",mac_phy_smi_read(mac_phy_addr, 0));




    //
    //tx rx packet test
    int rx_done;
    uint32_t rx_cpl;
    uint32_t rx_pkt_len;
    int pkt_idx = 0;
    uint8_t my_mac_address[6] = {0x00, 0x0a, 0x35, 0x01, 0xfe, 0xc0};
    uint8_t my_ip_address[4] = {192, 168, 0, 2};
    uint8_t host_mac_address[6] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    uint8_t host_ip_address[4] = {192, 168, 0, 3};
    uint32_t eth_state = 0;//0: idle, 1: host known ip and mac, 2: ready
    uint32_t udp_pkt_id = 0;


    //config my mac address, hardware can insert it into packet automatic
    *MAC_ADDR_H = 
        (((uint32_t)my_mac_address[0]) << 8) | 
        (((uint32_t)my_mac_address[1]) << 0);
    *MAC_ADDR_L = 
        (((uint32_t)my_mac_address[2]) << 24) | 
        (((uint32_t)my_mac_address[3]) << 16) | 
        (((uint32_t)my_mac_address[4]) <<  8) | 
        (((uint32_t)my_mac_address[5]) <<  0);
    *MAC_MODE = *MAC_MODE | 0x3;// tx enable and rx enable


    //initial rx bd prepare
    uint32_t rx_buf_offset;
    int rx_bd_num = 8;
    int rx_bd_fifo_ready;
    for (int pkt_idx = 0; pkt_idx < rx_bd_num; pkt_idx++) {
        rx_buf_offset = (4096/8)*pkt_idx;
        mac_rx_bd_push(rx_buf_offset);
    }

    while(1) {
        rx_cpl = *MAC_RX_CPL;
        rx_done = rx_cpl & 0x1;
        rx_pkt_len = rx_cpl >> 16;
        if (rx_done) {
            printf_zqh("mac rx_bd %0d done, cpl = %x\n", pkt_idx, rx_cpl);
            rx_buf_offset = (4096/8)*pkt_idx;

            //check eth pkt type
            if (eth_check_is_arp_pkt(rx_buf_offset, my_mac_address)) {
                struct arp_packet *arp_rx_pkt_ptr;

                arp_rx_pkt_ptr = (struct arp_packet *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);
                if (rx_pkt_ip_cmp((*arp_rx_pkt_ptr).m_arp_hdr.arp_tpa, my_ip_address)) {
                    printf_zqh("recieve one arp pkt\n");
                    //arp request
                    if ((*arp_rx_pkt_ptr).m_arp_hdr.arp_op == 0x0100) {
                        struct arp_packet *arp_resp_pkt_ptr;

                        //send arp resp
                        arp_resp_pkt_ptr = gen_arp_resp_pkt(0, rx_buf_offset, my_mac_address, my_ip_address);
                        send_eth_pkt(60, 0);
                        printf_zqh("send arp resp, tell host my mac adress\n");
                    }
                    //arp response, extract host's mac address
                    else {
                        for (int i = 0; i < 6; i++) {
                            host_mac_address[i] = (*arp_rx_pkt_ptr).m_arp_hdr.arp_sha[i];
                        }
                        eth_state = 1;
                        printf_zqh("get host's mac address\n");
                    }
                }
            }
            else if (eth_check_is_ip_pkt(rx_buf_offset)) {
                struct ip_packet_hdr *ip_rx_pkt_ptr;

                ip_rx_pkt_ptr = (struct ip_packet_hdr *) (((uint8_t *)MAC_RX_BUF) + rx_buf_offset);
                if (rx_pkt_ip_cmp((*ip_rx_pkt_ptr).m_ip_hdr.daddr, my_ip_address)) {
                    printf_zqh("recieve one ip pkt\n");
                    if (ip_check_is_icmp_pkt(rx_buf_offset)) {
                        struct icmp_packet_hdr *icmp_resp_pkt_ptr;

                        printf_zqh("recieve one icmp pkt\n");
                        icmp_resp_pkt_ptr = gen_icmp_resp_pkt(rx_pkt_len - 4, 0, rx_buf_offset, my_mac_address, my_ip_address);
                        send_eth_pkt(rx_pkt_len - 4, 0);
                        printf_zqh("mac icmp resp send done\n");
                    }
                    else if (ip_check_is_igmp_pkt(rx_buf_offset)) {
                        printf_zqh("recieve one igmp pkt\n");
                    }
                    else if (ip_check_is_tcp_pkt(rx_buf_offset)) {
                        printf_zqh("recieve one tcp pkt\n");
                    }
                    else if (ip_check_is_udp_pkt(rx_buf_offset)) {
                        printf_zqh("recieve one udp pkt\n");
                        uint8_t *data_buf;
                        uint16_t sport,dport;
                        uint32_t eth_pkt_len;
                        struct udp_packet_hdr *upd_pkt_ptr;
                        data_buf = ((uint8_t *)MAC_RX_BUF) + rx_buf_offset + 14 + 20 + 8;//udp payload data
                        sport = 8080;
                        dport = 8080;
                        eth_pkt_len = rx_pkt_len - 4;//no crc field
                        upd_pkt_ptr = gen_udp_pkt(eth_pkt_len, 0, udp_pkt_id, my_mac_address, my_ip_address, host_mac_address, host_ip_address, sport, dport, data_buf);
                        send_eth_pkt(eth_pkt_len, 0);
                        udp_pkt_id++;

                    }
                }
            }

            //recycle this rx bd
            mac_rx_bd_push(rx_buf_offset);

            pkt_idx++;
            if (pkt_idx >= rx_bd_num) {
                pkt_idx = 0;
            }
        }

        //
        if (eth_state == 0) {
            struct arp_packet *arp_req_pkt_ptr;

            arp_req_pkt_ptr = gen_arp_req_pkt(0, my_mac_address, my_ip_address, host_ip_address);
            send_eth_pkt(42, 0);
            printf_zqh("send arp req, ask for host's mac address\n");
        }
        else {
            uint8_t *data_buf;
            uint16_t sport,dport;
            uint32_t eth_pkt_len;
            struct udp_packet_hdr *upd_pkt_ptr;
            data_buf = "hello world\n";
            sport = 8080;
            dport = 8080;
            eth_pkt_len = strlen(data_buf) + 14 + 20 + 8;
            upd_pkt_ptr = gen_udp_pkt(eth_pkt_len, 0, udp_pkt_id, my_mac_address, my_ip_address, host_mac_address, host_ip_address, sport, dport, data_buf);
            send_eth_pkt(eth_pkt_len, 0);
            udp_pkt_id++;
            delay_ms(500);
        }
    }
}

#endif
