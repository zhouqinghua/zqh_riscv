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
//tmp                begin
//tmp                    bit[31:0] phy_tx_mem_addr = 0;
//tmp    
//tmp                    //mac_phy_collision(1);//set collision
//tmp    
//tmp                    //phy recieve mac's tx data and store into it's tx_mem
//tmp                    `ifdef HAS_ETH
//tmp                    `ZQH_TOP.test_harness.eth_phy0.set_tx_mem_addr(phy_tx_mem_addr);
//tmp                    `endif
//tmp    
//tmp                    //repeat(1333416) @(negedge `ZQH_TOP.clock); //after tx
//tmp                    #1215734.75ns;
//tmp                    //repeat(20127 - reset_time) @(negedge `ZQH_TOP.clock); //before tx, tx will be defer/collision
//tmp                    //repeat(20907 - reset_time) @(negedge `ZQH_TOP.clock); //before tx, tx will be defer/collision
//tmp    
//tmp                    //prepare phy's data
//tmp                    begin
//tmp                        for (int pkt_idx = 0; pkt_idx < 0; pkt_idx++) begin
//tmp                        //while(1) begin
//tmp                            int rx_len = 64;
//tmp                            int plus_drible_nibble = 0;
//tmp                            bit drop = 1;
//tmp                            bit[7:0] phy_data_q[$];
//tmp                            //bit[47:0] dest_addr = 48'h000102030405;//unicast
//tmp                            //bit[47:0] dest_addr = 48'h000102030406;//invalid unicast
//tmp                            //bit[47:0] dest_addr = 48'hffffffffffff;//broadcast
//tmp                            //bit[47:0] dest_addr = 48'h010203040506;//multicast and none pause frame
//tmp                            bit[47:0] dest_addr = 48'h0180C2000001;//multicast and pause frame
//tmp                            bit[47:0] source_addr = 48'h00ffffffffff;
//tmp    
//tmp                            //bit[15:0] type_len = 16'h0800;//ip
//tmp                            bit[15:0] type_len = 16'h8808;//pause
//tmp                            bit[15:0] pause_code = 16'h0001;
//tmp                            bit[15:0] pause_para = 16'h000f;
//tmp                            for (int i = 0; i < rx_len; i++) begin
//tmp                                if (i < 6) begin
//tmp                                    phy_data_q.push_back(dest_addr[(5 - i)*8 +: 8]);
//tmp                                end
//tmp                                else if (i < 12) begin
//tmp                                    phy_data_q.push_back(source_addr[(5 - (i - 6))*8 +: 8]);
//tmp                                end
//tmp                                else if (i < 14) begin
//tmp                                    phy_data_q.push_back(type_len[(1 - (i - 12))*8 +: 8]);
//tmp                                end
//tmp                                else if ((type_len == 16'h8808) && (i < 16)) begin
//tmp                                    phy_data_q.push_back(pause_code[(1 - (i - 14))*8 +: 8]);
//tmp                                end
//tmp                                else if ((type_len == 16'h8808) && (i < 18)) begin
//tmp                                    phy_data_q.push_back(pause_para[(1 - (i - 16))*8 +: 8]);
//tmp                                end
//tmp                                else begin
//tmp                                    phy_data_q.push_back(i);
//tmp                                end
//tmp                            end
//tmp                            mac_phy_set_rx_packet(50, phy_data_q, 1);
//tmp                            //foreach(phy_data_q[i]) begin
//tmp                            //    $display("phy_data_q[%0d] = %h", i, phy_data_q[i]);
//tmp                            //end
//tmp    
//tmp                            //mac_phy_rx_err(1);//set rx_err
//tmp                            //mac_phy_collision(1);//set collision
//tmp    
//tmp                            drop = 1;
//tmp                            phy_data_q.delete();
//tmp                            while(drop) begin
//tmp                                mac_phy_send_rx_packet(
//tmp                                    64'h0055_5555_5555_5555,
//tmp                                    4'h7,
//tmp                                    8'hD5,
//tmp                                    50,
//tmp                                    rx_len,
//tmp                                    plus_drible_nibble,
//tmp                                    drop);
//tmp                            end
//tmp    
//tmp                            //mac_phy_carrier_sense(1);//set carrer_sense
//tmp                        end
//tmp                    end
//tmp                end
    
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
