//zqh print log common class

class zqh_vbase_log;
    string m_inst_name = "log";
    string m_print_str;
    static int m_error_num = 0;
    static int m_warning_num = 0;
    static int m_debug_level = 0;

    function new(string inst = "log");
        m_inst_name = inst;
    endfunction:new
    
    function void set_debug_level();
        string str;
        if ($value$plusargs("zqh_debug_level=%s",str)) begin
            if (str == "DEBUG") begin
                m_debug_level = 0;
            end
            else if (str == "NOTE") begin
                m_debug_level = 1;
            end
            else if (str == "WARNING") begin
                m_debug_level = 2;
            end
            else if (str == "ERROR") begin
                m_debug_level = 3;
            end
        end
    endfunction
    
    function void log_print(string pre_fix = "", string str = "", string file = "", int line = 0, int level = 0);
        if (level >= m_debug_level) begin
            string tmp;
            $sformat(tmp, "%s@%t: %s :%s,%s,%0d", pre_fix, $realtime, str, m_inst_name, file, line);
            m_print_str = tmp;
            $display(m_print_str);
        end
        if (pre_fix == "#WARNING#") begin
            m_warning_num++;
        end
    
        if (pre_fix == "!ERROR!") begin
            m_error_num++;
        end
        //$fdisplay(fh, m_print_str);
    endfunction:log_print
    
    function void report(int mode = 0);
        string pass_word;
        if (m_error_num == 0) begin
            pass_word = "SIMULATION pass: ";
        end
        else begin
            pass_word = "SIMULATION fail: ";
        end
        $display("%serror num = %0d, waring num = %0d. use time = %t.",pass_word, m_error_num, m_warning_num, $realtime);
    endfunction
endclass:zqh_vbase_log

//normal style
//`define zqh_vbase_debug(log,str) log.log_print("-DEBUG-", str,`__FILE__,`__LINE__, 0)
//`define zqh_vbase_note(log,str) log.log_print("*NOTE*", str,`__FILE__,`__LINE__, 1)
//`define zqh_vbase_warning(log,str) log.log_print("#WARNING#", str,`__FILE__,`__LINE__, 2)
//`define zqh_vbase_error(log,str) log.log_print("!ERROR!", str,`__FILE__,`__LINE__, 3)

//iverilog style: sformat could not use
`define zqh_vbase_log_action(log, pre_fix, action, level) \
    if (log.m_debug_level <= level) begin \
        $write("%s@%t: ", pre_fix, $realtime); \
        action; \
        $display(":%s,%s,%0d", log.m_inst_name, `__FILE__, `__LINE__); \
    end
`define zqh_vbase_debug(log, action) `zqh_vbase_log_action(log, "-DEBUG-", action, 0)
`define zqh_vbase_note(log, action) `zqh_vbase_log_action(log, "*NOTE*", action, 1)
`define zqh_vbase_warning(log, action) `zqh_vbase_log_action(log, "#WARNING#", action, 2)
`define zqh_vbase_error(log, action) `zqh_vbase_log_action(log, "!ERROR!", action, 3)
