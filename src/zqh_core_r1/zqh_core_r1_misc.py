import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_misc import D_CONSTS

class zqh_core_r1_event_set(object):
    def __init__(self, gate, events):
        self.gate = gate
        self.events = events

    def size(self):
        return len(self.events)

    def hits(self):
        return cat_rvs(list(map(lambda x: x[1](), self.events)))
    def check(self, mask):
        return self.gate(mask, self.hits())
    def dump(self):
        for ((name, _), i) in list(zip(self.events, range(len(self.events)))):
            with when (self.check(value(1 << i, w = len(self.events)).to_bits())):
                vprintln("Event %s" % name)

class zqh_core_r1_event_sets(object):
    def __init__(self, eventSets):
        self.eventSets = eventSets
        self.eventSetIdBits = 8

    def maskEventSelector(self, eventSel):
        ## allow full associativity between counters and event sets (for now?)
        setMask = (1 << log2_ceil(len(self.eventSets))) - 1
        maskMask = (
            ((1 << max(list(map(lambda x: x.size(), self.eventSets)))) - 1) << 
            self.eventSetIdBits)
        return eventSel & value(setMask | maskMask, w = eventSel.get_w())

    def decode(self, counter):
        assert(len(self.eventSets) <= (1 << self.eventSetIdBits))
        return (counter[log2_ceil(len(self.eventSets))-1: 0], counter >> self.eventSetIdBits)

    def evaluate(self, eventSel):
        (set, mask) = self.decode(eventSel)
        sets = list(map(lambda x: x.check(mask), self.eventSets))
        return sel_bin(set,sets)
