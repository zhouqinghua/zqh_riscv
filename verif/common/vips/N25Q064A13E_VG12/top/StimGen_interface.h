

module SetConfig();
    `include "include/UserData.h"
    `include "include/DevParam.h"

endmodule

`ifdef HOLD_pin
  module Stimuli (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);
`else
  module Stimuli (S, RESET_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2);
`endif
    `include "include/DevParam.h"
   
   
    output S;
    output [`VoltageRange] Vcc;

    inout DQ0, DQ1; 

    inout Vpp_W_DQ2;

    `ifdef HOLD_pin
        inout HOLD_DQ3; 
    `endif
    

    `ifdef RESET_pin
       inout RESET_DQ3;
    `endif
   
   
