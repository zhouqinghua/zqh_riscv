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
    //gpio hw iof enable
    *GPIO_IOF_EN(1) = *GPIO_IOF_EN(1) | 0xc0000000;

    //
    //usb device test
    //initial host port first
    usb_host_initial_cfg();
    uint8_t usb_device_addr;
    usb_device_addr = 0x5a;
    usb_host_emum_common(usb_device_addr);


    usb_device_initial_cfg();
    usb_device_ready_trans(1, 0, NULL, 0);
    usb_device_ready_trans(2, 0, NULL, 0);

    uint32_t debug_cnt;
    uint32_t debug_more;
    uint32_t device_int_status;
    uint32_t device_ep_status;
    uint32_t device_ctrl_transfer_stage;
    uint8_t usb_device_rx_buf[64];
    struct USB_SETUP_PACKET device_setup_pkt;
    struct USB_DEVICE_DESCRIPTOR device_device_dcp;
    struct USB_CONFIGURATION_DESCRIPTOR device_cfg_dcp;
    struct USB_CBW usb_device_cbw;
    struct USB_CSW usb_device_csw;
    usb_host_trans_data_seq = 1;
    usb_device_trans_data_seq = 1;
    debug_more = 0;
    debug_cnt = 0;

    device_ctrl_transfer_stage = 0;
    while(1) {
        //scan device_int_status
        device_int_status = usb_device_read_int_status();
        if ((device_int_status & 0x20) != 0) {
            printf_zqh("usb int status stall_sent\n");
            //delay_ms(100);
            //while(1);
            continue;
        }
        else if ((device_int_status & 0x04) != 0) {
            printf_zqh("usb int status reset_event\n");
            printf_zqh("usb device 2nd reset event found\n");
            device_ctrl_transfer_stage = 0;
            usb_device_ready_trans(0, 0, NULL, 0);
            usb_device_ready_trans(1, 0, NULL, 0);
            usb_device_ready_trans(2, 0, NULL, 0);
            continue;
        }
        else if ((device_int_status & 0x01) != 0) {
            uint32_t trans_type;
            uint32_t pkt_len;
            uint8_t device_addr;
            uint8_t ep_out_addr;
            uint8_t ep_in_addr;
            uint16_t ep_in_mps;
            uint16_t ep_out_mps;

            //control transfer's setup pkt
            if (*USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0) != 0) {
                device_ep_status = *USB_CTRL_UTMI_DEVICE_STATUS(1,0);
                *USB_CTRL_UTMI_DEVICE_STATUS(1,0) = 0;
            }
            //bulk transfer's request pkt
            else {
                device_ep_status = *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_out_addr);
                *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_out_addr) = 0;
            }

            //check ep's status
            if ((device_ep_status & 0x0001) != 0) {
                printf_zqh("device ep crc_error\n");
                while(1);
            }
            else if ((device_ep_status & 0x0008) != 0) {
                printf_zqh("device ep rx_time_out\n");
            }
            printf_zqh("usb int status trans_done\n");


            //0: setup, 1: bulk in, 2: bulk out
            trans_type = (device_ep_status >> 8) & 0x03;
            device_addr = 0x5a;//host forward port's device addr
            ep_out_addr = host_ep_dcp_out[0].bEndpointAddress & 0x0f;
            ep_in_addr = host_ep_dcp_in[0].bEndpointAddress & 0x0f;
            ep_in_mps = host_ep_dcp_in[0].wMaxPacketSize;
            ep_out_mps = host_ep_dcp_out[0].wMaxPacketSize;


            //
            //setup requset pkt
            //control transfer is statefull. has setup, data and state stages
            //0: setup stage, 1: data stage write, 2: data state read, 3: state stage write, 4: state stage read
            if (*USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0) != 0) {
                device_ctrl_transfer_stage = 0;
                //
                //setup stage
                //{{{
                if (device_ctrl_transfer_stage == 0) {
                    //usb_host_trans_data_seq = 1;
                    usb_device_trans_data_seq = 1;
                    printf_zqh("setup trans found\n");
                    //recieve setup cmd
                    pkt_len = usb_device_read_rx_data(0, &device_setup_pkt);
                    printf_zqh("setup pkt_len = %0d\n", pkt_len);
                    display_usb_setup_packet(&device_setup_pkt);

                    //read: device -> host
                    if ((device_setup_pkt.bmRequestType & 0x80) != 0) {
                        device_ctrl_transfer_stage = 2;
                    }
                    //write: host -> device
                    else {
                        device_ctrl_transfer_stage = 1;
                    }
                }
                //}}}


                //
                //data stage
                //{{{
                //read
                if (device_ctrl_transfer_stage == 2) {
                    usb_setup_pkt_copy(&host_setup_pkt, &device_setup_pkt);
                    //get descriptor xxx
                    if ((device_setup_pkt.bmRequestType == 0x80) && 
                        (device_setup_pkt.bRequest == USB_REQ_GET_DESCRIPTOR)) {
                        //forward to host port side to get descriptor
                        usb_host_tx_addr_cfg(device_addr, 0);
                        //usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);

                        if ((device_setup_pkt.wValue >> 8) == 1) {
                            usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
                            printf_zqh("get descriptor device\n");
                            usb_dcp_copy(&device_device_dcp, usb_host_rx_buf);
                            display_usb_device_dcescriptor(&device_device_dcp);
                            pkt_len = usb_host_rx_buf[0];
                            if (device_setup_pkt.wLength < pkt_len) {
                                pkt_len = device_setup_pkt.wLength;
                            }
                        }
                        else if ((device_setup_pkt.wValue >> 8) == 2) {
                            usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
                            printf_zqh("get descriptor configuration\n");
                            usb_dcp_copy(&device_cfg_dcp, usb_host_rx_buf);
                            display_usb_cfg_dcescriptor(&device_cfg_dcp);
                            pkt_len = usb_host_rx_buf[2] + (usb_host_rx_buf[3] * 256);
                            if (device_setup_pkt.wLength < pkt_len) {
                                pkt_len = device_setup_pkt.wLength;
                            }
                        }
                        else if ((device_setup_pkt.wValue >> 8) == 3) {
                            printf_zqh("get descriptor string\n");
                            debug_cnt++;
                            //tmp pkt_len = usb_host_rx_buf[0];
                            //tmp printf_zqh("string dcp len = %d\n", pkt_len);
                            //tmp printf_zqh("string idx = %d\n", device_setup_pkt.wValue & 0x00ff);
                            //tmp printf_zqh("stored dcp len = %d\n", host_str_dcp[device_setup_pkt.wValue & 0x00ff][0]);
                            //tmp if (device_setup_pkt.wLength < pkt_len) {
                            //tmp     pkt_len = device_setup_pkt.wLength;
                            //tmp }
                            //
                            pkt_len = host_str_dcp[device_setup_pkt.wValue & 0x00ff][0];
                            for (int i = 0; i < pkt_len; i++) {
                                usb_host_rx_buf[i] = host_str_dcp[device_setup_pkt.wValue & 0x00ff][i];
                            }
                            if (device_setup_pkt.wLength < pkt_len) {
                                pkt_len = device_setup_pkt.wLength;
                            }
                        }
                        else if ((device_setup_pkt.wValue >> 8) == 6) {
                            usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
                            printf_zqh("get descriptor %0x\n", device_setup_pkt.wValue >> 8);
                            pkt_len = usb_host_rx_buf[0];
                            if (device_setup_pkt.wLength < pkt_len) {
                                pkt_len = device_setup_pkt.wLength;
                            }
                            pkt_len = device_setup_pkt.wLength;
                            //for (int i = 0; i < 64; i++) {
                            //    printf_zqh("usb_host_rx_buf[%0d] = %x\n", i, usb_host_rx_buf[i]);
                            //}
                        }
                        else {
                            printf_zqh("get descriptor unknown %0x\n", device_setup_pkt.wValue >> 8);
                            while(1);
                        }
                    }
                    else {
                        printf_zqh("get unknown\n");
                        printf_zqh("setup get trans forward to host. wLength = 0x%04d\n", device_setup_pkt.wLength);
                        //forward to host port to get data
                        usb_host_tx_addr_cfg(device_addr, 0);
                        pkt_len = usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
                        if (device_setup_pkt.wLength < pkt_len) {
                            pkt_len = device_setup_pkt.wLength;
                        }
                        for (int i = 0; i < pkt_len; i++) {
                            printf_zqh("usb_host_rx_buf[%0d] = 0x%02x\n", i, usb_host_rx_buf[i]);
                        }
                    }
                    //return get data
                    uint32_t done_status;
                    done_status = usb_device_tx_data_wait(0, usb_device_trans_data_seq, usb_host_rx_buf, pkt_len);
                    //timeout
                    if ((done_status & 0x0008) != 0) {
                        device_ctrl_transfer_stage = 0;
                    }
                    else {
                        usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                        device_ctrl_transfer_stage = 4;
                    }
                }
                //write
                else if (device_ctrl_transfer_stage == 1) {
                    usb_setup_pkt_copy(&host_setup_pkt, &device_setup_pkt);

                    //set address should not forward
                    //update address after state stage
                    if ((device_setup_pkt.bmRequestType == 0x00) && 
                        (device_setup_pkt.bRequest == USB_REQ_SET_ADDRESS)) {
                        ;
                    }
                    //other set cmd need forward to host port
                    else {
                        if ((device_setup_pkt.bmRequestType == 0x00) && 
                            (device_setup_pkt.bRequest == USB_REQ_SET_CONFIGURATION)) {
                            printf_zqh("set configuration\n");
                            usb_host_tx_addr_cfg(device_addr, 0);
                            usb_host_control_set_cfg(&host_setup_pkt);
                        }
                        else if ((device_setup_pkt.bmRequestType == 0x01) && 
                            (device_setup_pkt.bRequest == USB_REQ_SET_INTERFACE)) {
                            printf_zqh("set interface\n");
                            usb_host_tx_addr_cfg(device_addr, 0);
                            usb_host_control_set_itf(&host_setup_pkt);
                        }
                        else if (device_setup_pkt.bRequest == USB_REQ_CLEAR_FEATURE) {
                            uint32_t clean_ep;
                            printf_zqh("clear feature\n");
                            clean_ep = device_setup_pkt.wIndex & 0x000f;
                            usb_host_tx_addr_cfg(device_addr, 0);
                            usb_host_control_clear_feature(&host_setup_pkt);
                            usb_host_trans_stalled = 0;//clean stall flag


                            *USB_CTRL_UTMI_DEVICE_CONTROL(1,clean_ep) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,clean_ep) & 0xffffffef;
                            *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_out_addr) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_out_addr) & 0xffffffef;
                            //*USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x20;//clean interrupt flag of stall_sent
                            //debug_more = 1;
                        }
                        else {
                            printf_zqh("set unknown\n");
                            while(1);
                        }
                        //tmp printf_zqh("setup set trans forward to host. wLength = 0x%04d\n", device_setup_pkt.wLength);
                        //tmp usb_setup_pkt_copy(&host_setup_pkt, &device_setup_pkt);
                        //tmp //forward setup pkt to host port
                        //tmp usb_host_tx_addr_cfg(device_addr, 0);
                        //tmp usb_host_trans_setup(&host_setup_pkt);
                    }
                    device_ctrl_transfer_stage = 3;
                }
                //}}}


                //
                //state stage
                //{{{
                //control read need zero len OUT trans as state
                if (device_ctrl_transfer_stage == 4) {
                    //ready to recieve zero len OUT trans
                    usb_device_rx_data_wait(0);
                    printf_zqh("zero len OUT trans pkt len = %0d\n", *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0));
                    device_ep_status = *USB_CTRL_UTMI_DEVICE_STATUS(1,0);
                    *USB_CTRL_UTMI_DEVICE_STATUS(1,0) = 0;
                    printf_zqh("device_ep_status = %0x\n", device_ep_status);

                    //timeout no need read out data
                    if ((device_ep_status & 0x0008) == 0) {
                        //read out host's zero len out trans data
                        usb_device_drop_rx_data(3, usb_device_rx_buf);
                    }
                    printf_zqh("device control transfer read done\n");

                    //ready to recieve next setup cmd
                    //usb_device_rx_data_ready(0);
                }
                //control write need zero len IN trans as state
                else if (device_ctrl_transfer_stage == 3) {
                    usb_device_tx_data_wait(0, usb_device_trans_data_seq, NULL, 0);
                    usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;

                    //set address need be complete after state stage
                    //modify device_addr as fast as possible
                    if ((device_setup_pkt.bmRequestType == 0x00) && 
                        (device_setup_pkt.bRequest == USB_REQ_SET_ADDRESS)) {
                        *USB_CTRL_UTMI_DEVICE_ADDR(1) = device_setup_pkt.wValue;
                        printf_zqh("set address to 0x%02x\n", device_setup_pkt.wValue);
                    }
                    else if (device_setup_pkt.bRequest == USB_REQ_CLEAR_FEATURE) {
                        printf_zqh("clear feature post: read out the left csw of previous stalled cbw\n");
                        usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                        pkt_len = usb_host_csw_recv(&usb_device_csw);
                        printf_zqh("pkt_len = %0d\n", pkt_len);
                        display_usb_csw(&usb_device_csw);
                        //return the csw to host
                        usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, &usb_device_csw, pkt_len);
                        usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                    }

                    printf_zqh("device control transfer write done\n");

                    //ready to recieve next setup cmd
                    //usb_device_rx_data_ready(0);
                }
                //}}}
            }
            //bulk out cbw cmd
            else if (*USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,ep_out_addr) != 0) {
//                printf_zqh("bulk out trans cbw found\n");
                //for (int i = 0; i < 4; i++) {
                //    printf_zqh("ep%0d USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT = %x\n", i, *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,i));
                //    printf_zqh("ep%0d USB_CTRL_UTMI_DEVICE_CONTROL = %x\n", i, *USB_CTRL_UTMI_DEVICE_CONTROL(1,i));
                //}
                pkt_len = usb_device_read_rx_data(ep_out_addr, &usb_device_cbw);
//                printf_zqh("bulk pkt_len = %0d\n", pkt_len);
                display_usb_cbw(&usb_device_cbw);
//                display_usb_cbw_cbwcb(&usb_device_cbw);

                //read: device -> host
                if ((usb_device_cbw.bmCBWFlag & 0x80) != 0) {
                    printf_zqh("bulk cbw read\n");

                    //forward cbw requset to host port
//                    printf_zqh("bulk cbw read req forward to host\n");
                    usb_host_tx_addr_cfg(device_addr, ep_out_addr);
                    usb_host_cbw_send(&usb_device_cbw, 0);
                    if (usb_host_trans_stalled) {
                        printf_zqh("usb_host_cbw_send has stall\n");
                    }


                    //read cbw data
                    uint32_t read_cnt;
                    if (usb_device_cbw.CBWCB[0] == USB_CBS_SCSI_OPCODE_READ_10) {
                        read_cnt = usb_device_cbw.dCBWDataTransferLength/ep_in_mps;
                    }
                    else {
                        read_cnt = 1;
                    }
                    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                    for (int i = 0; i < read_cnt; i++) {
                        pkt_len = usb_host_cbw_data_recv(usb_host_rx_buf);
                        //if (usb_host_trans_stalled) {
                        //    printf_zqh("usb_host_cbw_data_recv has stall\n");
                        //    break;
                        //}

                        //printf_zqh("round %0d's pkt_len = %0d\n", i, pkt_len);
//                        printf_zqh("round %0d\n", i);
                        //for (int j = 0; j < pkt_len; j++) {
                        //    printf_zqh("pkt[%0d] = 0x%02x\n", j, usb_host_rx_buf[j]);
                        //}
                        //return cbw data
                        //printf_zqh("return cbw data to host\n");
                        usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, usb_host_rx_buf, pkt_len);
                        usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                    }


                    //check if host port forward trans has stall or not
                    if (usb_host_trans_stalled) {
                        printf_zqh("bulk cbw data read has stall\n");
                        //send stall to next trans
                        *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_in_addr) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_in_addr) | 0x10;
                        *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_out_addr) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep_out_addr) | 0x10;
                        usb_device_wait_stall_sent(ep_in_addr);
                        printf_zqh("stall_sent found 1\n");
                        //usb_device_wait_stall_sent(ep_in_addr);
                        //printf_zqh("stall_sent found 2\n");

                        //delay_ms(100);
                    }
                    else {
                        //read host port's csw
                        usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                        pkt_len = usb_host_csw_recv(&usb_device_csw);
                        display_usb_csw(&usb_device_csw);
                        if (usb_host_trans_stalled) {
                            printf_zqh("usb_host_csw_recv has stall\n");
                        }

                        //return csw
                        printf_zqh("return csw to host\n");
                        printf_zqh("pkt_len = %0d\n", pkt_len);
                        usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, &usb_device_csw, pkt_len);
                        usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                    }


                    //ready to recieve next cbw cmd
                    usb_device_rx_data_ready(ep_out_addr);

                }
                //out: host -> device
                else {
                    printf_zqh("bulk cbw write\n");
                    //forward cbw requset to host port
//                    printf_zqh("bulk cbw write req forward to host\n");
                    //printf_zqh("debug_cnt = %0d\n", debug_cnt);
                    //if (debug_cnt == 10) {
                    //    printf_zqh("usb_host_trans_data_seq = %0d\n", usb_host_trans_data_seq);
                    //    //usb_host_trans_data_seq = (usb_host_trans_data_seq + 1) & 1;
                    //    //debug_more = 1;
                    //}


                    usb_host_tx_addr_cfg(device_addr, ep_out_addr);
                    usb_host_cbw_send(&usb_device_cbw, 0);
                    if (usb_host_trans_stalled) {
                        printf_zqh("usb_host_cbw_send has stall\n");
                    }


                    //write cbw's data to meadia
                    //if (usb_device_cbw.dCBWDataTransferLength != 0) {
                    //    printf_zqh("unknown cbw write:\n");
                    //    display_usb_cbw_cbwcb(&usb_device_cbw);
                    //    while(1);
                    //}
                    uint32_t write_cnt;
                    if (usb_device_cbw.CBWCB[0] == USB_CBS_SCSI_OPCODE_TEST_UNIT_READY) {
                        printf_zqh("TEST_UNIT_READY\n");
                        write_cnt = 0;
                    }
                    else if (usb_device_cbw.CBWCB[0] == USB_CBS_SCSI_OPCODE_WRITE_10) {
                        printf_zqh("WRITE_10\n");
                        write_cnt = usb_device_cbw.dCBWDataTransferLength/ep_out_mps;
                    }
                    else {
                        printf_zqh("write other\n");
                        if (usb_device_cbw.dCBWDataTransferLength != 0) {
                            write_cnt = 1;
                        }
                        else {
                            write_cnt = 0;
                        }
                    }
                    for (int i = 0; i < write_cnt; i++) {
                        //read data from host
                        usb_device_rx_data_wait(ep_out_addr);
                        pkt_len = usb_device_read_rx_data(ep_out_addr, usb_device_rx_buf);
                        //printf_zqh("pkt_len = %0d\n", pkt_len);

                        //write data to host port
                        usb_host_tx_addr_cfg(device_addr, ep_out_addr);
                        usb_host_trans_bulk_out(usb_device_rx_buf, pkt_len, 0);
                    }
                    if (usb_host_trans_stalled) {
                        printf_zqh("usb_host_trans_bulk_out has stall\n");
                    }



                    //read host port's csw
                    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                    pkt_len = usb_host_csw_recv(&usb_device_csw);
                    display_usb_csw(&usb_device_csw);
                    if (usb_host_trans_stalled) {
                        printf_zqh("usb_host_csw_recv has stall\n");
                    }

                    //return csw
                    printf_zqh("return csw to host\n");
                    printf_zqh("pkt_len = %0d\n", pkt_len);
                    usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, &usb_device_csw, pkt_len);
                    usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;

                    //retrun data again
                    //if (debug_cnt == 10) {
                    //    printf_zqh("return data again to host\n");
                    //    //usb_host_tx_addr_cfg(device_addr, ep_in_addr);
                    //    //pkt_len = usb_host_csw_recv(&usb_device_csw);
                    //    //display_usb_csw(&usb_device_csw);

                    //    printf_zqh("pkt_len = %0d\n", pkt_len);
                    //    usb_device_tx_data_wait(ep_in_addr, usb_device_trans_data_seq, &usb_device_csw, pkt_len);
                    //    usb_device_trans_data_seq = (usb_device_trans_data_seq + 1) & 1;
                    //    debug_cnt = 0;
                    //}

                    //ready to recieve next cbw cmd
                    usb_device_rx_data_ready(ep_out_addr);
                }
            }
            else {
                //tmp printf_zqh("ep_in fifo size = %0d\n", *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,ep_in_addr));
                //tmp printf_zqh("ep_out fifo size = %0d\n", *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,ep_out_addr));
                //tmp printf_zqh("ep0 fifo size = %0d\n", *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0));
                //tmp printf_zqh("ep_in status = %0x\n", *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_in_addr));
                //tmp printf_zqh("ep_out status = %0x\n", *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_out_addr));
                //tmp printf_zqh("ep0 status = %0x\n", *USB_CTRL_UTMI_DEVICE_STATUS(1,0));

                //tmp //clean for next time
                //tmp *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_in_addr) = 0;
                //tmp *USB_CTRL_UTMI_DEVICE_STATUS(1,ep_out_addr) = 0;
                //tmp *USB_CTRL_UTMI_DEVICE_STATUS(1,0) = 0;

                printf_zqh("illegal trans\n");
                //while(1);
            }
        }
        //nak_sent
        else if ((device_int_status & 0x10) != 0) {
            if (debug_more) {
                printf_zqh("usb int status nak_sent\n");
                printf_zqh("device_int_status = %x\n", device_int_status);
                printf_zqh("new device int status = %x\n", *USB_CTRL_DEVICE_INTERRUPT_STATUS(1));

                //usb_device_ready_trans(1, 1, NULL, 0);
                usb_device_ready_trans(1, 1, usb_device_rx_buf, 0);

                //for (int i = 0; i < 4; i++) {
                //    printf_zqh("USB_CTRL_UTMI_DEVICE_CONTROL(1,%0d) = %x\n", i, *USB_CTRL_UTMI_DEVICE_CONTROL(1,i));
                //    printf_zqh("USB_CTRL_UTMI_DEVICE_STATUS(1,%0d) = %x\n", i, *USB_CTRL_UTMI_DEVICE_STATUS(1,i));
                //    printf_zqh("USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,%0d) = %x\n", i, *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,i));
                //    printf_zqh("USB_CTRL_DEVICE_TX_FIFO_DATA_COUNT(1,%0d) = %x\n", i, *USB_CTRL_DEVICE_TX_FIFO_DATA_COUNT(1,i));
                //}
                ////clean regs to see which ep is modified in next print
                //for (int i = 0; i < 4; i++) {
                //    *USB_CTRL_UTMI_DEVICE_STATUS(1,i) = 0xff;
                //}
            }
            continue;
        }
        //sof_recv
        else if ((device_int_status & 0x08) != 0) {
            continue;
        }
        else {
            continue;
        }
    }

    post_stop(0x01);
    return 0;
}
