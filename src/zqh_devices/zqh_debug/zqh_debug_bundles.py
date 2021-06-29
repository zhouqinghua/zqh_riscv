####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/devices/debug/Debug.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_debug_parameters import DefaultDebugModuleParams
from .zqh_debug_misc import *

#// *****************************************
#// Module Interfaces
#// 
#// *****************************************

#/** Structure to define the contents of a Debug Bus Request
#  */
class DMIReq(bundle):
    def set_par(self):
        super(DMIReq, self).set_par()
        self.p.par('addrBits', None)

    def set_var(self):
        super(DMIReq, self).set_var()
        self.var(bits('addr', w = self.p.addrBits))
        self.var(bits('data', w = DMIConsts.dmiDataSize))
        self.var(bits('op', w = DMIConsts.dmiOpSize))

#/** Structure to define the contents of a Debug Bus Response
#  */
class DMIResp(bundle):
    def set_var(self):
        super(DMIResp, self).set_var()
        self.var(bits('data', w = DMIConsts.dmiDataSize))
        self.var(bits('resp', w = DMIConsts.dmiRespSize))

#/** Structure to define the top-level DMI interface 
#  *  of DebugModule.
#  *  DebugModule is the consumer of this interface.
#  *  Therefore it has the 'flipped' version of this.
#  */
class DMIIO(bundle):
    def set_par(self):
        super(DMIIO, self).set_par()
        self.p = DefaultDebugModuleParams()

    def set_var(self):
        super(DMIIO, self).set_var()
        self.var(ready_valid('req', gen = DMIReq, addrBits = self.p.nDMIAddrSize))
        self.var(ready_valid('resp', gen = DMIResp).flip())

#/* structure for passing hartsel between the "Outer" and "Inner"
# */

class DebugInternalBundle(bundle):
    def set_var(self):
        super(DebugInternalBundle, self)
        self.var(bits('resumereq'))
        self.var(bits('hartsel', w = 10))
        self.var(bits('ackhavereset'))

#/* structure for top-level Debug Module signals which aren't the bus interfaces.
# */

class DebugCtrlBundle(bundle):
    def set_par(self):
        super(DebugCtrlBundle, self).set_par()
        self.p.par('nComponents', None)

    def set_var(self):
        super(DebugCtrlBundle, self).set_var()
        self.var(vec('debugUnavail', gen = bits, n = self.p.nComponents).as_input())
        self.var(outp('ndreset'))
        self.var(outp('dmactive'))


#/** This includes the clock and reset as these are passed through the
#  *  hierarchy until the Debug Module is actually instantiated. 
#  *  
#  */

class ClockedDMIIO(bundle):
    def set_var(self):
        super(ClockedDMIIO, self).set_var()
        self.var(DMIIO('dmi'))
        self.var(outp('dmiClock'))
        self.var(outp('dmiReset'))

class ClockedDMI_pad(bundle):
    def set_var(self):
        super(ClockedDMI_pad, self).set_var()
        self.var(DMIIO('dmi').flip())
        self.var(inp('dmiClock'))
        self.var(inp('dmiReset'))

class GeneratedI(bundle):
    def set_var(self):
        super(GeneratedI, self).set_var()
        self.var(bits('imm', w = 12))
        self.var(bits('rs1', w = 5))
        self.var(bits('funct3', w = 3))
        self.var(bits('rd', w = 5))
        self.var(bits('opcode', w = 7))

class GeneratedS(bundle):
    def set_var(self):
        super(GeneratedS, self).set_var()
        self.var(bits('immhi', w = 7))
        self.var(bits('rs2',   w = 5))
        self.var(bits('rs1',   w = 5))
        self.var(bits('funct3', w = 3))
        self.var(bits('immlo', w = 5))
        self.var(bits('opcode', w = 7))

class GeneratedUJ(bundle):
    def set_var(self):
        super(GeneratedUJ, self).set_var()
        self.var(bits('imm3',    w = 1))
        self.var(bits('imm0',    w = 10))
        self.var(bits('imm1',    w = 1))
        self.var(bits('imm2',    w = 8))
        self.var(bits('rd',      w = 5))
        self.var(bits('opcode',  w = 7))

    def setImm(self, imm) :
      ## TODO: Check bounds of imm.

      assert(imm % 2 == 0), "Immediate must be even for UJ encoding."
      immWire = bits(w = 21, init = imm)
      #val immBits = Wire(init = Vec(immWire.toBools))

      self.imm0 /= immWire[10: 1 ]
      self.imm1 /= immWire[11: 11]
      self.imm2 /= immWire[19: 12]
      self.imm3 /= immWire[20: 20]

class ACCESS_REGISTERFields(bundle):

  #/* This is 0 to indicate Access Register Command.
  #*/
  #val cmdtype = UInt(8.W)

  #val reserved0 = UInt(1.W)

  #/* 2: Access the lowest 32 bits of the register.

  #          3: Access the lowest 64 bits of the register.

  #          4: Access the lowest 128 bits of the register.

  #          If \Fsize specifies a size larger than the register's actual size,
  #          then the access must fail. If a register is accessible, then reads of \Fsize
  #          less than or equal to the register's actual size must be supported.

  #          This field controls the Argument Width as referenced in
  #          Table~\ref{tab:datareg}.
  #*/
  def set_var(self):
      super(ACCESS_REGISTERFields, self).set_var()
      self.var(bits('size', w = 3))

      self.var(bits('reserved1', w = 1))

      #/* When 1, execute the program in the Program Buffer exactly once
      #          after performing the transfer, if any.
      #*/
      self.var(bits('postexec'))

      #/* 0: Don't do the operation specified by \Fwrite.

      #          1: Do the operation specified by \Fwrite.

      #          This bit can be used to just execute the Program Buffer without
      #          having to worry about placing valid values into \Fsize or \Fregno.
      #*/
      self.var(bits('transfer'))

      #/* When \Ftransfer is set:
      #          0: Copy data from the specified register into {\tt arg0} portion
      #             of {\tt data}.

      #          1: Copy data from {\tt arg0} portion of {\tt data} into the
      #             specified register.
      #*/
      self.var(bits('write'))

      #/* Number of the register to access, as described in
      #        Table~\ref{tab:regno}.
      #        \Rdpc may be used as an alias for PC if this command is
      #        supported on a non-halted hart.
      #*/
      self.var(bits('regno', w = 16))


class QUICK_ACCESSFields(bundle):

  #/* This is 1 to indicate Quick Access command.
  #*/
  def set_var(self):
      super(QUICK_ACCESSFields, self).set_var()
      self.var(bits('cmdtype', w = 8))

      self.var(bits('reserved0', w = 24))
