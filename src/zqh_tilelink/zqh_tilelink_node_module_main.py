import sys
import os
from phgl_imp import *
from .zqh_tilelink_node_module_parameters import *
from .zqh_tilelink_bundles import zqh_tl_bundle
from .zqh_tilelink_node_parameters import zqh_tilelink_node_base_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_master_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_master_io_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_slave_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_slave_io_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_node_xbar_parameter
from .zqh_tilelink_node_parameters import zqh_tilelink_int_xbar_parameter
from .zqh_tilelink_bus import zqh_tilelink_bus
from .zqh_tilelink_misc import TMSG_CONSTS
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_base_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_slave_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_master_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_slave_io_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_master_io_parameter
from zqh_amba.zqh_axi4_bundles import zqh_axi4_all_channel_io
from .zqh_tilelink_interfaces import zqh_tl_interface_out
from .zqh_tilelink_interfaces import zqh_tl_interface_in
from zqh_common.zqh_transfer_size import zqh_transfer_size

class zqh_tilelink_node_module(csr_module):
    def set_par(self):
        super(zqh_tilelink_node_module, self).set_par()
        self.p = zqh_tilelink_node_module_parameter('p')

    def check_par(self):
        super(zqh_tilelink_node_module, self).check_par()
        self.gen_node_tree()
        self.gen_source_bits()
        self.gen_sink_bits()
        self.gen_bus_bits()

    def gen_node_tree(self):
        pass

    def set_port(self):
        super(zqh_tilelink_node_module, self).set_port()

    def gen_node_master(
        self, name, size_min = 0, size_max = 1, 
        tl_type = None, bundle_p = None, process = None, source_id_num = 1, idx = 0):
        if (bundle_p is None):
            self.p.par(
                name,
                zqh_tilelink_node_master_parameter(
                    name,
                    tl_type_out = [] if (tl_type is None) else [tl_type],
                    transfer_sizes = zqh_transfer_size(min = 0,max = 64),
                    do_imp = 1,
                    process = process,
                    source_id_num = source_id_num))
            self.p.par(
                'extern_out_'+name,
                zqh_tilelink_node_slave_io_parameter(
                    'extern_out_'+name,
                    tl_type_in = [] if (tl_type is None) else [tl_type],
                    transfer_sizes = zqh_transfer_size(min = 0,max = 64)))
        else:
            self.p.par(
                name,
                zqh_tilelink_node_master_parameter(
                    name, 
                    tl_type_out = [] if (tl_type is None) else [tl_type],
                    transfer_sizes = zqh_transfer_size(min = 0,max = 64),
                    bundle_out = [bundle_p],
                    do_imp = 1,
                    process = process,
                    source_id_num = source_id_num))
            self.p.par(
                'extern_out_'+name, 
                zqh_tilelink_node_slave_io_parameter(
                    'extern_out_'+name, 
                    tl_type_in = [] if (tl_type is None) else [tl_type],
                    transfer_sizes = zqh_transfer_size(min = 0,max = 64),
                    bundle_in = [bundle_p]))
        self.p[name].push_down(self.p['extern_out_'+name])
        if (len(self.p.extern_masters) > 0):
            self.p['extern_out_'+name].push_down(self.p.extern_masters[idx])

    def gen_node_slave(
        self, name, tl_type = None, bundle_p = None,
        process = None, idx = 0):
        if (bundle_p is None):
            self.p.par(
                name,
                zqh_tilelink_node_slave_parameter(
                    name,
                    tl_type_in = [] if (tl_type is None) else [tl_type],
                    do_imp = 1))
            self.p.par(
                'extern_in_'+name,
                zqh_tilelink_node_master_io_parameter(
                    'extern_in_'+name, 
                    tl_type_out = [] if (tl_type is None) else [tl_type]))
        else:
            self.p.par(
                name, 
                zqh_tilelink_node_slave_parameter(
                    name, 
                    tl_type_in = [] if (tl_type is None) else [tl_type], 
                    bundle_in = [bundle_p], do_imp = 1))
            self.p.par(
                'extern_in_'+name, 
                zqh_tilelink_node_master_io_parameter(
                    'extern_in_'+name, 
                    tl_type_out = [] if (tl_type is None) else [tl_type],
                    bundle_out = [bundle_p]))
        self.p['extern_in_'+name].push_down(self.p[name])
        if (len(self.p.extern_slaves) > 0):
            self.p.extern_slaves[idx].push_down(self.p['extern_in_'+name])

    def gen_axi4_node_slave(self, name, bundle_p = None, process = None, idx = 0):
        self.p.par(name, zqh_axi4_node_slave_parameter(name, do_imp = 1))
        self.p.par('extern_in_'+name, zqh_axi4_node_master_io_parameter('extern_in_'+name))
        self.p['extern_in_'+name].push_down(self.p[name])
        if (len(self.p.extern_slaves) > 0):
            self.p.extern_slaves[idx].push_down(self.p['extern_in_'+name])

    def gen_source_bits(self):
        for i in self.p:
            if (isinstance(self.p[i], zqh_tilelink_node_master_parameter)):
                self.p[i].gen_source_bits()

        for i in self.p.extern_slaves:
            if (isinstance(i, zqh_tilelink_node_base_parameter)):
                i.gen_source_bits()

    def gen_sink_bits(self):
        for i in self.p:
            if (isinstance(self.p[i], zqh_tilelink_node_slave_parameter)):
                self.p[i].gen_sink_bits()

        for i in self.p.extern_masters:
            if (isinstance(i, zqh_tilelink_node_base_parameter)):
                i.gen_sink_bits()

    def gen_bus_bits(self):
        for i in self.p:
            if (isinstance(self.p[i], zqh_tilelink_node_xbar_parameter)):
                #print('gen_bus_bits for bus')
                self.p[i].gen_up_bus_bits(
                    self.p[i].up_bus_data_bits,
                    self.p[i].up_bus_address_bits,
                    self.p[i].up_bus_size_bits)
                self.p[i].gen_down_bus_bits(
                    self.p[i].down_bus_data_bits,
                    self.p[i].down_bus_address_bits,
                    self.p[i].down_bus_size_bits)
        for i in self.p.extern_masters:
            #print('gen_bus_bits for extern_masters')
            if (isinstance(i, zqh_tilelink_node_base_parameter)):
                i.gen_up_bus_bits(
                    i.bundle_in[0].channel['a'].data_bits,
                    i.bundle_in[0].channel['a'].address_bits, 
                    i.bundle_in[0].channel['a'].size_bits)
                i.gen_down_bus_bits(
                    i.bundle_out[0].channel['a'].data_bits, 
                    i.bundle_out[0].channel['a'].address_bits, 
                    i.bundle_out[0].channel['a'].size_bits)
        for i in self.p.extern_slaves:
            #print('gen_bus_bits for extern_slaves')
            if (isinstance(i, zqh_tilelink_node_base_parameter)):
                i.gen_up_bus_bits(
                    i.bundle_in[0].channel['a'].data_bits,
                    i.bundle_in[0].channel['a'].address_bits,
                    i.bundle_in[0].channel['a'].size_bits)
                i.gen_down_bus_bits(
                    i.bundle_out[0].channel['a'].data_bits, 
                    i.bundle_out[0].channel['a'].address_bits, 
                    i.bundle_out[0].channel['a'].size_bits)

    def get_tl_to_id(self, a):
        if (isinstance(a, zqh_axi4_node_slave_io_parameter)):
            tmp_q = list(filter(
                lambda _: isinstance(self.p[_], zqh_axi4_node_slave_io_parameter),
                self.p))
        else:
            tmp_q = list(filter(
                lambda _: isinstance(self.p[_], zqh_tilelink_node_slave_io_parameter),
                self.p))
        for i in range(len(tmp_q)):
            if (a is self.p[tmp_q[i]]):
                return i
        assert(0), "could not find tl_to id"

    def get_tl_from_id(self, a):
        if (isinstance(a, zqh_axi4_node_master_io_parameter)):
            tmp_q = list(filter(
                lambda _: isinstance(self.p[_], zqh_axi4_node_master_io_parameter),
                self.p))
        else:
            tmp_q = list(filter(
                lambda _: isinstance(self.p[_], zqh_tilelink_node_master_io_parameter),
                self.p))
        for i in range(len(tmp_q)):
            if (a is self.p[tmp_q[i]]):
                return i
        assert(0), "could not find tl_from id"

    def gen_tl_io(self):
        #tile link port
        tmp_q = list(filter(
            lambda _: isinstance(self.p[_], zqh_tilelink_node_slave_io_parameter),
            self.p))
        self.io.var(vec(
            'tl_to',
            gen = lambda _: zqh_tl_bundle(
                self.p[tmp_q[_]].name,
                p = self.p[tmp_q[_]].bundle_out[0]),
            n = len(tmp_q)))
        #axi4 port
        tmp_q = list(filter(
            lambda _: isinstance(self.p[_], zqh_axi4_node_slave_io_parameter),
            self.p))
        self.io.var(vec(
            'axi4_to',
            gen = lambda _: zqh_axi4_all_channel_io(
                self.p[tmp_q[_]].name,
                p = self.p[tmp_q[_]].bundle_out[0]),
            n = len(tmp_q)))

        #tile link port
        tmp_q = list(filter(
            lambda _: isinstance(self.p[_], zqh_tilelink_node_master_io_parameter),
            self.p))
        self.io.var(vec(
            'tl_from',
            gen = lambda _: zqh_tl_bundle(
                self.p[tmp_q[_]].name,
                p = self.p[tmp_q[_]].bundle_out[0]).flip(),
            n = len(tmp_q)))
        #axi4 port
        tmp_q = list(filter(
            lambda _: isinstance(self.p[_], zqh_axi4_node_master_io_parameter),
            self.p))
        self.io.var(vec(
            'axi4_from',
            gen = lambda _: zqh_axi4_all_channel_io(
                self.p[tmp_q[_]].name,
                p = self.p[tmp_q[_]].bundle_out[0]).flip(),
            n = len(tmp_q)))

        #interrupt port
        tmp_q = list(filter(
            lambda _: isinstance(self.p[_], zqh_tilelink_node_master_io_parameter),
            self.p))
        int_source_num = sum(list(map(
            lambda _: self.p[_].bundle_out[0].int_source_bits,
            tmp_q)))
        self.io.var(vec(
            'int_source', 
            gen = outp, 
            n = int_source_num if (len(tmp_q) > 0) else 0))
        int_sink_num = sum(list(map(
            lambda _: self.p[_].bundle_out[0].int_sink_bits,
            tmp_q)))
        self.io.var(vec(
            'int_sink', 
            gen = inp, 
            n = int_sink_num if (len(tmp_q) > 0) else 0))

    def gen_imp(self):
        do_imp_q = list(filter(
            lambda _: isinstance(
                self.p[_], 
                (
                    zqh_tilelink_node_base_parameter,
                    zqh_axi4_node_base_parameter)) and (self.p[_].do_imp == 1),
            self.p))
        for i in do_imp_q:
            zqh_tilelink_bus.imp_master_slave(self.p[i])
            zqh_tilelink_bus.imp_cross_bus(self.p[i])
            zqh_tilelink_bus.imp_connect(self.p[i])

    def gen_int_connect(self):
        if (len(self.io.int_source) > 0):
            self.io.int_source /= self.int_out[0]

        tmp_q = list(filter(
            lambda _: isinstance(self.p[_], zqh_tilelink_int_xbar_parameter), self.p))
        for i in tmp_q:
            for j in self.p[i].down:
                for ep in j.down:
                    if (ep.bundle_in[0].int_source_bits > 0):
                        int_path = 'int_from_'+j.name+'_to_'+self.p[i].up[0].name
                        int_from_to = vec(
                            int_path,
                            gen = bits,
                            n = ep.bundle_in[0].int_source_bits)
                        int_from_to /= ep.imp.io.int_source
                        self.int_from_to_connect(self.p[i], int_from_to, ep)

    def int_from_to_connect(self, int_xbar, int_from_to, ep):
        int_start = sum(list(map(lambda _:len(_[0]), int_xbar.int_wire)))
        int_xbar.int_wire.append((int_from_to, ep))

        if (isinstance(int_xbar.up[0], zqh_tilelink_node_slave_parameter)):
            int_node = int_xbar.up[0].down[0]
        elif (isinstance(int_xbar.up[0], zqh_tilelink_node_master_parameter)):
            int_node = int_xbar.up[0].up[0]

        int_dest = int_node.imp

        with module_update(int_dest):
            for k in range(len(int_from_to)):
                int_dest.io.var(inp('int_in_'+str(int_start+k)))
                if (int_dest.p.is_int_sink):
                    int_dest.int_vec[int_start+k] /= int_dest.io['int_in_'+str(int_start+k)]
                else:
                    new_int_xbar = int_dest.p.int_xbar
                    new_int_from_to = [int_dest.io['int_in_'+str(int_start+k)]]
                    self.int_from_to_connect(new_int_xbar, new_int_from_to, ep)
        for k in range(len(int_from_to)):
            int_dest.io['int_in_'+str(int_start+k)] /= int_from_to[k]


    def reg_req_data_width(self):
        return self.reg_if.a.bits.data.get_w()

    def reg_req_addr_width(self):
        return self.reg_if.a.bits.address.get_w()

    def reg_req(self):
        return self.reg_if.a

    def reg_req_is_wr(self, req_bits):
        return req_bits.opcode.match_any([
            TMSG_CONSTS.put_full_data(),
            TMSG_CONSTS.put_partial_data()])

    def reg_req_is_rd(self, req_bits):
        return req_bits.opcode == TMSG_CONSTS.get()

    def reg_req_addr(self, req_bits):
        return req_bits.address & self.p.address().mask

    def reg_req_data(self, req_bits):
        return req_bits.data

    def reg_req_be(self, req_bits):
        return req_bits.mask

    def reg_req_size(self, req_bits):
        return req_bits.size

    def reg_resp(self):
        return self.reg_if.d

    def gen_reg_resp_bits(self, req_bits, data):
        return mux(
                self.reg_req_is_wr(req_bits),
                self.interface_in[0].access_ack_a(req_bits),
                self.interface_in[0].access_ack_data_a(req_bits, data))

    def post_main(self):
        super(zqh_tilelink_node_module, self).post_main()
        self.gen_tl_io()
        self.gen_imp()
        self.gen_int_connect()

    def main(self):
        super(zqh_tilelink_node_module, self).main()
        self.tl_in = []
        self.interface_in = []
        self.int_out = []

    def gen_node_interface(self, name):
        if (isinstance(self.p[name], zqh_tilelink_node_master_parameter)):
            self.interface_out = zqh_tl_interface_out(
                'interface_out',
                slave_nodes = self.p[name].get_nearest_slave_nodes(),
                bundle = self.p[name].bundle_in[0])
            self.p[name].push_up(zqh_tl_bundle(
                'tl_out',
                p = self.p[name].bundle_in[0]).as_bits())
            self.tl_out = self.p[name].up[0]
            self.int_out.append(vec(
                'int_out_'+str(len(self.int_out)),
                gen = bits, 
                n = self.p[name].bundle_in[0].int_source_bits))
        elif (isinstance(self.p[name], zqh_tilelink_node_slave_parameter)):
            self.interface_in.append(zqh_tl_interface_in(
                'interface_in_'+str(len(self.interface_in)), 
                bundle = self.p[name].bundle_in[0]))
            self.p[name].push_down(zqh_tl_bundle(
                'tl_in_'+str(len(self.tl_in)),
                p = self.p[name].bundle_out[0]).as_bits())
            self.tl_in.append(self.p[name].down[0])
            self.int_out.append(vec(
                'int_out_'+str(len(self.int_out)),
                gen = bits, 
                n = self.p[name].bundle_out[0].int_source_bits))
            self.reg_if = self.tl_in[0]

    def gen_node_interrupt(self, name):
        self.int_out.append(vec(
            'int_out_'+str(len(self.int_out)),
            gen = bits,
            n = self.p[name].bundle_out[0].int_source_bits))

    def gen_axi4_node_interface(self, name):
        if (isinstance(self.p[name], zqh_axi4_node_master_parameter)):
            self.p[name].push_up(zqh_axi4_all_channel_io(
                'axi4_out',
                p = self.p[name].bundle_in[0]).as_bits())
            self.axi4_out = self.p[name].up[0]
        elif (isinstance(self.p[name], zqh_axi4_node_slave_parameter)):
            self.p[name].push_down(zqh_axi4_all_channel_io(
                'axi4_in',
                p = self.p[name].bundle_out[0]).as_bits())
            self.axi4_in = self.p[name].down[0]
