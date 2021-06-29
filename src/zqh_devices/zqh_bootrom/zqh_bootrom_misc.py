from phgl_imp import *

class zqh_bootrom_rom_data(object):

    rom_map = []

    @classmethod
    def get_rom_data(self, fn):
        if (zqh_bootrom_rom_data.rom_map == []):
            array = vhex_read(fn, fill = 1)
            if (len(array)%64 != 0):
                new_addr = array[-1][0] + 1
                for i in range(new_addr, (new_addr//64 + 1)*64):
                    array.append((i, 0))
            zqh_bootrom_rom_data.rom_map = array
        return zqh_bootrom_rom_data.rom_map
