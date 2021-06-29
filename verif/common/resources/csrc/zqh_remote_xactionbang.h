// See LICENSE.Berkeley for license details.

#ifndef REMOTE_BITBANG_H
#define REMOTE_BITBANG_H

#include <stdint.h>
#include <sys/types.h>

#include "zqh_jtag_common.h"

class remote_xactionbang_t
{
public:
  // Create a new server, listening for connections from localhost on the given
  // port.
  remote_xactionbang_t(uint16_t port);

  // Do a bit of work.
  void tick(unsigned char * jtag_tck,
            unsigned char * jtag_tms,
            unsigned char * jtag_tdi,
            unsigned char * jtag_trstn,
            unsigned char jtag_tdo);

  unsigned char done() {return quit;}
  
  int exit_code() {return err;}
  
 private:

  int err;
  //zqh added
  int jtag_state_pre = JTAG_ST_TestLogicReset;
  int jtag_state = JTAG_ST_TestLogicReset;
  int jtag_tick_cnt = 0;
  int jtag_access_done = 0;
  int jtag_inst_len = 5;
  uint64_t jtag_tdo_all = 0;
  int dmi2jtag_state = DMI2JTAG_ST_INIT;

  
  unsigned char tck;
  unsigned char tms;
  unsigned char tdi;
  unsigned char trstn;
  unsigned char tdo;
  unsigned char quit;
    
  int socket_fd;
  int client_fd;

  static const ssize_t buf_size = 64 * 1024;
  char recv_buf[buf_size];
  ssize_t recv_start, recv_end;

  // Check for a client connecting, and accept if there is one.
  void accept();
  // Execute any commands the client has for us.
  // But we only execute 1 because we need time for the
  // simulation to run.
  void execute_command();

  // Reset. Currently does nothing.
  void reset();

  void set_pins(char _tck, char _tms, char _tdi);

  
  //zqh added
  void jtag_goto_test_logic_reset();
  void jtag_goto_run_test_idle();
  void jtag_init(int a = 1);
  void jtag_goto_select_dr_scan();
  void jtag_goto_select_ir_scan();
  void jtag_goto_capture_ir();
  void jtag_goto_shift_ir(int di = 0);
  void jtag_goto_exit_1_ir(int di);
  void jtag_do_shift_ir(int a);
  void jtag_goto_update_ir();
  void jtag_goto_capture_dr();
  char jtag_goto_shift_dr(int di = 0);
  char jtag_goto_exit_1_dr(int di = 0);
  uint64_t jtag_do_shift_dr(int width = 32, uint64_t a = 0);
  void jtag_goto_update_dr();
  uint64_t jtag_access(int inst, int width = 32, uint64_t wdata = 0);
  uint32_t jtag_dtmcs_read();
  uint64_t jtag_dmi_write(uint64_t wdata);
  uint64_t jtag_dmi_read();
  struct dtm_req {
    uint32_t addr;
    uint32_t op;
    uint32_t data;
  };
  struct dtm_resp {
    uint32_t resp;
    uint32_t data;
  };
  dtm_req dmi_req;
  dtm_req get_dmi_req();
  void send_dmi_resp(dtm_resp resp);

};

#endif
