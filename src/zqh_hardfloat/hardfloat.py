#source code coming from: https://github.com/ucb-bar/berkeley-hardfloat/tree/22ebeb54301ca85fa087180596d21fa56335fdbc/src/main/scala/*.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *

#/*============================================================================
#
#This Chisel source file is part of a pre-release version of the HardFloat IEEE
#Floating-Point Arithmetic Package, by John R. Hauser (with some contributions
#from Yunsup Lee and Andrew Waterman, mainly concerning testing).
#
#Copyright 2010, 2011, 2012, 2013, 2014, 2015, 2016 The Regents of the
#University of California.  All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the University nor the names of its contributors may
#    be used to endorse or promote products derived from this software without
#    specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS", AND ANY
#EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE
#DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#=============================================================================*/
#{{{
#primitives
def countLeadingZeros(in_):
    return pri_lsb_enc(in_.order_invert())

def orReduceBy2(in_):
    reducedWidth = (in_.get_w() + 1)>>1
    reducedVec = bits(w = reducedWidth)
    for ix in range(reducedWidth - 1):
        reducedVec[ix] /= in_[ix * 2 + 1: ix * 2].r_or()
    reducedVec[reducedWidth - 1] /= in_[in_.get_w() - 1: (reducedWidth - 1) * 2].r_or()
    return reducedVec.to_uint()

def orReduceBy4(in_):
    reducedWidth = (in_.get_w() + 3)>>2
    reducedVec = bits(w = reducedWidth)
    for ix in range(reducedWidth - 1):
        reducedVec[ix] /= in_[ix * 4 + 3: ix * 4].r_or()
    reducedVec[reducedWidth - 1] /= in_[in_.get_w() - 1: (reducedWidth - 1) * 4].r_or()
    return reducedVec.to_uint()

def lowMask(in_, topBound, bottomBound):
    assert(topBound != bottomBound)
    numInVals = 1<<in_.get_w()
    if (topBound < bottomBound):
        return lowMask(~in_, numInVals - 1 - topBound, numInVals - 1 - bottomBound)
    elif (numInVals > 64):
        ## For simulation performance, we should avoid generating
        ## exteremely wide shifters, so we divide and conquer.
        ## Empirically, this does not impact synthesis QoR.
        mid = int(numInVals / 2)
        msb = in_[in_.get_w() - 1]
        lsbs = in_[in_.get_w() - 2: 0]
        if (mid < topBound):
            if (mid <= bottomBound):
                return mux(msb,
                    lowMask(lsbs, topBound - mid, bottomBound - mid),
                    value(0)
                )
            else:
                return mux(msb,
                    cat([lowMask(lsbs, topBound - mid, 0),
                        value((1<<(mid - bottomBound)) - 1)
                    ]),
                    lowMask(lsbs, mid, bottomBound)
                )
        else:
            return ~mux(msb, value(0), ~lowMask(lsbs, topBound, bottomBound))
    else:
        shift = value(1<<numInVals).to_bits().to_sint()>>in_
        return shift[
                numInVals - 1 - bottomBound:
                numInVals - topBound
            ].order_invert()
##}}}

##{{{
#common
class consts(object):
    #/*------------------------------------------------------------------------
    #| For rounding to integer values, rounding mode 'odd' rounds to minimum
    #| magnitude instead, same as 'minMag'.
    #*------------------------------------------------------------------------*/
    @classmethod
    def round_near_even(self):
        return value(0b000, w = 3)
    @classmethod
    def round_minMag(self):
        return value(0b001, w = 3)
    @classmethod
    def round_min(self):
        return value(0b010, w = 3)
    @classmethod
    def round_max(self):
        return value(0b011, w = 3)
    @classmethod
    def round_near_maxMag(self):
        return value(0b100, w = 3)
    @classmethod
    def round_odd(self):
        return value(0b101, w = 3)
    #/*------------------------------------------------------------------------
    #*------------------------------------------------------------------------*/
    @classmethod
    def tininess_beforeRounding(self):
        return value(0, w = 1)
    @classmethod
    def tininess_afterRounding(self):
        return value(1, w = 1)
    #/*------------------------------------------------------------------------
    #*------------------------------------------------------------------------*/
    @classmethod
    def flRoundOpt_sigMSBitAlwaysZero(self):
        return 1
    @classmethod
    def flRoundOpt_subnormsAlwaysExact(self):
        return 2
    @classmethod
    def flRoundOpt_neverUnderflows(self):
        return 4
    @classmethod
    def flRoundOpt_neverOverflows(self):
        return 8

class RawFloat(bundle):
    def set_par(self):
        super(RawFloat, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)

    def set_var(self):
        super(RawFloat, self).set_var()
        self.var(bits('isNaN' ))              ## overrides all other fields
        self.var(bits('isInf' ))              ## overrides 'isZero', 'sExp', and 'sig'
        self.var(bits('isZero'))              ## overrides 'sExp' and 'sig'
        self.var(bits('sign'  ))
        self.var(bits('sExp', w = self.p.expWidth + 2).to_sint())
        self.var(bits('sig', w = self.p.sigWidth + 1))   ## 2 m.s. bits cannot both be 0

##*** CHANGE THIS INTO A '.isSigNaN' METHOD OF THE 'RawFloat' CLASS:
def isSigNaNRawFloat(in_):
    return in_.isNaN & ~in_.sig[in_.p.sigWidth - 2]

##}}}

##{{{
#rawFloatFromFN
def rawFloatFromFN(expWidth, sigWidth, in_):
    sign = in_[expWidth + sigWidth - 1]
    expIn = in_[expWidth + sigWidth - 2: sigWidth - 1]
    fractIn = in_[sigWidth - 2: 0]

    isZeroExpIn = (expIn == 0)
    isZeroFractIn = (fractIn == 0)

    normDist = countLeadingZeros(fractIn)
    subnormFract = (fractIn<<normDist)[sigWidth - 3: 0]<<1
    adjustedExp = \
        mux(isZeroExpIn, \
            normDist ^ ((1<<(expWidth + 1)) - 1), \
            expIn \
        ) + ((1<<(expWidth - 1)) \
                 | mux(isZeroExpIn, value(2, w = expWidth), value(1, w = expWidth)))

    isZero = isZeroExpIn & isZeroFractIn
    isSpecial = (adjustedExp[expWidth: expWidth - 1] == 3)

    out = RawFloat(expWidth = expWidth, sigWidth = sigWidth)
    out.isNaN  /= isSpecial & ~isZeroFractIn
    out.isInf  /= isSpecial &   isZeroFractIn
    out.isZero /= isZero
    out.sign   /= sign
    out.sExp   /= adjustedExp[expWidth: 0].z_ext()
    out.sig /= cat([value(0, w = 1), ~isZero, mux(isZeroExpIn, subnormFract, fractIn)])
    return out
##}}}

##{{{
#rawFloatFromIN
def rawFloatFromIN(signedIn, in_):
    expWidth = log2_up(in_.get_w())
    ##*** CHANGE THIS; CAN BE VERY LARGE:
    extIntWidth = 1<<expWidth

    sign = signedIn & in_[in_.get_w() - 1]
    absIn = mux(sign, -in_.as_uint(), in_.as_uint())
    extAbsIn = cat([value(0, w = extIntWidth), absIn])[extIntWidth - 1: 0]
    adjustedNormDist = countLeadingZeros(extAbsIn)
    sig = (extAbsIn<<adjustedNormDist)[extIntWidth - 1: extIntWidth - in_.get_w()]

    out = RawFloat(expWidth = expWidth, sigWidth = in_.get_w())
    out.isNaN  /= 0
    out.isInf  /= 0
    out.isZero /= ~sig[in_.get_w() - 1]
    out.sign   /= sign
    out.sExp   /= cat([value(1, 1), ~adjustedNormDist[expWidth - 1: 0]]).z_ext()
    out.sig    /= sig
    return out
##}}}

##{{{
#recFNFromFN
def recFNFromFN(expWidth, sigWidth, in_):
    rawIn = rawFloatFromFN(expWidth, sigWidth, in_)
    return cat([rawIn.sign,
        mux(rawIn.isZero, value(0, w = 3), rawIn.sExp[expWidth: expWidth - 2]) |
        mux(rawIn.isNaN, value(1, w = 3), value(0, w = 3)),
        rawIn.sExp[expWidth - 3: 0],
        rawIn.sig[sigWidth - 2: 0]
    ])
##}}}

##{{{
#rawFloatFromRecFN
#/*----------------------------------------------------------------------------
#| In the result, no more than one of 'isNaN', 'isInf', and 'isZero' will be
#| set.
#*----------------------------------------------------------------------------*/
def rawFloatFromRecFN(expWidth, sigWidth, in_):
    exp = in_[expWidth + sigWidth - 1: sigWidth - 1]
    isZero    = (exp[expWidth: expWidth - 2] == 0)
    isSpecial = (exp[expWidth: expWidth - 1] == 3)

    out = RawFloat(expWidth = expWidth, sigWidth = sigWidth)
    out.isNaN  /= isSpecial &  exp[expWidth - 2]
    out.isInf  /= isSpecial & ~exp[expWidth - 2]
    out.isZero /= isZero
    out.sign   /= in_[expWidth + sigWidth]
    out.sExp   /= exp.z_ext()
    out.sig    /= cat([value(0, 1), ~isZero, in_[sigWidth - 2: 0]])
    return out
##}}}

##{{{
#fNFromRecFN
def fNFromRecFN(expWidth, sigWidth, in_):
    minNormExp = (1<<(expWidth - 1)) + 2

    rawIn = rawFloatFromRecFN(expWidth, sigWidth, in_)

    isSubnormal = (rawIn.sExp < value(minNormExp, w = rawIn.sExp.get_w()).as_sint())
    denormShiftDist = value(1, w = log2_up(sigWidth - 1)) - rawIn.sExp[log2_up(sigWidth - 1) - 1: 0]
    denormFract = ((rawIn.sig>>1)>>denormShiftDist)[sigWidth - 2: 0]

    expOut = mux(isSubnormal,
        value(0, w = expWidth),
        rawIn.sExp[expWidth - 1: 0] -
        value((1<<(expWidth - 1)) + 1, w = expWidth))[expWidth - 1 : 0] | (rawIn.isNaN | rawIn.isInf).rep(expWidth)
    fractOut = mux(isSubnormal,
        denormFract,
        mux(rawIn.isInf, 0, rawIn.sig[sigWidth - 2: 0]))
    return cat([rawIn.sign, expOut, fractOut])
##}}}

##{{{
#MulAddRecFN
class MulAddRecFN_interIo(bundle):
    def set_par(self):
        super(MulAddRecFN_interIo, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)

    def set_var(self):
        super(MulAddRecFN_interIo, self).set_var()
##*** ENCODE SOME OF THESE CASES IN FEWER BITS?:
        self.var(bits('isSigNaNAny'))
        self.var(bits('isNaNAOrB'))
        self.var(bits('isInfA'))
        self.var(bits('isZeroA'))
        self.var(bits('isInfB'))
        self.var(bits('isZeroB'))
        self.var(bits('signProd'))
        self.var(bits('isNaNC'))
        self.var(bits('isInfC'))
        self.var(bits('isZeroC'))
        self.var(bits('sExpSum', w = self.p.expWidth + 2).to_sint())
        self.var(bits('doSubMags'))
        self.var(bits('CIsDominant'))
        self.var(bits('CDom_CAlignDist', w = log2_up(self.p.sigWidth + 1)))
        self.var(bits('highAlignedSigC', w = self.p.sigWidth + 2))
        self.var(bits('bit0AlignedSigC', w = 1))

class MulAddRecFNToRaw_preMulIO(bundle):
    def set_var(self):
        super(MulAddRecFNToRaw_preMulIO, self).set_var()
        self.var(inp('op', w = 2))
        self.var(inp('a', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('b', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('c', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(outp('mulAddA', w = self.p.sigWidth))
        self.var(outp('mulAddB', w = self.p.sigWidth))
        self.var(outp('mulAddC', w = self.p.sigWidth * 2))
        self.var(MulAddRecFN_interIo('toPostMul', p = self.p).as_output())

class MulAddRecFNToRaw_preMul(module):
    def set_par(self):
        super(MulAddRecFNToRaw_preMul, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)

    def set_port(self):
        super(MulAddRecFNToRaw_preMul, self).set_port()
        self.io = MulAddRecFNToRaw_preMulIO('io', p = self.p)

    def main(self):
        super(MulAddRecFNToRaw_preMul, self).main()
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        ##*** POSSIBLE TO REDUCE THIS BY 1 OR 2 BITS?  (CURRENTLY 2 BITS BETWEEN
        ##***  UNSHIFTED C AND PRODUCT):
        sigSumWidth = self.p.sigWidth * 3 + 3
    
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        rawA = rawFloatFromRecFN(self.p.expWidth, self.p.sigWidth, self.io.a)
        rawB = rawFloatFromRecFN(self.p.expWidth, self.p.sigWidth, self.io.b)
        rawC = rawFloatFromRecFN(self.p.expWidth, self.p.sigWidth, self.io.c)
    
        signProd = rawA.sign ^ rawB.sign ^ self.io.op[1]
        ##*** REVIEW THE BIAS FOR 'sExpAlignedProd':
        sExpAlignedProd = rawA.sExp + rawB.sExp + value(-(1<<self.p.expWidth) + self.p.sigWidth + 3, w = self.p.expWidth + 2).to_sint()
    
        doSubMags = signProd ^ rawC.sign ^ self.io.op[0]
    
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        sNatCAlignDist = sExpAlignedProd - rawC.sExp
        posNatCAlignDist = sNatCAlignDist[self.p.expWidth + 1: 0].to_uint()
        isMinCAlign = rawA.isZero | rawB.isZero | (sNatCAlignDist < value(0).to_sint())
        CIsDominant = ~rawC.isZero & (isMinCAlign | (posNatCAlignDist <= value(self.p.sigWidth)))
        CAlignDist = mux(isMinCAlign,
                value(0),
                mux(posNatCAlignDist < value(sigSumWidth - 1),
                    posNatCAlignDist[log2_up(sigSumWidth) - 1: 0],
                    value(sigSumWidth - 1)
                )
            )
        mainAlignedSigC = cat([mux(doSubMags, ~rawC.sig, rawC.sig),
                doSubMags.rep(sigSumWidth - self.p.sigWidth + 2)
            ]).to_sint()>>CAlignDist
        reduced4CExtra = (orReduceBy4(rawC.sig<<((sigSumWidth - self.p.sigWidth - 1) & 3)) &
                 lowMask(
                     CAlignDist>>2,
        ##*** NOT NEEDED?:
        ##                 (sigSumWidth + 2)>>2,
                     (sigSumWidth - 1)>>2,
                     (sigSumWidth - self.p.sigWidth - 1)>>2
                 )
            ).r_or()
        alignedSigC = cat([mainAlignedSigC>>3,
                mux(doSubMags,
                    mainAlignedSigC[2: 0].r_and() & ~reduced4CExtra,
                    mainAlignedSigC[2: 0].r_or() |   reduced4CExtra
                )
            ])
    
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        self.io.mulAddA /= rawA.sig
        self.io.mulAddB /= rawB.sig
        self.io.mulAddC /= alignedSigC[self.p.sigWidth * 2: 1]
    
        self.io.toPostMul.isSigNaNAny /= isSigNaNRawFloat(rawA) | isSigNaNRawFloat(rawB) | isSigNaNRawFloat(rawC)
        self.io.toPostMul.isNaNAOrB /= rawA.isNaN | rawB.isNaN
        self.io.toPostMul.isInfA    /= rawA.isInf
        self.io.toPostMul.isZeroA   /= rawA.isZero
        self.io.toPostMul.isInfB    /= rawB.isInf
        self.io.toPostMul.isZeroB   /= rawB.isZero
        self.io.toPostMul.signProd  /= signProd
        self.io.toPostMul.isNaNC    /= rawC.isNaN
        self.io.toPostMul.isInfC    /= rawC.isInf
        self.io.toPostMul.isZeroC   /= rawC.isZero
        self.io.toPostMul.sExpSum   /= mux(CIsDominant, rawC.sExp, sExpAlignedProd - value(self.p.sigWidth, w = sExpAlignedProd.get_w()).to_sint())
        self.io.toPostMul.doSubMags /= doSubMags
        self.io.toPostMul.CIsDominant /= CIsDominant
        self.io.toPostMul.CDom_CAlignDist /= CAlignDist[log2_up(self.p.sigWidth + 1) - 1: 0]
        self.io.toPostMul.highAlignedSigC /= alignedSigC[sigSumWidth - 1: self.p.sigWidth * 2 + 1]
        self.io.toPostMul.bit0AlignedSigC /= alignedSigC[0]

class MulAddRecFNToRaw_postMulIO(bundle):
    def set_var(self):
        super(MulAddRecFNToRaw_postMulIO, self).set_var()
        self.var(MulAddRecFN_interIo('fromPreMul', expWidth = self.p.expWidth, sigWidth = self.p.sigWidth).as_input())
        self.var(inp('mulAddResult', w = self.p.sigWidth * 2 + 1))
        self.var(inp('roundingMode', w = 3))
        self.var(outp('invalidExc'))
        self.var(RawFloat('rawOut', expWidth = self.p.expWidth, sigWidth = self.p.sigWidth + 2).as_output())

class MulAddRecFNToRaw_postMul(module):
    def set_par(self):
        super(MulAddRecFNToRaw_postMul, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)

    def set_port(self):
        super(MulAddRecFNToRaw_postMul, self).set_port()
        self.io = MulAddRecFNToRaw_postMulIO('io', p = self.p)
    
    def main(self):
        super(MulAddRecFNToRaw_postMul, self).main()
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        sigSumWidth = self.p.sigWidth * 3 + 3

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        roundingMode_min = (self.io.roundingMode == consts.round_min())

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        opSignC = self.io.fromPreMul.signProd ^ self.io.fromPreMul.doSubMags
        sigSum = cat([mux(self.io.mulAddResult[self.p.sigWidth * 2],
                    self.io.fromPreMul.highAlignedSigC + value(1),
                    self.io.fromPreMul.highAlignedSigC
                   ),
                self.io.mulAddResult[self.p.sigWidth * 2 - 1: 0],
                self.io.fromPreMul.bit0AlignedSigC
            ])

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        CDom_sign = opSignC
        CDom_sExp = self.io.fromPreMul.sExpSum - self.io.fromPreMul.doSubMags.z_ext()
        CDom_absSigSum = mux(self.io.fromPreMul.doSubMags,
                ~sigSum[sigSumWidth - 1: self.p.sigWidth + 1],
                cat([value(0, w = 1),
        ##*** IF GAP IS REDUCED TO 1 BIT, MUST REDUCE THIS COMPONENT TO 1 BIT TOO:
                    self.io.fromPreMul.highAlignedSigC[self.p.sigWidth + 1: self.p.sigWidth],
                    sigSum[sigSumWidth - 3: self.p.sigWidth + 2]
                ])
            )
        CDom_absSigSumExtra = mux(self.io.fromPreMul.doSubMags,
                (~sigSum[self.p.sigWidth: 1]).r_or(),
                sigSum[self.p.sigWidth + 1: 1].r_or()
            )
        CDom_mainSig = (CDom_absSigSum<<self.io.fromPreMul.CDom_CAlignDist)[
                self.p.sigWidth * 2 + 1: self.p.sigWidth - 3]
        CDom_reduced4SigExtra = (orReduceBy4(CDom_absSigSum[self.p.sigWidth - 1: 0]<<(~self.p.sigWidth & 3)) &
                 lowMask(self.io.fromPreMul.CDom_CAlignDist>>2, 0, self.p.sigWidth>>2)).r_or()
        CDom_sig = cat([CDom_mainSig>>3,
                CDom_mainSig[2: 0].r_or() | CDom_reduced4SigExtra |
                    CDom_absSigSumExtra
            ])

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        notCDom_signSigSum = sigSum[self.p.sigWidth * 2 + 3]
        notCDom_absSigSum = mux(notCDom_signSigSum,
                ~sigSum[self.p.sigWidth * 2 + 2: 0],
                sigSum[self.p.sigWidth * 2 + 2: 0] + self.io.fromPreMul.doSubMags
            )
        notCDom_reduced2AbsSigSum = orReduceBy2(notCDom_absSigSum)
        notCDom_normDistReduced2 = countLeadingZeros(notCDom_reduced2AbsSigSum)
        notCDom_nearNormDist = notCDom_normDistReduced2<<1
        notCDom_sExp = self.io.fromPreMul.sExpSum - notCDom_nearNormDist.z_ext()
        notCDom_mainSig = (notCDom_absSigSum<<notCDom_nearNormDist)[
                self.p.sigWidth * 2 + 3: self.p.sigWidth - 1]
        notCDom_reduced4SigExtra = (orReduceBy2(
                 notCDom_reduced2AbsSigSum[self.p.sigWidth>>1: 0]<<((self.p.sigWidth>>1) & 1)) &
                 lowMask(notCDom_normDistReduced2>>1, 0, (self.p.sigWidth + 2)>>2)
            ).r_or()
        notCDom_sig = cat([notCDom_mainSig>>3,
                notCDom_mainSig[2: 0].r_or() | notCDom_reduced4SigExtra
            ])
        notCDom_completeCancellation = (notCDom_sig[self.p.sigWidth + 2: self.p.sigWidth + 1] == value(0))
        notCDom_sign = mux(notCDom_completeCancellation,
                roundingMode_min,
                self.io.fromPreMul.signProd ^ notCDom_signSigSum
            )

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        notNaN_isInfProd = self.io.fromPreMul.isInfA | self.io.fromPreMul.isInfB
        notNaN_isInfOut = notNaN_isInfProd | self.io.fromPreMul.isInfC
        notNaN_addZeros = (self.io.fromPreMul.isZeroA | self.io.fromPreMul.isZeroB) & self.io.fromPreMul.isZeroC

        self.io.invalidExc /= self.io.fromPreMul.isSigNaNAny | \
            (self.io.fromPreMul.isInfA & self.io.fromPreMul.isZeroB) | \
            (self.io.fromPreMul.isZeroA & self.io.fromPreMul.isInfB) | \
            (~self.io.fromPreMul.isNaNAOrB & \
                 (self.io.fromPreMul.isInfA | self.io.fromPreMul.isInfB) & \
                 self.io.fromPreMul.isInfC & \
                 self.io.fromPreMul.doSubMags)
        self.io.rawOut.isNaN /= self.io.fromPreMul.isNaNAOrB | self.io.fromPreMul.isNaNC
        self.io.rawOut.isInf /= notNaN_isInfOut
        ##*** IMPROVE?:
        self.io.rawOut.isZero /= notNaN_addZeros | (~self.io.fromPreMul.CIsDominant & notCDom_completeCancellation)
        self.io.rawOut.sign /= \
            (notNaN_isInfProd & self.io.fromPreMul.signProd) | \
            (self.io.fromPreMul.isInfC & opSignC) | \
            (notNaN_addZeros & ~roundingMode_min & \
                self.io.fromPreMul.signProd & opSignC) | \
            (notNaN_addZeros & roundingMode_min & \
                (self.io.fromPreMul.signProd | opSignC)) | \
            (~notNaN_isInfOut & ~notNaN_addZeros & \
                 mux(self.io.fromPreMul.CIsDominant, CDom_sign, notCDom_sign))
        self.io.rawOut.sExp /= mux(self.io.fromPreMul.CIsDominant, CDom_sExp, notCDom_sExp)
        self.io.rawOut.sig /= mux(self.io.fromPreMul.CIsDominant, CDom_sig, notCDom_sig)
##}}}

##{{{
#RoundAnyRawFNToRecFN
class RoundAnyRawFNToRecFNIO(bundle):
    def set_var(self):
        super(RoundAnyRawFNToRecFNIO, self).set_var()
        self.var(inp('invalidExc'))   ## overrides 'infiniteExc' and 'in'
        self.var(inp('infiniteExc'))   ## overrides 'in' except for 'in.sign'
        self.var(RawFloat('input', expWidth = self.p.inExpWidth, sigWidth = self.p.inSigWidth).as_input())
                                                  ## (allowed exponent range has limits)
        self.var(inp('roundingMode', w = 3))
        self.var(inp('detectTininess', w = 1))
        self.var(outp('output', w = self.p.outExpWidth + self.p.outSigWidth + 1))
        self.var(outp('exceptionFlags', w = 5))

class RoundAnyRawFNToRecFN(module):
    def set_par(self):
        super(RoundAnyRawFNToRecFN, self).set_par()
        self.p.par('inExpWidth', None)
        self.p.par('inSigWidth', None)
        self.p.par('outExpWidth', None)
        self.p.par('outSigWidth', None)
        self.p.par('options', None)

    def set_port(self):
        super(RoundAnyRawFNToRecFN, self).set_port()
        self.io = RoundAnyRawFNToRecFNIO('io', p = self.p)

    def main(self):
        super(RoundAnyRawFNToRecFN, self).main()
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        sigMSBitAlwaysZero = ((self.p.options & consts.flRoundOpt_sigMSBitAlwaysZero()) != 0)
        effectiveInSigWidth = self.p.inSigWidth if (sigMSBitAlwaysZero) else (self.p.inSigWidth + 1)
        neverUnderflows = ((self.p.options & (consts.flRoundOpt_neverUnderflows() | consts.flRoundOpt_subnormsAlwaysExact())
             ) != 0) | (self.p.inExpWidth < self.p.outExpWidth)
        neverOverflows = ((self.p.options & consts.flRoundOpt_neverOverflows()) != 0) | (self.p.inExpWidth < self.p.outExpWidth)
        outNaNExp = 7<<(self.p.outExpWidth - 2)
        outInfExp = 6<<(self.p.outExpWidth - 2)
        outMaxFiniteExp = outInfExp - 1
        outMinNormExp = (1<<(self.p.outExpWidth - 1)) + 2
        outMinNonzeroExp = outMinNormExp - self.p.outSigWidth + 1

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        roundingMode_near_even   = (self.io.roundingMode == consts.round_near_even())
        roundingMode_minMag      = (self.io.roundingMode == consts.round_minMag())
        roundingMode_min         = (self.io.roundingMode == consts.round_min())
        roundingMode_max         = (self.io.roundingMode == consts.round_max())
        roundingMode_near_maxMag = (self.io.roundingMode == consts.round_near_maxMag())
        roundingMode_odd         = (self.io.roundingMode == consts.round_odd())

        roundMagUp = (roundingMode_min & self.io.input.sign) | (roundingMode_max & ~self.io.input.sign)

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        if (self.p.inExpWidth < self.p.outExpWidth):
            sAdjustedExp = (self.io.input.sExp +
                 (value(1<<self.p.outExpWidth).to_bits() - value(1<<self.p.inExpWidth).to_bits()).to_sint()
            )[self.p.outExpWidth: 0].z_ext()
        elif (self.p.inExpWidth == self.p.outExpWidth):
            sAdjustedExp = self.io.input.sExp
        else:
            sAdjustedExp = self.io.input.sExp + (value(1<<self.p.outExpWidth).to_bits() - value(1<<self.p.inExpWidth).to_bits()).to_sint()
        if (self.p.inSigWidth <= self.p.outSigWidth + 2):
            adjustedSig = self.io.input.sig<<(self.p.outSigWidth - self.p.inSigWidth + 2)
        else:
            adjustedSig = cat([self.io.input.sig[self.p.inSigWidth: self.p.inSigWidth - self.p.outSigWidth - 1],
                self.io.input.sig[self.p.inSigWidth - self.p.outSigWidth - 2: 0].r_or()
            ])
        doShiftSigDown1 = value(0) if (sigMSBitAlwaysZero) else adjustedSig[self.p.outSigWidth + 2]

        common_expOut   = bits('common_expOut', w = self.p.outExpWidth + 1)
        common_fractOut = bits('common_fractOut', w = self.p.outSigWidth - 1)
        common_overflow       = bits('common_overflow')
        common_totalUnderflow = bits('common_totalUnderflow')
        common_underflow      = bits('common_underflow')
        common_inexact        = bits('common_inexact')

        if ( neverOverflows & neverUnderflows & (effectiveInSigWidth <= self.p.outSigWidth)):

            ##--------------------------------------------------------------------
            ##--------------------------------------------------------------------
            common_expOut /= sAdjustedExp[self.p.outExpWidth: 0] + doShiftSigDown1
            common_fractOut /= mux(doShiftSigDown1,
                    adjustedSig[self.p.outSigWidth + 1: 3],
                    adjustedSig[self.p.outSigWidth: 2]
                )
            common_overflow       /= 0 
            common_totalUnderflow /= 0 
            common_underflow      /= 0 
            common_inexact        /= 0 

        else:
            ##--------------------------------------------------------------------
            ##--------------------------------------------------------------------
            if (neverUnderflows):
                roundMask = cat([value(0, w = self.p.outSigWidth), doShiftSigDown1, value(3, w = 2)])
            else:
                roundMask = cat([lowMask(
                        sAdjustedExp[self.p.outExpWidth: 0],
                        outMinNormExp - self.p.outSigWidth - 1,
                        outMinNormExp
                    ) | doShiftSigDown1,
                    value(3, w = 2)
                ])
            shiftedRoundMask = cat([value(0, 1), (roundMask>>1)])
            roundPosMask = ~shiftedRoundMask & roundMask
            roundPosBit = (adjustedSig & roundPosMask).r_or()
            anyRoundExtra = (adjustedSig & shiftedRoundMask).r_or()
            anyRound = roundPosBit | anyRoundExtra

            roundIncr = ((roundingMode_near_even | roundingMode_near_maxMag) & roundPosBit) | \
                    (roundMagUp & anyRound)
            roundedSig = mux(roundIncr,
                    (((adjustedSig | roundMask)>>2) + value(1)) &
                        ~mux(roundingMode_near_even & roundPosBit &
                                 ~anyRoundExtra,
                             roundMask>>1,
                             value(0, w = self.p.outSigWidth + 2)
                         ),
                    (adjustedSig & ~roundMask)>>2 |
                        mux(roundingMode_odd & anyRound, roundPosMask>>1, value(0))
                )
            ##*** IF SIG WIDTH IS VERY NARROW, NEED TO ACCOUNT FOR ROUND-EVEN ZEROING
            ##***  M.S. BIT OF SUBNORMAL SIG?
            sRoundedExp = sAdjustedExp + (roundedSig>>self.p.outSigWidth).z_ext()

            common_expOut /= sRoundedExp[self.p.outExpWidth: 0]
            common_fractOut /= mux(doShiftSigDown1,
                    roundedSig[self.p.outSigWidth - 1: 1],
                    roundedSig[self.p.outSigWidth - 2: 0]
                )
            common_overflow /= (value(0) if (neverOverflows) else (sRoundedExp>>(self.p.outExpWidth - 1) >= value(3, w = sRoundedExp.get_w()).to_sint()))
            common_totalUnderflow /= (value(0) if (neverUnderflows) else (sRoundedExp < value(outMinNonzeroExp, w = sRoundedExp.get_w()).to_sint()))

            unboundedRange_roundPosBit = mux(doShiftSigDown1, adjustedSig[2], adjustedSig[1])
            unboundedRange_anyRound = (doShiftSigDown1 & adjustedSig[2]) | adjustedSig[1: 0].r_or()
            unboundedRange_roundIncr = ((roundingMode_near_even | roundingMode_near_maxMag) &
                     unboundedRange_roundPosBit) | (roundMagUp & unboundedRange_anyRound)
            roundCarry = mux(doShiftSigDown1,
                    roundedSig[self.p.outSigWidth + 1],
                    roundedSig[self.p.outSigWidth]
                )
            common_underflow /= (value(0) if (neverUnderflows) else common_totalUnderflow | \
                         (anyRound & ((sAdjustedExp>>(self.p.outExpWidth)) <= value(0, w = sAdjustedExp.get_w()).to_sint()) & \
                              mux(doShiftSigDown1, roundMask[3], roundMask[2]) & \
                              ~((self.io.detectTininess == consts.tininess_afterRounding()) & \
                                     ~mux(doShiftSigDown1, \
                                           roundMask[4], \
                                           roundMask[3] \
                                       ) & \
                                     roundCarry & roundPosBit & \
                                     unboundedRange_roundIncr)))

            common_inexact /= common_totalUnderflow | anyRound

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        isNaNOut = self.io.invalidExc | self.io.input.isNaN
        notNaN_isSpecialInfOut = self.io.infiniteExc | self.io.input.isInf
        commonCase = ~isNaNOut & ~notNaN_isSpecialInfOut & ~self.io.input.isZero
        overflow  = commonCase & common_overflow
        underflow = commonCase & common_underflow
        inexact = overflow | (commonCase & common_inexact)

        overflow_roundMagUp = roundingMode_near_even | roundingMode_near_maxMag | roundMagUp
        pegMinNonzeroMagOut = commonCase & common_totalUnderflow & (roundMagUp | roundingMode_odd)
        pegMaxFiniteMagOut = overflow & ~overflow_roundMagUp
        notNaN_isInfOut = notNaN_isSpecialInfOut | (overflow & overflow_roundMagUp)

        signOut = mux(isNaNOut, value(0), self.io.input.sign)
        expOut = (common_expOut & \
                 ~mux(self.io.input.isZero | common_totalUnderflow, \
                      value(7<<(self.p.outExpWidth - 2), w = self.p.outExpWidth + 1), \
                      value(0) \
                  ) & \
                 ~mux(pegMinNonzeroMagOut, \
                      ~value(outMinNonzeroExp, w = self.p.outExpWidth + 1).to_bits(), \
                      value(0) \
                  ) & \
                 ~mux(pegMaxFiniteMagOut, \
                      value(1<<(self.p.outExpWidth - 1), w = self.p.outExpWidth + 1), \
                      value(0) \
                  ) & \
                 ~mux(notNaN_isInfOut, \
                      value(1<<(self.p.outExpWidth - 2), w = self.p.outExpWidth + 1), \
                      value(0) \
                  )) | \
                mux(pegMinNonzeroMagOut, \
                    value(outMinNonzeroExp, w = self.p.outExpWidth + 1), \
                    value(0) \
                ) | \
                mux(pegMaxFiniteMagOut, \
                    value(outMaxFiniteExp, w = self.p.outExpWidth + 1), \
                    value(0) \
                ) | \
                mux(notNaN_isInfOut, value(outInfExp, w = self.p.outExpWidth + 1), value(0)) | \
                mux(isNaNOut,        value(outNaNExp, w = self.p.outExpWidth + 1), value(0))
        fractOut = mux(isNaNOut | self.io.input.isZero | common_totalUnderflow, \
                mux(isNaNOut, value(1<<(self.p.outSigWidth - 2)), value(0)), \
                common_fractOut \
            ) | \
            pegMaxFiniteMagOut.rep(self.p.outSigWidth - 1)

        self.io.output /= cat([signOut, expOut, fractOut])
        self.io.exceptionFlags /= cat([self.io.invalidExc, self.io.infiniteExc, overflow, underflow, inexact])

class RoundRawFNToRecFNIO(bundle):
    def set_var(self):
        super(RoundRawFNToRecFNIO, self).set_var()
        self.var(inp('invalidExc'))   ## overrides 'infiniteExc' and 'in'
        self.var(inp('infiniteExc'))   ## overrides 'in' except for 'in.sign'
        self.var(RawFloat('input', expWidth = self.p.expWidth, sigWidth = self.p.sigWidth + 2).as_input())
        self.var(inp('roundingMode', w = 3))
        self.var(inp('detectTininess', w = 1))
        self.var(outp('output', w =  self.p.expWidth + self.p.sigWidth + 1))
        self.var(outp('exceptionFlags', w = 5))

class RoundRawFNToRecFN(module):
    def set_par(self):
        super(RoundRawFNToRecFN, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)
        self.p.par('options', None)

    def set_port(self):
        super(RoundRawFNToRecFN, self).set_port()
        self.io = RoundRawFNToRecFNIO('io', p = self.p)

    def main(self):
        super(RoundRawFNToRecFN, self).main()
        roundAnyRawFNToRecFN = RoundAnyRawFNToRecFN('roundAnyRawFNToRecFN', inExpWidth = self.p.expWidth, inSigWidth = self.p.sigWidth + 2, outExpWidth = self.p.expWidth, outSigWidth = self.p.sigWidth, options = self.p.options)
        roundAnyRawFNToRecFN.io.invalidExc     /= self.io.invalidExc
        roundAnyRawFNToRecFN.io.infiniteExc    /= self.io.infiniteExc
        roundAnyRawFNToRecFN.io.input          /= self.io.input
        roundAnyRawFNToRecFN.io.roundingMode   /= self.io.roundingMode
        roundAnyRawFNToRecFN.io.detectTininess /= self.io.detectTininess
        self.io.output            /= roundAnyRawFNToRecFN.io.output
        self.io.exceptionFlags /= roundAnyRawFNToRecFN.io.exceptionFlags
##}}}

##{{{
#CompareRecFN
class CompareRecFNIO(bundle):
    def set_var(self):
        super(CompareRecFNIO, self).set_var()
        self.var(inp('a', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('b', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('signaling'))
        self.var(outp('lt'))
        self.var(outp('eq'))
        self.var(outp('gt'))
        self.var(outp('exceptionFlags', w = 5))

class CompareRecFN(module):
    def set_par(self):
        super(CompareRecFN, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)

    def set_port(self):
        super(CompareRecFN, self).set_port()
        self.io = CompareRecFNIO('io', p = self.p)

    def main(self):
        super(CompareRecFN, self).main()
        rawA = rawFloatFromRecFN(self.p.expWidth, self.p.sigWidth, self.io.a)
        rawB = rawFloatFromRecFN(self.p.expWidth, self.p.sigWidth, self.io.b)

        ordered = ~rawA.isNaN & ~rawB.isNaN
        bothInfs  = rawA.isInf & rawB.isInf
        bothZeros = rawA.isZero & rawB.isZero
        eqExps = (rawA.sExp == rawB.sExp)
        common_ltMags = (rawA.sExp < rawB.sExp) | (eqExps & (rawA.sig < rawB.sig))
        common_eqMags = eqExps & (rawA.sig == rawB.sig)

        ordered_lt = \
            ~bothZeros & \
                ((rawA.sign & ~rawB.sign) | \
                     (~bothInfs & \
                          ((rawA.sign & ~common_ltMags & ~common_eqMags) | \
                               (~rawB.sign & common_ltMags))))
        ordered_eq = bothZeros | ((rawA.sign == rawB.sign) & (bothInfs | common_eqMags))

        invalid = isSigNaNRawFloat(rawA) | isSigNaNRawFloat(rawB) | (self.io.signaling & ~ordered)

        self.io.lt /= ordered & ordered_lt
        self.io.eq /= ordered & ordered_eq
        self.io.gt /= ordered & ~ordered_lt & ~ordered_eq
        self.io.exceptionFlags /= cat([invalid, value(0, w = 4)])

##}}}

##{{{
#RecFNToIN
class RecFNToINIO(bundle):
    def set_var(self):
        super(RecFNToINIO, self).set_var()
        self.var(inp('input', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('roundingMode', w = 3))
        self.var(inp('signedOut'))
        self.var(outp('output', w = self.p.intWidth))
        self.var(outp('intExceptionFlags', w = 3))

class RecFNToIN(module):
    def set_par(self):
        super(RecFNToIN, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)
        self.p.par('intWidth', None)

    def set_port(self):
        super(RecFNToIN, self).set_port()
        self.io = RecFNToINIO('io', p = self.p)
    
    def main(self):
        super(RecFNToIN, self).main()
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        rawIn = rawFloatFromRecFN(self.p.expWidth, self.p.sigWidth, self.io.input)

        magGeOne = rawIn.sExp[self.p.expWidth]
        posExp = rawIn.sExp[self.p.expWidth - 1: 0]
        magJustBelowOne = ~magGeOne & posExp.r_and()

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        roundingMode_near_even   = (self.io.roundingMode == consts.round_near_even())
        roundingMode_minMag = (self.io.roundingMode == consts.round_minMag()) | (self.io.roundingMode == consts.round_odd())
        roundingMode_min         = (self.io.roundingMode == consts.round_min())
        roundingMode_max         = (self.io.roundingMode == consts.round_max())
        roundingMode_near_maxMag = (self.io.roundingMode == consts.round_near_maxMag())

        #/*------------------------------------------------------------------------
        #| Assuming the input floating-point value is not a NaN, its magnitude is
        #| at least 1, and it is not obviously so large as to lead to overflow,
        #| convert its significand to fixed-point (i.e., with the binary point in a
        #| fixed location).  For a non-NaN input with a magnitude less than 1, this
        #| expression contrives to ensure that the integer bits of 'alignedSig'
        #| will all be zeros.
        #*------------------------------------------------------------------------*/
        shiftedSig = cat([magGeOne, rawIn.sig[self.p.sigWidth - 2: 0]])<< mux(magGeOne,
                    rawIn.sExp[min(self.p.expWidth - 2, log2_up(self.p.intWidth) - 1): 0],
                    value(0)
                )
        alignedSig = cat([shiftedSig>>(self.p.sigWidth - 2), shiftedSig[self.p.sigWidth - 3: 0].r_or()])
        unroundedInt = value(0, self.p.intWidth) | alignedSig>>2

        common_inexact = mux(magGeOne, alignedSig[1: 0].r_or(), ~rawIn.isZero)
        roundIncr_near_even = \
            (magGeOne       & (alignedSig[2: 1].r_and() | alignedSig[1: 0].r_and())) | \
            (magJustBelowOne & alignedSig[1: 0].r_or())
        roundIncr_near_maxMag = (magGeOne & alignedSig[1]) | magJustBelowOne
        roundIncr = \
            (roundingMode_near_even   & roundIncr_near_even             ) | \
            (roundingMode_near_maxMag & roundIncr_near_maxMag           ) | \
            (roundingMode_min         & ( rawIn.sign & common_inexact)) | \
            (roundingMode_max         & (~rawIn.sign & common_inexact))
        complUnroundedInt = mux(rawIn.sign, ~unroundedInt, unroundedInt)
        roundedInt = mux(roundIncr ^ rawIn.sign,
                complUnroundedInt + value(1),
                complUnroundedInt
            )

        magGeOne_atOverflowEdge = (posExp == value(self.p.intWidth - 1))
        ##*** CHANGE TO TAKE BITS FROM THE ORIGINAL 'rawIn.sig' INSTEAD OF FROM
        ##***  'unroundedInt'?:
        roundCarryBut2 = unroundedInt[self.p.intWidth - 3: 0].r_and() & roundIncr
        common_overflow = \
            mux(magGeOne,
                (posExp >= value(self.p.intWidth)) |
                    mux(self.io.signedOut, 
                        mux(rawIn.sign,
                            magGeOne_atOverflowEdge &
                                (unroundedInt[self.p.intWidth - 2: 0].r_or() | roundIncr),
                            magGeOne_atOverflowEdge |
                                ((posExp == value(self.p.intWidth - 2)) & roundCarryBut2)
                        ),
                        rawIn.sign |
                            (magGeOne_atOverflowEdge &
                                 unroundedInt[self.p.intWidth - 2] & roundCarryBut2)
                    ),
                ~self.io.signedOut & rawIn.sign & roundIncr
            )

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        invalidExc = rawIn.isNaN | rawIn.isInf
        overflow = ~invalidExc & common_overflow
        inexact  = ~invalidExc & ~common_overflow & common_inexact

        excSign = ~rawIn.isNaN & rawIn.sign
        excOut = \
            mux((self.io.signedOut == excSign),
                value(1<<(self.p.intWidth - 1)),
                value(0)
            ) | mux(~excSign, value((1<<(self.p.intWidth - 1)) - 1), value(0))

        self.io.output /= mux(invalidExc | common_overflow, excOut, roundedInt)
        self.io.intExceptionFlags /= cat([invalidExc, overflow, inexact])
##}}}

##{{{
#INToRecFN
class INToRecFNIO(bundle):
    def set_var(self):
        super(INToRecFNIO, self).set_var()
        self.var(inp('signedIn'))
        self.var(inp('input', w = self.p.intWidth))
        self.var(inp('roundingMode', w = 3))
        self.var(inp('detectTininess', w = 1))
        self.var(outp('output', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(outp('exceptionFlags', w = 5))

class INToRecFN(module):
    def set_par(self):
        super(INToRecFN, self).set_par()
        self.p.par('intWidth', None)
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)

    def set_port(self):
        super(INToRecFN, self).set_port()
        self.io = INToRecFNIO('io', p = self.p)

    def main(self):
        super(INToRecFN, self).main()
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        intAsRawFloat = rawFloatFromIN(self.io.signedIn, self.io.input)

        self.p.par('inExpWidth', None)
        self.p.par('inSigWidth', None)
        self.p.par('outExpWidth', None)
        self.p.par('outSigWidth', None)
        self.p.par('options', None)
        roundAnyRawFNToRecFN = RoundAnyRawFNToRecFN('roundAnyRawFNToRecFN', 
                        inExpWidth = intAsRawFloat.p.expWidth,
                        inSigWidth = self.p.intWidth,
                        outExpWidth = self.p.expWidth,
                        outSigWidth = self.p.sigWidth,
                        options = consts.flRoundOpt_sigMSBitAlwaysZero() | consts.flRoundOpt_neverUnderflows()
                    )
        roundAnyRawFNToRecFN.io.invalidExc     /= 0
        roundAnyRawFNToRecFN.io.infiniteExc    /= 0
        roundAnyRawFNToRecFN.io.input          /= intAsRawFloat
        roundAnyRawFNToRecFN.io.roundingMode   /= self.io.roundingMode
        roundAnyRawFNToRecFN.io.detectTininess /= self.io.detectTininess
        self.io.output            /= roundAnyRawFNToRecFN.io.output
        self.io.exceptionFlags /= roundAnyRawFNToRecFN.io.exceptionFlags
##}}}

##{{{
#RecFNToRecFN
class RecFNToRecFNIO(bundle):
    def set_var(self):
        super(RecFNToRecFNIO, self).set_var()
        self.var(inp('input', w = self.p.inExpWidth + self.p.inSigWidth + 1))
        self.var(inp('roundingMode', w = 3))
        self.var(inp('detectTininess', w = 1))
        self.var(outp('output', w = self.p.outExpWidth + self.p.outSigWidth + 1))
        self.var(outp('exceptionFlags', w = 5))

class RecFNToRecFN(module):
    def set_par(self):
        super(RecFNToRecFN, self).set_par()
        self.p.par('inExpWidth', None)
        self.p.par('inSigWidth', None)
        self.p.par('outExpWidth', None)
        self.p.par('outSigWidth', None)

    def set_port(self):
        super(RecFNToRecFN, self).set_port()
        self.io = RecFNToRecFNIO('io', p = self.p)

    def main(self):
        super(RecFNToRecFN, self).main()
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        rawIn = rawFloatFromRecFN(self.p.inExpWidth, self.p.inSigWidth, self.io.input)

        if ((self.p.inExpWidth == self.p.outExpWidth) and (self.p.inSigWidth <= self.p.outSigWidth)):

            ##--------------------------------------------------------------------
            ##--------------------------------------------------------------------
            self.io.output            /= self.io.input<<(self.p.outSigWidth - self.p.inSigWidth)
            self.io.exceptionFlags /= cat([isSigNaNRawFloat(rawIn), value(0, w = 4)])

        else:

            ##--------------------------------------------------------------------
            ##--------------------------------------------------------------------
            roundAnyRawFNToRecFN = RoundAnyRawFNToRecFN('roundAnyRawFNToRecFN', 
                inExpWidth  = self.p.inExpWidth,
                inSigWidth  = self.p.inSigWidth,
                outExpWidth = self.p.outExpWidth,
                outSigWidth = self.p.outSigWidth,
                options = consts.flRoundOpt_sigMSBitAlwaysZero()
            )
            roundAnyRawFNToRecFN.io.invalidExc     /= isSigNaNRawFloat(rawIn)
            roundAnyRawFNToRecFN.io.infiniteExc    /= 0
            roundAnyRawFNToRecFN.io.input          /= rawIn
            roundAnyRawFNToRecFN.io.roundingMode   /= self.io.roundingMode
            roundAnyRawFNToRecFN.io.detectTininess /= self.io.detectTininess
            self.io.output            /= roundAnyRawFNToRecFN.io.output
            self.io.exceptionFlags /= roundAnyRawFNToRecFN.io.exceptionFlags
##}}}

##{{{
#DivSqrtRecFN_small
#/*----------------------------------------------------------------------------
#| Computes a division or square root for floating-point in recoded form.
#| Multiple clock cycles are needed for each division or square-root operation,
#| except possibly in special cases.
#*----------------------------------------------------------------------------*/

class DivSqrtRecFNToRaw_smallIO(bundle):
    def set_var(self):
        super(DivSqrtRecFNToRaw_smallIO, self).set_var()
        #/*--------------------------------------------------------------------
        #*--------------------------------------------------------------------*/
        self.var(outp('inReady'))
        self.var(inp('inValid'))
        self.var(inp('sqrtOp'))
        self.var(inp('a', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('b', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(inp('roundingMode', w = 3))
        #/*--------------------------------------------------------------------
        #*--------------------------------------------------------------------*/
        self.var(outp('rawOutValid_div'))
        self.var(outp('rawOutValid_sqrt'))
        self.var(outp('roundingModeOut', w = 3))
        self.var(outp('invalidExc'))
        self.var(outp('infiniteExc'))
        self.var(RawFloat('rawOut', expWidth = self.p.expWidth, sigWidth = self.p.sigWidth + 2).as_output())

class DivSqrtRecFNToRaw_small(module):
    def set_par(self):
        super(DivSqrtRecFNToRaw_small, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)
        self.p.par('options', None)

    def set_port(self):
        super(DivSqrtRecFNToRaw_small, self).set_port()
        self.io = DivSqrtRecFNToRaw_smallIO('io', p = self.p)

    def main(self):
        super(DivSqrtRecFNToRaw_small, self).main()
        #/*------------------------------------------------------------------------
        #*------------------------------------------------------------------------*/
        cycleNum       = reg_r('cycleNum', w = log2_up(self.p.sigWidth + 3))

        sqrtOp_Z       = reg('sqrtOp_Z')
        majorExc_Z     = reg('majorExc_Z')
        ##*** REDUCE 3 BITS TO 2-BIT CODE:
        isNaN_Z        = reg('isNaN_Z')
        isInf_Z        = reg('isInf_Z')
        isZero_Z       = reg('isZero_Z')
        sign_Z         = reg('sign_Z')
        sExp_Z         = reg('sExp_Z', w = self.p.expWidth + 2).to_sint()
        fractB_Z       = reg('fractB_Z', w = self.p.sigWidth - 1)
        roundingMode_Z = reg('roundingMode_Z', w = 3)

        #/*------------------------------------------------------------------------
        #| (The most-significant and least-significant bits of 'rem_Z' are needed
        #| only for square roots.)
        #*------------------------------------------------------------------------*/
        rem_Z          = reg('rem_Z', w = self.p.sigWidth + 2)
        notZeroRem_Z   = reg('notZeroRem_Z')
        sigX_Z         = reg('sigX_Z', w = self.p.sigWidth + 2)

        #/*------------------------------------------------------------------------
        #*------------------------------------------------------------------------*/
        rawA_S = rawFloatFromRecFN(self.p.expWidth, self.p.sigWidth, self.io.a)
        rawB_S = rawFloatFromRecFN(self.p.expWidth, self.p.sigWidth, self.io.b)

        ##*** IMPROVE THESE:
        notSigNaNIn_invalidExc_S_div = (rawA_S.isZero & rawB_S.isZero) | (rawA_S.isInf & rawB_S.isInf)
        notSigNaNIn_invalidExc_S_sqrt = ~rawA_S.isNaN & ~rawA_S.isZero & rawA_S.sign
        majorExc_S = \
            mux(self.io.sqrtOp,
                isSigNaNRawFloat(rawA_S) | notSigNaNIn_invalidExc_S_sqrt,
                isSigNaNRawFloat(rawA_S) | isSigNaNRawFloat(rawB_S) |
                    notSigNaNIn_invalidExc_S_div |
                    (~rawA_S.isNaN & ~rawA_S.isInf & rawB_S.isZero)
            )
        isNaN_S = \
            mux(self.io.sqrtOp,
                rawA_S.isNaN | notSigNaNIn_invalidExc_S_sqrt,
                rawA_S.isNaN | rawB_S.isNaN | notSigNaNIn_invalidExc_S_div
            )
        isInf_S  = mux(self.io.sqrtOp, rawA_S.isInf,  rawA_S.isInf | rawB_S.isZero)
        isZero_S = mux(self.io.sqrtOp, rawA_S.isZero, rawA_S.isZero | rawB_S.isInf)
        sign_S = rawA_S.sign ^ (~self.io.sqrtOp & rawB_S.sign)

        specialCaseA_S = rawA_S.isNaN | rawA_S.isInf | rawA_S.isZero
        specialCaseB_S = rawB_S.isNaN | rawB_S.isInf | rawB_S.isZero
        normalCase_S_div = ~specialCaseA_S & ~specialCaseB_S
        normalCase_S_sqrt = ~specialCaseA_S & ~rawA_S.sign
        normalCase_S = mux(self.io.sqrtOp, normalCase_S_sqrt, normalCase_S_div)

        sExpQuot_S_div = rawA_S.sExp + cat([rawB_S.sExp[self.p.expWidth], ~rawB_S.sExp[self.p.expWidth - 1: 0]]).to_sint()
        ##*** IS THIS OPTIMAL?:
        sSatExpQuot_S_div = cat([mux((value(7<<(self.p.expWidth - 2), w = sExpQuot_S_div.get_w()).to_sint() <= sExpQuot_S_div),
                    value(6),
                    sExpQuot_S_div[self.p.expWidth + 1: self.p.expWidth - 2]
                ),
                sExpQuot_S_div[self.p.expWidth - 3: 0]
            ]).to_sint()

        evenSqrt_S = self.io.sqrtOp & ~rawA_S.sExp[0]
        oddSqrt_S  = self.io.sqrtOp &  rawA_S.sExp[0]

        #/*------------------------------------------------------------------------
        #*------------------------------------------------------------------------*/
        idle = (cycleNum == value(0))
        inReady = (cycleNum <= value(1))
        entering = inReady & self.io.inValid
        entering_normalCase = entering & normalCase_S

        skipCycle2 = (cycleNum == value(3)) & sigX_Z[self.p.sigWidth + 1]

        with when (~idle | self.io.inValid):
            cycleNum /= \
                mux(entering & ~normalCase_S, value(1), value(0)) | \
                mux(entering_normalCase, \
                    mux(self.io.sqrtOp, \
                        mux(rawA_S.sExp[0], value(self.p.sigWidth), value(self.p.sigWidth + 1)), \
                        value(self.p.sigWidth + 2) \
                    ), \
                    value(0) \
                ) | \
                mux(~idle & ~skipCycle2, cycleNum - value(1), value(0)) | \
                mux(~idle &   skipCycle2, value(1),            value(0))

        self.io.inReady /= inReady

        #/*------------------------------------------------------------------------
        #*------------------------------------------------------------------------*/
        with when (entering):
            sqrtOp_Z   /= self.io.sqrtOp
            majorExc_Z /= majorExc_S
            isNaN_Z    /= isNaN_S
            isInf_Z    /= isInf_S
            isZero_Z   /= isZero_S
            sign_Z     /= sign_S
        with when (entering_normalCase):
            sExp_Z /= mux(self.io.sqrtOp,
                    (rawA_S.sExp>>1) + value(1<<(self.p.expWidth - 1), w = rawA_S.sExp.get_w()).to_sint(),
                    sSatExpQuot_S_div
                )
            roundingMode_Z /= self.io.roundingMode
        with when (entering_normalCase & ~self.io.sqrtOp):
            fractB_Z /= rawB_S.sig[self.p.sigWidth - 2: 0]

        #/*------------------------------------------------------------------------
        #*------------------------------------------------------------------------*/
        rem = \
            mux(inReady & ~oddSqrt_S, rawA_S.sig<<1, value(0)) | \
            mux(inReady & oddSqrt_S, \
                cat([rawA_S.sig[self.p.sigWidth - 1: self.p.sigWidth - 2] - value(1), \
                    rawA_S.sig[self.p.sigWidth - 3: 0]<<3 \
                ]), \
                value(0) \
            ) | \
            mux(~inReady, rem_Z<<1, value(0))
        bitMask = (value(1).to_bits()<<cycleNum)>>2
        trialTerm = \
            mux(inReady & ~self.io.sqrtOp, rawB_S.sig<<1, value(0)) | \
            mux(inReady & evenSqrt_S,  value(1<<self.p.sigWidth), value(0)) | \
            mux(inReady & oddSqrt_S,   value(5<<(self.p.sigWidth - 1)), value(0)) | \
            mux(~inReady & ~sqrtOp_Z, cat([value(1, w = 1), fractB_Z])<<1, value(0)) | \
            mux(~inReady & sqrtOp_Z, sigX_Z<<1 | bitMask, value(0))
        trialRem = rem.z_ext() - trialTerm.z_ext()
        newBit = (value(0, w = trialRem.get_w()).to_sint() <= trialRem)

        with when (entering_normalCase | (cycleNum > value(2))):
            rem_Z /= mux(newBit, trialRem.as_uint(), rem)
        with when (entering_normalCase | (~inReady & newBit)):
            notZeroRem_Z /= (trialRem != value(0, w = trialRem.get_w()).to_sint())
            sigX_Z /= \
                mux(inReady & ~self.io.sqrtOp, newBit<<(self.p.sigWidth + 1), value(0)) | \
                mux(inReady &  self.io.sqrtOp, value(1<<self.p.sigWidth), value(0)) | \
                mux(inReady & oddSqrt_S, newBit<<(self.p.sigWidth - 1),    value(0)) | \
                mux(~inReady, sigX_Z | bitMask, value(0))

        #/*------------------------------------------------------------------------
        #*------------------------------------------------------------------------*/
        rawOutValid = (cycleNum == value(1))

        self.io.rawOutValid_div  /= rawOutValid & ~sqrtOp_Z
        self.io.rawOutValid_sqrt /= rawOutValid &  sqrtOp_Z
        self.io.roundingModeOut  /= roundingMode_Z
        self.io.invalidExc    /= majorExc_Z & isNaN_Z
        self.io.infiniteExc   /= majorExc_Z & ~isNaN_Z
        self.io.rawOut.isNaN  /= isNaN_Z
        self.io.rawOut.isInf  /= isInf_Z
        self.io.rawOut.isZero /= isZero_Z
        self.io.rawOut.sign   /= sign_Z
        self.io.rawOut.sExp   /= sExp_Z
        self.io.rawOut.sig    /= sigX_Z<<1 | notZeroRem_Z

class DivSqrtRecFN_small_req(bundle):
    def set_var(self):
        super(DivSqrtRecFN_small_req, self).set_var()
        self.var(bits('sqrtOp'))
        self.var(bits('a', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(bits('b', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(bits('roundingMode', w = 3))
        self.var(bits('detectTininess', w = 1))

class DivSqrtRecFN_small_resp(bundle):
    def set_var(self):
        super(DivSqrtRecFN_small_resp, self).set_var()
        self.var(bits('div'))
        self.var(bits('sqrt'))
        self.var(bits('data', w = self.p.expWidth + self.p.sigWidth + 1))
        self.var(bits('exceptionFlags', w = 5))

class DivSqrtRecFN_smallIO(bundle):
    def set_var(self):
        super(DivSqrtRecFN_smallIO, self).set_var()
        self.var(ready_valid('input', gen = DivSqrtRecFN_small_req, p = self.p).flip())
        self.var(valid('output', gen = DivSqrtRecFN_small_resp, p = self.p))

class DivSqrtRecFN_small(module):
    def set_par(self):
        super(DivSqrtRecFN_small, self).set_par()
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)
        self.p.par('options', None)

    def set_port(self):
        super(DivSqrtRecFN_small, self).set_port()
        self.io = DivSqrtRecFN_smallIO('io', p = self.p)

    def main(self):
        super(DivSqrtRecFN_small, self).main()
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        divSqrtRecFNToRaw = DivSqrtRecFNToRaw_small('divSqrtRecFNToRaw', expWidth = self.p.expWidth, sigWidth = self.p.sigWidth, options = self.p.options)

        self.io.input.ready /= divSqrtRecFNToRaw.io.inReady
        divSqrtRecFNToRaw.io.inValid      /= self.io.input.valid
        divSqrtRecFNToRaw.io.sqrtOp       /= self.io.input.bits.sqrtOp
        divSqrtRecFNToRaw.io.a            /= self.io.input.bits.a
        divSqrtRecFNToRaw.io.b            /= self.io.input.bits.b
        divSqrtRecFNToRaw.io.roundingMode /= self.io.input.bits.roundingMode

        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        self.io.output.valid /= divSqrtRecFNToRaw.io.rawOutValid_div | divSqrtRecFNToRaw.io.rawOutValid_sqrt
        self.io.output.bits.div  /= divSqrtRecFNToRaw.io.rawOutValid_div
        self.io.output.bits.sqrt /= divSqrtRecFNToRaw.io.rawOutValid_sqrt

        roundRawFNToRecFN = RoundRawFNToRecFN('roundRawFNToRecFN', expWidth = self.p.expWidth, sigWidth = self.p.sigWidth, options = 0)
        roundRawFNToRecFN.io.invalidExc   /= divSqrtRecFNToRaw.io.invalidExc
        roundRawFNToRecFN.io.infiniteExc  /= divSqrtRecFNToRaw.io.infiniteExc
        roundRawFNToRecFN.io.input        /= divSqrtRecFNToRaw.io.rawOut
        roundRawFNToRecFN.io.roundingMode /= divSqrtRecFNToRaw.io.roundingModeOut
        roundRawFNToRecFN.io.detectTininess /= self.io.input.bits.detectTininess
        self.io.output.bits.data /= roundRawFNToRecFN.io.output
        self.io.output.bits.exceptionFlags /= roundRawFNToRecFN.io.exceptionFlags

##}}}
