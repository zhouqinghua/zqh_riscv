module dmi_jtag_bfm#(
    parameter TICK_DELAY = 50,
    parameter JTAG_ST_TestLogicReset =  0,
    parameter JTAG_ST_RunTestIdle    =  1,
    parameter JTAG_ST_SelectDRScan   =  2,
    parameter JTAG_ST_CaptureDR      =  3,
    parameter JTAG_ST_ShiftDR        =  4,
    parameter JTAG_ST_Exit1DR        =  5,
    parameter JTAG_ST_PauseDR        =  6,
    parameter JTAG_ST_Exit2DR        =  7,
    parameter JTAG_ST_UpdateDR       =  8,
    parameter JTAG_ST_SelectIRScan   =  9,
    parameter JTAG_ST_CaptureIR      = 10,
    parameter JTAG_ST_ShiftIR        = 11,
    parameter JTAG_ST_Exit1IR        = 12,
    parameter JTAG_ST_PauseIR        = 13,
    parameter JTAG_ST_Exit2IR        = 14,
    parameter JTAG_ST_UpdateIR       = 15,
 
    parameter DMI2JTAG_ST_INIT       = 0,
    parameter DMI2JTAG_ST_REQ_CHECK  = 1,
    parameter DMI2JTAG_ST_REQ_READY  = 2,
    parameter DMI2JTAG_ST_REQ_SEND   = 3,
    parameter DMI2JTAG_ST_RESP_CHECK = 4,
    parameter DMI2JTAG_ST_RESP_READY = 5,
    parameter DMI2JTAG_ST_RESP_SEND  = 6,
    parameter DMI2JTAG_ST_RESP_DONE  = 7,
    parameter DMI2JTAG_ST_EXIT       = 8
)(

    input         clock,
    input         reset,
    input         enable,
    input         init_done,
    output reg       jtag_TCK,
    output reg       jtag_TMS,
    output reg       jtag_TDI,
    output reg       jtag_TRSTn,
    input         jtag_TDO_data,
    input         jtag_TDO_driven,
    output reg[31:0] exit
);
    class dmi_req;
        bit[31:0] addr;
        bit[31:0] op;
        bit[31:0] data;
    endclass

    class dmi_resp;
        bit[31:0] resp;
        bit[31:0] data;
    endclass

    dmi_req req_q[$];
    dmi_resp resp_q[$];

    reg[31:0] jtag_state_pre = JTAG_ST_TestLogicReset;
    reg[31:0] jtag_state = JTAG_ST_TestLogicReset;
    reg[31:0] jtag_tick_cnt = 0;
    reg[31:0] jtag_access_done = 0;
    reg[31:0] jtag_inst_len = 5;

    reg[63:0] jtag_tdo_all = 0;
    reg[31:0] dmi2jtag_state = DMI2JTAG_ST_INIT;
    
    reg tck_var = 1;
    reg tms_var = 1;
    reg tdi_var = 1;
    reg trstn_var = 1;
    reg tdo_var = 1;

    function void set_pins(bit _tck, bit _tms, bit _tdi);
        tck_var = _tck;
        tms_var = _tms;
        tdi_var = _tdi;
    endfunction
    
    dmi_req cur_req = new();
    function dmi_req get_dmi_req();
        dmi_req req;
        if (req_q.size() > 0) begin
            req = req_q.pop_front();
            //printf("Received a req: op = %0x, data = %x, addr = %x\n", req.op, req.data, req.addr);
        end
        else begin
            req = null;
        end
        return req;
    endfunction
    
    function void send_dmi_resp(dmi_resp resp);
        if (resp.resp != 0) begin
            $display("resp.resp has error: %x", resp.resp);
            while(1);
        end
        resp_q.push_back(resp);
        //printf("Send a resp: resp = %0x, data = %x\n", resp.resp, resp.data);
    endfunction
    
    
    function void jtag_goto_test_logic_reset();
        if (tck_var == 1) begin
            set_pins(0, 1, 0);
        end
        else begin
            set_pins(1, 1, 0);
        end
    endfunction
    
    function void jtag_goto_run_test_idle();
        if (tck_var == 1) begin
            set_pins(0, 0, 0);
        end
        else begin
            set_pins(1, 0, 0);
        end
    endfunction
    
    function void jtag_goto_select_dr_scan();
        if (tck_var == 1) begin
            set_pins(0, 1, 0);
        end
        else begin
            set_pins(1, 1, 0);
        end
    endfunction
    
    function void jtag_goto_select_ir_scan();
        if (tck_var == 1) begin
            set_pins(0, 1, 0);
        end
        else begin
            set_pins(1, 1, 0);
        end
    endfunction
    
    function void jtag_goto_capture_ir();
        if (tck_var == 1) begin
            set_pins(0, 0, 0);
        end
        else begin
            set_pins(1, 0, 0);
        end
    endfunction
    
    function void jtag_goto_shift_ir(int di = 0);
        if (tck_var == 1) begin
            set_pins(0, 0, di);
        end
        else begin
            set_pins(1, 0, di);
        end
    endfunction
    
    function void jtag_goto_exit_1_ir(int di);
        if (tck_var == 1) begin
            set_pins(0, 1, di);
        end
        else begin
            set_pins(1, 1, di);
        end
    endfunction
    
    
    function void jtag_do_shift_ir(int a);
        int tdi_bit;
        //shift idcode instruction
        tdi_bit = (a >> (jtag_tick_cnt/2)) & 1;
    
        //last bit
        if (jtag_tick_cnt >= ((jtag_inst_len - 1) * 2)) begin
            jtag_goto_exit_1_ir(tdi_bit);
        end
        else begin
            jtag_goto_shift_ir(tdi_bit);
        end
    
    endfunction
    
    function void jtag_goto_update_ir();
        if (tck_var == 1) begin
            set_pins(0, 1, 0);
        end
        else begin
            set_pins(1, 1, 0);
        end
    endfunction
    
    function void jtag_goto_capture_dr();
        if (tck_var == 1) begin
            set_pins(0, 0, 0);
        end
        else begin
            set_pins(1, 0, 0);
        end
    endfunction
    
    function bit[7:0] jtag_goto_shift_dr(int di = 0);
        if (tck_var == 1) begin
            set_pins(0, 0, di);
        end
        else begin
            set_pins(1, 0, di);
        end
        return tdo_var;
    endfunction
    
    function bit[7:0] jtag_goto_exit_1_dr(int di = 0);
        if (tck_var == 1) begin
            set_pins(0, 1, di);
        end
        else begin
            set_pins(1, 1, di);
        end
        return tdo_var;
    endfunction
    
    function bit[63:0] jtag_do_shift_dr(int width = 32, bit[63:0] a = 0);
        int tdi_bit;
        bit[63:0] tdo_bit = 0;
        bit[63:0] tdo_all = 0;
    
        if (jtag_tick_cnt == 0) begin
            jtag_tdo_all = 0;
        end
    
        tdi_bit = (a >> (jtag_tick_cnt/2)) & 1;
        //printf("jtag_do_shift_dr: width = %0d\n", width);
        //printf("jtag_do_shift_dr: jtag_tick_cnt = %0d\n", jtag_tick_cnt);
        if (jtag_tick_cnt >= (width - 1)*2) begin
            tdo_bit = jtag_goto_exit_1_dr(tdi_bit);
            //printf("jtag_do_shift_dr: jtag_goto_exit_1_dr\n");
        end
        else begin
            //printf("jtag_do_shift_dr: jtag_goto_shift_dr\n");
            tdo_bit = jtag_goto_shift_dr(tdi_bit);
        end
    
        if ((jtag_tick_cnt & 1) == 1) begin
            jtag_tdo_all = jtag_tdo_all | (tdo_bit << (jtag_tick_cnt/2));
        end
    
        return jtag_tdo_all;
    endfunction
    
    function void jtag_goto_update_dr();
        if (tck_var == 1) begin
            set_pins(0, 1, 0);
        end
        else begin
            set_pins(1, 1, 0);
        end
    endfunction
    
    function void jtag_init(int a = 1);
        int reset_cycle = 10;
        if (jtag_tick_cnt < reset_cycle*2) begin
            jtag_goto_test_logic_reset();
            jtag_tick_cnt++;
        end
        else if (jtag_tick_cnt < ((a + reset_cycle) * 2)) begin
            jtag_goto_run_test_idle();
            jtag_tick_cnt++;
        end
        if (jtag_tick_cnt == ((a + reset_cycle) * 2)) begin
            jtag_tick_cnt = 0;
            jtag_access_done = 1;
            jtag_state_pre = jtag_state;
            jtag_state = JTAG_ST_RunTestIdle;
        end
    endfunction
    
    function bit[63:0] jtag_access(int inst, int width = 32, bit[63:0] wdata = 0);
        //printf("jtag_access: jtag_state_pre = %d\n", jtag_state_pre);
        //printf("jtag_access: jtag_state = %d\n", jtag_state);
        case(jtag_state)
            JTAG_ST_TestLogicReset:begin
                jtag_goto_run_test_idle();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2) begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_RunTestIdle;
                    jtag_tick_cnt = 0;
                end
            end
            JTAG_ST_RunTestIdle:begin
                //run_test_idle keep 5 TCK clock
                //if (jtag_tick_cnt < 10) begin
                //    jtag_goto_run_test_idle();
                //end
                //else begin
                    jtag_goto_select_dr_scan();
                //end
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2) begin
                //if (jtag_tick_cnt == 12) begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_SelectDRScan;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_select_dr_scan\n");
                end
            end
            JTAG_ST_SelectDRScan:begin
                if (jtag_state_pre == JTAG_ST_UpdateIR) begin
                    jtag_goto_capture_dr();
                    jtag_tick_cnt++;
                    if (jtag_tick_cnt == 2)begin
                        jtag_state_pre = jtag_state;
                        jtag_state = JTAG_ST_CaptureDR;
                        jtag_tick_cnt = 0;
                        //printf("jtag_access: jtag_goto_capture_dr\n");
                    end
                end
                else begin
                    jtag_goto_select_ir_scan();
                    jtag_tick_cnt++;
                    if (jtag_tick_cnt == 2) begin
                        jtag_state_pre = jtag_state;
                        jtag_state = JTAG_ST_SelectIRScan;
                        jtag_tick_cnt = 0;
                        //printf("jtag_access: jtag_goto_select_ir_scan\n");
                    end
                end
            end
            JTAG_ST_SelectIRScan: begin
                jtag_goto_capture_ir();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2) begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_CaptureIR;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_capture_ir\n");
                end
            end
            JTAG_ST_CaptureIR:begin
                jtag_goto_shift_ir();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2) begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_ShiftIR;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_shift_ir\n");
                end
            end
            JTAG_ST_ShiftIR:begin
                jtag_do_shift_ir(inst);
                jtag_tick_cnt++;
                if (jtag_tick_cnt == (jtag_inst_len * 2)) begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_Exit1IR;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_exit_1_ir\n");
                end
            end
            JTAG_ST_Exit1IR:begin
                jtag_goto_update_ir();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2)begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_UpdateIR;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_update_ir\n");
                end
            end
            JTAG_ST_UpdateIR:begin
                jtag_goto_select_dr_scan();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2)begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_SelectDRScan;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_select_dr_scan\n");
                end
            end
            JTAG_ST_CaptureDR:begin
                jtag_goto_shift_dr();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2)begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_ShiftDR;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_shift_dr\n");
                end
            end
            JTAG_ST_ShiftDR:begin
                jtag_do_shift_dr(width, wdata);
                jtag_tick_cnt++;
                if (jtag_tick_cnt == (width * 2)) begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_Exit1DR;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_exit_1_dr\n");
                end
            end
            JTAG_ST_Exit1DR:begin
                jtag_goto_update_dr();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2)begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_UpdateDR;
                    jtag_tick_cnt = 0;
                    //printf("jtag_access: jtag_goto_update_dr\n");
                end
            end
            JTAG_ST_UpdateDR:begin
                jtag_goto_run_test_idle();
                jtag_tick_cnt++;
                if (jtag_tick_cnt == 2)begin
                    jtag_state_pre = jtag_state;
                    jtag_state = JTAG_ST_RunTestIdle;
                    jtag_tick_cnt = 0;
                    jtag_access_done = 1;
                    //printf("jtag_access: jtag_goto_run_test_idle\n");
                end
            end
        endcase
        return jtag_tdo_all;
        
        //tmp printf("jtag access: inst %x\n", inst);
        //tmp printf("jtag access: wdata %lx\n", wdata);
        //tmp printf("jtag acess: rdata %lx\n", rdata);
    
        //tmp return rdata;
    
    endfunction
    
    function bit[31:0] jtag_dtmcs_read();
        return jtag_access(8'h10);
    endfunction
    
    function bit[63:0] jtag_dmi_write(bit[63:0] wdata);
        return jtag_access(8'h11, 41, wdata);
    endfunction
    
    function bit[63:0] jtag_dmi_read();
        return jtag_access(8'h11, 41);
    endfunction

    function int jtag_tick (
        input reg[31:0] jtag_socket_port,
        output reg jtag_TCK,
        output reg jtag_TMS,
        output reg jtag_TDI,
        output reg jtag_TRSTn,
        input reg  jtag_TDO);
        tdo_var = jtag_TDO;
    
        case(dmi2jtag_state)
            DMI2JTAG_ST_INIT: begin
                jtag_init();
                if (jtag_access_done) begin
                    $display("jtag_init done");
                    dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
                    jtag_access_done = 0;
                end
            end
            DMI2JTAG_ST_REQ_CHECK: begin
                cur_req = get_dmi_req();
                if (cur_req != null) begin
                    if (cur_req.op == 1) begin
                        $display("dmi req read: op = %0x, addr = %x, data = %x", cur_req.op, cur_req.addr, cur_req.data);
                    end
                    else if (cur_req.op == 2) begin
                        $display("dmi req write: op = %0x, addr = %x, data = %x", cur_req.op, cur_req.addr, cur_req.data);
                    end
                    else begin
                        $display("dmi req none: op = %0x, addr = %x, data = %x", cur_req.op, cur_req.addr, cur_req.data);
                    end
                    dmi2jtag_state = DMI2JTAG_ST_REQ_READY;
                end
            end
            DMI2JTAG_ST_REQ_READY: begin
                bit[31:0] rdata;
                rdata = jtag_dtmcs_read();
                if (jtag_access_done) begin
                    int dmistat;
                    //printf("dtmcs rdata: %x\n", rdata);
                    dmistat = (rdata >> 10) & 32'h3;
                    if (dmistat == 0) begin
                        //printf("dtmcs dmistat is free for req\n");
                        dmi2jtag_state = DMI2JTAG_ST_REQ_SEND;
                    end
                    jtag_access_done = 0;
                end
            end
            DMI2JTAG_ST_REQ_SEND: begin
                bit[63:0] wdata;
    
                wdata = cur_req.op | (((cur_req.data)) << 2) | (((cur_req.addr)) << 34);
                jtag_dmi_write(wdata);
                if (jtag_access_done) begin
                    dmi2jtag_state = DMI2JTAG_ST_RESP_CHECK;
                    jtag_access_done = 0;
                end
            end
            DMI2JTAG_ST_RESP_CHECK: begin
                bit[31:0] rdata;
                bit[31:0] dmistat;
                rdata = jtag_dtmcs_read();
                if (jtag_access_done) begin
                    //printf("dtmcs rdata: %x\n", rdata);
                    dmistat = (rdata >> 10) & 32'h3;
                    if (dmistat == 0) begin
                        //printf("dtmcs dmistat is free for resp\n");
                        dmi2jtag_state = DMI2JTAG_ST_RESP_READY;
                    end
                    jtag_access_done = 0;
                end
            end
            DMI2JTAG_ST_RESP_READY: begin
                //printf("dtm is ready for resp\n");
                dmi2jtag_state = DMI2JTAG_ST_RESP_SEND;
            end
            DMI2JTAG_ST_RESP_SEND: begin
                bit[63:0] rdata;
    
                rdata = jtag_dmi_read();
                if (jtag_access_done) begin
                    bit[31:0] addr;
                    dmi_resp resp;
                    resp = new();
    
                    //resp.resp = ((rdata & 64'h3) == 0) ? 0 : 1;
                    resp.resp = rdata & 64'h3;
                    resp.data = (rdata >> 2) & 32'hffffffff;
                    addr = rdata >> 34;
                    $display("dmi resp: resp = %0x, data = %x",resp.resp, resp.data);
                    send_dmi_resp(resp);
                    dmi2jtag_state = DMI2JTAG_ST_RESP_DONE;
                    jtag_access_done = 0;
                end
            end
            DMI2JTAG_ST_RESP_DONE: begin
                dmi2jtag_state = DMI2JTAG_ST_REQ_CHECK;
                //tmp for debug
                //quit = 1;
            end
        endcase
    
        jtag_TCK = tck_var;
        jtag_TMS = tms_var;
        jtag_TDI = tdi_var;
        jtag_TRSTn = trstn_var;
    endfunction

   reg [31:0]                    tickCounterReg;
   wire [31:0]                   tickCounterNxt;
   
   assign tickCounterNxt = (tickCounterReg == 0) ? TICK_DELAY :  (tickCounterReg - 1);
   
   bit          r_reset;

   wire [31:0]  random_bits = $random;
   
   wire         #0.1 __jtag_TDO = jtag_TDO_driven ? 
                jtag_TDO_data : random_bits[0];
      
   int          __socket_port;
   bit          __jtag_TCK;
   bit          __jtag_TMS;
   bit          __jtag_TDI;
   bit          __jtag_TRSTn;
   int          __exit;

   reg          init_done_sticky;
   
   assign #0.1 jtag_TCK   = __jtag_TCK;
   assign #0.1 jtag_TMS   = __jtag_TMS;
   assign #0.1 jtag_TDI   = __jtag_TDI;
   assign #0.1 jtag_TRSTn = __jtag_TRSTn;
   
   assign #0.1 exit = __exit;

   //zqh added
   initial begin
        $value$plusargs("socket_port=%d", __socket_port);
   end


   always @(posedge clock) begin
      r_reset <= reset;
      if (reset || r_reset) begin
         __exit = 0;
         tickCounterReg <= TICK_DELAY;
         init_done_sticky <= 1'b0;
      end else begin
         init_done_sticky <= init_done | init_done_sticky;
         if (enable && init_done_sticky) begin
            tickCounterReg <= tickCounterNxt;
            if (tickCounterReg == 0) begin
               __exit = jtag_tick(
                                  __socket_port,
                                  __jtag_TCK,
                                  __jtag_TMS,
                                  __jtag_TDI,
                                  __jtag_TRSTn,
                                  __jtag_TDO);
            end
         end // if (enable && init_done_sticky)
      end // else: !if(reset || r_reset)
   end // always @ (posedge clock)

   //tmp initial begin
   //tmp     dmi_req req;
   //tmp     dmi_resp resp;

   //tmp     #10000ns;
   //tmp     req = new();
   //tmp     req.addr = 32'h12;
   //tmp     req.op = 1;
   //tmp     req_q.push_back(req);
   //tmp     $display("dmi_jtag_bfm push req");
   //tmp     wait(resp_q.size() > 0);
   //tmp     resp = resp_q.pop_front();
   //tmp     $display("dmi_jtag_bfm get resp: resp = %x, data = %x", resp.resp, resp.data);

   //tmp     req = new();
   //tmp     req.addr = 32'h16;
   //tmp     req.op = 1; req_q.push_back(req);
   //tmp     $display("dmi_jtag_bfm push req");
   //tmp     wait(resp_q.size() > 0);
   //tmp     resp = resp_q.pop_front();
   //tmp     $display("dmi_jtag_bfm get resp: resp = %x, data = %x", resp.resp, resp.data);
   //tmp end

   function void push_req(bit[31:0] op, bit[31:0] addr, bit[31:0] data);
       dmi_req req_pkt = new();
       req_pkt.op = op;
       req_pkt.addr = addr;
       req_pkt.data = data;
       //$display("dmi_jtag_bfm push req: op = %x, addr = %x, data = %x", op, addr, data);
       req_q.push_back(req_pkt);
   endfunction

   task wait_resp(output bit[31:0] resp, output bit[31:0] data);
       dmi_resp resp_pkt;
       wait(resp_q.size() > 0);
       resp_pkt = resp_q.pop_front();
       //$display("dmi_jtag_bfm get resp: resp = %x, data = %x", resp_pkt.resp, resp_pkt.data);
       resp = resp_pkt.resp;
       data = resp_pkt.data;
   endtask

endmodule
