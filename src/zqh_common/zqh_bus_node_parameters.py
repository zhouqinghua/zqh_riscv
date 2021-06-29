import sys
import os
from phgl_imp import *
from .zqh_address_space import zqh_address_space

class zqh_bus_node_base_parameter(parameter):
    def set_par(self):
        super(zqh_bus_node_base_parameter, self).set_par()
        self.par('up',[], no_cmp = 1)
        self.par('down',[], no_cmp = 1)
        self.par('address',[])
        self.par('transfer_sizes', None)
        self.par('bundle_in',[])
        self.par('bundle_out',[])
        self.par('buffer_in',None)
        self.par('buffer_out',None)
        self.par('imp',None, no_cmp = 1)
        self.par('do_imp',0)
        self.par('is_pos',0)
        self.par('process', None)
        self.par('address_mask', None)

        self.par('int_dest',[], no_cmp = 1)
        self.par('int_source',[], no_cmp = 1)

    def indent(self, n):
        tmp_str = ""
        for i in range(0,n):
            tmp_str += "  "
        return tmp_str

    def print_up(self, level = 0, log = 0):
        for i in range(len(self.up)):
            if (isinstance(self.up[i], zqh_bus_node_base_parameter)):
                if (self.up[i].address_mask is not None):
                    address_info = ', address_mask = 0x%08x' %(self.up[i].address_mask)
                else:
                    address_info = ''
                for j in range(len(self.up[i].address)):
                    address_info = address_info + ", base[%d] = 0x%08x mask[%d] = 0x%08x attr = %s" % (j, self.up[i].address[j].base, j, self.up[i].address[j].mask, self.up[i].address[j].attr)
                info = "%s%s up[%d]: %s%s" % (self.indent(level), self.name, i, self.up[i].name, address_info)
                info_log(info, log)
                self.up[i].print_up(level+1, log)

    def print_address_space(self, log = 0):
        #tmp info = '%s address_space:\n' %(self.name) + self.get_global_address_space().print_info()
        info = '%s address_space:\n' %(self.name)
        address_spaces = self.get_global_address_space()
        for i in address_spaces:
            info = info + i.print_info()
        info_log(info, log)


    def get_global_address_space(self):
        tmp_a = []
        for i in range(len(self.address)):
            (up_base, address_mask) = self.get_address_mask()
            if (address_mask is not None):
                global_base = self.address[i].base + up_base
            else:
                global_base = self.address[i].base
            address_space = zqh_address_space(
                base = global_base, 
                mask = self.address[i].mask, 
                attr = self.address[i].attr,
                order_type = self.address[i].order_type)
            #tmp return address_space
            tmp_a.append(address_space)
        if (len(tmp_a) != 0):
            return tmp_a

        for i in range(len(self.up)):
            if (isinstance(self.up[i], zqh_bus_node_base_parameter)):
                return self.up[i].get_global_address_space()

    def get_address_mask(self):
        if (self.address_mask is not None):
            address_space = self.up[0].get_global_address_space()[0]
            return (address_space.base, self.address_mask)
        else:
            if (len(self.up) == 0):
                return (0, None)
            for i in range(len(self.up)):
                if (isinstance(self.up[i], zqh_bus_node_base_parameter)):
                    return self.up[i].get_address_mask()
                else:
                    return (0, None)

    def address_match_any(self, a):
        if (len(self.down) == 0 or (isinstance(self, zqh_bus_node_base_parameter) and len(self.address) > 0)):
            return reduce(lambda x,y: x | y, list(map(lambda _: _.contains(a), self.address)))
        else:
            return reduce(lambda x,y: x | y, list(map(lambda _: _.address_match_any(a), self.down)))
