/*---------------------------------------------------------
-----------------------------------------------------------
-----------------------------------------------------------

            TESTBENCH

-----------------------------------------------------------
-----------------------------------------------------------
---------------------------------------------------------*/


`timescale 1ns / 1ps

module Testbench;


    `include "include/UserData.h"
    `include "include/DevParam.h"

    wire S, C;
    wire [`VoltageRange] Vcc; 
    wire clock_active;

    
    wire DQ0, DQ1;
  

    wire Vpp_W_DQ2; 

    `ifdef HOLD_pin
        wire HOLD_DQ3; 
    `endif
    

    `ifdef RESET_pin
        wire RESET_DQ3; 
    `endif
    
    
    `ifdef  N25Q256A33E
    
        N25QxxxTop DUT (S, C, RESET_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, RESET_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, RESET_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);

    `elsif  N25Q256A13E
    
        N25QxxxTop DUT (S, C, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);
    
    
    `elsif N25Q256A31E
        
        N25QxxxTop DUT (S, C, RESET_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, RESET_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, RESET_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);
    
    `elsif  N25Q256A11E
    
        N25QxxxTop DUT (S, C, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);
    
    `elsif N25Q064A13E
        
        N25Qxxx DUT (S, C, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);
    
    `elsif N25Q064A11E
        
        N25Qxxx DUT (S, C, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);

    `elsif N25Q032A13E
        
        N25Qxxx DUT (S, C, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);
    
    `elsif N25Q032A11E
        
        N25Qxxx DUT (S, C, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);

    `elsif N25Q008A11E
        
        N25Qxxx DUT (S, C, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        Stimuli stim (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);

        StimTasks tasks (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);

        ClockGenerator ck_gen (clock_active, C);

      
    `endif



endmodule    
