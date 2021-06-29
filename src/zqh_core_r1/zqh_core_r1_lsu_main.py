import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_lsu_bundles import *
from zqh_core_common.zqh_core_common_lsu_main import zqh_core_common_lsu
from .zqh_core_r1_lsu_dcache_dtim_main import zqh_core_r1_lsu_dcache_dtim

class zqh_core_r1_lsu_arbiter(module):
    def set_par(self):
        super(zqh_core_r1_lsu_arbiter, self).set_par()
        self.p.par('num_ports', None)

    def set_port(self):
        super(zqh_core_r1_lsu_arbiter, self).set_port()
        self.io.var(vec('input', gen = zqh_core_common_lsu_mem_io, n = self.p.num_ports))
        self.io.var(zqh_core_common_lsu_mem_io('out').flip())

    def main(self):
        super(zqh_core_r1_lsu_arbiter, self).main()
        if (self.p.num_ports == 1):
            self.io.out /= self.io.input[0]
        else:
            self.s1_id = reg('s1_id', w = log2_ceil(self.p.num_ports))
            s2_id = reg('s2_id', next = self.s1_id)

            self.io.out.req.valid /= reduce(
                lambda x, y: x | y, list(map(lambda _: _.req.valid, self.io.input)))
            self.io.input[0].req.ready /= self.io.out.req.ready
            for i in range(1, self.p.num_ports):
                self.io.input[i].req.ready /= (
                    self.io.input[i-1].req.ready & ~self.io.input[i-1].req.valid)

            for i in range(self.p.num_ports - 1, -1, -1):
                req = self.io.input[i].req
                def connect_s0():
                    self.io.out.req.bits.cmd /= req.bits.cmd
                    self.io.out.req.bits.type /= req.bits.type
                    self.io.out.req.bits.addr /= req.bits.addr
                    self.io.out.req.bits.error /= req.bits.error
                    self.io.out.req.bits.tag /= cat([
                        req.bits.tag,
                        value(i, w = log2_up(self.p.num_ports))])
                    self.s1_id /= i
                def connect_s1():
                    self.io.out.s1_kill /= self.io.input[i].s1_kill
                    self.io.out.s1_data /= self.io.input[i].s1_data
                def connect_s2():
                    pass

                if (i == self.p.num_ports - 1):
                    connect_s0()
                    connect_s1()
                    connect_s2()
                else:
                    with when (req.valid):
                        connect_s0() 
                    with when (self.s1_id == i):
                        connect_s1() 
                    with when (s2_id == i):
                        connect_s2() 

            for i in range(self.p.num_ports):
                resp = self.io.input[i].resp
                tag_hit = self.io.out.resp.bits.tag[log2_up(self.p.num_ports)-1:0] == i
                resp.valid /= self.io.out.resp.valid & tag_hit
                self.io.input[i].busy /= self.io.out.busy
                self.io.input[i].events /= self.io.out.events
                resp.bits /= self.io.out.resp.bits
                resp.bits.tag /= self.io.out.resp.bits.tag >> log2_up(self.p.num_ports)

                self.io.input[i].slow_kill /= self.io.out.slow_kill

class zqh_core_r1_lsu(zqh_core_common_lsu):
    def instance_dcache(self, mem_slave, flush_slave):
        dcache_arb = zqh_core_r1_lsu_arbiter(
            'dcache_arb',
            num_ports = self.p.num_arb_ports)
        dcache = zqh_core_r1_lsu_dcache_dtim(
            'dcache',
            extern_masters = [self.p.lsu_master])

        dcache_arb.io.input[0] /= flush_slave.io.lsu
        dcache_arb.io.input[1] /= self.io.cpu
        dcache.io.slave /= mem_slave.io.lsu
        return (dcache_arb, dcache)
