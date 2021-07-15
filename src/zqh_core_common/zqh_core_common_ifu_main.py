import sys
import os
from phgl_imp import *
from .zqh_core_common_misc import *
from .zqh_core_common_ifu_parameters import zqh_core_common_ifu_parameter
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_cpu_req
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_cpu_resp
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_cpu_io
from .zqh_core_common_ifu_bundles import zqh_core_common_ifu_slave_io
from zqh_tilelink.zqh_tilelink_node_module_main import zqh_tilelink_node_module
from .zqh_core_common_ifu_icache_itim_main import zqh_core_common_ifu_icache_itim
from .zqh_core_common_btb_bundles import zqh_core_common_btb_update
from .zqh_core_common_btb_bundles import zqh_core_common_btb_resp
from .zqh_core_common_btb_bundles import zqh_core_common_bht_update
from .zqh_core_common_btb_bundles import zqh_core_common_bht
from .zqh_core_common_btb_bundles import zqh_core_common_bht_resp
from .zqh_core_common_btb_bundles import zqh_core_common_ras
from .zqh_core_common_btb_main import zqh_core_common_btb
from .zqh_core_common_ifu_slave_mem import zqh_core_common_ifu_slave_mem

class zqh_core_common_ifu(zqh_tilelink_node_module):
    def set_par(self):
        super(zqh_core_common_ifu, self).set_par()
        self.p = zqh_core_common_ifu_parameter()

    def gen_node_tree(self):
        super(zqh_core_common_ifu, self).gen_node_tree()
        self.gen_node_master('ifu_master', bundle_p = self.p.gen_tl_bundle_p())
        self.gen_node_slave('mem_slave')

    def set_port(self):
        super(zqh_core_common_ifu, self).set_port()
        self.io.var(zqh_core_common_ifu_cpu_io('cpu'))
        self.io.var(inp('reset_pc', w = self.p.vaddr_bits))

    def main(self):
        super(zqh_core_common_ifu, self).main()

        icache = zqh_core_common_ifu_icache_itim(
            'icache', 
            extern_masters = [self.p.ifu_master])

        mem_slave = zqh_core_common_ifu_slave_mem(
            'mem_slave',
            extern_slaves = [self.p.mem_slave])
        if (self.p.itim_size != 0):
            icache.io.slave /= mem_slave.io.ifu

        qout = queue(
            'qout',
            gen = zqh_core_common_ifu_cpu_resp,
            entries = self.p.qout_entryies,
            data_bypass = self.p.qout_bypass_en,
            flush_en = 1)


        ####
        pc_s1 = reg('pc_s1', w = self.p.max_addr_bits)
        s1_kill = bits('s1_kill', init = 0)
        qout_enough_space = qout.io.count < (self.p.qout_entryies - self.p.mem_latency)
        req_addr_s0 = bits('req_addr_s0', w = self.p.max_addr_bits, init = pc_s1)
        pc_s1 /= req_addr_s0
        req_addr_last = pc_s1 if (self.p.mem_latency < 2) else icache.io.fetch.resp.bits.pc
        req_valid_s0 = icache.io.fetch.req.fire()
        icache_req_fire_s1 = reg_r('icache_req_fire_s1', next = req_valid_s0)
        req_valid_s1 = icache.io.fetch.valid_s1 & icache_req_fire_s1
        req_valid_s2 = reg_r('req_valid_s2', next = req_valid_s1)
        req_valid_last = req_valid_s1 if (self.p.mem_latency < 2) else req_valid_s2
        req_cache_miss_last = req_valid_last & ~icache.io.fetch.resp.valid
        req_cache_hit_last = req_valid_last & icache.io.fetch.resp.valid


        #icache access control
        icache_req_cmd = bits(
            'icache_req_cmd',
            w = self.io.cpu.req.bits.cmd.get_w(),
            init = IFU_CONSTS.FETCH())
        icache_req_error = bits('icache_req_error', init = 0)
        icache.io.fetch.req.valid /= self.io.cpu.req.valid | qout_enough_space
        icache.io.fetch.req.bits.cmd /= mux(
            self.io.cpu.req.valid,
            self.io.cpu.req.bits.cmd,
            icache_req_cmd)
        icache.io.fetch.req.bits.vaddr /= req_addr_s0
        icache.io.fetch.req.bits.error /= mux(
            self.io.cpu.req.valid,
            self.io.cpu.req.bits.error,
            icache_req_error)
        icache.io.fetch.s1_kill /= s1_kill


        ####
        #when cpu's fetch request is blocked, need set pending flag
        cpu_req_pending = reg_r('cpu_req_pending')
        cpu_req_cmd_s0 = self.io.cpu.req.bits.cmd
        cpu_req_cmd_s1 = reg(
            'cpu_req_cmd_s1',
            w = self.io.cpu.req.bits.cmd.get_w(),
            next = cpu_req_cmd_s0)
        cpu_req_cmd_s2 = reg(
            'cpu_req_cmd_s2',
            w = self.io.cpu.req.bits.cmd.get_w(),
            next = cpu_req_cmd_s1)
        cpu_req_cmd_last = cpu_req_cmd_s1 if (self.p.mem_latency < 2) else cpu_req_cmd_s2

        cpu_req_error_s0 = self.io.cpu.req.bits.error
        cpu_req_error_s1 = reg('cpu_req_error_s1', next = cpu_req_error_s0)
        cpu_req_error_s2 = reg('cpu_req_error_s2', next = cpu_req_error_s1)
        cpu_req_error_last = (
            cpu_req_error_s1 if (self.p.mem_latency < 2) else cpu_req_error_s2)

        cpu_req_valid_s0 = self.io.cpu.req.valid | cpu_req_pending
        cpu_req_s0 = bits('cpu_req_s0')
        cpu_req_s1 = reg('cpu_req_s1', next = cpu_req_s0)
        cpu_req_s2 = reg('cpu_req_s2', next = cpu_req_s1)
        cpu_req_last = cpu_req_s1 if (self.p.mem_latency < 2) else cpu_req_s2
        cpu_req_s0 /= cpu_req_valid_s0 | (req_cache_miss_last & cpu_req_last)
        cpu_req_cmd_reg = reg('cpu_req_cmd_reg', w = self.io.cpu.req.bits.cmd.get_w())
        cpu_req_error_reg = reg('cpu_req_error_reg')
        with when(self.io.cpu.req.valid & ~req_valid_s0):
            cpu_req_pending /= 1
            cpu_req_cmd_reg /= self.io.cpu.req.bits.cmd
            cpu_req_error_reg /= self.io.cpu.req.bits.error
        with elsewhen(icache_req_fire_s1 & ~icache.io.fetch.valid_s1 & cpu_req_s1):
            cpu_req_pending /= 1
            cpu_req_cmd_reg /= cpu_req_cmd_s1
            cpu_req_error_reg /= cpu_req_error_s1
        with elsewhen(req_cache_miss_last & cpu_req_last & ~req_valid_s0):
            cpu_req_pending /= 1
            cpu_req_cmd_reg /= cpu_req_cmd_last
            cpu_req_error_reg /= cpu_req_error_last
        with elsewhen(cpu_req_pending & req_valid_s0):
            cpu_req_pending /= 0
        with when(cpu_req_pending):
            icache_req_cmd /= cpu_req_cmd_reg
            icache_req_error /= cpu_req_error_reg


        ####
        #pc+4 for next pc
        req_addr_add_en_s1 = req_cache_hit_s1 if (self.p.mem_latency < 2) else req_valid_s1
        with when(req_addr_add_en_s1):
            req_addr_s0 /= cat([
                pc_s1[pc_s1.get_w() - 1 : log2_ceil(self.p.inst_bytes)],
                value(0, w = log2_ceil(self.p.inst_bytes))]) + self.p.inst_bytes


        ####
        #when cache miss, next pc need replay
        with when(req_cache_miss_last):
            req_addr_s0 /= req_addr_last


        ####
        #cache's output instruction before pre-decode for btb
        #push into qout
        inst_pre_dec_resp = valid(
            'inst_pre_dec_resp',
            gen = zqh_core_common_ifu_cpu_resp).as_bits()
        inst_pre_dec_resp.valid /= req_cache_hit_last
        inst_pre_dec_resp.bits.inst /= icache.io.fetch.resp.bits.inst
        inst_pre_dec_resp.bits.btb_hit /= 0
        inst_pre_dec_resp.bits.taken /= 0
        inst_pre_dec_resp.bits.bht_info /= 0
        inst_pre_dec_resp.bits.iv /= value(1).to_bits().rep(
            inst_pre_dec_resp.bits.iv.get_w())
        inst_pre_dec_resp.bits.pc /= req_addr_last
        inst_pre_dec_resp.bits.xcpt /= icache.io.fetch.resp.bits.xcpt

        qout.io.flush /= self.io.cpu.req.valid
        qout.io.enq /= inst_pre_dec_resp

        
        if (self.p.use_btb):
            self.btb = zqh_core_common_btb('btb')
            if (self.p.use_bht):
                self.bht = zqh_core_common_bht('bht')
            if (self.p.use_ras):
                self.ras = zqh_core_common_ras('ras')

            btb_resp = self.btb.io.lookup_resp.bits
            btb_resp_s1 = (zqh_core_common_btb_resp('btb_resp_s1').as_reg(next = btb_resp) 
                if (self.p.mem_latency < 2) else btb_resp)
            btb_resp_s2 = zqh_core_common_btb_resp('btb_resp_s2').as_reg(next = btb_resp_s1)
            btb_resp_last = btb_resp_s1 if (self.p.mem_latency < 2) else btb_resp_s2

            bht_resp = self.bht.get_entry(req_addr_s0) if (self.p.use_bht) else 0
            bht_resp_s1 = (zqh_core_common_bht_resp('bht_resp_s1').as_reg(next = bht_resp) 
                if (self.p.mem_latency < 2) else (
                    self.bht.get_entry(pc_s1) if (self.p.use_bht) else 0))
            bht_resp_s2 = zqh_core_common_bht_resp('bht_resp_s2').as_reg(next = bht_resp_s1)
            bht_resp_last = bht_resp_s1 if (self.p.mem_latency < 2) else bht_resp_s2

            #when btb give taken, next pc need get from btb_resp's target
            with when(req_valid_s1 & (btb_resp_s1.hit & btb_resp_s1.taken).r_or()):
                req_addr_s0 /= btb_resp_s1.tgt

            #set btb/bht info for this instruction
            inst_pre_dec_resp.bits.btb_hit /= btb_resp_last.hit
            inst_pre_dec_resp.bits.taken /= btb_resp_last.taken
            inst_pre_dec_resp.bits.bht_info /= bht_resp_last
            inst_pre_dec_resp.bits.iv /= btb_resp_last.iv

            #instruction decode for branch prediction
            (ifu_pc_jump_req, inst_post_dec_resp) = self.inst_dec_prediction(
                inst_pre_dec_resp)

            #overwrite qout's enq with inst_post_dec_resp
            qout.io.enq /= inst_post_dec_resp

            #record btb_req when it is blocked
            btb_req_pending = reg_r('btb_req_pending')
            btb_req_valid_s0 = ifu_pc_jump_req.valid | btb_req_pending
            btb_req_s0 = bits('btb_req_s0')
            btb_req_s1 = reg('btb_req_s1', next = btb_req_s0)
            btb_req_s2 = reg('btb_req_s2', next = btb_req_s1)
            btb_req_last = btb_req_s1 if (self.p.mem_latency < 2) else btb_req_s2
            btb_req_s0 /= btb_req_valid_s0 | (req_cache_miss_last & btb_req_last)
            with when(~cpu_req_valid_s0):
                with when(ifu_pc_jump_req.valid & ~req_valid_s0):
                    btb_req_pending /= 1
                with elsewhen(icache_req_fire_s1 & ~icache.io.fetch.valid_s1 & btb_req_s1):
                    btb_req_pending /= 1
                with elsewhen(req_cache_miss_last & btb_req_last & ~req_valid_s0):
                    btb_req_pending /= 1
                with elsewhen(btb_req_pending & req_valid_s0):
                    btb_req_pending /= 0
            with other():
                btb_req_pending /= 0

            #record btb resp taken when it is blocked
            btb_resp_taken_pending = reg_r('btb_resp_taken_pending')
            btb_resp_taken_valid_s0 = (
                (req_cache_hit_last & (btb_resp_last.hit & btb_resp_last.taken).r_or()) | 
                btb_resp_taken_pending)
            btb_resp_taken_s0 = bits('btb_resp_taken_s0')
            btb_resp_taken_s1 = reg('btb_resp_taken_s1', next = btb_resp_taken_s0)
            btb_resp_taken_s2 = reg('btb_resp_taken_s2', next = btb_resp_taken_s1)
            btb_resp_taken_last = (
                btb_resp_taken_s1 if (self.p.mem_latency < 2) else btb_resp_taken_s2)
            btb_resp_taken_s0 /= (
                btb_resp_taken_valid_s0 | 
                (req_cache_miss_last & btb_resp_taken_last))
            with when(~cpu_req_valid_s0 & ~btb_req_valid_s0):
                with when(req_cache_hit_last & (btb_resp_last.hit & btb_resp_last.taken).r_or() & ~req_valid_s0):
                    btb_resp_taken_pending /= 1
                with elsewhen(
                    icache_req_fire_s1 & 
                    ~icache.io.fetch.valid_s1 & 
                    btb_resp_taken_s1):
                    btb_resp_taken_pending /= 1
                with elsewhen(req_cache_miss_last & btb_resp_taken_last & ~req_valid_s0):
                    btb_resp_taken_pending /= 1
                with elsewhen(btb_resp_taken_pending & req_valid_s0):
                    btb_resp_taken_pending /= 0
            with other():
                btb_resp_taken_pending /= 0

            req_redirect_s0 = cpu_req_s0 | btb_req_s0 | btb_resp_taken_s0
            req_redirect_s1 = reg('req_redirect_s1', next = req_redirect_s0)

            btb_lookup_req_valid = (
                req_valid_s0 if (self.p.mem_latency < 2) else req_valid_s1)
            btb_lookup_req_bits_redirect = (
                req_redirect_s0 if (self.p.mem_latency < 2) else req_redirect_s1)
            btb_lookup_req_bits_pc = req_addr_s0 if (self.p.mem_latency < 2) else pc_s1
            btb_lookup_req_bits_bht_info = (
                bht_resp if (self.p.mem_latency < 2) else bht_resp_s1)
            self.btb.io.lookup_req.valid /= btb_lookup_req_valid
            self.btb.io.lookup_req.bits.redirect /= btb_lookup_req_bits_redirect
            self.btb.io.lookup_req.bits.pc /= btb_lookup_req_bits_pc
            self.btb.io.lookup_req.bits.bht_info /= btb_lookup_req_bits_bht_info

            #use prediction jump target address extract from instruction
            with when(ifu_pc_jump_req.valid):
                req_addr_s0 /= ifu_pc_jump_req.bits.vaddr


        with when(self.io.cpu.req.valid):
            req_addr_s0 /= self.io.cpu.req.bits.vaddr

        reseting = reg_s('reseting', next = 0)
        with when(reseting):
            req_addr_s0 /= self.io.reset_pc


        #when pc's flow change, need invalid s1 stage's fetch request
        s1_kill /= (
            0  
            if (self.p.mem_latency < 2) else (
                self.io.cpu.req.valid |
                (ifu_pc_jump_req.valid if (self.p.use_btb) else 0)))

        self.io.cpu.resp /= qout.io.deq
        self.io.cpu.events /= icache.io.fetch.events


    def inst_rvi_jal_jalr_decode(self, inst):
        opcode = inst[6:2]
        rd = inst[11:7]
        rs1 = inst[19:15]

        jal = opcode == I_CONSTS.opcode_map['opcode_jal']
        jalr = opcode == I_CONSTS.opcode_map['opcode_jalr']
        branch = opcode == I_CONSTS.opcode_map['opcode_branch']

        cfi_type = mux(
            (jal | jalr) & rd.match_any([1, 5]),
            CFI_CONSTS.call(),
            mux(
                jalr & rs1.match_any([1, 5]),
                CFI_CONSTS.ret(),
                mux(
                    jal | jalr, CFI_CONSTS.jump(),
                    CFI_CONSTS.branch())))
        return (jal, jalr, branch, cfi_type)

    def inst_tgt_pc_ret_pc_decode(self, rvc, jal, jalr, inst, pc):
        tgt_pc = pc + mux(
            jal,
            IMM_GEN.imm_j(inst),
            mux(
                jalr,
                IMM_GEN.imm_i(inst),
                IMM_GEN.imm_b(inst))).s_ext(pc.get_w())
        npc = pc + mux(rvc, 2, 4)
        return (tgt_pc[pc.get_w() - 1 : 0], npc[pc.get_w() - 1 : 0])

    def inst_rvc_decode(self, inst):
        rvc_code = inst[1:0]
        funct3 = inst[15:13]
        funct4 = inst[15:12]
        imm_11 = inst[12]
        imm_4 = inst[11]
        imm_9_8 = inst[10:9]
        imm_10 = inst[8]
        imm_6 = inst[7]
        imm_7 = inst[6]
        imm_3_1 = inst[5:3]
        imm_5 = inst[2]

        b_imm_8 = inst[12]
        b_imm_4_3 = inst[11:10]
        b_imm_7_6 = inst[6:5]
        b_imm_2_1 = inst[4:3]
        b_imm_5 = inst[2]

        rs1 = inst[11:7]
        rs2 = inst[6:2]
        rs1_c = inst[9:7]
        cj = (rvc_code == 0b01) & (funct3 == 0b101)
        cjal = (rvc_code == 0b01) & (funct3 == 0b001) & (self.io.cpu.rv64 == 0)
        cjr = (rvc_code == 0b10) & (funct4 == 0b1000) & (rs1 != 0) & (rs2 == 0)
        cjalr = (rvc_code == 0b10) & (funct4 == 0b1001) & (rs1 != 0) & (rs2 == 0)
        cbeqz = (rvc_code == 0b01) & (funct3 == 0b110)
        cbnez = (rvc_code == 0b01) & (funct3 == 0b111)

        rd = mux(cj | cjr, value(0, w = 5), value(1, w = 5))
        inst_rvi = bits(w = 32, init = 0)
        with when(cj | cjal):
            inst_rvi /= cat([
                imm_11, imm_10, imm_9_8, imm_7, imm_6, imm_5, imm_4, imm_3_1, imm_11,
                imm_11.rep(8),
                rd, 
                I_CONSTS.opcode_map['opcode_jal'],
                value(3, w = 2)])
        with elsewhen(cbeqz | cbnez):
            b_funct = mux(cbeqz, value(0, w = 3), value(1, w = 3))
            inst_rvi /= cat([
                b_imm_8,
                b_imm_8.rep(2),
                b_imm_8, b_imm_7_6, b_imm_5,
                value(0, w = 5),
                rs1_c.u_ext(5),
                b_funct,
                b_imm_4_3, b_imm_2_1,
                b_imm_8,
                I_CONSTS.opcode_map['opcode_branch'],
                value(3, w = 2)])
        with other():
            inst_rvi /= cat([
                value(0, w = 12),
                rs1,
                value(0, w = 3),
                rd,
                I_CONSTS.opcode_map['opcode_jalr'],
                value(3, w = 2)])

        return (cj | cjal | cjr | cjalr | cbeqz | cbnez, inst_rvi)

    def pc_for_btb(self, pc, rvc):
        return mux(
            pc[1] & ~rvc,
            pc + 2,
            pc)[pc.get_w() - 1 : 0] if (self.p.isa_c) else pc

    def inst_dec_prediction(self, inst_pre_dec):
        max_fetch_width = 2 if (self.p.isa_c) else 1

        ####
        #find call/ret instruction patten
        #ras and bht will use
        #rvi cross 4B boundary
        inst_partial = reg_r('inst_partial')
        #jalr's target is unpredictable unless ret(use ras)
        predict_unkown = reg_r('predict_unkown')
        pc_jump_en = bits(init = 0)

        inst_pc_msb = inst_pre_dec.bits.pc[inst_pre_dec.bits.pc.get_w() - 1 : 2]
        inst_reg = reg(w = inst_pre_dec.bits.inst.get_w()//2)
        inst_pc_reg = reg(w = inst_pre_dec.bits.pc.get_w())
        inst_pc_reg_msb = inst_pc_reg[inst_pre_dec.bits.pc.get_w() - 1 : 2]
        inst_decode_en = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        inst_is_rvc = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        inst_is_j = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        inst_is_jal = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        inst_is_jalr = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        inst_is_b = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        inst_is_call = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        inst_is_ret = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        inst_pc = list(map(
            lambda _: bits(w = inst_pre_dec.bits.pc.get_w()),
            range(max_fetch_width)))
        inst_all = list(map(lambda _: bits(w = 32), range(max_fetch_width)))

        inst_idx_start = ((~inst_partial & inst_pre_dec.bits.pc[1]) 
            if (self.p.isa_c) else 0)
        with when(inst_pre_dec.valid):
            pre_iv_mask = 0
            for i in range(max_fetch_width):
                hw_inst = inst_pre_dec.bits.inst[16*(i + 1) - 1 : 16*i]
                len_code = hw_inst[1:0]
                len_code_rvi = (len_code == 0b11) if (self.p.isa_c) else 1
                cur_iv_mask = bits(init = 0)
                with when(i >= inst_idx_start):
                    with when(inst_pre_dec.bits.iv[i] & (pre_iv_mask == 0)):
                        with when(~inst_partial):
                            with when(len_code_rvi):
                                if (i == 0):
                                    inst_decode_en[i] /= 1
                                    inst_is_rvc[i] /= 0
                                    cur_iv_mask /= 1
                                elif(self.p.isa_c):
                                    inst_partial /= 1
                                    inst_reg /= hw_inst
                                    inst_pc_reg /= inst_pre_dec.bits.pc
                            with other():
                                inst_decode_en[i] /= 1
                                inst_is_rvc[i] /= 1
                                if (i == 0):
                                    #invalid the following hw instruction
                                    with when(inst_pre_dec.bits.btb_hit[i] & inst_pre_dec.bits.taken[i]):
                                        cur_iv_mask /= 1
                        with elsewhen(self.p.isa_c):
                            if (i == 0):
                                inst_decode_en[i] /= 1
                                inst_is_rvc[i] /= 0
                                #invalid the following hw instruction
                                with when(inst_pre_dec.bits.btb_hit[i] & inst_pre_dec.bits.taken[i]):
                                    cur_iv_mask /= 1
                            else:
                                with when(len_code_rvi):
                                    inst_partial /= 1
                                    inst_reg /= hw_inst
                                    inst_pc_reg /= inst_pre_dec.bits.pc
                                with other():
                                    inst_decode_en[i] /= 1
                                    inst_is_rvc[i] /= 1
                                    inst_partial /= 0
                    with other():
                        inst_partial /= 0
                pre_iv_mask = cur_iv_mask

        #pc redirect happen, the following hw instrucion should be invalid
        with when(pc_jump_en):
            inst_partial /= 0
        with when(self.io.cpu.req.valid):
            inst_partial /= 0

        #force to 0 when no rvc
        if (self.p.isa_c == 0):
            inst_partial /= 0
            inst_reg /= 0
            inst_pc_reg /= 0

        for i in range(max_fetch_width):
            (rvc_cfi, inst_rvc2rvi) = self.inst_rvc_decode(
                inst_pre_dec.bits.inst[16*(i+1) - 1 : 16*i]) if (self.p.isa_c) else (0, 0)
            inst_rvi = mux(
                inst_is_rvc[i],
                inst_rvc2rvi, 
                mux(
                    inst_partial,
                    cat([inst_pre_dec.bits.inst[15:0], inst_reg]),
                    inst_pre_dec.bits.inst))
            rvc_cfi_mask = mux(inst_is_rvc[i], rvc_cfi, 1)
            inst_all[i] /= inst_rvi
            (rvi_jal, rvi_jalr, rvi_b, rvi_cfi_type) = self.inst_rvi_jal_jalr_decode(
                inst_rvi)
            with when(inst_decode_en[i]):
                inst_is_j[i] /= rvc_cfi_mask & (rvi_jal | rvi_jalr)
                inst_is_jal[i] /= rvc_cfi_mask & rvi_jal
                inst_is_jalr[i] /= rvc_cfi_mask & rvi_jalr
                inst_is_b[i] /= rvc_cfi_mask & rvi_b
                inst_is_call[i] /= rvc_cfi_mask & (rvi_cfi_type == CFI_CONSTS.call())
                inst_is_ret[i] /= rvc_cfi_mask & (rvi_cfi_type == CFI_CONSTS.ret())

        for i in range(max_fetch_width):
            if (i == 0):
                inst_pc[i] /= mux(
                    inst_partial,
                    cat([inst_pc_reg_msb, value(2, w = 2)]),
                    cat([inst_pc_msb, value(0, w = 2)]))
            else:
                inst_pc[i] /= cat([inst_pc_msb, value(2*i, w = 2)])


        ras_empty = self.ras.empty() if (self.p.use_ras) else bits(init = 1)
        ras_push_en = bits(init = 0)
        ras_pop_en = bits(init = 0)
        inst_sel_map = list(map(lambda _: bits(init = 0), range(max_fetch_width)))
        pre_jump = 0
        for i in range(max_fetch_width):
            b_taken = inst_is_b[i] & inst_pre_dec.bits.btb_hit[i] & (inst_pre_dec.bits.bht_info.taken() 
                if (self.p.use_bht) else inst_pre_dec.bits.taken[i])
            cur_taken = inst_is_j[i] | b_taken
            with when(pre_jump == 0):
                inst_sel_map[i] /= cur_taken
                pc_jump_en /= (
                    ((inst_is_jal[i] | b_taken) & ~(inst_pre_dec.bits.btb_hit[i] & inst_pre_dec.bits.taken[i])) | 
                    (inst_is_ret[i] & ~ras_empty))

                with when(~predict_unkown):
                    with when(inst_is_call[i]):
                        ras_push_en /= 1
                    with when(inst_is_ret[i]):
                        ras_pop_en /= 1
            pre_jump = pre_jump | cur_taken

        for i in range(max_fetch_width):
            with when(~(inst_pre_dec.bits.btb_hit[i] & inst_pre_dec.bits.taken[i])):
                with when(inst_is_jalr[i]):
                    with when(~inst_is_ret[i] | ras_empty):
                        predict_unkown /= 1

        with when(self.io.cpu.req.valid):
            predict_unkown /= 0

        inst_sel = sel_oh(inst_sel_map, inst_all)
        inst_sel_is_jal = sel_oh(inst_sel_map, inst_is_jal)
        inst_sel_is_jalr = sel_oh(inst_sel_map, inst_is_jalr)
        inst_sel_is_call = sel_oh(inst_sel_map, inst_is_call)
        inst_sel_is_ret = sel_oh(inst_sel_map, inst_is_ret)
        inst_sel_is_rvc = sel_oh(inst_sel_map, inst_is_rvc)
        inst_sel_pc = sel_oh(inst_sel_map, inst_pc)
        (inst_tgt_pc, inst_npc) = self.inst_tgt_pc_ret_pc_decode(
            inst_sel_is_rvc,
            inst_sel_is_jal,
            inst_sel_is_jalr,
            inst_sel,
            inst_sel_pc)

        if (self.p.use_ras):
            with when(~self.io.cpu.req.valid):
                with when(ras_push_en):
                    self.ras.push(inst_npc)
                with elsewhen(ras_pop_en):
                    self.ras.pop()
        

        #jal/jalr/branch's npc generate from instruction
        pc_jump_req = valid('pc_jump_req', gen = zqh_core_common_ifu_cpu_req).as_bits()
        pc_jump_req.valid /= pc_jump_en
        pc_jump_req.bits.cmd /= IFU_CONSTS.FETCH()
        pc_jump_req.bits.vaddr /= mux(
            inst_sel_is_ret,
            self.ras.peek() if (self.p.use_ras) else inst_tgt_pc,
            inst_tgt_pc)


        ####
        #instruction decode and prediction
        inst_post_dec = valid('inst_post_dec', gen = zqh_core_common_ifu_cpu_resp).as_bits()
        inst_post_dec /= inst_pre_dec
        with when(pc_jump_en):
            with when(inst_sel_map[0]):
                with when(inst_partial | inst_sel_is_rvc):
                    #mask off the left half word instruction
                    for i in range(1, max_fetch_width):
                        inst_post_dec.bits.iv[i] /= 0

            #set taken bit if btb not taken(miss)
            for i in range(max_fetch_width):
                with when(inst_sel_map[i] & ~(inst_pre_dec.bits.btb_hit[i] & inst_pre_dec.bits.taken[i])):
                    inst_post_dec.bits.taken[i] /= 1


        #speculative update btb
        self.btb.io.btb_update /= self.io.cpu.btb_update
        if (self.p.btb_pre_update_en):
            spec_btb_update = valid(
                'spec_btb_update',
                gen = zqh_core_common_btb_update).as_bits()
            spec_btb_update.valid /= pc_jump_en & ~predict_unkown
            spec_btb_update.bits.cfi_type /= mux(
                inst_sel_is_call,
                CFI_CONSTS.call(),
                mux(inst_sel_is_ret,
                    CFI_CONSTS.ret(),
                    mux(
                        inst_sel_is_jal | inst_sel_is_jalr,
                        CFI_CONSTS.jump(),
                        CFI_CONSTS.branch())))
            spec_btb_update.bits.taken /= 1
            spec_btb_update.bits.tgt /= pc_jump_req.bits.vaddr
            spec_btb_update.bits.pc /= self.pc_for_btb(inst_sel_pc, inst_sel_is_rvc)
            spec_btb_update.bits.rvc /= inst_sel_is_rvc
            spec_btb_update.bits.rvi_half /= inst_sel_pc[1] & ~inst_sel_is_rvc

            with when(~self.io.cpu.btb_update.valid):
                self.btb.io.btb_update /= spec_btb_update


        #predict bht update in fetch stage
        if (self.p.use_bht):
            bht_update_en = bits(init = 0)
            bht_update_taken = bits(init = 0)
            for i in range(max_fetch_width):
                with when(~predict_unkown):
                    with when(inst_is_b[i] & inst_pre_dec.bits.iv[i]):
                        bht_update_en /= 1
                        bht_update_taken /= inst_pre_dec.bits.btb_hit[i] & inst_pre_dec.bits.taken[i]

            with when(bht_update_en):
                self.bht.raw_history(bht_update_taken)

            #mem stage's accurate update
            #will overwrite predict update if mispredict happen
            with when(self.io.cpu.bht_update.valid):
                with when(self.io.cpu.bht_update.bits.branch):
                    self.bht.update_table(
                        self.io.cpu.bht_update.bits.pc,
                        self.io.cpu.bht_update.bits.bht_info,
                        self.io.cpu.bht_update.bits.taken)
                    with when(self.io.cpu.bht_update.bits.mispredict):
                        self.bht.update_history(
                            self.io.cpu.bht_update.bits.pc,
                            self.io.cpu.bht_update.bits.bht_info.history,
                            self.io.cpu.bht_update.bits.taken)
                with elsewhen(self.io.cpu.bht_update.bits.mispredict):
                    self.bht.set_history(self.io.cpu.bht_update.bits.bht_info.history)

        return (pc_jump_req, inst_post_dec)
