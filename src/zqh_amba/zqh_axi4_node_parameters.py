import sys
import os
from phgl_imp import *
from .zqh_axi4_parameters import zqh_axi4_all_channel_parameter
from zqh_common.zqh_bus_node_parameters import zqh_bus_node_base_parameter

class zqh_axi4_node_base_parameter(zqh_bus_node_base_parameter):
    def max_transfer(self):
        return self.transfer_sizes.max

    def push_down(self, a):
        self.down.append(a)
        if (isinstance(a, (zqh_axi4_node_base_parameter))):
            a.up.append(self)

    def push_up(self, a):
        self.up.append(a)
        if (isinstance(a, (zqh_axi4_node_base_parameter))):
            a.down.append(self)

class zqh_axi4_node_master_parameter(zqh_axi4_node_base_parameter):
    def set_par(self):
        super(zqh_axi4_node_master_parameter, self).set_par()
        self.par('bundle_out', [zqh_axi4_all_channel_parameter()])
        self.par('bundle_in', [zqh_axi4_all_channel_parameter()])

    def check_par(self):
        super(zqh_axi4_node_master_parameter, self).check_par()

        for i in range(len(self.bundle_out)):
            self.bundle_in[i].sync_all(self.bundle_out[i])

class zqh_axi4_node_master_io_parameter(zqh_axi4_node_master_parameter):
    pass

class zqh_axi4_node_slave_parameter(zqh_axi4_node_base_parameter):
    def set_par(self):
        super(zqh_axi4_node_slave_parameter, self).set_par()
        self.par('bundle_in', [zqh_axi4_all_channel_parameter()])
        self.par('bundle_out', [zqh_axi4_all_channel_parameter()])

    def check_par(self):
        super(zqh_axi4_node_slave_parameter, self).check_par()

        for i in range(len(self.bundle_in)):
            self.bundle_out[i].sync_all(self.bundle_in[i])

class zqh_axi4_node_slave_io_parameter(zqh_axi4_node_slave_parameter):
    pass
