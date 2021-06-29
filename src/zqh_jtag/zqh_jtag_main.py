#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/jtag/*.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_jtag_bundles import *
from .zqh_jtag_parameters import zqh_jtag_parameter
from .zqh_jtag_misc import *

class Chain(module):
    def check_par(self):
        super(Chain, self).check_par()
        self.reset_async()

    def set_port(self):
        super(Chain, self).set_port()

class JtagBypassChain(Chain):
    def check_par(self):
        super(JtagBypassChain, self).check_par()
        self.reset_async()

    def set_port(self):
        super(JtagBypassChain, self).set_port()
        self.io = ChainIO('io')

    def main(self):
        super(JtagBypassChain, self).main()
        self.io.chainOut.chainControlFrom(self.io.chainIn)

        reg_ = reg()  ## 10.1.1a single shift register stage

        self.io.chainOut.data /= reg_

        #zqh TBD cover(io.chainIn.capture, "bypass_chain_capture", "JTAG; bypass_chain_capture; This Bypass Chain captured data")

        with when (self.io.chainIn.capture):
          reg_ /= 0  ## 10.1.1b capture logic 0 on TCK rising
        with elsewhen (self.io.chainIn.shift):
          reg_ /= self.io.chainIn.data
        vassert(~(self.io.chainIn.capture & self.io.chainIn.update)
            & ~(self.io.chainIn.capture & self.io.chainIn.shift)
            & ~(self.io.chainIn.update & self.io.chainIn.shift))


#/** Simple shift register with parallel capture only, for read-only data registers.
#  *
#  * Number of stages is the number of bits in gen, which must have a known width.
#  *
#  * Useful notes:
#  * 7.2.1c shifter shifts on TCK rising edge
#  * 4.3.2a TDI captured on TCK rising edge, 6.1.2.1b assumed changes on TCK falling edge
#  */
class CaptureChain(Chain):
    def set_par(self):
        super(CaptureChain, self).set_par()
        self.p.par('gen', None)

    def check_par(self):
        super(CaptureChain, self).check_par()
        self.reset_async()

    def set_port(self):
        super(CaptureChain, self).set_port()
        self.io = CaptureChainModIO('io', gen = self.p.gen)

    def main(self):
        super(CaptureChain, self).main()
        self.io.chainOut.chainControlFrom(self.io.chainIn)

        n = self.io.capture.bits.get_w()

        regs = list(map(lambda _: reg() , range(n)))

        self.io.chainOut.data /= regs[0]

        #zqh TBD cover(io.chainIn.capture, "chain_capture", "JTAG; chain_capture; This Chain captured data")
        
        with when (self.io.chainIn.capture):
          capture_pack = self.io.capture.bits.pack()
          for x in range(n):
              regs[x] /= capture_pack[x]
          self.io.capture.capture /= 1
        with elsewhen (self.io.chainIn.shift):
          regs[n-1] /= self.io.chainIn.data
          for x in range(n-1):
              regs[x] /= regs[x+1]
          self.io.capture.capture /= 0
        with other():
          self.io.capture.capture /= 0
        vassert(~(self.io.chainIn.capture & self.io.chainIn.update)
            & ~(self.io.chainIn.capture & self.io.chainIn.shift)
            & ~(self.io.chainIn.update & self.io.chainIn.shift))

class CaptureUpdateChain(Chain):
    def set_par(self):
        super(CaptureUpdateChain, self).set_par()
        self.p.par('genCapture', None)
        self.p.par('genUpdate', None)

    def check_par(self):
        super(CaptureUpdateChain, self).check_par()
        self.reset_async()

    def set_port(self):
        super(CaptureUpdateChain, self).set_port()
        self.io = CaptureUpdateChainModIO(
            'io',
            genCapture = self.p.genCapture, 
            genUpdate = self.p.genUpdate)
    
    def main(self):
        super(CaptureUpdateChain, self).main()
        self.io.chainOut.chainControlFrom(self.io.chainIn)

        captureWidth = self.io.capture.bits.get_w()
        updateWidth = self.io.update.bits.get_w()
        n = max(captureWidth, updateWidth)

        regs = list(map(lambda _: reg(), range(n)))

        self.io.chainOut.data /= regs[0]

        updateBits = cat_rvs(regs)[updateWidth-1: 0]
        self.io.update.bits /= updateBits

        captureBits = self.io.capture.bits.pack()

        #zqh TBD cover(io.chainIn.capture, "chain_capture", "JTAG;chain_capture; This Chain captured data")
        #zqh TBD cover(io.chainIn.capture, "chain_update",  "JTAG;chain_update; This Chain updated data")

        with when (self.io.chainIn.capture):
          for x in range(min(n, captureWidth)):
              regs[x] /= captureBits[x]
          for x in range(captureWidth, n):
              regs[x] /= 0
          self.io.capture.capture /= 1
          self.io.update.valid /= 0
        with elsewhen (self.io.chainIn.update):
          self.io.capture.capture /= 0
          self.io.update.valid /= 1
        with elsewhen (self.io.chainIn.shift):
          regs[n-1] /= self.io.chainIn.data
          for x in range(n-1):
              regs[x] /= regs[x+1]
          self.io.capture.capture /= 0
          self.io.update.valid /= 0
        with other():
          self.io.capture.capture /= 0
          self.io.update.valid /= 0
        vassert(~(self.io.chainIn.capture & self.io.chainIn.update)
            & ~(self.io.chainIn.capture & self.io.chainIn.shift)
            & ~(self.io.chainIn.update & self.io.chainIn.shift))

class JtagStateMachine(module):
    def check_par(self):
        super(JtagStateMachine, self).check_par()
        self.reset_async()

    def set_port(self):
        super(JtagStateMachine, self).set_port()
        self.io = StateMachineIO('io')

    def main(self):
        super(JtagStateMachine, self).main()

        nextState = bits('nextState', w = JtagState.width())
        currStateReg = reg_rs(
            'currStateReg', 
            w = JtagState.width(),
            rs = JtagState.TestLogicReset)
        currStateReg /= nextState
        currState = currStateReg

        with when(currState == JtagState.TestLogicReset):
          nextState /= mux(self.io.tms, JtagState.TestLogicReset, JtagState.RunTestIdle)
        with when(currState == JtagState.RunTestIdle):
          nextState /= mux(self.io.tms, JtagState.SelectDRScan, JtagState.RunTestIdle)
        with when(currState == JtagState.SelectDRScan):
          nextState /= mux(self.io.tms, JtagState.SelectIRScan, JtagState.CaptureDR)
        with when(currState == JtagState.CaptureDR):
          nextState /= mux(self.io.tms, JtagState.Exit1DR, JtagState.ShiftDR)
        with when(currState == JtagState.ShiftDR):
          nextState /= mux(self.io.tms, JtagState.Exit1DR, JtagState.ShiftDR)
        with when(currState == JtagState.Exit1DR):
          nextState /= mux(self.io.tms, JtagState.UpdateDR, JtagState.PauseDR)
        with when(currState == JtagState.PauseDR):
          nextState /= mux(self.io.tms, JtagState.Exit2DR, JtagState.PauseDR)
        with when(currState == JtagState.Exit2DR):
          nextState /= mux(self.io.tms, JtagState.UpdateDR, JtagState.ShiftDR)
        with when(currState == JtagState.UpdateDR):
          nextState /= mux(self.io.tms, JtagState.SelectDRScan, JtagState.RunTestIdle)
        with when(currState == JtagState.SelectIRScan):
          nextState /= mux(self.io.tms, JtagState.TestLogicReset, JtagState.CaptureIR)
        with when(currState == JtagState.CaptureIR):
          nextState /= mux(self.io.tms, JtagState.Exit1IR, JtagState.ShiftIR)
        with when(currState == JtagState.ShiftIR):
          nextState /= mux(self.io.tms, JtagState.Exit1IR, JtagState.ShiftIR)
        with when(currState == JtagState.Exit1IR):
          nextState /= mux(self.io.tms, JtagState.UpdateIR, JtagState.PauseIR)
        with when(currState == JtagState.PauseIR):
          nextState /= mux(self.io.tms, JtagState.Exit2IR, JtagState.PauseIR)
        with when(currState == JtagState.Exit2IR):
          nextState /= mux(self.io.tms, JtagState.UpdateIR, JtagState.ShiftIR)
        with when(currState == JtagState.UpdateIR):
          nextState /= mux(self.io.tms, JtagState.SelectDRScan, JtagState.RunTestIdle)

        self.io.currState /= currState

        #zqh TBD // Generate Coverate Points
        #zqh TBD JtagState.State.all.foreach { s => 
        #zqh TBD   cover (currState === s.U && io.tms === true.B,  s"${s.toString}_tms_1", s"JTAG; ${s.toString} with TMS = 1; State Transition from ${s.toString} with TMS = 1")
        #zqh TBD   cover (currState === s.U && io.tms === false.B, s"${s.toString}_tms_0", s"JTAG; ${s.toString} with TMS = 0; State Transition from ${s.toString} with TMS = 0")
        #zqh TBD  cover (currState === s.U && reset.toBool === true.B, s"${s.toString}_reset", s"JTAG; ${s.toString} with reset; JTAG Reset asserted during ${s.toString}")
 
        #zqh TBD }


#/** JTAG TAP controller internal block, responsible for instruction decode and data register chain
#  * control signal generation.
#  *
#  * Misc notes:
#  * - Figure 6-3 and 6-4 provides examples with timing behavior
#  */
class JtagTapController(module):
    def set_par(self):
        super(JtagTapController, self).set_par()
        self.p = zqh_jtag_parameter()

    def check_par(self):
        super(JtagTapController, self).check_par()
        assert(self.p.irLength >= 2)  ## 7.1.1a
        self.reset_async()

    def set_port(self):
        super(JtagTapController, self).set_port()
        self.io = JtagControllerIO('io', irLength = self.p.irLength)

    def main(self):
        super(JtagTapController, self).main()

        tdo = bits('tdo', init =0)  ## 4.4.1c TDI should appear here uninverted after shifting
        tdo_driven = bits('tdo_driven', init = 0)
        self.io.jtag.TDO /= reg('tdoReg', next = tdo, clock_edge = 'negedge')  ## 4.5.1a TDO changes on falling edge of TCK, 6.1.2.1d driver active on first TCK falling edge in ShiftIR and ShiftDR states
        #zqh TBD self.io.jtag.TDO.driven /= reg('tdoeReg', next = tdo_driven, clock_edge = 'negedge')

        ##
        ## JTAG state machine
        ##

        currState = bits('currState', w = 4)

        ## At this point, the TRSTn should already have been
        ## combined with any POR, and it should also be
        ## synchronized to TCK.
        #zqh TBD require(!io.jtag.TRSTn.isDefined, "TRSTn should be absorbed into jtckPOReset outside of JtagTapController.")

        stateMachine = JtagStateMachine('stateMachine')
        stateMachine.io.reset /= self.io.control.jtag_reset
        stateMachine.io.tms /= self.io.jtag.TMS
        currState /= stateMachine.io.currState
        self.io.output.state /= stateMachine.io.currState

        ##
        ## Instruction Register
        ##
        ## 7.1.1d IR shifter two LSBs must be b01 pattern
        ## TODO: 7.1.1d allow design-specific IR bits, 7.1.1e (rec) should be a fixed pattern
        ## 7.2.1a behavior of instruction register and shifters
        irChain = CaptureUpdateChain(
            'irChain', 
            genCapture = lambda _: bits(_, w = self.p.irLength),
            genUpdate = lambda _: bits(_, w = self.p.irLength))
        irChain.io.chainIn.shift /= currState == JtagState.ShiftIR
        irChain.io.chainIn.data /= self.io.jtag.TDI
        irChain.io.chainIn.capture /= currState == JtagState.CaptureIR
        irChain.io.chainIn.update /= currState == JtagState.UpdateIR
        irChain.io.capture.bits /= 0b01

        updateInstruction = bits('updateInstruction', init = 1)

        nextActiveInstruction = bits('nextActiveInstruction', w = self.p.irLength)
        activeInstruction = reg_en_rs(
            'irReg',
            w = self.p.irLength,
            rs = self.p.initialInstruction, 
            next = nextActiveInstruction,
            en = updateInstruction, 
            clock_edge = 'negedge')   ## 7.2.1d active instruction output latches on TCK falling edge

        with when (currState == JtagState.UpdateIR):
          nextActiveInstruction /= irChain.io.update.bits
          updateInstruction /= 1
        with other():
          ##!!! Needed when using chisel3._ (See #1160)
          ## nextActiveInstruction := DontCare
          updateInstruction /= 0
        self.io.output.instruction /= activeInstruction

        self.io.output.reset_out /= currState == JtagState.TestLogicReset

        ##
        ## Data Register
        ##
        self.io.dataChainOut.shift /= currState == JtagState.ShiftDR
        self.io.dataChainOut.data /= self.io.jtag.TDI
        self.io.dataChainOut.capture /= currState == JtagState.CaptureDR
        self.io.dataChainOut.update /= currState == JtagState.UpdateDR

        ##
        ## Output Control
        ##
        with when (currState == JtagState.ShiftDR):
          tdo /= self.io.dataChainIn.data
          tdo_driven /= 1
        with elsewhen (currState == JtagState.ShiftIR):
          tdo /= irChain.io.chainOut.data
          tdo_driven /= 1
        with other():
          ##!!! Needed when using chisel3._ (See #1160)
          ##tdo := DontCare
          tdo_driven /= 0

def JtagTapGenerator (irLength, instructions, icode = None):
    #/** JTAG TAP generator, enclosed module must be clocked from TCK and reset from output of this
    #  * block.
    #  *
    #  * @param irLength length, in bits, of instruction register, must be at least 2
    #  * @param instructions map of instruction codes to data register chains that select that data
    #  * register; multiple instructions may map to the same data chain
    #  * @param idcode optional idcode instruction. idcode UInt will come from outside this core.
    #  *
    #  * @note all other instruction codes (not part of instructions or idcode) map to BYPASS
    #  * @note initial instruction is idcode (if supported), otherwise all ones BYPASS
    #  *
    #  * Usage notes:
    #  * - 4.3.1b TMS must appear high when undriven
    #  * - 4.3.1c (rec) minimize load presented by TMS
    #  * - 4.4.1b TDI must appear high when undriven
    #  * - 4.5.1b TDO must be inactive except when shifting data (undriven? 6.1.2)
    #  * - 6.1.3.1b TAP controller must not be (re-?)initialized by system reset (allows
    #  *   boundary-scan testing of reset pin)
    #  *   - 6.1 TAP controller can be initialized by a on-chip power on reset generator, the same one
    #  *     that would initialize system logic
    #  *
    #  * TODO:
    #  * - support concatenated scan chains
    #  */

    internalIo = JtagBlockIO(
        'internalIo', 
        irLength = irLength,
        hasIdcode = 1 if (icode is not None) else 0).as_bits()


    ## Create IDCODE chain if needed
    if (icode is not None):
        assert(not (icode in list(map(lambda _: _[0], instructions)))), "instructions may not contain IDCODE"
        idcodeChain = CaptureChain('idcodeChain', gen = JTAGIdcodeBundle)
        i = internalIo.idcode.pack()
        vassert(i % 2 == 1, "LSB must be set in IDCODE, see 12.1.1d")
        vassert(((i >> 1) & ((1 << 11) - 1)) != JtagIdcode.dummyMfrId(),
          "IDCODE must not have 0b00001111111 as manufacturer identity, see 12.2.1b")
        idcodeChain.io.capture.bits /= internalIo.idcode
        allInstructions = instructions + [(icode, idcodeChain)]
    else:
        allInstructions = instructions



    bypassIcode = (1 << irLength) - 1  ## required BYPASS instruction
    initialInstruction = icode if (icode is not None) else bypassIcode ## 7.2.1e load IDCODE or BYPASS instruction after entry into TestLogicReset

    assert(not (bypassIcode in list(map(lambda _: _[0], allInstructions)))), "instructions may not contain BYPASS code"

    controllerInternal = JtagTapController(
        'controllerInternal',
        irLength = irLength,
        initialInstruction = initialInstruction)

    unusedChainOut = ShifterIO('unusedChainOut')  ## De-selected chain output
    unusedChainOut.shift /= 0
    unusedChainOut.data /= 0
    unusedChainOut.capture /= 0
    unusedChainOut.update /= 0

    bypassChain = JtagBypassChain('bypassChain')

    ## The Great Data Register Chain Mux
    bypassChain.io.chainIn /= controllerInternal.io.dataChainOut  ## for simplicity, doesn't visibly affect anything else
    assert(len(allInstructions) > 0), "Seriously? JTAG TAP with no instructions?"

    chainToIcode = list(map(lambda _: list(reversed(_)), allInstructions))

    chainToSelect = list(map(
        lambda _: (_[0], controllerInternal.io.output.instruction == _[1]),
        chainToIcode))

    controllerInternal.io.dataChainIn /= sel_p_lsb(
        map(lambda _: _[1], chainToSelect),
        map(lambda _: _[0].io.chainOut, chainToSelect),
        bypassChain.io.chainOut)


    for x in chainToSelect:
      (chain, select) = x
      with when (select):
        chain.io.chainIn /= controllerInternal.io.dataChainOut
      with other():
        chain.io.chainIn /= unusedChainOut


    controllerInternal.io.jtag /= internalIo.jtag
    internalIo.control /= controllerInternal.io.control
    internalIo.output /= controllerInternal.io.output

    return internalIo
