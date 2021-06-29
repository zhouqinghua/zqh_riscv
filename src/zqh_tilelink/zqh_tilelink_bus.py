import sys
import os
from phgl_imp import *
from .zqh_tilelink_bundles import zqh_tl_bundle
from .zqh_tilelink_xbar import zqh_tilelink_xbar
from .zqh_tilelink_station import zqh_tilelink_station
from .zqh_tilelink_node_parameters import zqh_tilelink_node_base_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_xbar_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_slave_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_slave_io_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_master_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_master_io_parameter
from .zqh_tilelink_buffer import zqh_tl_buffer
from .zqh_tilelink_dw_fix_main import zqh_tilelink_dw_fix
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_base_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_slave_io_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_master_io_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_slave_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_master_parameter

class zqh_tilelink_bus(module):
    def set_par(self):
        super(zqh_tilelink_bus, self).set_par()
        self.p.par('node', None)

    def set_port(self):
        super(zqh_tilelink_bus, self).set_port()
        self.io.var(vec(
            'tl_from', 
            gen = lambda _: zqh_tl_bundle(_, p = self.p.node.bundle_in[_]),
            n = len(self.p.node.up)).flip())
        self.io.var(vec(
            'tl_to', 
            gen = lambda _: zqh_tl_bundle(_, p = self.p.node.bundle_out[_]),
            n = len(self.p.node.down)))

    def main(self):
        super(zqh_tilelink_bus, self).main()
        process_in = []
        if (self.p.node.buffer_in is not None):
            for i in range(len(self.p.node.up)):
                buffer = zqh_tl_buffer(
                    'buffer_in_'+str(i), 
                    buf_p = self.p.node.buffer_in,
                    tl_p = self.p.node.bundle_in[i])
                buffer.io.tl_in /= self.io.tl_from[i]
                process_in.append(buffer.io.tl_out)
        else:
            for i in range(len(self.io.tl_from)):
                process_in.append(self.io.tl_from[i])

        post_process = []
        if (self.p.node.process is not None):
            process_out = vec(
                'process_out',
                gen = lambda _: zqh_tl_bundle(_, p = self.p.node.bundle_out[_]).as_bits(),
                n = len(self.p.node.up))
            for i in range(len(process_in)):
                tmp_in = process_in[i]
                for j in range(len(self.p.node.process)):
                    if (self.p.node.process[j] is None):
                        res = tmp_in
                    else:
                        (func, args) = self.p.node.process[j]
                    res = func(self.p.node, tmp_in, args)
                    tmp_in = res
                process_out[i] /= res
                post_process.append(process_out[i])
        else:
            for i in range(len(self.io.tl_from)):
                post_process.append(process_in[i])

        post_dw_fix = []
        if (self.p.node.down_bus_data_bits != self.p.node.up_bus_data_bits):
            all_slave_size = list(map(
                lambda _: _.transfer_sizes.max,
                self.p.node.get_nearest_slave_nodes()))
            max_size = max(all_slave_size)
            #each slave's max size must same
            for i in all_slave_size:
                assert(i == max_size)
            fix_dw_tl_p = self.p.node.get_dw_fix_tl_p()
            for i in range(len(fix_dw_tl_p)):
                fix_dw_tl_p[i].sync_source_bits(post_process[i].p)
                fix_dw_tl_p[i].sync_sink_bits(post_process[i].p)
            for i in range(len(self.p.node.up)):
                has_burst = max_size > self.p.node.down_bus_data_bits
                res = zqh_tilelink_dw_fix(self.p.node, post_process[i], has_burst)
                post_dw_fix.append(res)
        else:
            fix_dw_tl_p = list(map(lambda _: _.p, post_process))
            post_dw_fix = post_process

        pre_buffer = []
        tl_xbar = zqh_tilelink_xbar(
            'tl_xbar',
            node = self.p.node, 
            tl_in_p = None if (self.p.node.process is None) else fix_dw_tl_p)
        assert(len(self.io.tl_from) == len(tl_xbar.io.tl_in))
        assert(len(self.io.tl_to) == len(tl_xbar.io.tl_out))
        for i in range(len(self.p.node.up)):
            tl_xbar.io.tl_in[i] /= post_dw_fix[i]
            assert(
                tl_xbar.io.tl_in[i].p.channel['a'].source_bits == 
                post_dw_fix[i].p.channel['a'].source_bits)
            assert(
                tl_xbar.io.tl_in[i].p.channel['b'].source_bits == 
                post_dw_fix[i].p.channel['b'].source_bits)
            assert(
                tl_xbar.io.tl_in[i].p.channel['c'].source_bits == 
                post_dw_fix[i].p.channel['c'].source_bits)
            assert(
                tl_xbar.io.tl_in[i].p.channel['d'].source_bits == 
                post_dw_fix[i].p.channel['d'].source_bits)
        for i in range(len(self.p.node.down)):
            pre_buffer.append(tl_xbar.io.tl_out[i])

        if (self.p.node.buffer_out is not None):
            for i in range(len(self.p.node.down)):
                buffer = zqh_tl_buffer(
                    'buffer_out_'+str(i), 
                    buf_p = self.p.node.buffer_out,
                    tl_p = self.p.node.bundle_out[i])
                buffer.io.tl_in /= pre_buffer[i]
                self.io.tl_to[i] /= buffer.io.tl_out
        else:
            for i in range(len(self.io.tl_to)):
                self.io.tl_to[i] /= pre_buffer[i]

    @classmethod
    def get_slave_node(self, a):
        node_q = []
        for i in range(len(a)):
            if (isinstance(a[i], zqh_tilelink_node_slave_parameter)):
                node_q.append(a[i])
            else:
                node_q.extend(self.get_slave_node(a[i].down))
        return node_q

    @classmethod
    def imp_master(self, a):
        if (isinstance(a, (
            zqh_tilelink_node_master_io_parameter,
            zqh_axi4_node_master_io_parameter))):
            if (isinstance(a.down[0], zqh_tilelink_node_xbar_parameter)):
                a.imp = a.down[0].parent if (a.imp is None) else a.imp
            else:
                a.imp = a.down[0].imp.parent if (a.imp is None) else a.imp
        elif (isinstance(a, (
            zqh_tilelink_node_slave_io_parameter,
            zqh_axi4_node_slave_io_parameter))):
            a.imp = a.up[0].imp.parent if (a.imp is None) else a.imp
        elif (isinstance(a, zqh_tilelink_node_master_parameter)):
            a.imp = zqh_tilelink_station(
                'station_from_'+a.name, 
                node = a) if (a.imp is None) else a.imp
            for i in a.up:
                self.imp_master(i)
        elif (isinstance(a, (
            zqh_tilelink_node_base_parameter, 
            zqh_axi4_node_base_parameter))):
            for i in a.up:
                self.imp_master(i)

    @classmethod
    def imp_slave(self, a):
        if (isinstance(a, (
            zqh_tilelink_node_slave_io_parameter,
            zqh_axi4_node_slave_io_parameter))):
            if (isinstance(a.up[0], zqh_tilelink_node_xbar_parameter)):
                a.imp = a.up[0].parent if (a.imp is None) else a.imp
            else:
                a.imp = a.up[0].imp.parent if (a.imp is None) else a.imp
        elif (isinstance(a, (
            zqh_tilelink_node_master_io_parameter,
            zqh_axi4_node_master_io_parameter))):
            a.imp = a.down[0].imp.parent if (a.imp is None) else a.imp
        elif (isinstance(a, (
            zqh_tilelink_node_slave_parameter,
            zqh_axi4_node_slave_parameter))):
            a.imp = zqh_tilelink_station(
                'station_to_'+a.name,
                node = a) if (a.imp is None) else a.imp
            for i in a.down:
                self.imp_slave(i)
        elif (isinstance(a, zqh_tilelink_node_base_parameter)):
            for i in a.down:
                self.imp_slave(i)

    @classmethod
    def imp_master_slave(self, a):
        if (isinstance(a, (
            zqh_tilelink_node_slave_parameter,
            zqh_axi4_node_slave_parameter))):
            self.imp_slave(a)
            self.imp_master(a)
        else:
            self.imp_master(a)
            self.imp_slave(a)

    @classmethod
    def imp_cross_bus_up(self, a):
        if (isinstance(a, (
            zqh_tilelink_node_master_parameter,
            zqh_axi4_node_master_parameter))):
            return
        elif (isinstance(a, zqh_tilelink_node_xbar_parameter)):
            a.imp = zqh_tilelink_bus('bus_'+a.name, node = a) if (a.imp is None) else a.imp
        for i in a.up:
            self.imp_cross_bus_up(i)

    @classmethod
    def imp_cross_bus_down(self, a):
        if (isinstance(a, (
            zqh_tilelink_node_slave_io_parameter,
            zqh_axi4_node_slave_io_parameter,
            zqh_tilelink_node_master_io_parameter,
            zqh_axi4_node_master_io_parameter))):
            return
        elif (isinstance(a, zqh_tilelink_node_xbar_parameter)):
            a.imp = zqh_tilelink_bus('bus_'+a.name, node = a) if (a.imp is None) else a.imp
        for i in a.down:
            self.imp_cross_bus_down(i)

    @classmethod
    def imp_cross_bus(self, a):
        self.imp_cross_bus_up(a)
        for i in a.down:
            if (isinstance(i, zqh_tilelink_node_base_parameter)):
                self.imp_cross_bus_down(i)

    @classmethod
    def imp_connect(self, a):
        self.imp_connect_up(a)
        self.imp_connect_down(a)

    @classmethod
    def imp_connect_up(self, a):
        if ((len(a.up) == 0) and isinstance(a, zqh_tilelink_node_master_parameter)):
            for i in a.imp.io.tl_from:
                i.a.valid /= 0
                i.d.ready /= 1
                if (i.p.tl_type == 'tl_c'):
                    i.c.valid /= 0
                    i.e.valid /= 0
                    i.b.ready /= 1

        for i in range(len(a.up)):
            if (isinstance(a.up[i], bundle)):
                a.imp.io.tl_from[i] /= a.up[i]
                assert(
                    a.imp.io.tl_from[i].a.bits.source.get_w() == 
                    a.up[i].a.bits.source.get_w())
                assert(
                    a.imp.io.tl_from[i].d.bits.sink.get_w() == 
                    a.up[i].d.bits.sink.get_w())
            else:
                idx = a.up[i].down.index(a)
                if (isinstance(a.up[i], (
                    zqh_tilelink_node_master_io_parameter, 
                    zqh_axi4_node_master_io_parameter))):
                    io_idx = a.up[i].imp.get_tl_from_id(a.up[i])
                    if (isinstance(a.up[i], (zqh_axi4_node_master_io_parameter))):
                        a.imp.io.tl_from[i] /= a.up[i].imp.io.axi4_from[idx+io_idx]
                    else:
                        a.imp.io.tl_from[i] /= a.up[i].imp.io.tl_from[idx+io_idx]
                        #tmp print(a.name)
                        #tmp print(a.imp.name)
                        #tmp print(a.up[i].name)
                        #tmp print(a.up[i].imp.name)
                        #tmp print(i)
                        #tmp print(idx)
                        #tmp print(io_idx)
                        #tmp print(a.imp.io.tl_from)
                        #tmp print(a.up[i].imp.io.tl_from)
                        assert(
                            a.imp.io.tl_from[i].a.bits.source.get_w() == 
                            a.up[i].imp.io.tl_from[idx+io_idx].a.bits.source.get_w())
                        assert(
                            a.imp.io.tl_from[i].d.bits.sink.get_w() == 
                            a.up[i].imp.io.tl_from[idx+io_idx].d.bits.sink.get_w())
                    if (a.up[i].address_mask is not None):
                        a.imp.io.tl_from[i].a.bits.address /= a.up[i].imp.io.tl_from[
                            idx+io_idx].a.bits.address & a.up[i].address_mask
                        if (
                            a.imp.io.tl_from[i].p.tl_type == 'tl_c' and 
                            a.up[i].imp.io.tl_from[idx+io_idx].p.tl_type == 'tl_c'):
                            a.imp.io.tl_from[i].c.bits.address /= a.up[i].imp.io.tl_from[
                                idx+io_idx].c.bits.address & a.up[i].address_mask
                elif (isinstance(a.up[i], (
                    zqh_tilelink_node_slave_io_parameter,
                    zqh_axi4_node_slave_io_parameter))):
                    tmp_idx = a.up[i].imp.get_tl_to_id(a.up[i])
                    a.imp.io.tl_from[i] /= a.up[i].imp.io.tl_to[tmp_idx]
                    assert(
                        a.imp.io.tl_from[i].a.bits.source.get_w() == 
                        a.up[i].imp.io.tl_to[tmp_idx].a.bits.source.get_w())
                    assert(
                        a.imp.io.tl_from[i].d.bits.sink.get_w() == 
                        a.up[i].imp.io.tl_to[tmp_idx].d.bits.sink.get_w())
                else:
                    a.imp.io.tl_from[i] /= a.up[i].imp.io.tl_to[idx]

                    if (a.up[i].address_mask is not None):
                        a.imp.io.tl_from[i].a.bits.address /= a.up[i].imp.io.tl_to[
                            idx].a.bits.address & a.up[i].address_mask
                        if (
                            a.imp.io.tl_from[i].p.tl_type == 'tl_c' and 
                            a.up[i].imp.io.tl_to[idx].p.tl_type == 'tl_c'):
                            a.imp.io.tl_from[i].c.bits.address /= a.up[i].imp.io.tl_to[
                                idx].c.bits.address & a.up[i].address_mask

                    self.imp_connect_up(a.up[i])

    @classmethod
    def imp_connect_down(self, a):
        if (len(a.down) == 0) and isinstance(a, zqh_tilelink_node_slave_parameter):
            for i in a.imp.io.tl_to:
                i.a.ready /= 1
                i.d.valid /= 0
                if (i.p.tl_type == 'tl_c'):
                    i.c.ready /= 1
                    i.e.ready /= 1
                    i.b.valid /= 0
        elif (len(a.down) == 0) and isinstance(a, zqh_axi4_node_slave_parameter):
            for i in a.imp.io.tl_to:
                i.aw.ready /= 1
                i.w.ready /= 1
                i.ar.ready /= 1
                i.b.valid /= 0
                i.r.valid /= 0
        for i in range(len(a.down)):
            if (isinstance(a.down[i], bundle)):
                a.down[i] /= a.imp.io.tl_to[i]
                if (isinstance(a.down[i], zqh_tilelink_node_base_parameter)):
                    assert(
                        a.down[i].a.bits.source.get_w() == 
                        a.imp.io.tl_to[i].a.bits.source.get_w())
                    assert(
                        a.down[i].d.bits.sink.get_w() == 
                        a.imp.io.tl_to[i].d.bits.sink.get_w())
            else:
                idx = a.down[i].up.index(a)
                if (isinstance(a.down[i], (zqh_tilelink_node_slave_io_parameter))):
                    a.down[i].imp.io.tl_to[
                        a.down[i].imp.get_tl_to_id(a.down[i])] /= a.imp.io.tl_to[i]
                    assert(
                        a.down[i].imp.io.tl_to[
                            a.down[i].imp.get_tl_to_id(a.down[i])].a.bits.source.get_w() == 
                        a.imp.io.tl_to[i].a.bits.source.get_w())
                    assert(
                        a.down[i].imp.io.tl_to[
                            a.down[i].imp.get_tl_to_id(a.down[i])].d.bits.sink.get_w() == 
                        a.imp.io.tl_to[i].d.bits.sink.get_w())
                elif (isinstance(a.down[i], (zqh_axi4_node_slave_io_parameter))):
                    a.down[i].imp.io.axi4_to[
                        a.down[i].imp.get_tl_to_id(a.down[i])] /= a.imp.io.tl_to[i]
                elif (isinstance(a.down[i], (zqh_tilelink_node_master_io_parameter))):
                    a.down[i].imp.io.tl_from[
                        a.down[i].imp.get_tl_from_id(a.down[i])] /= a.imp.io.tl_to[i]
                    assert(
                        a.down[i].imp.io.tl_from[
                            a.down[i].imp.get_tl_from_id(
                                a.down[i])].a.bits.source.get_w() == 
                        a.imp.io.tl_to[i].a.bits.source.get_w())
                    assert(
                        a.down[i].imp.io.tl_from[
                            a.down[i].imp.get_tl_from_id(a.down[i])].d.bits.sink.get_w() == 
                        a.imp.io.tl_to[i].d.bits.sink.get_w())
                    if (a.address_mask is not None):
                        a.down[i].imp.io.tl_from[
                            a.down[i].imp.get_tl_from_id(a.down[i])].a.bits.address /= (
                                a.imp.io.tl_to[i].a.bits.address & 
                                a.address_mask)
                elif (isinstance(a.down[i], (zqh_axi4_node_master_io_parameter))):
                    a.down[i].imp.io.axi4_from[
                        a.down[i].imp.get_tl_from_id(a.down[i])] /= a.imp.io.tl_to[i]
                    if (a.address_mask is not None):
                        a.down[i].imp.io.axi4_from[
                            a.down[i].imp.get_tl_from_id(a.down[i])].aw.bits.address /= (
                                a.imp.io.tl_to[i].a.bits.address & 
                                a.address_mask)
                        a.down[i].imp.io.axi4_from[
                            a.down[i].imp.get_tl_from_id(a.down[i])].ar.bits.address /= (
                                a.imp.io.tl_to[i].a.bits.address & 
                                a.address_mask)
                else:
                    a.down[i].imp.io.tl_from[idx] /= a.imp.io.tl_to[i]
                    if (isinstance(a.down[i], zqh_tilelink_node_base_parameter)):
                        assert(
                            a.down[i].imp.io.tl_from[idx].a.bits.source.get_w() == 
                            a.imp.io.tl_to[i].a.bits.source.get_w())
                        assert(
                            a.down[i].imp.io.tl_from[idx].d.bits.sink.get_w() == 
                            a.imp.io.tl_to[i].d.bits.sink.get_w())
                    self.imp_connect_down(a.down[i])
