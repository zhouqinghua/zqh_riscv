import sys
import os
from phgl_imp import *
from .zqh_tilelink_parameters import zqh_tl_bundle_all_channel_parameter
from zqh_amba.zqh_axi4_node_parameters import zqh_axi4_node_base_parameter
from zqh_common.zqh_address_space import zqh_address_space
from zqh_common.zqh_bus_node_parameters import zqh_bus_node_base_parameter

class zqh_tilelink_node_base_parameter(zqh_bus_node_base_parameter):
    def set_par(self):
        super(zqh_tilelink_node_base_parameter, self).set_par()
        self.par('tl_type_in', [])
        self.par('tl_type_out', [])
        self.par('new_a_source_bits', 0)
        self.par('new_c_source_bits', 0)
        self.par('new_d_sink_bits', 0)
        self.par('source_id_num', 1)

    def max_transfer(self):
        return self.transfer_sizes.max

    def push_down(self, a, tl_type = 'tl_uh'):
        self.down.append(a)
        if (isinstance(a, (
            zqh_tilelink_node_base_parameter,
            zqh_axi4_node_base_parameter))):
            a.up.append(self)
            if (isinstance(self, zqh_tilelink_node_xbar_parameter)):
                if (isinstance(a, zqh_tilelink_node_slave_parameter)):
                    if (len(a.tl_type_in) > 0):
                        tl_type = a.tl_type_in[0]
                self.bundle_out.append(
                    zqh_tl_bundle_all_channel_parameter(tl_type = tl_type))
            if (isinstance(a, zqh_tilelink_node_xbar_parameter)):
                a.bundle_in.append(
                    zqh_tl_bundle_all_channel_parameter(tl_type = tl_type))

    def push_up(self, a, tl_type = 'tl_uh'):
        self.up.append(a)
        if (isinstance(a, (
            zqh_tilelink_node_base_parameter,
            zqh_axi4_node_base_parameter))):
            a.down.append(self)
            if (isinstance(self, zqh_tilelink_node_xbar_parameter)):
                if (isinstance(a, zqh_tilelink_node_master_parameter)):
                    if (len(a.tl_type_out) > 0):
                        tl_type = a.tl_type_out[0]
                if (isinstance(a, zqh_tilelink_node_slave_parameter)):
                    if (len(a.tl_type_in) > 0):
                        tl_type = a.tl_type_in[0]
                self.bundle_in.append(
                    zqh_tl_bundle_all_channel_parameter(tl_type = tl_type))
            if (isinstance(a, zqh_tilelink_node_xbar_parameter)):
                a.bundle_out.append(
                    zqh_tl_bundle_all_channel_parameter(tl_type = tl_type))

    def is_address_slave(self):
        return isinstance(self, zqh_tilelink_node_slave_parameter) and len(self.address) > 0

    def is_farest_address_slave(self):
        return self.is_address_slave() and self.is_pos

    def get_nearest_slave_nodes(self, ret_q = None):
        if (ret_q is None):
            push_q = []
        else:
            push_q = ret_q
        if (self.is_address_slave()):
            push_q.append(self)
        else:
            for i in self.down:
                if (i.is_address_slave()):
                    push_q.append(i)
                else:
                    i.get_nearest_slave_nodes(push_q)
        return push_q

    def get_farest_slave_nodes(self, ret_q = None):
        if (ret_q is None):
            push_q = []
        else:
            push_q = ret_q
        if (self.is_farest_address_slave()):
            push_q.append(self)
        else:
            for i in self.down:
                if (i.is_farest_address_slave()):
                    push_q.append(i)
                else:
                    i.get_farest_slave_nodes(push_q)
        return push_q

    def get_master_nodes(self, ret_q = None):
        if (ret_q is None):
            push_q = []
        else:
            push_q = ret_q
        if (
            isinstance(self, zqh_tilelink_node_master_parameter) and 
            (len(self.up) == 0 or isinstance(self.up[0], bundle))):
            push_q.append(self)
        else:
            for i in self.up:
                if (
                    isinstance(i, zqh_tilelink_node_master_parameter) and 
                    (len(self.up) == 0 or isinstance(self.up[0], bundle))):
                    push_q.append(i)
                else:
                    i.get_master_nodes(push_q)
        return push_q

    def get_up_master_slave_nodes(self, ret_q = None):
        if (ret_q is None):
            push_q = []
        else:
            push_q = ret_q

        for i in self.up:
            if (
                isinstance(i, (
                    zqh_tilelink_node_master_parameter,
                    zqh_tilelink_node_slave_parameter))):
                push_q.append(i)
                i.get_up_master_slave_nodes(push_q)
        return push_q

    def get_down_master_slave_nodes(self, ret_q = None):
        if (ret_q is None):
            push_q = []
        else:
            push_q = ret_q

        for i in self.down:
            if (isinstance(i, (
                zqh_tilelink_node_master_parameter, 
                zqh_tilelink_node_slave_parameter))):
                push_q.append(i)
                i.get_down_master_slave_nodes(push_q)
        return push_q

    def get_up_xbar_nodes(self, ret_q = None):
        if (ret_q is None):
            push_q = []
        else:
            push_q = ret_q

        for i in self.up:
            if (isinstance(i, zqh_tilelink_node_xbar_parameter)):
                push_q.append(i)
            else:
                i.get_up_xbar_nodes(push_q)
        return push_q

    def get_down_xbar_nodes(self, ret_q = None):
        if (ret_q is None):
            push_q = []
        else:
            push_q = ret_q

        for i in self.down:
            if (isinstance(i, zqh_tilelink_node_xbar_parameter)):
                push_q.append(i)
            elif (isinstance(i, zqh_tilelink_node_base_parameter)):
                i.get_down_xbar_nodes(push_q)
        return push_q

    def gen_source_bits(self):
        for i in self.down:
            if (not isinstance(i, (zqh_tilelink_node_base_parameter))):
                continue
            #down node's bundle_in copy from up level's
            for j in range(len(i.up)):
                for k in range(len(i.up[j].down)):
                    if (i.up[j].down[k] is i):
                        #print("gen_source_bits %s.bundle_in[%d] from %s.bundle_out[%d] = %d" % (i.name, j, i.up[j].name, k, i.up[j].bundle_out[k].channel['a'].source_bits))
                        i.bundle_in[j].sync_source_bits(i.up[j].bundle_out[k])
                        #print("%s.bundle_in[%d] = %d" % (i.name, j, i.bundle_in[j].channel['a'].source_bits))

            #update down node's bundle_out's source_bits according up ports number
            source_w_in_a_max = max(list(map(
                lambda _: _.channel['a'].source_bits, i.bundle_in)))
            source_w_out_a_add = log2_ceil(len(i.up))
            source_w_out_a = source_w_in_a_max + source_w_out_a_add + i.new_a_source_bits

            source_w_in_c_max = max(list(map(
                lambda _: _.channel['c'].source_bits, i.bundle_in)))
            source_w_out_c_add = log2_ceil(len(i.up))
            source_w_out_c = source_w_in_c_max + source_w_out_c_add + i.new_c_source_bits

            for j in range(len(i.bundle_out)):
                i.bundle_out[j].update_source_bits(source_w_out_a, source_w_out_c)
                #print("gen_source_bits %s.bundle_out[%d] = %d" % (i.name, j, source_w_out_a))

            i.gen_source_bits()

    def gen_sink_bits(self):
        for i in self.up:
            if (not isinstance(i, zqh_tilelink_node_base_parameter)):
                continue

            #up node's bundle_out copy from down level's
            for j in range(len(i.down)):
                for k in range(len(i.down[j].up)):
                    if (i.down[j].up[k] is i):
                        i.bundle_out[j].sync_sink_bits(i.down[j].bundle_in[k])

            #update up node's bundle_in's sink_bits according down ports number
            sink_w_out_d_max = max(list(map(
                lambda _: _.channel['d'].sink_bits, i.bundle_out)))
            sink_w_in_d_add = log2_ceil(len(i.down))
            sink_w_in_d = sink_w_out_d_max + sink_w_in_d_add + i.new_d_sink_bits

            for j in range(len(i.bundle_in)):
                i.bundle_in[j].update_sink_bits(sink_w_in_d)

            i.gen_sink_bits()

    def gen_up_bus_bits(self, data_bits, address_bits, size_bits):
        #print('%s gen_up_bus_bits data_bits %d' % (self.name, data_bits))
        #print('%s gen_up_bus_bits address_bits %d' % (self.name, address_bits))
        #print('%s gen_up_bus_bits size_bits %d' % (self.name, size_bits))
        min_data_bits = data_bits
        max_address_bits = address_bits
        max_size_bits = size_bits
        if (isinstance(self, zqh_tilelink_node_xbar_parameter)):
            #print('self_bus_nodes:')
            xbars = self.get_up_xbar_nodes()
            if (len(xbars) > 0):
                xbars_min_data_bits = min(list(map(
                    lambda _: _.down_bus_data_bits, xbars)))
                xbars_max_address_bits = max(list(map(
                    lambda _: _.down_bus_address_bits, xbars)))
                xbars_max_size_bits = max(list(map(
                    lambda _: _.down_bus_size_bits, xbars)))
                min_data_bits = min(xbars_min_data_bits, data_bits)
                max_address_bits = max(xbars_max_address_bits, address_bits)
                max_size_bits = max(xbars_max_size_bits, size_bits)

            self.up_bus_data_bits = min_data_bits
            self.up_bus_address_bits = max_address_bits
            self.up_bus_size_bits = max_size_bits
            self.update_up_bus_bits(min_data_bits, max_address_bits, max_size_bits)

        up_bus_nodes = self.get_up_master_slave_nodes()
        #print('up_bus_nodes:')
        #print(list(map(lambda _: _.name, up_bus_nodes)))
        for i in up_bus_nodes:
            i.update_bus_bits(min_data_bits, max_address_bits, max_size_bits)

    def gen_down_bus_bits(self, data_bits, address_bits, size_bits):
        #print('%s gen_down_bus_bits data_bits %d' % (self.name, data_bits))
        #print('%s gen_down_bus_bits address_bits %d' % (self.name, address_bits))
        #print('%s gen_down_bus_bits size_bits %d' % (self.name, size_bits))
        min_data_bits = data_bits
        max_address_bits = address_bits
        max_size_bits = size_bits
        if (isinstance(self, zqh_tilelink_node_xbar_parameter)):
            #print('self_bus_nodes:')
            xbars = self.get_down_xbar_nodes()
            if (len(xbars) > 0):
                xbars_min_data_bits = min(list(map(
                    lambda _: _.up_bus_data_bits, xbars)))
                xbars_max_address_bits = max(list(
                    map(lambda _: _.up_bus_address_bits, xbars)))
                xbars_max_size_bits = max(list(map(
                    lambda _: _.up_bus_size_bits, xbars)))
                min_data_bits = min(xbars_min_data_bits, data_bits)
                max_address_bits = max(xbars_max_address_bits, address_bits)
                max_size_bits = max(xbars_max_size_bits, size_bits)

            self.down_bus_data_bits = min_data_bits
            self.down_bus_address_bits = max_address_bits
            self.down_bus_size_bits = max_size_bits
            self.update_down_bus_bits(min_data_bits, max_address_bits, max_size_bits)

        down_bus_nodes = self.get_down_master_slave_nodes()
        #print('down_bus_nodes:')
        #print(list(map(lambda _: _.name, down_bus_nodes)))
        for i in down_bus_nodes:
            i.update_bus_bits(min_data_bits, max_address_bits, max_size_bits)

    def update_up_bus_bits(self, data_bits, address_bits, size_bits):
        for i in self.bundle_in:
            i.update_bus_bits(data_bits, address_bits, size_bits)

    def update_down_bus_bits(self, data_bits, address_bits, size_bits):
        for i in self.bundle_out:
            i.update_bus_bits(data_bits, address_bits, size_bits)

    def update_bus_bits(self, data_bits, address_bits, size_bits):
        self.update_up_bus_bits(data_bits, address_bits, size_bits)
        self.update_down_bus_bits(data_bits, address_bits, size_bits)

    def master2slave_source_base(self, slave):
        assert(isinstance(self, (zqh_tilelink_node_master_parameter)))
        s_b_source = 0

        ms_chain = []
        self.find_ms_source(self, self, slave, ms_chain)
        ms_chain_index = list(zip(ms_chain, self.find_sm_index(ms_chain)))
        for i in list(reversed(ms_chain_index)):
            max_up_w = max(list(map(
                lambda _: (
                    _.bundle_out[0].channel['a'].source_bits if (
                        isinstance(_, zqh_tilelink_node_base_parameter)) else 0),
                i[0].up))) if (len(i[0].up) > 0) else 0
            s_b_source = s_b_source + (i[1] << max_up_w)

        return s_b_source

    def find_ms_source(self, top, m, s, ret_q):
        for i in range(len(m.down)):
            if (m.down[i] is s):
                ret_q.append(m)
                self.find_ms_source(top, top, m, ret_q)
                return
            elif (s is top):
                return 
            elif (isinstance(m.down[i],zqh_tilelink_node_base_parameter)):
                self.find_ms_source(top, m.down[i], s, ret_q)

    def find_sm_index(self, ms_q):
        ret_q = []
        for i in range(len(ms_q) - 1):
            ret_q.append(index_is(ms_q[i].up, ms_q[i+1]))
        ret_q.append(0)
        return ret_q

    def get_root_masters(self):
        m_q = []
        if (
            isinstance(self, (zqh_tilelink_node_master_parameter)) and 
            (
                (len(self.up) == 0) or 
                (
                    (len(self.up) == 1) and not 
                    isinstance(self.up[0], (zqh_tilelink_node_base_parameter))))):
            m_q.append(self)
        else:
            for i in self.up:
                if (
                    isinstance(i, (zqh_tilelink_node_master_parameter)) and 
                    (
                        (len(i.up) == 0) or 
                        (
                            (len(i.up) == 1) and not 
                            isinstance(i.up[0], (zqh_tilelink_node_base_parameter))))):
                    m_q.append(i)
                else:
                    m_q.extend(i.get_root_masters())
        return m_q

class zqh_tilelink_node_master_parameter(zqh_tilelink_node_base_parameter):
    def set_par(self):
        super(zqh_tilelink_node_master_parameter, self).set_par()
        self.par('bundle_out', [zqh_tl_bundle_all_channel_parameter()])
        self.par('bundle_in', [zqh_tl_bundle_all_channel_parameter()])

    def check_par(self):
        super(zqh_tilelink_node_master_parameter, self).check_par()
        for i in range(len(self.tl_type_out)):
            self.bundle_out[i].tl_type = self.tl_type_out[i]
            
        for i in range(len(self.bundle_out)):
            self.bundle_in[i].sync_all(self.bundle_out[i])

class zqh_tilelink_node_master_io_parameter(zqh_tilelink_node_master_parameter):
    pass

class zqh_tilelink_node_slave_parameter(zqh_tilelink_node_base_parameter):
    def set_par(self):
        super(zqh_tilelink_node_slave_parameter, self).set_par()
        self.par('bundle_in', [zqh_tl_bundle_all_channel_parameter()])
        self.par('bundle_out', [zqh_tl_bundle_all_channel_parameter()])

    def check_par(self):
        super(zqh_tilelink_node_slave_parameter, self).check_par()
        for i in range(len(self.tl_type_in)):
            self.bundle_in[i].tl_type = self.tl_type_in[i]

        for i in range(len(self.bundle_in)):
            self.bundle_out[i].sync_all(self.bundle_in[i])

class zqh_tilelink_node_slave_io_parameter(zqh_tilelink_node_slave_parameter):
    pass

class zqh_tilelink_node_xbar_parameter(zqh_tilelink_node_base_parameter):
    def set_par(self):
        super(zqh_tilelink_node_xbar_parameter, self).set_par()
        self.par('up_bus_data_bits', 64)
        self.par('up_bus_address_bits', 32)
        self.par('up_bus_size_bits', 4)

        self.par('down_bus_data_bits', 64)
        self.par('down_bus_address_bits', 32)
        self.par('down_bus_size_bits', 4)

    def get_dw_fix_tl_p(self):
        if (self.down_bus_data_bits != self.up_bus_data_bits):
            fix_tl_p = list(map(lambda _:type(_)(), self.bundle_in))
            for i in range(len(fix_tl_p)):
                fix_tl_p[i].sync_all(self.bundle_in[i])
                fix_tl_p[i].update_bus_bits(
                    self.down_bus_data_bits,
                    self.down_bus_address_bits,
                    self.down_bus_size_bits)
            return fix_tl_p
        else:
            return self.bundle_in

class zqh_tilelink_int_xbar_parameter(parameter):
    def set_par(self):
        super(zqh_tilelink_int_xbar_parameter, self).set_par()
        self.par('up',[], no_cmp = 1)
        self.par('down',[], no_cmp = 1)
        self.par('int_wire',[], no_cmp = 1)

    def push_up(self, a):
        self.up.append(a)
        a.int_source.append(self)

    def push_down(self, a):
        self.down.append(a)
        a.int_dest.append(self)

    def print_local_id_map(self, log = 0):
        if (isinstance(self.up[0], zqh_tilelink_node_slave_parameter)):
            int_node = self.up[0].down[0]
        elif (isinstance(self.up[0], zqh_tilelink_node_master_parameter)):
            int_node = self.up[0].up[0]
        int_dest = int_node.imp

        int_id = 0;
        for i in range(len(self.int_wire)):
            if (self.int_wire[i][1] is not None):
                for j in range(len(self.int_wire[i][0])):
                    info_log(
                        '%s interrupt id map: %d -> %s' %(
                            int_dest.name, int_id+j, self.int_wire[i][1].imp.name),
                        log)
            int_id = int_id + len(self.int_wire[i][0])

    def print_global_id_map(self, log = 0):
        self.get_end_xbar().print_local_id_map(log)

    def get_end_xbar(self):
        if (isinstance(self.up[0], zqh_tilelink_node_slave_parameter)):
            int_node = self.up[0].down[0]
        elif (isinstance(self.up[0], zqh_tilelink_node_master_parameter)):
            int_node = self.up[0].up[0]
        int_dest = int_node.imp

        return self if (int_dest.p.is_int_sink) else int_dest.p.int_xbar.get_end_xbar()
