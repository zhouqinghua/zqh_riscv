#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/devices/tilelink/Plic.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *

class zqh_plic_consts(object):

    maxDevices = 1023
    maxHarts = 15872
    priorityBase = 0x0
    pendingBase = 0x1000
    claimOffset  = 4
    priorityBytes = 4

    @classmethod
    def enableOffset(self, i):
        return i * ((zqh_plic_consts.maxDevices+7)//8)

    @classmethod
    def hartOffset(self, i):
        return i * 0x1000

    @classmethod
    def enableBase(self, i = 0):
        return self.enableOffset(i) + 0x2000

    @classmethod
    def hartBase(self, i = 0):
        return self.hartOffset(i) + 0x200000

    @classmethod
    def size(self):
        return 2**log2_ceil(self.hartBase(zqh_plic_consts.maxHarts))
