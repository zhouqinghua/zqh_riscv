//zqh_lib_common.sv

//zqh_data use macro
//{{{
//function copy macro
`define ZQH_LIB_MEMBER_COPY_START_1ST(CLASS) \
    CLASS local_to; \
    if (to == null) begin \
        local_to = new(); \
        $cast(to,local_to); \
        $cast(copy,local_to); \
    end \
    else begin \
        $cast(local_to,to); \
        $cast(copy,local_to); \
    end
`define ZQH_LIB_MEMBER_COPY_START(CLASS) \
    `ZQH_LIB_MEMBER_COPY_START_1ST(CLASS) \
    void'(super.copy(to));
`define ZQH_LIB_MEMBER_COPY(MEMBER) \
    local_to.MEMBER = this.MEMBER;
`define ZQH_LIB_MEMBER_COPY_ARRAY(MEMBER) \
    foreach(MEMBER[i]) begin \
        local_to.MEMBER[i] = this.MEMBER[i]; \
    end

//function data2str macro
`define ZQH_LIB_MEMBER_DATA2STR_START \
    data2str = super.data2str(pre_fix);
`define ZQH_LIB_MEMBER_DATA2STR_SCALAR(MEMBER) \
    data2str = $psprintf(`"%s%s``MEMBER = 'h%h`",data2str,pre_fix,MEMBER); \
    data2str = $psprintf("%s\n",data2str);
`define ZQH_LIB_MEMBER_DATA2STR_ENUM(MEMBER) \
    data2str = $psprintf(`"%s%s``MEMBER = %s`",data2str,pre_fix,MEMBER.name()); \
    data2str = $psprintf("%s\n",data2str);
`define ZQH_LIB_MEMBER_DATA2STR_STRING(MEMBER) \
    data2str = $psprintf(`"%s%s``MEMBER = %s`",data2str,pre_fix,MEMBER); \
    data2str = $psprintf("%s\n",data2str);
`define ZQH_LIB_MEMBER_DATA2STR_SCALAR_ARRAY(MEMBER) \
    foreach(MEMBER[i]) begin \
        data2str = $psprintf(`"%s%s``MEMBER[%0d] = 'h%h`",data2str,pre_fix,i,MEMBER[i]); \
        data2str = $psprintf("%s\n",data2str); \
    end
`define ZQH_LIB_MEMBER_DATA2STR_ENUM_ARRAY(MEMBER) \
    foreach(MEMBER[i]) begin \
        data2str = $psprintf(`"%s%s``MEMBER[%0d] = %s`",data2str,pre_fix,i,MEMBER[i].name()); \
        data2str = $psprintf("%s\n",data2str); \
    end

//function compare macro
`define ZQH_LIB_MEMBER_COMPARE_START(CLASS) \
    CLASS local_to; \
    compare = 1; \
    info = ""; \
    $cast(local_to, to); \
    compare = super.compare(to,info);
`define ZQH_LIB_MEMBER_COMPARE(MEMBER) \
    if (this.MEMBER != local_to.MEMBER) begin \
        compare = 0; \
        info = $psprintf(`"%sobs.MEMBER('h%h) != exp.MEMBER('h%h)`",info,this.MEMBER,local_to.MEMBER); \
        info = $psprintf("%s\n",info); \
    end
`define ZQH_LIB_MEMBER_COMPARE_ARRAY(MEMBER) \
    foreach(MEMBER[i]) begin \
        if (this.MEMBER[i] != local_to.MEMBER[i]) begin \
            compare = 0; \
            info = $psprintf(`"%sobs.MEMBER[%0d]('h%h) != exp.MEMBER[%0d]('h%h)`",info,i,this.MEMBER[i],i,local_to.MEMBER[i]); \
            info = $psprintf("%s\n",info); \
        end \
    end
//}}}
