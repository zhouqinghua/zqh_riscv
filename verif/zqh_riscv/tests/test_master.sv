//`timescale 1ns/1ps
module test_master();
    zqh_vbase_log log;
    zqh_riscv_env env();
    zqh_riscv_sanity_test zqh_riscv_sanity_test();
    string test_name;

    initial begin
        log = new("test_master");
        $value$plusargs("zqh_test=%s", test_name);
        if (test_name == zqh_riscv_sanity_test.name) begin
            zqh_riscv_sanity_test.run_test();
        end
        else begin
            `zqh_vbase_error(log, $display("unknow test: ", test_name));
            log.report();
            $finish();
        end
    end
endmodule
