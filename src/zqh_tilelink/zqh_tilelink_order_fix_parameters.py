import sys
import os
from phgl_imp import *

class zqh_tilelink_order_fix_parameter(parameter):
    def set_par(self):
        super(zqh_tilelink_order_fix_parameter, self).set_par()

        #
        #none: don't keep any order
        #to any slave node's requsets can be issued mult-outstandings
        #
        #pos: same destnation pos slave node will matain it's own's order
        #to same pos slave node's requests can be issued mult-outstandings
        #
        #mem: only memory agent can keep it's access order(same address keep in order)
        #to memory agent slave node's requests can be issued mult-outstandings
        #
        #self: order fix node itself need matain all the access order
        #to memory agent's different address access can be issued mult-outstandings
        #
        #all: any request will be keeped in order
        #no mult-outstandings. the next requset must wait laste's response back
        #
        #order efferts: none < pos < mem < self < all
        self.par('order_mode', 'pos')
