//dtm use abstract commond to do memory read/write
#include <fesvr/dtm.h>
#include <vpi_user.h>
#include <svdpi.h>

#include "zqh_jtag_common.h"



dtm_t* dtm2jtag;

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

int debug_tick ()
{
  if (!dtm2jtag) {
    s_vpi_vlog_info info;
    if (!vpi_get_vlog_info(&info))
      abort();
      dtm2jtag = new dtm_t(info.argc, info.argv);
  }

  dtm_t::resp resp_bits;
  resp_bits.resp = debug_resp_bits_resp;
  resp_bits.data = debug_resp_bits_data;

  dtm2jtag->tick
  (
    debug_req_ready,
    debug_resp_valid,
    resp_bits
  );

  debug_resp_ready = dtm2jtag->resp_ready();
  debug_req_valid = dtm2jtag->req_valid();
  debug_req_bits_addr = dtm2jtag->req_bits().addr;
  debug_req_bits_op = dtm2jtag->req_bits().op;
  debug_req_bits_data = dtm2jtag->req_bits().data;

  return dtm2jtag->done() ? (dtm2jtag->exit_code() << 1 | 1) : 0;
}

int jtag_state_pre = JTAG_ST_TestLogicReset;
int jtag_state = JTAG_ST_TestLogicReset;
int jtag_tick_cnt = 0;
int jtag_access_done = 0;
int jtag_inst_len = 5;

uint64_t jtag_tdo_all = 0;
int dmi2jtag_state = DMI2JTAG_ST_INIT;

unsigned char tck_var = 1;
unsigned char tms_var = 1;
unsigned char tdi_var = 1;
unsigned char trstn_var = 1;
unsigned char tdo_var = 1;

void set_pins(char _tck, char _tms, char _tdi){
  tck_var = _tck;
  tms_var = _tms;
  tdi_var = _tdi;
}

dtm_t::req dmi_req;
dtm_t::req get_dmi_req() {
  dtm_t::req req;

  if (debug_req_valid) {
      req.op = debug_req_bits_op;
      req.addr = debug_req_bits_addr;
      req.data = debug_req_bits_data;
      //printf("Received a req: op = %0x, data = %x, addr = %x\n", req.op, req.data, req.addr);
      return req;
  }
}

void send_dmi_resp(dtm_t::resp resp) {
    debug_resp_valid = 1;
    debug_resp_bits_resp = resp.resp;
    debug_resp_bits_data = resp.data;
    //printf("Send a resp: resp = %0x, data = %x\n", resp.resp, resp.data);
}


void jtag_goto_test_logic_reset() {
    if (tck_var == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void jtag_goto_run_test_idle() {
    if (tck_var == 1) {
        set_pins(0, 0, 0);
    }
    else {
        set_pins(1, 0, 0);
    }
}

void jtag_goto_select_dr_scan() {
    if (tck_var == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void jtag_goto_select_ir_scan() {
    if (tck_var == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void jtag_goto_capture_ir() {
    if (tck_var == 1) {
        set_pins(0, 0, 0);
    }
    else {
        set_pins(1, 0, 0);
    }
}

void jtag_goto_shift_ir(int di = 0) {
    if (tck_var == 1) {
        set_pins(0, 0, di);
    }
    else {
        set_pins(1, 0, di);
    }
}

void jtag_goto_exit_1_ir(int di) {
    if (tck_var == 1) {
        set_pins(0, 1, di);
    }
    else {
        set_pins(1, 1, di);
    }
}


void jtag_do_shift_ir(int a) {
    int tdi_bit;
    //shift idcode instruction
    tdi_bit = (a >> (jtag_tick_cnt/2)) & 1;

    //last bit
    if (jtag_tick_cnt >= ((jtag_inst_len - 1) * 2)) {
        jtag_goto_exit_1_ir(tdi_bit);
    }
    else {
        jtag_goto_shift_ir(tdi_bit);
    }

}

void jtag_goto_update_ir() {
    if (tck_var == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void jtag_goto_capture_dr() {
    if (tck_var == 1) {
        set_pins(0, 0, 0);
    }
    else {
        set_pins(1, 0, 0);
    }
}

char jtag_goto_shift_dr(int di = 0) {
    if (tck_var == 1) {
        set_pins(0, 0, di);
    }
    else {
        set_pins(1, 0, di);
    }
    return tdo_var;
}

char jtag_goto_exit_1_dr(int di = 0) {
    if (tck_var == 1) {
        set_pins(0, 1, di);
    }
    else {
        set_pins(1, 1, di);
    }
    return tdo_var;
}

uint64_t jtag_do_shift_dr(int width = 32, uint64_t a = 0) {
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

void jtag_goto_update_dr() {
    if (tck_var == 1) {
        set_pins(0, 1, 0);
    }
    else {
        set_pins(1, 1, 0);
    }
}

void jtag_init(int a = 1) {
    int reset_cycle = 10;
    if (jtag_tick_cnt < reset_cycle*2) {
        jtag_goto_test_logic_reset();
        jtag_tick_cnt++;
    }
    else if (jtag_tick_cnt < ((a + reset_cycle) * 2)) {
        jtag_goto_run_test_idle();
        jtag_tick_cnt++;
    }
    if (jtag_tick_cnt == ((a + reset_cycle) * 2)) {
        jtag_tick_cnt = 0;
        jtag_access_done = 1;
        jtag_state_pre = jtag_state;
        jtag_state = JTAG_ST_RunTestIdle;
    }
}

uint64_t jtag_access(int inst, int width = 32, uint64_t wdata = 0) {
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
    
    //tmp printf("jtag access: inst %x\n", inst);
    //tmp printf("jtag access: wdata %lx\n", wdata);
    //tmp printf("jtag acess: rdata %lx\n", rdata);

    //tmp return rdata;

}

uint32_t jtag_dtmcs_read() {
    return jtag_access(0x10);
}

uint64_t jtag_dmi_write(uint64_t wdata) {
    return jtag_access(0x11, 41, wdata);
}

uint64_t jtag_dmi_read() {
    return jtag_access(0x11, 41);
}

extern "C" int jtag_tick
(
 int           jtag_socket_port,
 unsigned char * jtag_TCK,
 unsigned char * jtag_TMS,
 unsigned char * jtag_TDI,
 unsigned char * jtag_TRSTn,
 unsigned char jtag_TDO
)
{
    dtm_done = debug_tick();
    tdo_var = jtag_TDO;

    if (dtm_done) {
        //do nothing
    }
    else {
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
                if (debug_req_valid) {
                    if (dmi_req.op == 1) {
                        printf("dmi req read: op = %0x, addr = %x, data = %x\n", dmi_req.op, dmi_req.addr, dmi_req.data);
                    }
                    else if (dmi_req.op == 2) {
                        printf("dmi req write: op = %0x, addr = %x, data = %x\n", dmi_req.op, dmi_req.addr, dmi_req.data);
                    }
                    else {
                        printf("dmi req none: op = %0x, addr = %x, data = %x\n", dmi_req.op, dmi_req.addr, dmi_req.data);
                    }
                    dmi2jtag_state = DMI2JTAG_ST_REQ_READY;
                    debug_req_ready = 1;
                }
                break;
            }
            case DMI2JTAG_ST_REQ_READY: {
                uint32_t rdata;
                rdata = jtag_dtmcs_read();
                debug_req_ready = 0;
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
                if (debug_resp_ready) {
                    //printf("dtm is ready for resp\n");
                    dmi2jtag_state = DMI2JTAG_ST_RESP_SEND;
                }
                break;
            }
            case DMI2JTAG_ST_RESP_SEND: {
                uint64_t rdata;

                rdata = jtag_dmi_read();
                if (jtag_access_done) {
                    uint32_t addr;
                    dtm_t::resp resp;

                    //resp.resp = ((rdata & 0x3) == 0) ? 0 : 1;
                    resp.resp = rdata & 0x3;
                    resp.data = (rdata >> 2) & 0xffffffff;
                    addr = rdata >> 34;
                    printf("dmi resp: resp = %0x, data = %x\n",resp.resp, resp.data);
                    send_dmi_resp(resp);
                    dmi2jtag_state = DMI2JTAG_ST_RESP_DONE;
                    jtag_access_done = 0;
                }
                break;
            }
            case DMI2JTAG_ST_RESP_DONE: {
                debug_resp_valid = 0;
                dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
                //tmp for debug
                //quit = 1;
                break;
            }
        }
    }

    * jtag_TCK = tck_var;
    * jtag_TMS = tms_var;
    * jtag_TDI = tdi_var;
    * jtag_TRSTn = trstn_var;
}
