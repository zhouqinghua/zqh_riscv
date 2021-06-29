#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/shm.h>
#include <pthread.h>

#include <fesvr/dtm.h>
#include <vpi_user.h>
#include <svdpi.h>

#include "zqh_jtag_common.h"

dtm_t* dtm;

char send_byte;
char recv_byte;
char * jtag_pin_all(int tck, int tms, int tdi) {
    char data;
    data = (tck << 2) + (tms << 1) + tdi + 0x30;
    send_byte = data;
    return &send_byte;
}

void socket_send_byte(int socket, char * ptr) {
    if (send(socket, ptr, 1, 0) == -1) {
        fprintf(stderr, "send failed: %s (%d)\n", strerror(errno), errno);
        abort();
    }
}

void jtag_goto_test_logic_reset(int socket, int a = 10) {
    for (int i = 0; i < a; i++) {
        socket_send_byte(socket, jtag_pin_all(0, 1, 0));
        socket_send_byte(socket, jtag_pin_all(1, 1, 0));
    }
}

void jtag_quit(int socket) {
    char data = 'Q';
    socket_send_byte(socket, &data);
}

void jtag_blink(int socket) {
    char data = 'B';
    socket_send_byte(socket, &data);
}

void jtag_goto_run_test_idle(int socket, int a = 1) {
    for (int i = 0; i < a; i++) {
        socket_send_byte(socket, jtag_pin_all(0, 0, 0));
        socket_send_byte(socket, jtag_pin_all(1, 0, 0));
    }
}

void jtag_init(int socket, int a = 1) {
    jtag_goto_test_logic_reset(socket);
    jtag_goto_run_test_idle(socket, a);
}


void jtag_goto_select_dr_scan(int socket) {
    socket_send_byte(socket, jtag_pin_all(0, 1, 0));
    socket_send_byte(socket, jtag_pin_all(1, 1, 0));
}

void jtag_goto_select_ir_scan(int socket) {
    socket_send_byte(socket, jtag_pin_all(0, 1, 0));
    socket_send_byte(socket, jtag_pin_all(1, 1, 0));
}

void jtag_goto_capture_ir(int socket) {
    socket_send_byte(socket, jtag_pin_all(0, 0, 0));
    socket_send_byte(socket, jtag_pin_all(1, 0, 0));
}

void jtag_goto_shift_ir(int socket, int tdi = 0) {
    socket_send_byte(socket, jtag_pin_all(0, 0, tdi));
    socket_send_byte(socket, jtag_pin_all(1, 0, tdi));
}

void jtag_goto_exit_1_ir(int socket, int tdi) {
    socket_send_byte(socket, jtag_pin_all(0, 1, tdi));
    socket_send_byte(socket, jtag_pin_all(1, 1, tdi));
}


void jtag_do_shift_ir(int socket, int a) {
    int tdi_bit = 0;
    //shift idcode instruction
    for (int i = 0; i < 5; i++) {
        tdi_bit = (a >> i) & 1;

        //last bit
        if (i == 4) {
            jtag_goto_exit_1_ir(socket, tdi_bit);
        }
        else {
            jtag_goto_shift_ir(socket, tdi_bit);
        }
    }
}

void jtag_goto_update_ir(int socket) {
    socket_send_byte(socket, jtag_pin_all(0, 1, 0));
    socket_send_byte(socket, jtag_pin_all(1, 1, 0));
}

void jtag_goto_capture_dr(int socket) {
    socket_send_byte(socket, jtag_pin_all(0, 0, 0));
    socket_send_byte(socket, jtag_pin_all(1, 0, 0));
}

char jtag_goto_shift_dr(int socket, int tdi = 0) {
    socket_send_byte(socket, jtag_pin_all(0, 0, tdi));

    //read tdo
    char data = 'R';
    socket_send_byte(socket, &data);
    char recv_data;
    if (recv(socket, &recv_data, 1, 0) <= 0) {
        fprintf(stderr, "jtag_goto_shift_dr recv failed: %s (%d)\n", strerror(errno), errno);
        abort();
    }

    //write tdi
    socket_send_byte(socket, jtag_pin_all(1, 0, tdi));

    return recv_data - '0';
}

char jtag_goto_exit_1_dr(int socket, int tdi = 0) {
    socket_send_byte(socket, jtag_pin_all(0, 1, tdi));

    //read tdo
    char data = 'R';
    socket_send_byte(socket, &data);
    char recv_data;
    if (recv(socket, &recv_data, 1, 0) <= 0) {
        fprintf(stderr, "jtag_goto_exit_1_dr recv failed: %s (%d)\n", strerror(errno), errno);
        abort();
    }

    //write tdi
    socket_send_byte(socket, jtag_pin_all(1, 1, tdi));

    return recv_data - '0';
}

uint64_t jtag_do_shift_dr(int socket, int width = 32, uint64_t a = 0) {
    int tdi_bit = 0;
    uint64_t tdo_bit = 0;
    uint64_t tdo_all = 0;
    for (int i = 0; i < width; i++) {
        tdi_bit = (a >> i) & 1;
        if (i == (width - 1)) {
            tdo_bit = jtag_goto_exit_1_dr(socket, tdi_bit);
        }
        else {
            tdo_bit = jtag_goto_shift_dr(socket, tdi_bit);
        }

        tdo_all = tdo_all | (tdo_bit << i);
    }

    return tdo_all;
}

void jtag_goto_update_dr(int socket) {
    socket_send_byte(socket, jtag_pin_all(0, 1, 0));
    socket_send_byte(socket, jtag_pin_all(1, 1, 0));
}

uint64_t jtag_access(int socket, int inst, int width = 32, uint64_t wdata = 0) {
    uint64_t rdata = 0;
    
    jtag_goto_select_dr_scan(socket);
    jtag_goto_select_ir_scan(socket);
    jtag_goto_capture_ir(socket);
    jtag_goto_shift_ir(socket);
    jtag_do_shift_ir(socket, inst);
    jtag_goto_update_ir(socket);
    jtag_goto_select_dr_scan(socket);
    jtag_goto_capture_dr(socket);
    jtag_goto_shift_dr(socket);
    rdata = jtag_do_shift_dr(socket, width, wdata);
    jtag_goto_update_dr(socket);
    jtag_goto_run_test_idle(socket, 5);
    
    //tmp printf("jtag access: inst %x\n", inst);
    //tmp printf("jtag access: wdata %lx\n", wdata);
    //tmp printf("jtag acess: rdata %lx\n", rdata);

    return rdata;

}

uint32_t jtag_dtmcs_read(int socket) {
    return jtag_access(socket, 0x10);
}

uint64_t jtag_dmi_write(int socket, uint64_t wdata) {
    return jtag_access(socket, 0x11, 41, wdata);
}

uint64_t jtag_dmi_read(int socket) {
    return jtag_access(socket, 0x11, 41);
}


unsigned char  debug_req_valid = 0;
unsigned char  debug_req_ready = 0;
unsigned int   debug_req_bits_addr;
unsigned int   debug_req_bits_op;
unsigned int   debug_req_bits_data;
unsigned char  debug_resp_valid = 0;
unsigned char  debug_resp_ready = 0;
unsigned int   debug_resp_bits_resp;
unsigned int   debug_resp_bits_data;
unsigned int   dtm_done = 0;

int req_cnt = 0;

int dmi2jtag_state = DMI2JTAG_ST_INIT;

 
void zqh_dmi2jtag_bit_client(int argc,char **argv)
{
    printf("argc: %d\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("argv[%0d]: %s\n", i, argv[i]);
    }

    int sock_cli = socket(AF_INET,SOCK_STREAM, 0);
 
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(atoi(argv[2]));
    servaddr.sin_addr.s_addr = INADDR_ANY;

    //zqh tmp if (connect(sock_cli, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    //zqh tmp {
    //zqh tmp     fprintf(stderr, "socket connect faild: %s %d\n", strerror(errno), errno);
    //zqh tmp     exit(1);
    //zqh tmp }
    while(connect(sock_cli, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        fprintf(stderr, "socket connect faild: %s %d\n", strerror(errno), errno);
        sleep(1);
    }

    if (!dtm) {
        dtm = new dtm_t(argc, argv);
    }

    while(1) {
        dtm_t::resp resp_bits;
        resp_bits.resp = debug_resp_bits_resp;
        resp_bits.data = debug_resp_bits_data;

        dtm->tick
        (
          debug_req_ready,
          debug_resp_valid,
          resp_bits
        );

        debug_resp_ready    = dtm->resp_ready();
        debug_req_valid     = dtm->req_valid();
        debug_req_bits_addr = dtm->req_bits().addr;
        debug_req_bits_op   = dtm->req_bits().op;
        debug_req_bits_data = dtm->req_bits().data;


        dtm_done = dtm->done() ? (dtm->exit_code() << 1 | 1) : 0;



        if (dtm_done != 0) {
           dmi2jtag_state = DMI2JTAG_ST_EXIT;
        }

        switch(dmi2jtag_state) {
            case DMI2JTAG_ST_INIT: {
                jtag_init(sock_cli);
                printf("jtag_init done\n");
                dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
                break;
            }
            case DMI2JTAG_ST_REQ_CHECK: {
                if (debug_req_valid) {
                    dmi2jtag_state = DMI2JTAG_ST_REQ_READY;
                }
                else {
                    jtag_blink(sock_cli);
                }
                break;
            }
            case DMI2JTAG_ST_REQ_READY: {
                uint32_t rdata;
                int dmistat;
                rdata = jtag_dtmcs_read(sock_cli);
                //tmp printf("dtmcs rdata: %x\n", rdata);
                dmistat = (rdata >> 10) & 0x3;
                if (dmistat == 0) {
                    //printf("dtmcs dmistat is free for req\n");
                    dmi2jtag_state = DMI2JTAG_ST_REQ_SEND;
                }
                break;

            }
            case DMI2JTAG_ST_REQ_SEND: {
                uint64_t wdata;
                uint64_t rdata;

                wdata = debug_req_bits_op | (((uint64_t)debug_req_bits_data) << 2) | (((uint64_t)debug_req_bits_addr) << 34);
                if (debug_req_bits_op == 1) {
                    printf("dmi req read: op = %0x, addr = %x, data = %x\n", debug_req_bits_op, debug_req_bits_addr, debug_req_bits_data);
                }
                else {
                    printf("dmi req write: op = %0x, addr = %x, data = %x\n", debug_req_bits_op, debug_req_bits_addr, debug_req_bits_data);
                }
                rdata = jtag_dmi_write(sock_cli, wdata);
                debug_req_ready = 1;
                dmi2jtag_state = DMI2JTAG_ST_RESP_CHECK;
                break;
            }
            case DMI2JTAG_ST_RESP_CHECK: {
                uint32_t rdata;
                uint32_t dmistat;
                debug_req_ready = 0;
                rdata = jtag_dtmcs_read(sock_cli);
                //printf("dtmcs rdata: %x\n", rdata);
                dmistat = (rdata >> 10) & 0x3;
                if (dmistat == 0) {
                    //printf("dtmcs dmistat is free for resp\n");
                    dmi2jtag_state = DMI2JTAG_ST_RESP_READY;
                }
                break;
            }
            case DMI2JTAG_ST_RESP_READY: {
                if (debug_resp_ready) {
                    dmi2jtag_state = DMI2JTAG_ST_RESP_SEND;
                }
                else {
                    jtag_blink(sock_cli);
                }
                break;
            }
            case DMI2JTAG_ST_RESP_SEND: {
                uint64_t rdata;
                uint32_t addr;

                rdata = jtag_dmi_read(sock_cli);
                debug_resp_valid = 1;
                debug_resp_bits_resp = ((rdata & 0x3) == 0) ? 0 : 1;
                debug_resp_bits_data = (rdata >> 2) & 0xffffffff;
                addr = rdata >> 34;
                dmi2jtag_state = DMI2JTAG_ST_RESP_DONE;

                printf("dmi resp: resp = %0x, data = %x\n",debug_resp_bits_resp, debug_resp_bits_data);

                //tmp req_cnt++; 
                //tmp if (req_cnt >= 1) {
                //tmp     while(1) {
                //tmp         jtag_blink(sock_cli);
                //tmp     }
                //tmp }
                break;
            }
            case DMI2JTAG_ST_RESP_DONE: {
                debug_resp_valid = 0;
                jtag_blink(sock_cli);
                dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
                break;
            }
            case DMI2JTAG_ST_EXIT: {
                jtag_quit(sock_cli);
                break;
            }
        }
    }




    //tmp char send_byte;
    //tmp char recvbuf;

    //tmp int cnt = 0;
    //tmp while (1) {
    //tmp     if (cnt%2 == 0) {
    //tmp         send_byte = '0';
    //tmp     }
    //tmp     else {
    //tmp         send_byte = '4';
    //tmp     }
    //tmp     send(sock_cli, &send_byte, sizeof(send_byte),0);
    //tmp     fprintf(stderr, "send %c\n",send_byte);
    //tmp     //tmp if(strcmp(sendbuf,"exit\n")==0)
    //tmp     //tmp     break;
    //tmp     //tmp recv(sock_cli, recvbuf, sizeof(recvbuf),0);
    //tmp     //tmp fputs(recvbuf, stdout);
    //tmp     //tmp fprintf(stderr, "recv %c\n",recvbuf[0]);
 
    //tmp     //memset(sendbuf, 0, sizeof(sendbuf));
    //tmp     //tmp memset(recvbuf, 0, sizeof(recvbuf));

    //tmp     cnt++;
    //tmp     //sleep(1);
    //tmp }
    //tmp close(sock_cli);
}

int main(int argc,char **argv) {
    zqh_dmi2jtag_bit_client(argc, argv);
    return 0;
}
