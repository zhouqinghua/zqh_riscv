####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/devices/debug/dm_registers.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *


class DMI_RegAddrs(object):
  #/* The address of this register will not change in the future, because it
  #      contains \Fversion.  It has changed from version 0.11 of this spec.
  #
  #      This register reports status for the overall debug module
  #      as well as the currently selected harts, as defined in \Fhasel.
  #
  #      Harts are nonexistent if they will never be part of this system, no
  #      matter how long a user waits. Eg. in a simple single-hart system only
  #      one hart exists, and all others are nonexistent. Debuggers may assume
  #      that a system has no harts with indexes higher than the first
  #      nonexistent one.
  #
  #      Harts are unavailable if they might exist/become available at a later
  #      time, or if there are other harts with higher indexes than this one. Eg.
  #      in a multi-hart system some might temporarily be powered down, or a
  #      system might support hot-swapping harts. Systems with very large number
  #      of harts may permanently disable some during manufacturing, leaving
  #      holes in the otherwise continuous hart index space. In order to let the
  #      debugger discover all harts, they must show up as unavailable even if
  #      there is no chance of them ever becoming available.
  #*/
  DMI_DMSTATUS =  0x11

  #/* This register controls the overall debug module
  #      as well as the currently selected harts, as defined in \Fhasel.

#\label{hartsel}
#\index{hartsel}
  #      Throughout this document we refer to \Fhartsel, which is \Fhartselhi
  #      combined with \Fhartsello. While the spec allows for 20 \Fhartsel bits,
  #      an implementation may choose to implement fewer than that. The actual
  #      width of \Fhartsel is called {\tt HARTSELLEN}. It must be at least 0
  #      and at most 20. A debugger should discover {\tt HARTSELLEN} by writing
  #      all ones to \Fhartsel (assuming the maximum size) and reading back the
  #      value to see which bits were actually set.
  #*/
  DMI_DMCONTROL =  0x10

  #/* This register gives information about the hart currently
  #    selected by \Fhartsel.
  #
  #    This register is optional. If it is not present it should
  #    read all-zero.
  #
  #    If this register is included, the debugger can do more with
  #    the Program Buffer by writing programs which
  #    explicitly access the {\tt data} and/or {\tt dscratch}
  #    registers.
  #*/
  DMI_HARTINFO =  0x12

  #/* This register selects which of the 32-bit portion of the hart array mask
  #    register (see Section~\ref{hartarraymask}) is accessible in \Rhawindow.
  #*/
  DMI_HAWINDOWSEL =  0x14

  #/* This register provides R/W access to a 32-bit portion of the
  #    hart array mask register (see Section~\ref{hartarraymask}).
  #    The position of the window is determined by \Rhawindowsel. I.e. bit 0
  #    refers to hart $\Rhawindowsel * 32$, while bit 31 refers to hart
  #    $\Rhawindowsel * 32 + 31$.
  #
  #    Since some bits in the hart array mask register may be constant 0, some
  #    bits in this register may be constant 0, depending on the current value
  #    of \Fhawindowsel.
  #*/
  DMI_HAWINDOW =  0x15

  DMI_ABSTRACTCS =  0x16

  #/* Writes to this register cause the corresponding abstract command to be
  #      executed.
  #
  #      Writing while an abstract command is executing causes \Fcmderr to be set.
  #
  #      If \Fcmderr is non-zero, writes to this register are ignored.
  #
  #      \begin{commentary}
  #          \Fcmderr inhibits starting a new command to accommodate debuggers
  #          that, for performance reasons, send several commands to be executed
  #          in a row without checking \Fcmderr in between. They can safely do
  #          so and check \Fcmderr at the end without worrying that one command
  #          failed but then a later command (which might have depended on the
  #          previous one succeeding) passed.
  #      \end{commentary}
  #*/
  DMI_COMMAND =  0x17

  #/* This register is optional. Including it allows more efficient burst accesses.
  #    Debugger can attempt to set bits and read them back to determine if the functionality is supported.
  #*/
  DMI_ABSTRACTAUTO =  0x18

  #/* When {\tt devtreevalid} is set, reading this register returns bits 31:0
  #    of the Device Tree address. Reading the other {\tt devtreeaddr}
  #    registers returns the upper bits of the address.
  #
  #    When system bus mastering is implemented, this must be an
  #    address that can be used with the System Bus Access module. Otherwise,
  #    this must be an address that can be used to access the
  #    Device Tree from the hart with ID 0.
  #
  #    If {\tt devtreevalid} is 0, then the {\tt devtreeaddr} registers
  #    hold identifier information which is not
  #    further specified in this document.
  #
  #    The Device Tree itself is described in the RISC-V Privileged
  #    Specification.
  #*/
  DMI_DEVTREEADDR0 =  0x19

  DMI_DEVTREEADDR1 =  0x1a

  DMI_DEVTREEADDR2 =  0x1b

  DMI_DEVTREEADDR3 =  0x1c

  #/* If there is more than one DM accessible on this DMI, this register
  #      contains the base address of the next one in the chain, or 0 if this is
  #      the last one in the chain.
  #*/
  DMI_NEXTDM =  0x1d

  #/* \Rdatazero through \Rdataeleven are basic read/write registers that may
  #      be read or changed by abstract commands. \Fdatacount indicates how many
  #      of them are implemented, starting at \Rsbdatazero, counting up.
  #      Table~\ref{tab:datareg} shows how abstract commands use these
  #      registers.
  #
  #      Accessing these registers while an abstract command is executing causes
  #      \Fcmderr to be set.
  #
  #      Attempts to write them while \Fbusy is set does not change their value.
  #
  #      The values in these registers may not be preserved after an abstract
  #      command is executed. The only guarantees on their contents are the ones
  #      offered by the command in question. If the command fails, no
  #      assumptions can be made about the contents of these registers.
  #*/
  DMI_DATA0 =  0x04

  DMI_DATA11 =  0x0f

  #/* \Rprogbufzero through \Rprogbuffifteen provide read/write access to the
  #      optional program buffer. \Fprogbufsize indicates how many of them are
  #      implemented starting at \Rprogbufzero, counting up.
  #
  #      Accessing these registers while an abstract command is executing causes
  #      \Fcmderr to be set.
  #
  #      Attempts to write them while \Fbusy is set does not change their value.
  #*/
  DMI_PROGBUF0 =  0x20

  DMI_PROGBUF15 =  0x2f

  #/* This register serves as a 32-bit serial port to the authentication
  #      module.

  #      When \Fauthbusy is clear, the debugger can communicate with the
  #      authentication module by reading or writing this register. There is no
  #      separate mechanism to signal overflow/underflow.
  #*/
  DMI_AUTHDATA =  0x30

  #/* Each bit in this read-only register indicates whether one specific hart
  #      is halted or not. Unavailable/nonexistent harts are not considered to
  #      be halted.

  #      The LSB reflects the halt status of hart \{hartsel[19:5],5'h0\}, and the
  #      MSB reflects halt status of hart \{hartsel[19:5],5'h1f\}.
  #*/
  DMI_HALTSUM0 =  0x40

  #/* Each bit in this read-only register indicates whether any of a group of
  #      harts is halted or not. Unavailable/nonexistent harts are not considered to
  #      be halted.

  #      This register may not be present in systems with fewer than
  #      33 harts.

  #      The LSB reflects the halt status of harts \{hartsel[19:10],10'h0\}
  #      through \{hartsel[19:10],10'h1f\}.
  #      The MSB reflects the halt status of harts \{hartsel[19:10],10'h3e0\}
  #      through \{hartsel[19:10],10'h3ff\}.
  #*/
  DMI_HALTSUM1 =  0x13

  #/* Each bit in this read-only register indicates whether any of a group of
  #      harts is halted or not. Unavailable/nonexistent harts are not considered to
  #      be halted.

  #      This register may not be present in systems with fewer than
  #      1025 harts.

  #      The LSB reflects the halt status of harts \{hartsel[19:15],15'h0\}
  #      through \{hartsel[19:15],15'h3ff\}.
  #      The MSB reflects the halt status of harts \{hartsel[19:15],15'h7c00\}
  #      through \{hartsel[19:15],15'h7fff\}.
  #*/
  DMI_HALTSUM2 =  0x34

  #/* Each bit in this read-only register indicates whether any of a group of
  #      harts is halted or not. Unavailable/nonexistent harts are not considered to
  #      be halted.

  #      This register may not be present in systems with fewer than
  #      32769 harts.

  #      The LSB reflects the halt status of harts 20'h0 through 20'h7fff.
  #      The MSB reflects the halt status of harts 20'hf8000 through 20'hfffff.
  #*/
  DMI_HALTSUM3 =  0x35

  #/* If \Fsbasize is less than 97, then this register is not present.

  #      When the system bus master is busy, writes to this register will set
  #      \Fsbbusyerror and don't do anything else.
  #*/
  DMI_SBADDRESS3 =  0x37

  DMI_SBCS =  0x38

  #/* If \Fsbasize is 0, then this register is not present.

  #      When the system bus master is busy, writes to this register will set
  #      \Fsbbusyerror and don't do anything else.

  #      \begin{steps}{If \Fsberror is 0, \Fsbbusyerror is 0, and \Fsbreadonaddr
  #      is set then writes to this register start the following:}
  #          \item Set \Fsbbusy.
  #          \item Perform a bus read from the new value of {\tt sbaddress}.
  #          \item If the read succeeded and \Fsbautoincrement is set, increment
  #          {\tt sbaddress}.
  #          \item Clear \Fsbbusy.
  #      \end{steps}
  #*/
  DMI_SBADDRESS0 =  0x39

  #/* If \Fsbasize is less than 33, then this register is not present.

  #      When the system bus master is busy, writes to this register will set
  #      \Fsbbusyerror and don't do anything else.
  #*/
  DMI_SBADDRESS1 =  0x3a

  #/* If \Fsbasize is less than 65, then this register is not present.

  #      When the system bus master is busy, writes to this register will set
  #      \Fsbbusyerror and don't do anything else.
  #*/
  DMI_SBADDRESS2 =  0x3b

  #/* If all of the {\tt sbaccess} bits in \Rsbcs are 0, then this register
  #      is not present.

  #      Any successful system bus read updates {\tt sbdata}. If the width of
  #      the read access is less than the width of {\tt sbdata}, the contents of
  #      the remaining high bits may take on any value.

  #      If \Fsberror or \Fsbbusyerror both aren't 0 then accesses do nothing.

  #      If the bus master is busy then accesses set \Fsbbusyerror, and don't do
  #      anything else.

  #      \begin{steps}{Writes to this register start the following:}
  #          \item Set \Fsbbusy.
  #          \item Perform a bus write of the new value of {\tt sbdata} to {\tt sbaddress}.
  #          \item If the write succeeded and \Fsbautoincrement is set,
  #          increment {\tt sbaddress}.
  #          \item Clear \Fsbbusy.
  #      \end{steps}

  #      \begin{steps}{Reads from this register start the following:}
  #          \item ``Return'' the data.
  #          \item Set \Fsbbusy.
  #          \item If \Fsbautoincrement is set, increment {\tt sbaddress}.
  #          \item If \Fsbreadondata is set, perform another system bus read.
  #          \item Clear \Fsbbusy.
  #      \end{steps}

  #      Only \Rsbdatazero has this behavior. The other {\tt sbdata} registers
  #      have no side effects. On systems that have buses wider than 32 bits, a
  #      debugger should access \Rsbdatazero after accessing the other {\tt
  #      sbdata} registers.
  #*/
  DMI_SBDATA0 =  0x3c

  #/* If \Fsbaccesssixtyfour and \Fsbaccessonetwentyeight are 0, then this
  #      register is not present.

  #      If the bus master is busy then accesses set \Fsbbusyerror, and don't do
  #      anything else.
  #*/
  DMI_SBDATA1 =  0x3d

  #/* This register only exists if \Fsbaccessonetwentyeight is 1.

  #      If the bus master is busy then accesses set \Fsbbusyerror, and don't do
  #      anything else.
  #*/
  DMI_SBDATA2 =  0x3e

  #/* This register only exists if \Fsbaccessonetwentyeight is 1.

  #      If the bus master is busy then accesses set \Fsbbusyerror, and don't do
  #      anything else.
  #*/
  DMI_SBDATA3 =  0x3f


class DMSTATUSFields(bundle):
    def set_var(self):
        super(DMSTATUSFields, self).set_var()

        self.var(bits('reserved0', w = 9))

        #/* If 1, then there is an implicit {\tt ebreak} instruction at the
        #          non-existent word immediately after the Program Buffer. This saves
        #          the debugger from having to write the {\tt ebreak} itself, and
        #          allows the Program Buffer to be one word smaller.

        #          This must be 1 when \Fprogbufsize is 1.
        #*/
        self.var(bits('impebreak'))

        self.var(bits('reserved1', w = 2))

        #/* This field is 1 when all currently selected harts have been reset but the reset has not been acknowledged.
        #*/
        self.var(bits('allhavereset'))

        #/* This field is 1 when any currently selected hart has been reset but the reset has not been acknowledged.
        #*/
        self.var(bits('anyhavereset'))

        #/* This field is 1 when all currently selected harts have acknowledged
        #          the previous resume request.
        #*/
        self.var(bits('allresumeack'))

        #/* This field is 1 when any currently selected hart has acknowledged
        #          the previous resume request.
        #*/
        self.var(bits('anyresumeack'))

        #/* This field is 1 when all currently selected harts do not exist in this system.
        #*/
        self.var(bits('allnonexistent'))

        #/* This field is 1 when any currently selected hart does not exist in this system.
        #*/
        self.var(bits('anynonexistent'))

        #/* This field is 1 when all currently selected harts are unavailable.
        #*/
        self.var(bits('allunavail'))

        #/* This field is 1 when any currently selected hart is unavailable.
        #*/
        self.var(bits('anyunavail'))

        #/* This field is 1 when all currently selected harts are running.
        #*/
        self.var(bits('allrunning'))

        #/* This field is 1 when any currently selected hart is running.
        #*/
        self.var(bits('anyrunning'))

        #/* This field is 1 when all currently selected harts are halted.
        #*/
        self.var(bits('allhalted'))

        #/* This field is 1 when any currently selected hart is halted.
        #*/
        self.var(bits('anyhalted'))

        #/* 0 when authentication is required before using the DM.  1 when the
        #          authentication check has passed. On components that don't implement
        #          authentication, this bit must be preset as 1.
        #*/
        self.var(bits('authenticated'))

        #/* 0: The authentication module is ready to process the next
        #          read/write to \Rauthdata.

        #          1: The authentication module is busy. Accessing \Rauthdata results
        #          in unspecified behavior.

        #          \Fauthbusy only becomes set in immediate response to an access to
        #          \Rauthdata.
        #*/
        self.var(bits('authbusy'))

        self.var(bits('reserved2', w = 1))

        #/* 0: \Rdevtreeaddrzero--\Rdevtreeaddrthree hold information which
        #          is not relevant to the Device Tree.

        #          1: \Rdevtreeaddrzero--\Rdevtreeaddrthree registers hold the address of the
        #          Device Tree.
        #*/
        self.var(bits('devtreevalid'))

        #/* 0: There is no Debug Module present.

        #          1: There is a Debug Module and it conforms to version 0.11 of this
        #          specification.

        #          2: There is a Debug Module and it conforms to version 0.13 of this
        #          specification.

        #          15: There is a Debug Module but it does not conform to any
        #          available version of this spec.
        #*/
        self.var(bits('version', w = 4))


class DMCONTROLFields(bundle):
    def set_var(self):
        super(DMCONTROLFields, self).set_var()

        #/* Writes the halt request bit for all currently selected harts.
        #          When set to 1, each selected hart will halt if it is not currently
        #          halted.

        #          Writing 1 or 0 has no effect on a hart which is already halted, but
        #          the bit must be cleared to 0 before the hart is resumed.

        #          Writes apply to the new value of \Fhartsel and \Fhasel.
        #*/
        self.var(bits('haltreq'))

        #/* Writes the resume request bit for all currently selected harts.
        #          When set to 1, each selected hart will resume if it is currently
        #          halted.

        #          The resume request bit is ignored while the halt request bit is
        #          set.

        #          Writes apply to the new value of \Fhartsel and \Fhasel.
        #*/
        self.var(bits('resumereq'))

        #/* This optional field writes the reset bit for all the currently
        #          selected harts.  To perform a reset the debugger writes 1, and then
        #          writes 0 to deassert the reset signal.

        #          If this feature is not implemented, the bit always stays 0, so
        #          after writing 1 the debugger can read the register back to see if
        #          the feature is supported.

        #          Writes apply to the new value of \Fhartsel and \Fhasel.
        #*/
        self.var(bits('hartreset'))

        #/* Writing 1 to this bit clears the {\tt havereset} bits for
        #          any selected harts.

        #          Writes apply to the new value of \Fhartsel and \Fhasel.
        #*/
        self.var(bits('ackhavereset'))

        self.var(bits('reserved0', w = 1))

        #/* Selects the  definition of currently selected harts.

        #          0: There is a single currently selected hart, that selected by \Fhartsel.

        #          1: There may be multiple currently selected harts -- that selected by \Fhartsel,
        #             plus those selected by the hart array mask register.

        #          An implementation which does not implement the hart array mask register
        #          must tie this field to 0. A debugger which wishes to use the hart array
        #          mask register feature should set this bit and read back to see if the functionality
        #          is supported.
        #*/
        self.var(bits('hasel'))

        #/* The low 10 bits of \Fhartsel: the DM-specific index of the hart to
        #          select. This hart is always part of the currently selected harts.
        #*/
        self.var(bits('hartsello', w = 10))

        #/* The high 10 bits of \Fhartsel: the DM-specific index of the hart to
        #          select. This hart is always part of the currently selected harts.
        #*/
        self.var(bits('hartselhi', w = 10))

        self.var(bits('reserved1', w = 4))

        #/* This bit controls the reset signal from the DM to the rest of the
        #          system. The signal should reset every part of the system, including
        #          every hart, except for the DM and any logic required to access the
        #          DM.
        #          To perform a system reset the debugger writes 1,
        #          and then writes 0
        #          to deassert the reset.
        #*/
        self.var(bits('ndmreset'))

        #/* This bit serves as a reset signal for the Debug Module itself.

        #          0: The module's state, including authentication mechanism,
        #          takes its reset values (the \Fdmactive bit is the only bit which can
        #          be written to something other than its reset value).

        #          1: The module functions normally.

        #          No other mechanism should exist that may result in resetting the
        #          Debug Module after power up, including the platform's system reset
        #          or Debug Transport reset signals.

        #          A debugger may pulse this bit low to get the debug module into a
        #          known state.

        #          Implementations may use this bit to aid debugging, for example by
        #          preventing the Debug Module from being power gated while debugging
        #          is active.
        #*/
        self.var(bits('dmactive'))


class HARTINFOFields(bundle):
    def set_var(self):
        super(HARTINFOFields, self).set_var()

        self.var(bits('reserved0', w = 8))

        #/* Number of {\tt dscratch} registers available for the debugger
        #          to use during program buffer execution, starting from \Rdscratchzero.
        #          The debugger can make no assumptions about the contents of these
        #          registers between commands.
        #*/
        self.var(bits('nscratch', w = 4))

        self.var(bits('reserved1', w = 3))

        #/* 0: The {\tt data} registers are shadowed in the hart by CSR
        #          registers. Each CSR register is XLEN bits in size, and corresponds
        #          to a single argument, per Table~\ref{tab:datareg}.

        #          1: The {\tt data} registers are shadowed in the hart's memory map.
        #          Each register takes up 4 bytes in the memory map.
        #*/
        self.var(bits('dataaccess'))

        #/* If \Fdataaccess is 0: Number of CSR registers dedicated to
        #          shadowing the {\tt data} registers.

        #          If \Fdataaccess is 1: Number of 32-bit words in the memory map
        #          dedicated to shadowing the {\tt data} registers.

        #          Since there are at most 12 {\tt data} registers, the value in this
        #          register must be 12 or smaller.
        #*/
        self.var(bits('datasize', w = 4))

        #/* If \Fdataaccess is 0: The number of the first CSR dedicated to
        #          shadowing the {\tt data} registers.

        #          If \Fdataaccess is 1: Signed address of RAM where the {\tt data}
        #          registers are shadowed, to be used to access relative to \Rzero.
        #*/
        self.var(bits('dataaddr', w = 12))


class HAWINDOWSELFields(bundle):
    def set_var(self):
        super(HAWINDOWSELFields, self).set_var()

        self.var(bits('reserved0', w = 17))

        #/* The high bits of this field may be tied to 0, depending on how large
        #        the array mask register is.  Eg. on a system with 48 harts only bit 0
        #        of this field may actually be writable.
        #*/
        self.var(bits('hawindowsel', w = 15))


class HAWINDOWFields(bundle):
    def set_var(self):
        super(HAWINDOWFields, self).set_var()

        self.var(bits('maskdata', w = 32))


class ABSTRACTCSFields(bundle):
    def set_var(self):
        super(ABSTRACTCSFields, self).set_var()

        self.var(bits('reserved0', w = 3))

        #/* Size of the Program Buffer, in 32-bit words. Valid sizes are 0 - 16.
        #*/
        self.var(bits('progbufsize', w = 5))

        self.var(bits('reserved1', w = 11))

        #/* 1: An abstract command is currently being executed.

        #          This bit is set as soon as \Rcommand is written, and is
        #          not cleared until that command has completed.
        #*/
        self.var(bits('busy'))

        self.var(bits('reserved2', w = 1))

        #/* Gets set if an abstract command fails. The bits in this field remain set until
        #          they are cleared by writing 1 to them. No abstract command is
        #          started until the value is reset to 0.

        #          0 (none): No error.

        #          1 (busy): An abstract command was executing while \Rcommand,
        #          \Rabstractcs, \Rabstractauto was written, or when one
        #          of the {\tt data} or {\tt progbuf} registers was read or written.

        #          2 (not supported): The requested command is not supported,
        #          regardless of whether the hart is running or not.

        #          3 (exception): An exception occurred while executing the command
        #          (eg. while executing the Program Buffer).

        #          4 (halt/resume): The abstract command couldn't execute because the
        #          hart wasn't in the required state (running/halted).

        #          7 (other): The command failed for another reason.
        #*/
        self.var(bits('cmderr', w = 3))

        self.var(bits('reserved3', w = 4))

        #/* Number of {\tt data} registers that are implemented as part of the
        #          abstract command interface. Valid sizes are 0 - 12.
        #*/
        self.var(bits('datacount', w = 4))


class COMMANDFields(bundle):
    def set_var(self):
        super(COMMANDFields, self).set_var()

        #/* The type determines the overall functionality of this
        #          abstract command.
        #*/
        self.var(bits('cmdtype', w = 8))

        #/* This field is interpreted in a command-specific manner,
        #          described for each abstract command.
        #*/
        self.var(bits('control', w = 24))


class ABSTRACTAUTOFields(bundle):
    def set_var(self):
        super(ABSTRACTAUTOFields, self).set_var()

        #/* When a bit in this field is 1, read or write accesses to the corresponding {\tt progbuf} word
        #        cause the command in \Rcommand to be executed again.
        #*/
        self.var(bits('autoexecprogbuf', w = 16))

        self.var(bits('reserved0', w = 4))

        #/* When a bit in this field is 1, read or write accesses to the corresponding {\tt data} word
        #        cause the command in \Rcommand to be executed again.
        #*/
        self.var(bits('autoexecdata', w = 12))


class DEVTREEADDR0Fields(bundle):
    def set_var(self):
        super(DEVTREEADDR0Fields, self).set_var()

        self.var(bits('addr', w = 32))


class NEXTDMFields(bundle):
    def set_var(self):
        super(NEXTDMFields, self).set_var()

        self.var(bits('addr', w = 32))


class DATA0Fields(bundle):
    def set_var(self):
        super(DATA0Fields, self).set_var()

        self.var(bits('data', w = 32))


class PROGBUF0Fields(bundle):
    def set_var(self):
        super(PROGBUF0Fields, self).set_var()

        self.var(bits('data', w = 32))


class AUTHDATAFields(bundle):
    def set_var(self):
        super(AUTHDATAFields, self).set_var()

        self.var(bits('data', w = 32))


class HALTSUM0Fields(bundle):
    def set_var(self):
        super(HALTSUM0Fields, self).set_var()

        self.var(bits('haltsum0', w = 32))


class HALTSUM1Fields(bundle):
    def set_var(self):
        super(HALTSUM1Fields, self).set_var()

        self.var(bits('haltsum1', w = 32))


class HALTSUM2Fields(bundle):
    def set_var(self):
        super(HALTSUM2Fields, self).set_var()

        self.var(bits('haltsum2', w = 32))


class HALTSUM3Fields(bundle):
    def set_var(self):
        super(HALTSUM3Fields, self).set_var()

        self.var(bits('haltsum3', w = 32))


class SBADDRESS3Fields(bundle):
    def set_var(self):
        super(SBADDRESS3Fields, self).set_var()

        #/* Accesses bits 127:96 of the physical address in {\tt sbaddress} (if
        #          the system address bus is that wide).
        #*/
        self.var(bits('address', w = 32))


class SBCSFields(bundle):
    def set_var(self):
        super(SBCSFields, self).set_var()

        #/* 0: The System Bus interface conforms to mainline drafts of this
        #          spec older than 1 January, 2018.

        #          1: The System Bus interface conforms to this version of the spec.

        #          Other values are reserved for future versions.
        #*/
        self.var(bits('sbversion', w = 3))

        self.var(bits('reserved0', w = 6))

        #/* Set when the debugger attempts to read data while a read is in
        #          progress, or when the debugger initiates a new access while one is
        #          already in progress (while \Fsbbusy is set). It remains set until
        #          it's explicitly cleared by the debugger.

        #          While this field is non-zero, no more system bus accesses can be
        #          initiated by the debug module.
        #*/
        self.var(bits('sbbusyerror'))

        #/* When 1, indicates the system bus master is busy. (Whether the
        #          system bus itself is busy is related, but not the same thing.) This
        #          bit goes high immediately when a read or write is requested for any
        #          reason, and does not go low until the access is fully completed.

        #          To avoid race conditions, debuggers must not try to clear \Fsberror
        #          until they read \Fsbbusy as 0.
        #*/
        self.var(bits('sbbusy'))

        #/* When 1, every write to \Rsbaddresszero automatically triggers a
        #          system bus read at the new address.
        #*/
        self.var(bits('sbreadonaddr'))

        #/* Select the access size to use for system bus accesses.

        #          0: 8-bit

        #          1: 16-bit

        #          2: 32-bit

        #          3: 64-bit

        #          4: 128-bit

        #          If \Fsbaccess has an unsupported value when the DM starts a bus
        #          access, the access is not performed and \Fsberror is set to 3.
        #*/
        self.var(bits('sbaccess', w = 3))

        #/* When 1, {\tt sbaddress} is incremented by the access size (in
        #          bytes) selected in \Fsbaccess after every system bus access.
        #*/
        self.var(bits('sbautoincrement'))

        #/* When 1, every read from \Rsbdatazero automatically triggers a
        #          system bus read at the (possibly auto-incremented) address.
        #*/
        self.var(bits('sbreadondata'))

        #/* When the debug module's system bus
        #          master causes a bus error, this field gets set. The bits in this
        #          field remain set until they are cleared by writing 1 to them.
        #          While this field is non-zero, no more system bus accesses can be
        #          initiated by the debug module.

        #          An implementation may report "Other" (7) for any error condition.

        #          0: There was no bus error.

        #          1: There was a timeout.

        #          2: A bad address was accessed.

        #          3: There was an alignment error.

        #          4: An access of unsupported size was requested.

        #          7: Other.
        #*/
        self.var(bits('sberror', w = 3))

        #/* Width of system bus addresses in bits. (0 indicates there is no bus
        #          access support.)
        #*/
        self.var(bits('sbasize', w = 7))

        #/* 1 when 128-bit system bus accesses are supported.
        #*/
        self.var(bits('sbaccess128'))

        #/* 1 when 64-bit system bus accesses are supported.
        #*/
        self.var(bits('sbaccess64'))

        #/* 1 when 32-bit system bus accesses are supported.
        #*/
        self.var(bits('sbaccess32'))

        #/* 1 when 16-bit system bus accesses are supported.
        #*/
        self.var(bits('sbaccess16'))

        #/* 1 when 8-bit system bus accesses are supported.
        #*/
        self.var(bits('sbaccess8'))


class SBADDRESS0Fields(bundle):
    def set_var(self):
        super(SBADDRESS0Fields, self).set_var()

        #/* Accesses bits 31:0 of the physical address in {\tt sbaddress}.
        #*/
        self.var(bits('address', w = 32))


class SBADDRESS1Fields(bundle):
    def set_var(self):
        super(SBADDRESS1Fields, self).set_var()

        #/* Accesses bits 63:32 of the physical address in {\tt sbaddress} (if
        #          the system address bus is that wide).
        #*/
        self.var(bits('address', w = 32))


class SBADDRESS2Fields(bundle):
    def set_var(self):
        super(SBADDRESS2Fields, self).set_var()

        #/* Accesses bits 95:64 of the physical address in {\tt sbaddress} (if
        #          the system address bus is that wide).
        #*/
        self.var(bits('address', w = 32))


class SBDATA0Fields(bundle):
    def set_var(self):
        super(SBDATA0Fields, self).set_var()

        #/* Accesses bits 31:0 of {\tt sbdata}.
        #*/
        self.var(bits('data', w = 32))


class SBDATA1Fields(bundle):
    def set_var(self):
        super(SBDATA0Fields, self).set_var()

        #/* Accesses bits 63:32 of {\tt sbdata} (if the system bus is that
        #          wide).
        #*/
        self.var(bits('data', w = 32))


class SBDATA2Fields(bundle):
    def set_var(self):
        super(SBDATA2Fields, self).set_var()

        #/* Accesses bits 95:64 of {\tt sbdata} (if the system bus is that
        #          wide).
        #*/
        self.var(bits('data', w = 32))


class SBDATA3Fields(bundle):
    def set_var(self):
        super(SBDATA3Fields, self).set_var()

        #/* Accesses bits 127:96 of {\tt sbdata} (if the system bus is that
        #          wide).
        #*/
        self.var(bits('data', w = 32))
