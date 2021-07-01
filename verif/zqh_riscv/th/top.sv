`timescale 1ns/1ps
module top;
    reg clock = 1'b0;
    reg clock_rtc = 1'b0;
    reg clock_uart = 1'b0;
    reg jtag_tck = 1'b0;
    reg reset_n = 1'b0;

    real clock_prd;
    real clock_rtc_prd;
    real jtag_tck_prd;
    real clock_uart_prd;
    initial begin
        clock_prd = `CLOCK_PERIOD/2.0;
        while(1) begin
            #(clock_prd) clock = ~clock;
        end
    end
    initial begin
        clock_rtc_prd = 500.0;
        while(1) begin
            #(clock_rtc_prd) clock_rtc = ~clock_rtc;
        end
    end
    initial begin
        jtag_tck_prd = `CLOCK_PERIOD*2.0;
        while(1) begin
            #(jtag_tck_prd) jtag_tck = ~jtag_tck;
        end
    end
    initial begin
        clock_uart_prd = (`CLOCK_PERIOD/5.0)/2.0;
        while(1) begin
            #(clock_uart_prd) clock_uart = ~clock_uart;
        end
    end

    reg [63:0] max_cycles = 0;
    reg [63:0] dump_start = 0;
    reg [63:0] trace_count = 0;
    reg wave_dump = 0;
    string wavefile;

    `ifdef HAS_DDR
        `ifdef DDR_LOG_PRINT
            defparam `ZQH_TOP.test_harness.ddr3_chips_0.DEBUG = 1;
            defparam `ZQH_TOP.test_harness.ddr3_chips_1.DEBUG = 1;
            `ifdef DDR_PHY_X8
            defparam `ZQH_TOP.test_harness.ddr3_chips_2.DEBUG = 1;
            defparam `ZQH_TOP.test_harness.ddr3_chips_3.DEBUG = 1;
            `endif
        `else
            defparam `ZQH_TOP.test_harness.ddr3_chips_0.DEBUG = 0;
            defparam `ZQH_TOP.test_harness.ddr3_chips_1.DEBUG = 0;
            `ifdef DDR_PHY_X8
            defparam `ZQH_TOP.test_harness.ddr3_chips_2.DEBUG = 0;
            defparam `ZQH_TOP.test_harness.ddr3_chips_3.DEBUG = 0;
            `endif
        `endif

        `ifdef DDR_STOP_ON_ERROR
            defparam `ZQH_TOP.test_harness.ddr3_chips_0.STOP_ON_ERROR = 1;
            defparam `ZQH_TOP.test_harness.ddr3_chips_1.STOP_ON_ERROR = 1;
            `ifdef DDR_PHY_X8
            defparam `ZQH_TOP.test_harness.ddr3_chips_2.STOP_ON_ERROR = 1;
            defparam `ZQH_TOP.test_harness.ddr3_chips_3.STOP_ON_ERROR = 1;
            `endif
        `else      
            defparam `ZQH_TOP.test_harness.ddr3_chips_0.STOP_ON_ERROR = 0;
            defparam `ZQH_TOP.test_harness.ddr3_chips_1.STOP_ON_ERROR = 0;
            `ifdef DDR_PHY_X8
            defparam `ZQH_TOP.test_harness.ddr3_chips_2.STOP_ON_ERROR = 0;
            defparam `ZQH_TOP.test_harness.ddr3_chips_3.STOP_ON_ERROR = 0;
            `endif
        `endif
    `endif

    initial begin
        $value$plusargs("max-cycles=%d", max_cycles);
        $value$plusargs("dump-start=%d", dump_start);
        $value$plusargs("wave_dump=%d", wave_dump);
        $value$plusargs("wavefile=%s", wavefile);
  
        `ifdef FSDB_ON
            wait(trace_count == dump_start);
            if (wave_dump == 1) begin
                $fsdbDumpfile(wavefile);
                $fsdbDumpvars("+all");
                $fsdbDumpSVA;
            end
        `endif
        `ifdef VCD_ON
            if (wave_dump == 1) begin
                $dumpfile(wavefile);
                $dumpvars(0, top);
            end
        `endif
    end
  
    reg [255:0] reason = "";
    reg time_out = 1'b0;
    reg[3:0] success = 0;
    reg[3:0] fails = 0;
    always @(posedge clock) begin
        trace_count = trace_count + 1;
        if (reset_n) begin
            if (max_cycles > 0 && trace_count > max_cycles) begin
                reason = "timeout";
                time_out = 1'b1;
            end
  
            //DUT's print_monitor will set stop_flag and stop_code
            `ifdef HAS_PRINT_MONITOR
            success[0] <= `ZQH_DUT.system.mmio_print_monitor.stop_flag_0_o & 
                (`ZQH_DUT.system.mmio_print_monitor.stop_code_0_o == 1);
            success[1] <= `ZQH_DUT.system.mmio_print_monitor.stop_flag_1_o & 
                (`ZQH_DUT.system.mmio_print_monitor.stop_code_1_o == 1);
            success[2] <= `ZQH_DUT.system.mmio_print_monitor.stop_flag_2_o & 
                (`ZQH_DUT.system.mmio_print_monitor.stop_code_2_o == 1);
            success[3] <= `ZQH_DUT.system.mmio_print_monitor.stop_flag_3_o & 
                (`ZQH_DUT.system.mmio_print_monitor.stop_code_3_o == 1);

            fails[0] <= `ZQH_DUT.system.mmio_print_monitor.stop_flag_0_o & 
                (`ZQH_DUT.system.mmio_print_monitor.stop_code_0_o > 1);
            fails[1] <= `ZQH_DUT.system.mmio_print_monitor.stop_flag_1_o & 
                (`ZQH_DUT.system.mmio_print_monitor.stop_code_1_o > 1);
            fails[2] <= `ZQH_DUT.system.mmio_print_monitor.stop_flag_2_o & 
                (`ZQH_DUT.system.mmio_print_monitor.stop_code_2_o > 1);
            fails[3] <= `ZQH_DUT.system.mmio_print_monitor.stop_flag_3_o & 
                (`ZQH_DUT.system.mmio_print_monitor.stop_code_3_o > 1);
            `endif
        end
    end
  
    zqh_test_harness_ut test_harness(
        .clock(clock),
        .io_clock_rtc(clock_rtc),
        .io_clock_uart(clock_uart),
        .io_clock_jtag(jtag_tck),
        .reset_n(reset_n) 
    );

    //usb device connetion
    initial begin
        //tmp force `ZQH_TOP.test_harness.dut_io_usb_device_dp = 0;
        //tmp force `ZQH_TOP.test_harness.dut_io_usb_device_dm = 0;
        //tmp #588947ns;
        //tmp release `ZQH_TOP.test_harness.dut_io_usb_device_dp;
        //tmp release `ZQH_TOP.test_harness.dut_io_usb_device_dm;

        //tmpfor (int i = 0; i < 10; i++) begin
        //tmp    force `ZQH_TOP.test_harness.dut_io_usb_device_dp = 0;
        //tmp    force `ZQH_TOP.test_harness.dut_io_usb_device_dm = 0;
        //tmp    #50000ns;
        //tmp    release `ZQH_TOP.test_harness.dut_io_usb_device_dp;
        //tmp    release `ZQH_TOP.test_harness.dut_io_usb_device_dm;
        //tmp    #50000ns;
        //tmpend
    end

`ifdef USE_JTAG
    //jtag interface
    always @(posedge clock) begin
        if (reset_n) begin
            if (`ZQH_TOP.test_harness.simJTAG.exit >= 2) begin
                fails[0] <= 1;
                fails[1] <= 1;
                fails[2] <= 1;
                fails[3] <= 1;
                reason = "SimJTAG exit";
            end
            else if (`ZQH_TOP.test_harness.simJTAG.exit == 2) begin
                success[0] <= 1;
                success[1] <= 1;
                success[2] <= 1;
                success[3] <= 1;
                reason = "SimJTAG exit";
            end
        end
    end
`endif

    //
    //DUT internal memory initial
    initial begin: memory_initial
        //tmp reg[511:0] m_cpu_instr_init_file;
        string m_cpu_instr_init_file;
        string bootloader_data_file;
        int fd;
        int code;
        string line;
        int address_found;
        bit[31:0] address;
        bit[7:0] data_byte;
        bit[31:0] memory_used[4];
        bit[511:0] mem_random_data;

        $value$plusargs("zqh_cpu_instr_init_file=%s",m_cpu_instr_init_file);

        //wait a few cycles for reset statble
        repeat(10) @(posedge `ZQH_TOP.clock);

        //initial itim and dtim memory to 0 to avoid ecc error
        `ifdef CORE0_EN
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(0).ifu.icache.data_array.m); idx++) begin
                mem_random_data = {
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom() 
                };
                `ZQH_CORE_WRAP(0).ifu.icache.data_array.m[idx] = mem_random_data;
            end
            `ifdef USE_ITIM
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(0).ifu.icache.itim_array.m); idx++) begin
                `ZQH_CORE_WRAP(0).ifu.icache.itim_array.m[idx] = 0;
            end
            `endif
            `ifdef USE_DTIM
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(0).lsu.dcache.dtim_array.m); idx++) begin
                `ZQH_CORE_WRAP(0).lsu.dcache.dtim_array.m[idx] = 0;
            end
            `endif
        `endif
        `ifdef CORE1_EN
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(1).ifu.icache.data_array.m); idx++) begin
                mem_random_data = {
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom() 
                };
                `ZQH_CORE_WRAP(1).ifu.icache.data_array.m[idx] = mem_random_data;
            end
            `ifdef USE_ITIM
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(1).ifu.icache.itim_array.m); idx++) begin
                `ZQH_CORE_WRAP(1).ifu.icache.itim_array.m[idx] = 0;
            end
            `endif
            `ifdef USE_DTIM
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(1).lsu.dcache.dtim_array.m); idx++) begin
                `ZQH_CORE_WRAP(1).lsu.dcache.dtim_array.m[idx] = 0;
            end
            `endif
        `endif
        `ifdef CORE2_EN
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(2).ifu.icache.data_array.m); idx++) begin
                mem_random_data = {
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom() 
                };
                `ZQH_CORE_WRAP(2).ifu.icache.data_array.m[idx] = mem_random_data;
            end
            `ifdef USE_ITIM
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(2).ifu.icache.itim_array.m); idx++) begin
                `ZQH_CORE_WRAP(2).ifu.icache.itim_array.m[idx] = 0;
            end
            `endif
            `ifdef USE_DTIM
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(2).lsu.dcache.dtim_array.m); idx++) begin
                `ZQH_CORE_WRAP(2).lsu.dcache.dtim_array.m[idx] = 0;
            end
            `endif
        `endif
        `ifdef CORE3_EN
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(3).ifu.icache.data_array.m); idx++) begin
                mem_random_data = {
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom(),
                    $urandom(), $urandom(), $urandom(), $urandom() 
                };
                `ZQH_CORE_WRAP(3).ifu.icache.data_array.m[idx] = mem_random_data;
            end
            `ifdef USE_ITIM
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(3).ifu.icache.itim_array.m); idx++) begin
                `ZQH_CORE_WRAP(3).ifu.icache.itim_array.m[idx] = 0;
            end
            `endif
            `ifdef USE_DTIM
            for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(3).lsu.dcache.dtim_array.m); idx++) begin
                `ZQH_CORE_WRAP(3).lsu.dcache.dtim_array.m[idx] = 0;
            end
            `endif
        `endif

        begin
            //initial mem_sram
            for (int idx = 0; idx < $size(`ZQH_DUT.system.mem_sram_control.data_array.m); idx++) begin
                //tmp std::randomize(mem_random_data);
                //mem_random_data = {$urandom(), $urandom(), $urandom(), $urandom()};
                mem_random_data = 0;
                `ZQH_DUT.system.mem_sram_control.data_array.m[idx] = mem_random_data;
            end

            //initial mmio_sram
            for (int idx = 0; idx < $size(`ZQH_DUT.system.mmio_sram_control.data_array.m); idx++) begin
                //tmp std::randomize(mem_random_data);
                //mem_random_data = {$urandom(), $urandom(), $urandom(), $urandom()};
                mem_random_data = 0;
                `ZQH_DUT.system.mmio_sram_control.data_array.m[idx] = mem_random_data;
            end

            //initial mem_axi4_sram
            `ifdef HAS_AXI4_SRAM
            for (int idx = 0; idx < $size(`ZQH_DUT.system.mem_axi4_sram_control.data_array.m); idx++) begin
                //tmp std::randomize(mem_random_data);
                //mem_random_data = {$urandom(), $urandom(), $urandom(), $urandom()};
                mem_random_data = 0;
                `ZQH_DUT.system.mem_axi4_sram_control.data_array.m[idx] = mem_random_data;
            end
            `endif

            //initial DDR3 model
            `ifdef HAS_DDR
            for (int idx = 0; idx < $size(`ZQH_TOP.test_harness.ddr3_chips_0.memory); idx++) begin
                //mem_random_data = {$urandom(), $urandom(), $urandom(), $urandom()};
                mem_random_data = 0;
                `ZQH_TOP.test_harness.ddr3_chips_0.memory[idx] = mem_random_data;
            end
            for (int idx = 0; idx < $size(`ZQH_TOP.test_harness.ddr3_chips_1.memory); idx++) begin
                //mem_random_data = {$urandom(), $urandom(), $urandom(), $urandom()};
                mem_random_data = 0;
                `ZQH_TOP.test_harness.ddr3_chips_1.memory[idx] = mem_random_data;
            end
            `ifdef DDR_PHY_X8
            for (int idx = 0; idx < $size(`ZQH_TOP.test_harness.ddr3_chips_2.memory); idx++) begin
                //mem_random_data = {$urandom(), $urandom(), $urandom(), $urandom()};
                mem_random_data = 0;
                `ZQH_TOP.test_harness.ddr3_chips_2.memory[idx] = mem_random_data;
            end
            for (int idx = 0; idx < $size(`ZQH_TOP.test_harness.ddr3_chips_3.memory); idx++) begin
                //mem_random_data = {$urandom(), $urandom(), $urandom(), $urandom()};
                mem_random_data = 0;
                `ZQH_TOP.test_harness.ddr3_chips_3.memory[idx] = mem_random_data;
            end
            `endif
            `endif
        end

 
        fd = $fopen(m_cpu_instr_init_file, "r");
        if (fd == 0) begin
            $display("%s could not open", m_cpu_instr_init_file);
            $finish();
        end
        address_found = 0;
        while($feof(fd) == 0) begin
            begin
                code = $fscanf(fd, "%s", line);
                if (code != 0) begin
                    //$display(line);
                    if ($sscanf(line, " @%h\n", address)) begin
                        //$display("%h", address);
                        address_found = 1;
                    end
                    else begin 
                        if ($sscanf(line, "%h\n", data_byte)) begin
                            if (address_found) begin
                                //$display("%h", data_byte);
                                dut_tim_init(address, data_byte);
                                //tmp dut_mem_sram_mem_init(address, data_byte);
                                `ifdef HAS_DDR
                                    ddr3_mem_init(address, data_byte);
                                `endif
                                dut_mem_sram_mem_init(address, data_byte);
                            end
                        end
                        address_found = 0;
                    end
                end
            end
        end
        `ifdef HAS_DDR
        memory_used[0] = `ZQH_TOP.test_harness.ddr3_chips_0.memory_used;
        memory_used[1] = `ZQH_TOP.test_harness.ddr3_chips_1.memory_used;
        `ifdef DDR_PHY_X8
        memory_used[2] = `ZQH_TOP.test_harness.ddr3_chips_2.memory_used;
        memory_used[3] = `ZQH_TOP.test_harness.ddr3_chips_3.memory_used;
        `endif
        `endif
        $fclose(fd);


        //bootloader instruction and data initial
        //bootloader_data_file = $psprintf("%s%s",`FILENAME_mem, ".data");
        $sformat(bootloader_data_file, "%s%s",`FILENAME_mem, ".data");
        fd = $fopen(bootloader_data_file, "r");
        if (fd == 0) begin
            $display("%s could not open", bootloader_data_file);
            $finish();
        end
        address_found = 0;
        while($feof(fd) == 0) begin
            begin
                code = $fscanf(fd, "%s", line);
                if (code != 0) begin
                    //$display(line);
                    if ($sscanf(line, " @%h\n", address)) begin
                        //$display("%h", address);
                        address_found = 1;
                    end
                    else begin 
                        if ($sscanf(line, "%h\n", data_byte)) begin
                            if (address_found) begin
                                //$display("%h", data_byte);
                                //tmp dut_mmio_sram_mem_init(address, data_byte);
                                dut_mem_sram_mem_init(address, data_byte);
                            end
                        end
                        address_found = 0;
                    end
                end
            end
        end
        $fclose(fd);
        //



        //gen itim's ecc code
        begin
            int has_ecc;
            int error_1bit;
            int error_2bit;
            has_ecc = 1;
            error_1bit = 0;
            error_2bit = 0;

            if (has_ecc) begin
                int data_width;
                bit[31:0] data;
                bit[38:0] flip_data;

                if (error_2bit) begin
                    flip_data = 39'b110_0000_0000_0000_0000_0000_0000_0000_0000_0000;
                end
                else if (error_1bit) begin
                    flip_data = 39'b000_0000_0000_0000_0000_0000_0000_0000_0000_0001;
                end
                else begin
                    flip_data = 39'b000_0000_0000_0000_0000_0000_0000_0000_0000_0000;
                end

            `ifdef USE_ITIM
                `ifdef CORE0_EN
                    data_width = $size(`ZQH_CORE_WRAP(0).ifu.icache.itim_array.io_wdata);
                    for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(0).ifu.icache.itim_array.m); idx++) begin
                        //each row has 2 32bit instruction data slice
                        for (int j = 0; j < data_width/39; j++) begin
                            data = `ZQH_CORE_WRAP(0).ifu.icache.itim_array.m[idx][j*39 +: 32];
                            `ZQH_CORE_WRAP(0).ifu.icache.itim_array.m[idx][j*39 +: 39] = zqh_vbase_ecc_encode32(data) ^ flip_data;
                        end
                    end
                `endif
                `ifdef CORE1_EN
                    data_width = $size(`ZQH_CORE_WRAP(1).ifu.icache.itim_array.m[0]);
                    for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(1).ifu.icache.itim_array.m); idx++) begin
                        //each row has 2 32bit instruction data slice
                        for (int j = 0; j < data_width/39; j++) begin
                            data = `ZQH_CORE_WRAP(1).ifu.icache.itim_array.m[idx][j*39 +: 32];
                            `ZQH_CORE_WRAP(1).ifu.icache.itim_array.m[idx][j*39 +: 39] = zqh_vbase_ecc_encode32(data) ^ flip_data;
                        end
                    end
                `endif
                `ifdef CORE2_EN
                    data_width = $size(`ZQH_CORE_WRAP(2).ifu.icache.itim_array.m[0]);
                    for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(2).ifu.icache.itim_array.m); idx++) begin
                        //each row has 2 32bit instruction data slice
                        for (int j = 0; j < data_width/39; j++) begin
                            data = `ZQH_CORE_WRAP(2).ifu.icache.itim_array.m[idx][j*39 +: 32];
                            `ZQH_CORE_WRAP(2).ifu.icache.itim_array.m[idx][j*39 +: 39] = zqh_vbase_ecc_encode32(data) ^ flip_data;
                        end
                    end
                `endif
                `ifdef CORE3_EN
                    data_width = $size(`ZQH_CORE_WRAP(3).ifu.icache.itim_array.m[0]);
                    for (int idx = 0; idx < $size(`ZQH_CORE_WRAP(3).ifu.icache.itim_array.m); idx++) begin
                        //each row has 2 32bit instruction data slice
                        for (int j = 0; j < data_width/39; j++) begin
                            data = `ZQH_CORE_WRAP(3).ifu.icache.itim_array.m[idx][j*39 +: 32];
                            `ZQH_CORE_WRAP(3).ifu.icache.itim_array.m[idx][j*39 +: 39] = zqh_vbase_ecc_encode32(data) ^ flip_data;
                        end
                    end
                `endif
            `endif
            end
        end

        //ddr3 chips rst_n will clean it's memory_used, need recover it when
        //rst_n de-assert
        `ifdef HAS_DDR
        repeat(20) @(posedge `ZQH_TOP.test_harness.ddr3_chips_0.ck);
        wait(`ZQH_TOP.test_harness.ddr3_chips_0.rst_n === 1);
        repeat(10) @(posedge `ZQH_TOP.test_harness.ddr3_chips_0.ck);
        `ZQH_TOP.test_harness.ddr3_chips_0.memory_used = memory_used[0];
        `ZQH_TOP.test_harness.ddr3_chips_1.memory_used = memory_used[1];
        `ifdef DDR_PHY_X8
        `ZQH_TOP.test_harness.ddr3_chips_2.memory_used = memory_used[2];
        `ZQH_TOP.test_harness.ddr3_chips_3.memory_used = memory_used[3];
        `endif
        `endif

    end

    task dut_tim_init(bit[31:0] address, bit[7:0] data_byte);
        bit[31:0] itim_base;
        bit[31:0] itim_size;
        bit[31:0] dtim_base;
        bit[31:0] dtim_size;
        bit[31:0] address_mode;
        bit[31:0] mem_address;
        int inst_off;
        int byte_off;
        bit[31:0] mem_data;
        bit[38:0] flip_data;

        itim_base = 32'h80000000;
        itim_size = 2**13;
        dtim_base = 32'h81000000;
        dtim_size = 2**13;

        address_mode = address%4;

        `ifdef USE_ITIM
        //icache/itim's ecc_bytes fixed to 4
        if ((address >= itim_base) && (address < itim_base + itim_size)) begin
            mem_address = (address & 32'h0fff_ffff) >> 3;
            inst_off = ((address%8)/4)*39;
            byte_off = address_mode*8 + inst_off;
            `ifdef CORE0_EN
                `ZQH_CORE_WRAP(0).ifu.icache.itim_array.m[mem_address][byte_off +: 8] = data_byte;
            `endif
            `ifdef CORE1_EN
                `ZQH_CORE_WRAP(1).ifu.icache.itim_array.m[mem_address][byte_off +: 8] = data_byte;
            `endif
            `ifdef CORE2_EN
                `ZQH_CORE_WRAP(2).ifu.icache.itim_array.m[mem_address][byte_off +: 8] = data_byte;
            `endif
            `ifdef CORE3_EN
                `ZQH_CORE_WRAP(3).ifu.icache.itim_array.m[mem_address][byte_off +: 8] = data_byte;
            `endif
        end
        `endif
    endtask

    //tmp task dut_mmio_sram_mem_init(bit[31:0] address, bit[7:0] data_byte);
    //tmp     bit[31:0] mem_address;
    //tmp     int data_bytes;
    //tmp     int address_offset;
    //tmp     int byte_off;
    //tmp     data_bytes = $size(`ZQH_DUT.system.mmio_sram_control.io_tl_from_extern_in_sram_control_slave_a_bits_data)/8;
    //tmp     address_offset = $clog2(data_bytes);
    //tmp     mem_address = (address & 32'h0fff_ffff) >> address_offset;
    //tmp     byte_off = (address%data_bytes) * 8;
    //tmp     `ZQH_DUT.system.mmio_sram_control.data_array.m[mem_address][byte_off +: 8] = data_byte;
    //tmp endtask

    task dut_mem_sram_mem_init(bit[31:0] address, bit[7:0] data_byte);
        bit[31:0] mem_address;
        int data_bytes;
        int address_offset;
        int byte_off;
        data_bytes = $size(`ZQH_DUT.system.mem_sram_control.io_tl_from_extern_in_sram_control_slave_a_bits_data)/8;
        address_offset = $clog2(data_bytes);
        mem_address = (address & 32'h0fff_ffff) >> address_offset;
        byte_off = (address%data_bytes) * 8;
        `ZQH_DUT.system.mem_sram_control.data_array.m[mem_address][byte_off +: 8] = data_byte;
    endtask

    task ddr3_mem_init(bit[31:0] address, bit[7:0] data_byte);
        `ifdef HAS_DDR

        `ifdef DDR_PHY_X8
            `define TB_DDR_XN 8
            `define TB_DDR_ADDR_BITS       14
            `define TB_DDR_ROW_BITS        14
            `define TB_DDR_COL_BITS        10
        `endif
        `ifdef DDR_PHY_X16
            `define TB_DDR_XN  16
            `define TB_DDR_ADDR_BITS       15
            `define TB_DDR_ROW_BITS        15
            `define TB_DDR_COL_BITS        10
        `endif
        `define TB_DDR_BL_MAX 8

        bit[31:0] address_ddr;
        int phy_data_bytes;
        int phy_data_bytes_bits;
        int dfi_data_bytes;
        int dfi_data_bytes_bits;
        int chip_id;
        int burst_idx_base;
        int burst_idx;
        bit[`TB_DDR_COL_BITS - 1:0] col;
        bit[`TB_DDR_COL_BITS - 1:0] col_bl;
        bit[2:0] bank;
        bit[`TB_DDR_ROW_BITS - 1:0] row;
        bit[2:0] address_h;
        bit[1:0] address_l;
        bit[`TB_DDR_BL_MAX*`TB_DDR_XN - 1 :0] data_bl;
        bit[31:0] data_bl_idx_start;

        phy_data_bytes = 4;
        phy_data_bytes_bits = $clog2(phy_data_bytes);
        dfi_data_bytes = phy_data_bytes * 2;
        dfi_data_bytes_bits = $clog2(dfi_data_bytes);

        col_bl = (address >> $clog2(phy_data_bytes))/`TB_DDR_BL_MAX * `TB_DDR_BL_MAX;
        bank = address >> ($size(col) + $clog2(phy_data_bytes));
        row = address >> ($size(bank) + $size(col) + $clog2(phy_data_bytes));
        chip_id = (address%dfi_data_bytes)/(`TB_DDR_XN/8 * 2);
        burst_idx_base = ((address >> $clog2(dfi_data_bytes)) * 2)%`TB_DDR_BL_MAX;
        burst_idx = burst_idx_base + (((address%phy_data_bytes) >> $clog2(`TB_DDR_XN/8))%2);
        col = col_bl + burst_idx;

        data_bl_idx_start = burst_idx*`TB_DDR_XN + (address%(`TB_DDR_XN/8))*8;
        if (chip_id == 0) begin
            //read and modify the corrisponding byte
            `ZQH_TOP.test_harness.ddr3_chips_0.memory_read(bank, row, col_bl, data_bl);
            data_bl[data_bl_idx_start +: 8] = data_byte;
            `ZQH_TOP.test_harness.ddr3_chips_0.memory_write(bank, row, col_bl, data_bl);
        end
        else if (chip_id == 1) begin
            `ZQH_TOP.test_harness.ddr3_chips_1.memory_read(bank, row, col_bl, data_bl);
            data_bl[data_bl_idx_start +: 8] = data_byte;
            `ZQH_TOP.test_harness.ddr3_chips_1.memory_write(bank, row, col_bl, data_bl);
        end
        else if (chip_id == 2) begin
            `ifdef DDR_PHY_X8
            `ZQH_TOP.test_harness.ddr3_chips_2.memory_read(bank, row, col_bl, data_bl);
            data_bl[data_bl_idx_start +: 8] = data_byte;
            `ZQH_TOP.test_harness.ddr3_chips_2.memory_write(bank, row, col_bl, data_bl);
            `endif
        end
        else if (chip_id == 3) begin
            `ifdef DDR_PHY_X8
            `ZQH_TOP.test_harness.ddr3_chips_3.memory_read(bank, row, col_bl, data_bl);
            data_bl[data_bl_idx_start +: 8] = data_byte;
            `ZQH_TOP.test_harness.ddr3_chips_3.memory_write(bank, row, col_bl, data_bl);
            `endif
        end
        //$display("ddr3_mem_init write address(%h), bank(%h), row(%h), col_bl(%h), chip_id(%h), burst_idx(%h). with data_byte(%h), data_bl(%h)", address, bank, row, col_bl, chip_id, burst_idx, data_byte, data_bl);
        `endif
    endtask



    task dmi_reg_read(bit[31:0] addr, output bit[31:0] data);
        bit[31:0] req_op;
        bit[31:0] req_addr;
        bit[31:0] resp_resp;
        bit[31:0] resp_data;
        req_op = 1;
        req_addr = addr;
        `ZQH_TOP.test_harness.simJTAG.push_req(req_op, req_addr, 0);
        `ZQH_TOP.test_harness.simJTAG.wait_resp(resp_resp, resp_data);
        if (resp_resp != 0) begin
            $display("resp error: resp = %x, data", resp_resp, resp_data);
            while(1);
        end
        data = resp_data;
    endtask
    task dmi_reg_write(bit[31:0] addr, bit[31:0] data);
        bit[31:0] req_op;
        bit[31:0] req_addr;
        bit[31:0] req_data;
        bit[31:0] resp_resp;
        bit[31:0] resp_data;
        req_op = 2;
        req_addr = addr;
        req_data = data;
        `ZQH_TOP.test_harness.simJTAG.push_req(req_op, req_addr, req_data);
        `ZQH_TOP.test_harness.simJTAG.wait_resp(resp_resp, resp_data);
        if (resp_resp != 0) begin
            $display("resp error: resp = %x, data", resp_resp, resp_data);
            while(1);
        end
    endtask

    task dmi_sba_store_32b(bit[63:0] taddr, bit[31:0] data);
        bit[31:0] sbcs_rd_data;
        bit[31:0] sbcs_busy;
        bit[31:0] sbcs_error;

        $display("zqh: dmi_sba_store_32b");
        $display("zqh: dmi_sba_store_32b taddr = 0x%x", taddr);
        $display("zqh: dmi_sba_store_32b data = 0x%x", data);
        //set sbcs
        dmi_reg_write(`DMI_SBCS, `DMI_SBCS_SBBUSYERROR | (2 << `DMI_SBCS_SBACCESS_OFFSET) | `DMI_SBCS_SBERROR);
    
        //set address
        dmi_reg_write(`DMI_SBADDRESS1, taddr[63:32]);//high 32bit
        dmi_reg_write(`DMI_SBADDRESS0, taddr[31:0]);//low 32bit
    
        //set store data
        dmi_reg_write(`DMI_SBDATA1, 0);//high 32bit
        dmi_reg_write(`DMI_SBDATA0, data);//low 32bit
    
        //wait done
        sbcs_busy = 1;
        while(sbcs_busy) begin
            dmi_reg_read(`DMI_SBCS, sbcs_rd_data);
            sbcs_busy = (sbcs_rd_data & `DMI_SBCS_SBBUSY) >> `DMI_SBCS_SBBUSY_OFFSET;
            sbcs_error = (sbcs_rd_data & `DMI_SBCS_SBERROR) >> `DMI_SBCS_SBERROR_OFFSET;
        end
        assert(sbcs_error == 0);
    
        $display("zqh: dmi_sba_store_32b done");
    endtask

    task dmi_sba_load_32b(bit[63:0] taddr, output bit[31:0] data);
        bit[31:0] sbcs_rd_data;
        bit[31:0] sbcs_busy;
        bit[31:0] sbcs_error;
    
        $display("zqh: dmi_sba_load_32b");
        $display("zqh: dmi_sba_load_32b taddr = 0x%x", taddr);
    
        //set sbcs
        dmi_reg_write(`DMI_SBCS, `DMI_SBCS_SBBUSYERROR | `DMI_SBCS_SBSINGLEREAD | (2 << `DMI_SBCS_SBACCESS_OFFSET) | `DMI_SBCS_SBERROR);
    
        //set access address
        dmi_reg_write(`DMI_SBADDRESS1, taddr[63:32]);//high 32bit
        dmi_reg_write(`DMI_SBADDRESS0, taddr[31:0]);//low 32bit
    
    
        //wait done
        sbcs_busy = 1;
        while(sbcs_busy) begin
            dmi_reg_read(`DMI_SBCS, sbcs_rd_data);
            sbcs_busy = (sbcs_rd_data & `DMI_SBCS_SBBUSY) >> `DMI_SBCS_SBBUSY_OFFSET;
            sbcs_error = (sbcs_rd_data & `DMI_SBCS_SBERROR) >> `DMI_SBCS_SBERROR_OFFSET;
        end
        assert(sbcs_error == 0);
    
    
    
        //readout data
        dmi_reg_read(`DMI_SBDATA0, data);//low 32b
        $display("zqh: dmi_sba_load_32b data = 0x%x", data);
        $display("zqh: dmi_sba_load_32b done");
    endtask

    task spi0_tx_rx_byte(bit[7:0] wrdata, bit[32:0] rx, output bit[7:0] rddata);
        //wait tx_fifo none full
        bit[31:0] txdata;
        bit[31:0] rxdata;
        bit[31:0] ip;
        txdata = 32'h80000000;
        while((txdata & 32'h80000000) != 0) begin
            dmi_sba_load_32b(`SPI0_TXDATA, txdata);
        end
        dmi_sba_store_32b(`SPI0_TXDATA, wrdata);
    
        //wait tx_fifo empty
        do begin
            dmi_sba_load_32b(`SPI0_IP, ip);
            ip = ip & 32'h01;
        end 
        while(ip == 0);
    
        //wait rx_fifo none empty
        rxdata = 32'h80000000;
        if (rx) begin
            while((rxdata & 32'h80000000) != 0) begin
                dmi_sba_load_32b(`SPI0_RXDATA, rxdata);
            end
        end
        rddata = rxdata;
    endtask

    task spi0_norflash_read_jedec_id(output bit[31:0] id);
        bit[31:0] rx_data;
        bit[31:0] tmp_reg_rddata;
        //use hold mode
        dmi_sba_store_32b(`SPI0_CSMODE, 2); //0: auto, 1: reserved, 2: hold, 3: off
        dmi_sba_store_32b(`SPI0_TXMARK, 1);//if tx_fifo is empty, ip.txwm will be valid
        dmi_sba_store_32b(`SPI0_FMT, 32'h00080008);//len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)
    
        //send cmd
        spi0_tx_rx_byte(32'h9f, 0, rx_data);
    
    
        //recieve 3 byte data
        dmi_sba_load_32b(`SPI0_FMT, tmp_reg_rddata);
        dmi_sba_store_32b(`SPI0_FMT, tmp_reg_rddata & 32'hfffffff7);//dir = 0(rx)
        id = 0;
        for (int i = 0; i < 3; i++) begin
            spi0_tx_rx_byte(0, 1, rx_data);
            id = (rx_data << ((2 - i)*8)) | id;
        end
    
        //reset to auto mode
        dmi_sba_store_32b(`SPI0_CSMODE, 0);
    endtask


    task spi0_norflash_read_unique_id(output bit[63:0] id);
        bit[63:0] rx_data;
        bit[31:0] tmp_reg_rddata;
        //use hold mode
        dmi_sba_store_32b(`SPI0_CSMODE, 2); //0: auto, 1: reserved, 2: hold, 3: off
        dmi_sba_store_32b(`SPI0_TXMARK, 1);//if tx_fifo is empty, ip.txwm will be valid
        dmi_sba_store_32b(`SPI0_FMT, 32'h00080008);//len = 8, dir = 1(tx), endian = 0(big endian), proto = 0(single)
    
    
        //send cmd
        spi0_tx_rx_byte(32'h4b, 0, rx_data);
    
        //send 4 dumy byte
        for (int i = 0; i < 4; i++) begin
            spi0_tx_rx_byte(0, 0, rx_data);
        end
    
        //recieve 8 byte data
        dmi_sba_load_32b(`SPI0_FMT, tmp_reg_rddata);
        dmi_sba_store_32b(`SPI0_FMT, tmp_reg_rddata & 32'hfffffff7);//dir = 0(rx)
        id = 0;
        for (int i = 0; i < 8; i++) begin
            spi0_tx_rx_byte(0, 1, rx_data);
            id = (rx_data << ((7 - i)*8)) | id;
        end
    
        //reset to auto mode
        dmi_sba_store_32b(`SPI0_CSMODE, 0);
    endtask
endmodule
