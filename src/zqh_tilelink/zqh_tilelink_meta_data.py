#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/tilelink/Metadata.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_misc import *
from .zqh_tilelink_misc import TPM_CONSTS
from zqh_core_common.zqh_core_common_misc import M_CONSTS
from zqh_core_common.zqh_core_common_misc import zqh_core_common_memory_consts
class zqh_client_states(object):
    width = 2

    @classmethod
    def nothing(self):
        return value(0, self.width)
    @classmethod
    def branch(self):
        return value(1, self.width)
    @classmethod
    def trunk(self):
        return value(2, self.width)
    @classmethod
    def dirty(self):
        return value(3, self.width)

    @classmethod
    def has_read_permission(self, state):
        return state > self.nothing()
    @classmethod
    def has_write_permission(self, state): 
        return state > self.branch()

class zqh_memory_op_categories(zqh_core_common_memory_consts):
    @classmethod
    def wr(self):
        return cat([value(1), value(1)])   # Op actually writes
    @classmethod
    def wi(self):
        return cat([value(0), value(1)])  # Future op will write
    @classmethod
    def rd(self):
        return cat([value(0), value(0)]) # Op only reads

    @classmethod
    def categorize(self, cmd):
      cat_ = cat([M_CONSTS.is_write(cmd), M_CONSTS.is_write_intent(cmd)])
      ##assert(cat.isOneOf(wr,wi,rd), "Could not categorize command.")
      return cat_

#/** Stores the client-side coherence information,
#  * such as permissions on the data and whether the data is dirty.
#  * Its API can be used to make TileLink messages in response to
#  * memory operations, cache control oeprations, or Probe messages.
#  */
class zqh_client_metadata(bundle):
    def set_var(self):
        super(zqh_client_metadata, self).set_var()
        #/** Actual state information stored in this bundle */
        self.var(bits('state', w = zqh_client_states.width))

    #/** Metadata equality */
    def __eq__(self, a):
        if isinstance(a, bits):
            return self.state == a
        elif isinstance(a, zqh_client_metadata):
            return self.state == a.state
        else:
            assert(0)
  
    def __ne__(self, a):
        return ~self.__eq__(a)
  
    #/** Is the block's data present in this cache */
    def is_valid(self, dummy = 0):
        return self.state > zqh_client_states.nothing()
  
    #/** Determine whether this cmd misses, and the new state (on hit) or param to be sent (on miss) */
    def grow_starter(self, cmd):
        c = zqh_memory_op_categories.categorize(cmd)
        key = cat([c, self.state])
        default = (
            value(0, w = 1),
            value(0, w = max(zqh_client_states.width, TPM_CONSTS.a_width)))
        mapping = [
          ##(effect, am now) -> (was a hit,   next)
            (
                cat([zqh_memory_op_categories.rd(), zqh_client_states.dirty() ])  ,
                (value(1),  zqh_client_states.dirty() )),
            (
                cat([zqh_memory_op_categories.rd(), zqh_client_states.trunk() ])  ,
                (value(1),  zqh_client_states.trunk() )),
            (
                cat([zqh_memory_op_categories.rd(), zqh_client_states.branch()])  ,
                (value(1),  zqh_client_states.branch())),
            (
                cat([zqh_memory_op_categories.wi(), zqh_client_states.dirty() ])  ,
                (value(1),  zqh_client_states.dirty() )),
            (
                cat([zqh_memory_op_categories.wi(), zqh_client_states.trunk() ])  ,
                (value(1),  zqh_client_states.trunk() )),
            (
                cat([zqh_memory_op_categories.wr(), zqh_client_states.dirty() ])  ,
                (value(1),  zqh_client_states.dirty() )),
            (
                cat([zqh_memory_op_categories.wr(), zqh_client_states.trunk() ])  ,
                (value(1),  zqh_client_states.dirty() )),
          ##(ceffect, am now) -> (was a miss,  param)
            (
                cat([zqh_memory_op_categories.rd(), zqh_client_states.nothing()]) ,
                (value(0), TPM_CONSTS.n_to_b()  )),
            (
                cat([zqh_memory_op_categories.wi(), zqh_client_states.branch() ]) ,
                (value(0), TPM_CONSTS.b_to_t()  )),
            (
                cat([zqh_memory_op_categories.wi(), zqh_client_states.nothing()]) ,
                (value(0), TPM_CONSTS.n_to_t()  )),
            (
                cat([zqh_memory_op_categories.wr(), zqh_client_states.branch() ]) ,
                (value(0), TPM_CONSTS.b_to_t()  )),
            (
                cat([zqh_memory_op_categories.wr(), zqh_client_states.nothing()]) ,
                (value(0), TPM_CONSTS.n_to_t()  ))]
        res = (
            sel_map(
                cat([c, self.state]),
                list(map(lambda _: (_[0], _[1][0]), mapping)), default[0]),
            sel_map(
                cat([c, self.state]),
                list(map(lambda _: (_[0], _[1][1]), mapping)), default[1]))
        return res
  
    #/** Determine what state to go to after miss based on Grant param
    #  * For now, doesn't depend on state (which may have been Probed).
    #  */
    def grow_finisher(self, cmd, param):
        c = zqh_memory_op_categories.categorize(cmd)
        ##assert(c === rd || param === toT, "Client was expecting trunk permissions.")
        return sel_map(cat([c, param]), [
        ##(effect param) -> (next)
          (
              cat([zqh_memory_op_categories.rd(), TPM_CONSTS.to_b()])   ,
              zqh_client_states.branch()),
          (
              cat([zqh_memory_op_categories.rd(), TPM_CONSTS.to_t()])   ,
              zqh_client_states.trunk() ),
          (
              cat([zqh_memory_op_categories.wi(), TPM_CONSTS.to_t()])   ,
              zqh_client_states.trunk() ),
          (
              cat([zqh_memory_op_categories.wr(), TPM_CONSTS.to_t()])   ,
              zqh_client_states.dirty() )], zqh_client_states.nothing())
  
    #/** Does this cache have permissions on this block sufficient to perform op,
    #  * and what to do next (Acquire message param or updated metadata). */
    def on_access(self, cmd):
        r = self.grow_starter(cmd)
        return (r[0], r[1], zqh_client_metadata.apply(r[1]))
  
    #/** Does a secondary miss on the block require another Acquire message */
    def on_secondary_access(self, first_cmd, second_cmd):
        r1 = self.grow_starter(first_cmd)
        r2 = self.grow_starter(second_cmd)
        needs_second_acq = (
            M_CONSTS.is_write_intent(second_cmd) & 
            ~M_CONSTS.is_write_intent(first_cmd))
        hit_again = r1[0] & r2[0]
        dirties = (
            zqh_memory_op_categories.categorize(second_cmd) == 
            zqh_memory_op_categories.wr())
        biggest_grow_param = mux(dirties, r2[1], r1[1])
        dirtiest_state = zqh_client_metadata.apply(biggest_grow_param)
        dirtiest_cmd = mux(dirties, second_cmd, first_cmd)
        return (
            needs_second_acq,
            hit_again,
            biggest_grow_param,
            dirtiest_state, 
            dirtiest_cmd)
  
    #/** Metadata change on a returned Grant */
    def on_grant(self, cmd, param): 
        return zqh_client_metadata.apply(self.grow_finisher(cmd, param))
  
    #/** Determine what state to go to based on Probe param */
    def shrink_helper(self, param):
        key = cat([param, self.state])
        default = (
            value(0, w = 1),
            value(0, w = TPM_CONSTS.c_width),
            value(0, w = zqh_client_states.width))
        mapping = [
            (
                cat([TPM_CONSTS.to_t(), zqh_client_states.dirty  ()]) , 
                (value(1), TPM_CONSTS.t_to_t(), zqh_client_states.trunk  ())),
            (
                cat([TPM_CONSTS.to_t(), zqh_client_states.trunk  ()]) , 
                (value(0), TPM_CONSTS.t_to_t(), zqh_client_states.trunk  ())),
            (
                cat([TPM_CONSTS.to_t(), zqh_client_states.branch ()]) , 
                (value(0), TPM_CONSTS.b_to_b(), zqh_client_states.branch ())),
            (
                cat([TPM_CONSTS.to_t(), zqh_client_states.nothing()]) , 
                (value(0), TPM_CONSTS.n_to_n(), zqh_client_states.nothing())),
            (
                cat([TPM_CONSTS.to_b(), zqh_client_states.dirty  ()]) , 
                (value(1), TPM_CONSTS.t_to_b(), zqh_client_states.branch ())),
            (
                ## Policy: Don't notify on clean downgrade
                cat([TPM_CONSTS.to_b(), zqh_client_states.trunk  ()]) , 
                (value(0), TPM_CONSTS.t_to_b(), zqh_client_states.branch ())),
            (
                cat([TPM_CONSTS.to_b(), zqh_client_states.branch ()]) , 
                (value(0), TPM_CONSTS.b_to_b(), zqh_client_states.branch ())),
            (
                cat([TPM_CONSTS.to_b(), zqh_client_states.nothing()]) , 
                (value(0), TPM_CONSTS.b_to_n(), zqh_client_states.nothing())),
            (
                cat([TPM_CONSTS.to_n(), zqh_client_states.dirty  ()]) , 
                (value(1), TPM_CONSTS.t_to_n(), zqh_client_states.nothing())),
            (
                ## Policy: Don't notify on clean downgrade
                cat([TPM_CONSTS.to_n(), zqh_client_states.trunk  ()]) , 
                (value(0), TPM_CONSTS.t_to_n(), zqh_client_states.nothing())),
            (
                ## Policy: Don't notify on clean downgrade
                cat([TPM_CONSTS.to_n(), zqh_client_states.branch ()]) , 
                (value(0), TPM_CONSTS.b_to_n(), zqh_client_states.nothing())),
            (
                cat([TPM_CONSTS.to_n(), zqh_client_states.nothing()]) ,
                (value(0), TPM_CONSTS.n_to_n(), zqh_client_states.nothing()))]
        res = (sel_map(key, list(map(lambda _: (_[0], _[1][0]), mapping)), default[0]),
            sel_map(key, list(map(lambda _: (_[0], _[1][1]), mapping)), default[1]),
            sel_map(key, list(map(lambda _: (_[0], _[1][2]), mapping)), default[2]))
        return res
  
    #/** Translate cache control cmds into Probe param */
    def cmd_to_perm_cap(self, cmd):
        return sel_map(cmd, [
            (M_CONSTS.M_FLUSH  () , TPM_CONSTS.to_n()),
            (M_CONSTS.M_PRODUCE() , TPM_CONSTS.to_b()),
            (M_CONSTS.M_CLEAN  () , TPM_CONSTS.to_t())], TPM_CONSTS.to_n())
  
    def on_cache_control(self, cmd):
        r = self.shrink_helper(self.cmd_to_perm_cap(cmd))
        return (r[0], r[1], zqh_client_metadata.apply(r[2]))
  
    def on_probe(self, param):
        r = self.shrink_helper(param)
        return (r[0], r[1], zqh_client_metadata.apply(r[2]))

    #/** Factories for zqh_client_metadata, including on reset */
    @classmethod
    def apply(self, perm):
        meta = zqh_client_metadata()
        meta.state /= perm
        return meta
    @classmethod
    def on_reset(self):
        return zqh_client_metadata.apply(zqh_client_states.nothing())
    @classmethod
    def maximum(self):
        return zqh_client_metadata.apply(zqh_client_states.dirty())
