
function bit[12:0] zqh_vbase_ecc_encode8(bit[7:0] a);
    bit [12:0] b; //@ main_zqh.py:855
    bit [1:0] _T_1; //@ ecc.py:186
    bit [12:0] _T_2; //@ ecc.py:187
    bit [11:0] _T_3; //@ ecc.py:134
    bit [7:0] _T_4; //@ ecc.py:147
    bit [7:0] _T_5; //@ ecc.py:147
    bit  _T_6; //@ ecc.py:147
    bit  _T_7; //@ ecc.py:147
    bit [11:0] _T_8; //@ ecc.py:134
    bit [7:0] _T_9; //@ ecc.py:147
    bit [7:0] _T_10; //@ ecc.py:147
    bit  _T_11; //@ ecc.py:147
    bit  _T_12; //@ ecc.py:147
    bit [11:0] _T_13; //@ ecc.py:134
    bit [7:0] _T_14; //@ ecc.py:147
    bit [7:0] _T_15; //@ ecc.py:147
    bit  _T_16; //@ ecc.py:147
    bit  _T_17; //@ ecc.py:147
    bit [11:0] _T_18; //@ ecc.py:134
    bit [7:0] _T_19; //@ ecc.py:147
    bit [7:0] _T_20; //@ ecc.py:147
    bit  _T_21; //@ ecc.py:147
    bit  _T_22; //@ ecc.py:147
    bit [1:0] _T_23; //@ ecc.py:147
    bit [2:0] _T_24; //@ ecc.py:147
    bit [3:0] _T_25; //@ ecc.py:147
    bit [11:0] _T_26; //@ ecc.py:148
    bit  _T_27; //@ ecc.py:76
    bit  _T_28; //@ ecc.py:76
    bit [12:0] _T_29; //@ ecc.py:76
    bit [12:0] _T_30; //@ ecc.py:188
    _T_1 = {1'h0, 1'h0}; //@ ecc.py:186
    _T_2 = (_T_1 << 4'hb); //@ ecc.py:187
    _T_3 = 12'h15b; //@ ecc.py:134
    _T_4 = _T_3[7:0]; //@ ecc.py:147
    _T_5 = (_T_4 & a); //@ ecc.py:147
    _T_6 = ^_T_5; //@ ecc.py:147
    _T_7 = (_T_6 ^ 1'h0); //@ ecc.py:147
    _T_8 = 12'h26d; //@ ecc.py:134
    _T_9 = _T_8[7:0]; //@ ecc.py:147
    _T_10 = (_T_9 & a); //@ ecc.py:147
    _T_11 = ^_T_10; //@ ecc.py:147
    _T_12 = (_T_11 ^ 1'h0); //@ ecc.py:147
    _T_13 = 12'h48e; //@ ecc.py:134
    _T_14 = _T_13[7:0]; //@ ecc.py:147
    _T_15 = (_T_14 & a); //@ ecc.py:147
    _T_16 = ^_T_15; //@ ecc.py:147
    _T_17 = (_T_16 ^ 1'h0); //@ ecc.py:147
    _T_18 = 12'h8f0; //@ ecc.py:134
    _T_19 = _T_18[7:0]; //@ ecc.py:147
    _T_20 = (_T_19 & a); //@ ecc.py:147
    _T_21 = ^_T_20; //@ ecc.py:147
    _T_22 = (_T_21 ^ 1'h0); //@ ecc.py:147
    _T_23 = {_T_22, _T_17}; //@ ecc.py:147
    _T_24 = {_T_23, _T_12}; //@ ecc.py:147
    _T_25 = {_T_24, _T_7}; //@ ecc.py:147
    _T_26 = {_T_25, a}; //@ ecc.py:148
    _T_27 = ^_T_26; //@ ecc.py:76
    _T_28 = (_T_27 ^ 1'h0); //@ ecc.py:76
    _T_29 = {_T_28, _T_26}; //@ ecc.py:76
    _T_30 = (_T_29 ^ _T_2); //@ ecc.py:188
    b = _T_30; //@ main_zqh.py:857

    return b;
endfunction 

function bit[21:0] zqh_vbase_ecc_encode16(bit[15:0] a);
    bit [21:0] b; //@ main_zqh.py:855
    bit [1:0] _T_1; //@ ecc.py:186
    bit [21:0] _T_2; //@ ecc.py:187
    bit [20:0] _T_3; //@ ecc.py:134
    bit [15:0] _T_4; //@ ecc.py:147
    bit [15:0] _T_5; //@ ecc.py:147
    bit  _T_6; //@ ecc.py:147
    bit  _T_7; //@ ecc.py:147
    bit [20:0] _T_8; //@ ecc.py:134
    bit [15:0] _T_9; //@ ecc.py:147
    bit [15:0] _T_10; //@ ecc.py:147
    bit  _T_11; //@ ecc.py:147
    bit  _T_12; //@ ecc.py:147
    bit [20:0] _T_13; //@ ecc.py:134
    bit [15:0] _T_14; //@ ecc.py:147
    bit [15:0] _T_15; //@ ecc.py:147
    bit  _T_16; //@ ecc.py:147
    bit  _T_17; //@ ecc.py:147
    bit [20:0] _T_18; //@ ecc.py:134
    bit [15:0] _T_19; //@ ecc.py:147
    bit [15:0] _T_20; //@ ecc.py:147
    bit  _T_21; //@ ecc.py:147
    bit  _T_22; //@ ecc.py:147
    bit [20:0] _T_23; //@ ecc.py:134
    bit [15:0] _T_24; //@ ecc.py:147
    bit [15:0] _T_25; //@ ecc.py:147
    bit  _T_26; //@ ecc.py:147
    bit  _T_27; //@ ecc.py:147
    bit [1:0] _T_28; //@ ecc.py:147
    bit [2:0] _T_29; //@ ecc.py:147
    bit [3:0] _T_30; //@ ecc.py:147
    bit [4:0] _T_31; //@ ecc.py:147
    bit [20:0] _T_32; //@ ecc.py:148
    bit  _T_33; //@ ecc.py:76
    bit  _T_34; //@ ecc.py:76
    bit [21:0] _T_35; //@ ecc.py:76
    bit [21:0] _T_36; //@ ecc.py:188
    _T_1 = {1'h0, 1'h0}; //@ ecc.py:186
    _T_2 = (_T_1 << 5'h14); //@ ecc.py:187
    _T_3 = 21'h1ad5b; //@ ecc.py:134
    _T_4 = _T_3[15:0]; //@ ecc.py:147
    _T_5 = (_T_4 & a); //@ ecc.py:147
    _T_6 = ^_T_5; //@ ecc.py:147
    _T_7 = (_T_6 ^ 1'h0); //@ ecc.py:147
    _T_8 = 21'h2366d; //@ ecc.py:134
    _T_9 = _T_8[15:0]; //@ ecc.py:147
    _T_10 = (_T_9 & a); //@ ecc.py:147
    _T_11 = ^_T_10; //@ ecc.py:147
    _T_12 = (_T_11 ^ 1'h0); //@ ecc.py:147
    _T_13 = 21'h4c78e; //@ ecc.py:134
    _T_14 = _T_13[15:0]; //@ ecc.py:147
    _T_15 = (_T_14 & a); //@ ecc.py:147
    _T_16 = ^_T_15; //@ ecc.py:147
    _T_17 = (_T_16 ^ 1'h0); //@ ecc.py:147
    _T_18 = 21'h807f0; //@ ecc.py:134
    _T_19 = _T_18[15:0]; //@ ecc.py:147
    _T_20 = (_T_19 & a); //@ ecc.py:147
    _T_21 = ^_T_20; //@ ecc.py:147
    _T_22 = (_T_21 ^ 1'h0); //@ ecc.py:147
    _T_23 = 21'h10f800; //@ ecc.py:134
    _T_24 = _T_23[15:0]; //@ ecc.py:147
    _T_25 = (_T_24 & a); //@ ecc.py:147
    _T_26 = ^_T_25; //@ ecc.py:147
    _T_27 = (_T_26 ^ 1'h0); //@ ecc.py:147
    _T_28 = {_T_27, _T_22}; //@ ecc.py:147
    _T_29 = {_T_28, _T_17}; //@ ecc.py:147
    _T_30 = {_T_29, _T_12}; //@ ecc.py:147
    _T_31 = {_T_30, _T_7}; //@ ecc.py:147
    _T_32 = {_T_31, a}; //@ ecc.py:148
    _T_33 = ^_T_32; //@ ecc.py:76
    _T_34 = (_T_33 ^ 1'h0); //@ ecc.py:76
    _T_35 = {_T_34, _T_32}; //@ ecc.py:76
    _T_36 = (_T_35 ^ _T_2); //@ ecc.py:188
    b = _T_36; //@ main_zqh.py:857

    return b;
endfunction

function bit[38:0] zqh_vbase_ecc_encode32(bit[31:0] a);
    bit [38:0] b; //@ main_zqh.py:855
    bit [1:0] _T_1; //@ ecc.py:186
    bit [38:0] _T_2; //@ ecc.py:187
    bit [37:0] _T_3; //@ ecc.py:134
    bit [31:0] _T_4; //@ ecc.py:147
    bit [31:0] _T_5; //@ ecc.py:147
    bit  _T_6; //@ ecc.py:147
    bit  _T_7; //@ ecc.py:147
    bit [37:0] _T_8; //@ ecc.py:134
    bit [31:0] _T_9; //@ ecc.py:147
    bit [31:0] _T_10; //@ ecc.py:147
    bit  _T_11; //@ ecc.py:147
    bit  _T_12; //@ ecc.py:147
    bit [37:0] _T_13; //@ ecc.py:134
    bit [31:0] _T_14; //@ ecc.py:147
    bit [31:0] _T_15; //@ ecc.py:147
    bit  _T_16; //@ ecc.py:147
    bit  _T_17; //@ ecc.py:147
    bit [37:0] _T_18; //@ ecc.py:134
    bit [31:0] _T_19; //@ ecc.py:147
    bit [31:0] _T_20; //@ ecc.py:147
    bit  _T_21; //@ ecc.py:147
    bit  _T_22; //@ ecc.py:147
    bit [37:0] _T_23; //@ ecc.py:134
    bit [31:0] _T_24; //@ ecc.py:147
    bit [31:0] _T_25; //@ ecc.py:147
    bit  _T_26; //@ ecc.py:147
    bit  _T_27; //@ ecc.py:147
    bit [37:0] _T_28; //@ ecc.py:134
    bit [31:0] _T_29; //@ ecc.py:147
    bit [31:0] _T_30; //@ ecc.py:147
    bit  _T_31; //@ ecc.py:147
    bit  _T_32; //@ ecc.py:147
    bit [1:0] _T_33; //@ ecc.py:147
    bit [2:0] _T_34; //@ ecc.py:147
    bit [3:0] _T_35; //@ ecc.py:147
    bit [4:0] _T_36; //@ ecc.py:147
    bit [5:0] _T_37; //@ ecc.py:147
    bit [37:0] _T_38; //@ ecc.py:148
    bit  _T_39; //@ ecc.py:76
    bit  _T_40; //@ ecc.py:76
    bit [38:0] _T_41; //@ ecc.py:76
    bit [38:0] _T_42; //@ ecc.py:188
    _T_1 = {1'h0, 1'h0}; //@ ecc.py:186
    _T_2 = (_T_1 << 6'h25); //@ ecc.py:187
    _T_3 = 38'h156aaad5b; //@ ecc.py:134
    _T_4 = _T_3[31:0]; //@ ecc.py:147
    _T_5 = (_T_4 & a); //@ ecc.py:147
    _T_6 = ^_T_5; //@ ecc.py:147
    _T_7 = (_T_6 ^ 1'h0); //@ ecc.py:147
    _T_8 = 38'h29b33366d; //@ ecc.py:134
    _T_9 = _T_8[31:0]; //@ ecc.py:147
    _T_10 = (_T_9 & a); //@ ecc.py:147
    _T_11 = ^_T_10; //@ ecc.py:147
    _T_12 = (_T_11 ^ 1'h0); //@ ecc.py:147
    _T_13 = 38'h4e3c3c78e; //@ ecc.py:134
    _T_14 = _T_13[31:0]; //@ ecc.py:147
    _T_15 = (_T_14 & a); //@ ecc.py:147
    _T_16 = ^_T_15; //@ ecc.py:147
    _T_17 = (_T_16 ^ 1'h0); //@ ecc.py:147
    _T_18 = 38'h803fc07f0; //@ ecc.py:134
    _T_19 = _T_18[31:0]; //@ ecc.py:147
    _T_20 = (_T_19 & a); //@ ecc.py:147
    _T_21 = ^_T_20; //@ ecc.py:147
    _T_22 = (_T_21 ^ 1'h0); //@ ecc.py:147
    _T_23 = 38'h1003fff800; //@ ecc.py:134
    _T_24 = _T_23[31:0]; //@ ecc.py:147
    _T_25 = (_T_24 & a); //@ ecc.py:147
    _T_26 = ^_T_25; //@ ecc.py:147
    _T_27 = (_T_26 ^ 1'h0); //@ ecc.py:147
    _T_28 = 38'h20fc000000; //@ ecc.py:134
    _T_29 = _T_28[31:0]; //@ ecc.py:147
    _T_30 = (_T_29 & a); //@ ecc.py:147
    _T_31 = ^_T_30; //@ ecc.py:147
    _T_32 = (_T_31 ^ 1'h0); //@ ecc.py:147
    _T_33 = {_T_32, _T_27}; //@ ecc.py:147
    _T_34 = {_T_33, _T_22}; //@ ecc.py:147
    _T_35 = {_T_34, _T_17}; //@ ecc.py:147
    _T_36 = {_T_35, _T_12}; //@ ecc.py:147
    _T_37 = {_T_36, _T_7}; //@ ecc.py:147
    _T_38 = {_T_37, a}; //@ ecc.py:148
    _T_39 = ^_T_38; //@ ecc.py:76
    _T_40 = (_T_39 ^ 1'h0); //@ ecc.py:76
    _T_41 = {_T_40, _T_38}; //@ ecc.py:76
    _T_42 = (_T_41 ^ _T_2); //@ ecc.py:188
    b = _T_42; //@ main_zqh.py:857

    return b;
endfunction

function bit[71:0] zqh_vbase_ecc_encode64(bit[63:0] a);
    bit [71:0] b; //@ main_zqh.py:855
    bit [1:0] _T_1; //@ ecc.py:186
    bit [71:0] _T_2; //@ ecc.py:187
    bit [70:0] _T_3; //@ ecc.py:134
    bit [63:0] _T_4; //@ ecc.py:147
    bit [63:0] _T_5; //@ ecc.py:147
    bit  _T_6; //@ ecc.py:147
    bit  _T_7; //@ ecc.py:147
    bit [70:0] _T_8; //@ ecc.py:134
    bit [63:0] _T_9; //@ ecc.py:147
    bit [63:0] _T_10; //@ ecc.py:147
    bit  _T_11; //@ ecc.py:147
    bit  _T_12; //@ ecc.py:147
    bit [70:0] _T_13; //@ ecc.py:134
    bit [63:0] _T_14; //@ ecc.py:147
    bit [63:0] _T_15; //@ ecc.py:147
    bit  _T_16; //@ ecc.py:147
    bit  _T_17; //@ ecc.py:147
    bit [70:0] _T_18; //@ ecc.py:134
    bit [63:0] _T_19; //@ ecc.py:147
    bit [63:0] _T_20; //@ ecc.py:147
    bit  _T_21; //@ ecc.py:147
    bit  _T_22; //@ ecc.py:147
    bit [70:0] _T_23; //@ ecc.py:134
    bit [63:0] _T_24; //@ ecc.py:147
    bit [63:0] _T_25; //@ ecc.py:147
    bit  _T_26; //@ ecc.py:147
    bit  _T_27; //@ ecc.py:147
    bit [70:0] _T_28; //@ ecc.py:134
    bit [63:0] _T_29; //@ ecc.py:147
    bit [63:0] _T_30; //@ ecc.py:147
    bit  _T_31; //@ ecc.py:147
    bit  _T_32; //@ ecc.py:147
    bit [70:0] _T_33; //@ ecc.py:134
    bit [63:0] _T_34; //@ ecc.py:147
    bit [63:0] _T_35; //@ ecc.py:147
    bit  _T_36; //@ ecc.py:147
    bit  _T_37; //@ ecc.py:147
    bit [1:0] _T_38; //@ ecc.py:147
    bit [2:0] _T_39; //@ ecc.py:147
    bit [3:0] _T_40; //@ ecc.py:147
    bit [4:0] _T_41; //@ ecc.py:147
    bit [5:0] _T_42; //@ ecc.py:147
    bit [6:0] _T_43; //@ ecc.py:147
    bit [70:0] _T_44; //@ ecc.py:148
    bit  _T_45; //@ ecc.py:76
    bit  _T_46; //@ ecc.py:76
    bit [71:0] _T_47; //@ ecc.py:76
    bit [71:0] _T_48; //@ ecc.py:188
    _T_1 = {1'h0, 1'h0}; //@ ecc.py:186
    _T_2 = (_T_1 << 7'h46); //@ ecc.py:187
    _T_3 = 71'h1ab55555556aaad5b; //@ ecc.py:134
    _T_4 = _T_3[63:0]; //@ ecc.py:147
    _T_5 = (_T_4 & a); //@ ecc.py:147
    _T_6 = ^_T_5; //@ ecc.py:147
    _T_7 = (_T_6 ^ 1'h0); //@ ecc.py:147
    _T_8 = 71'h2cd9999999b33366d; //@ ecc.py:134
    _T_9 = _T_8[63:0]; //@ ecc.py:147
    _T_10 = (_T_9 & a); //@ ecc.py:147
    _T_11 = ^_T_10; //@ ecc.py:147
    _T_12 = (_T_11 ^ 1'h0); //@ ecc.py:147
    _T_13 = 71'h4f1e1e1e1e3c3c78e; //@ ecc.py:134
    _T_14 = _T_13[63:0]; //@ ecc.py:147
    _T_15 = (_T_14 & a); //@ ecc.py:147
    _T_16 = ^_T_15; //@ ecc.py:147
    _T_17 = (_T_16 ^ 1'h0); //@ ecc.py:147
    _T_18 = 71'h801fe01fe03fc07f0; //@ ecc.py:134
    _T_19 = _T_18[63:0]; //@ ecc.py:147
    _T_20 = (_T_19 & a); //@ ecc.py:147
    _T_21 = ^_T_20; //@ ecc.py:147
    _T_22 = (_T_21 ^ 1'h0); //@ ecc.py:147
    _T_23 = 71'h1001fffe0003fff800; //@ ecc.py:134
    _T_24 = _T_23[63:0]; //@ ecc.py:147
    _T_25 = (_T_24 & a); //@ ecc.py:147
    _T_26 = ^_T_25; //@ ecc.py:147
    _T_27 = (_T_26 ^ 1'h0); //@ ecc.py:147
    _T_28 = 71'h2001fffffffc000000; //@ ecc.py:134
    _T_29 = _T_28[63:0]; //@ ecc.py:147
    _T_30 = (_T_29 & a); //@ ecc.py:147
    _T_31 = ^_T_30; //@ ecc.py:147
    _T_32 = (_T_31 ^ 1'h0); //@ ecc.py:147
    _T_33 = 71'h40fe00000000000000; //@ ecc.py:134
    _T_34 = _T_33[63:0]; //@ ecc.py:147
    _T_35 = (_T_34 & a); //@ ecc.py:147
    _T_36 = ^_T_35; //@ ecc.py:147
    _T_37 = (_T_36 ^ 1'h0); //@ ecc.py:147
    _T_38 = {_T_37, _T_32}; //@ ecc.py:147
    _T_39 = {_T_38, _T_27}; //@ ecc.py:147
    _T_40 = {_T_39, _T_22}; //@ ecc.py:147
    _T_41 = {_T_40, _T_17}; //@ ecc.py:147
    _T_42 = {_T_41, _T_12}; //@ ecc.py:147
    _T_43 = {_T_42, _T_7}; //@ ecc.py:147
    _T_44 = {_T_43, a}; //@ ecc.py:148
    _T_45 = ^_T_44; //@ ecc.py:76
    _T_46 = (_T_45 ^ 1'h0); //@ ecc.py:76
    _T_47 = {_T_46, _T_44}; //@ ecc.py:76
    _T_48 = (_T_47 ^ _T_2); //@ ecc.py:188
    b = _T_48; //@ main_zqh.py:857

    return b;
endfunction
