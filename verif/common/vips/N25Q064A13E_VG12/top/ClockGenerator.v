    
    
//--------------------------------------------------------------------------------
// This module generates the clock signal.
// The module is driven by "clock_active" signal, coming from "StimTasks" module.
// 
// (NB: Tasks of StimTasks module are invoked in "Stimuli" module).
//--------------------------------------------------------------------------------
`timescale 1ns / 1ns
    
    
module ClockGenerator (clock_active, C);

`include "include/UserData.h"
`include "include/DevParam.h"

input clock_active;
output C;
reg C;
   
   
    always begin : clock_generator

        if (clock_active) begin
            C = 1; #(T/2);
            C = 0; #(T/2);
        end else begin
            C = 0;
            @ clock_active;
        end

    end



endmodule    
