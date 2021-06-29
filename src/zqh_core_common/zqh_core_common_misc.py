import sys
import os
from phgl_imp import *

class zqh_core_common_instr_consts(object):
    def __init__(self):
        self.opcode_w = 5
        self.rd_w = 5
        self.rs1_w = 5
        self.rs2_w = 5
        self.rs3_w = 5
        self.funct3_w = 3
        self.funct7_w = 7
        self.fence_succ_w = 4
        self.fence_pred_w = 4

        self.opcode_map = {
            'opcode_load'     : value(0b00000 , w = self.opcode_w),
            'opcode_store'    : value(0b01000 , w = self.opcode_w),
            'opcode_madd'     : value(0b10000 , w = self.opcode_w),
            'opcode_branch'   : value(0b11000 , w = self.opcode_w),
            'opcode_load_fp'  : value(0b00001 , w = self.opcode_w),
            'opcode_store_fp' : value(0b01001 , w = self.opcode_w),
            'opcode_msub'     : value(0b10001 , w = self.opcode_w),
            'opcode_jalr'     : value(0b11001 , w = self.opcode_w),
            'opcode_custom0'  : value(0b00010 , w = self.opcode_w),
            'opcode_custom1'  : value(0b01010 , w = self.opcode_w),
            'opcode_nmsub'    : value(0b10010 , w = self.opcode_w),
            'opcode_mem'      : value(0b00011 , w = self.opcode_w),
            'opcode_amo'      : value(0b01011 , w = self.opcode_w),
            'opcode_nmadd'    : value(0b10011 , w = self.opcode_w),
            'opcode_jal'      : value(0b11011 , w = self.opcode_w),
            'opcode_op_imm'   : value(0b00100 , w = self.opcode_w),
            'opcode_op'       : value(0b01100 , w = self.opcode_w),
            'opcode_op_fp'    : value(0b10100 , w = self.opcode_w),
            'opcode_system'   : value(0b11100 , w = self.opcode_w),
            'opcode_auipc'    : value(0b00101 , w = self.opcode_w),
            'opcode_lui'      : value(0b01101 , w = self.opcode_w),
            'opcode_op_imm32' : value(0b00110 , w = self.opcode_w),
            'opcode_op32'     : value(0b01110 , w = self.opcode_w),
            'opcode_custom2'  : value(0b10110 , w = self.opcode_w),
            'opcode_custom3'  : value(0b11110 , w = self.opcode_w)
        }

    def BEQ               (self):
        return bit_pat("b?????????????????000?????1100011")
    def BNE               (self):
        return bit_pat("b?????????????????001?????1100011")
    def BLT               (self):
        return bit_pat("b?????????????????100?????1100011")
    def BGE               (self):
        return bit_pat("b?????????????????101?????1100011")
    def BLTU              (self):
        return bit_pat("b?????????????????110?????1100011")
    def BGEU              (self):
        return bit_pat("b?????????????????111?????1100011")
    def JALR              (self):
        return bit_pat("b?????????????????000?????1100111")
    def JAL               (self):
        return bit_pat("b?????????????????????????1101111")
    def LUI               (self):
        return bit_pat("b?????????????????????????0110111")
    def AUIPC             (self):
        return bit_pat("b?????????????????????????0010111")
    def ADDI              (self):
        return bit_pat("b?????????????????000?????0010011")
    def SLLI              (self):
        return bit_pat("b000000???????????001?????0010011")
    def SLTI              (self):
        return bit_pat("b?????????????????010?????0010011")
    def SLTIU             (self):
        return bit_pat("b?????????????????011?????0010011")
    def XORI              (self):
        return bit_pat("b?????????????????100?????0010011")
    def SRLI              (self):
        return bit_pat("b000000???????????101?????0010011")
    def SRAI              (self):
        return bit_pat("b010000???????????101?????0010011")
    def ORI               (self):
        return bit_pat("b?????????????????110?????0010011")
    def ANDI              (self):
        return bit_pat("b?????????????????111?????0010011")
    def ADD               (self):
        return bit_pat("b0000000??????????000?????0110011")
    def SUB               (self):
        return bit_pat("b0100000??????????000?????0110011")
    def SLL               (self):
        return bit_pat("b0000000??????????001?????0110011")
    def SLT               (self):
        return bit_pat("b0000000??????????010?????0110011")
    def SLTU              (self):
        return bit_pat("b0000000??????????011?????0110011")
    def XOR               (self):
        return bit_pat("b0000000??????????100?????0110011")
    def SRL               (self):
        return bit_pat("b0000000??????????101?????0110011")
    def SRA               (self):
        return bit_pat("b0100000??????????101?????0110011")
    def OR                (self):
        return bit_pat("b0000000??????????110?????0110011")
    def AND               (self):
        return bit_pat("b0000000??????????111?????0110011")
    def ADDIW             (self):
        return bit_pat("b?????????????????000?????0011011")
    def SLLIW             (self):
        return bit_pat("b0000000??????????001?????0011011")
    def SRLIW             (self):
        return bit_pat("b0000000??????????101?????0011011")
    def SRAIW             (self):
        return bit_pat("b0100000??????????101?????0011011")
    def ADDW              (self):
        return bit_pat("b0000000??????????000?????0111011")
    def SUBW              (self):
        return bit_pat("b0100000??????????000?????0111011")
    def SLLW              (self):
        return bit_pat("b0000000??????????001?????0111011")
    def SRLW              (self):
        return bit_pat("b0000000??????????101?????0111011")
    def SRAW              (self):
        return bit_pat("b0100000??????????101?????0111011")
    def LB                (self):
        return bit_pat("b?????????????????000?????0000011")
    def LH                (self):
        return bit_pat("b?????????????????001?????0000011")
    def LW                (self):
        return bit_pat("b?????????????????010?????0000011")
    def LD                (self):
        return bit_pat("b?????????????????011?????0000011")
    def LBU               (self):
        return bit_pat("b?????????????????100?????0000011")
    def LHU               (self):
        return bit_pat("b?????????????????101?????0000011")
    def LWU               (self):
        return bit_pat("b?????????????????110?????0000011")
    def SB                (self):
        return bit_pat("b?????????????????000?????0100011")
    def SH                (self):
        return bit_pat("b?????????????????001?????0100011")
    def SW                (self):
        return bit_pat("b?????????????????010?????0100011")
    def SD                (self):
        return bit_pat("b?????????????????011?????0100011")
    def FENCE             (self):
        return bit_pat("b?????????????????000?????0001111")
    def FENCE_I           (self):
        return bit_pat("b?????????????????001?????0001111")
    def MUL               (self):
        return bit_pat("b0000001??????????000?????0110011")
    def MULH              (self):
        return bit_pat("b0000001??????????001?????0110011")
    def MULHSU            (self):
        return bit_pat("b0000001??????????010?????0110011")
    def MULHU             (self):
        return bit_pat("b0000001??????????011?????0110011")
    def DIV               (self):
        return bit_pat("b0000001??????????100?????0110011")
    def DIVU              (self):
        return bit_pat("b0000001??????????101?????0110011")
    def REM               (self):
        return bit_pat("b0000001??????????110?????0110011")
    def REMU              (self):
        return bit_pat("b0000001??????????111?????0110011")
    def MULW              (self):
        return bit_pat("b0000001??????????000?????0111011")
    def DIVW              (self):
        return bit_pat("b0000001??????????100?????0111011")
    def DIVUW             (self):
        return bit_pat("b0000001??????????101?????0111011")
    def REMW              (self):
        return bit_pat("b0000001??????????110?????0111011")
    def REMUW             (self):
        return bit_pat("b0000001??????????111?????0111011")
    def AMOADD_W          (self):
        return bit_pat("b00000????????????010?????0101111")
    def AMOXOR_W          (self):
        return bit_pat("b00100????????????010?????0101111")
    def AMOOR_W           (self):
        return bit_pat("b01000????????????010?????0101111")
    def AMOAND_W          (self):
        return bit_pat("b01100????????????010?????0101111")
    def AMOMIN_W          (self):
        return bit_pat("b10000????????????010?????0101111")
    def AMOMAX_W          (self):
        return bit_pat("b10100????????????010?????0101111")
    def AMOMINU_W         (self):
        return bit_pat("b11000????????????010?????0101111")
    def AMOMAXU_W         (self):
        return bit_pat("b11100????????????010?????0101111")
    def AMOSWAP_W         (self):
        return bit_pat("b00001????????????010?????0101111")
    def LR_W              (self):
        return bit_pat("b00010??00000?????010?????0101111")
    def SC_W              (self):
        return bit_pat("b00011????????????010?????0101111")
    def AMOADD_D          (self):
        return bit_pat("b00000????????????011?????0101111")
    def AMOXOR_D          (self):
        return bit_pat("b00100????????????011?????0101111")
    def AMOOR_D           (self):
        return bit_pat("b01000????????????011?????0101111")
    def AMOAND_D          (self):
        return bit_pat("b01100????????????011?????0101111")
    def AMOMIN_D          (self):
        return bit_pat("b10000????????????011?????0101111")
    def AMOMAX_D          (self):
        return bit_pat("b10100????????????011?????0101111")
    def AMOMINU_D         (self):
        return bit_pat("b11000????????????011?????0101111")
    def AMOMAXU_D         (self):
        return bit_pat("b11100????????????011?????0101111")
    def AMOSWAP_D         (self):
        return bit_pat("b00001????????????011?????0101111")
    def LR_D              (self):
        return bit_pat("b00010??00000?????011?????0101111")
    def SC_D              (self):
        return bit_pat("b00011????????????011?????0101111")
    def ECALL             (self):
        return bit_pat("b00000000000000000000000001110011")
    def EBREAK            (self):
        return bit_pat("b00000000000100000000000001110011")
    def URET              (self):
        return bit_pat("b00000000001000000000000001110011")
    def SRET              (self):
        return bit_pat("b00010000001000000000000001110011")
    def HRET              (self):
        return bit_pat("b00100000001000000000000001110011")
    def MRET              (self):
        return bit_pat("b00110000001000000000000001110011")
    def DRET              (self):
        return bit_pat("b01111011001000000000000001110011")
    def SFENCE_VMA        (self):
        return bit_pat("b0001001??????????000000001110011")
    def WFI               (self):
        return bit_pat("b00010000010100000000000001110011")
    def CSRRW             (self):
        return bit_pat("b?????????????????001?????1110011")
    def CSRRS             (self):
        return bit_pat("b?????????????????010?????1110011")
    def CSRRC             (self):
        return bit_pat("b?????????????????011?????1110011")
    def CSRRWI            (self):
        return bit_pat("b?????????????????101?????1110011")
    def CSRRSI            (self):
        return bit_pat("b?????????????????110?????1110011")
    def CSRRCI            (self):
        return bit_pat("b?????????????????111?????1110011")
    def FADD_S            (self):
        return bit_pat("b0000000??????????????????1010011")
    def FSUB_S            (self):
        return bit_pat("b0000100??????????????????1010011")
    def FMUL_S            (self):
        return bit_pat("b0001000??????????????????1010011")
    def FDIV_S            (self):
        return bit_pat("b0001100??????????????????1010011")
    def FSGNJ_S           (self):
        return bit_pat("b0010000??????????000?????1010011")
    def FSGNJN_S          (self):
        return bit_pat("b0010000??????????001?????1010011")
    def FSGNJX_S          (self):
        return bit_pat("b0010000??????????010?????1010011")
    def FMIN_S            (self):
        return bit_pat("b0010100??????????000?????1010011")
    def FMAX_S            (self):
        return bit_pat("b0010100??????????001?????1010011")
    def FSQRT_S           (self):
        return bit_pat("b010110000000?????????????1010011")
    def FADD_D            (self):
        return bit_pat("b0000001??????????????????1010011")
    def FSUB_D            (self):
        return bit_pat("b0000101??????????????????1010011")
    def FMUL_D            (self):
        return bit_pat("b0001001??????????????????1010011")
    def FDIV_D            (self):
        return bit_pat("b0001101??????????????????1010011")
    def FSGNJ_D           (self):
        return bit_pat("b0010001??????????000?????1010011")
    def FSGNJN_D          (self):
        return bit_pat("b0010001??????????001?????1010011")
    def FSGNJX_D          (self):
        return bit_pat("b0010001??????????010?????1010011")
    def FMIN_D            (self):
        return bit_pat("b0010101??????????000?????1010011")
    def FMAX_D            (self):
        return bit_pat("b0010101??????????001?????1010011")
    def FCVT_S_D          (self):
        return bit_pat("b010000000001?????????????1010011")
    def FCVT_D_S          (self):
        return bit_pat("b010000100000?????????????1010011")
    def FSQRT_D           (self):
        return bit_pat("b010110100000?????????????1010011")
    def FLE_S             (self):
        return bit_pat("b1010000??????????000?????1010011")
    def FLT_S             (self):
        return bit_pat("b1010000??????????001?????1010011")
    def FEQ_S             (self):
        return bit_pat("b1010000??????????010?????1010011")
    def FLE_D             (self):
        return bit_pat("b1010001??????????000?????1010011")
    def FLT_D             (self):
        return bit_pat("b1010001??????????001?????1010011")
    def FEQ_D             (self):
        return bit_pat("b1010001??????????010?????1010011")
    def FCVT_W_S          (self):
        return bit_pat("b110000000000?????????????1010011")
    def FCVT_WU_S         (self):
        return bit_pat("b110000000001?????????????1010011")
    def FCVT_L_S          (self):
        return bit_pat("b110000000010?????????????1010011")
    def FCVT_LU_S         (self):
        return bit_pat("b110000000011?????????????1010011")
    def FMV_X_S           (self):
        return bit_pat("b111000000000?????000?????1010011")
    def FCLASS_S          (self):
        return bit_pat("b111000000000?????001?????1010011")
    def FCVT_W_D          (self):
        return bit_pat("b110000100000?????????????1010011")
    def FCVT_WU_D         (self):
        return bit_pat("b110000100001?????????????1010011")
    def FCVT_L_D          (self):
        return bit_pat("b110000100010?????????????1010011")
    def FCVT_LU_D         (self):
        return bit_pat("b110000100011?????????????1010011")
    def FMV_X_D           (self):
        return bit_pat("b111000100000?????000?????1010011")
    def FCLASS_D          (self):
        return bit_pat("b111000100000?????001?????1010011")
    def FCVT_S_W          (self):
        return bit_pat("b110100000000?????????????1010011")
    def FCVT_S_WU         (self):
        return bit_pat("b110100000001?????????????1010011")
    def FCVT_S_L          (self):
        return bit_pat("b110100000010?????????????1010011")
    def FCVT_S_LU         (self):
        return bit_pat("b110100000011?????????????1010011")
    def FMV_S_X           (self):
        return bit_pat("b111100000000?????000?????1010011")
    def FCVT_D_W          (self):
        return bit_pat("b110100100000?????????????1010011")
    def FCVT_D_WU         (self):
        return bit_pat("b110100100001?????????????1010011")
    def FCVT_D_L          (self):
        return bit_pat("b110100100010?????????????1010011")
    def FCVT_D_LU         (self):
        return bit_pat("b110100100011?????????????1010011")
    def FMV_D_X           (self):
        return bit_pat("b111100100000?????000?????1010011")
    def FLW               (self):
        return bit_pat("b?????????????????010?????0000111")
    def FLD               (self):
        return bit_pat("b?????????????????011?????0000111")
    def FSW               (self):
        return bit_pat("b?????????????????010?????0100111")
    def FSD               (self):
        return bit_pat("b?????????????????011?????0100111")
    def FMADD_S           (self):
        return bit_pat("b?????00??????????????????1000011")
    def FMSUB_S           (self):
        return bit_pat("b?????00??????????????????1000111")
    def FNMSUB_S          (self):
        return bit_pat("b?????00??????????????????1001011")
    def FNMADD_S          (self):
        return bit_pat("b?????00??????????????????1001111")
    def FMADD_D           (self):
        return bit_pat("b?????01??????????????????1000011")
    def FMSUB_D           (self):
        return bit_pat("b?????01??????????????????1000111")
    def FNMSUB_D          (self):
        return bit_pat("b?????01??????????????????1001011")
    def FNMADD_D          (self):
        return bit_pat("b?????01??????????????????1001111")
    def C_ADDI4SPN        (self):
        return bit_pat("b????????????????000???????????00")
    def C_FLD             (self):
        return bit_pat("b????????????????001???????????00")
    def C_LW              (self):
        return bit_pat("b????????????????010???????????00")
    def C_FLW             (self):
        return bit_pat("b????????????????011???????????00")
    def C_FSD             (self):
        return bit_pat("b????????????????101???????????00")
    def C_SW              (self):
        return bit_pat("b????????????????110???????????00")
    def C_FSW             (self):
        return bit_pat("b????????????????111???????????00")
    def C_ADDI            (self):
        return bit_pat("b????????????????000???????????01")
    def C_JAL             (self):
        return bit_pat("b????????????????001???????????01")
    def C_LI              (self):
        return bit_pat("b????????????????010???????????01")
    def C_LUI             (self):
        return bit_pat("b????????????????011???????????01")
    def C_SRLI            (self):
        return bit_pat("b????????????????100?00????????01")
    def C_SRAI            (self):
        return bit_pat("b????????????????100?01????????01")
    def C_ANDI            (self):
        return bit_pat("b????????????????100?10????????01")
    def C_SUB             (self):
        return bit_pat("b????????????????100011???00???01")
    def C_XOR             (self):
        return bit_pat("b????????????????100011???01???01")
    def C_OR              (self):
        return bit_pat("b????????????????100011???10???01")
    def C_AND             (self):
        return bit_pat("b????????????????100011???11???01")
    def C_SUBW            (self):
        return bit_pat("b????????????????100111???00???01")
    def C_ADDW            (self):
        return bit_pat("b????????????????100111???01???01")
    def C_J               (self):
        return bit_pat("b????????????????101???????????01")
    def C_BEQZ            (self):
        return bit_pat("b????????????????110???????????01")
    def C_BNEZ            (self):
        return bit_pat("b????????????????111???????????01")
    def C_SLLI            (self):
        return bit_pat("b????????????????000???????????10")
    def C_FLDSP           (self):
        return bit_pat("b????????????????001???????????10")
    def C_LWSP            (self):
        return bit_pat("b????????????????010???????????10")
    def C_FLWSP           (self):
        return bit_pat("b????????????????011???????????10")
    def C_MV              (self):
        return bit_pat("b????????????????1000??????????10")
    def C_ADD             (self):
        return bit_pat("b????????????????1001??????????10")
    def C_FSDSP           (self):
        return bit_pat("b????????????????101???????????10")
    def C_SWSP            (self):
        return bit_pat("b????????????????110???????????10")
    def C_FSWSP           (self):
        return bit_pat("b????????????????111???????????10")
    def CUSTOM0           (self):
        return bit_pat("b?????????????????000?????0001011")
    def CUSTOM0_RS1       (self):
        return bit_pat("b?????????????????010?????0001011")
    def CUSTOM0_RS1_RS2   (self):
        return bit_pat("b?????????????????011?????0001011")
    def CUSTOM0_RD        (self):
        return bit_pat("b?????????????????100?????0001011")
    def CUSTOM0_RD_RS1    (self):
        return bit_pat("b?????????????????110?????0001011")
    def CUSTOM0_RD_RS1_RS2(self):
        return bit_pat("b?????????????????111?????0001011")
    def CUSTOM1           (self):
        return bit_pat("b?????????????????000?????0101011")
    def CUSTOM1_RS1       (self):
        return bit_pat("b?????????????????010?????0101011")
    def CUSTOM1_RS1_RS2   (self):
        return bit_pat("b?????????????????011?????0101011")
    def CUSTOM1_RD        (self):
        return bit_pat("b?????????????????100?????0101011")
    def CUSTOM1_RD_RS1    (self):
        return bit_pat("b?????????????????110?????0101011")
    def CUSTOM1_RD_RS1_RS2(self):
        return bit_pat("b?????????????????111?????0101011")
    def CUSTOM2           (self):
        return bit_pat("b?????????????????000?????1011011")
    def CUSTOM2_RS1       (self):
        return bit_pat("b?????????????????010?????1011011")
    def CUSTOM2_RS1_RS2   (self):
        return bit_pat("b?????????????????011?????1011011")
    def CUSTOM2_RD        (self):
        return bit_pat("b?????????????????100?????1011011")
    def CUSTOM2_RD_RS1    (self):
        return bit_pat("b?????????????????110?????1011011")
    def CUSTOM2_RD_RS1_RS2(self):
        return bit_pat("b?????????????????111?????1011011")
    def CUSTOM3           (self):
        return bit_pat("b?????????????????000?????1111011")
    def CUSTOM3_RS1       (self):
        return bit_pat("b?????????????????010?????1111011")
    def CUSTOM3_RS1_RS2   (self):
        return bit_pat("b?????????????????011?????1111011")
    def CUSTOM3_RD        (self):
        return bit_pat("b?????????????????100?????1111011")
    def CUSTOM3_RD_RS1    (self):
        return bit_pat("b?????????????????110?????1111011")
    def CUSTOM3_RD_RS1_RS2(self):
        return bit_pat("b?????????????????111?????1111011")
    def SLLI_RV32         (self):
        return bit_pat("b0000000??????????001?????0010011")
    def SRLI_RV32         (self):
        return bit_pat("b0000000??????????101?????0010011")
    def SRAI_RV32         (self):
        return bit_pat("b0100000??????????101?????0010011")
    def FRFLAGS           (self):
        return bit_pat("b00000000000100000010?????1110011")
    def FSFLAGS           (self):
        return bit_pat("b000000000001?????001?????1110011")
    def FSFLAGSI          (self):
        return bit_pat("b000000000001?????101?????1110011")
    def FRRM              (self):
        return bit_pat("b00000000001000000010?????1110011")
    def FSRM              (self):
        return bit_pat("b000000000010?????001?????1110011")
    def FSRMI             (self):
        return bit_pat("b000000000010?????101?????1110011")
    def FSCSR             (self):
        return bit_pat("b000000000011?????001?????1110011")
    def FRCSR             (self):
        return bit_pat("b00000000001100000010?????1110011")
    def RDCYCLE           (self):
        return bit_pat("b11000000000000000010?????1110011")
    def RDTIME            (self):
        return bit_pat("b11000000000100000010?????1110011")
    def RDINSTRET         (self):
        return bit_pat("b11000000001000000010?????1110011")
    def RDCYCLEH          (self):
        return bit_pat("b11001000000000000010?????1110011")
    def RDTIMEH           (self):
        return bit_pat("b11001000000100000010?????1110011")
    def RDINSTRETH        (self):
        return bit_pat("b11001000001000000010?????1110011")
    def SCALL             (self):
        return bit_pat("b00000000000000000000000001110011")
    def SBREAK            (self):
        return bit_pat("b00000000000100000000000001110011")
I_CONSTS = zqh_core_common_instr_consts()

class zqh_core_common_decode_consts(object):
    def __init__(self):
        self.SZ_MT = 3
        self.SZ_BR = 3
        self.SZ_DW = 1
        self.SZ_SEL_ALU1 = 2
        self.SZ_SEL_ALU2 = 2
        self.SZ_SEL_IMM = 3

    def MT_X(self):  
        return bit_pat("b???",w = self.SZ_MT)
    def MT_B(self):  
        return value(0b000,w = self.SZ_MT)
    def MT_H(self):  
        return value(0b001,w = self.SZ_MT)
    def MT_W(self):  
        return value(0b010,w = self.SZ_MT)
    def MT_D(self):  
        return value(0b011,w = self.SZ_MT)
    def MT_BU(self): 
        return value(0b100,w = self.SZ_MT)
    def MT_HU(self): 
        return value(0b101,w = self.SZ_MT)
    def MT_WU(self): 
        return value(0b110,w = self.SZ_MT)

    def BR_EQ(self):   
        return value(0, w = self.SZ_BR)
    def BR_NE(self):   
        return value(1, w = self.SZ_BR)
    def BR_J(self):    
        return value(2, w = self.SZ_BR)
    def BR_N(self):    
        return value(3, w = self.SZ_BR)
    def BR_LT(self):   
        return value(4, w = self.SZ_BR)
    def BR_GE(self):   
        return value(5, w = self.SZ_BR)
    def BR_LTU(self):  
        return value(6, w = self.SZ_BR)
    def BR_GEU(self):  
        return value(7, w = self.SZ_BR)

    def A1_X(self):    
        return bit_pat("b??", w = self.SZ_SEL_ALU1)
    def A1_ZERO(self): 
        return value(0, w = self.SZ_SEL_ALU1)
    def A1_RS1(self):  
        return value(1, w = self.SZ_SEL_ALU1)
    def A1_PC(self):   
        return value(2, w = self.SZ_SEL_ALU1)

    def IMM_X(self):  
        return bit_pat("b???", w = self.SZ_SEL_IMM)
    def IMM_S(self):  
        return value(0, w = self.SZ_SEL_IMM)
    def IMM_B(self): 
        return value(1, w = self.SZ_SEL_IMM)
    def IMM_U(self):  
        return value(2, w = self.SZ_SEL_IMM)
    def IMM_J(self): 
        return value(3, w = self.SZ_SEL_IMM)
    def IMM_I(self):  
        return value(4, w = self.SZ_SEL_IMM)
    def IMM_Z(self):  
        return value(5, w = self.SZ_SEL_IMM)

    def A2_X(self):    
        return bit_pat("b??", w = self.SZ_SEL_ALU2)
    def A2_ZERO(self): 
        return value(0, w = self.SZ_SEL_ALU2)
    def A2_SIZE(self): 
        return value(1, w = self.SZ_SEL_ALU2)
    def A2_RS2(self):  
        return value(2, w = self.SZ_SEL_ALU2)
    def A2_IMM(self):  
        return value(3, w = self.SZ_SEL_ALU2)
    def X(self): 
        return bit_pat("b?", w = 1)
    def N(self): 
        return bit_pat("b0", w = 1)
    def Y(self): 
        return bit_pat("b1", w = 1)

    def DW_X(self):  
        return self.X()
    def DW_32(self): 
        return value(0, w = self.SZ_DW)
    def DW_64(self): 
        return value(1, w = self.SZ_DW)
    def DW_XPR(self): 
        return self.DW_64()    

D_CONSTS = zqh_core_common_decode_consts()

class zqh_core_common_memory_consts(object):
    def __init__(self):
        self.SZ      = 5
    def M_X(self):       
        return bit_pat("b?????",w = self.SZ)
    def M_XRD(self):     
        return value(0b00000,w = self.SZ) ## int load
    def M_XWR(self):     
        return value(0b00001,w = self.SZ) ## int store
    def M_PFR(self):     
        return value(0b00010,w = self.SZ) ## prefetch with intent to read
    def M_PFW(self):     
        return value(0b00011,w = self.SZ) ## prefetch with intent to write
    def M_XA_SWAP(self): 
        return value(0b00100,w = self.SZ)
    def M_FLUSH_ALL(self): 
        return value(0b00101,w = self.SZ)  ## flush all lines
    def M_XLR(self):     
        return value(0b00110,w = self.SZ)
    def M_XSC(self):     
        return value(0b00111,w = self.SZ)
    def M_XA_ADD(self):  
        return value(0b01000,w = self.SZ)
    def M_XA_XOR(self):  
        return value(0b01001,w = self.SZ)
    def M_XA_OR(self):   
        return value(0b01010,w = self.SZ)
    def M_XA_AND(self):  
        return value(0b01011,w = self.SZ)
    def M_XA_MIN(self):  
        return value(0b01100,w = self.SZ)
    def M_XA_MAX(self):  
        return value(0b01101,w = self.SZ)
    def M_XA_MINU(self): 
        return value(0b01110,w = self.SZ)
    def M_XA_MAXU(self): 
        return value(0b01111,w = self.SZ)
    def M_FLUSH(self):   
        return value(0b10000,w = self.SZ) ## write back dirty data and cede R/W permissions
    def M_PWR(self):     
        return value(0b10001,w = self.SZ) ## partial (masked) store
    def M_PRODUCE(self): 
        return value(0b10010,w = self.SZ) ## write back dirty data and cede W permissions
    def M_CLEAN(self):   
        return value(0b10011,w = self.SZ) ## write back dirty data and retain R/W permissions
    def M_SFENCE(self):  
        return value(0b10100,w = self.SZ) ## flush TLB
  
    def is_amo_logical(self, cmd): 
        return cmd.match_any([
            self.M_XA_SWAP(),
            self.M_XA_XOR(),
            self.M_XA_OR(),
            self.M_XA_AND()])
    def is_amo_arithmetic(self, cmd): 
        return cmd.match_any([
            self.M_XA_ADD(),
            self.M_XA_MIN(),
            self.M_XA_MAX(),
            self.M_XA_MINU(),
            self.M_XA_MAXU()])
    def is_amo(self, cmd): 
        return self.is_amo_logical(cmd) | self.is_amo_arithmetic(cmd)
    def is_read(self, cmd): 
        return cmd.match_any([
            self.M_XRD(),
            self.M_XLR(),
            self.M_XSC()]) | self.is_amo(cmd)
    def is_write(self, cmd): 
        return cmd.match_any([
            self.M_XWR(),
            self.M_PWR(),
            self.M_XSC()]) | self.is_amo(cmd)
    def is_write_intent(self, cmd): 
        return self.is_write(cmd) | cmd.match_any([self.M_PFW(), self.M_XLR()])

    def store_mask_gen(self, typ, addr, max_size):
        size = typ[log2_up(log2_up(max_size) + 1) - 1: 0]
        mask_map = map(
            lambda _: value(2**(2**_) - 1).to_bits() << (
                addr[log2_ceil(max_size) - 1 : _] << _),
            range(log2_up(max_size) + 1))
        return sel_bin(size, mask_map)[max_size - 1 : 0]

    def store_data_gen(self, typ, data, max_size):
        size = typ[log2_up(log2_up(max_size) + 1) - 1: 0]
        data_map = map(
            lambda _: data[(8*(2**_))-1:0].rep(1 << (log2_up(max_size)-_)),
            range(log2_up(max_size) + 1))
        return sel_bin(size, data_map)

    def load_data_gen(self, typ, addr, dat, max_size, min_size = 1):
        assert(is_pow_of_2(max_size))
        assert(is_pow_of_2(min_size))
        size = typ[log2_up(log2_up(max_size) + 1) - 1: 0]
        signed = ~typ.msb()

        #word -> half word -> byte
        #scan each lsb bit
        res = dat
        for i in range(log2_up(max_size)-1, log2_ceil(min_size) - 1, -1):
            pos = 8 << i
            shifted = mux(addr[i], res[2*pos-1:pos], res[pos-1:0])
            res = cat([
                mux(
                    (size == i),
                    (signed & shifted[pos-1]).rep(8*max_size-pos),
                    res[8*max_size-1:pos]), shifted])

        return res

M_CONSTS = zqh_core_common_memory_consts()

class zqh_core_common_ifu_consts(object):
    def __init__(self):
        self.SZ = 2

    def FETCH(self):
        return value(0,w = self.SZ)

    def FLUSH(self):
        return value(1,w = self.SZ)

IFU_CONSTS = zqh_core_common_ifu_consts()

class zqh_core_common_prv_consts(object):
    def __init__(self):
        self.SZ = 2

    def M(self):
        return value(3, w = self.SZ)
    def H(self):
        return value(2, w = self.SZ)
    def S(self):
        return value(1, w = self.SZ)
    def U(self):
        return value(0, w = self.SZ)

PRV_CONSTS = zqh_core_common_prv_consts()

class zqh_core_common_alu_consts(object):
    def __init__(self):
        self.SZ = 4

    def FN_X(self):    
        return bit_pat("b????", w = self.SZ)
    def FN_ADD(self):  
        return value(0, w = self.SZ)
    def FN_SL(self):   
        return value(1, w = self.SZ)
    def FN_SEQ(self):  
        return value(2, w = self.SZ)
    def FN_SNE(self):  
        return value(3, w = self.SZ)
    def FN_XOR(self):  
        return value(4, w = self.SZ)
    def FN_SR(self):   
        return value(5, w = self.SZ)
    def FN_OR(self):   
        return value(6, w = self.SZ)
    def FN_AND(self):  
        return value(7, w = self.SZ)
    def FN_SUB(self):  
        return value(10, w = self.SZ)
    def FN_SRA(self):  
        return value(11, w = self.SZ)
    def FN_SLT(self):  
        return value(12, w = self.SZ)
    def FN_SGE(self):  
        return value(13, w = self.SZ)
    def FN_SLTU(self): 
        return value(14, w = self.SZ)
    def FN_SGEU(self): 
        return value(15, w = self.SZ)

    def FN_MUL(self):    
        return value(0, w = self.SZ)
    def FN_MULH(self):   
        return value(1, w = self.SZ)
    def FN_MULHSU(self): 
        return value(2, w = self.SZ)
    def FN_MULHU(self):  
        return value(3, w = self.SZ)

    def FN_DIV(self):  
        return value(4, w = self.SZ)
    def FN_DIVU(self): 
        return value(5, w = self.SZ)
    def FN_REM(self):  
        return value(6, w = self.SZ)
    def FN_REMU(self): 
        return value(7, w = self.SZ)

A_CONSTS = zqh_core_common_alu_consts()

class zqh_core_common_cause_consts(object):
    def __init__(self):
        self.misaligned_fetch = 0x0
        self.fetch_access = 0x1
        self.illegal_instruction = 0x2
        self.breakpoint = 0x3
        self.misaligned_load = 0x4
        self.load_access = 0x5
        self.misaligned_store = 0x6
        self.store_access = 0x7
        self.user_ecall = 0x8
        self.supervisor_ecall = 0x9
        self.hypervisor_ecall = 0xa
        self.machine_ecall = 0xb
        self.fetch_page_fault = 0xc
        self.load_page_fault = 0xd
        self.store_page_fault = 0xf
        all = [self.misaligned_fetch,
               self.fetch_access,
               self.illegal_instruction,
               self.breakpoint,
               self.misaligned_load,
               self.load_access,
               self.misaligned_store,
               self.store_access,
               self.user_ecall,
               self.supervisor_ecall,
               self.hypervisor_ecall,
               self.machine_ecall,
               self.fetch_page_fault,
               self.load_page_fault,
               self.store_page_fault]

CS_CONSTS = zqh_core_common_cause_consts()

class zqh_core_common_csr_addr_consts(object):
    def __init__(self):
        self.fflags = 0x1
        self.frm = 0x2
        self.fcsr = 0x3
        self.cycle = 0xc00
        self.time = 0xc01
        self.instret = 0xc02
        self.hpmcounter3 = 0xc03
        self.hpmcounter4 = 0xc04
        self.hpmcounter5 = 0xc05
        self.hpmcounter6 = 0xc06
        self.hpmcounter7 = 0xc07
        self.hpmcounter8 = 0xc08
        self.hpmcounter9 = 0xc09
        self.hpmcounter10 = 0xc0a
        self.hpmcounter11 = 0xc0b
        self.hpmcounter12 = 0xc0c
        self.hpmcounter13 = 0xc0d
        self.hpmcounter14 = 0xc0e
        self.hpmcounter15 = 0xc0f
        self.hpmcounter16 = 0xc10
        self.hpmcounter17 = 0xc11
        self.hpmcounter18 = 0xc12
        self.hpmcounter19 = 0xc13
        self.hpmcounter20 = 0xc14
        self.hpmcounter21 = 0xc15
        self.hpmcounter22 = 0xc16
        self.hpmcounter23 = 0xc17
        self.hpmcounter24 = 0xc18
        self.hpmcounter25 = 0xc19
        self.hpmcounter26 = 0xc1a
        self.hpmcounter27 = 0xc1b
        self.hpmcounter28 = 0xc1c
        self.hpmcounter29 = 0xc1d
        self.hpmcounter30 = 0xc1e
        self.hpmcounter31 = 0xc1f
        self.sstatus = 0x100
        self.sie = 0x104
        self.stvec = 0x105
        self.scounteren = 0x106
        self.sscratch = 0x140
        self.sepc = 0x141
        self.scause = 0x142
        self.sbadaddr = 0x143
        self.sip = 0x144
        self.satp = 0x180
        self.mstatus = 0x300
        self.misa = 0x301
        self.medeleg = 0x302
        self.mideleg = 0x303
        self.mie = 0x304
        self.mtvec = 0x305
        self.mcounteren = 0x306
        self.mscratch = 0x340
        self.mepc = 0x341
        self.mcause = 0x342
        self.mbadaddr = 0x343
        self.mip = 0x344
        self.pmpcfg0 = 0x3a0
        self.pmpcfg1 = 0x3a1
        self.pmpcfg2 = 0x3a2
        self.pmpcfg3 = 0x3a3
        self.pmpaddr0 = 0x3b0
        self.pmpaddr1 = 0x3b1
        self.pmpaddr2 = 0x3b2
        self.pmpaddr3 = 0x3b3
        self.pmpaddr4 = 0x3b4
        self.pmpaddr5 = 0x3b5
        self.pmpaddr6 = 0x3b6
        self.pmpaddr7 = 0x3b7
        self.pmpaddr8 = 0x3b8
        self.pmpaddr9 = 0x3b9
        self.pmpaddr10 = 0x3ba
        self.pmpaddr11 = 0x3bb
        self.pmpaddr12 = 0x3bc
        self.pmpaddr13 = 0x3bd
        self.pmpaddr14 = 0x3be
        self.pmpaddr15 = 0x3bf
        self.tselect = 0x7a0
        self.tdata1 = 0x7a1
        self.tdata2 = 0x7a2
        self.tdata3 = 0x7a3
        self.dcsr = 0x7b0
        self.dpc = 0x7b1
        self.dscratch = 0x7b2
        self.mcycle = 0xb00
        self.minstret = 0xb02
        self.mhpmcounter3 = 0xb03
        self.mhpmcounter4 = 0xb04
        self.mhpmcounter5 = 0xb05
        self.mhpmcounter6 = 0xb06
        self.mhpmcounter7 = 0xb07
        self.mhpmcounter8 = 0xb08
        self.mhpmcounter9 = 0xb09
        self.mhpmcounter10 = 0xb0a
        self.mhpmcounter11 = 0xb0b
        self.mhpmcounter12 = 0xb0c
        self.mhpmcounter13 = 0xb0d
        self.mhpmcounter14 = 0xb0e
        self.mhpmcounter15 = 0xb0f
        self.mhpmcounter16 = 0xb10
        self.mhpmcounter17 = 0xb11
        self.mhpmcounter18 = 0xb12
        self.mhpmcounter19 = 0xb13
        self.mhpmcounter20 = 0xb14
        self.mhpmcounter21 = 0xb15
        self.mhpmcounter22 = 0xb16
        self.mhpmcounter23 = 0xb17
        self.mhpmcounter24 = 0xb18
        self.mhpmcounter25 = 0xb19
        self.mhpmcounter26 = 0xb1a
        self.mhpmcounter27 = 0xb1b
        self.mhpmcounter28 = 0xb1c
        self.mhpmcounter29 = 0xb1d
        self.mhpmcounter30 = 0xb1e
        self.mhpmcounter31 = 0xb1f
        self.mhpmevent3 = 0x323
        self.mhpmevent4 = 0x324
        self.mhpmevent5 = 0x325
        self.mhpmevent6 = 0x326
        self.mhpmevent7 = 0x327
        self.mhpmevent8 = 0x328
        self.mhpmevent9 = 0x329
        self.mhpmevent10 = 0x32a
        self.mhpmevent11 = 0x32b
        self.mhpmevent12 = 0x32c
        self.mhpmevent13 = 0x32d
        self.mhpmevent14 = 0x32e
        self.mhpmevent15 = 0x32f
        self.mhpmevent16 = 0x330
        self.mhpmevent17 = 0x331
        self.mhpmevent18 = 0x332
        self.mhpmevent19 = 0x333
        self.mhpmevent20 = 0x334
        self.mhpmevent21 = 0x335
        self.mhpmevent22 = 0x336
        self.mhpmevent23 = 0x337
        self.mhpmevent24 = 0x338
        self.mhpmevent25 = 0x339
        self.mhpmevent26 = 0x33a
        self.mhpmevent27 = 0x33b
        self.mhpmevent28 = 0x33c
        self.mhpmevent29 = 0x33d
        self.mhpmevent30 = 0x33e
        self.mhpmevent31 = 0x33f
        self.mvendorid = 0xf11
        self.marchid = 0xf12
        self.mimpid = 0xf13
        self.mhartid = 0xf14
        self.cycleh = 0xc80
        self.timeh = 0xc81
        self.instreth = 0xc82
        self.hpmcounter3h = 0xc83
        self.hpmcounter4h = 0xc84
        self.hpmcounter5h = 0xc85
        self.hpmcounter6h = 0xc86
        self.hpmcounter7h = 0xc87
        self.hpmcounter8h = 0xc88
        self.hpmcounter9h = 0xc89
        self.hpmcounter10h = 0xc8a
        self.hpmcounter11h = 0xc8b
        self.hpmcounter12h = 0xc8c
        self.hpmcounter13h = 0xc8d
        self.hpmcounter14h = 0xc8e
        self.hpmcounter15h = 0xc8f
        self.hpmcounter16h = 0xc90
        self.hpmcounter17h = 0xc91
        self.hpmcounter18h = 0xc92
        self.hpmcounter19h = 0xc93
        self.hpmcounter20h = 0xc94
        self.hpmcounter21h = 0xc95
        self.hpmcounter22h = 0xc96
        self.hpmcounter23h = 0xc97
        self.hpmcounter24h = 0xc98
        self.hpmcounter25h = 0xc99
        self.hpmcounter26h = 0xc9a
        self.hpmcounter27h = 0xc9b
        self.hpmcounter28h = 0xc9c
        self.hpmcounter29h = 0xc9d
        self.hpmcounter30h = 0xc9e
        self.hpmcounter31h = 0xc9f
        self.mcycleh = 0xb80
        self.minstreth = 0xb82
        self.mhpmcounter3h = 0xb83
        self.mhpmcounter4h = 0xb84
        self.mhpmcounter5h = 0xb85
        self.mhpmcounter6h = 0xb86
        self.mhpmcounter7h = 0xb87
        self.mhpmcounter8h = 0xb88
        self.mhpmcounter9h = 0xb89
        self.mhpmcounter10h = 0xb8a
        self.mhpmcounter11h = 0xb8b
        self.mhpmcounter12h = 0xb8c
        self.mhpmcounter13h = 0xb8d
        self.mhpmcounter14h = 0xb8e
        self.mhpmcounter15h = 0xb8f
        self.mhpmcounter16h = 0xb90
        self.mhpmcounter17h = 0xb91
        self.mhpmcounter18h = 0xb92
        self.mhpmcounter19h = 0xb93
        self.mhpmcounter20h = 0xb94
        self.mhpmcounter21h = 0xb95
        self.mhpmcounter22h = 0xb96
        self.mhpmcounter23h = 0xb97
        self.mhpmcounter24h = 0xb98
        self.mhpmcounter25h = 0xb99
        self.mhpmcounter26h = 0xb9a
        self.mhpmcounter27h = 0xb9b
        self.mhpmcounter28h = 0xb9c
        self.mhpmcounter29h = 0xb9d
        self.mhpmcounter30h = 0xb9e
        self.mhpmcounter31h = 0xb9f
        self.all = [self.fflags,
            self.frm,
            self.fcsr,
            self.cycle,
            self.time,
            self.instret,
            self.hpmcounter3,
            self.hpmcounter4,
            self.hpmcounter5,
            self.hpmcounter6,
            self.hpmcounter7,
            self.hpmcounter8,
            self.hpmcounter9,
            self.hpmcounter10,
            self.hpmcounter11,
            self.hpmcounter12,
            self.hpmcounter13,
            self.hpmcounter14,
            self.hpmcounter15,
            self.hpmcounter16,
            self.hpmcounter17,
            self.hpmcounter18,
            self.hpmcounter19,
            self.hpmcounter20,
            self.hpmcounter21,
            self.hpmcounter22,
            self.hpmcounter23,
            self.hpmcounter24,
            self.hpmcounter25,
            self.hpmcounter26,
            self.hpmcounter27,
            self.hpmcounter28,
            self.hpmcounter29,
            self.hpmcounter30,
            self.hpmcounter31,
            self.sstatus,
            self.sie,
            self.stvec,
            self.scounteren,
            self.sscratch,
            self.sepc,
            self.scause,
            self.sbadaddr,
            self.sip,
            self.satp,
            self.mstatus,
            self.misa,
            self.medeleg,
            self.mideleg,
            self.mie,
            self.mtvec,
            self.mcounteren,
            self.mscratch,
            self.mepc,
            self.mcause,
            self.mbadaddr,
            self.mip,
            self.pmpcfg0,
            self.pmpcfg1,
            self.pmpcfg2,
            self.pmpcfg3,
            self.pmpaddr0,
            self.pmpaddr1,
            self.pmpaddr2,
            self.pmpaddr3,
            self.pmpaddr4,
            self.pmpaddr5,
            self.pmpaddr6,
            self.pmpaddr7,
            self.pmpaddr8,
            self.pmpaddr9,
            self.pmpaddr10,
            self.pmpaddr11,
            self.pmpaddr12,
            self.pmpaddr13,
            self.pmpaddr14,
            self.pmpaddr15,
            self.tselect,
            self.tdata1,
            self.tdata2,
            self.tdata3,
            self.dcsr,
            self.dpc,
            self.dscratch,
            self.mcycle,
            self.minstret,
            self.mhpmcounter3,
            self.mhpmcounter4,
            self.mhpmcounter5,
            self.mhpmcounter6,
            self.mhpmcounter7,
            self.mhpmcounter8,
            self.mhpmcounter9,
            self.mhpmcounter10,
            self.mhpmcounter11,
            self.mhpmcounter12,
            self.mhpmcounter13,
            self.mhpmcounter14,
            self.mhpmcounter15,
            self.mhpmcounter16,
            self.mhpmcounter17,
            self.mhpmcounter18,
            self.mhpmcounter19,
            self.mhpmcounter20,
            self.mhpmcounter21,
            self.mhpmcounter22,
            self.mhpmcounter23,
            self.mhpmcounter24,
            self.mhpmcounter25,
            self.mhpmcounter26,
            self.mhpmcounter27,
            self.mhpmcounter28,
            self.mhpmcounter29,
            self.mhpmcounter30,
            self.mhpmcounter31,
            self.mhpmevent3,
            self.mhpmevent4,
            self.mhpmevent5,
            self.mhpmevent6,
            self.mhpmevent7,
            self.mhpmevent8,
            self.mhpmevent9,
            self.mhpmevent10,
            self.mhpmevent11,
            self.mhpmevent12,
            self.mhpmevent13,
            self.mhpmevent14,
            self.mhpmevent15,
            self.mhpmevent16,
            self.mhpmevent17,
            self.mhpmevent18,
            self.mhpmevent19,
            self.mhpmevent20,
            self.mhpmevent21,
            self.mhpmevent22,
            self.mhpmevent23,
            self.mhpmevent24,
            self.mhpmevent25,
            self.mhpmevent26,
            self.mhpmevent27,
            self.mhpmevent28,
            self.mhpmevent29,
            self.mhpmevent30,
            self.mhpmevent31,
            self.mvendorid,
            self.marchid,
            self.mimpid,
            self.mhartid]

        self.all32 = self.all + [self.cycleh,
            self.timeh,
            self.instreth,
            self.hpmcounter3h,
            self.hpmcounter4h,
            self.hpmcounter5h,
            self.hpmcounter6h,
            self.hpmcounter7h,
            self.hpmcounter8h,
            self.hpmcounter9h,
            self.hpmcounter10h,
            self.hpmcounter11h,
            self.hpmcounter12h,
            self.hpmcounter13h,
            self.hpmcounter14h,
            self.hpmcounter15h,
            self.hpmcounter16h,
            self.hpmcounter17h,
            self.hpmcounter18h,
            self.hpmcounter19h,
            self.hpmcounter20h,
            self.hpmcounter21h,
            self.hpmcounter22h,
            self.hpmcounter23h,
            self.hpmcounter24h,
            self.hpmcounter25h,
            self.hpmcounter26h,
            self.hpmcounter27h,
            self.hpmcounter28h,
            self.hpmcounter29h,
            self.hpmcounter30h,
            self.hpmcounter31h,
            self.mcycleh,
            self.minstreth,
            self.mhpmcounter3h,
            self.mhpmcounter4h,
            self.mhpmcounter5h,
            self.mhpmcounter6h,
            self.mhpmcounter7h,
            self.mhpmcounter8h,
            self.mhpmcounter9h,
            self.mhpmcounter10h,
            self.mhpmcounter11h,
            self.mhpmcounter12h,
            self.mhpmcounter13h,
            self.mhpmcounter14h,
            self.mhpmcounter15h,
            self.mhpmcounter16h,
            self.mhpmcounter17h,
            self.mhpmcounter18h,
            self.mhpmcounter19h,
            self.mhpmcounter20h,
            self.mhpmcounter21h,
            self.mhpmcounter22h,
            self.mhpmcounter23h,
            self.mhpmcounter24h,
            self.mhpmcounter25h,
            self.mhpmcounter26h,
            self.mhpmcounter27h,
            self.mhpmcounter28h,
            self.mhpmcounter29h,
            self.mhpmcounter30h,
            self.mhpmcounter31h]
CSRA_CONSTS = zqh_core_common_csr_addr_consts()


class zqh_csr_consts(object):
    def __init__(self):
        ## commands
        self.SZ = 3
        self.SZ_ADDR = 12
        self.firstCtr = CSRA_CONSTS.cycle
        self.firstCtrH = CSRA_CONSTS.cycleh
        self.firstHPC = CSRA_CONSTS.hpmcounter3
        self.firstHPCH = CSRA_CONSTS.hpmcounter3h
        self.firstHPE = CSRA_CONSTS.mhpmevent3
        self.firstMHPC = CSRA_CONSTS.mhpmcounter3
        self.firstMHPCH = CSRA_CONSTS.mhpmcounter3h
        self.firstHPM = 3
        self.nCtr = 32
        self.nHPM = self.nCtr - self.firstHPM
        self.hpmWidth = 40
        self.maxPMPs = 16

    def X(self):
        return bit_pat.dont_care(self.SZ)
    def N(self):
        return value(0, w = self.SZ)
    def W(self):
        return value(1, w = self.SZ)
    def S(self):
        return value(2, w = self.SZ)
    def C(self):
        return value(3, w = self.SZ)
    def I(self):
        return value(4, w = self.SZ)
    def R(self):
        return value(5, w = self.SZ)

    def SYSTEM_ECALL(self):
        return bit_pat('b000000000000', w = 12)

    def SYSTEM_EBREAK(self):
        return bit_pat('b000000000001', w = 12)

    def SYSTEM_MRET(self):
        return bit_pat('b001100000010', w = 12)

    def SYSTEM_WFI(self):
        return bit_pat('b000100000101', w = 12)

    def SYSTEM_DRET(self):
        return bit_pat('b011110110010', w = 12)
                       
    def SYSTEM_SRET(self):
        return bit_pat('b000100000010', w = 12)

    def SYSTEM_SFENCE_VMA(self):
        return bit_pat('b0001001?????', w = 12)

    def busErrorIntCause(self):
        return 128
    def debugIntCause(self):
        return 14 ## keep in sync with MIP.debug
    def debugTriggerCause(self):
      res = self.debugIntCause()
      return res

    def XL_32(self):
        return 1
    def XL_64(self):
        return 2
    def XL_128(self):
        return 3

CSR_CONSTS = zqh_csr_consts()

class zqh_inst_imm_gen(object):
    def imm_s(self, inst):
        return cat([
            inst[31].rep(20),
            inst[31:25],
            inst[11:7]])
    
    def imm_b(self, inst):
        return cat([
            inst[31].rep(20),
            inst[7],
            inst[30:25],
            inst[11:8],
            value(0, w = 1)])
    
    def imm_u(self, inst):
        return cat([
            inst[31:12],
            value(0, 12)])
    
    def imm_j(self, inst):
        return cat([
            inst[31].rep(11),
            inst[31],
            inst[19:12],
            inst[20],
            inst[30:21],
            value(0, 1)])
    
    def imm_i(self, inst):
        return cat([
            inst[31].rep(20),
            inst[31:20]])
    
    def imm_z(self, inst):
        return cat([
            value(0, w = 27),
            inst[19:15]])
    
    def imm_gen(self, sel_imm, inst):
        if isinstance(sel_imm, value):
            sel = sel_imm.to_bits()
        elif isinstance(sel_imm, int):
            sel = value(sel_imm).to_bits()
        else:
            sel = sel_imm

        imm = bits(w = 32, init = 0).to_sint()
        with when(sel == D_CONSTS.IMM_S()):
            imm /= self.imm_s(inst)
        with elsewhen(sel == D_CONSTS.IMM_B()):
            imm /= self.imm_b(inst)
        with elsewhen(sel == D_CONSTS.IMM_U()):
            imm /= self.imm_u(inst)
        with elsewhen(sel == D_CONSTS.IMM_J()):
            imm /= self.imm_j(inst)
        with elsewhen(sel == D_CONSTS.IMM_I()):
            imm /= self.imm_i(inst)
        with elsewhen(sel == D_CONSTS.IMM_Z()):
            imm /= self.imm_z(inst)

        return imm

IMM_GEN = zqh_inst_imm_gen()

class zqh_core_common_cfi_type_consts(object):
    def __init__(self):
        self.SZ = 2

    def branch(self):
        return 0

    def jump(self):
        return 1

    def call(self):
        return 2

    def ret(self):
        return 3
CFI_CONSTS = zqh_core_common_cfi_type_consts()

class zqh_core_common_btb_consts(object):
    def __init__(self):
        self.SZ = 2

    def btb_update(self):
        return value(0, w = self.SZ)

    def ras_update(self):
        return value(1, w = self.SZ)
BTB_CONSTS = zqh_core_common_btb_consts()
