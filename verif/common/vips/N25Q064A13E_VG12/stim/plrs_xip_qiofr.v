//-MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON-
//-MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON-
//-MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON-
//
//  N25Q064A13E
//
//  Verilog Behavioral Model
//  Version 1.2
//
//  Copyright (c) 2013 Micron Inc.
//
//-MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON-
//-MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON-
//-MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON--MICRON-


//-----------------------------
// For the N25Qxxx device
//-----------------------------

`timescale 1ns / 1ns


`include "top/StimGen_interface.h"
// the port list of current module is contained in "StimGen_interface.h" file

    defparam Testbench.DUT.memory_file = "";

    reg [15:0] regData='b1111111111111111;

    reg [addrDim-1:0] A0='h0, A1, A2='h08,B1='h003300;

    reg [15:0] R;

    integer i;

    initial begin

        if ((devName=="N25Q256A33E") ||(devName=="N25Q256A31E"))
            A1='hFFFFFA;
        else if ((devName=="N25Q032A13E") ||(devName=="N25Q032A11E"))
            A1='h3FFFFA;


        tasks.init;
        

        // dual program
        $display("\n --- Dual program");
        tasks.write_enable;
        tasks.send_command('hA2);
        `ifdef byte_4
        tasks.send_3byte_address(B1);
        `else
        tasks.send_address(B1);
        `endif
        for (i=1; i<=8; i=i+1)
            tasks.send_data_dual('hC1);
        tasks.close_comm;
        #(program_delay+100);

        // read
        $display("\n --- Read");
        tasks.send_command('h03);
        `ifdef byte_4
        tasks.send_3byte_address(B1);
        `else
        tasks.send_address(B1);
        `endif

        tasks.read(9);
        tasks.close_comm;


       
         // write volatile configuration register 
        $display("\n--- Write volatile configuration register");
        tasks.write_enable;
        tasks.send_command('h81);
        regData[6:2] = 'b01011; 
        tasks.send_data(regData[7:0]);
        tasks.close_comm;
        #(write_VCR_delay+100);  

         // read volatile configuration register 
        tasks.send_command('h85);
        tasks.read(2); 
        tasks.close_comm;
        #100;


           // write non volatile configuration register 
        $display("\n--- Write non volatile configuration register");
        tasks.write_enable;
        tasks.send_command('hB1);
        regData[6:2] = 'b01001; 
        tasks.send_data(regData[7:0]);
        tasks.send_data(regData[15:8]);
        tasks.close_comm;
//        #(write_NVCR_delay+100);  
        #200000000;
        $display("\n--- Power down");

        tasks.setVcc('d2900);
        #100;
        tasks.setVcc('d2800);
        #100;
        tasks.setVcc('d2700);
        #100;
        tasks.setVcc('d2600);
        #100;
        tasks.setVcc('d2500);
        #100;
        tasks.setVcc('d2400);
        #100;
        tasks.setVcc('d2300);
        #100;

        //R = $random(155);
        //R = $random($time);
        R = 'hf9ff;
        $display("-----------------------------------------------------");
        $display("---Forcing NVCR to %h value to simulate powerloss", R);
        $display("-----------------------------------------------------");
        force DUT.NonVolatileReg.NVCR = R;

        $display("\n--- Power up");
        `ifdef VCC_3V
        tasks.setVcc('d3000);
        `else
         tasks.setVcc('d1800);
        `endif
        #full_access_power_up_delay;
        
        release DUT.NonVolatileReg.NVCR;

        tasks.send_power_loss_rescue_sequence_part1_quad(); //let's give one less clock cycle
        tasks.close_comm;
        #10;
        tasks.send_power_loss_rescue_sequence_part1_dual();
        tasks.close_comm;
        #50;
        tasks.send_power_loss_rescue_sequence_part1_extended();
        tasks.close_comm;
        #50;
        tasks.send_power_loss_rescue_sequence_part2();
        tasks.close_comm;
        #100
        #200000000;
         // read non volatile configuration register 
         $display("\n--- Read non volatile configuration register @ %0t",$time);
        tasks.send_command('hB5);
        tasks.read(2); 
        tasks.close_comm;
        #100;

           // write non volatile configuration register 
        $display("\n--- Write non volatile configuration register");
        tasks.write_enable;
        tasks.send_command('hB1);
        regData[6:2] = 'b01011; 
        tasks.send_data(regData[7:0]);
        tasks.send_data(regData[15:8]);
        tasks.close_comm;
        #(write_NVCR_delay+100);  

         // read non volatile configuration register 
         $display("\n--- Read non volatile configuration register @ %0t ",$time);
        tasks.send_command('hB5);
        tasks.read(2); 
        tasks.close_comm;
        #100;

         // write volatile configuration register 
        $display("\n--- Write volatile configuration register");
        tasks.write_enable;
        tasks.send_command('h81);
        regData[6:2] = 'b01011; 
        tasks.send_data(regData[7:0]);
        tasks.close_comm;
        #(write_VCR_delay+100);  

         // read volatile configuration register 
        tasks.send_command('h85);
        tasks.read(2); 
        tasks.close_comm;
        #100;
//        $display("\n--- Power down");
//
//        tasks.setVcc('d2900);
//        #100;
//        tasks.setVcc('d2800);
//        #100;
//        tasks.setVcc('d2700);
//        #100;
//        tasks.setVcc('d2600);
//        #100;
//        tasks.setVcc('d2500);
//        #100;
//        tasks.setVcc('d2400);
//        #100;
//        tasks.setVcc('d2300);
//        #100;
//
//         // read non volatile configuration register 
//         $display("\n--- Read non volatile configuration register @ %0t ",$time);
//        tasks.send_command('hB5);
//        tasks.read(2); 
//        tasks.close_comm;
//        #100;
//
//        $display("\n--- Power up");
//        `ifdef VCC_3V
//        tasks.setVcc('d3000);
//        `else
//         tasks.setVcc('d1800);
//        `endif
//        #full_access_power_up_delay;
//
//         // read non volatile configuration register 
//         $display("\n--- Read non volatile configuration register @ %0t ",$time);
//        tasks.send_command('hB5);
//        tasks.read(2); 
//        tasks.close_comm;
//        #100;
//
//           // write non volatile configuration register 
//        $display("\n--- Write non volatile configuration register");
//        tasks.write_enable;
//        tasks.send_command('hB1);
//        regData[6:2] = 'b01001; 
//        tasks.send_data(regData[7:0]);
//        tasks.send_data(regData[15:8]);
//        tasks.close_comm;
//        #(write_NVCR_delay+100);  
//
//         // read non volatile configuration register 
//         $display("\n--- Read non volatile configuration register @ %0t ",$time);
//        tasks.send_command('hB5);
//        tasks.read(2); 
//        tasks.close_comm;
//        #100;

    end  


    endmodule






