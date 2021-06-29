//zqh_vbase_test base class

class zqh_vbase_test;
    string m_class_name = "";
    string m_inst_name = "";
    zqh_vbase_log log;
    zqh_vbase_env m_base_env;
    string m_cpu_instr_init_file;
    string m_cpu_data_init_file;
    extern function new(string inst_name = "", zqh_vbase_env env);
    extern virtual task build();
    extern virtual task config_test();
    extern virtual task reset();
    extern virtual task config_dut();
    extern virtual task start();
    extern virtual task run();
    extern virtual task clean_up();
    extern virtual task report();

    extern virtual task run_test();
    extern virtual function void get_cpu_init_file();
endclass

function zqh_vbase_test::new(string inst_name = "", zqh_vbase_env env);
    m_class_name = "zqh_vbase_test";
    m_inst_name = inst_name;
    log = new(inst_name);
    m_base_env = env;
endfunction

task zqh_vbase_test::build();
endtask

task zqh_vbase_test::config_test();
    get_cpu_init_file();
endtask

task zqh_vbase_test::reset();
endtask

task zqh_vbase_test::config_dut();
endtask

task zqh_vbase_test::start();
endtask

task zqh_vbase_test::run();
endtask

task zqh_vbase_test::clean_up();
endtask

task zqh_vbase_test::report();
    log.report();
endtask

task zqh_vbase_test::run_test();
    m_base_env.build();
    build();

    m_base_env.config_test();
    config_test();

    m_base_env.reset();
    reset();

    m_base_env.config_dut();
    config_dut();

    m_base_env.start();
    start();

    m_base_env.run();
    run();

    m_base_env.clean_up();
    clean_up();

    #0.1;
    m_base_env.report();
    report();

endtask

function void zqh_vbase_test::get_cpu_init_file();
    if (!$value$plusargs("zqh_cpu_instr_init_file=%s",m_cpu_instr_init_file)) begin
        `zqh_vbase_error(log,$psprintf("m_cpu_instr_init_file get fail."));
    end
    else begin
        `zqh_vbase_note(log,$psprintf("m_cpu_instr_init_file is:%s",m_cpu_instr_init_file));
    end
    if (!$value$plusargs("zqh_cpu_data_init_file=%s",m_cpu_data_init_file)) begin
        `zqh_vbase_error(log,$psprintf("m_cpu_data_init_file get fail."));
    end
    else begin
        `zqh_vbase_note(log,$psprintf("m_cpu_data_init_file is:%s",m_cpu_data_init_file));
    end
endfunction
