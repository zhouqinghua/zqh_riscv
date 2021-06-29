#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/tile/FPU.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_core_parameters import zqh_core_common_core_parameter
from .zqh_fpu_misc import *
from zqh_hardfloat.hardfloat import recFNFromFN
from zqh_hardfloat.hardfloat import fNFromRecFN

class zqh_f_type(parameter):
    def set_par(self):
        super(zqh_f_type, self)
        self.par('exp', None)
        self.par('sig', None)
    
    @classmethod
    def S(self):
        return zqh_f_type(exp = 8, sig = 24)

    @classmethod
    def D(self):
        return zqh_f_type(exp = 11, sig = 53)
  
    @classmethod
    def all(self):
        return [self.S(), self.D()]

    def ieeeWidth(self):
        return self.exp + self.sig
    def recodedWidth(self):
        return self.ieeeWidth() + 1
  
    def qNaN(self):
        return value(
            (7 << (self.exp + self.sig - 3)) + (1 << (self.sig - 2)),
            self.exp + self.sig + 1)
    def isNaN(self, x):
        return x[self.sig + self.exp - 1: self.sig + self.exp - 3].r_and()
    def isSNaN(self, x):
        return self.isNaN(x) & ~x[self.sig - 2]
  
    def classify(self, x):
        sign = x[self.sig + self.exp]
        code = x[self.exp + self.sig - 1: self.exp + self.sig - 3]
        codeHi = code[2: 1]
        isSpecial = codeHi == 3
  
        isHighSubnormalIn = x[self.exp + self.sig - 3: self.sig - 1] < 2
        isSubnormal = (code == 1) | ((codeHi == 1) & isHighSubnormalIn)
        isNormal = ((codeHi == 1) & ~isHighSubnormalIn) | (codeHi == 2)
        isZero = code == 0
        isInf = isSpecial & ~code[0]
        isNaN = code.r_and()
        isSNaN = isNaN & ~x[self.sig-2]
        isQNaN = isNaN & x[self.sig-2]
  
        return cat([isQNaN, isSNaN, isInf & ~sign, isNormal & ~sign,
            isSubnormal & ~sign, isZero & ~sign, isZero & sign,
            isSubnormal & sign, isNormal & sign, isInf & sign])
  
    ## convert between formats, ignoring rounding, range, NaN
    def unsafeConvert(self, x, to):
        if (self.exp == to.exp and self.sig == to.sig):
            return x
        else:
            sign = x[self.sig + self.exp]
            fractIn = x[self.sig - 2: 0]
            expIn = x[self.sig + self.exp - 1: self.sig - 1]
            fractOut = fractIn << to.sig >> self.sig
            expCode = expIn[self.exp: self.exp - 2]
            commonCase = (expIn + (1 << to.exp)) - (1 << self.exp)
            expOut = mux(
                (expCode == 0) | (expCode >= 6),
                cat([expCode, commonCase[to.exp - 3: 0]]),
                commonCase[to.exp: 0])
            return cat([sign, expOut, fractOut])
  
    def recode(self, x):
        return recFNFromFN(self.exp, self.sig, x)
    def ieee(self, x):
        return fNFromRecFN(self.exp, self.sig, x)

class zqh_fpu_parameter(zqh_core_common_core_parameter):
    def set_par(self):
        super(zqh_fpu_parameter, self).set_par()
        self.par('divSqrt', True)
        self.par('sfmaLatency', 3)
        self.par('dfmaLatency', 4)
        self.par('minXLen', 32)

    def check_par(self):
        super(zqh_fpu_parameter, self).check_par()
        assert(self.flen == 32 or self.flen == 64)
        self.par(
            'floatTypes', list(filter(
                lambda _: _.ieeeWidth() <= self.flen,
                zqh_f_type.all())))
        self.par('minType', self.floatTypes[0])
        self.par('maxType', self.floatTypes[-1])
        self.par('maxExpWidth', self.maxType.exp)
        self.par('maxSigWidth', self.maxType.sig)

    def nIntTypes(self):
        return log2_ceil(int(self.xlen/self.minXLen)) + 1
    def prevType(self, t):
        return self.floatTypes[self.typeTag(t) - 1]
    def typeTag(self, t):
        return self.floatTypes.index(t)
  
    def isBox(self, x, t):
        return x[t.sig + t.exp: t.sig + t.exp - 4].r_and()
  
    def box0(self, x, xt, y, yt):
        assert(xt.ieeeWidth() == 2 * yt.ieeeWidth())
        swizzledNaN = cat([
            x[xt.sig + xt.exp: xt.sig + xt.exp - 3],
            x[xt.sig - 2: yt.recodedWidth() - 1].r_and(),
            x[xt.sig + xt.exp - 5: xt.sig],
            y[yt.recodedWidth() - 2],
            x[xt.sig - 2: yt.recodedWidth() - 1],
            y[yt.recodedWidth() - 1],
            y[yt.recodedWidth() - 3: 0]])
        return mux(xt.isNaN(x), swizzledNaN, x)
  
    ## implement NaN unboxing for FU inputs
    def unbox(self, x, tag, exactType):
        outType = exactType if (exactType is not None) else self.maxType
        def helper(x, t):
            if (t == self.minType):
                prev = []
            else:
                prevT = self.prevType(t)
                unswizzled = cat([
                    x[prevT.sig + prevT.exp - 1],
                    x[t.sig - 1],
                    x[prevT.sig + prevT.exp - 2: 0]])
                prev_t = helper(unswizzled, prevT)
                isbox = self.isBox(x, t)
                prev_t = list(map(lambda p: (isbox & p[0], p[1]), prev_t))
                prev = prev_t
            prev = prev + [(value(1), t.unsafeConvert(x, outType))]
            return prev
  
        [oks, floats] = list(zip(*helper(x, self.maxType)))
        #print(helper(x, self.maxType))
        #print(list(zip(*helper(x, self.maxType))))
        #tmp assert(len(oks) > 1)
        #tmp assert(len(floats) > 1)
        if (exactType is None or len(self.floatTypes) == 1):
            return mux(sel_bin(tag, oks), sel_bin(tag, floats), self.maxType.qNaN())
        else:
            t = exactType
            return floats[self.typeTag(t)] | mux(oks[self.typeTag(t)], 0, t.qNaN())
  
    ## make sure that the redundant bits in the NaN-boxed encoding are consistent
    def consistent(self, x):
        def helper(x, t): 
            if (self.typeTag(t) == 0):
                return value(1)
            else:
              prevT = self.prevType(t)
              unswizzled = cat([
                  x[prevT.sig + prevT.exp - 1],
                  x[t.sig - 1],
                  x[prevT.sig + prevT.exp - 2: 0]])
              prevOK = ~self.isBox(x, t) | helper(unswizzled, prevT)
              curOK = (
                    ~t.isNaN(x) | 
                    (x[t.sig + t.exp - 4] == x[t.sig - 2: prevT.recodedWidth() - 1].r_and()))
              return prevOK & curOK
        return helper(x, self.maxType)
  
    ## generate a NaN box from an FU result
    def box1(self, x, t):
        if (t == self.maxType):
            return x
        else:
            nt = self.floatTypes[self.typeTag(t) + 1]
            bigger = self.box0(value((1 << nt.recodedWidth())-1).to_bits(), nt, x, t)
            return bigger | ((1 << self.maxType.recodedWidth()) - (1 << nt.recodedWidth()))
  
    ## generate a NaN box from an FU result
    def box2(self, x, tag):
        opts = list(map(lambda t: self.box1(x, t), self.floatTypes))
        return sel_bin(tag, opts)
  
    ## zap bits that hardfloat thinks are don't-cares, but we do care about
    def sanitizeNaN(self, x, t):
        if (self.typeTag(t) == 0):
            return x
        else:
            maskedNaN = (
                x & 
                ~value(
                    (1 << (t.sig-1)) | (1 << (t.sig+t.exp-4)),
                    w = t.recodedWidth()).to_bits())
            return mux(t.isNaN(x), maskedNaN, x)
  
    ## implement NaN boxing and recoding for FL*/fmv.*.x
    def recode(self, x, tag):
        def helper(x, t):
            if (self.typeTag(t) == 0):
                return t.recode(x)
            else:
                prevT = self.prevType(t)
                return self.box0(t.recode(x), t, helper(x, prevT), prevT)
  
        ## fill MSBs of subword loads to emulate a wider load of a NaN-boxed value
        boxes = list(map(
            lambda t: value((1 << self.maxType.ieeeWidth()) - (1 << t.ieeeWidth())),
            self.floatTypes))
        return helper(sel_bin(tag, boxes) | x, self.maxType)
  
    ## implement NaN unboxing and un-recoding for FS*/fmv.x.*
    def ieee(self, x, t = None):
        if (t is None):
            t = self.maxType
        if (self.typeTag(t) == 0):
            return t.ieee(x)
        else:
            unrecoded = t.ieee(x)
            prevT = self.prevType(t)
            prevRecoded = cat([
                x[prevT.recodedWidth()-2],
                x[t.sig-1],
                x[prevT.recodedWidth()-3: 0]])
            prevUnrecoded = self.ieee(prevRecoded, prevT)
            return cat([
                unrecoded >> prevT.ieeeWidth(),
                mux(t.isNaN(x), prevUnrecoded, unrecoded[prevT.ieeeWidth()-1: 0])])
