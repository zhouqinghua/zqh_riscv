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
int dmi2jtag_state = DMI2JTAG_ST_INIT;
 
void zqh_dmi2jtag_xaction_client(int argc,char **argv)
{
    printf("argc: %d\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("argv[%0d]: %s\n", i, argv[i]);
    }
    //exit(1);

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

        switch(dmi2jtag_state){
            case DMI2JTAG_ST_INIT: {
                if (debug_req_valid) {
                    dmi2jtag_state = DMI2JTAG_ST_REQ_SEND;
                }
                break;
            }
            case DMI2JTAG_ST_REQ_SEND: {
                dtm_t::req req_bits;
                req_bits.addr = debug_req_bits_addr;
                req_bits.op = debug_req_bits_op;
                req_bits.data = debug_req_bits_data;
                if (send(sock_cli, &req_bits, sizeof(req_bits), 0) == -1) {
                    fprintf(stderr, "send failed: %s (%d)\n", strerror(errno), errno);
                    abort();
                }
                if (req_bits.op == 1) {
                    printf("dmi req read: op = %0x, addr = %x, data = %x, \n", req_bits.op, req_bits.addr, req_bits.data);
                }
                else if (req_bits.op == 2) {
                    printf("dmi req write: op = %0x, addr = %x, data = %x\n", req_bits.op, req_bits.addr, req_bits.data);
                }
                else {
                    printf("dmi req none: op = %0x, addr = %x, data = %x\n", req_bits.op, req_bits.addr, req_bits.data);
                }
                debug_req_ready = 1;
                dmi2jtag_state = DMI2JTAG_ST_RESP_SEND;
                break;
            }
            case DMI2JTAG_ST_RESP_SEND: {
                debug_req_ready = 0;
                if (debug_resp_ready) {
                    dtm_t::resp resp_cur;
                    if (recv(sock_cli, &resp_cur, sizeof(resp_cur), 0) <= 0) {
                        fprintf(stderr, "recv failed: %s (%d)\n", strerror(errno), errno);
                        abort();
                    }
                    debug_resp_valid = 1;
                    debug_resp_bits_resp = resp_cur.resp;
                    debug_resp_bits_data = resp_cur.data;
                    printf("dmi resp: resp = %0x, data = %x\n",resp_cur.resp, resp_cur.data);
                    dmi2jtag_state = DMI2JTAG_ST_RESP_DONE;
                    sleep(1);
                }
                break;
            }
            case DMI2JTAG_ST_RESP_DONE: {
                debug_resp_valid = 0;
                debug_req_ready = 0;
                dmi2jtag_state = DMI2JTAG_ST_INIT;
                break;
            }
        }
    }
}

//extern "C" int zqh_dmi2jtag_client_start(int port) {
int main(int argc,char **argv) {
    zqh_dmi2jtag_xaction_client(argc, argv);
    return 0;
}
