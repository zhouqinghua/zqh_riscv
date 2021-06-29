import sys
import os
from phgl_imp import *
from .zqh_tilelink_bundles import zqh_tl_bundle
from .zqh_tilelink_interfaces import zqh_tl_interface_in
from .zqh_tilelink_interfaces import zqh_tl_interface_out
from .zqh_tilelink_arbiter import zqh_tl_arbiter
from .zqh_tilelink_misc import TMSG_CONSTS

class zqh_tilelink_xbar(module):
    def set_par(self):
        super(zqh_tilelink_xbar, self).set_par()
        self.p.par('node', None)
        self.p.par('policy', zqh_tl_arbiter.roundRobin)
        self.p.par('tl_in_p', None)

    def set_port(self):
        super(zqh_tilelink_xbar, self).set_port()
        tl_in_p = (
            self.p.node.get_dw_fix_tl_p() if (self.p.tl_in_p is None) else
            self.p.tl_in_p)
        self.io.var(vec(
            'tl_in',
            gen = lambda _: zqh_tl_bundle(_, p = tl_in_p[_]),
            n = len(tl_in_p)).flip())
        self.io.var(vec(
            'tl_out', gen = lambda _: zqh_tl_bundle(_, p = self.p.node.bundle_out[_]),
            n = len(self.p.node.down)))

    def main(self):
        super(zqh_tilelink_xbar, self).main()
        port_in_num = len(self.p.node.up)
        port_out_num = len(self.p.node.down)

        if (port_in_num == 1 and port_out_num == 1):
            self.io.tl_out /= self.io.tl_in
            return

        interfacesIn = list(map(
            lambda _: zqh_tl_interface_in(
                'interfacesIn_'+str(_),
                slave_nodes = self.p.node.get_nearest_slave_nodes(),
                bundle = self.io.tl_in[_].p),
            range(port_in_num)))
        interfacesOut = list(map(
            lambda _: zqh_tl_interface_out(
                'interfacesOut_'+str(_),
                slave_nodes = self.p.node.get_nearest_slave_nodes(),
                bundle = self.p.node.bundle_out[_]),
            range(port_out_num)))

        inputIdRanges = range(port_in_num)
        inputId_w = log2_ceil(port_in_num)
        outputIdRanges = range(port_out_num)
        outputId_w = log2_ceil(port_out_num)



        beatsAI = list(map(
            lambda _: _[1].num_beats(_[0].a.bits),
            list(zip(self.io.tl_in, interfacesIn))))
        beatsCI = list(map(
            lambda _: _[1].num_beats(_[0].c.bits) if (_[0].p.tl_type == 'tl_c') else None,
            list(zip(self.io.tl_in, interfacesIn))))
        beatsEI = list(map(
            lambda _: _[1].num_beats(_[0].e.bits) if (_[0].p.tl_type == 'tl_c') else None,
            list(zip(self.io.tl_in, interfacesIn))))
        beatsDO = list(map(
            lambda _: _[1].num_beats(_[0].d.bits), 
            list(zip(self.io.tl_out, interfacesOut))))
        beatsBO = list(map(
            lambda _: _[1].num_beats(_[0].b.bits) if (_[0].p.tl_type == 'tl_c') else None,
            list(zip(self.io.tl_out, interfacesOut))))

        reqAOI = list(map(
            lambda o: list(map(
                lambda i: (
                    value(1).to_bits() if (port_out_num <= 1) else 
                    self.p.node.down[o].address_match_any(self.io.tl_in[i].a.bits.address)),
                range(port_in_num))),
            range(port_out_num)))
        reqCOI = list(map(
            lambda o: list(map(
                lambda i: (
                    value(1).to_bits() if (port_out_num <= 1) else 
                    self.p.node.down[o].address_match_any(
                        self.io.tl_in[i].c.bits.address)) if (
                            self.io.tl_in[i].p.tl_type == 'tl_c') else None,
                range(port_in_num))),
            range(port_out_num)))
        reqEOI = list(map(
            lambda o: list(map(
                lambda i: (
                    value(1).to_bits() if (port_out_num <= 1) else 
                    (
                        self.io.tl_in[i].e.bits.sink[
                            self.io.tl_in[i].p.channel['e'].sink_bits - 1 :
                            self.io.tl_in[i].p.channel['e'].sink_bits - outputId_w] == 
                        outputIdRanges[o])) if (
                            self.io.tl_in[i].p.tl_type == 'tl_c') else None,
                range(port_in_num))),
            range(port_out_num)))
        reqBIO = list(map(
            lambda i: list(map(
                lambda o: (
                    value(1).to_bits() if (port_in_num <= 1) else 
                    (
                        (
                            self.io.tl_out[o].b.bits.source[
                                self.p.node.bundle_out[o].channel['b'].source_bits - 1 :
                                self.p.node.bundle_out[o].channel['b'].source_bits - 
                                inputId_w] == inputIdRanges[i]) if (
                                    self.p.node.bundle_out[o].tl_type == 'tl_c') else None)),
                range(port_out_num))),
            range(port_in_num)))
        reqDIO = list(map(
            lambda i: list(map(
                lambda o: (
                    value(1).to_bits() if (port_in_num <= 1) else 
                    (
                        mux(
                            self.io.tl_out[o].d.bits.opcode == TMSG_CONSTS.release_ack(),
                            self.io.tl_out[o].d.bits.source[
                                self.p.node.bundle_out[o].channel['c'].source_bits - 1 :
                                self.p.node.bundle_out[o].channel['c'].source_bits - 
                                inputId_w],
                            self.io.tl_out[o].d.bits.source[
                                self.p.node.bundle_out[o].channel['a'].source_bits - 1 :
                                self.p.node.bundle_out[o].channel['a'].source_bits - 
                                inputId_w]) == 
                        inputIdRanges[i])),
                range(port_out_num))),
            range(port_in_num)))

        portsAOI = list(map(
            lambda o: list(map(
                lambda i: ready_valid(
                    'portsAOI_'+str(o)+'_'+str(i),
                    gen = type(self.io.tl_out[o].a.bits), 
                    p = self.p.node.bundle_out[o].channel['a']).as_bits(),
                range(port_in_num))),
            range(port_out_num)))
        for o in range(len(portsAOI)):
            for i in range(len(portsAOI[o])):
                portsAOI[o][i].valid /= self.io.tl_in[i].a.valid & reqAOI[o][i]
                portsAOI[o][i].bits /= self.io.tl_in[i].a.bits
                portsAOI[o][i].bits.source /= cat([
                    value(inputIdRanges[i], w = inputId_w),
                    self.io.tl_in[i].a.bits.source.u_ext(
                        self.p.node.bundle_out[o].channel['a'].source_bits - inputId_w)])
        for i in range(port_in_num):
            self.io.tl_in[i].a.ready /= reduce(
                lambda x, y: x | y, 
                list(map(
                    lambda _: _[0][i].ready & _[1][i],
                    list(zip(portsAOI, reqAOI)))))
        portsCOI = list(map(
            lambda o: list(map(
                lambda i: ready_valid(
                    'portsCOI_'+str(o)+'_'+str(i),
                    gen = type(self.io.tl_out[o].c.bits),
                    p = self.p.node.bundle_out[o].channel['c']).as_bits() if (
                        self.p.node.bundle_out[o].tl_type == 'tl_c') else None,
                range(port_in_num))),
            range(port_out_num)))
        for o in range(len(portsCOI)):
            if (self.p.node.bundle_out[o].tl_type == 'tl_c'):
                for i in range(len(portsCOI[o])):
                    if (self.io.tl_in[i].p.tl_type == 'tl_c'):
                        portsCOI[o][i].valid /= self.io.tl_in[i].c.valid & reqCOI[o][i]
                        portsCOI[o][i].bits /= self.io.tl_in[i].c.bits
                        portsCOI[o][i].bits.source /= cat([
                            value(inputIdRanges[i], w = inputId_w),
                            self.io.tl_in[i].c.bits.source.u_ext(
                                self.p.node.bundle_out[o].channel['c'].source_bits - 
                                inputId_w)])
                    else:
                        portsCOI[o][i].valid /= 0
                        portsCOI[o][i].bits /= 0
                        portsCOI[o][i].bits.source /= cat([
                            value(inputIdRanges[i], w = inputId_w),
                            value(
                                0,
                                w = self.p.node.bundle_out[o].channel['c'].source_bits - 
                                inputId_w)])
        for i in range(port_in_num):
            if (self.io.tl_in[i].p.tl_type == 'tl_c'):
                self.io.tl_in[i].c.ready /= reduce(
                    lambda x, y: x | y, 
                    list(map(
                        lambda _: _[0][i].ready & _[1][i], 
                        list(filter(
                            lambda _: _[0][i] is not None,
                            list(zip(portsCOI, reqCOI)))))))
        portsEOI = list(map(
            lambda o: list(map(
                lambda i: ready_valid(
                    'portsEOI_'+str(o)+'_'+str(i),
                    gen = type(self.io.tl_out[o].e.bits),
                    p = self.p.node.bundle_out[o].channel['e']).as_bits() if (
                        self.p.node.bundle_out[o].tl_type == 'tl_c') else None,
                range(port_in_num))),
            range(port_out_num)))
        for o in range(len(portsEOI)):
            if (self.p.node.bundle_out[o].tl_type == 'tl_c'):
                for i in range(len(portsEOI[o])):
                    if (self.io.tl_in[i].p.tl_type == 'tl_c'):
                        portsEOI[o][i].valid /= self.io.tl_in[i].e.valid & reqEOI[o][i]
                        portsEOI[o][i].bits /= self.io.tl_in[i].e.bits
                    else:
                        portsEOI[o][i].valid /= 0
                        portsEOI[o][i].bits /= 0
        for i in range(port_in_num):
            if (self.io.tl_in[i].p.tl_type == 'tl_c'):
                self.io.tl_in[i].e.ready /= reduce(
                    lambda x, y: x | y, 
                    list(map(
                        lambda _: _[0][i].ready & _[1][i], 
                        list(filter(
                            lambda _: _[0][i] is not None,
                            list(zip(portsEOI, reqEOI)))))))
        portsBIO = list(map(
            lambda i: list(map(
                lambda o: ready_valid(
                    'portsBIO_'+str(i)+'_'+str(o),
                    gen = type(self.io.tl_in[i].b.bits), 
                    p = self.io.tl_in[i].p.channel['b']).as_bits() if (
                        self.io.tl_in[i].p.tl_type == 'tl_c') else None,
                range(port_out_num))),
            range(port_in_num)))
        for i in range(len(portsBIO)):
            if (self.io.tl_in[i].p.tl_type == 'tl_c'):
                for o in range(len(portsBIO[i])):
                    if (self.io.tl_out[o].p.tl_type == 'tl_c'):
                        portsBIO[i][o].valid /= self.io.tl_out[o].b.valid & reqBIO[i][o]
                        portsBIO[i][o].bits /= self.io.tl_out[o].b.bits
                        portsBIO[i][o].bits.source /= self.io.tl_out[o].b.bits.source
                    else:
                        portsBIO[i][o].valid /= 0
                        portsBIO[i][o].bits /= 0
                        portsBIO[i][o].bits.source /= 0
        for o in range(port_out_num):
            if (self.p.node.bundle_out[o].tl_type == 'tl_c'):
                self.io.tl_out[o].b.ready /= reduce(
                    lambda x, y: x | y, 
                    list(map(
                        lambda _: _[0][o].ready & _[1][o],
                        list(filter(
                            lambda _: _[0][o] is not None,
                            list(zip(portsBIO, reqBIO)))))))
        portsDIO = list(map(
            lambda i: list(map(
                lambda o: ready_valid(
                    'portsDIO_'+str(i)+'_'+str(o),
                    gen = type(self.io.tl_in[i].d.bits),
                    p = self.io.tl_in[i].p.channel['d']).as_bits(),
                range(port_out_num))),
            range(port_in_num)))
        for i in range(len(portsDIO)):
            for o in range(len(portsDIO[i])):
                portsDIO[i][o].valid /= self.io.tl_out[o].d.valid & reqDIO[i][o]
                portsDIO[i][o].bits /= self.io.tl_out[o].d.bits
                portsDIO[i][o].bits.source /= self.io.tl_out[o].d.bits.source
        for o in range(port_out_num):
            self.io.tl_out[o].d.ready /= reduce(
                lambda x, y: x | y, 
                list(map(lambda _: _[0][o].ready & _[1][o], list(zip(portsDIO, reqDIO)))))

        for o in range(port_out_num):
            zqh_tl_arbiter.apply(
                self.p.policy,
                self.io.tl_out[o].a,
                list(filter(lambda _: _[1] is not None, list(zip(beatsAI, portsAOI[o])))))
            if (self.p.node.bundle_out[o].tl_type == 'tl_c'):
                zqh_tl_arbiter.apply(
                    self.p.policy,
                    self.io.tl_out[o].c,
                    list(filter(
                        lambda _: _[0] is not None and _[1] is not None,
                        list(zip(beatsCI, portsCOI[o])))))
                zqh_tl_arbiter.apply(
                    self.p.policy,
                    self.io.tl_out[o].e,
                    list(filter(
                        lambda _: _[0] is not None and _[1] is not None,
                        list(zip(beatsEI, portsEOI[o])))))

        for i in range(port_in_num):
            zqh_tl_arbiter.apply(
                self.p.policy,
                self.io.tl_in[i].d,
                list(filter(lambda _: _[1] is not None, list(zip(beatsDO, portsDIO[i])))))
            if (self.io.tl_in[i].p.tl_type == 'tl_c'):
                zqh_tl_arbiter.apply(
                    self.p.policy,
                    self.io.tl_in[i].b,
                    list(filter(
                        lambda _: _[0] is not None and _[1] is not None,
                        list(zip(beatsBO, portsBIO[i])))))
