import sys
import os
from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_bootrom_parameters import *
from .zqh_bootrom_bundles import *
from .zqh_bootrom_misc import *

class zqh_bootrom(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_bootrom, self).set_par()
        self.p = zqh_bootrom_parameter()

    def gen_node_tree(self):
        super(zqh_bootrom, self).gen_node_tree()
        self.gen_node_slave('bootrom_slave', tl_type = 'tl_uh')
        self.p.bootrom_slave.print_up()
        self.p.bootrom_slave.print_address_space()

    def set_port(self):
        super(zqh_bootrom, self).set_port()

    def main(self):
        super(zqh_bootrom, self).main()
        self.gen_node_interface('bootrom_slave')

        rom_map = zqh_bootrom_rom_data.get_rom_data(self.p.bootrom_file)
        rom_size_byte = len(rom_map)
        rom_data_bits = self.tl_in[0].d.bits.data.get_w()
        rom_data_bytes = rom_data_bits // 8

        rom_address = bits('rom_address', w = log2_ceil(rom_size_byte), init = 0)
        rom_data = bits('rom_data', w = rom_data_bits, init = 0)

        def func_rom_read(
            reg_ptr,
            fire,
            address,
            size,
            mask_bit,
            access_address = None,
            access_data = None):
            access_address /= address
            return (1, 1, access_data)
        self.cfg_reg(csr_reg_group(
            'rom_access', 
            offset = 0x0000, 
            size = rom_data_bytes, 
            mem_size = 2**log2_ceil(rom_size_byte), 
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = rom_data_bits, read = lambda a0, a1, a2, a3, a4: func_rom_read(a0, a1, a2, a3, a4, rom_address, rom_data))], comments = '''\
bootrom memory access.
can only be read. write will be dropped.'''))


        rom_mem = vec(
            'rom_mem', 
            gen = bits, 
            n = rom_size_byte//rom_data_bytes,
            w = rom_data_bits)
        for i in range(len(rom_mem)):
            rom_mem[i] /= cat_rvs(map(
                lambda _: value(_, w = 8),
                map(lambda _: _[1], rom_map[i*rom_data_bytes : (i+1)*rom_data_bytes])))
        rom_data /= rom_mem[rom_address >> log2_ceil(rom_data_bytes)]
