#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/jtag/*.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_jtag_misc import JtagState

#/** JTAG signals, viewed from the master side
#  */
class JTAGIO(bundle):
    def set_par(self):
        super(JTAGIO, self).set_par()
        self.p.par('hasTRSTn', 0)

    def set_var(self):
        super(JTAGIO, self).set_var()
        if (self.p.hasTRSTn):
            self.var(outp('TRSTn'))
        self.var(outp('TCK'))
        self.var(outp('TMS'))
        self.var(outp('TDI'))
        self.var(inp('TDO'))

class JTAG_pad(bundle):
    def set_par(self):
        super(JTAG_pad, self).set_par()
        self.p.par('hasTRSTn', 0)

    def set_var(self):
        super(JTAG_pad, self).set_var()
        if (self.p.hasTRSTn):
            self.var(inp('TRSTn'))
        self.var(inp('TCK'))
        self.var(inp('TMS'))
        self.var(inp('TDI'))
        self.var(outp('TDO'))


#/** JTAG block output signals.
#  */
class JtagOutput(bundle):
    def set_par(self):
        super(JtagOutput, self).set_par()
        self.p.par('irLength', 8)

    def set_var(self):
        super(JtagOutput, self).set_var()
        self.var(outp('state', w = JtagState.width()))  ## state, transitions on TCK rising edge
        self.var(outp('instruction', w = self.p.irLength))  ## current active instruction
        self.var(outp('reset_out'))  ## synchronous reset asserted in Test-Logic-Reset state, should NOT hold the FSM in reset

class JtagControl(bundle):
    def set_var(self):
        super(JtagControl, self).set_var()
        self.var(inp('jtag_reset'))

class JTAGIdcodeBundle(bundle):
    def set_var(self):
        super(JTAGIdcodeBundle, self).set_var()
        self.var(bits('version', w = 4))
        self.var(bits('partNumber', w = 16))
        self.var(bits('mfrId', w = 11))
        self.var(bits('always1'))

#/** Aggregate JTAG block IO.
#  */
class JtagBlockIO(bundle):
    def set_par(self):
        super(JtagBlockIO, self).set_par()
        self.p.par('irLength', 8)
        self.p.par('hasIdcode', 0)

    def set_var(self):
        super(JtagBlockIO, self).set_var()
        self.var(JTAGIO('jtag').flip())
        self.var(JtagControl('control'))
        self.var(JtagOutput('output', irLength = self.p.irLength))
        if (self.p.hasIdcode):
            self.var(JTAGIdcodeBundle('idcode').as_input())


class ShifterIO(bundle):
    def set_var(self):
        super(ShifterIO, self).set_var()
        self.var(bits('shift'))  ## advance the scan chain on clock high
        self.var(bits('data'))  ## as input: bit to be captured into shifter MSB on next rising edge; as output: value of shifter LSB
        self.var(bits('capture'))  ## high in the CaptureIR/DR state when this chain is selected
        self.var(bits('update'))  ## high in the UpdateIR/DR state when this chain is selected

    #/** Sets a output shifter IO's control signals from a input shifter IO's control signals.
    #  */
    def chainControlFrom(self, in_):
      self.shift /= in_.shift
      self.capture /= in_.capture
      self.update /= in_.update

#/** Internal controller block IO with data shift outputs.
#  */
class JtagControllerIO(JtagBlockIO):
    def set_var(self):
        super(JtagControllerIO, self).set_var()
        self.var(ShifterIO('dataChainOut').as_output())
        self.var(ShifterIO('dataChainIn').as_input())


class StateMachineIO(bundle):
    def set_var(self):
        super(StateMachineIO, self).set_var()
        self.var(inp('tms'))
        self.var(outp('currState', w = JtagState.width()))


class ChainIO(bundle):
    def set_var(self):
        super(ChainIO, self).set_var()
        self.var(ShifterIO('chainIn').as_input())
        self.var(ShifterIO('chainOut').as_output())


class Capture(bundle):
    def set_par(self):
        super(Capture, self).set_par()
        self.p.par('gen', None)

    def set_var(self):
        super(Capture, self).set_var()
        self.var(self.p.gen('bits').as_input())  ## data to capture, should be always valid
        self.var(outp('capture'))  ## will be high in capture state (single cycle), captured on following rising edge

class CaptureChainModIO(ChainIO):
    def set_par(self):
        super(CaptureChainModIO, self).set_par()
        self.p.par('gen', None)

    def set_var(self):
        super(CaptureChainModIO, self).set_var()
        self.var(Capture('capture', gen = self.p.gen))

class CaptureUpdateChainModIO(ChainIO):
    def set_par(self):
        super(CaptureUpdateChainModIO, self).set_par()
        self.p.par('genCapture', None)
        self.p.par('genUpdate', None)

    def set_var(self):
        super(CaptureUpdateChainModIO, self).set_var()
        self.var(Capture('capture', gen = self.p.genCapture))
        self.var(valid('update', gen = self.p.genUpdate))  ## valid high when in update state (single cycle), contents may change any time after
