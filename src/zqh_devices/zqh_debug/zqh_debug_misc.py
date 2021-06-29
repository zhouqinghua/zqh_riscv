import sys
import os
from phgl_imp import *

#/** Constant values used by both Debug Bus Response & Request
#  */
class DMIConsts(object):
  dmiDataSize = 32

  dmiOpSize = 2
  dmi_OP_NONE            = 0b00
  dmi_OP_READ            = 0b01
  dmi_OP_WRITE           = 0b10

  dmiRespSize = 2
  dmi_RESP_SUCCESS     = 0b00
  dmi_RESP_FAILURE     = 0b01
  dmi_RESP_HW_FAILURE  = 0b10
  ## This is used outside this block
  ## to indicate 'busy'.
  dmi_RESP_RESERVED    = 0b11

class DsbBusConsts(object):
  sbAddrWidth = 12
  sbIdWidth   = 10 

class DsbRegAddrs(object):
  ADDR_OFFSET   = 0x1000 #above dmi reg's space

  ## These are used by the ROM.
  HALTED       = 0x100
  GOING        = 0x104
  RESUMING     = 0x108
  EXCEPTION    = 0x10C

  WHERETO      = 0x300
  ## This needs to be aligned for up to lq/sq

  
  ## This shows up in HartInfo, and needs to be aligned
  ## to enable up to LQ/SQ instructions.
  DATA         = 0x380

  ## We want DATA to immediately follow PROGBUF so that we can
  ## use them interchangeably. Leave another slot if there is an
  ## implicit ebreak.
  def PROGBUF(cfg):
    tmp = DsbRegAddrs.DATA - (cfg.nProgramBufferWords * 4)
    return (tmp - 4) if (cfg.hasImplicitEbreak) else tmp
 
  ## This is unused if hasImpEbreak is false, and just points to the end of the PROGBUF.
  def IMPEBREAK(self, cfg):
      return self.DATA - 4 

  ## We want abstract to be immediately before PROGBUF
  ## because we auto-generate 2 instructions.
  def ABSTRACT(cfg):
      return DsbRegAddrs.PROGBUF(cfg) - 8

  FLAGS        = 0x400
  ROMBASE      = 0x800
 

#/** Enumerations used both in the hardware
#  * and in the configuration specification.
#  */

class DebugModuleAccessType(object):
  (Access8Bit, Access16Bit, Access32Bit, Access64Bit, Access128Bit) = range(5)


class DebugAbstractCommandError(object):
  (Success, ErrBusy, ErrNotSupported, ErrException, ErrHaltResume) = range(5)


class DebugAbstractCommandType(object):
  (AccessRegister, QuickAccess)  = range(2)

class DebugRomContents(object):
  debug_rom_raw = (
      0x6f, 0x00, 0xc0, 0x00, 0x6f, 0x00, 0x80, 0x03, 0x6f, 0x00, 0x40, 0x04,
      0x0f, 0x00, 0xf0, 0x0f, 0x73, 0x10, 0x24, 0x7b, 0x73, 0x24, 0x40, 0xf1,
      0x23, 0x20, 0x80, 0x10, 0x03, 0x44, 0x04, 0x40, 0x13, 0x74, 0x34, 0x00,
      0xe3, 0x08, 0x04, 0xfe, 0x13, 0x74, 0x14, 0x00, 0x63, 0x08, 0x04, 0x00,
      0x73, 0x24, 0x20, 0x7b, 0x23, 0x22, 0x00, 0x10, 0x67, 0x00, 0x00, 0x30,
      0x73, 0x24, 0x40, 0xf1, 0x23, 0x24, 0x80, 0x10, 0x73, 0x24, 0x20, 0x7b,
      0x73, 0x00, 0x20, 0x7b, 0x23, 0x26, 0x00, 0x10, 0x73, 0x00, 0x10, 0x00)
