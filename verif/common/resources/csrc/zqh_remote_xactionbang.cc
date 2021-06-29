
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstdlib>

#include "zqh_jtag_common.h"
#include "zqh_remote_xactionbang.h"

remote_xactionbang_t::remote_xactionbang_t(uint16_t port) :
  socket_fd(0),
  client_fd(0),
  recv_start(0),
  recv_end(0),
  err(0)
{
  socket_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (socket_fd == -1) {
    fprintf(stderr, "remote_bitbang failed to make socket: %s (%d)\n",
            strerror(errno), errno);
    abort();
  }

  fcntl(socket_fd, F_SETFL, O_NONBLOCK);
  int reuseaddr = 1;
  if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &reuseaddr,
                 sizeof(int)) == -1) {
    fprintf(stderr, "remote_bitbang failed setsockopt: %s (%d)\n",
            strerror(errno), errno);
    abort();
  }

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = INADDR_ANY;
  addr.sin_port = htons(port);

  if (::bind(socket_fd, (struct sockaddr *) &addr, sizeof(addr)) == -1) {
    fprintf(stderr, "remote_bitbang failed to bind socket: %s (%d)\n",
            strerror(errno), errno);
    abort();
  }

  if (listen(socket_fd, 1) == -1) {
    fprintf(stderr, "remote_bitbang failed to listen on socket: %s (%d)\n",
            strerror(errno), errno);
    abort();
  }

  socklen_t addrlen = sizeof(addr);
  if (getsockname(socket_fd, (struct sockaddr *) &addr, &addrlen) == -1) {
    fprintf(stderr, "remote_bitbang getsockname failed: %s (%d)\n",
            strerror(errno), errno);
    abort();
  }

  tck = 1;
  tms = 1;
  tdi = 1;
  trstn = 1;
  quit = 0;

  fprintf(stderr, "This emulator compiled with JTAG Remote Bitbang client. To enable, use +jtag_rbb_enable=1.\n");
  fprintf(stderr, "Listening on port %d\n",
         ntohs(addr.sin_port));
}

void remote_xactionbang_t::accept()
{

  fprintf(stderr,"Attempting to accept client socket\n");
  int again = 1;
  while (again != 0) {
    client_fd = ::accept(socket_fd, NULL, NULL);
    if (client_fd == -1) {
      if (errno == EAGAIN) {
        // No client waiting to connect right now.
      } else {
        fprintf(stderr, "failed to accept on socket: %s (%d)\n", strerror(errno),
                errno);
        again = 0;
        abort();
      }
    } else {
      fcntl(client_fd, F_SETFL, O_NONBLOCK);
      fprintf(stderr, "Accepted successfully.\n");
      again = 0;
    }
  }
}

void remote_xactionbang_t::jtag_goto_test_logic_reset() {
    if (tck == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void remote_xactionbang_t::jtag_goto_run_test_idle() {
    if (tck == 1) {
        set_pins(0, 0, 0);
    }
    else {
        set_pins(1, 0, 0);
    }
}

void remote_xactionbang_t::jtag_goto_select_dr_scan() {
    if (tck == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void remote_xactionbang_t::jtag_goto_select_ir_scan() {
    if (tck == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void remote_xactionbang_t::jtag_goto_capture_ir() {
    if (tck == 1) {
        set_pins(0, 0, 0);
    }
    else {
        set_pins(1, 0, 0);
    }
}

void remote_xactionbang_t::jtag_goto_shift_ir(int di) {
    if (tck == 1) {
        set_pins(0, 0, di);
    }
    else {
        set_pins(1, 0, di);
    }
}

void remote_xactionbang_t::jtag_goto_exit_1_ir(int di) {
    if (tck == 1) {
        set_pins(0, 1, di);
    }
    else {
        set_pins(1, 1, di);
    }
}


void remote_xactionbang_t::jtag_do_shift_ir(int a) {
    int tdi_bit;
    //shift idcode instruction
    //for (int i = 0; i < 5; i++) {
        tdi_bit = (a >> (jtag_tick_cnt/2)) & 1;

        //last bit
        if (jtag_tick_cnt >= ((jtag_inst_len - 1) * 2)) {
            jtag_goto_exit_1_ir(tdi_bit);
        }
        else {
            jtag_goto_shift_ir(tdi_bit);
        }

    //}
}

void remote_xactionbang_t::jtag_goto_update_ir() {
    if (tck == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void remote_xactionbang_t::jtag_goto_capture_dr() {
    if (tck == 1) {
        set_pins(0, 0, 0);
    }
    else {
        set_pins(1, 0, 0);
    }
}

char remote_xactionbang_t::jtag_goto_shift_dr(int di) {
    if (tck == 1) {
        set_pins(0, 0, di);
    }
    else {
        set_pins(1, 0, di);
    }
    return tdo;
}

char remote_xactionbang_t::jtag_goto_exit_1_dr(int di) {
    if (tck == 1) {
        set_pins(0, 1, di);
    }
    else {
        set_pins(1, 1, di);
    }
    return tdo;
}

uint64_t remote_xactionbang_t::jtag_do_shift_dr(int width, uint64_t a) {
    int tdi_bit;
    uint64_t tdo_bit = 0;
    uint64_t tdo_all = 0;

    if (jtag_tick_cnt == 0) {
        jtag_tdo_all = 0;
    }

    tdi_bit = (a >> (jtag_tick_cnt/2)) & 1;
    //printf("jtag_do_shift_dr: width = %0d\n", width);
    //printf("jtag_do_shift_dr: jtag_tick_cnt = %0d\n", jtag_tick_cnt);
    if (jtag_tick_cnt >= (width - 1)*2) {
        tdo_bit = jtag_goto_exit_1_dr(tdi_bit);
        //printf("jtag_do_shift_dr: jtag_goto_exit_1_dr\n");
    }
    else {
        //printf("jtag_do_shift_dr: jtag_goto_shift_dr\n");
        tdo_bit = jtag_goto_shift_dr(tdi_bit);
    }

    if ((jtag_tick_cnt & 1) == 1) {
        jtag_tdo_all = jtag_tdo_all | (tdo_bit << (jtag_tick_cnt/2));
    }

    return jtag_tdo_all;
}

void remote_xactionbang_t::jtag_goto_update_dr() {
    if (tck == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void remote_xactionbang_t::jtag_init(int a) {
    if (jtag_tick_cnt < 2) {
        jtag_goto_test_logic_reset();
        jtag_tick_cnt++;
    }
    else if (jtag_tick_cnt < ((a + 1) * 2)) {
        jtag_goto_run_test_idle();
        jtag_tick_cnt++;
    }
    if (jtag_tick_cnt == ((a + 1) * 2)) {
        jtag_tick_cnt = 0;
        jtag_access_done = 1;
        jtag_state_pre = jtag_state;
        jtag_state = JTAG_ST_RunTestIdle;
    }
}

uint64_t remote_xactionbang_t::jtag_access(int inst, int width, uint64_t wdata) {
    //printf("jtag_access: jtag_state_pre = %d\n", jtag_state_pre);
    //printf("jtag_access: jtag_state = %d\n", jtag_state);
    switch(jtag_state) {
        case(JTAG_ST_TestLogicReset):{
            jtag_goto_run_test_idle();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2) {
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_RunTestIdle;
                jtag_tick_cnt = 0;
            }
            break;
        }
        case(JTAG_ST_RunTestIdle):{
            jtag_goto_select_dr_scan();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2) {
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_SelectDRScan;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_select_dr_scan\n");
            }
            break;
        }
        case(JTAG_ST_SelectDRScan):{
            if (jtag_state_pre == JTAG_ST_UpdateIR) {
                jtag_goto_capture_dr();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2){
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_CaptureDR;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_capture_dr\n");
                }
            }
            else {
                jtag_goto_select_ir_scan();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2) {
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_SelectIRScan;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_select_ir_scan\n");
                }
            }
            break;
        }
        case(JTAG_ST_SelectIRScan):{
            jtag_goto_capture_ir();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2) {
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_CaptureIR;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_capture_ir\n");
            }
            break;
        }
        case(JTAG_ST_CaptureIR):{
            jtag_goto_shift_ir();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2) {
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_ShiftIR;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_shift_ir\n");
            }
            break;
        }
        case(JTAG_ST_ShiftIR):{
            jtag_do_shift_ir(inst);
            jtag_tick_cnt++;
            if (jtag_tick_cnt == (jtag_inst_len * 2)) {
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_Exit1IR;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_exit_1_ir\n");
            }
            break;
        }
        case(JTAG_ST_Exit1IR):{
            jtag_goto_update_ir();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2){
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_UpdateIR;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_update_ir\n");
            }
            break;
        }
        case(JTAG_ST_UpdateIR):{
            jtag_goto_select_dr_scan();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2){
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_SelectDRScan;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_select_dr_scan\n");
            }
            break;
        }
        case(JTAG_ST_CaptureDR):{
            jtag_goto_shift_dr();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2){
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_ShiftDR;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_shift_dr\n");
            }
            break;
        }
        case(JTAG_ST_ShiftDR):{
            jtag_do_shift_dr(width, wdata);
            jtag_tick_cnt++;
            if (jtag_tick_cnt == (width * 2)) {
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_Exit1DR;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_exit_1_dr\n");
            }
            break;
        }
        case(JTAG_ST_Exit1DR):{
            jtag_goto_update_dr();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2){
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_UpdateDR;
                jtag_tick_cnt = 0;
                //printf("jtag_access: jtag_goto_update_dr\n");
            }
            break;
        }
        case(JTAG_ST_UpdateDR):{
            jtag_goto_run_test_idle();
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2){
                jtag_state_pre = jtag_state;
                jtag_state = JTAG_ST_RunTestIdle;
                jtag_tick_cnt = 0;
                jtag_access_done = 1;
                //printf("jtag_access: jtag_goto_run_test_idle\n");
            }
            break;
        }
    }
    return jtag_tdo_all;
}

uint32_t remote_xactionbang_t::jtag_dtmcs_read() {
    return jtag_access(0x10);
}

uint64_t remote_xactionbang_t::jtag_dmi_write(uint64_t wdata) {
    return jtag_access(0x11, 41, wdata);
}

uint64_t remote_xactionbang_t::jtag_dmi_read() {
    return jtag_access(0x11, 41);
}

void remote_xactionbang_t::tick(
                            unsigned char * jtag_tck,
                            unsigned char * jtag_tms,
                            unsigned char * jtag_tdi,
                            unsigned char * jtag_trstn,
                            unsigned char jtag_tdo
                            )
{
  if (client_fd > 0) {
    tdo = jtag_tdo;
    execute_command();
  } else {
    this->accept();
  }

  * jtag_tck = tck;
  * jtag_tms = tms;
  * jtag_tdi = tdi;
  * jtag_trstn = trstn;

}

void remote_xactionbang_t::reset(){
  //trstn = 0;
}

void remote_xactionbang_t::set_pins(char _tck, char _tms, char _tdi){
  tck = _tck;
  tms = _tms;
  tdi = _tdi;
}

remote_xactionbang_t::dtm_req remote_xactionbang_t::get_dmi_req() {
  //tmp char command;
  dtm_req req;
  int again = 1;
  while (again) {
    ssize_t num_read = read(client_fd, &req, sizeof(req));
    if (num_read == -1) {
      if (errno == EAGAIN) {
        // We'll try again the next call.
        //fprintf(stderr, "Received no command. Will try again on the next call\n");
      } else {
        fprintf(stderr, "remote_bitbang failed to read on socket: %s (%d)\n",
                strerror(errno), errno);
        again = 0;
        abort();
      }
    } else if (num_read == 0) {
      fprintf(stderr, "No Command Received.\n");
      again = 1;
    } else {
      again = 0;
    }
  }
  //fprintf(stderr, "Received a req: op = %0x, data = %x, addr = %x\n", req.op, req.data, req.addr);
  return req;
}

void remote_xactionbang_t::send_dmi_resp(remote_xactionbang_t::dtm_resp resp) {
  while (1) {
    ssize_t bytes = write(client_fd, &resp, sizeof(resp));
    if (bytes == -1) {
      fprintf(stderr, "failed to write to socket: %s (%d)\n", strerror(errno), errno);
      abort();
    }
    if (bytes > 0) {
      break;
    }
  }
  //fprintf(stderr, "Send a resp: resp = %0x, data = %x\n", resp.resp, resp.data);
}

void remote_xactionbang_t::execute_command() {
  if (quit) {
      return;
  }

  switch(dmi2jtag_state) {
      case DMI2JTAG_ST_INIT: {
          jtag_init();
          if (jtag_access_done) {
              printf("jtag_init done\n");
              dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
              jtag_access_done = 0;
          }
          break;
      }
      case DMI2JTAG_ST_REQ_CHECK: {
          dmi_req = get_dmi_req();
          if (dmi_req.op == 1) {
              //printf("dmi read req: op = %0x, data = %x, addr = %x\n", dmi_req.op, dmi_req.data, dmi_req.addr);
          }
          else {
              //printf("dmi write req: op = %0x, data = %x, addr = %x\n", dmi_req.op, dmi_req.data, dmi_req.addr);
          }
          dmi2jtag_state = DMI2JTAG_ST_REQ_READY;
          break;
      }
      case DMI2JTAG_ST_REQ_READY: {
          uint32_t rdata;
          rdata = jtag_dtmcs_read();
          if (jtag_access_done) {
              int dmistat;
              //printf("dtmcs rdata: %x\n", rdata);
              dmistat = (rdata >> 10) & 0x3;
              if (dmistat == 0) {
                  //printf("dtmcs dmistat is free for req\n");
                  dmi2jtag_state = DMI2JTAG_ST_REQ_SEND;
              }
              jtag_access_done = 0;
          }
          break;

      }
      case DMI2JTAG_ST_REQ_SEND: {
          uint64_t wdata;

          wdata = dmi_req.op | (((uint64_t)(dmi_req.data)) << 2) | (((uint64_t)(dmi_req.addr)) << 34);
          jtag_dmi_write(wdata);
          if (jtag_access_done) {
              dmi2jtag_state = DMI2JTAG_ST_RESP_CHECK;
              jtag_access_done = 0;
          }
          break;
      }
      case DMI2JTAG_ST_RESP_CHECK: {
          uint32_t rdata;
          uint32_t dmistat;
          rdata = jtag_dtmcs_read();
          if (jtag_access_done) {
              //printf("dtmcs rdata: %x\n", rdata);
              dmistat = (rdata >> 10) & 0x3;
              if (dmistat == 0) {
                  //printf("dtmcs dmistat is free for resp\n");
                  dmi2jtag_state = DMI2JTAG_ST_RESP_READY;
              }
              jtag_access_done = 0;
          }
          break;
      }
      case DMI2JTAG_ST_RESP_READY: {
          dmi2jtag_state = DMI2JTAG_ST_RESP_SEND;
          break;
      }
      case DMI2JTAG_ST_RESP_SEND: {
          uint64_t rdata;

          rdata = jtag_dmi_read();
          if (jtag_access_done) {
              uint32_t addr;
              dtm_resp resp;

              resp.resp = ((rdata & 0x3) == 0) ? 0 : 1;
              resp.data = (rdata >> 2) & 0xffffffff;
              addr = rdata >> 34;
              dmi2jtag_state = DMI2JTAG_ST_RESP_DONE;
              //printf("dmi resp: resp = %0x, data = %x, addr = %x\n",resp.resp, resp.data, addr);
              send_dmi_resp(resp);
              jtag_access_done = 0;
          }
          break;
      }
      case DMI2JTAG_ST_RESP_DONE: {
          dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
          //tmp for debug
          //quit = 1;
          break;
      }
  }
}
