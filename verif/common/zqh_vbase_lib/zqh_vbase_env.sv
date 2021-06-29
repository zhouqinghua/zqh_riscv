//zqh_vbase_env base class

class zqh_vbase_env;
    string m_class_name = "";
    string m_inst_name = "";
    extern function new(string inst_name = "");
    extern virtual task build();
    extern virtual task config_test();
    extern virtual task reset();
    extern virtual task config_dut();
    extern virtual task start();
    extern virtual task run();
    extern virtual task clean_up();
    extern virtual task report();
endclass

function zqh_vbase_env::new(string inst_name = "");
    m_class_name = "zqh_vbase_env";
    m_inst_name = inst_name;
    zqh_vbase_log::set_debug_level();
endfunction

task zqh_vbase_env::build();
endtask

task zqh_vbase_env::config_test();
endtask

task zqh_vbase_env::reset();
endtask

task zqh_vbase_env::config_dut();
endtask

task zqh_vbase_env::start();
endtask

task zqh_vbase_env::run();
endtask

task zqh_vbase_env::clean_up();
endtask

task zqh_vbase_env::report();
endtask

