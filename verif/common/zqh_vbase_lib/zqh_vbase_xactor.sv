//zqh_vbase_xactor base class

class zqh_vbase_xactor;
    string m_class_name = "";
    string m_inst_name = "";
    int m_id = 0;
    extern function new(string inst_name = "", int id = 0);
    extern virtual task start();
    extern virtual task report();
endclass

function zqh_vbase_xactor::new(string inst_name = "", int id = 0);
    m_class_name = "zqh_vbase_xactor";
    m_inst_name = inst_name;
    m_id = id;
endfunction

task zqh_vbase_xactor::start();
endtask

task zqh_vbase_xactor::report();
endtask
