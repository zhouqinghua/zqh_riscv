from phgl_imp import *
from .zqh_ddr_phy_bundles import *
from .zqh_ddr_phy_parameters import *
from .zqh_ddr_phy_pad_ctrl import zqh_ddr_phy_pad_ctrl

class zqh_ddr_phy(csr_module):
    def set_par(self):
        super(zqh_ddr_phy, self).set_par()
        self.p = zqh_ddr_phy_parameter()

    def set_port(self):
        super(zqh_ddr_phy, self).set_port()
        self.io.var(inp('dll_clock_ref'))
        self.io.var(inp('dll_reset_por'))
        self.io.var(zqh_ddr_phy_reg_io('reg'))
        self.io.var(zqh_ddr_phy_dfi_io('dfi'))
        self.io.var(zqh_ddr_phy_dram_io('ddr', p = self.p))

    def main(self):
        super(zqh_ddr_phy, self).main()
        self.reg_if = self.io.reg

        #cfg_regs
        #{{{
        for i in range(self.p.slice_num):
            for j in range(8):
                reg_name = 'cfg_regs_'+str(8*i+j)
                reg_size = 4
                reg_offset = 0x20*i+ j*reg_size
                
                if (j == 0):
                    self.cfg_reg(csr_reg_group(
                        reg_name,
                        offset = reg_offset,
                        size = reg_size,
                        fields_desc = [
                            csr_reg_field_desc('data',  width = 32, reset = 0)]))
                elif (j == 1):
                    self.cfg_reg(csr_reg_group(
                        reg_name,
                        offset = reg_offset,
                        size = reg_size, 
                        fields_desc = [
                            csr_reg_field_desc('data',  width = 32, reset = 0)]))
                elif (j == 2):
                    self.cfg_reg(csr_reg_group(
                        reg_name, 
                        offset = reg_offset,
                        size = reg_size, 
                        fields_desc = [
                            csr_reg_field_desc('data',  width = 32, reset = 0)]))
                elif (j == 3):
                    self.cfg_reg(csr_reg_group(
                        reg_name, 
                        offset = reg_offset, 
                        size = reg_size, 
                        fields_desc = [
                            csr_reg_field_desc('tstctrl',  width = 6, reset = 0, comments = '''\
Defines the test control bits.'''),
                            csr_reg_field_desc('pwrdn',  width = 1, reset = 0, comments = '''\
 DLL Power-Down.'''),
                            csr_reg_field_desc('reserved1', width = 8, access = 'VOL'),
                            csr_reg_field_desc('reserved0', width = 8, access = 'VOL'),
                            csr_reg_field_desc('madj',  width = 8, reset = 0, comments = '''\
Defines the DLL master adjust bits''')]))
                elif (j == 4):
                    self.cfg_reg(csr_reg_group(
                        reg_name,
                        offset = reg_offset,
                        size = reg_size,
                        fields_desc = [
                            csr_reg_field_desc('adj_read_dq',  width = 8, reset = 0, comments = '''\
DLL slave adjust bits for write's dq.'''),
                            csr_reg_field_desc('adj_read_dqs',  width = 8, reset = 0, comments = '''\
DLL slave adjust bits for read's dqs.'''),
                            csr_reg_field_desc('adj_write_dq',  width = 8, reset = 0, comments = '''\
DLL slave adjust bits for write's dq.'''),
                            csr_reg_field_desc('adj_write_dqs',  width = 8, reset = 0, comments = '''\
DLL slave adjust bits for write's dqs.''')]))
                elif (j == 5):
                    self.cfg_reg(csr_reg_group(
                        reg_name, 
                        offset = reg_offset, 
                        size = reg_size, 
                        fields_desc = [
                            csr_reg_field_desc('data',  width = 32, reset = 0, access = 'RO')]))
                elif (j == 6):
                    self.cfg_reg(csr_reg_group(
                        reg_name,
                        offset = reg_offset,
                        size = reg_size,
                        fields_desc = [
                            csr_reg_field_desc('data', width = 1, access = 'VOL')]))
                elif (j == 7):
                    self.cfg_reg(csr_reg_group(
                        reg_name, 
                        offset = reg_offset, 
                        size = reg_size,
                        fields_desc = [
                            csr_reg_field_desc('data', width = 1, access = 'VOL')]))

        slice_cfg = []
        for i in range(self.p.slice_num):
            slice_cfg.append({})

            reg_name = 'cfg_regs_'+str(8*i+3)
            slice_cfg[i]['dll_master_ctrl_madj'] = self.regs[reg_name].madj
            
            reg_name = 'cfg_regs_'+str(8*i+4)
            slice_cfg[i]['dll_slave_ctrl_adj_read_dq'] = self.regs[reg_name].adj_read_dq
            slice_cfg[i]['dll_slave_ctrl_adj_read_dqs'] = self.regs[reg_name].adj_read_dqs
            slice_cfg[i]['dll_slave_ctrl_adj_write_dq'] = self.regs[reg_name].adj_write_dq
            slice_cfg[i]['dll_slave_ctrl_adj_write_dqs'] = self.regs[reg_name].adj_write_dqs


        for i in range(12):
            reg_name = 'cfg_regs_'+str(8*self.p.slice_num+i)
            reg_size = 4
            reg_offset = 0x20*self.p.slice_num+ i*reg_size
            
            if (i == 0):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size, fields_desc = [
                        csr_reg_field_desc('ddr3_mode', width = 1, reset = 0, comments = '''\
Enables the generation of the additional DQS pulse required for DDR3 controllers to serve as the “preamble” of the write DQS.
-- ’b0 = No action
-- ’b1 = Generate Pulse (DDR3 memories)'''),
                        csr_reg_field_desc('reserved0', width = 12, access = 'VOL')]))
            elif (i == 1):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset,
                    size = reg_size, 
                    fields_desc = [
                        csr_reg_field_desc('tsel_off_value_data', width = 2, reset = 0, comments = '''\
Termination select off value for the data'''),
                        csr_reg_field_desc('reserved4', width = 2, access = 'VOL'),
                        csr_reg_field_desc('tsel_rd_value_data', width = 2, reset = 0, comments = '''\
Termination select read value for the data'''),
                        csr_reg_field_desc('reserved3', width = 2, access = 'VOL'),
                        csr_reg_field_desc('tsel_off_value_dqs', width = 2, reset = 0, comments = '''\
Termination select off value for the data strobe'''),
                        csr_reg_field_desc('reserved2', width = 2, access = 'VOL'),
                        csr_reg_field_desc('tsel_rd_value_dqs', width = 2, reset = 0, comments = '''\
Termination select read value for the data strobe'''),
                        csr_reg_field_desc('reserved1', width = 2, access = 'VOL'),
                        csr_reg_field_desc('tsel_off_value_dm', width = 2, reset = 0, comments = '''\
Termination select off value for the data mask'''),
                        csr_reg_field_desc('reserved0', width = 2, access = 'VOL'),
                        csr_reg_field_desc('tsel_rd_value_dm', width = 2, reset = 0, comments = '''\
Termination select read value for the data mask''')], comments = '''\
Controls termination read and off values.'''))
            elif (i == 2):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset, 
                    size = reg_size, 
                    fields_desc = [
                        csr_reg_field_desc('dqs_pads',  width = 16, reset = 0, comments = '''\
DQS pads'''),
                        csr_reg_field_desc('dm_dq_pads',  width = 16, reset = 0, comments = '''\
DQ/DM pads''')], comments = '''\
Controls the pad drive parameters for the DQ, DM and DQS pads.'''))
            elif (i == 3):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset, 
                    size = reg_size, fields_desc = [
                        csr_reg_field_desc('clock_pads',  width = 16, reset = 0, comments = '''\
Clock pads'''),
                        csr_reg_field_desc('ac_pads',  width = 16, reset = 0, comments = '''\
Address/Control pads''')], comments = '''\
Controls the pad drive parameters for the address/control and clock pads.'''))
            elif (i == 4):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset, 
                    size = reg_size, fields_desc = [
                        csr_reg_field_desc('i_pads',  width = 16, reset = 0, comments = '''\
Input feedback pads'''),
                        csr_reg_field_desc('io_o_fdbk_pads',  width = 16, reset = 0, comments = '''\
Input/Output feedback and Output feedback pads''')], comments = '''\
Controls the pad drive parameters for the feedback pads.'''))
            elif (i == 5):
                self.cfg_reg(csr_reg_group(
                    reg_name,
                    offset = reg_offset,
                    size = reg_size,
                    fields_desc = [
                        csr_reg_field_desc('dqs_pads',  width = 16, reset = 0, comments = '''\
DQS pads'''),
                        csr_reg_field_desc('dm_dq_pads',  width = 16, reset = 0, comments = '''\
DQ/DM pads''')], comments = '''\
Controls the pad termination parameters for the DQ, DM and DQS pads'''))
            elif (i == 6):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset, 
                    size = reg_size, 
                    fields_desc = [
                        csr_reg_field_desc('clock_pads',  width = 16, reset = 0, comments = '''\
Clock pads'''),
                        csr_reg_field_desc('ac_pads',  width = 16, reset = 0, comments = '''\
Address/Control pads''')], comments = '''\
Controls the pad termination parameters for the address/control and clock pads.'''))
            elif (i == 7):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset, 
                    size = reg_size, 
                    fields_desc = [
                        csr_reg_field_desc('i_pads',  width = 16, reset = 0, comments = '''\
Input feedback pads'''),
                        csr_reg_field_desc('io_o_fdbk_pads',  width = 16, reset = 0, comments = '''\
Input/Output feedback and Output feedback pads''')], comments = '''\
Controls the pad termination parameters for the feedback pads.'''))
            elif (i == 8):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = 
                    reg_offset, 
                    size = reg_size, 
                    fields_desc = [
                        csr_reg_field_desc('pad_cal_pu_code',  width = 6, reset = 0),
                        csr_reg_field_desc('pad_cal_sample_wait',  width = 8, reset = 0),
                        csr_reg_field_desc('reserved0', width = 1, access = 'VOL'),
                        csr_reg_field_desc('pad_cal_ctrl_bits',  width = 5, reset = 0),
                        csr_reg_field_desc('pad_cal_ctrl_1',  width = 1, reset = 0),
                        csr_reg_field_desc('pad_cal_ctrl_0',  width = 1, reset = 0)], comments = '''\
Controls the pad control parameters for calibration block'''))
            elif (i == 9):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset, 
                    size = reg_size, 
                    fields_desc = [
                        csr_reg_field_desc('data',  width = 32, reset = 0, access = 'RO')]))
            elif (i == 10):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset, 
                    size = reg_size, 
                    fields_desc = [
                        csr_reg_field_desc('data',  width = 32, reset = 0)]))
            elif (i == 11):
                self.cfg_reg(csr_reg_group(
                    reg_name, 
                    offset = reg_offset, 
                    size = reg_size, 
                    fields_desc = [
                        csr_reg_field_desc('data',  width = 18, reset = 0)]))
        #}}}

        ####
        #dfi signal process
        dll_all_locked = bits('dll_all_locked', init = 0)
        self.io.dfi.status.init_complete /= 0
        with when(reg_r(next = self.io.dfi.status.init_start)):
            with when(reg_r(next = self.io.dfi.dll_rst_n)):
                with when(dll_all_locked):
                    self.io.dfi.status.init_complete /= 1
        self.io.dfi.training.rdlvl_resp /= 0
        self.io.dfi.training.rdlvl_mode /= 0
        self.io.dfi.training.rdlvl_req /= 0
        self.io.dfi.training.rdlvl_gate_mode /= 0
        self.io.dfi.training.rdlvl_gate_req /= 0
        self.io.dfi.training.wrlvl_mode /= 0
        self.io.dfi.training.wrlvl_resp /= 0
        self.io.dfi.training.wrlvl_req /= 0

        pad_ctrl = zqh_ddr_phy_pad_ctrl('pad_ctrl', slice_num = self.p.slice_num)

        #read dqs/dq delay
        #sample dq data at dqs's posedge/negedge
        #dqs should be delayed 1/4 cycle(90deg)
        if (self.p.imp_mode == 'fpga'):
            IDELAYCTRL_inst = IDELAYCTRL('IDELAYCTRL_inst')
            IDELAYCTRL_inst.io.REFCLK /= self.io.dll_clock_ref
            IDELAYCTRL_inst.io.RST /= async_dff(~self.io.dfi.dll_rst_n, 2)

        read_dqs_dll = list(map(
            lambda _:self.gen_dll(
                'read_dqs_dll_'+str(_),
                dw = pad_ctrl.io.port_ctrl.mem_dqs[_].get_w(), sp = 'CLOCK', num = 2),
            range(self.p.slice_num)))

        read_dqs_delay = list(map(
            lambda _:bits(
                'read_dqs_delay_'+str(_),
                w = pad_ctrl.io.port_ctrl.mem_dqs[_].get_w()),
            range(self.p.slice_num)))
        read_dq = list(map(
            lambda _:bits(
                'read_dq_'+str(_),
                w = pad_ctrl.io.port_ctrl.mem_data[_].get_w()),
            range(self.p.slice_num)))
        for i in range(self.p.slice_num):
            read_dqs_dll[i].io.clock_ref /= self.io.clock
            read_dqs_dll[i].io.dll_reset /= ~self.io.dfi.dll_rst_n
            read_dqs_dll[i].io.madj /= slice_cfg[i]['dll_master_ctrl_madj']
            read_dqs_dll[i].io.adj /= slice_cfg[i]['dll_slave_ctrl_adj_read_dqs']
            read_dqs_dll[i].io.data_in /= self.io.clock.rep(pad_ctrl.io.port_ctrl.mem_dqs[i].get_w()) #test use clock instead of dqs
            read_dqs_delay[i] /= read_dqs_dll[i].io.data_out
            read_dq[i] /= pad_ctrl.io.port_ctrl.mem_data[i]


        init_complete_done = reg_r('init_complete_done')
        with when(self.io.dfi.status.init_complete):
            init_complete_done /= 1
        with elsewhen(init_complete_done):
            with when(self.io.dfi.status.init_start):
                init_complete_done /= 0


        ####
        #pad_ctrl

        #address/control signals
        dfi_control_dly0 = self.io.dfi.control.clone(
            'dfi_control_dly0').as_reg(next = self.io.dfi.control)
        dfi_control_dly1 = self.io.dfi.control.clone(
            'dfi_control_dly1').as_reg(next = dfi_control_dly0)
        dfi_control_dly2 = self.io.dfi.control.clone(
            'dfi_control_dly2').as_reg(next = dfi_control_dly1, clock_edge = 'negedge')
        pad_ctrl.io.port_ctrl.mem_address /= dfi_control_dly2.address
        pad_ctrl.io.port_ctrl.mem_bank /= dfi_control_dly2.bank
        pad_ctrl.io.port_ctrl.mem_cas_n /= dfi_control_dly2.cas_n
        pad_ctrl.io.port_ctrl.mem_cke /= dfi_control_dly2.cke
        pad_ctrl.io.port_ctrl.mem_clk /= self.io.clock
        pad_ctrl.io.port_ctrl.mem_cs_n /= dfi_control_dly2.cs_n
        pad_ctrl.io.port_ctrl.mem_odt /= dfi_control_dly2.odt
        pad_ctrl.io.port_ctrl.mem_ras_n /= dfi_control_dly2.ras_n
        pad_ctrl.io.port_ctrl.mem_reset_n /= dfi_control_dly2.reset_n
        pad_ctrl.io.port_ctrl.mem_we_n /= dfi_control_dly2.we_n

        #write data signals
        slice_data_w = (self.io.dfi.wrdata.wrdata.get_w()//self.p.slice_num)//2
        dfi_wrdata_slice_group = self.io.dfi.wrdata.wrdata.grouped(
            self.io.dfi.wrdata.wrdata.get_w()//self.p.slice_num)
        dfi_wrdata_mask_slice_group = self.io.dfi.wrdata.wrdata_mask.grouped(
            self.io.dfi.wrdata.wrdata_mask.get_w()//self.p.slice_num)

        write_dq_clock_dll = list(map(
            lambda _:self.gen_dll('write_dq_clock_dll_'+str(_), dw = 1, sp = 'CLOCK', num = 2),
            range(self.p.slice_num)))

        write_dqs_clock_dll = list(map(
            lambda _:self.gen_dll('write_dqs_clock_dll_'+str(_), dw = 1, sp = 'CLOCK', num = 2),
            range(self.p.slice_num)))

        write_dq_clock_delay = vec('write_dq_clock_delay', gen = bits, n = self.p.slice_num)
        write_dqs_clock_delay = vec('write_dqs_clock_delay', gen = bits, n = self.p.slice_num)
        for i in range(self.p.slice_num):
            write_dq_clock_dll[i].io.clock_ref /= self.io.clock
            write_dq_clock_dll[i].io.dll_reset /= ~self.io.dfi.dll_rst_n
            write_dq_clock_dll[i].io.madj /= slice_cfg[i]['dll_master_ctrl_madj']
            write_dq_clock_dll[i].io.adj /= slice_cfg[i]['dll_slave_ctrl_adj_write_dq']
            write_dq_clock_dll[i].io.data_in /= self.io.clock
            write_dq_clock_delay[i] /= write_dq_clock_dll[i].io.data_out

            write_dqs_clock_dll[i].io.clock_ref /= self.io.clock
            write_dqs_clock_dll[i].io.dll_reset /= ~self.io.dfi.dll_rst_n
            write_dqs_clock_dll[i].io.madj /= slice_cfg[i]['dll_master_ctrl_madj']
            write_dqs_clock_dll[i].io.adj /= slice_cfg[i]['dll_slave_ctrl_adj_write_dqs']
            write_dqs_clock_dll[i].io.data_in /= self.io.clock
            write_dqs_clock_delay[i] /= write_dqs_clock_dll[i].io.data_out


        dfi_wrdata_slice_group_delay1 = list(map(
            lambda _: reg(
                'dfi_wrdata_slice_group_delay1_'+str(_),
                next = dfi_wrdata_slice_group[_],
                w = dfi_wrdata_slice_group[_].get_w()),
            range(self.p.slice_num)))
        dfi_wrdata_slice_group_delay2 = list(map(
            lambda _: reg(
                'dfi_wrdata_slice_group_delay2_'+str(_),
                next = dfi_wrdata_slice_group_delay1[_],
                w = dfi_wrdata_slice_group[_].get_w()),
            range(self.p.slice_num)))

        dfi_wrdata_mask_slice_group_delay1 = list(map(
            lambda _: reg(
                'dfi_wrdata_mask_slice_group_delay1_'+str(_),
                next = dfi_wrdata_mask_slice_group[_],
                w = dfi_wrdata_mask_slice_group[_].get_w()),
            range(self.p.slice_num)))
        dfi_wrdata_mask_slice_group_delay2 = list(map(
            lambda _: reg(
                'dfi_wrdata_mask_slice_group_delay2_'+str(_),
                next = dfi_wrdata_mask_slice_group_delay1[_],
                w = dfi_wrdata_mask_slice_group[_].get_w()),
            range(self.p.slice_num)))


        dfi_wrdata_en_delay1 = list(map(
            lambda _: reg_r(
                'dfi_wrdata_en_delay1_'+str(_),
                next = self.io.dfi.wrdata.wrdata_en[_]),
            range(self.p.slice_num)))
        dfi_wrdata_en_delay2 = list(map(
            lambda _: reg_r(
                'dfi_wrdata_en_delay2_'+str(_),
                next = dfi_wrdata_en_delay1[_]),
            range(self.p.slice_num)))
        dfi_wrdata_en_delay3 = list(map(
            lambda _: reg_r(
                'dfi_wrdata_en_delay3_'+str(_),
                next = dfi_wrdata_en_delay2[_]),
            range(self.p.slice_num)))

        for i in range(self.p.slice_num):
            dqs_oe_dll_pre = reg_r(
                'dqs_oe_dll_pre_'+str(i),
                clock_edge = 'negedge',
                next = dfi_wrdata_en_delay2[i] | dfi_wrdata_en_delay3[i])
            dqs_oe_dll_delayed = reg_r(
                'dqs_oe_dll_delayed_'+str(i),
                next = dqs_oe_dll_pre,
                clock = write_dqs_clock_delay[i])
            pad_ctrl.io.port_ctrl.dqs_oe[i] /= dqs_oe_dll_delayed


            write_dqs_oddr = oddr_sim(
                'write_dqs_oddr_'+str(i),
                w = pad_ctrl.io.port_ctrl.write_dqs[i].get_w(),
                imp_mode = self.p.imp_mode,
                DDR_CLK_EDGE = 'SAME_EDGE')
            write_dqs_oddr.io.C /= write_dqs_clock_delay[i]
            write_dqs_oddr.io.CE /= 1
            write_dqs_oddr.io.D1 /= (dfi_wrdata_en_delay2[i] | dfi_wrdata_en_delay3[i]).rep(pad_ctrl.io.port_ctrl.mem_dqs[i].get_w())
            write_dqs_oddr.io.D2 /= 0
            write_dqs_oddr.io.R /= self.io.reset
            write_dqs_oddr.io.S /= 0
            pad_ctrl.io.port_ctrl.write_dqs[i] /= write_dqs_oddr.io.Q


            data_oe_dll_delayed = reg_r(
                'data_oe_dll_delayed_'+str(i),
                clock = write_dq_clock_delay[i],
                clock_edge = 'negedge',
                next = dfi_wrdata_en_delay3[i])
            pad_ctrl.io.port_ctrl.data_oe[i] /= data_oe_dll_delayed


            data_out_oddr = oddr_sim(
                'data_out_oddr_'+str(i),
                w = slice_data_w,
                imp_mode = self.p.imp_mode,
                DDR_CLK_EDGE = 'SAME_EDGE')
            data_out_oddr.io.C /= ~write_dq_clock_delay[i] #half cycle earlier
            data_out_oddr.io.CE /= 1
            data_out_oddr.io.D1 /= dfi_wrdata_slice_group_delay2[i][slice_data_w - 1 : 0]
            data_out_oddr.io.D2 /= dfi_wrdata_slice_group_delay2[i][slice_data_w*2 - 1 : slice_data_w]
            data_out_oddr.io.R /= self.io.reset
            data_out_oddr.io.S /= 0
            pad_ctrl.io.port_ctrl.data_out[i] /= data_out_oddr.io.Q


            pad_ctrl.io.port_ctrl.dm_oe[i] /= 1

            dm_out_oddr = oddr_sim(
                'dm_out_oddr_'+str(i),
                w = pad_ctrl.io.port_ctrl.dm_out[i].get_w(),
                imp_mode = self.p.imp_mode,
                DDR_CLK_EDGE = 'SAME_EDGE')
            dm_out_oddr.io.C /= ~write_dq_clock_delay[i] #half cycle earlier
            dm_out_oddr.io.CE /= 1
            dm_out_oddr.io.D1 /= dfi_wrdata_mask_slice_group_delay2[i][pad_ctrl.io.port_ctrl.dm_out[i].get_w() - 1 : 0]
            dm_out_oddr.io.D2 /= dfi_wrdata_mask_slice_group_delay2[i][pad_ctrl.io.port_ctrl.dm_out[i].get_w()*2 - 1 : pad_ctrl.io.port_ctrl.dm_out[i].get_w()]
            dm_out_oddr.io.R /= self.io.reset
            dm_out_oddr.io.S /= 0
            pad_ctrl.io.port_ctrl.dm_out[i] /= dm_out_oddr.io.Q


        if (self.p.imp_mode == 'sim'):
            dll_all_locked /=reduce(
                lambda a,b:a&b, 
                list(map(
                    lambda _: _.io.lock, 
                        read_dqs_dll + 
                        write_dq_clock_dll)))
        elif (self.p.imp_mode == 'fpga'):
            dll_all_locked /= async_dff(IDELAYCTRL_inst.io.RDY, 2)
        else:
            assert(0)


        #read data signals
        dq_iddr_slice_group_p = []
        dq_iddr_slice_group_n = []
        for i in range(self.p.slice_num):
            byte_group_p = []
            byte_group_n = []
            for j in range(read_dqs_delay[i].get_w()):
                dq_iddr = iddr_sim('dq_iddr_'+str(i)+'_'+str(j), w = 8, DDR_CLK_EDGE = "SAME_EDGE_PIPELINED", imp_mode = self.p.imp_mode)
                dq_iddr.io.C /= read_dqs_delay[i][j]
                dq_iddr.io.CE /= 1
                dq_iddr.io.D /= read_dq[i][(j+1)*8 - 1 : j*8]
                dq_iddr.io.R /= self.io.reset
                dq_iddr.io.S /= 0
                byte_group_p.append(dq_iddr.io.Q1)
                byte_group_n.append(dq_iddr.io.Q2)
            dq_iddr_slice_group_p.append(cat_rvs(byte_group_p))
            dq_iddr_slice_group_n.append(cat_rvs(byte_group_n))

        dq_iddr_delay1_pn = list(map(
            lambda _:reg(
                'dq_iddr_delay1_pn_'+str(_),
                next = cat([
                    dq_iddr_slice_group_n[_],
                    dq_iddr_slice_group_p[_]]),
                w = slice_data_w * 2),
            range(self.p.slice_num)))
        dq_iddr_delay2_pn = list(map(
            lambda _:reg(
                'dq_iddr_delay2_pn_'+str(_),
                next = dq_iddr_delay1_pn[_],
                w = slice_data_w * 2),
            range(self.p.slice_num)))


        rddata_en_dly0 = reg_r(
            'rddata_en_dly0', 
            w = self.io.dfi.rddata.rddata_en.get_w(),
            next = self.io.dfi.rddata.rddata_en)
        rddata_en_dly1 = reg_r(
            'rddata_en_dly1', 
            w = self.io.dfi.rddata.rddata_en.get_w(), 
            next = rddata_en_dly0)
        rddata_en_dly2 = reg_r(
            'rddata_en_dly2', 
            w = self.io.dfi.rddata.rddata_en.get_w(),
            next = rddata_en_dly1)
        rddata_en_dly3 = reg_r(
            'rddata_en_dly3',
            w = self.io.dfi.rddata.rddata_en.get_w(),
            next = rddata_en_dly2)
        rddata_valid_dly = reg_r(
            'rddata_valid_dly',
            w = self.io.dfi.rddata.rddata_en.get_w())
        self.io.dfi.rddata.rddata_valid /= reg_r(next = rddata_valid_dly.r_or())
        for i in range(self.p.slice_num):
            rddata_valid_dly[i] /= rddata_en_dly3[i]
        self.io.dfi.rddata.rddata /= cat_rvs(dq_iddr_delay1_pn)


        self.io.ddr /= pad_ctrl.io.port_dram

    def gen_dll(self, name, dw, sp, num):
        return dll_sim(name, DW = dw, imp_mode = self.p.imp_mode, sp = sp, num = num)

    def connect_dll(self, a, pi, po):
        a.io.clock_ref /= pi[0]
        a.io.dll_reset /= pi[1]
        a.io.madj /= pi[2]
        a.io.adj /= pi[3]
        a.io.data_in /= pi[4]
        po /= a.io.data_out
