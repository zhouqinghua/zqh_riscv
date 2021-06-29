#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/tilelink/Bundles.scala:TLMessages, TLPermissions, TLAtomics, TLHints
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *

class zqh_tl_messages(object):
    @classmethod
    def put_full_data    (self):
        return value(0)
    @classmethod
    def put_partial_data (self):
        return value(1)
    @classmethod
    def arithmetic_data (self):
        return value(2)
    @classmethod
    def logical_data    (self):
        return value(3)
    @classmethod
    def get            (self):
        return value(4)
    @classmethod
    def hint           (self):
        return value(5)
    @classmethod
    def acquire_block   (self):
        return value(6)
    @classmethod
    def acquire_perm    (self):
        return value(7)
    @classmethod
    def probe          (self):
        return value(6)
    @classmethod
    def access_ack      (self):
        return value(0)
    @classmethod
    def access_ack_data  (self):
        return value(1)
    @classmethod
    def hint_ack        (self):
        return value(2)
    @classmethod
    def probe_ack       (self):
        return value(4)
    @classmethod
    def probe_ack_data   (self):
        return value(5)
    @classmethod
    def release        (self):
        return value(6)
    @classmethod
    def release_data    (self):
        return value(7)
    @classmethod
    def grant          (self):
        return value(4)
    @classmethod
    def grant_data      (self):
        return value(5)
    @classmethod
    def release_ack     (self):
        return value(6)
    @classmethod
    def grant_ack       (self):
        return value(0)
 
    @classmethod
    def is_a(self, x):
        return x <= self.acquire_perm()
    @classmethod
    def is_b(self, x):
        return x <= self.probe()
    @classmethod
    def is_c(self, x):
        return x <= self.release_data()
    @classmethod
    def is_d(self, x):
        return x <= self.release_ack()

    @classmethod
    def ad_response(self):
        return [
            self.access_ack(), self.access_ack(), self.access_ack_data(), 
            self.access_ack_data(), self.access_ack_data(), self.hint_ack(), 
            self.grant(), self.grant()]
    @classmethod
    def bc_response(self):
        return [
            self.access_ack(), self.access_ack(), self.access_ack_data(), 
            self.access_ack_data(), self.access_ack_data(), self.hint_ack(), 
            self.probe_ack(), self.probe_ack()]
TMSG_CONSTS = zqh_tl_messages()

class zqh_tl_permissions(object):
    a_width = 2
    bd_width = 2
    c_width = 3

    @classmethod
    def to_t(self):
        return value(0, self.bdWidth)
    @classmethod
    def to_b(self):
        return value(1, self.bdWidth)
    @classmethod
    def to_n(self):
        return value(2, self.bdWidth)
    @classmethod
    def is_cap(self, x):
        return x <= self.toN()

    @classmethod
    def n_to_b(self):
        return value(0, self.aWidth)
    @classmethod
    def n_to_t(self):
        return value(1, self.aWidth)
    @classmethod
    def b_to_t(self):
        return value(2, self.aWidth)
    @classmethod
    def is_grow(self, x):
        return x <= self.BtoT()

    @classmethod
    def t_to_b(self):
        return value(0, self.cWidth)
    @classmethod
    def t_to_n(self):
        return value(1, self.cWidth)
    @classmethod
    def b_to_n(self):
        return value(2, self.cWidth)
    @classmethod
    def is_shrink(self, x):
        return x <= self.BtoN()

    @classmethod
    def t_to_t(self):
        return value(3, self.cWidth)
    @classmethod
    def b_to_b(self):
        return value(4, self.cWidth)
    @classmethod
    def n_to_n(self):
        return value(5, self.cWidth)
    @classmethod
    def is_report(self, x):
        return x <= self.NtoN()
TPM_CONSTS = zqh_tl_permissions()

class zqh_tl_atomics(object):
    width = 3

    @classmethod
    def min(self):
        return value(0, self.width)
    @classmethod
    def max(self):
        return value(1, self.width)
    @classmethod
    def minu(self):
        return value(2, self.width)
    @classmethod
    def maxu(self):
        return value(3, self.width)
    @classmethod
    def add(self):
        return value(4, self.width)
    @classmethod
    def is_arithmetic(self, x):
        return x <= self.ADD()

    @classmethod
    def xor(self):
        return value(0, self.width)
    @classmethod
    def orr(self):
        return value(1, self.width)
    @classmethod
    def andd(self):
        return value(2, self.width)
    @classmethod
    def swap(self):
        return value(3, self.width)
    @classmethod
    def is_logical(self, x):
        return x <= self.SWAP()
TAMO_CONSTS = zqh_tl_atomics()

class zqh_tl_hints(object):
    width = 1

    @classmethod
    def prefetch_read(self):
        return value(0, self.width)
    @classmethod
    def prefetch_write(self):
        return value(1, self.width)
THT_CONSTS = zqh_tl_hints()
