import sys
import os
from phgl_imp import *
from .zqh_tilelink_bundles import zqh_tl_bundle
from .zqh_tilelink_buffer import zqh_tl_buffer
from .zqh_tilelink_node_parameters import zqh_tilelink_node_base_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_base_parameter
from zqh_amba.zqh_axi4_bundles import zqh_axi4_all_channel_io
from zqh_amba.zqh_axi4_buffer import zqh_axi4_buffer

class zqh_tilelink_station(module):
    def set_par(self):
        super(zqh_tilelink_station, self).set_par()
        self.p.par('node', None)

    def set_port(self):
        super(zqh_tilelink_station, self).set_port()
        if (
            (len(self.p.node.up) > 0) and 
            isinstance(self.p.node.up[0], zqh_axi4_node_base_parameter)):
            self.io.var(vec(
                'tl_from',
                gen = lambda _: zqh_axi4_all_channel_io(
                    _,
                    p = self.p.node.up[0].bundle_out[_]),
                n = 1).flip())
        elif(isinstance(self.p.node, zqh_axi4_node_base_parameter)):
            self.io.var(vec(
                'tl_from', 
                gen = lambda _: zqh_axi4_all_channel_io(
                    _, 
                    p = self.p.node.bundle_in[_]),
                n = 1).flip())
        else:
            self.io.var(vec(
                'tl_from',
                gen = lambda _: zqh_tl_bundle(
                    _,
                    p = self.p.node.bundle_in[_]),
                n = 1).flip())

        if (
            (len(self.p.node.down) > 0) and 
            isinstance(self.p.node.down[0], zqh_axi4_node_base_parameter)):
            self.io.var(vec(
                'tl_to',
                gen = lambda _: zqh_axi4_all_channel_io(
                    _,
                    p = self.p.node.down[0].bundle_in[_]),
                n = 1))
        elif(isinstance(self.p.node, zqh_axi4_node_base_parameter)):
            self.io.var(vec(
                'tl_to', 
                gen = lambda _: zqh_axi4_all_channel_io(
                    _,
                    p = self.p.node.bundle_out[_]),
                n = 1))
        else:
            self.io.var(vec(
                'tl_to',
                gen = lambda _: zqh_tl_bundle(_, p = self.p.node.bundle_out[_]),
                n = 1))

    def main(self):
        super(zqh_tilelink_station, self).main()

        if (self.p.node.buffer_out is not None):
            if (isinstance(self.p.node, zqh_tilelink_node_base_parameter)):
                buffer = zqh_tl_buffer(
                    'buffer_out',
                    buf_p = self.p.node.buffer_out,
                    tl_p = self.p.node.bundle_out[0])
                buffer.io.tl_in /= self.io.tl_from[0]
                post_buffer_from = buffer.io.tl_out
            elif (isinstance(self.p.node, zqh_axi4_node_base_parameter)):
                buffer = zqh_axi4_buffer(
                    'buffer_out',
                    buf_p = self.p.node.buffer_out,
                    axi4_p = self.p.node.bundle_out[0])
                buffer.io.axi4_in /= self.io.tl_from[0]
                post_buffer_from = buffer.io.axi4_out
            else:
                assert(0)
        elif (self.p.node.buffer_in is not None):
            if (isinstance(self.p.node, zqh_tilelink_node_base_parameter)):
                buffer = zqh_tl_buffer(
                    'buffer_in',
                    buf_p = self.p.node.buffer_in, 
                    tl_p = self.p.node.bundle_in[0])
                buffer.io.tl_in /= self.io.tl_from[0]
                post_buffer_from = buffer.io.tl_out
            elif (isinstance(self.p.node, zqh_axi4_node_base_parameter)):
                buffer = zqh_axi4_buffer(
                    'buffer_in', 
                    buf_p = self.p.node.buffer_in,
                    axi4_p = self.p.node.bundle_in[0])
                buffer.io.axi4_in /= self.io.tl_from[0]
                post_buffer_from = buffer.io.axi4_out
            else:
                assert(0)
        else:
            post_buffer_from = self.io.tl_from[0]

        if (self.p.node.process is not None):
            tmp_in = post_buffer_from
            for j in range(len(self.p.node.process)):
                if (self.p.node.process[j] is None):
                    res = tmp_in
                else:
                    (func, args) = self.p.node.process[j]
                    res = func(self.p.node, tmp_in, args)
                tmp_in = res
            self.io.tl_to[0] /= res
        else:
            self.io.tl_to[0] /= post_buffer_from
