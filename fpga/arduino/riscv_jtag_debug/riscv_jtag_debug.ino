#define BAUD_RATE 57600

int serial_putc( char c, struct __file * )
{
  Serial.write( c );  
  return c;
}
void printf_begin(void)
{
  fdevopen( &serial_putc, 0 );
}

#define TCK_PIN 13
#define TMS_PIN 12
#define TDI_PIN 11
#define TDO_PIN 10


#define JTAG_ST_TestLogicReset  0
#define JTAG_ST_RunTestIdle     1
#define JTAG_ST_SelectDRScan    2
#define JTAG_ST_CaptureDR       3
#define JTAG_ST_ShiftDR         4
#define JTAG_ST_Exit1DR         5
#define JTAG_ST_PauseDR         6
#define JTAG_ST_Exit2DR         7
#define JTAG_ST_UpdateDR        8
#define JTAG_ST_SelectIRScan    9
#define JTAG_ST_CaptureIR      10
#define JTAG_ST_ShiftIR        11
#define JTAG_ST_Exit1IR        12
#define JTAG_ST_PauseIR        13
#define JTAG_ST_Exit2IR        14
#define JTAG_ST_UpdateIR       15

#define DMI2JTAG_ST_INIT       0
#define DMI2JTAG_ST_REQ_CHECK  1
#define DMI2JTAG_ST_REQ_READY  2
#define DMI2JTAG_ST_REQ_SEND   3
#define DMI2JTAG_ST_RESP_CHECK 4
#define DMI2JTAG_ST_RESP_READY 5
#define DMI2JTAG_ST_RESP_SEND  6
#define DMI2JTAG_ST_RESP_DONE  7
#define DMI2JTAG_ST_EXIT       8


void setup() {
  // put your setup code here, to run once:
  Serial.begin(BAUD_RATE);
  printf_begin();

  pinMode(TCK_PIN,OUTPUT);
  pinMode(TMS_PIN,OUTPUT);
  pinMode(TDI_PIN,OUTPUT);
  pinMode(TDO_PIN,INPUT);
}

void delay_sw(uint16_t a) {
    for (uint16_t i = 0; i < a; i++) {
        for (uint16_t j = 0; j < 3000; j++) {
            _NOP();
        }
    }
}


uint8_t jtag_state_pre = JTAG_ST_TestLogicReset;
uint8_t jtag_state = JTAG_ST_TestLogicReset;
uint8_t jtag_tick_cnt = 0;
uint8_t jtag_access_done = 0;
uint8_t jtag_inst_len = 5;

uint64_t jtag_tdo_all = 0;
uint8_t dmi2jtag_state = DMI2JTAG_ST_INIT;

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

struct debug_request {
    uint8_t op;
    uint32_t addr;
    uint32_t data;
};

struct debug_response {
    uint8_t resp;
    uint32_t data;
};

struct debug_request dmi_req;
uint8_t dmi_req_valid = 0;
struct debug_response dmi_resp;
uint8_t dmi_resp_valid = 0;

struct debug_request sba_req;
uint8_t sba_req_valid = 0;
struct debug_response sba_resp;
uint8_t sba_resp_valid = 0;

void gen_dmi_req(uint8_t op, uint32_t addr, uint32_t data) {
    dmi_req.op = op;
    dmi_req.addr = addr;
    dmi_req.data = data;
    dmi_req_valid = 1;
}
void gen_dmi_req_write(uint32_t addr, uint32_t data) {
    gen_dmi_req(2, addr, data);
}
void gen_dmi_req_read(uint32_t addr) {
    gen_dmi_req(1, addr, 0);
}

//struct debug_request get_dmi_req() {
//   debug_request req;

//   req.op = 1;
//   req.addr = 0x12;
//   req.data = 0;
   //printf("Received a req: op = %0x, data = %x, addr = %x\n", req.op, req.data, req.addr);
   //dmi_req_valid = 1;
//   return req;
//}

uint8_t resp_error_cnt = 0;
void send_dmi_resp(struct debug_response resp) {
    //printf("Send a resp: resp = %0x, data = %x\n", resp.resp, resp.data);
    if (resp.resp != 0) {
        resp_error_cnt++;
        printf("dmi response has error %d\n", resp_error_cnt);
        if (resp_error_cnt == 2) {
            while(1);
        }
    }
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

void jtag_goto_shift_ir(uint8_t di = 0) {
    if (tck_var == 1) {
        set_pins(0, 0, di);
    }
    else {
        set_pins(1, 0, di);
    }
}

void jtag_goto_exit_1_ir(uint8_t di) {
    if (tck_var == 1) {
        set_pins(0, 1, di);
    }
    else {
        set_pins(1, 1, di);
    }
}


void jtag_do_shift_ir(uint8_t a) {
    uint8_t tdi_bit;
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

char jtag_goto_shift_dr(uint8_t di = 0) {
    if (tck_var == 1) {
        set_pins(0, 0, di);
    }
    else {
        set_pins(1, 0, di);
    }
    return tdo_var;
}

char jtag_goto_exit_1_dr(uint8_t di = 0) {
    if (tck_var == 1) {
        set_pins(0, 1, di);
    }
    else {
        set_pins(1, 1, di);
    }
    return tdo_var;
}

uint64_t jtag_do_shift_dr(uint8_t width = 32, uint64_t a = 0) {
    uint8_t tdi_bit;
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

void jtag_init(uint8_t a = 1) {
    uint8_t reset_cycle = 10;
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

uint64_t jtag_access(uint8_t inst, uint8_t width = 32, uint64_t wdata = 0) {
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
            //if (jtag_tick_cnt < 10) {
            //  jtag_goto_run_test_idle();
            //}
            //else {
              jtag_goto_select_dr_scan();
            //}
            jtag_tick_cnt++;
            if (jtag_tick_cnt == 2) {
            //if (jtag_tick_cnt == 12) {
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

void jtag_dmi_write(uint64_t wdata) {
    jtag_access(0x11, 41, wdata);
}

uint64_t jtag_dmi_read() {
    return jtag_access(0x11, 41);
}

uint8_t jtag_TCK;
uint8_t jtag_TMS;
uint8_t jtag_TDI;
uint8_t jtag_TRSTn;
uint8_t jtag_TDO;

void jtag_tick() {
    tdo_var = jtag_TDO;
    switch(dmi2jtag_state) {
        case DMI2JTAG_ST_INIT: {
            dmi_resp_valid = 0;
            jtag_init();
            if (jtag_access_done) {
                printf("jtag_init done\n");
                dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
                jtag_access_done = 0;
            }
            break;
        }
        case DMI2JTAG_ST_REQ_CHECK: {
            //dmi_req = get_dmi_req();
            dmi_resp_valid = 0;
            if (dmi_req_valid) {
                //if (dmi_req.op == 1) {
                //    printf("dmi req read: op = %0x, addr = %lx, data = %lx\n", dmi_req.op, dmi_req.addr, dmi_req.data);
                //}
                //else if (dmi_req.op == 2) {
                //    printf("dmi req write: op = %0x, addr = %lx, data = %lx\n", dmi_req.op, dmi_req.addr, dmi_req.data);
                //}
                //else {
                //    printf("dmi req none: op = %0x, addr = %lx, data = %lx\n", dmi_req.op, dmi_req.addr, dmi_req.data);
                //}
                dmi2jtag_state = DMI2JTAG_ST_REQ_READY;
            }
            break;
        }
        case DMI2JTAG_ST_REQ_READY: {
            uint32_t rdata;
            rdata = jtag_dtmcs_read();
            if (jtag_access_done) {
                int dmistat;
                //printf("dtmcs rdata: %lx\n", rdata);
                dmistat = (rdata >> 10) & 0x3;
                if (dmistat == 0) {
                    //printf("dtmcs dmistat is free for req\n");
                    dmi2jtag_state = DMI2JTAG_ST_REQ_SEND;
                }
                jtag_access_done = 0;
                dmi_req_valid = 0;
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
                //printf("dtmcs rdata: %lx\n", rdata);
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
            //printf("dtm is ready for resp\n");
            dmi2jtag_state = DMI2JTAG_ST_RESP_SEND;
            break;
        }
        case DMI2JTAG_ST_RESP_SEND: {
            uint64_t rdata;

            rdata = jtag_dmi_read();
            if (jtag_access_done) {
                //dmi_resp.resp = ((rdata & 0x3) == 0) ? 0 : 1;
                dmi_resp.resp = rdata & 0x3;
                dmi_resp.data = (rdata >> 2) & 0xffffffff;
                //printf("dmi resp: resp = %0x, data = %lx\n",dmi_resp.resp, dmi_resp.data);
                send_dmi_resp(dmi_resp);
                dmi2jtag_state = DMI2JTAG_ST_RESP_DONE;
                jtag_access_done = 0;
            }
            break;
        }
        case DMI2JTAG_ST_RESP_DONE: {
            dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
            dmi_resp_valid = 1;
            break;
        }
    }

    jtag_TCK = tck_var;
    jtag_TMS = tms_var;
    jtag_TDI = tdi_var;
    jtag_TRSTn = trstn_var;
}

//ascii string to int
uint32_t my_atoi_16(char *str) {
  int len;
  int char_idx;
  uint32_t resault;
  uint32_t cur_int;
  uint8_t shift_n;
  resault = 0;
  len = strlen(str);
  char_idx = 0;
  for (int i = len - 1; i >= 0; i--) {
    cur_int = 0;
    //end char
    if ((str[i] == '\r') || (str[i] == '\n') || (str[i] == ' ')) {
      //cur_int = 0;
      continue;
    }
    else if ((str[i] >= '0') && (str[i] <= '9')) {
      cur_int = str[i] - '0';
      char_idx++;
    }
    else if ((str[i] >= 'a') && (str[i] <= 'f')) {
      cur_int = str[i] - 'a' + 10;
      char_idx++;
    }
    else if ((str[i] >= 'A') && (str[i] <= 'F')) {
      cur_int = str[i] - 'A' + 10;
      char_idx++;
    }
    //illegal char
    else {
      cur_int = 0;
      resault = 0;
      break;
    }

    shift_n = (char_idx - 1)*4;
    resault = resault + (cur_int << shift_n);
  }
  return resault;
}

void send_back(uint8_t ptr[]) {
  uint8_t len;
  len = strlen(ptr);
  for (int i = 0; i < len; i++) {
    Serial.write(ptr[i]);
  }
}



uint8_t inByte = 0;         // incoming serial byte
#define DMI_IDLE      0
#define DMI_RECV_OP   1
#define DMI_RECV_ADDR 2
#define DMI_RECV_DATA 3
#define DMI_CMD   4
#define DMI_SBA_CMD   5
uint8_t dmi_state = DMI_IDLE;
uint8_t cmd_is_sba = 0;
uint8_t recv_idx = 0;
uint8_t recv_bytes_op[4];
uint8_t recv_bytes_addr[20];
uint8_t recv_bytes_data[20];

#define SBA_IDLE      0
#define SBA_SBCS_SET       1
#define SBA_ADDR0_SET      2
#define SBA_ADDR1_SET      3
#define SBA_DATA0_SET      4
#define SBA_DATA1_SET      5
#define SBA_SBCS_BUSY_CHK  6
#define SBA_DATA0_RD       7
#define SBA_RESP           8
uint8_t sba_state = SBA_IDLE;

#define DMI_SBCS                            0x38

#define DMI_SBCS_SBBUSY_OFFSET        21
#define DMI_SBCS_SBBUSY_LENGTH        1
#define DMI_SBCS_SBBUSY               ((uint32_t (0x1)) << DMI_SBCS_SBBUSY_OFFSET)

#define DMI_SBCS_SBBUSYERROR_OFFSET        22
#define DMI_SBCS_SBBUSYERROR_LENGTH        1
#define DMI_SBCS_SBBUSYERROR               ((uint32_t (0x1)) << DMI_SBCS_SBBUSYERROR_OFFSET)

/*
* When a 1 is written here, triggers a read at the address in {\tt
* sbaddress} using the access size set by \Fsbaccess.
 */
#define DMI_SBCS_SBSINGLEREAD_OFFSET        20
#define DMI_SBCS_SBSINGLEREAD_LENGTH        1
#define DMI_SBCS_SBSINGLEREAD               ((uint32_t (0x1)) << DMI_SBCS_SBSINGLEREAD_OFFSET)
/*
* Select the access size to use for system bus accesses triggered by
* writes to the {\tt sbaddress} registers or \Rsbdatazero.
*
* 0: 8-bit
*
* 1: 16-bit
*
* 2: 32-bit
*
* 3: 64-bit
*
* 4: 128-bit
*
* If an unsupported system bus access size is written here,
* the DM may not perform the access, or may perform the access
* with any access size.
 */
#define DMI_SBCS_SBACCESS_OFFSET            17
#define DMI_SBCS_SBACCESS_LENGTH            3
#define DMI_SBCS_SBACCESS                   ((uint32_t (0x7)) << DMI_SBCS_SBACCESS_OFFSET)
/*
* When 1, the internal address value (used by the system bus master)
* is incremented by the access size (in bytes) selected in \Fsbaccess
* after every system bus access.
 */
#define DMI_SBCS_SBAUTOINCREMENT_OFFSET     16
#define DMI_SBCS_SBAUTOINCREMENT_LENGTH     1
#define DMI_SBCS_SBAUTOINCREMENT            ((uint32_t (0x1)) << DMI_SBCS_SBAUTOINCREMENT_OFFSET)
/*
* When 1, every read from \Rsbdatazero automatically triggers a system
* bus read at the new address.
 */
#define DMI_SBCS_SBAUTOREAD_OFFSET          15
#define DMI_SBCS_SBAUTOREAD_LENGTH          1
#define DMI_SBCS_SBAUTOREAD                 ((uint32_t (0x1)) << DMI_SBCS_SBAUTOREAD_OFFSET)
/*
* When the debug module's system bus
* master causes a bus error, this field gets set. The bits in this
* field remain set until they are cleared by writing 1 to them.
* While this field is non-zero, no more system bus accesses can be
* initiated by the debug module.
*
* 0: There was no bus error.
*
* 1: There was a timeout.
*
* 2: A bad address was accessed.
*
* 3: There was some other error (eg. alignment).
*
* 4: The system bus master was busy when one of the
* {\tt sbaddress} or {\tt sbdata} registers was written,
* or the {\tt sbdata} register was read when it had
* stale data.
 */
#define DMI_SBCS_SBERROR_OFFSET             12
#define DMI_SBCS_SBERROR_LENGTH             3
#define DMI_SBCS_SBERROR                    ((uint32_t (0x7)) << DMI_SBCS_SBERROR_OFFSET)
/*
* Width of system bus addresses in bits. (0 indicates there is no bus
* access support.)
 */
#define DMI_SBCS_SBASIZE_OFFSET             5
#define DMI_SBCS_SBASIZE_LENGTH             7
#define DMI_SBCS_SBASIZE                    ((uint32_t (0x7f)) << DMI_SBCS_SBASIZE_OFFSET)
/*
* 1 when 128-bit system bus accesses are supported.
 */
#define DMI_SBCS_SBACCESS128_OFFSET         4
#define DMI_SBCS_SBACCESS128_LENGTH         1
#define DMI_SBCS_SBACCESS128                ((uint32_t (0x1)) << DMI_SBCS_SBACCESS128_OFFSET)
/*
* 1 when 64-bit system bus accesses are supported.
 */
#define DMI_SBCS_SBACCESS64_OFFSET          3
#define DMI_SBCS_SBACCESS64_LENGTH          1
#define DMI_SBCS_SBACCESS64                 ((uint32_t (0x1)) << DMI_SBCS_SBACCESS64_OFFSET)
/*
* 1 when 32-bit system bus accesses are supported.
 */
#define DMI_SBCS_SBACCESS32_OFFSET          2
#define DMI_SBCS_SBACCESS32_LENGTH          1
#define DMI_SBCS_SBACCESS32                 ((uint32_t (0x1)) << DMI_SBCS_SBACCESS32_OFFSET)
/*
* 1 when 16-bit system bus accesses are supported.
 */
#define DMI_SBCS_SBACCESS16_OFFSET          1
#define DMI_SBCS_SBACCESS16_LENGTH          1
#define DMI_SBCS_SBACCESS16                 ((uint32_t (0x1)) << DMI_SBCS_SBACCESS16_OFFSET)
/*
* 1 when 8-bit system bus accesses are supported.
 */
#define DMI_SBCS_SBACCESS8_OFFSET           0
#define DMI_SBCS_SBACCESS8_LENGTH           1
#define DMI_SBCS_SBACCESS8                  ((uint32_t (0x1)) << DMI_SBCS_SBACCESS8_OFFSET)
#define DMI_SBADDRESS0                      0x39
/*
* Accesses bits 31:0 of the internal address.
 */
#define DMI_SBADDRESS0_ADDRESS_OFFSET       0
#define DMI_SBADDRESS0_ADDRESS_LENGTH       32
#define DMI_SBADDRESS0_ADDRESS              ((uint32_t (0xffffffff)) << DMI_SBADDRESS0_ADDRESS_OFFSET)
#define DMI_SBADDRESS1                      0x3a
/*
* Accesses bits 63:32 of the internal address (if the system address
* bus is that wide).
 */
#define DMI_SBADDRESS1_ADDRESS_OFFSET       0
#define DMI_SBADDRESS1_ADDRESS_LENGTH       32
#define DMI_SBADDRESS1_ADDRESS              ((uint32_t (0xffffffff)) << DMI_SBADDRESS1_ADDRESS_OFFSET)
#define DMI_SBADDRESS2                      0x3b
/*
* Accesses bits 95:64 of the internal address (if the system address
* bus is that wide).
 */
#define DMI_SBADDRESS2_ADDRESS_OFFSET       0
#define DMI_SBADDRESS2_ADDRESS_LENGTH       32
#define DMI_SBADDRESS2_ADDRESS              ((uint32_t (0xffffffff)) << DMI_SBADDRESS2_ADDRESS_OFFSET)
#define DMI_SBDATA0                         0x3c
/*
* Accesses bits 31:0 of the internal data.
 */
#define DMI_SBDATA0_DATA_OFFSET             0
#define DMI_SBDATA0_DATA_LENGTH             32
#define DMI_SBDATA0_DATA                    ((uint32_t (0xffffffff)) << DMI_SBDATA0_DATA_OFFSET)
#define DMI_SBDATA1                         0x3d
/*
* Accesses bits 63:32 of the internal data (if the system bus is
* that wide).
 */
#define DMI_SBDATA1_DATA_OFFSET             0
#define DMI_SBDATA1_DATA_LENGTH             32
#define DMI_SBDATA1_DATA                    ((uint32_t (0xffffffff)) << DMI_SBDATA1_DATA_OFFSET)
#define DMI_SBDATA2                         0x3e
/*
* Accesses bits 95:64 of the internal data (if the system bus is
* that wide).
 */
#define DMI_SBDATA2_DATA_OFFSET             0
#define DMI_SBDATA2_DATA_LENGTH             32
#define DMI_SBDATA2_DATA                    ((uint32_t (0xffffffff)) << DMI_SBDATA2_DATA_OFFSET)
#define DMI_SBDATA3                         0x3f
/*
* Accesses bits 127:96 of the internal data (if the system bus is
* that wide).
 */
#define DMI_SBDATA3_DATA_OFFSET             0
#define DMI_SBDATA3_DATA_LENGTH             32
#define DMI_SBDATA3_DATA                    ((uint32_t (0xffffffff)) << DMI_SBDATA3_DATA_OFFSET)


//#define TDO_RD ((*portInputRegister(2) & 4) != 0)
#define TDO_RD (((*((volatile uint8_t *)(0x23))) & 4) != 0)
#define MY_DIGITALWRITE(BIT, VAL) \
    if (VAL == LOW) { \
    	*((volatile uint8_t *)(0x25)) &= ~BIT; \
    } else {  \
    	*((volatile uint8_t *)(0x25)) |= BIT; \
    }

#define TCK_WR(VAL) MY_DIGITALWRITE(32, VAL)
#define TMS_WR(VAL) MY_DIGITALWRITE(16, VAL)
#define TDI_WR(VAL) MY_DIGITALWRITE(8, VAL)




void loop() {
  uint8_t op;
  uint32_t addr;
  uint32_t wr_data;
    
  //jtag pin initial
  digitalWrite(TCK_PIN, 1);
  digitalWrite(TMS_PIN, 1);
  digitalWrite(TDI_PIN, 1);

  delay_sw(1000);
  printf("zqh_riscv_debug start\n");

  //clean recieve buffer
  if (Serial.available() > 0) {
    inByte = Serial.read();
  }

  //indicate host to send flash address and data
  Serial.print("**FLASH INIT DONE**\n");
    

  while(1) {
    if (dmi_state == DMI_CMD) {
      //jtag_TDO = digitalRead(TDO_PIN);
      jtag_TDO = TDO_RD;

      jtag_tick();

      //digitalWrite(TCK_PIN, jtag_TCK);
      TCK_WR(jtag_TCK);
      //digitalWrite(TMS_PIN, jtag_TMS);
      TMS_WR(jtag_TMS);
      //digitalWrite(TDI_PIN, jtag_TDI);
      TDI_WR(jtag_TDI);

      if (dmi_resp_valid == 1) {
        if (cmd_is_sba) {
            dmi_state = DMI_SBA_CMD;
        }
        else {
          Serial.print("#@\n");//resp key
          Serial.println(dmi_resp.resp, HEX);
          Serial.println(dmi_resp.data, HEX);
          dmi_state = DMI_IDLE;
          dmi_resp_valid = 0;
        }
      }
    }
    else if (dmi_state == DMI_SBA_CMD) {
      if (sba_state == SBA_IDLE) {
        sba_state = SBA_SBCS_SET;
      }
      else if (sba_state == SBA_SBCS_SET) {
        //printf("in SBA_SBCS_SET\n");
        if (dmi_resp_valid == 1) {
          sba_state = SBA_ADDR1_SET;
          dmi_resp_valid = 0;
        }
        else if (dmi_req_valid == 0) {
          //load
          if (sba_req.op == 1) {
            gen_dmi_req_write(DMI_SBCS, DMI_SBCS_SBBUSYERROR | DMI_SBCS_SBSINGLEREAD | ((uint32_t (2)) << DMI_SBCS_SBACCESS_OFFSET) | DMI_SBCS_SBERROR);
          }
          //store
          else if (sba_req.op == 2) {
            gen_dmi_req_write(DMI_SBCS, DMI_SBCS_SBBUSYERROR | ((uint32_t (2)) << DMI_SBCS_SBACCESS_OFFSET) | DMI_SBCS_SBERROR);
          }
          dmi_state = DMI_CMD;
        }
      }
      else if (sba_state == SBA_ADDR1_SET) {
        //printf("in SBA_ADDR1_SET\n");
        if (dmi_resp_valid == 1) {
          sba_state = SBA_ADDR0_SET;
          dmi_resp_valid = 0;
        }
        else if (dmi_req_valid == 0) {
          gen_dmi_req_write(DMI_SBADDRESS1, 0);//high 32bit
          dmi_state = DMI_CMD;
        }
      }
      else if (sba_state == SBA_ADDR0_SET) {
        //printf("in SBA_ADDR0_SET\n");
        if (dmi_resp_valid == 1) {
          //load
          if (sba_req.op == 1) {
            sba_state = SBA_SBCS_BUSY_CHK;
          }
          else if (sba_req.op == 2) {
            sba_state = SBA_DATA1_SET;
          }
          dmi_resp_valid = 0;
        }
        else if (dmi_req_valid == 0) {
          gen_dmi_req_write(DMI_SBADDRESS0, sba_req.addr);//low 32bit
          dmi_state = DMI_CMD;
        }
      }
      else if (sba_state == SBA_DATA1_SET) {
        //printf("in SBA_DATA1_SET\n");
        if (dmi_resp_valid == 1) {
          sba_state = SBA_DATA0_SET;
          dmi_resp_valid = 0;
        }
        else if (dmi_req_valid == 0) {
          gen_dmi_req_write(DMI_SBDATA1, 0);//high 32bit
          dmi_state = DMI_CMD;
        }
      }
      else if (sba_state == SBA_DATA0_SET) {
        //printf("in SBA_DATA0_SET\n");
        if (dmi_resp_valid == 1) {
          sba_state = SBA_SBCS_BUSY_CHK;
          dmi_resp_valid = 0;
        }
        else if (dmi_req_valid == 0) {
          gen_dmi_req_write(DMI_SBDATA0, sba_req.data);//low 32bit
          dmi_state = DMI_CMD;
        }
      }
      else if (sba_state == SBA_SBCS_BUSY_CHK) {
        //printf("in SBA_SBCS_BUSY_CHK\n");
        if (dmi_resp_valid == 1) {
          uint8_t sbcs_busy;
          uint8_t sbcs_error;
          sbcs_busy = (dmi_resp.data & DMI_SBCS_SBBUSY) >> DMI_SBCS_SBBUSY_OFFSET;
          sbcs_error = (dmi_resp.data & DMI_SBCS_SBERROR) >> DMI_SBCS_SBERROR_OFFSET;
          if (sbcs_busy) {
            gen_dmi_req_read(DMI_SBCS);
            dmi_state = DMI_CMD;
          }
          else {
              if (sbcs_error != 0) {
                //printf("sbcs_error = %x\n", sbcs_error);
                while(1);
              }
              //load
              if (sba_req.op == 1) {
                sba_state = SBA_DATA0_RD;
              }
              //store
              else if (sba_req.op == 2) {
                sba_state = SBA_RESP;
              }
          }
          dmi_resp_valid = 0;
        }
        else if (dmi_req_valid == 0) {
          gen_dmi_req_read(DMI_SBCS);
          dmi_state = DMI_CMD;
        }
      }
      else if (sba_state == SBA_DATA0_RD) {
        //printf("in SBA_DATA0_RD\n");
        if (dmi_resp_valid == 1) {
          sba_state = SBA_RESP;
          dmi_resp_valid = 0;
        }
        else if (dmi_req_valid == 0) {
          gen_dmi_req_read(DMI_SBDATA0);//low 32b
          dmi_state = DMI_CMD;
        }
      }
      else if (sba_state == SBA_RESP) {
        //printf("in SBA_RESP\n");
        Serial.print("#@\n");//resp key
        Serial.println(0, HEX);
        if (sba_req.op == 1) {
          Serial.println(dmi_resp.data, HEX);
        }
        else if (sba_req.op == 2) {
          Serial.println(0, HEX);
        }
        dmi_state = DMI_IDLE;
        sba_state = SBA_IDLE;
      }
    }
    else {
      if (Serial.available() <= 0) {
        continue;
      }
  
      // get incoming byte:
      inByte = Serial.read();
  
      if (dmi_state == DMI_IDLE) {
        if (inByte == '\n') {
          dmi_state = DMI_IDLE;
        }
        //dmi op
        else if (inByte == '#') {
          dmi_state = DMI_RECV_OP;
          recv_idx = 0;
          cmd_is_sba = 0;
        }
        //sba op
        else if (inByte == '$') {
          dmi_state = DMI_RECV_OP;
          recv_idx = 0;
          cmd_is_sba = 1;
          //printf("set cmd_is_sba\n");
        }
        //address
        else if (inByte == '@') {
          dmi_state = DMI_RECV_ADDR;
          recv_idx = 0;
        }
        //data
        else {
          dmi_state = DMI_RECV_DATA;
          recv_bytes_data[0] = inByte;
          recv_idx = 1;
        }
      }
      else if (dmi_state == DMI_RECV_OP) {
        recv_bytes_op[recv_idx] = inByte;
        recv_idx++;
        if (inByte == '\n') {
          recv_bytes_op[recv_idx] = 0;
          //addr = 0;
          //sscanf(recv_bytes_addr, "%x\n", &addr);
          op = my_atoi_16(recv_bytes_op);
  //        Serial.println(addr, HEX);
          //Serial.println(recv_bytes_addr);
          //send_back(recv_bytes_addr);
          dmi_state = DMI_IDLE;
        }
      }
      else if (dmi_state == DMI_RECV_ADDR) {
        recv_bytes_addr[recv_idx] = inByte;
        recv_idx++;
        if (inByte == '\n') {
          recv_bytes_addr[recv_idx] = 0;
          //addr = 0;
          //sscanf(recv_bytes_addr, "%x\n", &addr);
          addr = my_atoi_16(recv_bytes_addr);
  //        Serial.println(addr, HEX);
          //Serial.println(recv_bytes_addr);
          //send_back(recv_bytes_addr);
          dmi_state = DMI_IDLE;
        }
      }
      else if (dmi_state == DMI_RECV_DATA) {
        recv_bytes_data[recv_idx] = inByte;
        recv_idx++;
        if (inByte == '\n') {
          recv_bytes_data[recv_idx] = 0;
          //wr_data = 0;
          //sscanf(recv_bytes_data, "%x\n", &wr_data);
          wr_data = my_atoi_16(recv_bytes_data);
  
          if (cmd_is_sba) {
            sba_req.op = op;
            sba_req.addr = addr;
            sba_req.data = wr_data;
            sba_req_valid = 1;
            //printf("sba.op = %x\n", sba_req.op);
            //printf("sba.addr = %lx\n", sba_req.addr);
            //printf("sba.data = %lx\n", sba_req.data);
  
            dmi_state = DMI_SBA_CMD;
          }
          else {
            dmi_req.op = op;
            dmi_req.addr = addr;
            dmi_req.data = wr_data;
            dmi_req_valid = 1;
  
            dmi_state = DMI_CMD;
          }
        }
      }
    }
  }
}
