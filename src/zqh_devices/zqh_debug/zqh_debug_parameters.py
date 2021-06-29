####
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/devices/debug/Debug.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_parameters import zqh_tilelink_node_module_parameter
from zqh_tilelink.zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter

#/** Parameters exposed to the top-level design, set based on
#  * external requirements, etc.
#  *
#  *  This object checks that the parameters conform to the 
#  *  full specification. The implementation which receives this
#  *  object can perform more checks on what that implementation
#  *  actually supports.
#  *  nComponents : The number of components to support debugging.
#  *  nDMIAddrSize : Size of the Debug Bus Address
#  *  nAbstractDataWords: Number of 32-bit words for Abstract Commands
#  *  nProgamBufferWords: Number of 32-bit words for Program Buffer
#  *  hasBusMaster: Whether or not a bus master should be included
#  *  maxSupportedSBAccess: Maximum transaction size supported by System Bus Access logic.
#  *  supportQuickAccess : Whether or not to support the quick access command.
#  *  supportHartArray : Whether or not to implement the hart array register.
#  *  hasImplicitEbreak: There is an additional RO program buffer word containing an ebreak
#  **/
class DebugModuleParams(parameter): 
  def set_par(self):
      super(DebugModuleParams, self).set_par();
      self.par('nComponents', 1)
      self.par('nDMIAddrSize', 7)
      self.par('nProgramBufferWords', 16)
      self.par('nAbstractDataWords', 4)
      self.par('nScratch', 1)
      self.par('hasBusMaster', 1)
      self.par('maxSupportedSBAccess', 32)
      self.par('supportQuickAccess', 0)
      self.par('supportHartArray', 0)
      self.par('hasImplicitEbreak', 0)
      self.par('xlen', 64)

      self.par('max_harts', 16)
  
  def check_par(self):
      super(DebugModuleParams, self).check_par()
      if (self.xlen == 32):
          self.nAbstractDataWords = 1
      elif (self.xlen == 64):
          self.nAbstractDataWords = 2
      else:
          self.nAbstractDataWords = 4
      self.maxSupportedSBAccess = self.xlen

      assert((self.nDMIAddrSize >= 7) and (self.nDMIAddrSize <= 32)), "Legal DMIAddrSize is 7-32, not ${nDMIAddrSize}" % (self.nDMIAddrSize)

      assert((self.nAbstractDataWords  > 0)  and (self.nAbstractDataWords  <= 16)), "Legal nAbstractDataWords is 0-16, not ${nAbstractDataWords}" % (self.nAbstractDataWords)
      assert((self.nProgramBufferWords >= 0) and (self.nProgramBufferWords <= 16)), "Legal nProgramBufferWords is 0-16, not ${nProgramBufferWords}" % (self.nProgramBufferWords)

      #if (supportQuickAccess) {
      #  // TODO: Check that quick access requirements are met.
      #}
  def gen_sb_tl_master_bundle_p(self, name = ''):
      return zqh_tl_bundle_all_channel_parameter(name)



class DefaultDebugModuleParams(DebugModuleParams, zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(DefaultDebugModuleParams, self).set_par()
        #self.par('xlen', 64)
        self.par('dumy', 0)

    def check_par(self):
        super(DefaultDebugModuleParams, self).check_par()
        #if (self.xlen == 32):
        #    self.nAbstractDataWords = 1
        #elif (self.xlen == 64):
        #    self.nAbstractDataWords = 2
        #else:
        #    self.nAbstractDataWords = 4
        #self.maxSupportedSBAccess = self.xlen

    def address(self):
        return self.extern_slaves[0].address[0]

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name, int_source_bits = self.nComponents)

    def gen_dmi_in_tl_bundle_p(self, name = ''):
        p = zqh_tl_bundle_all_channel_parameter(name)
        p.update_bus_bits(32, 8, 2)
        return p


#case object DebugModuleParams extends Field[DebugModuleParams]
#
#/** Functional parameters exposed to the design configuration.
#  *
#  *  hartIdToHartSel: For systems where hart ids are not 1:1 with hartsel, provide the mapping.
#  *  hartSelToHartId: Provide inverse mapping of the above
#  **/
#case class DebugModuleHartSelFuncs (
#  hartIdToHartSel : (UInt) => UInt = (x:UInt) => x,
#  hartSelToHartId : (UInt) => UInt = (x:UInt) => x
#)
#
#case object DebugModuleHartSelKey extends Field(DebugModuleHartSelFuncs())

class zqh_debug_dmi2tl_parameter(DebugModuleParams, zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_debug_dmi2tl_parameter, self).set_par()
        self.par('tl_bundle_p', self.gen_tl_bundle_p())

    def check_par(self):
        super(zqh_debug_dmi2tl_parameter, self).check_par()

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name)

class zqh_debug_dmi_inside_parameter(DebugModuleParams, zqh_tilelink_node_module_parameter):
    def set_par(self):
        super(zqh_debug_dmi_inside_parameter, self).set_par()
        self.par('tl_bundle_p', self.gen_tl_bundle_p())
        self.par('sync_delay', 3)

    def check_par(self):
        super(zqh_debug_dmi_inside_parameter, self).check_par()

    def gen_tl_bundle_p(self, name = ''):
        return zqh_tl_bundle_all_channel_parameter(name)

    def address(self):
        return self.extern_slaves[0].address[0]

    def hartIdToHartSel(self, x): 
        return x
    def hartSelToHartId(self, x):
        n = log2_up(self.nComponents)
        if (isinstance(x, bits) and x.get_w() > n):
            return x[n-1 : 0]
        else:
            return x

