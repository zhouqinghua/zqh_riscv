//`timescale 1ns/1ps
module zqh_riscv_sanity_test();
    zqh_vbase_log log;
    string name = "zqh_riscv_sanity_test";

    task run_test();
        log = new(name);
        $display("run_test: %s", name);

        while(test_master.env.m_run_state == 0) begin
            @(posedge `ZQH_TOP.clock);
        end
        //wait(test_master.env.m_run_state != 0);

        //wfi
        //tmp repeat(27000) @(posedge `ZQH_TOP.clock);
        //tmp //`zqh_vbase_note(log, "zqh test log");
        //tmp `zqh_vbase_note(log, $display("force interrupt for wfi"));
        //tmp force `ZQH_DUT.io_interrupts_int[0] = 1;
        //tmp repeat(10) @(posedge `ZQH_TOP.clock);
        //tmp `zqh_vbase_note(log, $display("release interrupt for wfi"));
        //tmp release `ZQH_DUT.io_interrupts_int[0];
        //tmp `zqh_vbase_note(log, $display("test %s finished", name));

        //
        //debug interrupt
        //tmp repeat(27000) @(posedge `ZQH_TOP.clock);
        //tmp force `ZQH_CORE_WRAP(0).io_interrupts_debug = 1;
        //tmp repeat(10) @(posedge `ZQH_TOP.clock);
        //tmp release`ZQH_CORE_WRAP(0).io_interrupts_debug;

        //
        //spi flash jtag download
        repeat(10000) @(posedge `ZQH_TOP.clock);

        begin
            string bootloader_flash_file;
            int fd;
            int code;
            string line;
            int address_found;
            bit[31:0] address;
            bit[7:0] data_byte;

            bit[31:0] req_op;
            bit[31:0] req_addr;
            bit[31:0] req_data;
            bit[31:0] resp_resp;
            bit[31:0] resp_data;

            bit[31:0] jedec_id;
            bit[63:0] unique_id;

            bootloader_flash_file = `FILENAME_mem;
            fd = $fopen(bootloader_flash_file, "r");
            if (fd == 0) begin
                $display("%s could not open", bootloader_flash_file);
                $finish();
            end
            `ZQH_TOP.spi0_norflash_read_jedec_id(jedec_id);
            $display("spi0_norflash_read_jedec_id done: jedec_id = 0x%x", jedec_id);
            `ZQH_TOP.spi0_norflash_read_unique_id(unique_id);
            $display("spi0_norflash_read_unique_id done: unique_id = 0x%x", unique_id);

//tmp            address_found = 0;
//tmp            while($feof(fd) == 0) begin
//tmp                begin
//tmp                    code = $fscanf(fd, "%s", line);
//tmp                    if (code != 0) begin
//tmp                        //$display(line);
//tmp                        if ($sscanf(line, " @%h\n", address)) begin
//tmp                            $display("%h", address);
//tmp                            address_found = 1;
//tmp                        end
//tmp                        else begin 
//tmp                            if ($sscanf(line, "%h\n", data_byte)) begin
//tmp                                if (address_found) begin
//tmp                                    $display("%h", data_byte);
//tmp                                    dmi_flash_write_byte(address, data_byte);
//tmp                                end
//tmp                            end
//tmp                            address_found = 0;
//tmp                        end
//tmp                    end
//tmp                end
//tmp            end
            $fclose(fd);





            //for (int i = 0; i < 10; i++) begin
            //while(1) begin
            //    req_op = 1;
            //    req_addr = 32'h12;
            //    `ZQH_TOP.test_harness.simJTAG.push_req(req_op, req_addr, req_data);
            //    `ZQH_TOP.test_harness.simJTAG.wait_resp(resp_resp, resp_data);
            //    //repeat(10000) @(posedge `ZQH_TOP.clock);
            //end
        end

    endtask
endmodule
