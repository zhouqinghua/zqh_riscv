import sys
import os
from phgl_imp import *
from .zqh_axi4_parameters import *

class zqh_axi4_base_bundle(bundle):
    def set_par(self):
        super(zqh_axi4_base_bundle, self).set_par()
        self.p = zqh_axi4_base_parameter()

    def set_var(self):
        super(zqh_axi4_base_bundle, self).set_var()
        self.var(bits('id', w = self.p.id_w))
        self.var(bits('addr', w = self.p.addr_w))
        self.var(bits('len', w = self.p.len_w))
        self.var(bits('size', w = self.p.size_w))
        self.var(bits('burst', w = self.p.burst_w))
        self.var(bits('lock'))
        self.var(bits('cache', w = self.p.cache_w))
        self.var(bits('prot', w = self.p.prot_w))
        self.var(bits('qos', w = self.p.qos_w))
        if (self.p.region_w is not None):
            self.var(bits('region', w = self.p.region_w))
        if (self.p.user_w is not None):
            self.var(bits('user', w = self.p.user_w))

class zqh_axi4_aw_bundle(zqh_axi4_base_bundle):
    def set_par(self):
        super(zqh_axi4_aw_bundle, self).set_par()
        self.p = zqh_axi4_aw_parameter()

class zqh_axi4_w_bundle(bundle):
    def set_par(self):
        super(zqh_axi4_w_bundle, self).set_par()
        self.p = zqh_axi4_w_parameter()
    
    def set_var(self):
        super(zqh_axi4_w_bundle, self).set_var()
        self.var(bits('data', w = self.p.data_w))
        self.var(bits('strb', w = self.p.strb_w))
        self.var(bits('last'))
        if (self.p.user_w is not None):
            self.var(bits('user', w = self.p.user_w))

class zqh_axi4_b_bundle(bundle):
    def set_par(self):
        super(zqh_axi4_b_bundle, self).set_par()
        self.p = zqh_axi4_b_parameter()
    
    def set_var(self):
        super(zqh_axi4_b_bundle, self).set_var()
        self.var(bits('id', self.p.id_w))
        self.var(bits('resp', self.p.resp_w))
        if (self.p.user_w is not None):
            self.var(bits('user', self.p.user_w))

class zqh_axi4_ar_bundle(zqh_axi4_base_bundle):
    def set_par(self):
        super(zqh_axi4_ar_bundle, self).set_par()
        self.p = zqh_axi4_ar_parameter()

class zqh_axi4_r_bundle(bundle):
    def set_par(self):
        super(zqh_axi4_r_bundle, self).set_par()
        self.p = zqh_axi4_r_parameter()
    
    def set_var(self):
        super(zqh_axi4_r_bundle, self).set_var()
        self.var(bits('id', self.p.id_w))
        self.var(bits('data', self.p.data_w))
        self.var(bits('resp', self.p.resp_w))
        self.var(bits('last'))
        if (self.p.user_w is not None):
            self.var(bits('user', self.p.user_w))

class zqh_axi4_all_channel_io(bundle):
    def set_par(self):
        super(zqh_axi4_all_channel_io, self).set_par()
        self.p = zqh_axi4_all_channel_parameter()

    def set_var(self):
        super(zqh_axi4_all_channel_io, self).set_var()
        self.var(ready_valid('aw', gen = zqh_axi4_aw_bundle, p = self.p.channel['aw']))
        self.var(ready_valid('w', gen = zqh_axi4_w_bundle, p = self.p.channel['w']))
        self.var(ready_valid('b', gen = zqh_axi4_b_bundle, p = self.p.channel['b']).flip())
        self.var(ready_valid('ar', gen = zqh_axi4_ar_bundle, p = self.p.channel['ar']))
        self.var(ready_valid('r', gen = zqh_axi4_r_bundle, p = self.p.channel['r']).flip())
