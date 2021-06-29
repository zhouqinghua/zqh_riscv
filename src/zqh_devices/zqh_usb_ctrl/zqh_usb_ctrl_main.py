from phgl_imp import *
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_usb_ctrl_parameters import zqh_usb_ctrl_parameter
from .zqh_usb_ctrl_bundles import *
from zqh_usb_phy.zqh_usb_phy_common_bundles import zqh_usb_utmi_l1
from zqh_usb_phy.zqh_usb_phy_bundles import zqh_usb_phy_reg_io
from .zqh_usb_ctrl_utmi import zqh_usb_ctrl_utmi

class zqh_usb_ctrl(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_usb_ctrl, self).set_par()
        self.p = zqh_usb_ctrl_parameter()

    def gen_node_tree(self):
        super(zqh_usb_ctrl, self).gen_node_tree()
        self.gen_node_slave(
            'usb_ctrl_slave',
            tl_type = 'tl_uh', 
            bundle_p = self.p.gen_tl_bundle_p()) 
        self.p.usb_ctrl_slave.print_up()
        self.p.usb_ctrl_slave.print_address_space()

    def set_port(self):
        super(zqh_usb_ctrl, self).set_port()
        self.io.var(zqh_usb_phy_reg_io('phy_reg').flip())
        self.io.var(zqh_usb_utmi_l1('utmi', dw = 8).flip())

    def main(self):
        super(zqh_usb_ctrl, self).main()
        self.gen_node_interface('usb_ctrl_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        #{{{
        self.cfg_reg(csr_reg_group(
            'version', 
            offset = 0x0000, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('major', width = 4, reset = 1, access = 'RO', comments = '''\
Major revision number'''),
                csr_reg_field_desc('minor', width = 4, reset = 1, access = 'RO', comments = '''\
Minor revision number''')]))
        self.cfg_reg(csr_reg_group(
            'config', 
            offset = 0x0004, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('mode', width = 1, reset = 0, comments = '''\
Set to 1 to enable host mode. Set to 0 to enable slave mode.'''),
                csr_reg_field_desc('phy_reset', width = 1, reset = 1, comments = '''\
Set to 1 to reset utmi phy. Set to 0 to de-reset utmi phy.'''),
                csr_reg_field_desc('trans_en', width = 1, reset = 0, comments = '''\
transaction enable
Set to 1 to enable transmit/recieve transactions.''')]))

        #tmp host_tx_fifo_data_write = reg_r()
        #tmp host_tx_fifo_data_be = reg(w = 1)
        host_tx_fifo_data_write = bits(init = 0)
        host_tx_fifo_data_be = bits(init = 0)
        #tmp with when(host_tx_fifo_data_write):
        #tmp     host_tx_fifo_data_write /= 0
        def func_host_tx_fifo_data_write(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata
                tmp = host_tx_fifo_data_write
                tmp /= 1

                tmp1 = host_tx_fifo_data_be
                for i in range(host_tx_fifo_data_be.get_w()):
                    tmp1[i] /= mask_bit[i*8]
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'host_tx_fifo_data', 
            offset = 0x0008, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = 8, write = func_host_tx_fifo_data_write, comments = '''\
Prior to requesting an OUTDATA0_TRANS or an OUTDATA1_TRANS , load transmit fifo with data by writing to host_tx_fifo_data.''')]))
        self.cfg_reg(csr_reg_group(
            'host_tx_fifo_data_count', 
            offset = 0x000c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 16, reset = 0, access = 'VOL', comments = '''\
Indicates the number of data entries within the tx fifo.''')]))
        self.cfg_reg(csr_reg_group(
            'host_tx_fifo_control', 
            offset = 0x0010, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('fifo_force_empty', width = 1, reset = 0, comments = '''\
Set this bit to 1 will flush tx fifo.
Clear this bit to 0 will de-assert tx fifo's flush operation''')]))
        #tmp with when(self.regs['host_tx_fifo_control'].fifo_force_empty):
        #tmp     #only valid 1 cycle
        #tmp     self.regs['host_tx_fifo_control'].fifo_force_empty /= 0

        host_rx_fifo_data_read = bits(init = 0)
        def func_host_rx_fifo_data_read(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                tmp = host_rx_fifo_data_read
                tmp /= 1
            return (1, 1, reg_ptr)
        self.cfg_reg(csr_reg_group(
            'host_rx_fifo_data', 
            offset = 0x0014, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 8, reset = 0, access = 'VOL', read = func_host_rx_fifo_data_read, comments = '''\
If the last transaction was an IN_TRANS, then the receive payload can be retrieved by reading RX_FIFO_DATA.''')]))
        self.cfg_reg(csr_reg_group(
            'host_rx_fifo_data_count', 
            offset = 0x0018, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('data', width = 16, reset = 0, access = 'VOL', comments = '''\
Indicates the number of data entries within the rx fifo.''')]))
        self.cfg_reg(csr_reg_group(
            'host_rx_fifo_control', 
            offset = 0x001c, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('fifo_force_empty', width = 1, reset = 0, comments = '''\
Set this bit to 1 will flush rx fifo.
Clear this bit to 0 will de-assert rx fifo's flush operation.''')]))
        #tmp with when(self.regs['host_rx_fifo_control'].fifo_force_empty):
        #tmp     #only valid 1 cycle
        #tmp     self.regs['host_rx_fifo_control'].fifo_force_empty /= 0

        self.cfg_reg(csr_reg_group(
            'host_interrupt_status', 
            offset = 0x0020, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('sof_sent', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Automatically set to 1 when a SOF transmission occurs. Must be cleared by writing 1.'''),
                csr_reg_field_desc('discon_event', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Automatically set to 1 when a disconnect occurs. Must be cleared by writing 1.
                        '''),
                csr_reg_field_desc('con_event', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Automatically set to 1 when a connect occurs. Must be cleared by writing 1.'''),
                csr_reg_field_desc('resume', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Automatically set to 1 when resume state is detected. Must be cleared by writing 1.'''),
                csr_reg_field_desc('trans_done', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Automatically set to 1 when a transaction is completed. Must be cleared by writing 1.''')]))
        self.cfg_reg(csr_reg_group(
            'host_interrupt_en', 
            offset = 0x0024, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('sof_sent', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on SOF transmission.'''),
                csr_reg_field_desc('discon_event', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on disconnect event.'''),
                csr_reg_field_desc('con_event', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on connect event.'''),
                csr_reg_field_desc('resume', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on resume detected.'''),
                csr_reg_field_desc('trans_done', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on transaction completion.''')]))



        device_tx_fifo_data_write_array = []
        device_tx_fifo_data_be_array = []
        device_tx_fifo_data_reg_array = []
        device_tx_fifo_data_count_reg_array = []
        device_tx_fifo_control_reg_array = []
        device_rx_fifo_data_read_array = []
        device_rx_fifo_data_reg_array = []
        device_rx_fifo_data_count_reg_array = []
        device_rx_fifo_control_reg_array = []
        def func_device_tx_fifo_data_write_ep0(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata
                tmp = device_tx_fifo_data_write_array[0]
                tmp /= 1

                tmp1 = device_tx_fifo_data_be
                for i in range(device_tx_fifo_data_be.get_w()):
                    tmp1[i] /= mask_bit[i*8]
            return (1, 1)
        def func_device_tx_fifo_data_write_ep1(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata
                tmp = device_tx_fifo_data_write_array[1]
                tmp /= 1

                tmp1 = device_tx_fifo_data_be
                for i in range(device_tx_fifo_data_be.get_w()):
                    tmp1[i] /= mask_bit[i*8]
            return (1, 1)
        def func_device_tx_fifo_data_write_ep2(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata
                tmp = device_tx_fifo_data_write_array[2]
                tmp /= 1

                tmp1 = device_tx_fifo_data_be
                for i in range(device_tx_fifo_data_be.get_w()):
                    tmp1[i] /= mask_bit[i*8]
            return (1, 1)
        def func_device_tx_fifo_data_write_ep3(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                reg_ptr /= wdata
                tmp = device_tx_fifo_data_write_array[3]
                tmp /= 1

                tmp1 = device_tx_fifo_data_be
                for i in range(device_tx_fifo_data_be.get_w()):
                    tmp1[i] /= mask_bit[i*8]
            return (1, 1)
        func_device_tx_fifo_data_write_array = [
            func_device_tx_fifo_data_write_ep0,
            func_device_tx_fifo_data_write_ep1,
            func_device_tx_fifo_data_write_ep2,
            func_device_tx_fifo_data_write_ep3]

        def func_device_rx_fifo_data_read_ep0(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                tmp = device_rx_fifo_data_read_array[0]
                tmp /= 1
            return (1, 1, reg_ptr)
        def func_device_rx_fifo_data_read_ep1(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                tmp = device_rx_fifo_data_read_array[1]
                tmp /= 1
            return (1, 1, reg_ptr)
        def func_device_rx_fifo_data_read_ep2(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                tmp = device_rx_fifo_data_read_array[2]
                tmp /= 1
            return (1, 1, reg_ptr)
        def func_device_rx_fifo_data_read_ep3(reg_ptr, fire, address, size, mask_bit):
            with when(fire):
                tmp = device_rx_fifo_data_read_array[3]
                tmp /= 1
            return (1, 1, reg_ptr)
        func_device_rx_fifo_data_read_array = [
            func_device_rx_fifo_data_read_ep0,
            func_device_rx_fifo_data_read_ep1,
            func_device_rx_fifo_data_read_ep2,
            func_device_rx_fifo_data_read_ep3]

        for i in range(self.p.device_ep_num):
            suffix_str = '_ep' + str(i)
            addr_base = 0x100 + 32*i

            #tmp device_tx_fifo_data_write = reg_r()
            #tmp device_tx_fifo_data_be = reg(w = 1)
            #tmp with when(device_tx_fifo_data_write):
            #tmp     device_tx_fifo_data_write /= 0
            device_tx_fifo_data_write = bits(init = 0)
            device_tx_fifo_data_be = bits(init = 0)

            device_tx_fifo_data_write_array.append(device_tx_fifo_data_write)
            #tmp def func_device_tx_fifo_data_write(reg_ptr, fire, address, size, wdata, mask_bit):
            #tmp     with when(fire):
            #tmp         reg_ptr /= wdata
            #tmp         tmp = device_tx_fifo_data_write
            #tmp         tmp /= 1

            #tmp         tmp1 = device_tx_fifo_data_be
            #tmp         for i in range(device_tx_fifo_data_be.get_w()):
            #tmp             tmp1[i] /= mask_bit[i*8]
            #tmp     return (1, 1)
            device_tx_fifo_data_reg = self.cfg_reg(csr_reg_group(
                'device_tx_fifo_data'+suffix_str, 
                offset = 0x0000+addr_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('data', access = 'VOL', width = 8, write = func_device_tx_fifo_data_write_array[i])], comments = '''\
Prior to receiving a IN_TRANS, load transmit fifo with data by writing to device_tx_fifo_data
                            '''))
            device_tx_fifo_data_count_reg = self.cfg_reg(csr_reg_group(
                'device_tx_fifo_data_count'+suffix_str, 
                offset = 0x0004+addr_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('data', width = 16, reset = 0, access = 'VOL', comments = '''\
Indicates the number of data entries within the tx fifo.''')]))
            device_tx_fifo_control_reg = self.cfg_reg(csr_reg_group(
                'device_tx_fifo_control'+suffix_str, 
                offset = 0x0008+addr_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('fifo_force_empty', width = 1, reset = 0, comments = '''\
Set this bit to 1 will flush tx fifo.
Clear this bit to 0 will de-assert tx fifo's flush operation.''')]))
            #tmp with when(device_tx_fifo_control_reg.fifo_force_empty):
            #tmp     #only valid 1 cycle
            #tmp     device_tx_fifo_control_reg.fifo_force_empty /= 0

            device_rx_fifo_data_read = bits(init = 0)
            device_rx_fifo_data_read_array.append(device_rx_fifo_data_read)
            #tmp def func_device_rx_fifo_data_read(reg_ptr, fire, address, size, mask_bit):
            #tmp     with when(fire):
            #tmp         tmp = device_rx_fifo_data_read
            #tmp         tmp /= 1
            #tmp     return (1, 1, reg_ptr)
            device_rx_fifo_data_reg = self.cfg_reg(csr_reg_group(
                'device_rx_fifo_data'+suffix_str, 
                offset = 0x000c+addr_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('data', width = 8, reset = 0, access = 'VOL', read = func_device_rx_fifo_data_read_array[i], comments = '''\
After receiving an OUTDATA_TRANS, or a SETUP_TRANS, get receive data from fifo by reading from RX_FIFO_DATA.''')]))
            device_rx_fifo_data_count_reg = self.cfg_reg(csr_reg_group(
                'device_rx_fifo_data_count'+suffix_str, 
                offset = 0x0010+addr_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('data', width = 16, reset = 0, access = 'VOL', comments = '''\
Indicates the number of data samples within the fifo.''')]))
            device_rx_fifo_control_reg = self.cfg_reg(csr_reg_group(
                'device_rx_fifo_control'+suffix_str, 
                offset = 0x0014+addr_base, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('fifo_force_empty', width = 1, reset = 0, comments = '''\
Set this bit to 1 will flush rx fifo.
Clear this bit to 0 will de-assert rx fifo's flush operation.''')]))
            #tmp with when(device_rx_fifo_control_reg.fifo_force_empty):
            #tmp     #only valid 1 cycle
            #tmp     device_rx_fifo_control_reg.fifo_force_empty /= 0

            device_tx_fifo_data_be_array.append(device_tx_fifo_data_be)
            device_tx_fifo_data_reg_array.append(device_tx_fifo_data_reg)
            device_tx_fifo_data_count_reg_array.append(device_tx_fifo_data_count_reg)
            device_tx_fifo_control_reg_array.append(device_tx_fifo_control_reg)
            device_rx_fifo_data_reg_array.append(device_rx_fifo_data_reg)
            device_rx_fifo_data_count_reg_array.append(device_rx_fifo_data_count_reg)
            device_rx_fifo_control_reg_array.append(device_rx_fifo_control_reg)


        self.cfg_reg(csr_reg_group(
            'device_interrupt_status', 
            offset = 0x0180, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('vbus_det', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Set to 1 when a change VBUS presence is detected. Must be cleared by writing 1.'''),
                csr_reg_field_desc('stall_sent', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Set to 1 when a stall sent. Must be cleared by writing 1.'''),
                csr_reg_field_desc('nak_sent', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Set to 1 when a NAK sent. Must be cleared by writing 1.'''),
                csr_reg_field_desc('sof_recv', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Set to 1 when a SOF packet is received. Must be cleared by writing 1.'''),
                csr_reg_field_desc('reset_event', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Set to 1 when a change in reset state (D+ and D- low) is detected. ie either entered or left reset state. Must be cleared by writing 1.'''),
                csr_reg_field_desc('resume', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Set to 1 when resume state is detected.  Must be cleared by writing 1.'''),
                csr_reg_field_desc('trans_done', wr_action = 'ONE_TO_CLEAR', width = 1, reset = 0, comments = '''\
Set to 1 when a transaction is completed. Must be cleared by writing 1.''')]))
        self.cfg_reg(csr_reg_group(
            'device_interrupt_en', 
            offset = 0x0184, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('vbus_det', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on VBUS detected.'''),
                csr_reg_field_desc('stall_sent', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on stall transaction.'''),
                csr_reg_field_desc('nak_sent', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on NAK'd transaction.'''),
                csr_reg_field_desc('sof_recv', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on SOF received.'''),
                csr_reg_field_desc('reset_event', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on reset detected.'''),
                csr_reg_field_desc('resume', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on resume detected.'''),
                csr_reg_field_desc('trans_done', width = 1, reset = 0, comments = '''\
Set to 1 to enable interrupt on transaction complete.''')]))





        cfg_mem_address  = bits('cfg_mem_address', w = 32, init = 0)
        cfg_mem_wr_mask  = bits('cfg_mem_wr_mask', w = 4, init = 0)
        def func_reg_write(reg_ptr, fire, address, size, wdata, mask_bit,
            wr_valid = None, wr_data = None, access_address = None, wr_mask = None,
            req_ready = None, resp_valid = None):
            with when(fire):
                wr_valid /= 1
                access_address /= address
            wr_data /= wdata
            wr_mask /= cat_rvs(map(lambda _: mask_bit[_*8], range(wr_mask.get_w())))
            return (req_ready, resp_valid)
        def func_reg_read(reg_ptr, fire, address, size, mask_bit,
            rd_valid = None, rd_data = None, access_address = None,
            req_ready = None, resp_valid = None):
            with when(fire):
                rd_valid /= 1
                access_address /= address
            return (req_ready, resp_valid, rd_data.pack())
        def wr_process_gen(wr_valid, wr_data, req_ready, resp_valid):
            return lambda a0, a1, a2, a3, a4, a5: func_reg_write(
                a0, a1, a2, a3, a4, a5,
                wr_valid, wr_data, cfg_mem_address, cfg_mem_wr_mask, req_ready, resp_valid)
        def rd_process_gen(rd_valid, rd_data, req_ready, resp_valid):
            return lambda a0, a1, a2, a3, a4: func_reg_read(
                a0, a1, a2, a3, a4,
                rd_valid, rd_data, cfg_mem_address, req_ready, resp_valid)

        #utmi cfg reg space: 0x0200 - 0x03ff
        utmi_cfg_mem_wr_valid   = bits('utmi_cfg_mem_wr_valid', init = 0)
        utmi_cfg_mem_wr_data    = bits('utmi_cfg_mem_wr_data', w = 32, init = 0)
        utmi_cfg_mem_rd_valid   = bits('utmi_cfg_mem_rd_valid', init = 0)
        utmi_cfg_mem_rd_data    = bits('utmi_cfg_mem_rd_data', w = 32, init = 0)
        utmi_cfg_mem_req_ready  = bits('utmi_cfg_mem_req_ready', init = 1)
        utmi_cfg_mem_resp_valid = bits('utmi_cfg_mem_resp_valid', init = 0)
        self.cfg_reg(csr_reg_group(
            'utmi_cfg_mem',
            offset = 0x0200,
            size = 4,
            mem_size = 2**9,
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = 32,
                    write = wr_process_gen(
                        utmi_cfg_mem_wr_valid,
                        utmi_cfg_mem_wr_data,
                        utmi_cfg_mem_req_ready,
                        utmi_cfg_mem_resp_valid),
                    read = rd_process_gen(
                        utmi_cfg_mem_rd_valid,
                        utmi_cfg_mem_rd_data,
                        utmi_cfg_mem_req_ready,
                        utmi_cfg_mem_resp_valid))], comments = '''\
utmi configure space.'''))

        #phy cfg reg space: 0x0400 - 0x04ff
        phy_cfg_mem_wr_valid = bits('phy_cfg_mem_wr_valid', init = 0)
        phy_cfg_mem_wr_data  = bits('phy_cfg_mem_wr_data', w = 32, init = 0)
        phy_cfg_mem_rd_valid = bits('phy_cfg_mem_rd_valid', init = 0)
        phy_cfg_mem_rd_data  = bits('phy_cfg_mem_rd_data', w = 32, init = 0)
        phy_cfg_mem_req_ready = bits('phy_cfg_mem_req_ready', init = 1)
        phy_cfg_mem_resp_valid = bits('phy_cfg_mem_resp_valid', init = 0)
        self.cfg_reg(csr_reg_group(
            'phy_cfg_mem',
            offset = 0x0400,
            size = 4,
            mem_size = 2**8,
            fields_desc = [
                csr_reg_field_desc('data', access = 'VOL', width = 32,
                    write = wr_process_gen(
                        phy_cfg_mem_wr_valid,
                        phy_cfg_mem_wr_data,
                        phy_cfg_mem_req_ready,
                        phy_cfg_mem_resp_valid),
                    read = rd_process_gen(
                        phy_cfg_mem_rd_valid,
                        phy_cfg_mem_rd_data,
                        phy_cfg_mem_req_ready,
                        phy_cfg_mem_resp_valid))], comments = '''\
PHY configure space.'''))

        #}}}

        utmi_md = zqh_usb_ctrl_utmi('utmi_md')
        utmi_md.io.clock /= self.io.utmi.CLK
        utmi_md.io.reset /= self.io.utmi.Reset
        utmi_md.io.utmi /= self.io.utmi
        utmi_md.io.cfg_mode /= async_dff(self.regs['config'].mode, self.p.sync_delay, clock = self.io.utmi.CLK)
        utmi_md.io.cfg_trans_en /= async_dff(self.regs['config'].trans_en, self.p.sync_delay, clock = self.io.utmi.CLK)

        #utmi_md reg access
        utmi_reg_req_fifo = async_ready_valid(
            'utmi_reg_req_fifo',
            gen = csr_reg_req,
            gen_p = utmi_md.io.reg.p)
        utmi_reg_req_fifo.io.enq_clock /= self.io.clock
        utmi_reg_req_fifo.io.enq_reset /= self.io.reset
        utmi_reg_req_fifo.io.deq_clock /= self.io.utmi.CLK
        utmi_reg_req_fifo.io.deq_reset /= self.io.utmi.Reset
        utmi_reg_req_fifo.io.enq.valid /= utmi_cfg_mem_wr_valid | utmi_cfg_mem_rd_valid
        utmi_reg_req_fifo.io.enq.bits.write /= utmi_cfg_mem_wr_valid
        utmi_reg_req_fifo.io.enq.bits.addr /= cfg_mem_address
        utmi_reg_req_fifo.io.enq.bits.data /= utmi_cfg_mem_wr_data
        utmi_reg_req_fifo.io.enq.bits.be /= cfg_mem_wr_mask
        utmi_cfg_mem_req_ready /= utmi_reg_req_fifo.io.enq.ready
        utmi_md.io.reg.req /= utmi_reg_req_fifo.io.deq

        utmi_reg_resp_fifo = async_ready_valid(
            'utmi_reg_resp_fifo',
            gen = csr_reg_resp,
            gen_p = utmi_md.io.reg.p)
        utmi_reg_resp_fifo.io.enq_clock /= self.io.utmi.CLK
        utmi_reg_resp_fifo.io.enq_reset /= self.io.utmi.Reset
        utmi_reg_resp_fifo.io.deq_clock /= self.io.clock
        utmi_reg_resp_fifo.io.deq_reset /= self.io.reset
        utmi_reg_resp_fifo.io.deq.ready /= 1
        utmi_reg_resp_fifo.io.enq /= utmi_md.io.reg.resp
        utmi_cfg_mem_resp_valid /= utmi_reg_resp_fifo.io.deq.fire()
        utmi_cfg_mem_rd_data /= utmi_reg_resp_fifo.io.deq.bits.data


        #phy reg access
        phy_reg_req_fifo = async_ready_valid(
            'phy_reg_req_fifo',
            gen = type(self.io.phy_reg.req.bits),
            gen_p = self.io.phy_reg.req.bits.p)
        phy_reg_req_fifo.io.enq_clock /= self.io.clock
        phy_reg_req_fifo.io.enq_reset /= self.io.reset
        phy_reg_req_fifo.io.deq_clock /= self.io.utmi.CLK
        phy_reg_req_fifo.io.deq_reset /= self.io.utmi.Reset
        phy_reg_req_fifo.io.enq.valid /= phy_cfg_mem_wr_valid | phy_cfg_mem_rd_valid
        phy_reg_req_fifo.io.enq.bits.write /= phy_cfg_mem_wr_valid
        phy_reg_req_fifo.io.enq.bits.addr /= cfg_mem_address
        phy_reg_req_fifo.io.enq.bits.data /= phy_cfg_mem_wr_data
        phy_reg_req_fifo.io.enq.bits.be /= cfg_mem_wr_mask
        phy_cfg_mem_req_ready /= phy_reg_req_fifo.io.enq.ready
        self.io.phy_reg.req /= phy_reg_req_fifo.io.deq

        phy_reg_resp_fifo = async_ready_valid(
            'phy_reg_resp_fifo',
            gen = type(self.io.phy_reg.resp.bits),
            gen_p = self.io.phy_reg.resp.bits.p)
        phy_reg_resp_fifo.io.enq_clock /= self.io.utmi.CLK
        phy_reg_resp_fifo.io.enq_reset /= self.io.utmi.Reset
        phy_reg_resp_fifo.io.deq_clock /= self.io.clock
        phy_reg_resp_fifo.io.deq_reset /= self.io.reset
        phy_reg_resp_fifo.io.deq.ready /= 1
        phy_reg_resp_fifo.io.enq /= self.io.phy_reg.resp
        phy_cfg_mem_resp_valid /= phy_reg_resp_fifo.io.deq.fire()
        phy_cfg_mem_rd_data /= phy_reg_resp_fifo.io.deq.bits.data


        #host tx data fifo
        host_tx_data_fifo = queue(
            'host_tx_data_fifo',
            gen = lambda _: zqh_usb_ctrl_utmi_tx_data(_, dw = 8), 
            entries = 64,
            flush_en = 1)
        host_tx_data_fifo.io.enq.valid /= host_tx_fifo_data_write
        host_tx_data_fifo.io.enq.bits.data /= self.regs['host_tx_fifo_data'].data
        host_tx_data_fifo.io.enq.bits.be /= host_tx_fifo_data_be 
        host_tx_data_fifo.io.flush /= ~self.regs['config'].trans_en | self.regs['host_tx_fifo_control'].fifo_force_empty

        utmi_host_tx_sync_fifo = async_queue(
            'utmi_host_tx_sync_fifo',
            gen = lambda _: zqh_usb_ctrl_utmi_tx_data(_, dw = 8), 
            entries = 8,
            flush_en = 1)
        utmi_host_tx_sync_fifo.io.enq_clock /= self.io.clock
        utmi_host_tx_sync_fifo.io.enq_reset /= self.io.reset
        utmi_host_tx_sync_fifo.io.deq_clock /= self.io.utmi.CLK
        utmi_host_tx_sync_fifo.io.deq_reset /= self.io.utmi.Reset
        utmi_host_tx_sync_fifo.io.enq /= host_tx_data_fifo.io.deq
        utmi_host_tx_sync_fifo.io.flush /= ~self.regs['config'].trans_en | self.regs['host_tx_fifo_control'].fifo_force_empty
        utmi_md.io.host_data_tx /= utmi_host_tx_sync_fifo.io.deq

        self.regs['host_tx_fifo_data_count'].data /= host_tx_data_fifo.io.count + utmi_host_tx_sync_fifo.io.count


        #host rx data fifo
        utmi_rx_sync_fifo = async_queue(
            'utmi_rx_sync_fifo',
            gen = lambda _: zqh_usb_ctrl_utmi_rx_data(_, dw = 8), 
            entries = 8,
            flush_en = 1)
        utmi_rx_sync_fifo.io.enq_clock /= self.io.utmi.CLK
        utmi_rx_sync_fifo.io.enq_reset /= self.io.utmi.Reset
        utmi_rx_sync_fifo.io.deq_clock /= self.io.clock
        utmi_rx_sync_fifo.io.deq_reset /= self.io.reset
        utmi_rx_sync_fifo.io.enq /= utmi_md.io.data_rx
        utmi_rx_sync_fifo.io.flush /= ~self.regs['config'].trans_en | self.regs['host_rx_fifo_control'].fifo_force_empty
        utmi_rx_sync_fifo.io.deq.ready /= 0

        host_rx_data_fifo = queue(
            'host_rx_data_fifo',
            gen = lambda _: zqh_usb_ctrl_utmi_rx_data(_, dw = 8), 
            entries = 70,#1 byte pid + 64 byte payload + 2 byte crc + zero out pkt(1 byte pid + 2 byte crc)
            flush_en = 1)
        host_rx_data_fifo.io.enq.valid /= self.regs['config'].mode & utmi_rx_sync_fifo.io.deq.valid
        host_rx_data_fifo.io.enq.bits /= utmi_rx_sync_fifo.io.deq.bits
        with when(self.regs['config'].mode):
            utmi_rx_sync_fifo.io.deq.ready /= host_rx_data_fifo.io.enq.ready
        host_rx_data_fifo.io.flush /= ~self.regs['config'].trans_en | self.regs['host_rx_fifo_control'].fifo_force_empty
        self.regs['host_rx_fifo_data'].data /= host_rx_data_fifo.io.deq.bits.data
        host_rx_data_fifo.io.deq.ready /= host_rx_fifo_data_read
        self.regs['host_rx_fifo_data_count'].data /= host_rx_data_fifo.io.count


        for i in range(self.p.device_ep_num):
            #device tx data fifo
            device_tx_data_fifo = queue(
                'device_tx_data_fifo'+'_ep'+str(i),
                gen = lambda _: zqh_usb_ctrl_utmi_tx_data(_, dw = 8), 
                entries = 64,
                flush_en = 1)
            device_tx_data_fifo.io.enq.valid /= device_tx_fifo_data_write_array[i]
            device_tx_data_fifo.io.enq.bits.data /= device_tx_fifo_data_reg_array[i]
            device_tx_data_fifo.io.enq.bits.be /= device_tx_fifo_data_be_array[i]
            device_tx_data_fifo.io.flush /= ~self.regs['config'].trans_en | device_tx_fifo_control_reg_array[i].fifo_force_empty

            utmi_device_tx_sync_fifo = async_queue(
                'utmi_device_tx_sync_fifo'+'_ep'+str(i),
                gen = lambda _: zqh_usb_ctrl_utmi_tx_data(_, dw = 8), 
                entries = 8,
                flush_en = 1)
            utmi_device_tx_sync_fifo.io.enq_clock /= self.io.clock
            utmi_device_tx_sync_fifo.io.enq_reset /= self.io.reset
            utmi_device_tx_sync_fifo.io.deq_clock /= self.io.utmi.CLK
            utmi_device_tx_sync_fifo.io.deq_reset /= self.io.utmi.Reset
            utmi_device_tx_sync_fifo.io.enq /= device_tx_data_fifo.io.deq
            utmi_device_tx_sync_fifo.io.flush /= ~self.regs['config'].trans_en | device_tx_fifo_control_reg_array[i].fifo_force_empty
            utmi_md.io.device_data_tx[i] /= utmi_device_tx_sync_fifo.io.deq
            device_tx_fifo_data_count_reg_array[i].data /= device_tx_data_fifo.io.count + utmi_device_tx_sync_fifo.io.count




            #device rx data fifo
            device_rx_data_fifo = queue(
                'device_rx_data_fifo'+'_ep'+str(i),
                gen = lambda _: zqh_usb_ctrl_utmi_rx_data(_, dw = 8), 
                entries = 70,
                flush_en = 1)
            device_rx_data_fifo.io.enq.valid /= utmi_rx_sync_fifo.io.deq.valid & (utmi_rx_sync_fifo.io.deq.bits.ep == i)
            device_rx_data_fifo.io.enq.bits /= utmi_rx_sync_fifo.io.deq.bits
            with when(~self.regs['config'].mode):
                with when(utmi_rx_sync_fifo.io.deq.bits.ep == i):
                    utmi_rx_sync_fifo.io.deq.ready /= device_rx_data_fifo.io.enq.ready
            device_rx_data_fifo.io.flush /= ~self.regs['config'].trans_en | device_rx_fifo_control_reg_array[i].fifo_force_empty
            device_rx_fifo_data_reg_array[i].data /= device_rx_data_fifo.io.deq.bits.data
            device_rx_fifo_data_count_reg_array[i].data /= device_rx_data_fifo.io.count
            device_rx_data_fifo.io.deq.ready /= device_rx_fifo_data_read_array[i]




        self.io.utmi.Reset /= self.regs['config'].phy_reset


        #interrupt
        self.int_out[0] /= 0

        host_int_trans_done_sync = async_dff(utmi_md.io.host_int_trans_done, self.p.sync_delay)
        host_int_resume_sync     = async_dff(utmi_md.io.host_int_resume, self.p.sync_delay)
        host_int_con_event_sync  = async_dff(utmi_md.io.host_int_con_event, self.p.sync_delay)
        host_int_discon_event_sync  = async_dff(utmi_md.io.host_int_discon_event, self.p.sync_delay)
        host_int_sof_sent_sync   = async_dff(utmi_md.io.host_int_sof_sent, self.p.sync_delay)

        device_int_trans_done_sync  = async_dff(utmi_md.io.device_int_trans_done, self.p.sync_delay)
        device_int_resume_sync      = async_dff(utmi_md.io.device_int_resume, self.p.sync_delay)
        device_int_reset_event_sync = async_dff(utmi_md.io.device_int_reset_event, self.p.sync_delay)
        device_int_sof_recv_sync    = async_dff(utmi_md.io.device_int_sof_recv, self.p.sync_delay)
        device_int_nak_sent_sync    = async_dff(utmi_md.io.device_int_nak_sent, self.p.sync_delay)
        device_int_stall_sent_sync  = async_dff(utmi_md.io.device_int_stall_sent, self.p.sync_delay)
        device_int_vbus_det_sync    = async_dff(utmi_md.io.device_int_vbus_det, self.p.sync_delay)

        with when(self.regs['config'].mode):
            with when(l2h(host_int_trans_done_sync)):
                self.regs['host_interrupt_status'].trans_done /= 1
            with when(l2h(host_int_resume_sync)):
                self.regs['host_interrupt_status'].resume /= 1
            with when(l2h(host_int_con_event_sync)):
                self.regs['host_interrupt_status'].con_event /= 1
            with when(l2h(host_int_discon_event_sync)):
                self.regs['host_interrupt_status'].discon_event /= 1
            with when(l2h(host_int_sof_sent_sync)):
                self.regs['host_interrupt_status'].sof_sent /= 1

            self.int_out[0] /= (
                (self.regs['host_interrupt_status'].trans_done & self.regs['host_interrupt_en'].trans_done) | 
                (self.regs['host_interrupt_status'].resume & self.regs['host_interrupt_en'].resume) | 
                (self.regs['host_interrupt_status'].con_event & self.regs['host_interrupt_en'].con_event) | 
                (self.regs['host_interrupt_status'].sof_sent & self.regs['host_interrupt_en'].sof_sent))
        with other():
            with when(l2h(device_int_trans_done_sync)):
                self.regs['device_interrupt_status'].trans_done /= 1
            with when(l2h(device_int_resume_sync)):
                self.regs['device_interrupt_status'].resume /= 1
            with when(l2h(device_int_reset_event_sync)):
                self.regs['device_interrupt_status'].reset_event /= 1
            with when(l2h(device_int_sof_recv_sync)):
                self.regs['device_interrupt_status'].sof_recv /= 1
            with when(l2h(device_int_nak_sent_sync)):
                self.regs['device_interrupt_status'].nak_sent /= 1
            with when(l2h(device_int_stall_sent_sync)):
                self.regs['device_interrupt_status'].stall_sent /= 1
            with when(l2h(device_int_vbus_det_sync)):
                self.regs['device_interrupt_status'].vbus_det /= 1

            self.int_out[0] /= (
                (self.regs['device_interrupt_status'].trans_done & self.regs['device_interrupt_en'].trans_done) | 
                (self.regs['device_interrupt_status'].resume & self.regs['device_interrupt_en'].resume) | 
                (self.regs['device_interrupt_status'].reset_event & self.regs['device_interrupt_en'].reset_event) | 
                (self.regs['device_interrupt_status'].sof_recv & self.regs['device_interrupt_en'].sof_recv) | 
                (self.regs['device_interrupt_status'].nak_sent & self.regs['device_interrupt_en'].nak_sent) | 
                (self.regs['device_interrupt_status'].stall_sent & self.regs['device_interrupt_en'].stall_sent) | 
                (self.regs['device_interrupt_status'].vbus_det & self.regs['device_interrupt_en'].vbus_det))
