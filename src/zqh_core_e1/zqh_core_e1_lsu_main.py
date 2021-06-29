import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_lsu_bundles import *
from zqh_core_common.zqh_core_common_lsu_main import zqh_core_common_lsu
from .zqh_core_e1_lsu_dcache_dtim_main import zqh_core_e1_lsu_dcache_dtim

class zqh_core_e1_lsu_arbiter(module):
    def set_par(self):
        super(zqh_core_e1_lsu_arbiter, self).set_par()
        self.p.par('num_ports', 2)

    def set_port(self):
        super(zqh_core_e1_lsu_arbiter, self).set_port()
        self.io.var(vec('input', gen = zqh_core_common_lsu_mem_io, n = self.p.num_ports))
        self.io.var(zqh_core_common_lsu_mem_io('out').flip())

    def main(self):
        super(zqh_core_e1_lsu_arbiter, self)

        dtim_arbiter = sp_arbiter(
            'dtim_arbiter',
            gen = zqh_core_common_lsu_mem_req,
            n = self.p.num_ports)
        for i in range(self.p.num_ports):
            dtim_arbiter.io.input[i] /= self.io.input[i].req
            self.io.input[i].resp /= self.io.out.resp
            self.io.input[i].busy /= self.io.out.busy
            self.io.input[i].events /= self.io.out.events

            #tag msb with port id
            tag_id_h = self.io.input[i].req.bits.tag.get_w() - 1
            tag_id_l = self.io.input[i].req.bits.tag.get_w() - log2_up(self.p.num_ports)
            if (self.p.num_ports > 1):
                dtim_arbiter.io.input[i].bits.tag[tag_id_h : tag_id_l] /= i
                #dispatch response to input port
                self.io.input[i].resp.valid /= (
                    self.io.out.resp.valid & 
                    (self.io.out.resp.bits.tag[tag_id_h : tag_id_l] == i))
                #mask off msb's tag id
                self.io.input[i].resp.bits.tag[tag_id_h : tag_id_l] /= 0
        self.io.out.req /= dtim_arbiter.io.out

class zqh_core_e1_lsu(zqh_core_common_lsu):
    def instance_dcache(self, mem_slave, flush_slave):
        dcache = zqh_core_e1_lsu_dcache_dtim(
            'dcache',
            extern_masters = [self.p.lsu_master])
        dcache_arb = zqh_core_e1_lsu_arbiter(
            'dcache_arb',
            num_ports = self.p.num_arb_ports)

        dcache_arb.io.input[0] /= flush_slave.io.lsu
        dcache_arb.io.input[1] /= mem_slave.io.lsu
        dcache_arb.io.input[2] /= self.io.cpu

        return (dcache_arb, dcache)
