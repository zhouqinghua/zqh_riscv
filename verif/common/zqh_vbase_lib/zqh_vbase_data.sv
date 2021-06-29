//zqh_vbase_data base class

class zqh_vbase_data;
    int m_stream_id = 0; //used to track different data stream
    string m_class_name = ""; //classs name

    extern function new();
    extern virtual function int pack(int mode = 0);
    extern virtual function int unpack(int mode = 0);
    extern virtual function string psdisplay(string pre_fix = "");
    extern virtual function string data2str(string pre_fix = "");
    extern virtual function zqh_vbase_data copy(zqh_vbase_data to = null);
    extern virtual function int compare(zqh_vbase_data to, ref string info);

    extern virtual function string data2str_pre(string pre_fix = "");
    extern virtual function string data2str_post(string pre_fix = "");
endclass

function zqh_vbase_data::new();
    m_class_name = "zqh_vbase_data";
endfunction

function int zqh_vbase_data::pack(int mode = 0);
    return 0;
endfunction

function int zqh_vbase_data::unpack(int mode = 0);
    return 0;
endfunction

function string zqh_vbase_data::psdisplay(string pre_fix = "");
    psdisplay = data2str_pre(pre_fix);
    psdisplay = {psdisplay,data2str(pre_fix)};
    psdisplay = {psdisplay,data2str_post(pre_fix)};
endfunction

function string zqh_vbase_data::data2str(string pre_fix = "");
    `ZQH_LIB_MEMBER_DATA2STR_STRING(m_class_name)
    `ZQH_LIB_MEMBER_DATA2STR_SCALAR(m_stream_id)
endfunction

function string zqh_vbase_data::data2str_pre(string pre_fix = "");
    data2str_pre = $psprintf("%s%s member:\n",pre_fix, m_class_name);
endfunction

function string zqh_vbase_data::data2str_post(string pre_fix = "");
    data2str_post = $psprintf("%s%s member end",pre_fix, m_class_name);
endfunction

function zqh_vbase_data zqh_vbase_data::copy(zqh_vbase_data to = null);
    `ZQH_LIB_MEMBER_COPY_START_1ST(zqh_vbase_data)
    `ZQH_LIB_MEMBER_COPY(m_stream_id)
    `ZQH_LIB_MEMBER_COPY(m_class_name)
endfunction

function int zqh_vbase_data::compare(zqh_vbase_data to, ref string info);
    return 1;
endfunction
