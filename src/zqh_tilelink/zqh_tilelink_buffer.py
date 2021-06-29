import sys
import os
from phgl_imp import *
from .zqh_tilelink_bundles import zqh_tl_bundle

class zqh_tl_buffer(module):
    def set_par(self):
        super(zqh_tl_buffer, self).set_par()
        self.p.par('buf_p', None)
        self.p.par('tl_p', None)

    def set_port(self):
        super(zqh_tl_buffer, self).set_port()
        self.io.var(zqh_tl_bundle('tl_in', p = self.p.tl_p).flip())
        self.io.var(zqh_tl_bundle('tl_out', p = self.p.tl_p))

    def main(self):
        super(zqh_tl_buffer, self).main()
        qa = queue(
            'qa', 
            gen = type(self.io.tl_in.a.bits), 
            gen_p = self.p.tl_p.channel['a'], 
            entries = self.p.buf_p['a'].depth, 
            data_bypass = self.p.buf_p['a'].data_bypass, 
            ready_bypass = self.p.buf_p['a'].ready_bypass)
        qd = queue(
            'qd', 
            gen = type(self.io.tl_in.d.bits),
            gen_p = self.p.tl_p.channel['d'],
            entries = self.p.buf_p['d'].depth,
            data_bypass = self.p.buf_p['d'].data_bypass,
            ready_bypass = self.p.buf_p['d'].ready_bypass)

        qa.io.enq  /= self.io.tl_in.a
        qd.io.enq /= self.io.tl_out.d
        self.io.tl_out.a /= qa.io.deq 
        self.io.tl_in.d  /= qd.io.deq

        if (self.p.tl_p.tl_type == 'tl_c'):
            qb = queue(
                'qb',
                gen = type(self.io.tl_in.b.bits),
                gen_p = self.p.tl_p.channel['b'],
                entries = self.p.buf_p['b'].depth,
                data_bypass = self.p.buf_p['b'].data_bypass,
                ready_bypass = self.p.buf_p['b'].ready_bypass)
            qc = queue(
                'qc', 
                gen = type(self.io.tl_in.c.bits),
                gen_p = self.p.tl_p.channel['c'],
                entries = self.p.buf_p['c'].depth,
                data_bypass = self.p.buf_p['c'].data_bypass,
                ready_bypass = self.p.buf_p['c'].ready_bypass)
            qe = queue(
                'qe', 
                gen = type(self.io.tl_in.e.bits),
                gen_p = self.p.tl_p.channel['e'], 
                entries = self.p.buf_p['e'].depth,
                data_bypass = self.p.buf_p['e'].data_bypass, 
                ready_bypass = self.p.buf_p['e'].ready_bypass)

            qb.io.enq /= self.io.tl_out.b
            qc.io.enq /= self.io.tl_in.c
            qe.io.enq /= self.io.tl_in.e
            self.io.tl_in.b  /= qb.io.deq
            self.io.tl_out.c /= qc.io.deq
            self.io.tl_out.e /= qe.io.deq
