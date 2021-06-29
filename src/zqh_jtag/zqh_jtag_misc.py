#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/jtag/*.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *

class JtagState(object):

    (TestLogicReset,
     RunTestIdle,
     SelectDRScan,
     CaptureDR,
     ShiftDR,
     Exit1DR,
     PauseDR,
     Exit2DR,
     UpdateDR,
     SelectIRScan,
     CaptureIR,
     ShiftIR,
     Exit1IR,
     PauseIR,
     Exit2IR,
     UpdateIR) = range(16)

    @classmethod
    def width(self):
        return log2_ceil(16)

class JtagIdcode(object):
  #/** Generates a JTAG IDCODE as a 32-bit integer, using the format in 12.1.1d.
  #  */
  @classmethod
  def apply(self, version, partNumber, mfrId):
    assert(version < (1 << 4)), "version field must be 4 bits at most"
    assert(partNumber < (1 << 16)), "part number must be 16 bits at most"
    assert(mfrId < (1 << 11)), "manufacturer identity must be 11 bits at most"
    return (version << 28) | (partNumber << 12) | (mfrId << 1) | 1

  #/** A dummy manufacturer ID, not to be used per 12.2.1b since bus masters may shift this out to
  #  * determine the end of a bus.
  #  */
  @classmethod
  def dummyMfrId(self):
      return 0x7f
