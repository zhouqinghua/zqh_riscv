//zqh_vbase_cfg base class

class zqh_vbase_cfg;
    string m_class_name = "";
    string m_inst_name = "";
    extern function new(string inst_name = "");
    extern virtual task gen_cfg();
    extern virtual task do_cfg();
    extern virtual task report();
endclass

function zqh_vbase_cfg::new(string inst_name = "");
    m_class_name = "zqh_vbase_cfg";
    m_inst_name = inst_name;
endfunction

task zqh_vbase_cfg::gen_cfg();
endtask

task zqh_vbase_cfg::do_cfg();
endtask

task zqh_vbase_cfg::report();
endtask

