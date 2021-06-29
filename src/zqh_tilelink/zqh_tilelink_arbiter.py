#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/tilelink/Arbiter.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *

class zqh_tl_arbiter(object):
    @classmethod
    def lowestIndexFirst(self, width, valids, select): 
        return ~(valids.lsb_or() << 1)[width-1: 0]

    @classmethod
    def roundRobin(self, width, valids, select):
        if (width == 1):
            return value(1, w=1).to_bits()
        else:
            valid = valids[width-1: 0]
            mask = reg_s(w = width)
            filter = cat([valid & ~mask, valid])
            unready = (filter.msb_or(cap =  width) >> 1) | (mask << width)
            readys = ~((unready >> width) & unready[width-1: 0])
            with when (select & valid.r_or()):
                mask /= (readys & valid).lsb_or()
            return readys[width-1: 0]

    @classmethod
    def apply(self, policy, sink, sources):
        if (len(sources) == 0):
            sink.valid /= 0
        elif (len(sources) == 1):
            sink.valid /= sources[0][1].valid
            sink.bits /= sources[0][1].bits
            sources[0][1].ready /= sink.ready
        else:
            pairs = sources
            beatsIn = list(map(lambda _: _[0], pairs))
            sourcesIn = list(map(lambda _: _[1], pairs))

            ## The number of beats which remain to be sent
            beatsLeft = reg_r(w = max(list(map(lambda _: _.get_w(), beatsIn))))
            idle = beatsLeft == 0
            latch = idle & sink.ready ## winner (if any) claims sink

            ## Who wants access to the sink?
            valids = list(map(lambda _: _.valid, sourcesIn))
            ## Arbitrate amongst the requests
            readys = policy(len(valids), cat_rvs(valids), latch).grouped()
            ## Which request wins arbitration?
            winner = list(map(lambda _: _[0] & _[1], list(zip(readys, valids))))

            ## Confirm the policy works properly
            assert(len(readys) == len(valids))
            ## Never two winners
            prefixOR = scan_left(lambda x,y: x | y, winner, value(0).to_bits())[:-1]
            vassert(reduce(
                lambda x,y: x & y, 
                list(map(
                    lambda _: ~_[0] | ~_[1],
                    list(zip(prefixOR, winner))))))
            ## If there was any request, there is a winner
            vassert(~reduce(lambda x,y: x | y, valids) | reduce(lambda x,y: x | y, winner))

            ## Track remaining beats
            maskedBeats = list(map(
                lambda _: mux(_[0], _[1], 0),
                list(zip(winner, beatsIn))))
            initBeats = reduce(lambda a,b: a | b, maskedBeats) ## no winner => 0 beats
            beatsLeft /= mux(latch, initBeats, beatsLeft - sink.fire())

            ## The one-hot source granted access in the previous cycle
            state = reg_r(w = len(sources))
            muxState = mux(idle, cat_rvs(winner), state)
            state /= muxState

            if (len(sources) > 1):
                allowed = mux(idle, cat_rvs(readys), state)
                for (s, r) in list(zip(sourcesIn, allowed.grouped())):
                    s.ready /= sink.ready & r
            else:
                sourcesIn[0].ready /= sink.ready

            sink.valid /= mux(
                idle,
                reduce(lambda a,b: a | b, valids),
                sel_oh(state, valids))
            sink.bits /= sel_oh(muxState, list(map(lambda _: _.bits, sourcesIn)))
