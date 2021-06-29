import sys
import os
from phgl_imp import *
from .zqh_axi4_bundles import zqh_axi4_all_channel_io

class zqh_axi4_buffer(module):
    def set_par(self):
        super(zqh_axi4_buffer, self).set_par()
        self.p.par('buf_p', None)
        self.p.par('axi4_p', None)

    def set_port(self):
        super(zqh_axi4_buffer, self).set_port()
        self.io.var(zqh_axi4_all_channel_io('axi4_in', p = self.p.axi4_p).flip())
        self.io.var(zqh_axi4_all_channel_io('axi4_out', p = self.p.axi4_p))

    def main(self):
        super(zqh_axi4_buffer, self).main()
        qar = queue(
            'qar',
            gen = type(self.io.axi4_in.ar.bits),
            gen_p = self.p.axi4_p.channel['ar'],
            entries = self.p.buf_p['ar'].depth,
            data_bypass = self.p.buf_p['ar'].data_bypass,
            ready_bypass = self.p.buf_p['ar'].ready_bypass)
        qaw = queue(
            'qaw',
            gen = type(self.io.axi4_in.aw.bits),
            gen_p = self.p.axi4_p.channel['aw'],
            entries = self.p.buf_p['aw'].depth,
            data_bypass = self.p.buf_p['aw'].data_bypass,
            ready_bypass = self.p.buf_p['aw'].ready_bypass)
        qw = queue(
            'qw',
            gen = type(self.io.axi4_in.w.bits),
            gen_p = self.p.axi4_p.channel['w'],
            entries = self.p.buf_p['w'].depth,
            data_bypass = self.p.buf_p['w'].data_bypass,
            ready_bypass = self.p.buf_p['w'].ready_bypass)
        qr = queue(
            'qr',
            gen = type(self.io.axi4_in.r.bits),
            gen_p = self.p.axi4_p.channel['r'],
            entries = self.p.buf_p['r'].depth,
            data_bypass = self.p.buf_p['r'].data_bypass,
            ready_bypass = self.p.buf_p['r'].ready_bypass)
        qb = queue(
            'qb',
            gen = type(self.io.axi4_in.b.bits),
            gen_p = self.p.axi4_p.channel['b'],
            entries = self.p.buf_p['b'].depth,
            data_bypass = self.p.buf_p['b'].data_bypass,
            ready_bypass = self.p.buf_p['b'].ready_bypass)

        qar.io.enq  /= self.io.axi4_in.ar
        qr.io.enq /= self.io.axi4_out.r
        self.io.axi4_out.ar /= qar.io.deq 
        self.io.axi4_in.r  /= qr.io.deq

        qaw.io.enq  /= self.io.axi4_in.aw
        qw.io.enq  /= self.io.axi4_in.w
        qb.io.enq /= self.io.axi4_out.b
        self.io.axi4_out.aw /= qaw.io.deq 
        self.io.axi4_out.w /= qw.io.deq 
        self.io.axi4_in.b  /= qb.io.deq
