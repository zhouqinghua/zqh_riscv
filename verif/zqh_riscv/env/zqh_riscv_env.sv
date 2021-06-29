//`timescale 1ns/1ps
module zqh_riscv_env();
    zqh_vbase_log log;
    string name = "zqh_riscv_env";
    bit[3:0] m_hart_on = 0;
    int m_build_state = 0;
    int m_config_test_state = 0;
    int m_reset_state = 0;
    int m_config_dut_state = 0;
    int m_start_state = 0;
    int m_run_state = 0;
    int m_clean_up_state = 0;
    int m_report_state = 0;
    
    initial begin
        $printtimescale(top);
        $timeformat(-9, 2, "ns", 5);
        log = new(name);
        build();
        config_test();
        reset();
        config_dut();
        start();
        run();
        clean_up();
        report();
    end

    task build();
        m_build_state = 1;
        for (int i = 0; i < `CORE_NUM; i++) begin
            m_hart_on[i] = 1;
        end
        //$assertoff(0, `ZQH_TOP);
        m_build_state = 2;
    endtask

    task config_test();
        m_config_test_state = 1;
        ;
        m_config_test_state = 2;
    endtask

    task reset();
        m_reset_state = 1;

        //boot_mode set
        begin
            static reg[7:0] boot_mode = 0;
            $value$plusargs("boot_mode=%d", boot_mode);
            force `ZQH_DUT.io_boot_mode = boot_mode;
        end


        //uart's tx loopback to rx
        begin
            int uart_lb= 0;
            $value$plusargs("uart_lb=%d", uart_lb);
            if (uart_lb) begin
                force `ZQH_TOP.test_harness.uart_print_monitor.io_tx = `ZQH_TOP.test_harness.uart_print_monitor.io_rx;
            end
        end

        //uart print monitor's baud div/parity same as DUT's
        force `ZQH_TOP.test_harness.uart_print_monitor.clock = `ZQH_TOP.test_harness.dut.system.mmio_uart0.clock;
        force `ZQH_TOP.test_harness.uart_print_monitor.reset = `ZQH_TOP.test_harness.dut.system.mmio_uart0.reset;
        force `ZQH_TOP.test_harness.uart_print_monitor.cfg_div = `ZQH_TOP.test_harness.dut.system.mmio_uart0.div_div_o;
        force `ZQH_TOP.test_harness.uart_print_monitor.cfg_parity = `ZQH_TOP.test_harness.dut.system.mmio_uart0.txctrl_parity_o;

        //jtag logic reset, simulation need tck posedge to tigger
        begin
            force `ZQH_DUT.io_jtag_TCK = 0;
            repeat(10) @(posedge `ZQH_TOP.clock);
            force `ZQH_DUT.io_jtag_TCK = 1;
            repeat(10) @(posedge `ZQH_TOP.clock);
            force `ZQH_DUT.io_jtag_TCK = 0;
            repeat(10) @(posedge `ZQH_TOP.clock);
            release `ZQH_DUT.io_jtag_TCK;
        end

        //tmp force `ZQH_DUT.io_interrupts_int = 0;

        //spi flash power on
        //tmp `ZQH_TOP.spi_flash_vcc = 3000; //VCC_3V

        //i2c eeprom force less write wait time
        `ZQH_TOP.test_harness.i2c_eeprom_24xx.tWC = 500;

        //eth_phy config
        //100Mbps
        //`ZQH_TOP.test_harness.eth_phy0.control_bit14_10 = 5'b01000; // bit 13 set - speed 100
        //repeat(5) @(posedge `ZQH_TOP.clock);
        //`ZQH_TOP.test_harness.eth_phy0.control_bit8_0   = 9'h0_00;  // bit 6 reset - (10/100), bit 8 set - FD
        
        //1000Mbps
        `ifdef HAS_ETH
        //`ZQH_TOP.test_harness.eth_phy0.control_bit14_10 = 5'b00000; // bit 13
        //repeat(5) @(posedge `ZQH_TOP.clock);
        //`ZQH_TOP.test_harness.eth_phy0.control_bit8_0   = 9'h1_40;  // bit 6, bit 8 set - FD


        begin
            int eth_phy_lb = 0;
            $value$plusargs("eth_phy_lb=%d", eth_phy_lb);
            if (eth_phy_lb) begin
                force `ZQH_TOP.test_harness.dut.system.mmio_eth_mac.io_mac_phy_gmii_rx_clk = `ZQH_TOP.test_harness.dut.system.mmio_eth_mac.io_mac_phy_gmii_tx_gclk;
                force `ZQH_TOP.test_harness.dut.system.mmio_eth_mac.io_mac_phy_gmii_rx_dv = `ZQH_TOP.test_harness.dut.system.mmio_eth_mac.io_mac_phy_gmii_tx_en;
                force `ZQH_TOP.test_harness.dut.system.mmio_eth_mac.io_mac_phy_gmii_rx_err = `ZQH_TOP.test_harness.dut.system.mmio_eth_mac.io_mac_phy_gmii_tx_err;
                force `ZQH_TOP.test_harness.dut.system.mmio_eth_mac.io_mac_phy_gmii_rx_d = `ZQH_TOP.test_harness.dut.system.mmio_eth_mac.io_mac_phy_gmii_tx_d;
            end
        end
        `endif


        #(`RESET_DELAY/2);
        `ZQH_TOP.reset_n = 0;
        #(`RESET_DELAY/2);
        `ZQH_TOP.reset_n = 1;
        repeat(5) @(posedge `ZQH_TOP.clock);
        //$asserton(0, `ZQH_TOP);
        m_reset_state = 2;
    endtask

    task config_dut();
        m_config_dut_state = 1;
        //tmp fork
        //tmp     `ZQH_TOP.test_harness.eth_phy0.preamble_suppresed(0);  // avoid block
        //tmp join_none
        //change to this style
        `ifdef HAS_ETH
        `ZQH_TOP.test_harness.eth_phy0.no_preamble = 0;
        //no need `ZQH_TOP.test_harness.eth_phy0.md_transfer_cnt_reset = 1;
        repeat(5) @(posedge `ZQH_TOP.clock);
        //no need `ZQH_TOP.test_harness.eth_phy0.md_transfer_cnt_reset = 0;
        `endif

    endtask

    task start();
        m_start_state = 1;
        fork
            //while(1) begin
            //    repeat(100) @(posedge `ZQH_TOP.clock);
            //    force `ZQH_DUT.dmemAccessWrapper.dcache.tlb.io_resp_miss = 1;
            //    repeat(100) @(posedge `ZQH_TOP.clock);
            //    force `ZQH_DUT.dmemAccessWrapper.dcache.tlb.io_resp_miss = 0;
            //end
            //begin
            //  repeat(20500) @(posedge `ZQH_TOP.clock);
            //  force `ZQH_DUT.dmemAccessWrapper.dcache.dma_req_valid = 1;
            //  repeat(10000) @(posedge `ZQH_TOP.clock);
            //  force `ZQH_DUT.dmemAccessWrapper.dcache.dma_req_valid = 0;
            //end
    
            //interrupt
            //begin
            //    repeat(70000) @(posedge `ZQH_TOP.clock);
            //    `ZQH_TOP.test_harness.int_if.cb.io_int[0] <= 1;
            //    //`ZQH_TOP.test_harness.int_if.cb.io_int[1] <= 1;
            //    repeat(100) @(posedge `ZQH_TOP.clock);
            //    `ZQH_TOP.test_harness.int_if.cb.io_int[0] <= 0;
            //    //`ZQH_TOP.test_harness.int_if.cb.io_int[1] <= 0;
            //end
    
            //check load/store address misalign exception
            //begin
            //    repeat(70000) @(posedge `ZQH_TOP.clock);
            //    force top.test_harness.DUT.tile.core_wrap_0.core.io_lsu_req_bits_addr[0] = 1;
            //    @(posedge `ZQH_TOP.clock);
            //    release top.test_harness.DUT.tile.core_wrap_0.core.io_lsu_req_bits_addr[0];
            //end
    
            //icache exception
            //begin
            //    repeat(5000) @(posedge `ZQH_TOP.clock);
            //    force `ZQH_DUT.tile_0.core.ibuf.io_inst_0_bits_xcpt0_pf_inst = 1;
            //    repeat(1) @(posedge `ZQH_TOP.clock);
            //    release `ZQH_DUT.tile_0.core.ibuf.io_inst_0_bits_xcpt0_pf_inst;
            //end
    
            //icache memory error
            //while(1) begin
            //    @(negedge `ZQH_TOP.clock);
            //    if (`ZQH_DUT0.frontend.icache.s1_valid_o === 1) begin
            //        force `ZQH_DUT0.frontend.icache.s1_tag_disparity_0 = 1;
            //        force `ZQH_DUT0.frontend.icache.s1_tag_disparity_1 = 1;
            //        force `ZQH_DUT0.frontend.icache.s1_tag_disparity_2 = 1;
            //        force `ZQH_DUT0.frontend.icache.s1_tag_disparity_3 = 1;
            //        @(negedge `ZQH_TOP.clock);
            //        release `ZQH_DUT0.frontend.icache.s1_tag_disparity_0;
            //        release `ZQH_DUT0.frontend.icache.s1_tag_disparity_1;
            //        release `ZQH_DUT0.frontend.icache.s1_tag_disparity_2;
            //        release `ZQH_DUT0.frontend.icache.s1_tag_disparity_3;
            //    end
            //    repeat(100) @(posedge `ZQH_TOP.clock);
            //end
    
            //icache tl_error
            //begin
            //    repeat(14000) @(posedge `ZQH_TOP.clock);
            //    while(1) begin
            //        @(negedge `ZQH_TOP.clock);
            //        if (`ZQH_DUT.tile_0.frontend.io_tl_to_extern_out_frontend_master_d_valid === 1) begin
            //            force `ZQH_DUT.tile_0.frontend.io_tl_to_extern_out_frontend_master_d_bits_corrupt = 1;
            //            repeat(8) @(negedge `ZQH_TOP.clock);
            //            release `ZQH_DUT.tile_0.frontend.io_tl_to_extern_out_frontend_master_d_bits_corrupt;
            //            break;
            //        end
            //    end
            //end
    
            //dcache memory error
            //begin
            //    repeat(1000) @(posedge `ZQH_TOP.clock);
            //    while(1) begin
            //        @(negedge `ZQH_TOP.clock);
            //        if (`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_0_en === 1) begin
            //            //force `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_0_i = 1;
            //            //force `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_1_i = 1;
            //            //force `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_2_i = 1;
            //            //force `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_3_i = 1;
            //            @(negedge `ZQH_TOP.clock);
            //            //release `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_0_i;
            //            //release `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_1_i;
            //            //release `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_2_i;
            //            //release `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.s2_meta_correctable_errors_3_i;
            //        end
            //        repeat(10) @(posedge `ZQH_TOP.clock);
            //    end
            //end
    
            //dcache tag memory ecc error insert
            //begin
            //    static bit force_v;
            //    repeat(1000) @(posedge `ZQH_TOP.clock);
            //    while(1) begin
            //        @(negedge `ZQH_TOP.clock);
            //        if ((`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.tag_array.io_en === 1) &&
            //            (`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.tag_array.io_wmode === 0)) begin
            //            @(negedge `ZQH_TOP.clock);
            //            force_v = ~`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.tag_array.io_rdata[0];
            //            force `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.tag_array.io_rdata[0] = force_v;
            //            @(negedge `ZQH_TOP.clock);
            //            release `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.tag_array.io_rdata[0];
            //        end
            //        repeat(10) @(posedge `ZQH_TOP.clock);
            //    end
            //end
    
            //dcache data memory ecc error insert
            //begin
            //    static bit force_v;
            //    repeat(1000) @(posedge `ZQH_TOP.clock);
            //    while(1) begin
            //        @(negedge `ZQH_TOP.clock);
            //        if ((`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.data.data_arrays_0.io_en === 1) &&
            //            (`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.data.data_arrays_0.io_wmode === 0)) begin
            //            @(negedge `ZQH_TOP.clock);
            //            force_v = ~`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.data.data_arrays_0.io_rdata[0];
            //            force `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.data.data_arrays_0.io_rdata[0] = force_v;
            //            @(negedge `ZQH_TOP.clock);
            //            release `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.data.data_arrays_0.io_rdata[0];
            //        end
            //        repeat(10) @(posedge `ZQH_TOP.clock);
            //    end
            //end
    
            //new data scratchpad data memory ecc error insert
            //begin
            //    static bit force_v = 0;
            //    repeat(1000) @(posedge `ZQH_TOP.clock);
            //    while(1) begin
            //        @(negedge `ZQH_TOP.clock);
            //        if ((`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.data_scratchpad.data_arrays.io_en === 1) &&
            //            (`ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.data_scratchpad.data_arrays.io_wmode === 0)) begin
            //            fork
            //                begin
            //                    @(negedge `ZQH_TOP.clock);
            //                    std::randomize(force_v) with {
            //                        force_v dist {
            //                            0 :/ 50,
            //                            1 :/ 50
            //                        };
            //                    };
            //                    force `ZQH_DUT0.dmemAccessWrapper.dcacheWithScratchpad.data_scratchpad.data_arrays.io_rdata[0] = force_v;
            //                    @(negedge `ZQH_TOP.clock);
            //                end
            //            join_none
            //        end
            //        //repeat(5) @(posedge `ZQH_TOP.clock);
            //    end
            //end
            
            //tmp force dcache a output
            //begin
            //    int wait_8 = 0;
            //    repeat(3000) @(posedge `ZQH_TOP.clock);
            //    #0.1ns;
            //    force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.io_tl_to_dcache_out_extern_master_a_ready = 1;
            //    for (int i = 0; i < 8; i++) begin
            //        repeat(0) @(posedge `ZQH_TOP.clock);
            //        force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_valid = 1;
            //        force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_bits_opcode = 0;
            //        force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_bits_param = 0;
            //        if (i < 2) begin
            //            force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_bits_size = 6;
            //            wait_8 = 1;
            //        end
            //        else if (i < 3) begin
            //            force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_bits_size = 2;
            //            wait_8 = 0;
            //        end
            //        else begin
            //            force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_bits_size = 6;
            //            wait_8 = 1;
            //        end
            //        force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_bits_address = 32'h6000_0000;
            //        force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_bits_mask = 8'hff;
            //        if (wait_8) begin
            //            repeat(8) @(posedge `ZQH_TOP.clock);
            //        end
            //        else begin
            //            repeat(1) @(posedge `ZQH_TOP.clock);
            //        end
            //        #0.1ns;
            //        force top.DUT0.tile_0.dmemAccessWrapper.dcacheWithScratchpad.tl_out_a_valid = 0;
            //    end
            //end
    
            //force dcache uncacheable
            //begin
            //    force top.test_harness.DUT.tile_0.dmemAccessWrapper.dcache.tlb.io_resp_cacheable = 0;
            //end
    
            //i2c other master arbitrition with this master
    //tmp        begin
    //tmp            repeat(8672.5 - 777 - 1000) @(posedge `ZQH_TOP.clock);
    //tmp
    //tmp            //start
    //tmp            repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp            #0.1;
    //tmp            force top.test_harness.io_i2c_sda = 0;
    //tmp            repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp            #0.1;
    //tmp            force top.test_harness.io_i2c_scl = 0;
    //tmp
    //tmp            repeat(3000) @(posedge `ZQH_TOP.clock);
    //tmp
    //tmp            //stop
    //tmp            repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp            #0.1;
    //tmp            release top.test_harness.io_i2c_scl;
    //tmp            repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp            #0.1;
    //tmp            release top.test_harness.io_i2c_sda;
    //tmp
    //tmp            repeat(650) @(posedge `ZQH_TOP.clock);
    //tmp
    //tmp
    //tmp            //start
    //tmp            repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp            #0.1;
    //tmp            force top.test_harness.io_i2c_sda = 0;
    //tmp            repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp            #0.1;
    //tmp            force top.test_harness.io_i2c_scl = 0;
    //tmp
    //tmp            release top.test_harness.io_i2c_sda;
    //tmp            //repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp            //#0.1;
    //tmp            //release top.test_harness.io_i2c_scl;
    //tmp
    //tmp            //trigger master's scl_sync
    //tmp            for (int i = 0; i < 9; i++) begin
    //tmp                repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp                #0.1;
    //tmp                release top.test_harness.io_i2c_scl;
    //tmp                repeat(192) @(posedge `ZQH_TOP.clock);
    //tmp                #0.1;
    //tmp                force top.test_harness.io_i2c_scl = 0;
    //tmp            end
    //tmp
    //tmp
    //tmp        end
     
                //test ifu's itim and tl fetch access cross
                //begin
                //    static bit hit_tim = 0;
                //    force top.test_harness.DUT.tile.core_wrap_0.ifu.hit_itim = hit_tim;
                //    while(1) begin
                //        repeat(1) @(posedge `ZQH_TOP.clock);
                //        std::randomize(hit_tim);
                //    end
                //end
    
    
                //test zqh_core_e1_ifu's uncache able fetch
                //begin
                //    while(1) begin
                //        force top.test_harness.DUT.tile.core_wrap_0.ifu.fetch_addr_cacheable_s0 = 0;
                //        repeat(1) @(posedge `ZQH_TOP.clock);
                //        release top.test_harness.DUT.tile.core_wrap_0.ifu.fetch_addr_cacheable_s0;
                //        repeat(1) @(posedge `ZQH_TOP.clock);
                //    end
                //end
    
                //icache tag ecc insert
                //begin
                //    int which_bit = 0;
                //    bit do_force;
                //    static bit[111:0] bit_v;
                //    while(1) begin
                //        repeat(1) @(negedge `ZQH_TOP.clock);
                //        std::randomize(which_bit) with {
                //            which_bit >=0;
                //            which_bit <= 111;
                //        };
                //        bit_v = top.test_harness.DUT.tile.core_wrap_0.ifu.tag_array.io_rdata;
                //        std::randomize(do_force);
                //        if (do_force) begin
                //            bit_v[which_bit] = ~bit_v[which_bit];
                //            force top.test_harness.DUT.tile.core_wrap_0.ifu.tag_array.io_rdata = bit_v;
                //            repeat(1) @(negedge `ZQH_TOP.clock);
                //            release top.test_harness.DUT.tile.core_wrap_0.ifu.tag_array.io_rdata;
                //        end
                //    end
                //end
    
                //icache data ecc insert
                //begin
                //    int which_bit = 0;
                //    bit do_force;
                //    static bit[311:0] bit_v;
                //    while(1) begin
                //        repeat(1) @(negedge `ZQH_TOP.clock);
                //        std::randomize(which_bit) with {
                //            which_bit >=0;
                //            which_bit <= 311;
                //        };
                //        bit_v = top.test_harness.DUT.tile.core_wrap_0.ifu.data_array.io_rdata[311:0];
                //        std::randomize(do_force);
                //        if (do_force) begin
                //            bit_v[which_bit] = ~bit_v[which_bit];
                //            force top.test_harness.DUT.tile.core_wrap_0.ifu.data_array.io_rdata = bit_v;
                //            repeat(1) @(negedge `ZQH_TOP.clock);
                //            release top.test_harness.DUT.tile.core_wrap_0.ifu.data_array.io_rdata;
                //        end
                //    end
                //end
    
                //ifu fetch's d_resp has error, need trigger exception
                //begin
                //    repeat(50000) @(negedge `ZQH_TOP.clock);
                //    while(1) begin
                //        repeat(1) @(negedge `ZQH_TOP.clock);
                //        if (top.test_harness.DUT.tile.core_wrap_0.ifu.io_tl_to_extern_out_ifu_master_d_valid === 1) begin
                //            force top.test_harness.DUT.tile.core_wrap_0.ifu.io_tl_to_extern_out_ifu_master_d_bits_corrupt = 1;
                //            repeat(10) @(negedge `ZQH_TOP.clock);
                //            release top.test_harness.DUT.tile.core_wrap_0.ifu.io_tl_to_extern_out_ifu_master_d_bits_corrupt;
                //            break;
                //        end
                //    end
                //end
    
                ////mac_phy's cs/cd
                //begin
                //    //repeat(18107 - reset_time) @(negedge `ZQH_TOP.clock);
                //    //repeat(24067 - reset_time) @(negedge `ZQH_TOP.clock);
                //    //repeat(25187 - reset_time) @(negedge `ZQH_TOP.clock);
                //    //force top.test_harness.dut.io_mac_phy_mii_cscd_cs = 1;
                //    force top.test_harness.dut.io_mac_phy_mii_cscd_cd = 1;
    
                //    //repeat(1000) @(negedge `ZQH_TOP.clock);
                //    repeat(94987) @(negedge `ZQH_TOP.clock);
                //    //release top.test_harness.dut.io_mac_phy_mii_cscd_cs;
                //    release top.test_harness.dut.io_mac_phy_mii_cscd_cd;
                //end
    
                //
                //mac rx packet
                begin
                    bit[31:0] phy_tx_mem_addr = 0;
    
                    //mac_phy_collision(1);//set collision
    
                    //phy recieve mac's tx data and store into it's tx_mem
                    `ifdef HAS_ETH
                    `ZQH_TOP.test_harness.eth_phy0.set_tx_mem_addr(phy_tx_mem_addr);
                    `endif
    
                    //repeat(1333416) @(negedge `ZQH_TOP.clock); //after tx
                    #1215734.75ns;
                    //repeat(20127 - reset_time) @(negedge `ZQH_TOP.clock); //before tx, tx will be defer/collision
                    //repeat(20907 - reset_time) @(negedge `ZQH_TOP.clock); //before tx, tx will be defer/collision
    
                    //prepare phy's data
                    begin
                        for (int pkt_idx = 0; pkt_idx < 0; pkt_idx++) begin
                        //while(1) begin
                            int rx_len = 64;
                            int plus_drible_nibble = 0;
                            bit drop = 1;
                            bit[7:0] phy_data_q[$];
                            //bit[47:0] dest_addr = 48'h000102030405;//unicast
                            //bit[47:0] dest_addr = 48'h000102030406;//invalid unicast
                            //bit[47:0] dest_addr = 48'hffffffffffff;//broadcast
                            //bit[47:0] dest_addr = 48'h010203040506;//multicast and none pause frame
                            bit[47:0] dest_addr = 48'h0180C2000001;//multicast and pause frame
                            bit[47:0] source_addr = 48'h00ffffffffff;
    
                            //bit[15:0] type_len = 16'h0800;//ip
                            bit[15:0] type_len = 16'h8808;//pause
                            bit[15:0] pause_code = 16'h0001;
                            bit[15:0] pause_para = 16'h000f;
                            for (int i = 0; i < rx_len; i++) begin
                                if (i < 6) begin
                                    phy_data_q.push_back(dest_addr[(5 - i)*8 +: 8]);
                                end
                                else if (i < 12) begin
                                    phy_data_q.push_back(source_addr[(5 - (i - 6))*8 +: 8]);
                                end
                                else if (i < 14) begin
                                    phy_data_q.push_back(type_len[(1 - (i - 12))*8 +: 8]);
                                end
                                else if ((type_len == 16'h8808) && (i < 16)) begin
                                    phy_data_q.push_back(pause_code[(1 - (i - 14))*8 +: 8]);
                                end
                                else if ((type_len == 16'h8808) && (i < 18)) begin
                                    phy_data_q.push_back(pause_para[(1 - (i - 16))*8 +: 8]);
                                end
                                else begin
                                    phy_data_q.push_back(i);
                                end
                            end
                            mac_phy_set_rx_packet(50, phy_data_q, 1);
                            //foreach(phy_data_q[i]) begin
                            //    $display("phy_data_q[%0d] = %h", i, phy_data_q[i]);
                            //end
    
                            //mac_phy_rx_err(1);//set rx_err
                            //mac_phy_collision(1);//set collision
    
                            drop = 1;
                            phy_data_q.delete();
                            while(drop) begin
                                mac_phy_send_rx_packet(
                                    64'h0055_5555_5555_5555,
                                    4'h7,
                                    8'hD5,
                                    50,
                                    rx_len,
                                    plus_drible_nibble,
                                    drop);
                            end
    
                            //mac_phy_carrier_sense(1);//set carrer_sense
                        end
                    end
                end
    
        join_none
        m_start_state = 2;
    endtask

    task run();
        int done;
        done = 0;
        m_run_state = 1;
        while(done == 0) begin
            if (`ZQH_TOP.time_out) begin
                $display("*** FAILED ***%s after %0d simulation cycles", `ZQH_TOP.reason, `ZQH_TOP.trace_count);
                //break;
                done = 1;
            end

            if ((((`ZQH_TOP.fails[0] === 1) && m_hart_on[0]) || !m_hart_on[0]) &&
                (((`ZQH_TOP.fails[1] === 1) && m_hart_on[1]) || !m_hart_on[1]) &&
                (((`ZQH_TOP.fails[2] === 1) && m_hart_on[2]) || !m_hart_on[2]) &&
                (((`ZQH_TOP.fails[3] === 1) && m_hart_on[3]) || !m_hart_on[3])) begin
                $display("*** FAILED ***%s after %0d simulation cycles", "sw_tc", `ZQH_TOP.trace_count);
                //break;
                done = 1;
            end
  
            if ((((`ZQH_TOP.success[0] === 1) && m_hart_on[0]) || !m_hart_on[0]) &&
                (((`ZQH_TOP.success[1] === 1) && m_hart_on[1]) || !m_hart_on[1]) &&
                (((`ZQH_TOP.success[2] === 1) && m_hart_on[2]) || !m_hart_on[2]) &&
                (((`ZQH_TOP.success[3] === 1) && m_hart_on[3]) || !m_hart_on[3])) begin
                $display("Completed after %0d simulation cycles", `ZQH_TOP.trace_count);
                //break;
                done = 1;
            end
            @(posedge `ZQH_TOP.clock);
        end
        m_run_state = 2;
    endtask

    task clean_up();
        m_clean_up_state = 1;
        ;
        m_clean_up_state = 2;
    endtask

    task report();
        m_report_state = 1;
        log.report();
        $finish();
        m_report_state = 2;
    endtask


    task mac_phy_send_rx_packet(
        bit[(8*8)-1:0] preamble_data,
        bit[3:0] preamble_len,
        bit[7:0] sfd_data,
        bit[31:0] start_addr,
        bit[31:0] len,
        bit plus_drible_nibble,
        output bit drop);
    
        `ifdef HAS_ETH
        bit collision;
        bit phy_send_done;
    
        collision = 0;
        phy_send_done = 0;
    
        //half duplex mode need wait carier sence
        if (`ZQH_TOP.test_harness.eth_phy0.control_bit8_0[8] == 0) begin
            wait(`ZQH_TOP.test_harness.eth_phy0.mcrs_o == 0);
        end
        fork
            begin
                `ZQH_TOP.test_harness.eth_phy0.send_rx_packet(preamble_data, preamble_len, sfd_data, start_addr, len, plus_drible_nibble);
                phy_send_done = 1;
            end
    
            //check if colicollision happen at half duplex mode
            while((`ZQH_TOP.test_harness.eth_phy0.control_bit8_0[8] == 0) & ((collision == 0) | (phy_send_done == 1))) begin
                if (`ZQH_TOP.test_harness.eth_phy0.mcoll_o) begin
                    collision = 1;
                    $display("collision happen, should retry");
                    //break;
                end
                if (phy_send_done) begin
                    //break;
                end
                repeat(1) @(`ZQH_TOP.test_harness.eth_phy0.mrx_clk_o);
            end
        join
    
        //wait ipg
        repeat(50) @(`ZQH_TOP.test_harness.eth_phy0.mrx_clk_o);
    
        drop = collision;
        `endif
    endtask
    
    task mac_phy_rx_err(bit data);
        `ifdef HAS_ETH
        `ZQH_TOP.test_harness.eth_phy0.rx_err(data);
        `endif
    endtask
    
    task mac_phy_carrier_sense(bit data);
        `ifdef HAS_ETH
        `ZQH_TOP.test_harness.eth_phy0.carrier_sense(data);
        `endif
    endtask
    
    task mac_phy_collision(bit data);
        `ifdef HAS_ETH
        `ZQH_TOP.test_harness.eth_phy0.collision(data);
        `endif
    endtask
    
    task mac_phy_set_rx_packet(bit[31:0] start_addr, bit[7:0] data_q[$], bit do_crc);
        `ifdef HAS_ETH
        bit[31:0] crc;
        crc = 32'hffffffff;
        for (int i = 0; i < data_q.size() - 4; i++) begin
            `ZQH_TOP.test_harness.eth_phy0.rx_mem[start_addr + i] = data_q[i];
            crc = mac_fcs_crc_8b(crc, data_q[i]);
        end
    
        //last 4 byte is fcs
        crc = mac_fcs_crc_last_fix(crc);
        for (int i = 0; i < 4; i++) begin
            if (do_crc) begin
                data_q[data_q.size() - 4 + i] = crc[i*8 +: 8];
                `ZQH_TOP.test_harness.eth_phy0.rx_mem[start_addr + data_q.size() - 4 + i] = crc[i*8 +: 8];
            end
            else begin
                `ZQH_TOP.test_harness.eth_phy0.rx_mem[start_addr + data_q.size() - 4 + i] = data_q[data_q.size() - 4 + i];
            end
        end
        `endif
    endtask
    
    function bit[31:0] mac_fcs_crc_last_fix(bit[31:0] crc);
        bit[31:0] crc_tmp;
        bit[31:0] crc_last;
        crc_tmp = ~crc;
        for (int i = 0; i < 32; i++) begin
            crc_last[i] = crc_tmp[31 - i];
        end
        return crc_last;
    endfunction
    
    function bit[31:0] mac_fcs_crc_8b(bit[31:0] init_v, bit[7:0] din);
        bit[32:0] crc_poly;
        bit[7:0] din_refin;
        crc_poly = 33'h104c11db7;
        for (int i = 0; i < 8; i++) begin
            din_refin[i] = din[7 - i];
        end
        return crc32_8b(init_v, din_refin, crc_poly);
    endfunction
    
    
    function bit[31:0] crc32_8b(bit[31:0] data_old, bit[7:0] data_new, bit[32:0] poly);
        bit[31:0] crc_tmp;
        crc_tmp = data_old;
        for (int i = 0; i < 8; i++) begin
            crc_tmp = {crc_tmp[30 : 0], 1'b0} ^ ({32{crc_tmp[31] ^ data_new[7 - i]}} & poly[31:0]);
        end
        return crc_tmp;
    endfunction
endmodule
