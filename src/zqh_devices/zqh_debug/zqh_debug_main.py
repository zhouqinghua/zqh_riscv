####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/devices/debug/Debug.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_debug_parameters import DefaultDebugModuleParams
from .zqh_debug_parameters import zqh_debug_dmi2tl_parameter
from .zqh_debug_parameters import zqh_debug_dmi_inside_parameter
from .zqh_debug_bundles import *
from .zqh_debug_dm_registers import *
from .zqh_debug_misc import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from zqh_tilelink.zqh_tilelink_bundles import zqh_tl_bundle
from zqh_tilelink.zqh_tilelink_misc import TMSG_CONSTS
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_master_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_slave_io_parameter
from zqh_tilelink.zqh_tilelink_node_parameters import zqh_tilelink_node_xbar_parameter
from zqh_common.zqh_address_space import zqh_address_space
from zqh_common.zqh_address_space import zqh_address_attr
from zqh_common.zqh_address_space import zqh_order_type
from zqh_common.zqh_transfer_size import zqh_transfer_size
from zqh_core_common.zqh_core_common_misc import I_CONSTS
from zqh_core_common.zqh_core_common_misc import M_CONSTS

class zqh_debug_inside_addr_fix_module(module):
    def set_par(self):
        super(zqh_debug_inside_addr_fix_module, self).set_par()
        self.p.par('addr_offset', None)
        self.p.par('bundle_in', None)
        self.p.par('node', None)

    def set_port(self):
        super(zqh_debug_inside_addr_fix_module, self).set_port()
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.bundle_in).flip())
        self.io.var(zqh_tl_bundle('tl_out', p = self.p.bundle_in))

    def main(self):
        super(zqh_debug_inside_addr_fix_module, self).main()
        self.io.tl_out /= self.io.tl_in
        self.io.tl_out.a.bits.address /= self.io.tl_in.a.bits.address + self.p.addr_offset

def zqh_debug_inside_addr_fix(node, tl_in, p):
    inside_addr_fix = zqh_debug_inside_addr_fix_module(
        'inside_addr_fix',
        addr_offset = p, 
        bundle_in = tl_in.p,
        node = node)
    inside_addr_fix .io.tl_in /= tl_in
    return inside_addr_fix.io.tl_out

class zqh_debug_outside(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_debug_outside, self).set_par()
        self.p = zqh_debug_dmi2tl_parameter()

    def check_par(self):
        super(zqh_debug_outside, self).check_par()
        self.reset_async()

    def gen_node_tree(self):
        super(zqh_debug_outside, self).gen_node_tree()
        self.gen_node_master('tl_master', bundle_p = self.p.tl_bundle_p)

    def set_port(self):
        super(zqh_debug_outside, self).set_port()
        self.io.var(ClockedDMIIO('dmi_in').flip())
        self.io.var(inp('clock_tl'))
        self.io.var(inp('reset_tl'))
        self.io.var(ready_valid('dmcontrol', gen = DebugInternalBundle))
        self.io.var(DebugCtrlBundle('ctrl', nComponents = self.p.nComponents))
        self.io.var(outp('int_flag', w = self.p.nComponents))

    def main(self):
        super(zqh_debug_outside, self).main()
        self.gen_node_interface('tl_master')
        assert(self.tl_out.a.bits.p.data_bits == DMIConsts.dmiDataSize)
        assert(self.tl_out.a.bits.p.address_bits >= (self.io.dmi_in.dmi.req.bits.addr.get_w() + log2_ceil(DMIConsts.dmiDataSize//8)))

        access_op_wr = self.io.dmi_in.dmi.req.bits.op == DMIConsts.dmi_OP_WRITE
        access_dmcontrol = self.io.dmi_in.dmi.req.bits.addr == DMI_RegAddrs.DMI_DMCONTROL

        self.io.dmi_in.dmi.req.ready /= 0

        dmcontrol_fifo = async_queue(
            'dmcontrol_fifo', 
            gen = DebugInternalBundle,
            entries = 4)
        dmcontrol_fifo.io.enq_clock /= self.io.clock #dmi's
        dmcontrol_fifo.io.enq_reset /= self.io.reset #dmi's
        dmcontrol_fifo.io.deq_clock /= self.io.clock_tl #tilelink's
        dmcontrol_fifo.io.deq_reset /= self.io.reset_tl #tilelink's
        self.io.dmcontrol /= dmcontrol_fifo.io.deq

        #must in dmi's clock domain
        dmcontrol_reg = DMCONTROLFields('dmcontrol_reg').as_reg(tp = 'reg_r')
        self.io.ctrl.ndreset /= dmcontrol_reg.ndmreset
        self.io.ctrl.dmactive /= dmcontrol_reg.dmactive

        dmcontrol_access_valid = self.io.dmi_in.dmi.req.fire() & access_dmcontrol
        dmcontrol_wr_valid = self.io.dmi_in.dmi.req.fire() & access_op_wr & access_dmcontrol
        dmcontrol_wr_data = DMCONTROLFields(
            'dmcontrol_wr_data',
            init = self.io.dmi_in.dmi.req.bits.data)
        dmcontrol_resp_flag = reg_r('dmcontrol_resp_flag')
        dmcontrol_fifo.io.enq.valid /= 0
        dmcontrol_fifo.io.enq.bits.resumereq /= dmcontrol_wr_data.resumereq
        dmcontrol_fifo.io.enq.bits.hartsel /= dmcontrol_wr_data.hartsello
        dmcontrol_fifo.io.enq.bits.ackhavereset /= dmcontrol_wr_data.ackhavereset

        with when(access_dmcontrol):
            with when(access_op_wr):
                with when(~dmcontrol_resp_flag):
                    self.io.dmi_in.dmi.req.ready /= dmcontrol_fifo.io.enq.ready
                    dmcontrol_fifo.io.enq.valid /= self.io.dmi_in.dmi.req.valid
            with other():
                with when(~dmcontrol_resp_flag):
                    self.io.dmi_in.dmi.req.ready /= 1

        with when(dmcontrol_access_valid):
            dmcontrol_resp_flag /= 1

        self.io.dmi_in.dmi.resp.valid /= 0
        with when(dmcontrol_resp_flag):
            self.io.dmi_in.dmi.resp.valid /= 1
            self.io.dmi_in.dmi.resp.bits.resp /= DMIConsts.dmi_RESP_SUCCESS
            self.io.dmi_in.dmi.resp.bits.data /= dmcontrol_reg.pack()
            with when(self.io.dmi_in.dmi.resp.fire()):
                dmcontrol_resp_flag /= 0

        with when(~dmcontrol_reg.dmactive):
            dmcontrol_reg /= 0
        with elsewhen(dmcontrol_wr_valid):
            dmcontrol_reg.ndmreset     /= dmcontrol_wr_data.ndmreset
            dmcontrol_reg.hartsello    /= dmcontrol_wr_data.hartsello
            dmcontrol_reg.haltreq      /= dmcontrol_wr_data.haltreq
            dmcontrol_reg.resumereq    /= dmcontrol_wr_data.resumereq
            dmcontrol_reg.ackhavereset /= dmcontrol_wr_data.ackhavereset

        with when (dmcontrol_wr_valid):
            dmcontrol_reg.dmactive /= dmcontrol_wr_data.dmactive


        ##--------------------------------------------------------------
        ## Interrupt Registers
        ##--------------------------------------------------------------

        debugIntNxt = vec('debugIntNxt', gen = bits, n = self.p.nComponents, init = 0)
        debugIntRegs = vec('debugIntRegs', gen = reg_r, n = self.p.nComponents)
        debugIntRegs /= debugIntNxt

        debugIntNxt /= debugIntRegs

        ## Halt request registers are set & cleared by writes to DMCONTROL.haltreq
        ## resumereq also causes the core to execute a 'dret',
        ## so resumereq is passed through to Inner.
        ## hartsel must also be used by the DebugModule state machine,
        ## so it is passed to Inner.
        ## It is true that there is no backpressure -- writes
        ## which occur 'too fast' will be dropped.

        for component in range(self.p.nComponents):
          with when (~dmcontrol_reg.dmactive):
            debugIntNxt[component] /= 0
          with other():
            with when (dmcontrol_wr_valid & (dmcontrol_wr_data.hartsello == component)):
              debugIntNxt[component] /= dmcontrol_wr_data.haltreq

        self.io.int_flag /= debugIntRegs.pack()


        tl_a_fifo = async_queue(
            'tl_a_fifo', 
            gen = type(self.tl_out.a.bits),
            gen_p = self.tl_out.a.bits.p, 
            entries = 4)
        tl_a_fifo.io.enq_clock /= self.io.clock #dmi's
        tl_a_fifo.io.enq_reset /= self.io.reset #dmi's
        tl_a_fifo.io.deq_clock /= self.io.clock_tl
        tl_a_fifo.io.deq_reset /= self.io.reset_tl

        with when(~access_dmcontrol):
            self.io.dmi_in.dmi.req.ready /= tl_a_fifo.io.enq.ready
        tl_a_fifo.io.enq.valid /= self.io.dmi_in.dmi.req.valid & ~access_dmcontrol
        tl_a_fifo.io.enq.bits.opcode /= mux(
            self.io.dmi_in.dmi.req.bits.op == DMIConsts.dmi_OP_WRITE,
            TMSG_CONSTS.put_full_data(),
            TMSG_CONSTS.get())
        tl_a_fifo.io.enq.bits.param /= 0
        tl_a_fifo.io.enq.bits.size /= 2
        tl_a_fifo.io.enq.bits.source /= 0
        tl_a_fifo.io.enq.bits.address /= self.io.dmi_in.dmi.req.bits.addr << 2
        tl_a_fifo.io.enq.bits.mask /= value(1).to_bits().rep(
            tl_a_fifo.io.enq.bits.data.get_w()//8)
        tl_a_fifo.io.enq.bits.data /= self.io.dmi_in.dmi.req.bits.data
        self.tl_out.a /= tl_a_fifo.io.deq


        tl_d_fifo = async_queue(
            'tl_d_fifo', 
            gen = type(self.tl_out.d.bits),
            gen_p = self.tl_out.d.bits.p,
            entries = 4)
        tl_d_fifo.io.enq_clock /= self.io.clock_tl
        tl_d_fifo.io.enq_reset /= self.io.reset_tl
        tl_d_fifo.io.deq_clock /= self.io.clock #dmi's
        tl_d_fifo.io.deq_reset /= self.io.reset #dmi's

        tl_d_fifo.io.enq /= self.tl_out.d
        tl_d_fifo.io.deq.ready /= 0
        with when(~dmcontrol_resp_flag):
            tl_d_fifo.io.deq.ready /= self.io.dmi_in.dmi.resp.ready
            self.io.dmi_in.dmi.resp.valid /= tl_d_fifo.io.deq.valid
            self.io.dmi_in.dmi.resp.bits.resp /= mux(
                tl_d_fifo.io.deq.bits.error,
                DMIConsts.dmi_RESP_FAILURE,
                DMIConsts.dmi_RESP_SUCCESS)
            self.io.dmi_in.dmi.resp.bits.data /= tl_d_fifo.io.deq.bits.data

class zqh_debug_dmi_inside(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_debug_dmi_inside, self).set_par()
        self.p = zqh_debug_dmi_inside_parameter()

    def gen_node_tree(self):
        super(zqh_debug_dmi_inside, self).gen_node_tree()
        self.gen_node_slave('inside_slave', bundle_p = self.p.gen_tl_bundle_p())

        self.gen_node_master(
            'sb_master', 
            size_min = 0,
            size_max = self.p.maxSupportedSBAccess//8, 
            bundle_p = self.p.gen_sb_tl_master_bundle_p())

    def set_port(self):
        super(zqh_debug_dmi_inside, self).set_port()
        self.io.var(inp('dmactive'))
        self.io.var(inp('debugUnavail'))
        self.io.var(ready_valid('dmcontrol', gen = DebugInternalBundle).flip())

    def main(self):
        super(zqh_debug_dmi_inside, self).main()
        self.gen_node_interface('inside_slave')
        self.gen_node_interface('sb_master')
        assert(self.tl_in[0].a.bits.data.get_w() == 32)


        ##--------------------------------------------------------------
        ## Sanity Check Configuration For this implementation.
        ##--------------------------------------------------------------

        assert(self.p.supportQuickAccess == 0), "No Quick Access support yet"
        assert(self.p.supportHartArray == 0), "No Hart Array support yet"

        dmactive_sync = async_dff_rs(self.io.dmactive, self.p.sync_delay, rs = 0)

        ##--------------------------------------------------------------
        ## Register & Wire Declarations (which need to be pre-declared)
        ##--------------------------------------------------------------

        haltedBitRegs    = vec('haltedBitRegs', gen = reg_r, n = self.p.nComponents)
        resumeReqRegs    = vec('resumeReqRegs', gen = reg_r, n = self.p.nComponents)
        haveResetBitRegs = vec('haveResetBitRegs', gen = reg_s, n = self.p.nComponents)


        ## --- regmapper outputs

        hartHaltedWrEn       = bits('hartHaltedWrEn', init = 0)
        hartHaltedId         = bits('hartHaltedId', w = DsbBusConsts.sbIdWidth)
        hartGoingWrEn        = bits('hartGoingWrEn', init = 0)
        hartGoingId          = bits('hartGoingId', w = DsbBusConsts.sbIdWidth)
        hartResumingWrEn     = bits('hartResumingWrEn', init = 0)
        hartResumingId       = bits('hartResumingId', w = DsbBusConsts.sbIdWidth)
        hartExceptionWrEn    = bits('hartExceptionWrEn', init = 0)
        hartExceptionId      = bits('hartExceptionId', w = DsbBusConsts.sbIdWidth)

        dmiProgramBufferRdEn = vec(
            'dmiProgramBufferRdEn',
            gen = bits,
            n = self.p.nProgramBufferWords * 4,
            init = 0)
        dmiProgramBufferAccessLegal = bits('dmiProgramBufferAccessLegal', init = 0)
        dmiProgramBufferWrEnMaybe = vec(
            'dmiProgramBufferWrEnMaybe', 
            gen = bits,
            n = self.p.nProgramBufferWords * 4,
            init = 0)

        dmiAbstractDataRdEn = vec(
            'dmiAbstractDataRdEn', 
            gen = bits,
            n = self.p.nAbstractDataWords * 4,
            init = 0)
        dmiAbstractDataAccessLegal = bits('dmiAbstractDataAccessLegal', init = 0)
        dmiAbstractDataWrEnMaybe = vec(
            'dmiAbstractDataWrEnMaybe', 
            gen = bits, 
            n = self.p.nAbstractDataWords * 4, 
            init = 0)

        ##--------------------------------------------------------------
        ## Registers coming from 'CONTROL' in Outer
        ##--------------------------------------------------------------

        selectedHartReg = reg_r('selectedHartReg', w = 10)

        with when (self.io.dmcontrol.fire()):
          selectedHartReg /= self.io.dmcontrol.bits.hartsel

        self.io.dmcontrol.ready /= 1


        ##--------------------------------------------------------------
        ## DMI Registers
        ##--------------------------------------------------------------

        ##----DMSTATUS

        DMSTATUSRdData = DMSTATUSFields('DMSTATUSRdData', init = 0)
        DMSTATUSRdData.authenticated /= 1 ## Not implemented
        DMSTATUSRdData.version       /= 2    ## Version 0.13

        with when (selectedHartReg >= self.p.nComponents):
          DMSTATUSRdData.allnonexistent /= 1
          DMSTATUSRdData.anynonexistent /= 1
        with elsewhen (self.io.debugUnavail[selectedHartReg]):
          DMSTATUSRdData.allunavail /= 1
          DMSTATUSRdData.anyunavail /= 1
        with elsewhen (haltedBitRegs[selectedHartReg]):
          DMSTATUSRdData.allhalted /= 1
          DMSTATUSRdData.anyhalted /= 1
        with other():
          DMSTATUSRdData.allrunning /= 1
          DMSTATUSRdData.anyrunning /= 1
         
        DMSTATUSRdData.allhavereset /= haveResetBitRegs[selectedHartReg]
        DMSTATUSRdData.anyhavereset /= haveResetBitRegs[selectedHartReg]


        resumereq = self.io.dmcontrol.fire() & self.io.dmcontrol.bits.resumereq

        with when (self.io.dmcontrol.fire()):
          with when (self.io.dmcontrol.bits.ackhavereset):
            haveResetBitRegs.idx_write(self.io.dmcontrol.bits.hartsel, 0)

        DMSTATUSRdData.allresumeack /= ~resumeReqRegs[selectedHartReg] & ~resumereq
        DMSTATUSRdData.anyresumeack /= ~resumeReqRegs[selectedHartReg] & ~resumereq

        ##TODO
        DMSTATUSRdData.devtreevalid /= 0

        DMSTATUSRdData.impebreak /= self.p.hasImplicitEbreak


        ##----HARTINFO

        HARTINFORdData = HARTINFOFields('HARTINFORdData', init = 0)
        HARTINFORdData.dataaccess  /= 1
        HARTINFORdData.datasize    /= self.p.nAbstractDataWords
        HARTINFORdData.dataaddr    /= DsbRegAddrs.DATA
        HARTINFORdData.nscratch    /= self.p.nScratch

        ##----HALTSUM*
        numHaltedStatus = ((self.p.nComponents - 1) // 32) + 1
        haltedStatus   = vec('haltedStatus', gen = bits, n = numHaltedStatus, w = 32)

        for ii in range(numHaltedStatus):
            end_idx = ii * 32 + len(haltedBitRegs)
            haltedStatus[ii] /= cat_rvs(map(
                lambda _: haltedBitRegs[_], 
                range(ii * 32, end_idx)))

        haltedSummary = cat_rvs(map(lambda _: _.r_or(), haltedStatus))
        HALTSUM1RdData = HALTSUM1Fields('HALTSUM1RdData', init = haltedSummary)

        selectedHaltedStatus = mux(
            (selectedHartReg >> 5) > numHaltedStatus,
            0, 
            haltedStatus[selectedHartReg >> 5])
        HALTSUM0RdData = HALTSUM0Fields('HALTSUM0RdData', init = selectedHaltedStatus)

        ## Since we only support 1024 harts, we don't implement HALTSUM2 or HALTSUM3


        ##----ABSTRACTCS

        ABSTRACTCSReset = ABSTRACTCSFields('ABSTRACTCSReset', init = 0)
        ABSTRACTCSReset.datacount   /= self.p.nAbstractDataWords
        ABSTRACTCSReset.progbufsize /= self.p.nProgramBufferWords

        ABSTRACTCSReg       = ABSTRACTCSFields('ABSTRACTCSReg').as_reg()
        ABSTRACTCSWrDataVal = bits('ABSTRACTCSWrDataVal', w = 32, init = 0)
        ABSTRACTCSWrData    = ABSTRACTCSFields(
            'ABSTRACTCSWrData', 
            init = ABSTRACTCSWrDataVal)
        ABSTRACTCSRdData    = ABSTRACTCSFields('ABSTRACTCSRdData', init = ABSTRACTCSReg)

        ABSTRACTCSRdEn = bits('ABSTRACTCSRdEn', init = 0)
        ABSTRACTCSWrEnMaybe = bits('ABSTRACTCSWrEnMaybe', init = 0)

        ABSTRACTCSWrEnLegal = bits('ABSTRACTCSWrEnLegal', init = 0)
        ABSTRACTCSWrEn      = ABSTRACTCSWrEnMaybe & ABSTRACTCSWrEnLegal

        errorBusy        = bits('errorBusy', init = 0)
        errorException   = bits('errorException', init = 0)
        errorUnsupported = bits('errorUnsupported', init = 0)
        errorHaltResume  = bits('errorHaltResume', init = 0)

        with when(~dmactive_sync):
          ABSTRACTCSReg /= ABSTRACTCSReset
        with other():
          with when (errorBusy):
            ABSTRACTCSReg.cmderr /= DebugAbstractCommandError.ErrBusy
          with elsewhen (errorException):
            ABSTRACTCSReg.cmderr /= DebugAbstractCommandError.ErrException
          with elsewhen (errorUnsupported):
            ABSTRACTCSReg.cmderr /= DebugAbstractCommandError.ErrNotSupported
          with elsewhen (errorHaltResume):
            ABSTRACTCSReg.cmderr /= DebugAbstractCommandError.ErrHaltResume
          with other():
            with when (ABSTRACTCSWrEn):
              ABSTRACTCSReg.cmderr /= ABSTRACTCSReg.cmderr & ~(ABSTRACTCSWrData.cmderr)

        ## For busy, see below state machine.
        abstractCommandBusy = bits('abstractCommandBusy', init = 1)
        ABSTRACTCSRdData.busy /= abstractCommandBusy


        ##---- ABSTRACTAUTO

        ABSTRACTAUTOReset     = ABSTRACTAUTOFields('ABSTRACTAUTOReset', init = 0)
        ABSTRACTAUTOReg       = ABSTRACTAUTOFields('ABSTRACTAUTOReg').as_reg()
        ABSTRACTAUTOWrDataVal = bits('ABSTRACTAUTOWrDataVal', w = 32, init = 0)
        ABSTRACTAUTOWrData    = ABSTRACTAUTOFields(
            'ABSTRACTAUTOWrData', 
            init = ABSTRACTAUTOWrDataVal)
        ABSTRACTAUTORdData    = ABSTRACTAUTOFields(
            'ABSTRACTAUTORdData',
            init = ABSTRACTAUTOReg)

        ABSTRACTAUTORdEn = bits('ABSTRACTAUTORdEn', init = 0)
        ABSTRACTAUTOWrEnMaybe = bits('ABSTRACTAUTOWrEnMaybe', init = 0)

        ABSTRACTAUTOWrEnLegal = bits('ABSTRACTAUTOWrEnLegal', init = 0)
        ABSTRACTAUTOWrEn      = ABSTRACTAUTOWrEnMaybe & ABSTRACTAUTOWrEnLegal

        with when (~dmactive_sync):
          ABSTRACTAUTOReg /= ABSTRACTAUTOReset
        with elsewhen (ABSTRACTAUTOWrEn):
          ABSTRACTAUTOReg.autoexecprogbuf /= (
                ABSTRACTAUTOWrData.autoexecprogbuf & 
                ((1 << self.p.nProgramBufferWords) - 1))
          ABSTRACTAUTOReg.autoexecdata /= (
                ABSTRACTAUTOWrData.autoexecdata & 
                ((1 << self.p.nAbstractDataWords) - 1))

        dmiAbstractDataAccessVec  = vec(
            'dmiAbstractDataAccessVec',
            gen = bits,
            n = self.p.nAbstractDataWords * 4,
            init = 0)
        for i in range(self.p.nAbstractDataWords * 4):
            dmiAbstractDataAccessVec[i] /= (
                dmiAbstractDataWrEnMaybe[i] | dmiAbstractDataRdEn[i])

        dmiProgramBufferAccessVec  = vec(
            'dmiProgramBufferAccessVec',
            gen = bits, 
            n = self.p.nProgramBufferWords * 4, 
            init = 0)
        for i in range(self.p.nProgramBufferWords * 4):
            dmiProgramBufferAccessVec[i] /= (
                dmiProgramBufferWrEnMaybe[i] | dmiProgramBufferRdEn[i])

        dmiAbstractDataAccess  = reduce(lambda a,b: a | b, dmiAbstractDataAccessVec)
        dmiProgramBufferAccess = reduce(lambda a,b: a | b, dmiProgramBufferAccessVec)

        ## This will take the shorter of the lists, which is what we want.
        autoexecData  = vec(
            'autoexecData', 
            gen = bits, 
            n = self.p.nAbstractDataWords, 
            init = 0)
        autoexecProg  = vec(
            'autoexecProg', 
            gen = bits, 
            n = self.p.nProgramBufferWords, 
            init = 0)
        for i in range(self.p.nAbstractDataWords):
            autoexecData[i] /= (
                dmiAbstractDataAccessVec[i * 4] & ABSTRACTAUTOReg.autoexecdata[i])

        for i in range(self.p.nProgramBufferWords):
            autoexecProg[i] /= (
                dmiProgramBufferAccessVec[i * 4] & ABSTRACTAUTOReg.autoexecprogbuf[i])

        autoexec = reduce(
            lambda a,b: a|b, autoexecData) | reduce(lambda a,b: a|b, autoexecProg)

        ##---- COMMAND

        COMMANDReset = COMMANDFields('COMMANDReset', init = 0)
        COMMANDReg = COMMANDFields('COMMANDReg').as_reg()

        COMMANDWrDataVal    = bits('COMMANDWrDataVal', w = 32, init = 0)
        COMMANDWrData       = COMMANDFields('COMMANDWrData', init = COMMANDWrDataVal)
        COMMANDWrEnMaybe    = bits('COMMANDWrEnMaybe', init = 0)
        COMMANDWrEnLegal    = bits('COMMANDWrEnLegal', init = 0)
        COMMANDRdEn  = bits('COMMANDRdEn', init = 0)

        COMMANDWrEn = COMMANDWrEnMaybe & COMMANDWrEnLegal
        COMMANDRdData = COMMANDReg

        with when (~dmactive_sync):
          COMMANDReg /= COMMANDReset
        with other():
          with when (COMMANDWrEn):
            COMMANDReg /= COMMANDWrData

        ## --- Abstract Data

        ## These are byte addressible, s.t. the Processor can use
        ## byte-addressible instructions to store to them.
        abstractDataMem = vec(
            'abstractDataMem', 
            gen = reg, 
            n = self.p.nAbstractDataWords*4, 
            w = 8)
        abstractDataNxt = vec(
            'abstractDataNxt', 
            gen = bits, 
            n = self.p.nAbstractDataWords*4,
            w = 8)
        abstractDataNxt /= abstractDataMem

        ## --- Program Buffer
        programBufferMem = vec(
            'programBufferMem', 
            gen = reg, 
            n = self.p.nProgramBufferWords*4,
            w = 8)
        programBufferNxt = vec(
            'programBufferNxt',
            gen = bits,
            n = self.p.nProgramBufferWords*4,
            w = 8)
        programBufferNxt /= programBufferMem

        ##--------------------------------------------------------------
        ## These bits are implementation-specific bits set
        ## by harts executing code.
        ##--------------------------------------------------------------

        for component in range(self.p.nComponents):
          with when (~dmactive_sync):
            haltedBitRegs[component] /= 0
            resumeReqRegs[component] /= 0
          with other():
            ## Hart Halt Notification Logic
            with when (hartHaltedWrEn):
              with when (self.p.hartIdToHartSel(hartHaltedId) == component):
                haltedBitRegs[component] /= 1
            with elsewhen (hartResumingWrEn):
              with when (self.p.hartIdToHartSel(hartResumingId) == component):
                haltedBitRegs[component] /= 0

            ## Hart Resume Req Logic
            ## If you request a hart to resume at the same moment
            ## it actually does resume, then the request wins.
            ## So don't try to write resumereq more than once
            with when (hartResumingWrEn):
              with when (self.p.hartIdToHartSel(hartResumingId) == component):
                resumeReqRegs[component] /= 0
            with when(resumereq):
              resumeReqRegs.idx_write(self.io.dmcontrol.bits.hartsel, 1)

        #tmp if (self.p.hasBusMaster):
        #tmp     assert(0)
        #tmp else:
        #tmp     (sbcsFields, sbAddrFields, sbDataFields) = (None, None, None)

        ####
        #dmi's csr
        #{{{
        def func_reg_write(
            reg_ptr, 
            fire, 
            address, 
            size, 
            wdata,
            mask_bit,
            wr_valid = None, 
            wr_data = None):
            if (wr_valid is not None):
                with when(fire):
                    wr_valid /= 1
                wr_data /= wdata
            else:
                with when(fire):
                    wr_data /= wdata
            return (1, 1)
        def func_reg_read(
            reg_ptr, 
            fire, 
            address, 
            size, 
            mask_bit,
            rd_valid = None,
            rd_data = None):
            if (rd_valid is not None):
                with when(fire):
                    rd_valid /= 1
            return (1, 1, rd_data.pack())
        def wr_process_gen(wr_valid, wr_data):
            return lambda a0, a1, a2, a3, a4, a5: func_reg_write(
                a0, a1, a2, a3, a4, a5, wr_valid, wr_data)
        def rd_process_gen(rd_valid, rd_data):
            return lambda a0, a1, a2, a3, a4: func_reg_read(
                a0, a1, a2, a3, a4, rd_valid, rd_data)
        self.cfg_reg(csr_reg_group(
            'dmi_dmstatus', 
            offset = DMI_RegAddrs.DMI_DMSTATUS << 2, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = DMSTATUSRdData.pack(), access = 'VOL')]))
        self.cfg_reg(csr_reg_group(
            'dmi_hartinfo', 
            offset = DMI_RegAddrs.DMI_HARTINFO << 2,
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = HARTINFORdData.pack(), access = 'VOL')]))
        self.cfg_reg(csr_reg_group(
            'dmi_haltsum0', 
            offset = DMI_RegAddrs.DMI_HALTSUM0 << 2, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = HALTSUM0RdData.pack(), access = 'VOL')]))
        self.cfg_reg(csr_reg_group(
            'dmi_haltsum1', 
            offset = DMI_RegAddrs.DMI_HALTSUM1 << 2, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = HALTSUM1RdData.pack(), access = 'VOL')]))
        self.cfg_reg(csr_reg_group(
            'dmi_abstractcs',
            offset = DMI_RegAddrs.DMI_ABSTRACTCS << 2, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0, access = 'VOL',
                    read = rd_process_gen(ABSTRACTCSRdEn,  ABSTRACTCSRdData.pack()),
                    write = wr_process_gen(ABSTRACTCSWrEnMaybe, ABSTRACTCSWrDataVal))]))
        self.cfg_reg(csr_reg_group(
            'dmi_abstractauto', 
            offset = DMI_RegAddrs.DMI_ABSTRACTAUTO << 2,
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0, access = 'VOL',
                    read = rd_process_gen(ABSTRACTAUTORdEn,  ABSTRACTAUTORdData.pack()),
                    write = wr_process_gen(ABSTRACTAUTOWrEnMaybe, ABSTRACTAUTOWrDataVal))]))
        self.cfg_reg(csr_reg_group(
            'dmi_command',
            offset = DMI_RegAddrs.DMI_COMMAND << 2, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0, access = 'VOL',
                    read = rd_process_gen(COMMANDRdEn, COMMANDRdData.pack()),
                    write = wr_process_gen(COMMANDWrEnMaybe, COMMANDWrDataVal))]))
        for i in range(self.p.nAbstractDataWords):
            self.cfg_reg(csr_reg_group(
                'dmi_data_'+str(i),
                offset = (DMI_RegAddrs.DMI_DATA0 + i) << 2,
                size = 4, 
                fields_desc = list(reversed(list(map(
                    lambda _: csr_reg_field_desc('value_'+str(_), width = 8, access = 'VOL',
                        read = rd_process_gen(dmiAbstractDataRdEn[i*4 + _], abstractDataMem[i*4 + _].pack()),
                        write = wr_process_gen(dmiAbstractDataWrEnMaybe[i*4 + _], abstractDataNxt[i*4 + _]),
                        ), range(4)))))))
        for i in range(self.p.nProgramBufferWords):
            self.cfg_reg(csr_reg_group(
                'dmi_progbuf_'+str(i), 
                offset = (DMI_RegAddrs.DMI_PROGBUF0 + i) << 2, 
                size = 4, 
                fields_desc = list(reversed(list(map(
                    lambda _: csr_reg_field_desc('value_'+str(_), width = 8, access = 'VOL',
                        read = rd_process_gen(dmiProgramBufferRdEn[i*4 + _],programBufferMem[i*4 + _].pack()),
                        write = wr_process_gen(dmiProgramBufferWrEnMaybe[i*4 + _], programBufferNxt[i*4 + _]),
                            ), range(4)))))))
        if (self.p.hasBusMaster):
            self.cfg_reg(csr_reg_group(
                'dmi_sbcs', 
                offset = DMI_RegAddrs.DMI_SBCS << 2, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('sbversion', width = 3, reset = 1, access = 'VOL'),
                    csr_reg_field_desc('reserved0', width = 6, access = 'VOL'),
                    csr_reg_field_desc('sbbusyerror', width = 1, reset = 0, wr_action = 'ONE_TO_CLEAR'),
                    csr_reg_field_desc('sbbusy', width = 1, reset = 0, access = 'RO'),
                    csr_reg_field_desc('sbreadonaddr', width = 1, reset = 0),
                    csr_reg_field_desc('sbaccess', width = 3, reset = 0),
                    csr_reg_field_desc('sbautoincrement', width = 1, reset = 0),
                    csr_reg_field_desc('sbreadondata', width = 1, reset = 0),
                    csr_reg_field_desc('sberror', width = 3, reset = 0, wr_action = 'ONE_TO_CLEAR'),
                    csr_reg_field_desc('sbasize', width = 7, reset = 32, access = 'VOL'),
                    csr_reg_field_desc('sbaccess128', width = 1, reset = self.p.maxSupportedSBAccess >= 128, access = 'VOL'),
                    csr_reg_field_desc('sbaccess64', width = 1, reset = self.p.maxSupportedSBAccess >= 64, access = 'VOL'),
                    csr_reg_field_desc('sbaccess32', width = 1, reset = self.p.maxSupportedSBAccess >= 32, access = 'VOL'),
                    csr_reg_field_desc('sbaccess16', width = 1, reset = self.p.maxSupportedSBAccess >= 16, access = 'VOL'),
                    csr_reg_field_desc('sbaccess8', width = 1, reset = self.p.maxSupportedSBAccess >= 8, access = 'VOL')]))

            dmi_sbdata0_rd = bits('dmi_sbdata0_rd', init = 0)
            dmi_sbdata1_rd = bits('dmi_sbdata1_rd', init = 0)
            dmi_sbdata2_rd = bits('dmi_sbdata2_rd', init = 0)
            dmi_sbdata3_rd = bits('dmi_sbdata3_rd', init = 0)
            dmi_sbdata0_rd_data = bits('dmi_sbdata0_rd_data', w = 32, init = 0)
            dmi_sbdata1_rd_data = bits('dmi_sbdata1_rd_data', w = 32, init = 0)
            dmi_sbdata2_rd_data = bits('dmi_sbdata2_rd_data', w = 32, init = 0)
            dmi_sbdata3_rd_data = bits('dmi_sbdata3_rd_data', w = 32, init = 0)
            dmi_sbdata0_wr = bits('dmi_sbdata0_wr', init = 0)
            dmi_sbdata1_wr = bits('dmi_sbdata1_wr', init = 0)
            dmi_sbdata2_wr = bits('dmi_sbdata2_wr', init = 0)
            dmi_sbdata3_wr = bits('dmi_sbdata3_wr', init = 0)
            dmi_sbdata0_wr_data = bits('dmi_sbdata0_wr_data', w = 32, init = 0)
            dmi_sbdata1_wr_data = bits('dmi_sbdata1_wr_data', w = 32, init = 0)
            dmi_sbdata2_wr_data = bits('dmi_sbdata2_wr_data', w = 32, init = 0)
            dmi_sbdata3_wr_data = bits('dmi_sbdata3_wr_data', w = 32, init = 0)
            self.cfg_reg(csr_reg_group(
                'dmi_sbdata0', 
                offset = DMI_RegAddrs.DMI_SBDATA0 << 2,
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('data', width = 32, access = 'VOL',
                        read = rd_process_gen(dmi_sbdata0_rd, dmi_sbdata0_rd_data),
                        write = wr_process_gen(dmi_sbdata0_wr, dmi_sbdata0_wr_data))]))
            self.cfg_reg(csr_reg_group(
                'dmi_sbdata1', 
                offset = DMI_RegAddrs.DMI_SBDATA1 << 2,
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('data', width = 32, access = 'VOL',
                        read = rd_process_gen(dmi_sbdata1_rd, dmi_sbdata1_rd_data),
                        write = wr_process_gen(dmi_sbdata1_wr, dmi_sbdata1_wr_data))]))
            self.cfg_reg(csr_reg_group(
                'dmi_sbdata2', 
                offset = DMI_RegAddrs.DMI_SBDATA2 << 2, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('data', width = 32, access = 'VOL',
                        read = rd_process_gen(dmi_sbdata2_rd, dmi_sbdata2_rd_data),
                        write = wr_process_gen(dmi_sbdata2_wr, dmi_sbdata2_wr_data))]))
            self.cfg_reg(csr_reg_group(
                'dmi_sbdata3', 
                offset = DMI_RegAddrs.DMI_SBDATA3 << 2,
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('data', width = 32, access = 'VOL',
                        read = rd_process_gen(dmi_sbdata3_rd, dmi_sbdata3_rd_data),
                        write = wr_process_gen(dmi_sbdata3_wr, dmi_sbdata3_wr_data))]))

            dmi_sbaddress0_wr = bits('dmi_sbaddress0_wr', init = 0)
            dmi_sbaddress1_wr = bits('dmi_sbaddress1_wr', init = 0)
            dmi_sbaddress2_wr = bits('dmi_sbaddress2_wr', init = 0)
            dmi_sbaddress3_wr = bits('dmi_sbaddress3_wr', init = 0)
            dmi_sbaddress0_wr_data = bits('dmi_sbaddress0_wr_data', w = 32, init = 0)
            dmi_sbaddress1_wr_data = bits('dmi_sbaddress1_wr_data', w = 32, init = 0)
            dmi_sbaddress2_wr_data = bits('dmi_sbaddress2_wr_data', w = 32, init = 0)
            dmi_sbaddress3_wr_data = bits('dmi_sbaddress3_wr_data', w = 32, init = 0)
            self.cfg_reg(csr_reg_group(
                'dmi_sbaddress0', 
                offset = DMI_RegAddrs.DMI_SBADDRESS0 << 2, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('address', width = 32, access = 'VOL',
                        write = wr_process_gen(dmi_sbaddress0_wr, dmi_sbaddress0_wr_data))]))
            self.cfg_reg(csr_reg_group(
                'dmi_sbaddress1',
                offset = DMI_RegAddrs.DMI_SBADDRESS1 << 2,
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('address', width = 32, reset = 0, access = 'VOL',
                        write = wr_process_gen(dmi_sbaddress1_wr, dmi_sbaddress1_wr_data))]))
            self.cfg_reg(csr_reg_group(
                'dmi_sbaddress2',
                offset = DMI_RegAddrs.DMI_SBADDRESS2 << 2,
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('address', width = 32, reset = 0, access = 'VOL',
                        write = wr_process_gen(dmi_sbaddress2_wr, dmi_sbaddress2_wr_data))]))
            self.cfg_reg(csr_reg_group(
                'dmi_sbaddress3', 
                offset = DMI_RegAddrs.DMI_SBADDRESS3 << 2,
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('address', width = 32, reset = 0, access = 'VOL',
                        write = wr_process_gen(dmi_sbaddress3_wr, dmi_sbaddress3_wr_data))]))
        #}}}


        for i in range(len(abstractDataMem)):
            with when (dmiAbstractDataWrEnMaybe[i] & dmiAbstractDataAccessLegal):
                abstractDataMem[i] /= abstractDataNxt[i]
        
        for i in range(len(programBufferMem)):
            with when (dmiProgramBufferWrEnMaybe[i] & dmiProgramBufferAccessLegal):
                programBufferMem[i] /= programBufferNxt[i]


        ##--------------------------------------------------------------
        ## "Variable" ROM Generation
        ##--------------------------------------------------------------

        goReg        = reg('goReg')
        goAbstract   = bits('goAbstract', init = 0)
        jalAbstract  = GeneratedUJ('jalAbstract', init = I_CONSTS.JAL().value)
        jalAbstract.setImm(DsbRegAddrs.ABSTRACT(self.p) - DsbRegAddrs.WHERETO)

        with when (~dmactive_sync):
          goReg /= 0
        with other():
          with when (goAbstract):
            goReg /= 1
          with elsewhen (hartGoingWrEn):
            vassert(hartGoingId == 0, "Unexpected 'GOING' hart.")##Chisel3 #540 %x, expected %x", hartGoingId, 0.U)
            goReg /= 0

        class flagBundle(bundle):
            def set_var(self):
                super(flagBundle, self)
                self.var(bits('reserved', w = 6))
                self.var(bits('resume'))
                self.var(bits('go'))

        flags = vec('flags', gen = flagBundle, n = self.p.max_harts, init = 0)
        vassert ((self.p.hartSelToHartId(selectedHartReg) < self.p.max_harts), "HartSel to HartId Mapping is illegal for this Debug Implementation, because HartID must be < 1024 for it to work.")
        for i in range(len(flags)):
            with when(self.p.hartSelToHartId(selectedHartReg) == i):
                flags[i].go /= goReg
        for component in range(self.p.nComponents):
            for i in range(len(flags)):
                with when(self.p.hartSelToHartId(component) == i):
                  flags[i].resume /= resumeReqRegs[component]



        ##----------------------------
        ## Abstract Command Decoding & Generation
        ##----------------------------

        accessRegisterCommandWr  = ACCESS_REGISTERFields(
            'accessRegisterCommandWr', init = COMMANDWrData.pack())
        accessRegisterCommandReg = ACCESS_REGISTERFields(
            'accessRegisterCommandReg', init = COMMANDReg.pack())

        ## TODO: Quick Access

        abstractGeneratedMem = vec('abstractGeneratedMem', gen = reg, n = 2, w = 32)
        abstractGeneratedI = GeneratedI('abstractGeneratedI')
        abstractGeneratedS = GeneratedS('abstractGeneratedS')
        nop = GeneratedI('nop')

        #LD/SD's opcode are same as LW/SW
        abstractGeneratedI.opcode /= GeneratedI(init = I_CONSTS.LW().value).opcode
        abstractGeneratedI.rd     /= (accessRegisterCommandReg.regno & 0x1F)
        abstractGeneratedI.funct3 /= accessRegisterCommandReg.size
        abstractGeneratedI.rs1    /= 0
        abstractGeneratedI.imm    /= DsbRegAddrs.DATA

        abstractGeneratedS.opcode /= GeneratedS(init = I_CONSTS.SW().value).opcode
        abstractGeneratedS.immlo  /= DsbRegAddrs.DATA & 0x1F
        abstractGeneratedS.funct3 /= accessRegisterCommandReg.size
        abstractGeneratedS.rs1    /= 0
        abstractGeneratedS.rs2    /= accessRegisterCommandReg.regno & 0x1F
        abstractGeneratedS.immhi  /= DsbRegAddrs.DATA >> 5

        nop /= GeneratedI(init = I_CONSTS.ADDI().value)
        nop.rd   /= 0
        nop.rs1  /= 0
        nop.imm  /= 0

        with when (goAbstract):
          abstractGeneratedMem[0] /= mux(
              accessRegisterCommandReg.transfer,
              mux(accessRegisterCommandReg.write,
                ## To write a register, we need to do LW.
                abstractGeneratedI.pack(),
                ## To read a register, we need to do SW.
                abstractGeneratedS.pack()),
              nop.pack())
          abstractGeneratedMem[1] /= mux(
              accessRegisterCommandReg.postexec,
              nop.pack(),
              I_CONSTS.EBREAK().value)

        ##--------------------------------------------------------------
        ## Hart Bus Access
        ##--------------------------------------------------------------

        #// This memory is writable.
        self.cfg_reg(csr_reg_group(
            'debug_hart_halted', 
            offset = DsbRegAddrs.HALTED + DsbRegAddrs.ADDR_OFFSET,
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0, access = 'VOL',
                    write = wr_process_gen(hartHaltedWrEn, hartHaltedId))]))
        self.cfg_reg(csr_reg_group(
            'debug_hart_going',
            offset = DsbRegAddrs.GOING + DsbRegAddrs.ADDR_OFFSET,
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0, access = 'VOL',
                    write = wr_process_gen(hartGoingWrEn, hartGoingId))]))
        self.cfg_reg(csr_reg_group(
            'debug_hart_resuming',
            offset = DsbRegAddrs.RESUMING + DsbRegAddrs.ADDR_OFFSET, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0, access = 'VOL',
                    write = wr_process_gen(hartResumingWrEn, hartResumingId))]))
        self.cfg_reg(csr_reg_group(
            'debug_hart_exception', 
            offset = DsbRegAddrs.EXCEPTION + DsbRegAddrs.ADDR_OFFSET, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = 0, access = 'VOL',
                    write = wr_process_gen(hartExceptionWrEn, hartExceptionId))]))
        for i in range(self.p.nAbstractDataWords):
            self.cfg_reg(csr_reg_group(
                'debug_data_'+str(i),
                offset = (DsbRegAddrs.DATA + i*4) + DsbRegAddrs.ADDR_OFFSET,
                size = 4, 
                fields_desc = list(reversed(list(map(lambda _: csr_reg_field_desc('value_'+str(_), width = 8, access = 'VOL',
                        read = rd_process_gen(None, abstractDataMem[i*4 + _].pack()),
                        write = wr_process_gen(None, abstractDataMem[i*4 + _]),
                        ), range(4)))))))
        for i in range(self.p.nProgramBufferWords):
            self.cfg_reg(csr_reg_group(
                'debug_progbuf_'+str(i),
                offset = (DsbRegAddrs.PROGBUF(self.p) + i*4) + DsbRegAddrs.ADDR_OFFSET,
                size = 4,
                fields_desc = list(reversed(list(map(lambda _: csr_reg_field_desc('value_'+str(_), width = 8, access = 'VOL',
                        read = rd_process_gen(None ,programBufferMem[i*4 + _].pack()),
                        write = wr_process_gen(None, programBufferMem[i*4 + _]),
                        ), range(4)))))))

        #// These sections are read-only.
        if (self.p.hasImplicitEbreak):
            self.cfg_reg(csr_reg_group(
                'debug_impebreak', 
                offset = DsbRegAddrs.IMPEBREAK(self.p) + DsbRegAddrs.ADDR_OFFSET,
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('value', width = 32, reset = I_CONSTS.EBREAK().value, access = 'VOL')]))
        #tmp for i in range(14):
        #tmp     self.cfg_reg(csr_reg_group(
        #tmp         'debug_whereto_'+str(i),
        #tmp         offset = (DsbRegAddrs.WHERETO + i*4) + DsbRegAddrs.ADDR_OFFSET, 
        #tmp         size = 4,
        #tmp         fields_desc = [
        #tmp             csr_reg_field_desc('value', width = 32, reset = jalAbstract.pack() if (i == 0) else 0, access = 'VOL')]))
        self.cfg_reg(csr_reg_group(
            'debug_whereto',
            offset = DsbRegAddrs.WHERETO + DsbRegAddrs.ADDR_OFFSET, 
            size = 4,
            fields_desc = [
                csr_reg_field_desc('value', width = 32, reset = jalAbstract.pack(), access = 'VOL')]))
        for i in range(len(abstractGeneratedMem)):
            self.cfg_reg(csr_reg_group(
                'debug_abstract_'+str(i), 
                offset = (DsbRegAddrs.ABSTRACT(self.p) + i*4) + DsbRegAddrs.ADDR_OFFSET, 
                size = 4,
                fields_desc = [
                    csr_reg_field_desc('value', width = 32, reset = abstractGeneratedMem[i].pack(), access = 'VOL')]))
        #one hart one byte
        for i in range(len(flags)//4):
            self.cfg_reg(csr_reg_group(
                'debug_flags_'+str(i), 
                offset = (DsbRegAddrs.FLAGS + i*4) + DsbRegAddrs.ADDR_OFFSET,
                size = 4,
                fields_desc = list(reversed(list(map(lambda _: csr_reg_field_desc('value_'+str(_), width = 8, reset = flags[i*4 + _].pack(), access = 'VOL'), range(4)))))))
        rom_size = len(DebugRomContents.debug_rom_raw)
        rom_size_64B = (rom_size//64 + (1 if (rom_size%64 != 0) else 0)) * 64
        for i in range(rom_size_64B//4):
            self.cfg_reg(csr_reg_group(
                'debug_rom_'+str(i), 
                offset = (DsbRegAddrs.ROMBASE + i*4) + DsbRegAddrs.ADDR_OFFSET, 
                size = 4,
                fields_desc = list(reversed(list(map(lambda _: csr_reg_field_desc('value_'+str(_), width = 8, reset = DebugRomContents.debug_rom_raw[i*4 + _] if ((i*4+_) < rom_size) else 0, access = 'VOL'), range(4)))))))


        ## Override System Bus accesses with dmactive reset.
        with when (~dmactive_sync):
          for x in abstractDataMem:
              x /= 0
          for x in programBufferMem:
              x /= 0

        ##--------------------------------------------------------------
        ## Abstract Command State Machine
        ##--------------------------------------------------------------
        (Waiting, CheckGenerate, Exec) = range(3)

        ## This is not an initialization!
        ctrlStateReg = reg_rs('ctrlStateReg', w = 2, rs = Waiting)

        hartHalted   = haltedBitRegs[selectedHartReg]
        ctrlStateNxt = bits('ctrlStateNxt', w = ctrlStateReg.get_w(), init = ctrlStateReg)

        ##------------------------
        ## DMI Register Control and Status

        abstractCommandBusy /= (ctrlStateReg != Waiting)

        ABSTRACTCSWrEnLegal   /= (ctrlStateReg == Waiting)
        COMMANDWrEnLegal      /= (ctrlStateReg == Waiting)
        ABSTRACTAUTOWrEnLegal /= (ctrlStateReg == Waiting)
        dmiAbstractDataAccessLegal  /= (ctrlStateReg == Waiting)
        dmiProgramBufferAccessLegal /= (ctrlStateReg == Waiting)

        errorBusy /= (ABSTRACTCSWrEnMaybe    & ~ABSTRACTCSWrEnLegal)        | \
                     (ABSTRACTAUTOWrEnMaybe  & ~ABSTRACTAUTOWrEnLegal)      | \
                     (COMMANDWrEnMaybe       & ~COMMANDWrEnLegal)           | \
                     (dmiAbstractDataAccess  & ~dmiAbstractDataAccessLegal) | \
                     (dmiProgramBufferAccess & ~dmiProgramBufferAccessLegal)

        ## TODO: Maybe Quick Access
        commandWrIsAccessRegister = (
            COMMANDWrData.cmdtype == DebugAbstractCommandType.AccessRegister)
        commandRegIsAccessRegister = (
            COMMANDReg.cmdtype == DebugAbstractCommandType.AccessRegister)

        commandWrIsUnsupported = COMMANDWrEn & ~commandWrIsAccessRegister;

        commandRegIsUnsupported = bits('commandRegIsUnsupported', init = 1)
        commandRegBadHaltResume = bits('commandRegBadHaltResume', init = 0)
        with when (commandRegIsAccessRegister):
          with when (
                ~accessRegisterCommandReg.transfer | 
                (
                    (accessRegisterCommandReg.regno >= 0x1000) & 
                    (accessRegisterCommandReg.regno <= 0x101F))):
            commandRegIsUnsupported /= 0
            commandRegBadHaltResume /= ~hartHalted

        wrAccessRegisterCommand  = (
            COMMANDWrEn & commandWrIsAccessRegister  & (ABSTRACTCSReg.cmderr == 0))
        regAccessRegisterCommand = (
            autoexec & commandRegIsAccessRegister & (ABSTRACTCSReg.cmderr == 0))



        ##------------------------
        ## Variable ROM STATE MACHINE
        ## -----------------------

        with when (ctrlStateReg == Waiting):
          with when (wrAccessRegisterCommand | regAccessRegisterCommand):
            ctrlStateNxt /= CheckGenerate
          with elsewhen (commandWrIsUnsupported): ## These checks are really on the command type.
            errorUnsupported /= 1
          with elsewhen (autoexec & commandRegIsUnsupported):
            errorUnsupported /= 1
        with elsewhen (ctrlStateReg == CheckGenerate):

          ## We use this state to ensure that the COMMAND has been
          ## registered by the time that we need to use it, to avoid
          ## generating it directly from the COMMANDWrData.
          ## This 'commandRegIsUnsupported' is really just checking the
          ## AccessRegisterCommand parameters (regno)
          with when (commandRegIsUnsupported):
            errorUnsupported /= 1
            ctrlStateNxt /= Waiting
          with elsewhen (commandRegBadHaltResume):
            errorHaltResume /= 1
            ctrlStateNxt /= Waiting
          with other():
            ctrlStateNxt /= Exec
            goAbstract /= 1
        
        with elsewhen (ctrlStateReg == Exec):

          ## We can't just look at 'hartHalted' here, because
          ## hartHaltedWrEn is overloaded to mean 'got an ebreak'
          ## which may have happened when we were already halted.
          with when(
              (goReg == 0) & 
              hartHaltedWrEn & 
              (self.p.hartIdToHartSel(hartHaltedId) == selectedHartReg)):
            ctrlStateNxt /= Waiting
          with when(hartExceptionWrEn):
            vassert(hartExceptionId == 0, "Unexpected 'EXCEPTION' hart")##Chisel3 #540, %x, expected %x", hartExceptionId, 0.U)
            ctrlStateNxt /= Waiting
            errorException /= 1

        with when (~dmactive_sync):
          ctrlStateReg /= Waiting
        with other():
          ctrlStateReg /= ctrlStateNxt
        vassert ((~hartExceptionWrEn | (ctrlStateReg == Exec)), "Unexpected EXCEPTION write: should only get it in Debug Module EXEC state")


        #system bus access
        if (self.p.hasBusMaster):
            dmi_sbaddress0_reg = reg('dmi_sbaddress0_reg', w = self.regs['dmi_sbaddress0'].address.get_w())
            with when(dmi_sbaddress0_wr):
                dmi_sbaddress0_reg /= dmi_sbaddress0_wr_data
            dmi_sbdata0_reg = reg('dmi_sbdata0_reg', w = self.regs['dmi_sbdata0'].data.get_w())
            with when(dmi_sbdata0_wr):
                dmi_sbdata0_reg /= dmi_sbdata0_wr_data
            dmi_sbdata0_rd_data /= dmi_sbdata0_reg
            if (self.p.maxSupportedSBAccess >= 64):
                dmi_sbdata1_reg = reg('dmi_sbdata1_reg', w = self.regs['dmi_sbdata1'].data.get_w())
                with when(dmi_sbdata1_wr):
                    dmi_sbdata1_reg /= dmi_sbdata1_wr_data
                dmi_sbdata1_rd_data /= dmi_sbdata1_reg

            SB_NO_ERROR    = 0
            SB_TIMEOUT     = 1
            SB_BAD_ADDR    = 2
            SB_ALGN_ERROR  = 3
            SB_BAD_ACCESS  = 4
            SB_OTHER_ERROR = 7

            sb_curr_addr = mux(dmi_sbaddress0_wr, dmi_sbaddress0_wr_data, dmi_sbaddress0_reg)
            sb_algn_error  = (
                ((self.regs['dmi_sbcs'].sbaccess == 1) & (sb_curr_addr[0] != 0)) |
                ((self.regs['dmi_sbcs'].sbaccess == 2) & (sb_curr_addr[1:0] != 0)) |
                ((self.regs['dmi_sbcs'].sbaccess == 3) & (sb_curr_addr[2:0] != 0)) |
                ((self.regs['dmi_sbcs'].sbaccess == 4) & (sb_curr_addr[3:0] != 0)))
            sb_bad_access = (
                ((self.regs['dmi_sbcs'].sbaccess == 0) & ~self.regs['dmi_sbcs'].sbaccess8) |
                ((self.regs['dmi_sbcs'].sbaccess == 1) & ~self.regs['dmi_sbcs'].sbaccess16) |
                ((self.regs['dmi_sbcs'].sbaccess == 2) & ~self.regs['dmi_sbcs'].sbaccess32) |
                ((self.regs['dmi_sbcs'].sbaccess == 3) & ~self.regs['dmi_sbcs'].sbaccess64) |
                ((self.regs['dmi_sbcs'].sbaccess == 4) & ~self.regs['dmi_sbcs'].sbaccess128))
            sb_error = mux(sb_algn_error, SB_ALGN_ERROR, mux(sb_bad_access, SB_BAD_ACCESS, SB_NO_ERROR))

            (SB_IDLE, SB_REQ, SB_RESP, SB_ERR) = range(4)
            sb_state = reg_rs('sb_state', w = 3, rs = SB_IDLE)
            sb_access_is_wr = reg_r('sb_access_is_wr')
            sb_error_reg = reg_r('sb_error_reg', w = 3)

            sb_req_done = bits('sb_req_done', init = self.tl_out.a.fire())
            sb_resp_done = bits('sb_resp_done', init = self.tl_out.d.fire())
            with when(sb_state == SB_IDLE):
                sb_state /= SB_IDLE
                sb_access_is_wr /= 0
                sb_error_reg /= sb_error
                with when(~self.regs['dmi_sbcs'].sbbusy & ~self.regs['dmi_sbcs'].sbbusyerror):
                    with when(
                        (self.regs['dmi_sbcs'].sbreadonaddr & dmi_sbaddress0_wr) |
                        (self.regs['dmi_sbcs'].sbreadondata & dmi_sbdata0_rd)):
                        sb_access_is_wr /= 0
                        with when(sb_error != SB_NO_ERROR):
                            sb_state /= SB_ERR
                        with other():
                            sb_state /= SB_REQ
                    with elsewhen(dmi_sbdata0_wr):
                        sb_access_is_wr /= 1
                        with when(sb_error != SB_NO_ERROR):
                            sb_state /= SB_ERR
                        with other():
                            sb_state /= SB_REQ
            with when(sb_state == SB_REQ):
                with when(sb_req_done):
                    sb_state /= SB_RESP
            with when(sb_state == SB_RESP):
                with when(sb_resp_done):
                    sb_state /= SB_IDLE
            with when(sb_state == SB_ERR):
                sb_state /= SB_IDLE

            dmi_sbdata_all = dmi_sbdata0_reg
            if (self.p.maxSupportedSBAccess >= 64):
                dmi_sbdata_all = cat([dmi_sbdata1_reg, dmi_sbdata0_reg])
            get_req_bits = self.interface_out.get(
                0,
                dmi_sbaddress0_reg,
                self.regs['dmi_sbcs'].sbaccess)[1]
            put_req_bits = self.interface_out.put( 
                0,
                dmi_sbaddress0_reg,
                self.regs['dmi_sbcs'].sbaccess, M_CONSTS.store_data_gen(
                    self.regs['dmi_sbcs'].sbaccess,
                    dmi_sbdata_all.u_ext(self.tl_out.a.bits.data.get_w()),
                    self.tl_out.a.bits.data.get_w()//8))[1]
            self.tl_out.a.bits /= mux(sb_access_is_wr, put_req_bits, get_req_bits)

            self.tl_out.a.valid /= 0
            with when(sb_state == SB_REQ):
                self.tl_out.a.valid /= 1

            self.tl_out.d.ready /= 1
            rd_data_shift = M_CONSTS.load_data_gen(
                            cat([1, self.regs['dmi_sbcs'].sbaccess]),
                            dmi_sbaddress0_reg,
                            self.tl_out.d.bits.data,
                            self.tl_out.d.bits.data.get_w()//8,
                            1)
            with when(sb_state == SB_RESP):
                with when(sb_resp_done):
                    with when(~sb_access_is_wr):
                        dmi_sbdata0_reg /= rd_data_shift[31:0]
                        if (self.p.maxSupportedSBAccess >= 64):
                            dmi_sbdata1_reg /= rd_data_shift[63:32]

                    with when(self.regs['dmi_sbcs'].sbautoincrement):
                            dmi_sbaddress0_reg /= dmi_sbaddress0_reg + (1 << self.regs['dmi_sbcs'].sbaccess)

            self.regs['dmi_sbcs'].sbbusy /= sb_state != SB_IDLE
            with when(sb_state == SB_ERR):
                self.regs['dmi_sbcs'].sberror/= sb_error_reg


class zqh_debug_module(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_debug_module, self).set_par()
        self.p = DefaultDebugModuleParams()

    def gen_node_tree(self):
        super(zqh_debug_module, self).gen_node_tree()
        self.gen_node_master('dmi_sb_master', bundle_p = self.p.gen_sb_tl_master_bundle_p())
        self.p.par(
            'in_extern_slave', 
            zqh_tilelink_node_master_io_parameter(
                'in_extern_slave',
                address_mask = 0x0fff, 
                bundle_out = [self.p.gen_tl_bundle_p()]))
        self.p.par(
            'inside_addr_fix', 
            zqh_tilelink_node_master_parameter(
                'inside_addr_fix',
                process = [[zqh_debug_inside_addr_fix, DsbRegAddrs.ADDR_OFFSET]]))
        self.p.par('dmi_tl_master', zqh_tilelink_node_master_parameter('dmi_tl_master'))
        self.p.par('dmi_bus', zqh_tilelink_node_xbar_parameter('dmi_bus',
            do_imp = 1,
            up_bus_data_bits = DMIConsts.dmiDataSize,
            up_bus_address_bits = 16,
            up_bus_size_bits = 2,
            down_bus_data_bits = DMIConsts.dmiDataSize,
            down_bus_address_bits = 16,
            down_bus_size_bits = 2))
        self.p.par('dmi_tl_slave' , zqh_tilelink_node_slave_parameter(
            'dmi_tl_slave', 
            address = [
                zqh_address_space(
                    base = 0x0000, 
                    mask = 0xffff, 
                    attr = zqh_address_attr.MEM_RWAX_UC,
                    order_type = zqh_order_type.SO)],
            transfer_sizes = zqh_transfer_size(min = 0,max = 4)))
        self.p.dmi_bus.push_up(self.p.dmi_tl_master)
        self.p.dmi_bus.push_down(self.p.dmi_tl_slave)

        if (len(self.p.extern_slaves) > 0):
            self.p.in_extern_slave.push_up(self.p.extern_slaves[0])
        self.p.inside_addr_fix.push_up(self.p.in_extern_slave)
        self.p.dmi_bus.push_up(self.p.inside_addr_fix)

        self.p.dmi_tl_slave.print_up()
        self.p.dmi_tl_slave.print_address_space()

    def set_port(self):
        super(zqh_debug_module, self).set_port()
        self.io.var(DebugCtrlBundle('ctrl', nComponents = self.p.nComponents))
        self.io.var(ClockedDMIIO('dmi').flip())

    def main(self):
        super(zqh_debug_module, self).main()
        self.gen_node_interrupt('in_extern_slave')

        if (self.p.dumy):
            self.io.ctrl.ndreset /= 0
            self.io.ctrl.dmactive /= 0
            self.io.dmi.dmi.req.ready /= 0
            self.io.dmi.dmi.resp.valid /= 0
            self.int_out[0] /= 0
            return

        debug_outside = zqh_debug_outside(
            'debug_outside',
            extern_masters = [self.p.dmi_tl_master])
        debug_outside.io.dmi_in /= self.io.dmi
        debug_outside.io.clock /= self.io.dmi.dmiClock #default clock is dmi's
        debug_outside.io.reset /= self.io.dmi.dmiReset
        debug_outside.io.clock_tl /= self.io.clock #tilelink's clock
        debug_outside.io.reset_tl /= self.io.reset

        self.int_out[0] /= debug_outside.io.int_flag.pack()

        self.io.ctrl /= debug_outside.io.ctrl

        debug_inside = zqh_debug_dmi_inside(
            'debug_inside', 
            extern_slaves = [self.p.dmi_tl_slave],
            extern_masters = [self.p.dmi_sb_master])
        debug_inside.io.dmactive /= debug_outside.io.ctrl.dmactive
        debug_inside.io.debugUnavail /= self.io.ctrl.debugUnavail
        debug_inside.io.dmcontrol /= debug_outside.io.dmcontrol
