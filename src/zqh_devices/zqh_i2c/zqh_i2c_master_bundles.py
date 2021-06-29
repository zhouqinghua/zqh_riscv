import sys
import os
from phgl_imp import *

class zqh_i2c_master_io(bundle):
    def set_var(self):
        super(zqh_i2c_master_io, self).set_var()
        self.var(inout_pin_io('scl'))
        self.var(inout_pin_io('sda'))

class zqh_i2c_master_pad(bundle):
    def set_var(self):
        super(zqh_i2c_master_pad, self).set_var()
        self.var(inoutp('scl'))
        self.var(inoutp('sda'))

class zqh_i2c_master_command_bundle(bundle):
    def set_var(self):
        super(zqh_i2c_master_command_bundle, self).set_var()
        self.var(bits('ack'  ))
        self.var(bits('write'))
        self.var(bits('read' ))
        self.var(bits('stop' ))
        self.var(bits('start'))

    def start_pos(self):
        return 0

    def stop_pos(self):
        return 1

    def read_pos(self):
        return 2

    def write_pos(self):
        return 3

    def ack_pos(self):
        return 4

    def irqAck_pos(self):
        return 7


class zqh_i2c_master_status_bundle(bundle):
    def set_var(self):
        super(zqh_i2c_master_status_bundle, self).set_var()
        self.var(bits('trans_progress' ))
        self.var(bits('reserved', w = 3    ))
        self.var(bits('arb_lost'            ))
        self.var(bits('busy'               ))
        self.var(bits('recv_ack'        ))
