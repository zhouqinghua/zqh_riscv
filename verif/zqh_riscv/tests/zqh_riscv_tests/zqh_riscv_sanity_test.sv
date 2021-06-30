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
    endtask
endmodule
