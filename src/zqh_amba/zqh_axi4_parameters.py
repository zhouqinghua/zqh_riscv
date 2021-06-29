import sys
import os
from phgl_imp import *

class zqh_axi4_base_parameter(parameter):
    def set_par(self):
        super(zqh_axi4_base_parameter, self).set_par()
        self.par('id_w',4)
        self.par('addr_w',32)
        self.par('len_w',8)
        self.par('size_w',3)
        self.par('burst_w',2)
        self.par('cache_w',4)
        self.par('prot_w',3)
        self.par('qos_w',4)
        self.par('region_w',None)
        self.par('user_w',None)

    @classmethod
    def burst_fixed(self):
        return value(0, w = 2)

    @classmethod
    def burst_incr(self):
        return value(1, w = 2)

    @classmethod
    def burst_wrap(self):
        return value(2, w = 2)

    @classmethod
    def burst_reversed(self):
        return value(3, w = 2)

    def sync_all(self, a):
        self.id_w     = a.id_w    
        self.addr_w   = a.addr_w  
        self.len_w    = a.len_w   
        self.size_w   = a.size_w  
        self.burst_w  = a.burst_w 
        self.cache_w  = a.cache_w 
        self.prot_w   = a.prot_w  
        self.qos_w    = a.qos_w   
        self.region_w = a.region_w
        self.user_w   = a.user_w  

class zqh_axi4_aw_parameter(zqh_axi4_base_parameter):
    def set_par(self):
        super(zqh_axi4_aw_parameter, self).set_par()

class zqh_axi4_w_parameter(zqh_axi4_aw_parameter):
    def set_par(self):
        super(zqh_axi4_w_parameter, self).set_par()
        self.par('data_w',64)
        self.par('strb_w',8)

    def sync_all(self, a):
        super(zqh_axi4_w_parameter, self).sync_all(a)
        self.data_w = a.data_w
        self.strb_w= a.strb_w

class zqh_axi4_b_parameter(zqh_axi4_w_parameter):
    def set_par(self):
        super(zqh_axi4_b_parameter, self).set_par()
        self.par('resp_w',2)

    def sync_all(self, a):
        super(zqh_axi4_b_parameter, self).sync_all(a)
        self.resp_w = a.resp_w

class zqh_axi4_ar_parameter(zqh_axi4_base_parameter):
    def set_par(self):
        super(zqh_axi4_ar_parameter, self).set_par()

class zqh_axi4_r_parameter(zqh_axi4_ar_parameter):
    def set_par(self):
        super(zqh_axi4_r_parameter, self).set_par()
        self.par('data_w',64)
        self.par('resp_w',2)

    def sync_all(self, a):
        super(zqh_axi4_r_parameter, self).sync_all(a)
        self.data_w = a.data_w
        self.resp_w = a.resp_w

class zqh_axi4_all_channel_parameter(parameter):
    def set_par(self):
        super(zqh_axi4_all_channel_parameter, self).set_par()
        self.par('channel', {})

    def check_par(self):
        super(zqh_axi4_all_channel_parameter, self).check_par()
        self.channel['aw'] = zqh_axi4_aw_parameter()
        self.channel['w']  = zqh_axi4_w_parameter()
        self.channel['b']  = zqh_axi4_b_parameter()
        self.channel['ar'] = zqh_axi4_ar_parameter()
        self.channel['r']  = zqh_axi4_r_parameter()

    def sync_all(self, a):
        self.channel['aw'].sync_all(a.channel['aw'])
        self.channel['w' ].sync_all(a.channel['w' ])
        self.channel['b' ].sync_all(a.channel['b' ])
        self.channel['ar'].sync_all(a.channel['ar'])
        self.channel['r' ].sync_all(a.channel['r' ])
