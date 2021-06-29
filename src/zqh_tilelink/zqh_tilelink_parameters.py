import sys
import os
from phgl_imp import *
from itertools import groupby

class zqh_tl_bundle_parameter(parameter):
    def set_par(self):
        super(zqh_tl_bundle_parameter, self).set_par()
        self.par('address_bits', 16)
        self.par('data_bits',    8)
        self.par('source_bits',  1)
        self.par('sink_bits',    1)
        self.par('size_bits',    2)

    def check_par(self):
        super(zqh_tl_bundle_parameter, self).check_par()
        assert(self.address_bits >= 1)
        assert(self.data_bits    >= 8)
        assert(self.source_bits  >= 1)
        assert(self.sink_bits    >= 1)
        assert(self.size_bits    >= 1)
        assert(is_pow_of_2(self.data_bits))

    def sync_all(self, a):
        self.address_bits = a.address_bits
        self.data_bits    = a.data_bits     
        self.source_bits  = a.source_bits   
        self.sink_bits    = a.sink_bits    
        self.size_bits    = a.size_bits    


class zqh_tl_bundle_all_channel_parameter(parameter):
    def set_par(self):
        super(zqh_tl_bundle_all_channel_parameter, self).set_par()
        self.par('channel', {})
        self.par('end_source_id', 1)
        self.par('end_sink_id',  1)
        self.par('tl_type', 'tl_uh')
        self.par('int_source_bits', 0)
        self.par('int_sink_bits', 0)

    def check_par(self):
        super(zqh_tl_bundle_all_channel_parameter, self).check_par()
        self.channel['a'] = zqh_tl_bundle_parameter(
            'a', 
            source_bits = log2_up(self.end_source_id),
            sink_bits = log2_up(self.end_sink_id))
        self.channel['b'] = zqh_tl_bundle_parameter('b')
        self.channel['c'] = zqh_tl_bundle_parameter('c')
        self.channel['d'] = zqh_tl_bundle_parameter(
            'd', 
            source_bits = log2_up(self.end_source_id), 
            sink_bits = log2_up(self.end_sink_id))
        self.channel['e'] = zqh_tl_bundle_parameter('e')

    def update_source_bits(self, tl_a, tl_c = None):
        self.channel['a'].source_bits = tl_a
        self.channel['b'].source_bits = tl_a
        if (tl_c is not None):
            self.channel['c'].source_bits = tl_c
        self.channel['d'].source_bits = tl_a
        self.channel['e'].source_bits = tl_a

    def update_sink_bits(self, a):
        self.channel['a'].sink_bits = a
        self.channel['b'].sink_bits = a
        self.channel['c'].sink_bits = a
        self.channel['d'].sink_bits = a
        self.channel['e'].sink_bits = a

    def update_bus_bits(self, data_bits, address_bits, size_bits):
        self.channel['a'].data_bits = data_bits
        self.channel['b'].data_bits = data_bits
        self.channel['c'].data_bits = data_bits
        self.channel['d'].data_bits = data_bits
        self.channel['e'].data_bits = data_bits

        self.channel['a'].address_bits = address_bits
        self.channel['b'].address_bits = address_bits
        self.channel['c'].address_bits = address_bits
        self.channel['d'].address_bits = address_bits
        self.channel['e'].address_bits = address_bits

        self.channel['a'].size_bits = size_bits
        self.channel['b'].size_bits = size_bits
        self.channel['c'].size_bits = size_bits
        self.channel['d'].size_bits = size_bits
        self.channel['e'].size_bits = size_bits

    def update_int_source_bits(self, a):
        self.int_source_bits = a

    def sync_source_bits(self, a):
        assert(isinstance(a, zqh_tl_bundle_all_channel_parameter))
        self.channel['a'].source_bits = a.channel['a'].source_bits
        self.channel['b'].source_bits = a.channel['b'].source_bits
        self.channel['c'].source_bits = a.channel['c'].source_bits
        self.channel['d'].source_bits = a.channel['d'].source_bits
        self.channel['e'].source_bits = a.channel['e'].source_bits

    def sync_sink_bits(self, a):
        assert(isinstance(a, zqh_tl_bundle_all_channel_parameter))
        self.channel['a'].sink_bits = a.channel['a'].sink_bits
        self.channel['b'].sink_bits = a.channel['b'].sink_bits
        self.channel['c'].sink_bits = a.channel['c'].sink_bits
        self.channel['d'].sink_bits = a.channel['d'].sink_bits
        self.channel['e'].sink_bits = a.channel['e'].sink_bits

    def sync_all(self, a):
        self.channel['a'].sync_all(a.channel['a'])
        self.channel['b'].sync_all(a.channel['b'])
        self.channel['c'].sync_all(a.channel['c'])
        self.channel['d'].sync_all(a.channel['d'])
        self.channel['e'].sync_all(a.channel['e'])
        self.end_source_id = a.end_source_id
        self.end_sink_id = a.end_sink_id
        self.tl_type = a.tl_type
        self.int_source_bits = a.int_source_bits
        self.int_sink_bits = a.int_sink_bits

class zqh_tl_manager_port_parameter(parameter):
    def set_par(self):
        super(zqh_tl_manager_port_parameter, self).set_par()
        self.par('slave_nodes',  [])
        self.par('beat_bytes',  8)
        self.par('end_sink_id',  1)

    def check_par(self):
        super(zqh_tl_manager_port_parameter, self).check_par()
        assert(is_pow_of_2(self.beat_bytes))
        assert(self.end_sink_id >= 0)

    def max_transfer(self):
        return max(list(map(lambda _: _.max_transfer(), self.slave_nodes)))

    def address_attr_filter(self, p):
        return list(filter(
            lambda _: p(_), 
            flatten(list(map(lambda _: _.address, self.slave_nodes)))))

    def address_attr_check(self, address, p):
        return reduce(
            lambda x,y: x | y, 
            list(map(lambda _: _.contains(address), self.address_attr_filter(p))))

class zqh_tl_interface_parameter(parameter):
    def set_par(self):
        super(zqh_tl_interface_parameter, self).set_par()
        self.par('manager', zqh_tl_manager_port_parameter('manager'))
        self.par('bundle', zqh_tl_bundle_all_channel_parameter('bundle'))

    def max_size_bits(self):
        return log2_ceil(self.manager.max_transfer())
    
class zqh_buffer_parameter(parameter):
    def set_par(self):
        super(zqh_buffer_parameter, self).set_par()
        self.par('depth', None)
        self.par('data_bypass', None)
        self.par('ready_bypass', None)

    @classmethod
    def default_p(self):
        tmp = zqh_buffer_parameter('default')
        tmp.depth = 2
        tmp.data_bypass = 0
        tmp.ready_bypass = 0
        return tmp

    @classmethod
    def normal_p(self, depth):
        tmp = zqh_buffer_parameter('normal')
        tmp.depth = depth
        tmp.data_bypass = 0
        tmp.ready_bypass = 0
        return tmp

    @classmethod
    def none_p(self):
        tmp = zqh_buffer_parameter('none')
        tmp.depth = 0
        tmp.data_bypass = 0
        tmp.ready_bypass = 0
        return tmp

    @classmethod
    def data_bypass_p(self):
        tmp = zqh_buffer_parameter()
        tmp.depth = 1
        tmp.data_bypass = 1
        tmp.ready_bypass = 0
        return tmp

    @classmethod
    def ready_bypass_p(self, depth):
        tmp = zqh_buffer_parameter()
        tmp.depth = depth
        tmp.data_bypass = 0
        tmp.ready_bypass = 1
        return tmp
