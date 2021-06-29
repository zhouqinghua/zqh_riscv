import sys
import os
from phgl_imp import *

class zqh_address_attr(object):
    MEM_RWAX_C_S  = 0 #memory: read, write, atomic, execute, cacheable, snoopable
    MEM_RWAX_C_US = 1 #memory: read, write, atomic, execute, cacheable, unsnoopable
    MEM_RX_C_US   = 2 #memory: read, execute, cacheable, unsnoopable
    MEM_RWAX_UC   = 3 #memory: read, write, atomic, execute, uncacheable
    DEV_RWAX      = 4 #device: read, write, atomic, execute
    DEV_RWA       = 5 #device: read, write, atomic, unexecute

class zqh_order_type(object):
    SO  = 0 #strong order
    RO  = 1 #out of ouder except same address

class zqh_address_space(parameter):
    def set_par(self):
        super(zqh_address_space, self).set_par()
        self.par('base', 0)
        self.par('mask', 0)
        self.par('attr', zqh_address_attr.DEV_RWAX)
        self.par('order_type', zqh_order_type.SO)

    def cacheable(self):
        return self.attr in (zqh_address_attr.MEM_RWAX_C_S, zqh_address_attr.MEM_RWAX_C_US, zqh_address_attr.MEM_RX_C_US)

    def contains(self, x):
        if isinstance(x, (int)):
            return ((x ^ self.base) & ~self.mask) == 0
        elif isinstance(x, bits):
            return ((x ^ value(self.base, w = x.get_w())) & ~value(self.mask, w = x.get_w())) == value(0, w = x.get_w())
        elif isinstance(x, zqh_address_space):
            return ((x.mask | (self.base ^ x.base)) & ~self.mask) == 0
        else:
            assert(0)

    def print_info(self):
        info =        'base = 0x%08x\n' % (self.base)
        info = info + 'mask = 0x%08x\n' % (self.mask)
        info = info + 'attr = %d\n' % (self.attr)
        info = info + 'order_type = %d' % (self.order_type)
        return info
