import sys
import os
from phgl_imp import *
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/util/Replacement.scala
#re-write by python and do some modifications

class zqh_replacement_policy(bundle):
    def set_par(self):
        super(zqh_replacement_policy, self).set_par()
        self.p.par('ways', None)

    def way(self):
        return None
    def miss(self):
        return None
    def hit(self):
        return None

class zqh_random_replacement(zqh_replacement_policy):
    def set_var(self):
        super(zqh_random_replacement, self).set_var()
        self.var(bits('replace', init = 0))
        self.var(bits('lfsr', w = 16, init = lfsr16(increment = self.replace)))

    def way(self):
        if(self.p.ways == 1):
            return value(0)
        else:
            return self.lfsr[log2_up(self.p.ways)-1:0]
    def miss(self):
        self.replace /= 1
    def hit(self):
        pass

class zqh_pseudo_lru(bundle):
    def set_par(self):
        super(zqh_pseudo_lru, self).set_par()
        self.p.par('n', None)

    def set_var(self):
        super(zqh_pseudo_lru,self).set_var()
        self.var(reg_r('state_reg', w = self.p.n-1))

    def access(self, way):
        self.state_reg /= self.get_next_state(self.state_reg,way)

    def get_next_state(self, state, way):
        next_state = state << 1
        idx = value(1, w = 1).to_bits()
        for i in range(log2_up(self.p.n)-1, -1, -1):
            bit = way[i]
            next_state = next_state.idx_mask(idx, ~bit)
            idx = cat([idx, bit])
        return next_state[self.p.n-1: 1]

    def replace(self):
        return self.get_replace_way(self.state_reg)

    def get_replace_way(self, state):
        shifted_state = state << 1
        idx = value(1, w = 1).to_bits()
        for i in range(log2_up(self.p.n)-1, -1, -1):
            in_bounds = cat([idx, value(1 << i)])[log2_up(self.p.n)-1: 0] < self.p.n
            idx = cat([idx, in_bounds & shifted_state[idx]])
        return idx[log2_up(self.p.n)-1:0]
