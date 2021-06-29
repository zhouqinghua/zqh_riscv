#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/tilelink/Edges.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from .zqh_tilelink_parameters import zqh_tl_interface_parameter
from .zqh_tilelink_bundles import zqh_tl_bundle_a
from .zqh_tilelink_bundles import zqh_tl_bundle_b
from .zqh_tilelink_bundles import zqh_tl_bundle_c
from .zqh_tilelink_bundles import zqh_tl_bundle_d
from .zqh_tilelink_bundles import zqh_tl_bundle_e
from .zqh_tilelink_misc import TMSG_CONSTS
from .zqh_tilelink_parameters import zqh_tl_manager_port_parameter

class zqh_tl_interface_base(zqh_tl_interface_parameter):
    def set_par(self):
        super(zqh_tl_interface_base, self).set_par()
        self.par('slave_nodes', [])

    def check_par(self):
        super(zqh_tl_interface_base, self).check_par()
        self.manager = zqh_tl_manager_port_parameter(
            'manager',
            slave_nodes = self.slave_nodes)

    def mask(self, address, lgSize):
        return mask_gen(address, lgSize, self.manager.beat_bytes)

    def has_data(self, x):
        tp = type(x)
        if (tp is zqh_tl_bundle_a):
            opdata = ~x.opcode[2]
        elif (tp is zqh_tl_bundle_b):
            opdata = ~x.opcode[2]
        elif (tp is zqh_tl_bundle_c):
            opdata = x.opcode[0]
        elif (tp is zqh_tl_bundle_d):
            opdata = x.opcode[0]
        elif (tp is zqh_tl_bundle_e):
            opdata = value(0)

        return opdata

    def num_beats(self, x):
        tp = type(x)
        if (tp is zqh_tl_bundle_e):
            return value(0).to_bits()
        else:
            if (self.max_size_bits() == 0):
                return 0
            else:
                decode = bin2lsb1(
                    x.size,
                    self.max_size_bits()) >> log2_ceil(self.manager.beat_bytes)
                return mux(self.has_data(x), decode, 0)

    def first_last_helper(self, bits, fire):
        beats1   = self.num_beats(bits)
        counter  = reg_r(
            w = log2_up(self.manager.max_transfer() // self.manager.beat_bytes))
        counter1 = counter - 1
        first = counter == 0
        last  = (counter == 1) | (beats1 == 0)
        done  = last & fire
        count = (beats1 & ~counter1)
        with when (fire):
            counter /= mux(first, beats1, counter1)
        return (first, last, done, count)

    def done(self, x, fire = None): 
        if (fire is None):
            tmp_bits = x.bits
            tmp_fire = x.fire()
        else:
            tmp_bits = x
            tmp_fire = fire
        return self.first_last_helper(tmp_bits, tmp_fire)[2]

    def count(self, x, fire = None):
        if (fire is None):
            tmp_bits = x.bits
            tmp_fire = x.fire()
        else:
            tmp_bits = x
            tmp_fire = fire

        r = self.first_last_helper(tmp_bits, tmp_fire)
        return (r[0], r[1], r[2], r[3])

    def addr_inc(self, x, fire = None):
        if (fire is None):
            tmp_bits = x.bits
            tmp_fire = x.fire()
        else:
            tmp_bits = x
            tmp_fire = fire
        r = self.first_last_helper(tmp_bits, tmp_fire)
        return (r[0], r[1], r[2], r[3] << log2_ceil(self.manager.beat_bytes))

class zqh_tl_interface_out(zqh_tl_interface_base):
    def acquire_block(self, fromSource, toAddress, lgSize, growPermissions):
        legal = 1
        a = zqh_tl_bundle_a(p = self.bundle.channel['a'])
        a.opcode  /= TMSG_CONSTS.acquire_block()
        a.param   /= growPermissions
        a.size    /= lgSize
        a.source  /= fromSource
        a.address /= toAddress
        a.mask    /= self.mask(toAddress, lgSize)
        a.data    /= value(0)
        return (legal, a)

    def release(
        self, fromSource, toAddress, lgSize, 
        shrinkPermissions, data = None, error = None):
        legal = 1
        c = zqh_tl_bundle_c(p = self.bundle.channel['c'])
        c.opcode  /= TMSG_CONSTS.release() if (data is None) else TMSG_CONSTS.release_Data()
        c.param   /= shrinkPermissions
        c.size    /= lgSize
        c.source  /= fromSource
        c.address /= toAddress
        c.data    /= value(0) if (data is None) else data
        c.error /= 0 if (error is None) else error
        return (legal, c)

    def probe_ack(self, b, reportPermissions, data = None):
        return self.probe_ack_do(b.source, b.address, b.size, reportPermissions, data, 0)

    def probe_ack_do(
        self, fromSource, toAddress, lgSize, 
        reportPermissions, data = None, erro = None):
        c = zqh_tl_bundle_c(p = self.bundle.channel['c'])
        c.opcode  /= (
            TMSG_CONSTS.probe_ack() if (data is None) else TMSG_CONSTS.probe_ack_data())
        c.param   /= reportPermissions
        c.size    /= lgSize
        c.source  /= fromSource
        c.address /= toAddress
        c.data    /= value(0) if (data is None) else data
        c.error /= 0 if (error is None) else error 
        return c

    def grant_ack(self, d):
        if isinstance(d, zqh_tl_bundle_d):
            toSink = d.sink
        else:
            toSink = d

        e = zqh_tl_bundle_e(p = self.bundle.channel['e'])
        e.sink /= toSink
        return e

    def get(self, fromSource, toAddress, lgSize):
        legal = 1
        a = zqh_tl_bundle_a(p = self.bundle.channel['a'])
        a.opcode  /= TMSG_CONSTS.get()
        a.param   /= value(0)
        a.size    /= lgSize
        a.source  /= fromSource
        a.address /= toAddress
        a.mask    /= self.mask(toAddress, lgSize)
        a.data    /= value(0)
        return (legal, a)

    def put(self, fromSource, toAddress, lgSize, data, mask = None, error = 0):
        legal = 1
        a = zqh_tl_bundle_a(p = self.bundle.channel['a'])
        if (mask is None):
            a.opcode  /= TMSG_CONSTS.put_full_data()
        else:
            a.opcode  /= TMSG_CONSTS.put_partial_data()
        a.param   /= value(0)
        a.size    /= lgSize
        a.source  /= fromSource
        a.address /= toAddress
        if (mask is None):
            a.mask    /= self.mask(toAddress, lgSize)
        else:
            a.mask    /= mask
        a.data    /= data
        return (legal, a)

    def arithmetic(self, fromSource, toAddress, lgSize, data, atomic, error = 0):
        legal = 1
        a = zqh_tl_bundle_a(p = self.bundle.channel['a'])
        a.opcode  /= TMSG_CONSTS.arithmetic_data()
        a.param   /= atomic
        a.size    /= lgSize
        a.source  /= fromSource
        a.address /= toAddress
        a.mask    /= self.mask(toAddress, lgSize)
        a.data    /= data
        return (legal, a)

    def logical(self, fromSource, toAddress, lgSize, data, atomic, error = 0):
        legal = 1
        a = zqh_tl_bundle_a(p = self.bundle.channel['a'])
        a.opcode  /= TMSG_CONSTS.logical_data()
        a.param   /= atomic
        a.size    /= lgSize
        a.source  /= fromSource
        a.address /= toAddress
        a.mask    /= self.mask(toAddress, lgSize)
        a.data    /= data
        return (legal, a)

    def hint(self, fromSource, toAddress, lgSize, param):
        legal = 1
        a = zqh_tl_bundle_a(p = self.bundle.channel['a'])
        a.opcode  /= TMSG_CONSTS.hint()
        a.param   /= param
        a.size    /= lgSize
        a.source  /= fromSource
        a.address /= toAddress
        a.mask    /= self.mask(toAddress, lgSize)
        a.data    /= value(0)
        return (legal, a)

class zqh_tl_interface_in(zqh_tl_interface_base):

    def probe(self, fromAddress, toSource, lgSize, capPermissions):
      legal = 1
      b = zqh_tl_bundle_b(p = self.bundle.channel['b'])
      b.opcode  /= TMSG_CONSTS.probe()
      b.param   /= capPermissions
      b.size    /= lgSize
      b.source  /= toSource
      b.address /= fromAddress
      b.mask    /= self.mask(fromAddress, lgSize)
      b.data    /= 0
      return (legal, b)

    def release_ack(self, toSource, lgSize):
        d = zqh_tl_bundle_d(p = self.bundle.channel['d'])
        d.opcode  /= TMSG_CONSTS.release_ack()
        d.param   /= 0
        d.size    /= lgSize
        d.source  /= toSource
        d.sink    /= 0
        d.data    /= 0
        d.error /= 0
        return d

    def access_ack_a(self, a):
        return self.access_ack(a.source, a.size)
    def access_ack(self, toSource, lgSize):
        d = zqh_tl_bundle_d(p = self.bundle.channel['d'])
        d.opcode  /= TMSG_CONSTS.access_ack()
        d.param   /= 0
        d.size    /= lgSize
        d.source  /= toSource
        d.sink    /= 0
        d.data    /= 0
        d.error /= 0
        return d

    def access_ack_data_a(self, a, data, error = 0):
        return self.access_ack_data(a.source, a.size, data, error)
    def access_ack_data(self, toSource, lgSize, data, error = 0):
        d = zqh_tl_bundle_d(p = self.bundle.channel['d'])
        d.opcode  /= TMSG_CONSTS.access_ack_data()
        d.param   /= 0
        d.size    /= lgSize
        d.source  /= toSource
        d.sink    /= 0
        d.data    /= data
        d.error /= error
        return d
