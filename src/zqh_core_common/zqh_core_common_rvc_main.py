#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/RVC.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_core_common_core_parameters import zqh_core_common_core_parameter

class zqh_core_common_rvc_decoder(object):
    def __init__(self, x, rv64):
        self.x = x
        self.rv64 = rv64

    def rs1p(self):
        return cat([value(1,w = 2), self.x[9:7]])
    def rs2p(self):
        return cat([value(1, w = 2), self.x[4:2]])
    def rs2(self):
        return self.x[6:2]
    def rd(self):
        return self.x[11:7]
    def addi4spnImm(self):
        return cat([self.x[10:7], self.x[12:11], self.x[5], self.x[6], value(0, w = 2)])
    def lwImm(self):
        return cat([self.x[5], self.x[12:10], self.x[6], value(0, w = 2)])
    def ldImm(self):
        return cat([self.x[6:5], self.x[12:10], value(0, w = 3)])
    def lwspImm(self):
        return cat([self.x[3:2], self.x[12], self.x[6:4], value(0, w = 2)])
    def ldspImm(self):
        return cat([self.x[4:2], self.x[12], self.x[6:5], value(0, w = 3)])
    def swspImm(self):
        return cat([self.x[8:7], self.x[12:9], value(0, w = 2)])
    def sdspImm(self):
        return cat([self.x[9:7], self.x[12:10], value(0, w = 3)])
    def luiImm(self):
        return cat([self.x[12].rep(15), self.x[6:2], value(0, w = 12)])
    def addi16spImm(self):
        return cat([self.x[12].rep(3), self.x[4:3], self.x[5], self.x[2],
            self.x[6], value(0, w = 4)])
    def addiImm(self):
        return cat([self.x[12].rep(7), self.x[6:2]])
    def jImm(self):
        return cat([self.x[12].rep(10), self.x[8], self.x[10:9], self.x[6],
            self.x[7], self.x[2], self.x[11], self.x[5:3], value(0, w = 1)])
    def bImm(self):
        return cat([self.x[12].rep(5), self.x[6:5], self.x[2], self.x[11:10],
            self.x[4:3], value(0, w = 1)])
    def shamt(self):
        return cat([self.x[12], self.x[6:2]])
    def x0(self):
        return value(0, w = 5)
    def ra(self):
        return value(1, w = 5)
    def sp(self):
        return value(2, w = 5)

    def q0(self):
        def addi4spn():
            opc = mux(self.x[12:5].r_or(), value(0x13, w = 7), value(0x1F, w = 7))
            return cat([self.addi4spnImm(), self.sp(), value(0,3), self.rs2p(), opc])
        def ld():
            return cat([self.ldImm(), self.rs1p(), value(3,3), self.rs2p(), value(0x03,7)])
        def lw():
            return cat([self.lwImm(), self.rs1p(), value(2,3), self.rs2p(), value(0x03,7)])
        def fld():
            return cat([self.ldImm(), self.rs1p(), value(3,3), self.rs2p(), value(0x07,7)])
        def flw():
            return mux(
                self.rv64,
                ld(),
                cat([self.lwImm(), self.rs1p(), value(2,3), self.rs2p(), value(0x07,7)]))
        def unimp():
            return cat([self.lwImm() >> 5, self.rs2p(), self.rs1p(), value(2,3),
                self.lwImm()[4:0], value(0x3F,7)])
        def sd():
            return cat([self.ldImm() >> 5, self.rs2p(), self.rs1p(), value(3,3),
                self.ldImm()[4:0], value(0x23,7)])
        def sw():
            return cat([self.lwImm() >> 5, self.rs2p(), self.rs1p(), value(2,3),
                self.lwImm()[4:0], value(0x23,7)])
        def fsd():
            return cat([self.ldImm() >> 5, self.rs2p(), self.rs1p(), value(3,3),
                self.ldImm()[4:0], value(0x27,7)])
        def fsw():
            return mux(self.rv64, sd(), cat([self.lwImm() >> 5, self.rs2p(),
                self.rs1p(), value(2,3), self.lwImm()[4:0], value(0x27,7)]))
        return [addi4spn(), fld(), lw(), flw(), unimp(), fsd(), sw(), fsw()]

    def q1(self):
        def addi():
            return cat([self.addiImm(), self.rd(), value(0,3), self.rd(), value(0x13,7)])
        def addiw():
            opc = mux(self.rd().r_or(), value(0x1B,7), value(0x1F,7))
            return cat([self.addiImm(), self.rd(), value(0,3), self.rd(), opc])
        def jal():
            return mux(
                self.rv64,
                addiw(),
                cat([self.jImm()[20], self.jImm()[10:1], self.jImm()[11], self.jImm()[19:12],
                    self.ra(),
                    value(0x6F,7)]))
        def li():
            return cat([self.addiImm(), self.x0(), value(0,3), self.rd(), value(0x13,7)])
        def addi16sp():
            opc = mux(
                self.addiImm().r_or(),
                value(0x13,7),
                value(0x1F,7))
            return cat([self.addi16spImm(), self.rd(), value(0,3), self.rd(), opc])
        def lui():
            opc = mux(self.addiImm().r_or(), value(0x37,7), value(0x3F,7))
            me = cat([self.luiImm()[31:12], self.rd(), opc])
            return sel_bin(
                (self.rd() == self.x0()) | (self.rd() == self.sp()),
                reversed([addi16sp(), me]))
        def j():
            return cat([self.jImm()[20], self.jImm()[10:1], self.jImm()[11],
                self.jImm()[19:12], self.x0(), value(0x6F,7)])
        def beqz():
            return cat([self.bImm()[12], self.bImm()[10:5], self.x0(), self.rs1p(),
                value(0,3), self.bImm()[4:1], self.bImm()[11], value(0x63,7)])
        def bnez():
            return cat([self.bImm()[12], self.bImm()[10:5], self.x0(), self.rs1p(),
                value(1,3), self.bImm()[4:1], self.bImm()[11], value(0x63,7)])
        def arith():
            def srli():
                return cat([self.shamt(), self.rs1p(), value(5,3), self.rs1p(),
                    value(0x13,7)])
            def srai():
                return srli() | value(1 << 30)
            def andi():
                return cat([self.addiImm(), self.rs1p(), value(7,3), self.rs1p(),
                    value(0x13,7)])
            def rtype():
                funct = sel_bin(
                    cat([self.x[12], self.x[6:5]]),
                    [value(0,3), value(4,3), value(6,3), value(7,3),
                        value(0,3), value(0,3), value(2,3), value(3,3)])
                sub = mux(self.x[6:5] == value(0), value(1 << 30), value(0))
                opc = mux(self.x[12], value(0x3B,7), value(0x33,7))
                return cat([self.rs2p(), self.rs1p(), funct, self.rs1p(), opc]) | sub
            return sel_bin(self.x[11:10], [srli(), srai(), andi(), rtype()])
        return [addi(), jal(), li(), lui(), arith(), j(), beqz(), bnez()]
  
    def q2(self):
        load_opc = mux(self.rd().r_or(), value(0x03,7), value(0x1F,7))
        def slli():
            return cat([self.shamt(), self.rd(), value(1,3), self.rd(), value(0x13,7)])
        def ldsp():
            return cat([self.ldspImm(), self.sp(), value(3,3), self.rd(), load_opc])
        def lwsp():
            return cat([self.lwspImm(), self.sp(), value(2,3), self.rd(), load_opc])
        def fldsp():
            return cat([self.ldspImm(), self.sp(), value(3,3), self.rd(), value(0x07,7)])
        def flwsp():
            return mux(
                self.rv64,
                ldsp(),
                cat([self.lwspImm(), self.sp(), value(2,3), self.rd(), value(0x07,7)]))
        def sdsp():
            return cat([self.sdspImm() >> 5, self.rs2(), self.sp(), 
                value(3,3), self.sdspImm()[4:0], value(0x23,7)])
        def swsp():
            return cat([self.swspImm() >> 5, self.rs2(), self.sp(), 
                value(2,3), self.swspImm()[4:0], value(0x23,7)])
        def fsdsp():
            return cat([self.sdspImm() >> 5, self.rs2(), self.sp(), 
                value(3,3), self.sdspImm()[4:0], value(0x27,7)])
        def fswsp():
            return mux(self.rv64, sdsp(), cat([self.swspImm() >> 5, self.rs2(), 
                self.sp(), value(2,3), self.swspImm()[4:0], value(0x27,7)]))
        def jalr():
            mv = cat([self.rs2(), self.x0(), value(0,3), self.rd(), value(0x33,7)])
            add = cat([self.rs2(), self.rd(), value(0,3), self.rd(), value(0x33,7)])
            jr = cat([self.rs2(), self.rd(), value(0,3), self.x0(), value(0x67,7)])
            reserved = cat([jr >> 7, value(0x1F,7)])
            jr_reserved = mux(self.rd().r_or(), jr, reserved)
            jr_mv = sel_bin(self.rs2().r_or(), reversed([mv, jr_reserved]))
            jalr = cat([self.rs2(), self.rd(), value(0,3), self.ra(), value(0x67,7)])
            ebreak = cat([jr >> 7, value(0x73,7)]) | value(1 << 20)
            jalr_ebreak = mux(self.rd().r_or(), jalr, ebreak)
            jalr_add = sel_bin(self.rs2().r_or(), reversed([add, jalr_ebreak]))
            return sel_bin(self.x[12], reversed([jalr_add, jr_mv]))
        return [slli(), fldsp(), lwsp(), flwsp(), jalr(), fsdsp(), swsp(), fswsp()]

    def decode(self):
      s = self.q0() + self.q1() + self.q2()
      return sel_bin(cat([self.x[1:0], self.x[15:13]]), s)

class zqh_core_common_rvc_expander(module):
    def set_par(self):
        super(zqh_core_common_rvc_expander, self).set_par()
        self.p = zqh_core_common_core_parameter()

    def set_port(self):
        super(zqh_core_common_rvc_expander, self).set_port()
        self.no_crg()
        self.io.var(inp('inst_in', w = 16))
        self.io.var(outp('inst_out', w = 32))
        self.io.var(inp('rv64'))

    def main(self):
        super(zqh_core_common_rvc_expander, self).main()
        self.io.inst_out /= zqh_core_common_rvc_decoder(
            self.io.inst_in,
            self.io.rv64).decode()
