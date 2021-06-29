import sys
import os
from phgl_imp import *
from .zqh_pwm_parameters import zqh_pwm_parameter
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_pwm_bundles import zqh_pwm_io

class zqh_pwm(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_pwm, self).set_par()
        self.p = zqh_pwm_parameter()

    def gen_node_tree(self):
        super(zqh_pwm, self).gen_node_tree()
        self.gen_node_slave(
            'pwm_slave',
            tl_type = 'tl_uh',
            bundle_p = self.p.gen_tl_bundle_p())
        self.p.pwm_slave.print_up()
        self.p.pwm_slave.print_address_space()

    def set_port(self):
        super(zqh_pwm, self).set_port()
        self.io.var(zqh_pwm_io('pwm', ncmp = self.p.ncmp))

    def main(self):
        super(zqh_pwm, self).main()
        self.gen_node_interface('pwm_slave')
        assert(self.tl_in[0].a.bits.data.get_w() >= 32)

        #{{{
        pwmcmpip_bus_write_valid = bits(w = self.p.ncmp, init = 0)
        pwmcmpip_bus_write_data = bits(w = self.p.ncmp, init = 0)
        def func_pwmcmpip_write(reg_ptr, fire, address, size, wdata, mask_bit):
            with when(fire):
                for i in range(self.p.ncmp):
                    with when(mask_bit[i]):
                        pwmcmpip_bus_write_valid[i] /= 1
                        pwmcmpip_bus_write_data[i] /= wdata[i]
            return (1, 1)
        self.cfg_reg(csr_reg_group(
            'pwmcfg',
            offset = 0x000,
            size = 4,
            fields_desc = [
                csr_reg_field_desc('pwmcmpip', width = self.p.ncmp, write = func_pwmcmpip_write, reset = 0),
                csr_reg_field_desc('reserved5', access = 'VOL', width = 4 - self.p.ncmp) if (self.p.ncmp < 4) else None,
                csr_reg_field_desc('pwmcmpgang', width = self.p.ncmp, reset = 0, comments = '''\
A comparator can be ganged together with its next-highest-numbered neighbor to generate arbitrary
PWM pulses. When the pwmcmpXgang bit is set, comparator X fires and raises its pwmXgpio
signal. When comparator X + 1 (or pwmcmp0 for pwmcmp3) fires, the pwmXgpio output is reset to
zero.'''),
                csr_reg_field_desc('reserved4', access = 'VOL', width = 4 - self.p.ncmp) if (self.p.ncmp < 4) else None,
                csr_reg_field_desc('pwminv', width = self.p.ncmp, reset = 0, comments = '''\
each pwm output gpio can be inverted.
when pwminv[X] is set, it's output gipo will be inverted.'''),
                csr_reg_field_desc('reserved3', access = 'VOL', width = 4 - self.p.ncmp) if (self.p.ncmp < 4) else None,
                csr_reg_field_desc('pwmcmpcenter', width = self.p.ncmp, reset = 0, comments = '''\
A per-comparator pwmcmpXcenter bit in pwmcfg allows a single PWM comparator to generate a
center-aligned symmetric duty-cycle as shown in Figure 20.4 The pwmcmpXcenter bit changes the
comparator to compare with the bitwise inverted pwms value whenever the MSB of pwms is high.'''),
                csr_reg_field_desc('reserved2', access = 'VOL', width = 2),
                csr_reg_field_desc('pwmenoneshot', width = 1, reset = 0, comments = '''\
When pwmenoneshot is
set, the counter can increment but pwmenoneshot is reset to zero once the counter resets, disabling
further counting (unless pwmenalways is set). The pwmenoneshot bit provides a way for software
to generate a single PWM cycle then stop. Software can set the pwnenoneshot again at any time
to replay the one-shot waveform.'''),
                csr_reg_field_desc('pwmenalways', width = 1, reset = 0, comments = '''\
If the pwmenalways bit is set, the PWM counter increments continuously.'''),
                csr_reg_field_desc('reserved1', access = 'VOL', width = 1),
                csr_reg_field_desc('pwmdeglitch', width = 1, reset = 0, comments = '''\
To avoid glitches in the PWM waveforms when changing pwmcmpX register values, the
pwmdeglitch bit in pwmcfg can be set to capture any high output of a PWM comparator in a sticky
bit (pwmcmpXip for comparator X) and prevent the output falling again within the same PWM cycle.
If pwmdeglitch is set, but pwmzerocmp is clear, the deglitch circuit is still operational but is now triggered when pwms contains all 1s and will cause a carry out of the high bit of the pwms incrementer
just before the counter wraps to zero.'''),
                csr_reg_field_desc('pwmzerocmp', width = 1, reset = 0, comments = '''\
If the pwmzerocomp bit is set, when pwms reaches or exceeds pwmcmp0, pwmcount is cleared to zero
and the current PWM cycle is completed. Otherwise, the counter is allowed to wrap around.'''),
                csr_reg_field_desc('pwmsticky', width = 1, reset = 0, comments = '''\
The pwmsticky bit will disallow the pwmcmpXip registers from clearing if they’re already set, and is
used to ensure interrupts are seen from the pwmcmpXip bits.'''),
                csr_reg_field_desc('reserved0', access = 'VOL', width = 4),
                csr_reg_field_desc('pwmscale', width = 4, reset = 0, comments = '''\
The 4-bit pwmscale field scales the PWM counter value before feeding it to the PWM comparators.
The value in pwmscale is the bit position within the pwmcount register of the start of a cmpwidth-bit
pwms field. A value of 0 in pwmscale indicates no scaling, and pwms would then be equal to the
low cmpwidth bits of pwmcount. The maximum value of 15 in pwmscale corresponds to dividing the
clock rate by 2**15''')]))
        self.cfg_reg(csr_reg_group(
            'pwmcount', 
            offset = 0x008, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('pwmcount', width = 31, reset = 0, comments = '''\
The PWM unit is based around a counter held in pwmcount. The counter can be read or written
over the TileLink bus. The pwmcount register is (15 + cmpwidth) bits wide. For example, for
cmpwidth of 16 bits, the counter is held in pwmcount[30:0], and bit 31 of pwmcount returns a zero
when read''')]))
        self.cfg_reg(csr_reg_group(
            'pwms', 
            offset = 0x010,
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('pwms', access = 'RO', width = self.p.cmp_width, comments = '''
pwmcount's after pwmscale  value. pwms = pwmcount << pwmscale''')]))
        self.cfg_reg(csr_reg_group(
            'pwmmax', 
            offset = 0x018, 
            size = 4, 
            fields_desc = [
                csr_reg_field_desc('pwmmax', width = self.p.cmp_width, reset = 0, comments = '''\
when pwmzerocmp is cleared, pwmmax is the max value of pwms.
pwmcount will be reset to zero when it reach pwmmax.''')]))
        for i in range(self.p.ncmp):
            self.cfg_reg(csr_reg_group(
                'pwmcmp'+str(i), 
                offset = 0x020 + i*4, 
                size = 4, 
                fields_desc = [
                    csr_reg_field_desc('pwmcmp', width = self.p.cmp_width, reset = 0, comments = '''\
Each compare register is a cmpwdith-bit value against which the current pwms value is compared
every cycle. The output of each comparator is high whenever the value of pwms is greater than or
equal to the corresponding pwmcmpX.''')]))
        #}}}

        pwms = (
            self.regs['pwmcount'].pwmcount >> 
            self.regs['pwmcfg'].pwmscale)[self.p.cmp_width - 1 : 0]
        pwmscenter = mux(pwms[self.p.cmp_width - 1], ~pwms, pwms)
        self.regs['pwms'].pwms /= pwms

        count_lsb_match = list(map(
            lambda _: value(1) if (_ == 0) else 
                (self.regs['pwmcount'].pwmcount[(_-1):0] == value(2**_ - 1)),
            range(2**self.regs['pwmcfg'].pwmscale.get_w())))
        scale_match = sel_bin(self.regs['pwmcfg'].pwmscale, count_lsb_match)
        pwmcmp_match = list(map(
            lambda _: mux(
                self.regs['pwmcfg'].pwmcmpcenter[_],
                pwmscenter,
                pwms) >= self.regs['pwmcmp'+str(_)].pwmcmp,
            range(self.p.ncmp)))
        pwmmax_match = (pwms == self.regs['pwmmax'].pwmmax) & scale_match
        count_max_match = (pwms == value(2**self.p.cmp_width - 1)) & scale_match

        # bus write has higher priority
        count_reset_valid = bits('count_reset_valid', init = 0)
        with when(
            self.regs['pwmcfg'].pwmenalways | 
            self.regs['pwmcfg'].pwmenoneshot):
            with when(
                (self.regs['pwmcfg'].pwmzerocmp & pwmmax_match) | 
                count_max_match):
                self.regs['pwmcount'].pwmcount /= 0
                count_reset_valid /= 1
            with other():
                self.regs['pwmcount'].pwmcount /= self.regs['pwmcount'].pwmcount + 1

        # clear pwmenoneshot
        with when(self.regs['pwmcfg'].pwmenoneshot):
            with when(count_reset_valid):
                self.regs['pwmcfg'].pwmenoneshot /= 0

        # pwmcmpip capture
        ip_capture = bits('ip_hold_valid')
        ip_capture /= (
            ~self.regs['pwmcfg'].pwmdeglitch | 
            (self.regs['pwmcfg'].pwmdeglitch & count_reset_valid))
        for i in range(self.p.ncmp):
            with when(
                (
                    self.regs['pwmcfg'].pwmcmpip[i] & 
                    ~self.regs['pwmcfg'].pwmcmpcenter[i]) |
                (
                    self.regs['pwmcfg'].pwmcmpip[i] & 
                    self.regs['pwmcfg'].pwmcmpcenter[i] & 
                    ~pwms[self.p.cmp_width - 1]) |
                (
                    ~self.regs['pwmcfg'].pwmcmpip[i] & 
                    self.regs['pwmcfg'].pwmcmpcenter[i] & 
                    pwms[self.p.cmp_width - 1])):
                with when(
                    ~(
                        (
                            self.regs['pwmcfg'].pwmdeglitch & 
                            ~reg_r(next = count_reset_valid)) | 
                        self.regs['pwmcfg'].pwmsticky)):
                    self.regs['pwmcfg'].pwmcmpip[i] /= (
                        pwmcmp_match[i] | 
                        (pwmcmpip_bus_write_valid[i] & pwmcmpip_bus_write_data[i]))
                with other():
                    with when(pwmcmpip_bus_write_valid[i]):
                        self.regs['pwmcfg'].pwmcmpip[i] /= pwmcmpip_bus_write_data[i]
            with other():
                self.regs['pwmcfg'].pwmcmpip[i] /= (
                    pwmcmp_match[i] | 
                    (pwmcmpip_bus_write_valid[i] & pwmcmpip_bus_write_data[i]))

        
        for i in range(self.p.ncmp):
            next_ip = 0 if (i == self.p.ncmp - 1) else (i+1)
            self.io.pwm.do[i] /= mux(
                self.regs['pwmcfg'].pwminv[i],
                ~self.regs['pwmcfg'].pwmcmpip[i],
                self.regs['pwmcfg'].pwmcmpip[i])
            with when(self.regs['pwmcfg'].pwmcmpgang[i]):
                with when(self.regs['pwmcfg'].pwmcmpip[next_ip]):
                    self.io.pwm.do[i] /= self.regs['pwmcfg'].pwminv[i]

        #interrupt
        self.int_out[0] /= (
            self.regs['pwmcfg'].pwmsticky & self.regs['pwmcfg'].pwmcmpip.r_or())
