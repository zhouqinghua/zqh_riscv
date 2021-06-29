import sys
import os
from phgl_imp import *
from .zqh_debug_transport_parameters import *
from .zqh_debug_bundles import DMIIO, DMIReq
from .zqh_debug_transport_bundles import *
from .zqh_debug_misc import DMIConsts
from .zqh_debug_transport_misc import dtmJTAGAddrs
from zqh_jtag.zqh_jtag_bundles import JTAGIO, JTAGIdcodeBundle
from zqh_jtag.zqh_jtag_main import CaptureUpdateChain, JtagTapGenerator

class DebugTransportModuleJTAG(module):
    def set_par(self):
        super(DebugTransportModuleJTAG, self).set_par()
        self.p.par('debugAddrBits', None)
        self.p.par('dumy', 0) #only instance module port
        self.p.par('c', JtagDTMKeyDefault())

    def check_par(self):
        super(DebugTransportModuleJTAG, self).check_par()
        self.reset_async()

    def set_port(self):
        super(DebugTransportModuleJTAG, self).set_port()
        self.io.var(DMIIO('dmi'))
        self.io.var(JTAGIO('jtag', hasTRSTn = 0).flip()) ## TODO: re-use SystemJTAGIO here?
        self.io.var(inp('jtag_reset'))
        self.io.var(inp('jtag_mfr_id', w = 11))
        self.io.var(outp('fsmReset'))

    def main(self):
        super(DebugTransportModuleJTAG, self).main()

        if (self.p.dumy):
            self.io.jtag.TDO /= 0
            self.io.dmi.req.valid /= 0
            self.io.dmi.resp.ready /= 0
            self.io.fsmReset /= 1
            return

        ##--------------------------------------------------------
        ## Reg and Wire Declarations

        dtmInfo = DTMInfo('dtmInfo')

        busyReg = reg_r('busyReg')
        stickyBusyReg = reg_r('stickyBusyReg')
        stickyNonzeroRespReg = reg_r('stickyNonzeroRespReg')

        skipOpReg = reg_r('skipOpReg') ## Skip op because we're busy
        downgradeOpReg = reg_r('downgradeOpReg') ## downgrade op because prev. failed.

        busy = bits('busy')
        nonzeroResp = bits('nonzeroResp')

        busyResp    = DMIAccessCapture('busyResp', addrBits = self.p.debugAddrBits)
        nonbusyResp = DMIAccessCapture('nonbusyResp', addrBits = self.p.debugAddrBits)
        dmiResp     = DMIAccessCapture('dmiResp', addrBits = self.p.debugAddrBits)
        nopResp     = DMIAccessCapture('nopResp', addrBits = self.p.debugAddrBits)


        dmiReqReg  = DMIReq('dmiReqReg', addrBits = self.p.debugAddrBits).as_reg(tp = 'reg_r')
        dmiReqValidReg = reg_r('dmiReqValidReg')

        dmiStatus = bits('dmiStatus', w = 2)

        ##--------------------------------------------------------
        ## DTM Info Chain Declaration

        #tmp dmiStatus /= cat([stickyNonzeroRespReg, stickyNonzeroRespReg | stickyBusyReg])
        dmiStatus /= cat([stickyNonzeroRespReg, stickyNonzeroRespReg | busy])

        dtmInfo.debugVersion   /= 1 ## This implements version 1 of the spec.
        dtmInfo.debugAddrBits  /= self.p.debugAddrBits
        dtmInfo.dmiStatus     /= dmiStatus
        dtmInfo.dmiIdleCycles /= self.p.c.debugIdleCycles
        dtmInfo.reserved0      /= 0
        dtmInfo.dmireset      /= 0 ## This is write-only
        dtmInfo.reserved1      /= 0

        dtmInfoChain = CaptureUpdateChain('dtmInfoChain', genCapture = DTMInfo, genUpdate = DTMInfo)
        dtmInfoChain.io.capture.bits /= dtmInfo

        ##--------------------------------------------------------
        ## Debug Access Chain Declaration

        dmiAccessChain = CaptureUpdateChain('dmiAccessChain',
            genCapture = lambda _: DMIAccessCapture(_, addrBits = self.p.debugAddrBits),
            genUpdate = lambda _: DMIAccessUpdate(_, addrBits = self.p.debugAddrBits))

        ##--------------------------------------------------------
        ## Debug Access Support

        ## Busy Register. We become busy when we first try to send a request.
        ## We stop being busy when we accept a response.

        with when (self.io.dmi.req.valid):
          busyReg /= 1
        with when (self.io.dmi.resp.fire()):
          busyReg /= 0

        ## We are busy during a given CAPTURE
        ## if we haven't received a valid response yet or if we
        ## were busy last time without a reset.
        ## busyReg will still be set when we check it,
        ## so the logic for checking busy looks ahead.
        busy /= (busyReg & ~self.io.dmi.resp.valid) | stickyBusyReg

        ## Downgrade/Skip. We make the decision to downgrade or skip
        ## during every CAPTURE_DR, and use the result in UPDATE_DR.
        ## The sticky versions are reset by write to dmiReset in DTM_INFO.
        with when (dmiAccessChain.io.update.valid):
          skipOpReg /= 0
          downgradeOpReg /= 0
        with when (dmiAccessChain.io.capture.capture):
          skipOpReg /= busy
          downgradeOpReg /= (~busy & nonzeroResp)
          stickyBusyReg /= busy
          stickyNonzeroRespReg /= nonzeroResp
        with when (dtmInfoChain.io.update.valid):
          with when (dtmInfoChain.io.update.bits.dmireset):
            stickyNonzeroRespReg /= 0
            stickyBusyReg /= 0

        ## Especially for the first request, we must consider dtmResp.valid,
        ## so that we don't consider junk in the FIFO to be an error response.
        ## The current specification says that any non-zero response is an error.
        ## But there is actually no case in the current design where you SHOULD get an error,
        ## as we haven't implemented Bus Masters or Serial Ports, which are the only cases errors
        ## can occur.
        nonzeroResp /= stickyNonzeroRespReg | (self.io.dmi.resp.valid & (self.io.dmi.resp.bits.resp != 0))
        vassert(~nonzeroResp, "There is no reason to get a non zero response in the current system.")
        vassert(~stickyNonzeroRespReg, "There is no reason to have a sticky non zero response in the current system.")

        busyResp.addr  /= 0
        busyResp.resp  /= value(1).to_bits().rep(DMIConsts.dmiRespSize) ## Generalizing busy to 'all-F'
        busyResp.data  /= 0

        dmiResp.addr /= dmiReqReg.addr
        dmiResp.resp /= self.io.dmi.resp.bits.resp
        dmiResp.data /= self.io.dmi.resp.bits.data

        nopResp.addr /= 0
        nopResp.resp /= 0
        nopResp.data /= 0

        ##--------------------------------------------------------
        ## Debug Access Chain Implementation

        dmiAccessChain.io.capture.bits /= mux(busy, busyResp, mux(self.io.dmi.resp.valid, dmiResp, nopResp))
        #tmp with when (dmiAccessChain.io.update.valid):
        #tmp   skipOpReg /= 0
        #tmp   downgradeOpReg /= 0
        #tmp with when (dmiAccessChain.io.capture.capture):
        #tmp   skipOpReg /= busy
        #tmp   downgradeOpReg /= (~busy & nonzeroResp)
        #tmp   stickyBusyReg /= busy
        #tmp   stickyNonzeroRespReg /= nonzeroResp

        ##--------------------------------------------------------
        ## Drive Ready Valid Interface

        dmiReqValidCheck = bits('dmiReqValidCheck', init = 0)
        vassert(~(dmiReqValidCheck & self.io.dmi.req.fire()), "Conflicting updates for dmiReqValidReg, should not happen.")

        with when (dmiAccessChain.io.update.valid):
          with when (skipOpReg):
            ## Do Nothing
            pass
          with elsewhen (downgradeOpReg | (dmiAccessChain.io.update.bits.op == DMIConsts.dmi_OP_NONE)):
            ##Do Nothing
            dmiReqReg.addr /= 0
            dmiReqReg.data /= 0
            dmiReqReg.op   /= 0
          with other():
            dmiReqReg /= dmiAccessChain.io.update.bits
            dmiReqValidReg /= 1
            dmiReqValidCheck /= 1

        with when (self.io.dmi.req.fire()):
          dmiReqValidReg /= 0

        self.io.dmi.resp.ready /= mux(
          dmiReqReg.op == DMIConsts.dmi_OP_WRITE,
            ## for write operations confirm resp immediately because we don't care about data
            self.io.dmi.resp.valid,
            ## for read operations confirm resp when we capture the data
            dmiAccessChain.io.capture.capture & ~busy)

        #zqh TBD // incorrect operation - not enough time was spent in JTAG Idle state after DMI Write
        #zqh TBD cover(dmiReqReg.op === DMIConsts.dmi_OP_WRITE & dmiAccessChain.io.capture.capture & busy, "Not enough Idle after DMI Write");
        #zqh TBD // correct operation - enough time was spent in JTAG Idle state after DMI Write
        #zqh TBD cover(dmiReqReg.op === DMIConsts.dmi_OP_WRITE & dmiAccessChain.io.capture.capture & !busy, "Enough Idle after DMI Write");

        #zqh TBD // incorrect operation - not enough time was spent in JTAG Idle state after DMI Read
        #zqh TBD cover(dmiReqReg.op === DMIConsts.dmi_OP_READ & dmiAccessChain.io.capture.capture & busy, "Not enough Idle after DMI Read");
        #zqh TBD // correct operation - enough time was spent in JTAG Idle state after DMI Read
        #zqh TBD cover(dmiReqReg.op === DMIConsts.dmi_OP_READ & dmiAccessChain.io.capture.capture & !busy, "Enough Idle after DMI Read");

        self.io.dmi.req.valid /= dmiReqValidReg

        ## This is a name-based, not type-based assignment. Do these still work?
        self.io.dmi.req.bits /= dmiReqReg

        ##--------------------------------------------------------
        ## Actual JTAG TAP
        idcode = JTAGIdcodeBundle('idcode', init = 0)
        idcode.always1    /= 1
        idcode.version    /= self.p.c.idcodeVersion
        idcode.partNumber /= self.p.c.idcodePartNum
        idcode.mfrId      /= self.io.jtag_mfr_id

        tapIO = JtagTapGenerator(irLength = 5,
          instructions = [
            (dtmJTAGAddrs.DMI_ACCESS, dmiAccessChain),
            (dtmJTAGAddrs.DTM_INFO  , dtmInfoChain)],
          icode = dtmJTAGAddrs.IDCODE
        )

        tapIO.idcode /= idcode
        tapIO.jtag /= self.io.jtag

        tapIO.control.jtag_reset /= self.io.jtag_reset

        ##--------------------------------------------------------
        ## Reset Generation (this is fed back to us by the instantiating module,
        ## and is used to reset the debug registers).

        self.io.fsmReset /= tapIO.output.reset_out
