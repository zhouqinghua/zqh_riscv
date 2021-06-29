


/*-------------------------------------------------------------------------
-- The procedures here following may be used to send
-- commands to the serial flash.
-- These procedures must be combined using one of the following sequences:
--  
-- 1) send_command / close_comm 
-- 2) send_command / send_address / close_comm
-- 3) send_command / send_address / send_data /close_comm
-- 4) send_command / send_address / read / close_comm
-- 5) send_command / read / close_comm
-- NOT ALL TASKS HAVE DTR ADDED
-------------------------------------------------------------------------*/

`timescale 1ns / 1ns

module StimTasksConfig();
    `include "include/UserData.h"
    `include "include/DevParam.h"

endmodule


`ifdef HOLD_pin
  module StimTasks (S, HOLD_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);
`else
  module StimTasks (S, RESET_DQ3, DQ0, DQ1, Vcc, Vpp_W_DQ2, clock_active);
`endif

`include "include/DevParam.h"

    output S;
    reg S;
    
    output [`VoltageRange] Vcc;
    reg [`VoltageRange] Vcc;

    output clock_active;
    reg clock_active;

    
    output DQ0, DQ1; 
    reg DQ0='bZ; reg DQ1='bZ; 
    
    output Vpp_W_DQ2;
    reg Vpp_W_DQ2;

    
    `ifdef HOLD_pin
        output HOLD_DQ3; reg HOLD_DQ3; 
    `endif
    
    `ifdef RESET_pin
        output RESET_DQ3; reg RESET_DQ3; 
    `endif


    reg DoubleTransferRate = 0;
    reg double_command = 0;
    reg dummy_bytes_sent = 0;
    reg [7:0] sampled_read_byte; // local variable that samples output pins for data byte
    reg four_byte_address_mode = 0;
    reg four_4byte_address_mode = 0; // added the register to check for exclusive 4 byte address commands
    wire [3:0] num_addr_bytes;    
    assign num_addr_bytes = ((four_byte_address_mode || four_4byte_address_mode) ? 4 : 3); // appended the 4 byte address mode for checking the number of bytes


        



    //-----------------
    // Initialization
    //-----------------


    task init;
    begin
        
        S = 1;
        `ifdef HOLD_pin
          HOLD_DQ3 = 1; 
        `endif
        `ifdef RESET_pin
          RESET_DQ3 = 1;
        `endif
        power_up;

    end
    endtask



    task power_up;
    begin

    `ifdef VCC_3V
        Vcc='d3000;
    `else
        Vcc='d1800;
    `endif    
        Vpp_W_DQ2=1;
        #(full_access_power_up_delay+100);

    end
    endtask

    //----------------------------------------------------------
    // Tasks for send commands, send adressses, and read memory
    //----------------------------------------------------------


    task send_command;

    input [cmdDim-1:0] cmd;
    
    integer i;
    
    begin

        if (cmd == 'h27 || cmd == 'hFF || cmd == 'hFE)
           double_command = 1;
  
        //$display("doubeltransferrate is : %b", DoubleTransferRate);
	if (DoubleTransferRate) begin
          clock_active = 1;  #(T/4);
          S=0; #(T/2); 
        
          for (i=cmdDim-1; i>=1; i=i-1) begin
            DQ0=cmd[i]; #(T/2);
          end

          DQ0=cmd[0]; #(T/2); 
	end else begin // single transfer rate
         if(! double_command) begin      
           clock_active = 1;  #(T/4);
           S=0;
         end
         #(T/4); 
         double_command = 0;
        
         for (i=cmdDim-1; i>=1; i=i-1) begin
            DQ0=cmd[i]; #T;
         end
        
         DQ0=cmd[0]; #(T/2+T/4); 
	end

    end
    endtask



   task send_command_dual;

    input [cmdDim-1:0] cmd;
    
    integer i;
    
    begin

	if (DoubleTransferRate) begin
        clock_active = 1;  #(T/4);
        S=0; #(T/2); 
        for (i=cmdDim-1; i>=3; i=i-2) begin
             DQ1=cmd[i]; 
             DQ0=cmd[i-1];
             #(T/2);
        end
        DQ1 =cmd[1];
        DQ0=cmd[0]; #(T/2); 
        DQ1=1'bZ;
	end else begin // single transfer rate
        clock_active = 1;  #(T/4);
        S=0; #(T/4); 
        

        for (i=cmdDim-1; i>=3; i=i-2) begin
             DQ1=cmd[i]; 
             DQ0=cmd[i-1];
             #T;
        end
        DQ1 =cmd[1];
        DQ0=cmd[0]; #(T/2+T/4); 
        DQ1=1'bZ;
	end

    end
    endtask


    task send_command_quad;

    input [cmdDim-1:0] cmd;
    
    integer i;
    
    begin

	if (DoubleTransferRate) begin
        clock_active = 1;  #(T/4);
        S=0; #(T/2); 

        for (i=cmdDim-1; i>=7; i=i-4) begin

            `ifdef HOLD_pin
             HOLD_DQ3=cmd[i];
             `endif
             `ifdef RESET_pin
              RESET_DQ3 = 1;
             `endif

             Vpp_W_DQ2=cmd[i-1];
             DQ1=cmd[i-2]; 
             DQ0=cmd[i-3];
             #(T/2);
        end    
            `ifdef HOLD_pin
             HOLD_DQ3=cmd[i];
            `endif
            `ifdef RESET_pin
              RESET_DQ3 =cmd[i];
            `endif

            Vpp_W_DQ2=cmd[i-1];
            DQ1=cmd[i-2]; 
            DQ0=cmd[i-3]; #(T/2);
         
           `ifdef HOLD_pin
            HOLD_DQ3=1'bZ;
           `endif
           `ifdef RESET_pin 
            RESET_DQ3 = 1'bZ;

           `endif
           Vpp_W_DQ2=1'bZ;
           DQ1=1'bZ;
	end else begin // single transfer rate
        clock_active = 1;  #(T/4);
        S=0; #(T/4); 
        

        for (i=cmdDim-1; i>=7; i=i-4) begin
        
            `ifdef HOLD_pin
             HOLD_DQ3=cmd[i];
             `endif

            `ifdef RESET_pin
             RESET_DQ3=cmd[i];
            `endif
             
             Vpp_W_DQ2=cmd[i-1];
             DQ1=cmd[i-2]; 
             DQ0=cmd[i-3];
            #T;
        end   
        
           `ifdef HOLD_pin
            HOLD_DQ3=cmd[i];
           `endif

           `ifdef RESET_pin
            RESET_DQ3=cmd[i];
           `endif
           
            Vpp_W_DQ2=cmd[i-1];
            DQ1=cmd[i-2]; 
            DQ0=cmd[i-3]; #(T/2+T/4);
           
           `ifdef HOLD_pin
            HOLD_DQ3=1'bZ;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=1'bZ;
           `endif
           
            Vpp_W_DQ2=1'bZ;
            DQ1=1'bZ;
       end



   end
 endtask


`ifdef byte_4
    task send_3byte_address;



    input [addrDim-1 : 0] addr;

    integer i;
    
    begin
        if (DoubleTransferRate) begin
          for (i=8*num_addr_bytes-1; i>=1; i=i-1) begin
            DQ0 = (i > addrDim-1 ? 1'b0 : addr[i]); #(T/2);
          end

          DQ0 = addr[0];  #(T/2);
        end else begin // single transfer rate

          #(T/4);
          for (i=8*num_addr_bytes-1; i>=1; i=i-1) begin
            DQ0 = (i > addrDim-1 ? 1'b0 : addr[i]); #T;
          end    

          DQ0 = addr[0];  #(T/2+T/4);
          DQ0=1'bZ; 
        end

    end
    endtask 

    task send_3byte_address_;

    input [addrDimLatch4-1 : 0] addr;

    integer i;
    
    begin
        if (DoubleTransferRate) begin
          for (i=8*num_addr_bytes-1; i>=1; i=i-1) begin
            DQ0 = (i > addrDim-1 ? 1'b0 : addr[i]); #(T/2);
          end

          DQ0 = addr[0];  #(T/2);
        end else begin // single transfer rate

          #(T/4);
          for (i=8*num_addr_bytes-1; i>=1; i=i-1) begin
            //DQ0 = (i > addrDim-1 ? 1'b0 : addr[i]); #T;
            DQ0 =  addr[i]; #T;
          end    

          DQ0 = addr[0];  #(T/2+T/4);
          DQ0=1'bZ; 
        end

    end
    endtask 


    task XIP_send_3byte_address;


      input [addrDim-1 : 0] addr;


      integer i;
    
    begin
        if (DoubleTransferRate) begin
          clock_active = 1;  #(T/4);
          S=0;
          #(T/2);
          for (i=8*num_addr_bytes-1; i>=1; i=i-1) begin
            DQ0 = (i > addrDim-1 ? 1'b0 : addr[i]); #(T/2);
          end

          DQ0 = addr[0];  #(T/2);
          DQ0=1'bZ;
        end else begin // single transfer rate
          clock_active = 1;  #(T/4);
          S=0;  
          #(T/4);
          for (i=8*num_addr_bytes-1; i>=1; i=i-1) begin
            DQ0 = (i > addrDim-1 ? 1'b0 : addr[i]); #T;
          end    

          DQ0 = addr[0];  #(T/2+T/4);
          DQ0=1'bZ;
        end

    end
    endtask 


  task send_3byte_address_dual;



    input [addrDim-1 : 0] addr;
 

    integer i;
    
    begin

        if (DoubleTransferRate) begin
          #(T/2);
          for (i=8*num_addr_bytes-1; i>=3; i=i-2) begin
            DQ1 = (i > addrDim-1 ? 1'b0 : addr[i]);
            DQ0 = (i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            #(T/2);
          end
          DQ1 = addr[1];
          DQ0 = addr[0];  #(T/2);
          DQ1=1'bZ;
          DQ0=1'bZ;
        end else begin // single transfer rate

          #(T/4);
          for (i=8*num_addr_bytes-1; i>=3; i=i-2) begin
            DQ1 = (i > addrDim-1 ? 1'b0 : addr[i]);
            DQ0 = (i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            #T;
          end    
          DQ1 = addr[1];
          DQ0 = addr[0];  #(T/2+T/4);
          DQ1=1'bZ;
          DQ0=1'bZ;
        end

    end
    endtask 

    task XIP_send_3byte_address_dual;


    input [addrDim-1 : 0] addr;


    integer i;
    
    begin
    
        if (DoubleTransferRate) begin
          clock_active = 1;  #(T/4);
          S=0;
          #(T/2);

          for (i=8*num_addr_bytes-1; i>=3; i=i-2) begin
            DQ1 = (i > addrDim-1 ? 1'b0 : addr[i]);
            DQ0 = (i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            #(T/2);
          end
          DQ1 = addr[1];
          DQ0 = addr[0];  #(T/2);
          DQ1=1'bZ;
          DQ0=1'bZ;
        end else begin // single transfer rate

          clock_active = 1;  #(T/4);
          S=0;
          #(T/4);
          for (i=8*num_addr_bytes-1; i>=3; i=i-2) begin
            DQ1 = (i > addrDim-1 ? 1'b0 : addr[i]);
            DQ0 = (i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            #T;
          end 
          DQ1 = addr[1];
          DQ0 = addr[0];  #(T/2+T/4);
          DQ1=1'bZ;
          DQ0=1'bZ;
        end 

    end
    endtask 

    task send_3byte_address_quad;


    input [addrDim-1 : 0] addr;
 

    integer i;
    
    begin

       if (DoubleTransferRate) begin
         for (i=8*num_addr_bytes-1; i>=7; i=i-4) begin
            `ifdef HOLD_pin
            HOLD_DQ3= (i > addrDim-1 ? 1'b0 : addr[i]);
            `endif
            `ifdef RESET_pin
            RESET_DQ3= (i > addrDim-1 ? 1'b0 : addr[i]);
            `endif
            Vpp_W_DQ2= (i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            DQ1 = (i-2 > addrDim-1 ? 1'b0 : addr[i-2]);
            DQ0 = (i-3 > addrDim-1 ? 1'b0 : addr[i-3]);
            #(T/2);
          end
            `ifdef HOLD_pin
            HOLD_DQ3=addr[3];
            `endif
            `ifdef RESET_pin
            RESET_DQ3=addr[3];
            `endif

            Vpp_W_DQ2=addr[2];
            DQ1 = addr[1];
            DQ0 = addr[0]; #(T/2);

         `ifdef HOLD_pin
           HOLD_DQ3=1'bZ;
         `endif
         `ifdef RESET_pin
           RESET_DQ3=1'bZ;
         `endif

          Vpp_W_DQ2=1'bZ;
          DQ1=1'bZ;
          DQ0=1'bZ;
        end else begin // single transfer rate

        #(T/4);
        for (i=8*num_addr_bytes-1; i>=7; i=i-4) begin
           `ifdef HOLD_pin
            HOLD_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
           `endif
           
           `ifdef RESET_pin
            RESET_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
           `endif
           

            Vpp_W_DQ2=(i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            DQ1 = (i-2 > addrDim-1 ? 1'b0 : addr[i-2]);
            DQ0 = (i-3 > addrDim-1 ? 1'b0 : addr[i-3]);
            #T;
            
        end 
        
           `ifdef HOLD_pin
            HOLD_DQ3=addr[i];
           `endif
           
           `ifdef RESET_pin
            RESET_DQ3=addr[i];
           `endif
           

            Vpp_W_DQ2=addr[i-1];
            DQ1 = addr[i-2];
            DQ0 = addr[i-3]; #(T/2+T/4);
            
           `ifdef HOLD_pin    
            HOLD_DQ3=1'bZ;
           `endif
            
           `ifdef RESET_pin
            RESET_DQ3=1'bZ;
           `endif

            Vpp_W_DQ2=1'bZ;
            DQ1=1'bZ;
            DQ0=1'bZ;
         end 

    end
    endtask 


    task XIP_send_3byte_address_quad;


    input [addrDim-1 : 0] addr;

    integer i;
    
    begin
        
        if (DoubleTransferRate) begin
          clock_active = 1;  #(T/4);
          S=0;
          #(T/2);
          for (i=8*num_addr_bytes-1; i>=7; i=i-4) begin
           `ifdef HOLD_pin
            HOLD_DQ3= (i > addrDim-1 ? 1'b0 : addr[i]);
            `endif
            `ifdef RESET_pin
            RESET_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
            `endif
            Vpp_W_DQ2=(i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            DQ1 =  (i-2 > addrDim-1 ? 1'b0 : addr[i-2]);
            DQ0 =  (i-3 > addrDim-1 ? 1'b0 : addr[i-3]);
            #(T/2);
          end

            `ifdef HOLD_pin
            HOLD_DQ3=addr[3];
            `endif
            `ifdef RESET_pin
            RESET_DQ3=addr[3];
            `endif
            Vpp_W_DQ2=addr[2];
            DQ1 = addr[1];
            DQ0 = addr[0]; #(T/2);

           `ifdef HOLD_pin
          HOLD_DQ3=1'bZ;
          `endif
          `ifdef RESET_pin
            RESET_DQ3=1'bZ;
          `endif
  
          Vpp_W_DQ2=1'bZ;
          DQ1=1'bZ;
        end else begin // single transfer rate

          clock_active = 1;  #(T/4);
          S=0;
          #(T/4);
        for (i=8*num_addr_bytes-1; i>=7; i=i-4) begin

           `ifdef HOLD_pin 
            HOLD_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
           `endif
         
           `ifdef RESET_pin
            RESET_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
           `endif

            Vpp_W_DQ2=(i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            DQ1 = (i-2 > addrDim-1 ? 1'b0 : addr[i-2]);
            DQ0 = (i-3 > addrDim-1 ? 1'b0 : addr[i-3]);
            #T;
         end 
           `ifdef HOLD_pin 
            HOLD_DQ3=addr[i];
           `endif
           
           `ifdef RESET_pin
            RESET_DQ3=addr[i];
           `endif

            Vpp_W_DQ2=addr[i-1];
            DQ1 = addr[i-2];
            DQ0 = addr[i-3]; #(T/2+T/4);
            
           `ifdef HOLD_pin   
            HOLD_DQ3=1'bZ;
           `endif
           
           `ifdef RESET_pin
             RESET_DQ3=1'bZ;
           `endif
           
            Vpp_W_DQ2=1'bZ;
            DQ1=1'bZ;
            DQ0=1'bZ;
       end
        

    end
    endtask 

 
 //

 task send_4byte_address;

    input [addrDim-1 : 0] addr4;



    integer i;
    
    begin

        #(T/4);

       
        // first MSB bits are don't care
       `ifdef N25Q256A33E

        DQ0=0; #T; DQ0=0;#T; DQ0=0; #T; DQ0=0; #T; DQ0=0;#T; DQ0=0; #T; DQ0=0; #T;
     
       `endif

       `ifdef N25Q256A31E

        DQ0=0; #T; DQ0=0;#T; DQ0=0; #T; DQ0=0; #T; DQ0=0;#T; DQ0=0; #T; DQ0=0; #T;
     
       `endif 

        for (i=addrDim-1; i>=1; i=i-1) begin

            DQ0 = addr4[i]; #T;
        end    

        DQ0 = addr4[0];  #(T/2+T/4);
        DQ0=1'bZ;

    end
    endtask 


    task XIP_send_4byte_address;

    input [addrDim-1 : 0] addr;


      integer i;
    
    begin
        
        clock_active = 1;  #(T/4);
        S=0;  
        #(T/4);


          // first MSB bits are don't care
       `ifdef N25Q256A33E

         DQ0=0; #T; DQ0=0;#T; DQ0=0; #T; DQ0=0; #T; DQ0=0;#T; DQ0=0; #T; DQ0=0; #T;
         
     
       `endif 
        
        `ifdef N25Q256A31E

         DQ0=0; #T; DQ0=0;#T; DQ0=0; #T; DQ0=0; #T; DQ0=0;#T; DQ0=0; #T; DQ0=0; #T;
         
     
       `endif 
        for (i=addrDim-1; i>=1; i=i-1) begin

            DQ0 = addr[i]; #T;
      
      end    

        DQ0 = addr[0];  #(T/2+T/4);
        DQ0=1'bZ;

    end
    endtask 


  task send_4byte_address_dual;

    input [addrDim-1 : 0] addr4;


    integer i;
    
    begin

        #(T/4);
        
        //verificare
        `ifdef N25Q256A33E  

        DQ1=0; DQ0=0;  #T; DQ1=0; DQ0=0; #T; DQ1=0;  DQ0=0; #T; DQ1=0; DQ0=addr4[addrDim-1]; #T;

     
       `endif 

        `ifdef N25Q256A31E  

        DQ1=0; DQ0=0;  #T; DQ1=0; DQ0=0; #T; DQ1=0;  DQ0=0; #T; DQ1=0; DQ0=addr4[addrDim-1]; #T;

     
       `endif 

       

        for (i=addrDim-2; i>=3; i=i-2) begin

            DQ1 = addr4[i];

            DQ0 = addr4[i-1];

            #T;
        end    
        
        DQ1 = addr4[1];

        DQ0 = addr4[0];  #(T/2+T/4);

        DQ1=1'bZ;
        DQ0=1'bZ;
        

    end
    endtask 

    task XIP_send_4byte_address_dual;

    input [addrDim-1 : 0] addr4;


    integer i;
    
    begin
    
        clock_active = 1;  #(T/4);
        S=0;
        #(T/4);
        
         //verificare
        `ifdef N25Q256A33E  

         DQ1=0; DQ0=0;  #T; DQ1=0; DQ0=0; #T; DQ1=0;  DQ0=0; #T; DQ1=0; DQ0=addr4[addrDim-1]; #T;

                   
        `endif 
         
         `ifdef N25Q256A31E  

         DQ1=0; DQ0=0;  #T; DQ1=0; DQ0=0; #T; DQ1=0;  DQ0=0; #T; DQ1=0; DQ0=addr4[addrDim-1]; #T;

                   
        `endif

        for (i=addrDim-2; i>=3; i=i-2) begin
        
            DQ1 = addr4[i];
            DQ0 = addr4[i-1];
            #T;
            
        end 
        
        DQ1 = addr4[1];
        DQ0 = addr4[0];  #(T/2+T/4);
        DQ1=1'bZ;
        DQ0=1'bZ;
        

    end
    endtask 

    task send_4byte_address_quad;

    input [addrDim-1 : 0] addr4;
 

    integer i;
    
    begin

        #(T/4);
    
        `ifdef N25Q256A33E  

          `ifdef HOLD_pin
            HOLD_DQ3=0;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=0;
           `endif

            Vpp_W_DQ2=0;
            
             DQ1=0;
             
             
             DQ0=0;
             
             #T; 

             `ifdef HOLD_pin
            HOLD_DQ3=0;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=0;
           `endif

            Vpp_W_DQ2=0;
            
             DQ1=0;
             
             
             DQ0=addr4[addrDim-1];

             #T;


        `endif


        `ifdef N25Q256A31E  

          `ifdef HOLD_pin
            HOLD_DQ3=0;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=0;
           `endif

            Vpp_W_DQ2=0;
            
             DQ1=0;
             
             
             DQ0=0;
             
             #T; 

             `ifdef HOLD_pin
            HOLD_DQ3=0;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=0;
           `endif

            Vpp_W_DQ2=0;
            
             DQ1=0;
             
             
             DQ0=addr4[addrDim-1];

             #T;


        `endif


        for (i=addrDim-2; i>=7; i=i-4) begin

           `ifdef HOLD_pin
            HOLD_DQ3=addr4[i];
           `endif
           
           `ifdef RESET_pin
            RESET_DQ3=addr4[i];
           `endif
           

            Vpp_W_DQ2=addr4[i-1];
            DQ1 = addr4[i-2];
            DQ0 = addr4[i-3];
            #T;
            
        end 
        
           `ifdef HOLD_pin
            HOLD_DQ3=addr4[i];
           `endif
           
           `ifdef RESET_pin
            RESET_DQ3=addr4[i];
           `endif
           

            Vpp_W_DQ2=addr4[i-1];
            DQ1 = addr4[i-2];
            DQ0 = addr4[i-3]; #(T/2+T/4);
            
           `ifdef HOLD_pin    
            HOLD_DQ3=1'bZ;
           `endif
            
           `ifdef RESET_pin
            RESET_DQ3=1'bZ;
           `endif

            Vpp_W_DQ2=1'bZ;
            DQ1=1'bZ;
            DQ0=1'bZ;
        

    end
    endtask 


    task XIP_send_4byte_address_quad;

    input [addrDim-1 : 0] addr4;

    integer i;
    
    begin
        
        clock_active = 1;  #(T/4);
        S=0;
        #(T/4);
        
        `ifdef N25Q256A33E  

          `ifdef HOLD_pin
            HOLD_DQ3=0;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=0;
           `endif

            Vpp_W_DQ2=0;
            
             DQ1=0;
             
             
             DQ0=0;
             
             #T; 

             `ifdef HOLD_pin
            HOLD_DQ3=0;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=0;
           `endif

            Vpp_W_DQ2=0;
            
             DQ1=0;
             
             
             DQ0=addr4[addrDim-1];

             #T;


        `endif

         `ifdef N25Q256A31E  

          `ifdef HOLD_pin
            HOLD_DQ3=0;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=0;
           `endif

            Vpp_W_DQ2=0;
            
             DQ1=0;
             
             
             DQ0=0;
             
             #T; 

             `ifdef HOLD_pin
            HOLD_DQ3=0;
           `endif

           `ifdef RESET_pin
            RESET_DQ3=0;
           `endif

            Vpp_W_DQ2=0;
            
             DQ1=0;
             
             
             DQ0=addr4[addrDim-1];

             #T;


        `endif


        
        for (i=addrDim-2; i>=7; i=i-4) begin

           `ifdef HOLD_pin 
            HOLD_DQ3=addr4[i];
           `endif
         
           `ifdef RESET_pin
            RESET_DQ3=addr4[i];
           `endif

            Vpp_W_DQ2=addr4[i-1];
            DQ1 = addr4[i-2];
            DQ0 = addr4[i-3];
            #T;
            
       end 
       
           `ifdef HOLD_pin 
            HOLD_DQ3=addr4[i];
           `endif
           
           `ifdef RESET_pin
            RESET_DQ3=addr4[i];
           `endif

            Vpp_W_DQ2=addr4[i-1];
            DQ1 = addr4[i-2];
            DQ0 = addr4[i-3]; #(T/2+T/4);
            
           `ifdef HOLD_pin   
            HOLD_DQ3=1'bZ;
           `endif
           
           `ifdef RESET_pin
             RESET_DQ3=1'bZ;
           `endif
           
            Vpp_W_DQ2=1'bZ;
            DQ1=1'bZ;
            DQ0=1'bZ;
        

    end
    endtask 

`else

    task send_address;

    input [addrDim-1 : 0] addr;

    integer i;
    
    begin
	if (DoubleTransferRate) begin
        for (i=8*num_addr_bytes-1; i>=1; i=i-1) begin
            DQ0 = (i > addrDim-1 ? 1'b0 : addr[i]); #(T/2);
        end    

        DQ0 = addr[0];  #(T/2);
	end else begin // single transfer rate

        #(T/4);


        `ifdef N25Q032A13E
          DQ0=0; #T; DQ0=0;#T;
        `endif   
        `ifdef N25Q032A11E
          DQ0=0; #T; DQ0=0;#T;
        `endif  
        `ifdef N25Q008A11E
          DQ0=0; #T; DQ0=0;#T;DQ0=0;#T;DQ0=0;#T;
        `endif  
        for (i=addrDim-1; i>=1; i=i-1) begin
            DQ0 = addr[i]; #T;
        end    

        DQ0 = addr[0];  #(T/2+T/4);
      end

    end
    endtask 


 task XIP_send_address;

    input [addrDim-1 : 0] addr;

    integer i;
    
    begin
        
	if (DoubleTransferRate) begin
        clock_active = 1;  #(T/4);
        S=0;  
        #(T/2);


        for (i=8*num_addr_bytes-1; i>=1; i=i-1) begin
            DQ0 = (i > addrDim-1 ? 1'b0 : addr[i]); #(T/2);
        end    

        DQ0 = addr[0];  #(T/2);
	end else begin // single transfer rate
        clock_active = 1;  #(T/4);
        S=0;  
        #(T/4);


         `ifdef N25Q032A13E
          DQ0=0; #T; DQ0=0;#T;
        `endif   
         `ifdef N25Q032A11E
          DQ0=0; #T; DQ0=0;#T;
        `endif 

        for (i=addrDim-1; i>=1; i=i-1) begin
            DQ0 = addr[i]; #T;
        end    

        DQ0 = addr[0];  #(T/2+T/4);

      end
    end
    endtask 


  task send_address_dual;

    input [addrDim-1 : 0] addr;

    integer i;
    
    begin
	if (DoubleTransferRate) begin
        for (i=8*num_addr_bytes-1; i>=3; i=i-2) begin
            DQ1 = (i > addrDim-1 ? 1'b0 : addr[i]);
            DQ0 = (i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            #(T/2);
        end    
        DQ1 = addr[1];
        DQ0 = addr[0];  #(T/2);
        DQ1=1'bZ;
	end else begin // single transfer rate

        #(T/4);
        
         `ifdef N25Q032A13E
          DQ1=0;DQ0=0;#T;
        `endif   
          
           `ifdef N25Q032A11E
          DQ1=0;DQ0=0;#T;
        `endif   


        for (i=addrDim-1; i>=3; i=i-2) begin
            DQ1 = addr[i];
            DQ0 = addr[i-1];
            #T;
        end    
        DQ1 = addr[1];
        DQ0 = addr[0];  #(T/2+T/4);
        DQ1=1'bZ;

      end

    end
    endtask 

    task XIP_send_address_dual;

    input [addrDim-1 : 0] addr;

    integer i;
    
    begin
	if (DoubleTransferRate) begin
        clock_active = 1;  #(T/4);
        S=0;
        #(T/2);

        for (i=8*num_addr_bytes-1; i>=3; i=i-2) begin
            DQ1 = (i > addrDim-1 ? 1'b0 : addr[i]);
            DQ0 = (i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            #(T/2);
        end    
        DQ1 = addr[1];
        DQ0 = addr[0];  #(T/2);
        DQ1=1'bZ;
	end else begin // single transfer rate
        clock_active = 1;  #(T/4);
        S=0;
        #(T/4);
        
         `ifdef N25Q032A13E
          DQ1=0;DQ0=0;#T;
        `endif
         `ifdef N25Q032A11E
          DQ1=0;DQ0=0;#T;
        `endif

        for (i=addrDim-1; i>=3; i=i-2) begin
            DQ1 = addr[i];
            DQ0 = addr[i-1];
            #T;
        end    
        DQ1 = addr[1];
        DQ0 = addr[0];  #(T/2+T/4);
        DQ1=1'bZ;

      end 

    end
    endtask 

    task send_address_quad;

    input [addrDim-1 : 0] addr;

    integer i;
    
    begin

	if (DoubleTransferRate) begin
        for (i=8*num_addr_bytes-1; i>=7; i=i-4) begin
            `ifdef HOLD_pin
            HOLD_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
            `endif
            `ifdef RESET_pin
            RESET_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
            `endif

            Vpp_W_DQ2=(i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            DQ1 = (i-2 > addrDim-1 ? 1'b0 : addr[i-2]);
            DQ0 = (i-3 > addrDim-1 ? 1'b0 : addr[i-3]);
            #(T/2);
        end 
            `ifdef HOLD_pin
            HOLD_DQ3=addr[3];
            `endif
            `ifdef RESET_pin
            RESET_DQ3=addr[3];
            `endif

            Vpp_W_DQ2=addr[2];
            DQ1 = addr[1];
            DQ0 = addr[0]; #(T/2);

        `ifdef HOLD_pin
        HOLD_DQ3=1'bZ;
        `endif

        `ifdef RESET_pin
          RESET_DQ3=1'bZ;
        `endif


        Vpp_W_DQ2=1'bZ;
        DQ1=1'bZ;
	end else begin // single transfer rate
        #(T/4);
        
        `ifdef N25Q032A13E
        
        `ifdef HOLD_pin
            HOLD_DQ3=0;
        `endif
        
        `ifdef RESET_pin
            RESET_DQ3=0;
        `endif
         Vpp_W_DQ2=0;

          DQ1=addr[addrDim-1]; 
          DQ0=addr[addrDim-2];
          #T;
        `endif
         
         `ifdef N25Q032A11E
        
        `ifdef HOLD_pin
            HOLD_DQ3=0;
        `endif
        
        `ifdef RESET_pin
            RESET_DQ3=0;
        `endif
         Vpp_W_DQ2=0;

          DQ1=addr[addrDim-1]; 
          DQ0=addr[addrDim-2];
          #T;
        `endif

        for (i=addrDim-3; i>=7; i=i-4) begin
        `ifdef HOLD_pin
            HOLD_DQ3=addr[i];
        `endif
        `ifdef RESET_pin
            RESET_DQ3=addr[i];
        `endif

         
            Vpp_W_DQ2=addr[i-1];
            DQ1 = addr[i-2];
            DQ0 = addr[i-3];
            #T;
        end  
         `ifdef HOLD_pin
            HOLD_DQ3=addr[i];
         `endif
         `ifdef RESET_pin
            RESET_DQ3=addr[i];
        `endif

            Vpp_W_DQ2=addr[i-1];
            DQ1 = addr[i-2];
            DQ0 = addr[i-3]; #(T/2+T/4);
        
        `ifdef HOLD_pin
        HOLD_DQ3=1'bZ;
        `endif
        `ifdef RESET_pin
        RESET_DQ3=1'bZ;
        `endif

        
        Vpp_W_DQ2=1'bZ;
        DQ1=1'bZ;

      end 

    end
    endtask 


    task XIP_send_address_quad;

    input [addrDim-1 : 0] addr;

    integer i;
    
    begin
        
    	if (DoubleTransferRate) begin
        clock_active = 1;  #(T/4);
        S=0;
        #(T/2);
        for (i=8*num_addr_bytes-1; i>=7; i=i-4) begin
           
           `ifdef HOLD_pin
            HOLD_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
            `endif
            `ifdef RESET_pin
            RESET_DQ3=(i > addrDim-1 ? 1'b0 : addr[i]);
            `endif
            Vpp_W_DQ2=(i-1 > addrDim-1 ? 1'b0 : addr[i-1]);
            DQ1 = (i-2 > addrDim-1 ? 1'b0 : addr[i-2]);
            DQ0 = (i-3 > addrDim-1 ? 1'b0 : addr[i-3]);
            #(T/2);
        end  
            
            `ifdef HOLD_pin
            HOLD_DQ3=addr[3];
            `endif
            `ifdef RESET_pin
            RESET_DQ3=addr[3];
            `endif
            Vpp_W_DQ2=addr[2];
            DQ1 = addr[1];
            DQ0 = addr[0]; #(T/2);
        
         `ifdef HOLD_pin
        HOLD_DQ3=1'bZ;
        `endif

        `ifdef RESET_pin
          RESET_DQ3=1'bZ;
        `endif


        Vpp_W_DQ2=1'bZ;
        DQ1=1'bZ;
	end else begin // single transfer rate
        clock_active = 1;  #(T/4);
        S=0;
        #(T/4);
         
          
        `ifdef N25Q032A13E
        
        `ifdef HOLD_pin
            HOLD_DQ3=0;
        `endif
        
        `ifdef RESET_pin
            RESET_DQ3=0;
        `endif
         Vpp_W_DQ2=0;

          DQ1=addr[addrDim-1]; 
          DQ0=addr[addrDim-2];
          #T;
        `endif
         
         `ifdef N25Q032A11E
        
        `ifdef HOLD_pin
            HOLD_DQ3=0;
        `endif
        
        `ifdef RESET_pin
            RESET_DQ3=0;
        `endif
         Vpp_W_DQ2=0;

          DQ1=addr[addrDim-1]; 
          DQ0=addr[addrDim-2];
          #T;
        `endif

        for (i=addrDim-3; i>=7; i=i-4) begin
            `ifdef HOLD_pin
            HOLD_DQ3=addr[i];
            `endif
           `ifdef RESET_pin
            RESET_DQ3=addr[i];
           `endif
            Vpp_W_DQ2=addr[i-1];
            DQ1 = addr[i-2];
            DQ0 = addr[i-3];
            #T;
        end 
        
           `ifdef HOLD_pin
            HOLD_DQ3=addr[i];
           `endif
           `ifdef RESET_pin
            RESET_DQ3=addr[i];
           `endif
            Vpp_W_DQ2=addr[i-1];
            DQ1 = addr[i-2];
            DQ0 = addr[i-3]; #(T/2+T/4);
        
        `ifdef HOLD_pin
        HOLD_DQ3=1'bZ;
        `endif
        `ifdef RESET_pin
        RESET_DQ3=1'bZ;
        `endif

        Vpp_W_DQ2=1'bZ;
        DQ1=1'bZ;

      end 

    end
    endtask 

`endif
 //

    task send_data;

    input [dataDim-1:0] data;
    
    integer i;
    
    begin

	if (DoubleTransferRate) begin
        for (i=dataDim-1; i>=1; i=i-1) begin
            DQ0=data[i]; #(T/2);
        end

        DQ0=data[0]; #(T/2); 
	end else begin // single transfer rate
        #(T/4);

        
        for (i=dataDim-1; i>=1; i=i-1) begin
            DQ0=data[i]; #T;
        end

        DQ0=data[0]; #(T/2+T/4); 
      end

    end
    endtask





    
        task send_data_dual;

        input [dataDim-1:0] data;
        
        integer i;
        
        begin

	if (DoubleTransferRate) begin
            for (i=dataDim-1; i>=3; i=i-2) begin
                DQ1=data[i]; 
                DQ0=data[i-1];
                #(T/2);
            end

            DQ1=data[1];
            DQ0=data[0]; #(T/2);
            DQ1=1'bZ;
	end else begin // single transfer rate
            #(T/4);

            
            for (i=dataDim-1; i>=3; i=i-2) begin
                DQ1=data[i]; 
                DQ0=data[i-1];
                #T;
            end

            DQ1=data[1];
            DQ0=data[0]; #(T/2+T/4);
            DQ1=1'bZ;

          end
        end
        endtask



        task send_data_quad;

        input [dataDim-1:0] data;
        
        integer i;
        
        begin

	if (DoubleTransferRate) begin
            for (i=dataDim-1; i>=7; i=i-4) begin
                
                `ifdef HOLD_pin
                HOLD_DQ3=data[i];
                `endif
                `ifdef RESET_pin
                RESET_DQ3=data[i];
                `endif
                Vpp_W_DQ2=data[i-1];
                DQ1=data[i-2]; 
                DQ0=data[i-3];
                #(T/2);
            end
            
            `ifdef HOLD_pin
            HOLD_DQ3=data[3];
            `endif
            `ifdef RESET_pin
            RESET_DQ3=data[3];
            `endif

            Vpp_W_DQ2=data[2];
            DQ1=data[1];
            DQ0=data[0]; #(T/2);
            
            `ifdef HOLD_pin
            HOLD_DQ3=1'bZ;
            `endif
            `ifdef RESET_pin
             RESET_DQ3=1'bZ;
            `endif
            Vpp_W_DQ2=1'bZ;
            DQ1=1'bZ;
	end else begin // single transfer rate
            #(T/4);

            
            for (i=dataDim-1; i>=7; i=i-4) begin
               `ifdef HOLD_pin
                HOLD_DQ3=data[i];
                 `endif
               `ifdef RESET_pin
                RESET_DQ3=data[i];
                `endif

                Vpp_W_DQ2=data[i-1];
                DQ1=data[i-2]; 
                DQ0=data[i-3];
                #T;
            end
            `ifdef HOLD_pin
            HOLD_DQ3=data[3];
            `endif
            `ifdef RESET_pin
            RESET_DQ3=data[3];
            `endif

            Vpp_W_DQ2=data[2];
            DQ1=data[1];
            DQ0=data[0]; #(T/2+T/4);
            `ifdef HOLD_pin
            HOLD_DQ3=1'bZ;
            `endif
            `ifdef RESET_pin
            RESET_DQ3=1'bZ;
            `endif

            Vpp_W_DQ2=1'bZ;
            DQ1=1'bZ;
          end

        end
        endtask



task send_dummy;

    input [dummyDim-1:0] data;

    input integer n;
    
    integer i;
    
    begin

	if (DoubleTransferRate) begin
        for (i=n-1; i>=1; i=i-1) begin
            DQ0=data[i]; #T;
        end

	// Unlike other DTR instr/addr/data tasks, we end in middle of high clk pulse, instead of middle of low clk pulse
	// Difference is caused by fact that in DTR, last instr/addr/data bit is latched on negedge clk, but last dummy bit is latched on posedge clk
        DQ0=data[0]; #(T/2);
	end else begin // single transfer rate
        #(T/4);

        
        for (i=n-1; i>=1; i=i-1) begin
            DQ0=data[i]; #T;
        end

        DQ0=data[0]; #(T/2+T/4); 
      end

    end
    endtask

  task send_dummy_dual;

    input [dummyDim-1:0] data;

    input integer n;
    
    integer i;
    
    begin

        #(T/4);

        
        for (i=n-1; i>=1; i=i-1) begin
            DQ1=data[i]; 
            DQ0=data[i]; #T;
        end
        
        DQ1=data[0];
        DQ0=data[0]; #(T/2+T/4); 
       
        DQ1=1'bZ;



    end
    endtask




   task send_dummy_quad;

    input [dummyDim-1:0] data;

    input integer n;

    
    integer i;
    
    begin

        #(T/4);

        
        for (i=n-1; i>=1; i=i-1) begin
           
           `ifdef HOLD_pin
             HOLD_DQ3=data[i];
           `endif
           `ifdef RESET_pin
             RESET_DQ3=data[i];
           `endif
             Vpp_W_DQ2=data[i];

             DQ1=data[i]; 
             DQ0=data[i]; #T;
        end
        
        `ifdef HOLD_pin
         HOLD_DQ3=data[0];
        `endif
        `ifdef RESET_pin
         RESET_DQ3=data[0];
        `endif
        Vpp_W_DQ2=data[0];
        DQ1=data[0];
        DQ0=data[0]; #(T/2+T/4); 
       `ifdef HOLD_pin
         HOLD_DQ3=1'bZ;
       `endif
       `ifdef RESET_pin
        RESET_DQ3=1'bZ;
       `endif

        Vpp_W_DQ2=1'bZ;
        DQ1=1'bZ;



    end
    endtask


 
    task read;

    input n;
    integer n, i, j;

   reg [7:0] temp_read_byte;
    
    fork
    begin
    for (i=1; i<=n; i=i+1) begin 
        #(8*T/(DoubleTransferRate+1)); // halved if DTR mode
    end  
    if (DoubleTransferRate && dummy_bytes_sent) #(T/2);
    end
    begin
	if (DoubleTransferRate) begin
	    #1; // task may be at nededge C already, but data output actually starts on next negedge
	    for (j=1; j<=n; j=j+1) begin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[7] = Testbench.DQ1; // use Testbench.DQ1 b/c local DQ1 only shows what task is driving (highZ)
		@(posedge ck_gen.C) #(tCHQV+1);	temp_read_byte[6] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[5] = Testbench.DQ1;
		@(posedge ck_gen.C) #(tCHQV+1);	temp_read_byte[4] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[3] = Testbench.DQ1;
		@(posedge ck_gen.C) #(tCHQV+1);	temp_read_byte[2] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[1] = Testbench.DQ1;
		@(posedge ck_gen.C) #(tCHQV+1);	temp_read_byte[0] = Testbench.DQ1;
		sampled_read_byte = temp_read_byte;
		`ifdef PRINT_ALL_DATA
		$display("SIO-DTR Read out byte at time %t is %2h", $time, sampled_read_byte);
		`endif
	    end
	end else begin // single transfer rate
	    #1; // task may be at posedge C already, but data output actually starts on next posedge
	    for (j=1; j<=n; j=j+1) begin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[7] = Testbench.DQ1; // use Testbench.DQ1 b/c local DQ1 only shows what task is driving (highZ)
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[6] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[5] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[4] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[3] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[2] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[1] = Testbench.DQ1;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[0] = Testbench.DQ1;
		sampled_read_byte = temp_read_byte;
		`ifdef PRINT_ALL_DATA
		$display("SIO Read out byte at time %t is %2h", $time, sampled_read_byte);
		`endif
	    end
	end
    end
    join

    endtask



    
    task read_dual;

    input n;
    integer n, i, j;
    reg [7:0] temp_read_byte;
    
    fork
    begin
    DQ0 = 1'bZ;
    for (i=1; i<=2*n; i=i+1) begin 
        #(4*T/(DoubleTransferRate+1)); // halved if DTR mode
    end   
    if (DoubleTransferRate && dummy_bytes_sent) #(T/2);
    end
    begin
	if (DoubleTransferRate) begin
	    #1; // task may be at nededge C already, but data output actually starts on next negedge
	    for (j=1; j<=2*n; j=j+1) begin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[7] = Testbench.DQ1; // use Testbench.DQ1 b/c local DQ1 only shows what task is driving (highZ)
						temp_read_byte[6] = Testbench.DQ0;
		@(posedge ck_gen.C) #(tCHQV+1);	temp_read_byte[5] = Testbench.DQ1;
						temp_read_byte[4] = Testbench.DQ0;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[3] = Testbench.DQ1;
						temp_read_byte[2] = Testbench.DQ0;
		@(posedge ck_gen.C) #(tCHQV+1);	temp_read_byte[1] = Testbench.DQ1;
						temp_read_byte[0] = Testbench.DQ0;
		sampled_read_byte = temp_read_byte;
		`ifdef PRINT_ALL_DATA
		$display("DIO-DTR Read out byte at time %t is %2h", $time, sampled_read_byte);
		`endif
	    end
	end else begin // single transfer rate
	    #1; // task may be at posedge C already, but data output actually starts on next posedge
	    for (j=1; j<=2*n; j=j+1) begin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[7] = Testbench.DQ1; // use Testbench.DQ1 b/c local DQ1 only shows what task is driving (highZ)
						temp_read_byte[6] = Testbench.DQ0;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[5] = Testbench.DQ1;
						temp_read_byte[4] = Testbench.DQ0;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[3] = Testbench.DQ1;
						temp_read_byte[2] = Testbench.DQ0;
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[1] = Testbench.DQ1;
						temp_read_byte[0] = Testbench.DQ0;
		sampled_read_byte = temp_read_byte;
		`ifdef PRINT_ALL_DATA
		$display("DIO Read out byte at time %t is %2h", $time, sampled_read_byte);
		`endif
	    end
	end
    end
    join
    endtask

   
   task read_quad;

    input n;
    integer n, i, j;
    reg [7:0] temp_read_byte;
    
    fork
    begin
    DQ0 = 1'bZ;
    for (i=1; i<=4*n; i=i+1) begin 
        #(2*T/(DoubleTransferRate+1)); // halved if DTR mode
    end   
    if (DoubleTransferRate && dummy_bytes_sent) #(T/2);
    end
    begin
	if (DoubleTransferRate) begin
	    #1; // task may be at nededge C already, but data output actually starts on next negedge
	    for (j=1; j<=4*n; j=j+1) begin
		`ifdef HOLD_pin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[7] = Testbench.HOLD_DQ3; // use Testbench.DQ1 b/c local DQ1 only shows what task is driving (highZ)
		`endif
		`ifdef RESET_pin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[7] = Testbench.RESET_DQ3;
		`endif
						temp_read_byte[6] = Testbench.Vpp_W_DQ2;
						temp_read_byte[5] = Testbench.DQ1;
						temp_read_byte[4] = Testbench.DQ0;
		`ifdef HOLD_pin
		@(posedge ck_gen.C) #(tCHQV+1);	temp_read_byte[3] = Testbench.HOLD_DQ3;
		`endif
		`ifdef RESET_pin
		@(posedge ck_gen.C) #(tCHQV+1);	temp_read_byte[3] = Testbench.RESET_DQ3;
		`endif
						temp_read_byte[2] = Testbench.Vpp_W_DQ2;
						temp_read_byte[1] = Testbench.DQ1;
						temp_read_byte[0] = Testbench.DQ0;
		sampled_read_byte = temp_read_byte;
		`ifdef PRINT_ALL_DATA
		$display("QIO-DTR Read out byte at time %t is %2h", $time, sampled_read_byte);
		`endif
	    end
	end else begin // single transfer rate
	    #1; // task may be at posedge C already, but data output actually starts on next posedge
	    for (j=1; j<=4*n; j=j+1) begin
		`ifdef HOLD_pin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[7] = Testbench.HOLD_DQ3; // use Testbench.DQ1 b/c local DQ1 only shows what task is driving (highZ)
		`endif
		`ifdef RESET_pin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[7] = Testbench.RESET_DQ3;
		`endif
						temp_read_byte[6] = Testbench.Vpp_W_DQ2;
						temp_read_byte[5] = Testbench.DQ1;
						temp_read_byte[4] = Testbench.DQ0;
		`ifdef HOLD_pin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[3] = Testbench.HOLD_DQ3;
		`endif
		`ifdef RESET_pin
		@(negedge ck_gen.C) #(tCLQV+1);	temp_read_byte[3] = Testbench.RESET_DQ3;
		`endif
						temp_read_byte[2] = Testbench.Vpp_W_DQ2;
						temp_read_byte[1] = Testbench.DQ1;
						temp_read_byte[0] = Testbench.DQ0;
		sampled_read_byte = temp_read_byte;
		`ifdef PRINT_ALL_DATA
		$display("QIO Read out byte at time %t is %2h", $time, sampled_read_byte);
		`endif
	    end
	end
    end
    join

    endtask




    // shall be used in a sequence including send command
    // and close communication tasks
    
    task add_clock_cycle;

    input integer n;
    integer i;

        for(i=1; i<=n; i=i+1) #T;

    endtask







    task close_comm;

    begin
        S = 1;
        clock_active = 0;
        # T;
        # 100;

    end
    endtask





    //------------------
    // others tasks
    //------------------


    `ifdef HOLD_pin
    task set_HOLD;
    input value;
        HOLD_DQ3 = value;
    endtask
    `endif


    task set_clock;
    input value;
        clock_active = value;
    endtask 


    task set_S;
    input value;
        S = value;
    endtask
    

    task setVcc;
    input [`VoltageRange] value;
        Vcc = value;
    endtask


    task Vcc_waveform;
    input [`VoltageRange] V1; input time t1;
    input [`VoltageRange] V2; input time t2;
    input [`VoltageRange] V3; input time t3;
    begin
      Vcc=V1; #t1;
      Vcc=V2; #t2;
      Vcc=V3; #t3;
    end
    endtask



    task set_Vpp_W;
    input value;
        Vpp_W_DQ2 = value;
    endtask



    `ifdef RESET_pin
    
    task set_RESET;
    input value;
        RESET_DQ3 = value;
    endtask

    task RESET_pulse;
    begin
        RESET_DQ3 = 0;
        #100;
        RESET_DQ3 = 1;
    end
    endtask
    
    `endif
    

    task dtr_mode_select;
    input on_off;
        DoubleTransferRate = on_off;
    endtask



    task addr_4byte_select;
    input on_off;
        four_byte_address_mode = on_off;
    endtask



    //------------------------------------------
    // Tasks to send complete command sequences
    //------------------------------------------


    task write_enable;
    begin
        send_command('h06); //write enable
        close_comm;
        #100;
    end  
    endtask

    task write_enable_dual;
    begin
        send_command_dual('h06); //write enable
        close_comm;
        #100;
    end  
    endtask

    task write_enable_quad;
    begin
        send_command_quad('h06); //write enable
        close_comm;
        #100;
    end  
    endtask

`ifdef byte_4
    task unlock_sector_3byte_address;

    input [addrDim-2:0] A;

    begin
        // write lock register (to unlock sector to be programmed)
        tasks.write_enable;
        tasks.send_command('hE5);
        tasks.send_3byte_address(A);
        tasks.send_data('h00);
        tasks.close_comm;
        #100;
    end 
    endtask

     task unlock_sector_dual_3byte_address;

    input [addrDim-2:0] A;
    begin
        // write lock register (to unlock sector to be programmed)
        tasks.write_enable_dual;
        tasks.send_command_dual('hE5);
        tasks.send_3byte_address_dual(A);
        tasks.send_data_dual('h00);
        tasks.close_comm;
        #100;
    end 
    endtask

     task unlock_sector_quad_3byte_address;

     input [addrDim-2:0] A; 
    begin
        // write lock register (to unlock sector to be programmed)
        tasks.write_enable_quad;
        tasks.send_command_quad('hE5);
        tasks.send_3byte_address_quad(A);
        tasks.send_data_quad('h00);
        tasks.close_comm;
        #100;
    end 
    endtask
`else

      task unlock_sector;
    input [addrDim-1:0] A;
    begin
        // write lock register (to unlock sector to be programmed)
        tasks.write_enable;
        tasks.send_command('hE5);
        tasks.send_address(A);
        tasks.send_data('h00);
        tasks.close_comm;
        #100;
    end 
    endtask

     task unlock_sector_dual;
    input [addrDim-1:0] A;
    begin
        // write lock register (to unlock sector to be programmed)
        tasks.write_enable_dual;
        tasks.send_command_dual('hE5);
        tasks.send_address_dual(A);
        tasks.send_data_dual('h00);
        tasks.close_comm;
        #100;
    end 
    endtask

     task unlock_sector_quad;
    input [addrDim-1:0] A;
    begin
        // write lock register (to unlock sector to be programmed)
        tasks.write_enable_quad;
        tasks.send_command_quad('hE5);
        tasks.send_address_quad(A);
        tasks.send_data_quad('h00);
        tasks.close_comm;
        #100;
    end 
    endtask


`endif

endmodule    

