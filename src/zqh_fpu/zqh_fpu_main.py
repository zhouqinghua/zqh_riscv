#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/tile/FPU.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *
from zqh_core_common.zqh_core_common_misc import I_CONSTS
from zqh_core_common.zqh_core_common_misc import D_CONSTS
from .zqh_fpu_misc import *
from zqh_fpu.zqh_fpu_parameters import zqh_fpu_parameter
from zqh_fpu.zqh_fpu_parameters import zqh_f_type
from .zqh_fpu_bundles import *
from zqh_common.zqh_decode_logic import zqh_decode_logic
from zqh_hardfloat.hardfloat import *

class zqh_fpu_decoder(module):
    def set_par(self):
        super(zqh_fpu_decoder, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_port(self):
        super(zqh_fpu_decoder, self).set_port()
        self.no_crg()
        self.io = zqh_fpu_decoder_io('io')

    def main(self):
        super(zqh_fpu_decoder, self).main()
        default =                [D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X()]
        f = [(I_CONSTS.FLW      (), [D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FSW      (), [D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FMV_S_X  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FCVT_S_W (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_S_WU(), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_S_L (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_S_LU(), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMV_X_S  (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FCLASS_S (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FCVT_W_S (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_WU_S(), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_L_S (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_LU_S(), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FEQ_S    (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FLT_S    (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FLE_S    (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FSGNJ_S  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FSGNJN_S (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FSGNJX_S (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FMIN_S   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMAX_S   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FADD_S   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FSUB_S   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMUL_S   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMADD_S  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMSUB_S  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FNMADD_S (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FNMSUB_S (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FDIV_S   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FSQRT_S  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y()])]
        d = [(I_CONSTS.FLD      (), [D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FSD      (), [D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FMV_D_X  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FCVT_D_W (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_D_WU(), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_D_L (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_D_LU(), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMV_X_D  (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FCLASS_D (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FCVT_W_D (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_WU_D(), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_L_D (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_LU_D(), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_S_D (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FCVT_D_S (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FEQ_D    (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FLT_D    (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FLE_D    (), [D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FSGNJ_D  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FSGNJN_D (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FSGNJX_D (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N()]),
             (I_CONSTS.FMIN_D   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMAX_D   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FADD_D   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FSUB_D   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMUL_D   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMADD_D  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FMSUB_D  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FNMADD_D (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FNMSUB_D (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FDIV_D   (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.Y()]),
             (I_CONSTS.FSQRT_D  (), [D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.X(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.N(),D_CONSTS.Y(),D_CONSTS.Y()])]

        if (self.p.flen == 32):
            insns = f
        elif (self.p.flen == 64):
            insns = f + d
        else:
            assert(0)
        decoder = zqh_decode_logic().decode_sig_list(self.io.inst, default, insns)
        s = self.io.sigs
        sigs = [s.ldst, s.wen, s.ren1, s.ren2, s.ren3, s.swap12,
                s.swap23, s.singleIn, s.singleOut, s.fromint, s.toint,
                s.fastpipe, s.fma, s.div, s.sqrt, s.wflags]
        for (s,d) in list(zip(sigs, decoder)):
            s /= d

class zqh_fp_to_int(module):
    def set_par(self):
        super(zqh_fp_to_int, self).set_par()        
        self.p = zqh_fpu_parameter()
        self.p.par('latency', None)

    def check_par(self):
        super(zqh_fp_to_int, self).check_par()
        assert((self.p.latency is None) or (self.p.latency == 1))

    def set_port(self):
        super(zqh_fp_to_int, self).set_port()
        self.io = zqh_fp_to_int_io('io')

    def main(self):
        super(zqh_fp_to_int, self).main()
        if (self.p.latency is not None):
            in_ = self.io.input.bits.clone('in_').as_reg(
                tp = 'reg_en',
                next = self.io.input.bits,
                en = self.io.input.valid)
            valid = reg('valid', next=self.io.input.valid)
        else:
            in_ = self.io.input.bits
            valid = self.io.input.valid

        dcmp = CompareRecFN(
            'dcmp',
            expWidth = self.p.maxExpWidth,
            sigWidth = self.p.maxSigWidth)
        dcmp.io.a /= in_.in1
        dcmp.io.b /= in_.in2
        dcmp.io.signaling /= ~in_.rm[1]

        tag = ~in_.singleOut ## TODO typeTag
        store = self.p.ieee(in_.in1)
        toint = bits('toint', w = store.get_w(), init = store)
        intType = bits('intType', w = tag.get_w(), init = tag)
        self.io.output.bits.store /= sel_bin(
            tag, 
            list(map(
                lambda t: store[t.ieeeWidth() - 1: 0].rep(
                    self.p.maxType.ieeeWidth() // t.ieeeWidth()),
                self.p.floatTypes)))
        self.io.output.bits.toint /= sel_bin(
            intType,
            list(map(
                lambda i: toint[(self.p.minXLen << i) - 1: 0].s_ext(self.p.xlen), 
                range(self.p.nIntTypes()))))
        self.io.output.bits.exc /= value(0)

        with when (in_.rm[0]):
            classify_out = sel_bin(
                tag, 
                list(map(
                    lambda t: t.classify(self.p.maxType.unsafeConvert(in_.in1, t)),
                    self.p.floatTypes)))
            toint /= classify_out | (store >> self.p.minXLen << self.p.minXLen)
            intType /= 0

        conv = RecFNToIN(
            'conv', 
            expWidth = self.p.maxExpWidth, 
            sigWidth = self.p.maxSigWidth, 
            intWidth = self.p.xlen)
        conv.io.input /= in_.in1
        conv.io.roundingMode /= in_.rm
        conv.io.signedOut /= ~in_.typ[0]

        narrow = []
        for i in range(self.p.nIntTypes() - 1):
            w = self.p.minXLen << i
            tmp = RecFNToIN(
                'narrow_'+str(i), 
                expWidth = self.p.maxExpWidth, 
                sigWidth = self.p.maxSigWidth, 
                intWidth = w)
            tmp.io.input /= in_.in1
            tmp.io.roundingMode /= in_.rm
            tmp.io.signedOut /= ~in_.typ[0]
            narrow.append(tmp)

        with when (in_.wflags): ## feq/flt/fle, fcvt
            toint /= (
                (~in_.rm & cat([dcmp.io.lt, dcmp.io.eq])).r_or() | 
                (store >> self.p.minXLen << self.p.minXLen))
            self.io.output.bits.exc /= dcmp.io.exceptionFlags
            intType /= 0

            with when (~in_.ren2): ## fcvt
                cvtType = in_.typ[log2_ceil(self.p.nIntTypes()): 1]
                intType /= cvtType

                toint /= conv.io.output
                self.io.output.bits.exc /= cat([
                    conv.io.intExceptionFlags[2: 1].r_or(),
                    value(0, w = 3),
                    conv.io.intExceptionFlags[0]])

                for i in range(self.p.nIntTypes() - 1):
                    w = self.p.minXLen << i
                    with when (cvtType == i):
                        excSign = (
                            in_.in1[self.p.maxExpWidth + self.p.maxSigWidth] &
                            ~self.p.maxType.isNaN(in_.in1))
                        excOut = cat([conv.io.signedOut == excSign, (~excSign).rep(w-1)])
                        invalid = (
                            conv.io.intExceptionFlags[2] | 
                            narrow[i].io.intExceptionFlags[1])
                        with when (invalid):
                            toint /= cat([conv.io.output >> w, excOut]) 
                        self.io.output.bits.exc /= cat([
                            invalid, 
                            value(0, w = 3),
                            ~invalid & conv.io.intExceptionFlags[0]])

        self.io.output.valid /= valid
        self.io.output.bits.lt /= (
            dcmp.io.lt | 
            (
                (dcmp.io.a.as_sint() < value(0, w = dcmp.io.a.get_w()).to_sint()) & 
                (dcmp.io.b.as_sint() >= value(0, w = dcmp.io.b.get_w()).to_sint())))
        self.io.output.bits.input /= in_

class zqh_int_to_fp(module):
    def set_par(self):
        super(zqh_int_to_fp, self).set_par()
        self.p = zqh_fpu_parameter()
        self.p.par('latency', None)

    def set_port(self):
        super(zqh_int_to_fp, self).set_port()
        self.io = zqh_int_to_fp_io('io')

    def main(self):
        super(zqh_int_to_fp, self).main()
        in_ = pipe(self.io.input)
        tag = ~in_.bits.singleIn ## TODO typeTag

        Mux = zqh_fp_result('Mux')
        Mux.exc /= value(0)
        Mux.data /= self.p.recode(in_.bits.in1, ~in_.bits.singleIn)

        res = bits(w = in_.bits.in1.get_w(), init = in_.bits.in1.as_sint()).to_sint()
        for i in range(self.p.nIntTypes() - 1):
            smallInt = in_.bits.in1[(self.p.minXLen << i) - 1: 0]
            with when (in_.bits.typ[log2_ceil(self.p.nIntTypes()): 1] == i):
                res /= mux(in_.bits.typ[0], smallInt.z_ext(), smallInt.as_sint())
        intValue = res.as_uint()

        i2f = []
        for i in range(len(self.p.floatTypes)):
            t = self.p.floatTypes[i]
            tmp = INToRecFN(
                'i2f_'+str(i), 
                intWidth = self.p.xlen, 
                expWidth = t.exp, 
                sigWidth = t.sig)
            tmp.io.signedIn /= ~in_.bits.typ[0]
            tmp.io.input /= intValue
            tmp.io.roundingMode /= in_.bits.rm
            tmp.io.detectTininess /= consts.tininess_afterRounding()
            i2f.append(tmp)

        with when (in_.bits.wflags): ## fcvt
            ## could be improved for RVD/RVQ with a single variable-position rounding
            ## unit, rather than N fixed-position ones
            t_idx = 0
            i2fResults = []
            for t in self.p.floatTypes:
                i2fResults.append(
                    (
                        self.p.sanitizeNaN(i2f[t_idx].io.output, t),
                        i2f[t_idx].io.exceptionFlags))
                t_idx = t_idx + 1

            [data, exc] = list(zip(*i2fResults))
            dataPadded = list(map(
                lambda d: cat([data[-1] >> d.get_w(), d]),
                data[:-1])) + [data[-1]]
            Mux.data /= sel_bin(tag, dataPadded)
            Mux.exc /= sel_bin(tag, exc)

        self.io.output /= pipe_valid(in_.valid, Mux, self.p.latency-1)

class zqh_fp_to_fp(module):
    def set_par(self):
        super(zqh_fp_to_fp, self).set_par()
        self.p = zqh_fpu_parameter()
        self.p.par('latency', None)

    def set_port(self):
        super(zqh_fp_to_fp, self).set_port()
        self.io = zqh_fp_to_fp_io('io')

    def main(self):
        super(zqh_fp_to_fp, self).main()
        in_ = pipe(self.io.input)

        signNum = mux(
            in_.bits.rm[1],
            in_.bits.in1 ^ in_.bits.in2,
            mux(in_.bits.rm[0], ~in_.bits.in2, in_.bits.in2))
        fsgnj = cat([signNum[self.p.flen], in_.bits.in1[self.p.flen-1: 0]])

        fsgnjMux = zqh_fp_result('fsgnjMux')
        fsgnjMux.exc /= value(0)
        fsgnjMux.data /= fsgnj

        with when (in_.bits.wflags): ## fmin/fmax
            isnan1 = self.p.maxType.isNaN(in_.bits.in1)
            isnan2 = self.p.maxType.isNaN(in_.bits.in2)
            isInvalid = (
                self.p.maxType.isSNaN(in_.bits.in1) | 
                self.p.maxType.isSNaN(in_.bits.in2))
            isNaNOut = isnan1 & isnan2
            isLHS = isnan2 | ((in_.bits.rm[0] != self.io.lt) & ~isnan1)
            fsgnjMux.exc /= isInvalid << 4
            fsgnjMux.data /= mux(
                isNaNOut,
                self.p.maxType.qNaN(),
                mux(isLHS, in_.bits.in1, in_.bits.in2))

        inTag = ~in_.bits.singleIn ## TODO typeTag
        outTag = ~in_.bits.singleOut ## TODO typeTag
        Mux = zqh_fp_result('Mux', init = fsgnjMux)
        for t in self.p.floatTypes[:-1]:
            with when (outTag == self.p.typeTag(t)):
                Mux.data /= cat([
                    fsgnjMux.data >> t.recodedWidth(),
                    self.p.maxType.unsafeConvert(fsgnjMux.data, t)])

        narrower = []
        ot_idx = 0
        if (len(self.p.floatTypes) > 1):
            for i in range(len(self.p.floatTypes) - 1): 
                outType = self.p.floatTypes[i]
                tmp = RecFNToRecFN(
                    'narrower_'+str(i), 
                    inExpWidth = self.p.maxType.exp, 
                    inSigWidth = self.p.maxType.sig, 
                    outExpWidth = outType.exp, 
                    outSigWidth = outType.sig)
                tmp.io.input /= in_.bits.in1
                tmp.io.roundingMode /= in_.bits.rm
                tmp.io.detectTininess /= consts.tininess_afterRounding()
                narrower.append(tmp)

        with when (in_.bits.wflags & ~in_.bits.ren2): ## fcvt
            if (len(self.p.floatTypes) > 1):
                ## widening conversions simply canonicalize NaN operands
                widened = mux(
                    self.p.maxType.isNaN(in_.bits.in1), 
                    self.p.maxType.qNaN(),
                    in_.bits.in1)
                fsgnjMux.data /= widened
                fsgnjMux.exc /= self.p.maxType.isSNaN(in_.bits.in1) << 4

                ## narrowing conversions require rounding (for RVQ, this could be
                ## optimized to use a single variable-position rounding unit, rather
                ## than two fixed-position ones)
                for outType in self.p.floatTypes[:-1]: 
                    with when(
                        (outTag == self.p.typeTag(outType)) & 
                        ((self.p.typeTag(outType) == 0) | (outTag < inTag))):
                        narrowed = self.p.sanitizeNaN(narrower[ot_idx].io.output, outType)
                        Mux.data /= cat([fsgnjMux.data >> narrowed.get_w(), narrowed])
                        Mux.exc /= narrower[ot_idx].io.exceptionFlags
                    ot_idx = ot_idx + 1

        self.io.output /= pipe_valid(in_.valid, Mux, self.p.latency-1)

class zqh_mul_add_rec_fn_pipe(module):
    def set_par(self):
        super(zqh_mul_add_rec_fn_pipe, self).set_par()
        self.p.par('latency', None)
        self.p.par('expWidth', None)
        self.p.par('sigWidth', None)

    def set_port(self):
        super(zqh_mul_add_rec_fn_pipe, self).set_port()
        assert(self.p.latency<=2)
        self.io = zqh_mul_add_rec_fn_pipe_io(
            'io', 
            expWidth = self.p.expWidth, 
            sigWidth = self.p.sigWidth)

    def main(self):
        super(zqh_mul_add_rec_fn_pipe, self).main()
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        mulAddRecFNToRaw_preMul = MulAddRecFNToRaw_preMul(
            'mulAddRecFNToRaw_preMul', 
            expWidth = self.p.expWidth,
            sigWidth = self.p.sigWidth)
        mulAddRecFNToRaw_postMul = MulAddRecFNToRaw_postMul(
            'mulAddRecFNToRaw_postMul',
            expWidth = self.p.expWidth,
            sigWidth = self.p.sigWidth)

        mulAddRecFNToRaw_preMul.io.op /= self.io.op
        mulAddRecFNToRaw_preMul.io.a  /= self.io.a
        mulAddRecFNToRaw_preMul.io.b  /= self.io.b
        mulAddRecFNToRaw_preMul.io.c  /= self.io.c

        mulAddResult = (
            mulAddRecFNToRaw_preMul.io.mulAddA *
            mulAddRecFNToRaw_preMul.io.mulAddB) + mulAddRecFNToRaw_preMul.io.mulAddC

        valid_stage0 = bits('valid_stage0')
        roundingMode_stage0 = bits('roundingMode_stage0', w = 3)
        detectTininess_stage0 = bits('detectTininess_stage0', w = 1)
  
        postmul_regs = 1 if(self.p.latency>0) else 0
        mulAddRecFNToRaw_postMul.io.fromPreMul   /= pipe_valid(
            self.io.validin,
            mulAddRecFNToRaw_preMul.io.toPostMul,
            postmul_regs).bits
        mulAddRecFNToRaw_postMul.io.mulAddResult /= pipe_valid(
            self.io.validin,
            mulAddResult,
            postmul_regs).bits
        mulAddRecFNToRaw_postMul.io.roundingMode /= pipe_valid(
            self.io.validin,
            self.io.roundingMode,
            postmul_regs).bits
        roundingMode_stage0                      /= pipe_valid(
            self.io.validin, 
            self.io.roundingMode,
            postmul_regs).bits
        detectTininess_stage0                    /= pipe_valid(
            self.io.validin, 
            self.io.detectTininess, 
            postmul_regs).bits
        valid_stage0                             /= pipe_valid(
            self.io.validin, 
            value(0).to_bits(), 
            postmul_regs).valid
        
        ##------------------------------------------------------------------------
        ##------------------------------------------------------------------------
        roundRawFNToRecFN = RoundRawFNToRecFN(
            'roundRawFNToRecFN', 
            expWidth = self.p.expWidth, 
            sigWidth = self.p.sigWidth, 
            options = 0)

        round_regs = 1 if(self.p.latency==2) else 0
        roundRawFNToRecFN.io.invalidExc         /= pipe_valid(
            valid_stage0, 
            mulAddRecFNToRaw_postMul.io.invalidExc, 
            round_regs).bits
        roundRawFNToRecFN.io.input              /= pipe_valid(
            valid_stage0, 
            mulAddRecFNToRaw_postMul.io.rawOut, 
            round_regs).bits
        roundRawFNToRecFN.io.roundingMode       /= pipe_valid(
            valid_stage0, 
            roundingMode_stage0, 
            round_regs).bits
        roundRawFNToRecFN.io.detectTininess     /= pipe_valid(
            valid_stage0, detectTininess_stage0,
            round_regs).bits
        self.io.validout                        /= pipe_valid(
            valid_stage0, 
            value(0).to_bits(), 
            round_regs).valid

        roundRawFNToRecFN.io.infiniteExc /= 0

        self.io.output            /= roundRawFNToRecFN.io.output
        self.io.exceptionFlags /= roundRawFNToRecFN.io.exceptionFlags

class zqh_fpu_fma_pipe(module):
    def set_par(self):
        super(zqh_fpu_fma_pipe, self).set_par()
        self.p = zqh_fpu_parameter()
        self.p.par('latency', None)
        self.p.par('t', None)

    def set_port(self):
        super(zqh_fpu_fma_pipe, self).set_port()
        assert(self.p.latency>0)
        self.io = zqh_fpu_fma_pipe_io('io')

    def main(self):
        super(zqh_fpu_fma_pipe, self).main()
        valid = reg('valid', next=self.io.input.valid)
        in_ = zqh_fp_input('in_').as_reg()
        with when (self.io.input.valid):
            one = 1 << (self.p.t.sig + self.p.t.exp - 1)
            zero = (
                (self.io.input.bits.in1 ^ self.io.input.bits.in2) & 
                (1 << (self.p.t.sig + self.p.t.exp)))
            cmd_fma = self.io.input.bits.ren3
            cmd_addsub = self.io.input.bits.swap23
            in_ /= self.io.input.bits
            with when (cmd_addsub):
                in_.in2 /= one 
            with when (~(cmd_fma | cmd_addsub)):
                in_.in3 /= zero 

        fma = zqh_mul_add_rec_fn_pipe(
            'fma', 
            latency = min(self.p.latency-1, 2), 
            expWidth = self.p.t.exp, 
            sigWidth = self.p.t.sig)
        fma.io.validin /= valid
        fma.io.op /= in_.fmaCmd
        fma.io.roundingMode /= in_.rm
        fma.io.detectTininess /= consts.tininess_afterRounding()
        fma.io.a /= in_.in1
        fma.io.b /= in_.in2
        fma.io.c /= in_.in3

        res = zqh_fp_result('res')
        res.data /= self.p.sanitizeNaN(fma.io.output, self.p.t)
        res.exc /= fma.io.exceptionFlags

        self.io.output /= pipe_valid(fma.io.validout, res, max(self.p.latency-3, 0))

class zqh_fpu(module):
    def set_par(self):
        super(zqh_fpu, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_port(self):
        super(zqh_fpu, self).set_port()
        self.io = zqh_fpu_io('io')

    def main(self):
        super(zqh_fpu, self).main()
        self.io.inst.ready /= 1

        ex_reg_valid = reg_r('ex_reg_valid', next=self.io.inst.valid)
        req_valid = ex_reg_valid | self.io.cp_req.valid
        ex_reg_inst = reg_en(
            'ex_reg_inst',
            w = self.io.inst.bits.get_w(),
            next = self.io.inst.bits,
            en = self.io.inst.valid)
        ex_cp_valid = self.io.cp_req.fire()
        mem_cp_valid = reg_r('mem_cp_valid', next = ex_cp_valid)
        wb_cp_valid = reg_r('wb_cp_valid', next = mem_cp_valid)
        mem_reg_valid = reg_r('mem_reg_valid')
        killm = (self.io.killm | self.io.nack_mem) & ~mem_cp_valid
        ## Kill X-stage instruction if M-stage is killed.  This prevents it from
        ## speculatively being sent to the div-sqrt unit, which can cause priority
        ## inversion for two back-to-back divides, the first of which is killed.
        killx = self.io.killx | (mem_reg_valid & killm)
        mem_reg_valid /= (ex_reg_valid & ~killx) | ex_cp_valid
        mem_reg_inst = reg_en(
            'mem_reg_inst', 
            w = ex_reg_inst.get_w(),
            next = ex_reg_inst, 
            en = ex_reg_valid)
        wb_reg_valid = reg_r('wb_reg_valid', next=mem_reg_valid & (~killm | mem_cp_valid))

        fp_decoder = zqh_fpu_decoder('fp_decoder')
        fp_decoder.io.inst /= self.io.inst.bits

        cp_ctrl = zqh_fpu_ctrl_sigs('cp_ctrl')
        cp_ctrl /= self.io.cp_req.bits
        self.io.cp_resp.valid /= 0
        self.io.cp_resp.bits.data /= 0

        id_ctrl = fp_decoder.io.sigs
        ex_ctrl = mux(
            ex_cp_valid,
            cp_ctrl,
            zqh_fpu_ctrl_sigs().as_reg(
                tp = 'reg_en',
                next = id_ctrl,
                en = self.io.inst.valid))
        mem_ctrl = zqh_fpu_ctrl_sigs('mem_ctrl').as_reg(
            tp = 'reg_en',
            next = ex_ctrl,
            en = req_valid)
        wb_ctrl = zqh_fpu_ctrl_sigs('wb_ctrl').as_reg(
            tp = 'reg_en',
            next = mem_ctrl,
            en = mem_reg_valid)

        ## load response
        load_wb = reg('load_wb', next = self.io.lsu_resp.valid)
        load_wb_double = reg_en(
            'load_wb_double',
            next = self.io.lsu_resp.bits.type[0],
            en = self.io.lsu_resp.valid)
        load_wb_data = reg_en(
            'load_wb_data',
            w = self.io.lsu_resp.bits.data.get_w(),
            next = self.io.lsu_resp.bits.data,
            en = self.io.lsu_resp.valid)
        load_wb_tag = reg_en(
            'load_wb_tag',
            w = self.io.lsu_resp.bits.tag.get_w(),
            next = self.io.lsu_resp.bits.tag,
            en = self.io.lsu_resp.valid)

        ## regfile
        regfile = vec(
            'regfile',
            gen = lambda _: reg(_, w = self.p.flen+1),
            n = self.p.num_gprs)
        with when(load_wb):
            wdata = self.p.recode(load_wb_data, load_wb_double)
            regfile(load_wb_tag, wdata)
            vassert(self.p.consistent(wdata))
            #no need if (self.p.enableCommitLog):
            #no need     vprintln("f%d p%d 0x%x", (load_wb_tag, load_wb_tag + 32, load_wb_data))

        ex_ra = list(map(lambda _: reg('ex_ra_'+str(_), w = 5), range(3)))
        ex_rs = list(map(lambda a: regfile[a], ex_ra))

        with when (self.io.inst.valid):
            with when (id_ctrl.ren1):
                with when (~id_ctrl.swap12):
                    ex_ra[0] /= self.io.inst.bits[19:15] 
                with when (id_ctrl.swap12):
                    ex_ra[1] /= self.io.inst.bits[19:15] 
            with when (id_ctrl.ren2):
                with when (id_ctrl.swap12):
                    ex_ra[0] /= self.io.inst.bits[24:20] 
                with when (id_ctrl.swap23):
                    ex_ra[2] /= self.io.inst.bits[24:20] 
                with when (~id_ctrl.swap12 & ~id_ctrl.swap23):
                    ex_ra[1] /= self.io.inst.bits[24:20] 
            with when (id_ctrl.ren3):
                ex_ra[2] /= self.io.inst.bits[31:27] 
        ex_rm = mux(ex_reg_inst[14:12] == 7, self.io.fcsr_rm, ex_reg_inst[14:12])

        def fuInput(minT):
          req = zqh_fp_input()
          tag = ~ex_ctrl.singleIn ## TODO typeTag
          req /= ex_ctrl
          req.rm /= ex_rm
          req.in1 /= self.p.unbox(ex_rs[0], tag, minT)
          req.in2 /= self.p.unbox(ex_rs[1], tag, minT)
          req.in3 /= self.p.unbox(ex_rs[2], tag, minT)
          req.typ /= ex_reg_inst[21:20]
          req.fmaCmd /= ex_reg_inst[3:2] | (~ex_ctrl.ren3 & ex_reg_inst[27])
          with when (ex_cp_valid):
              req /= self.io.cp_req.bits
              with when (self.io.cp_req.bits.swap23):
                req.in2 /= self.io.cp_req.bits.in3
                req.in3 /= self.io.cp_req.bits.in2
          return req

        fma_s = zqh_fpu_fma_pipe('fma_s', latency = self.p.sfmaLatency, t = zqh_f_type.S())
        fma_s.io.input.valid /= req_valid & ex_ctrl.fma & ex_ctrl.singleOut
        fma_s.io.input.bits /= fuInput(fma_s.p.t)

        fp2int = zqh_fp_to_int('fp2int', latency = 1)
        fp2int.io.input.valid /= req_valid & (
            ex_ctrl.toint |
            ex_ctrl.div |
            ex_ctrl.sqrt |
            (ex_ctrl.fastpipe & ex_ctrl.wflags))
        fp2int.io.input.bits /= fuInput(None)
        self.io.store_data.valid /= fp2int.io.output.valid
        self.io.store_data.bits /= fp2int.io.output.bits.store
        self.io.toint_data.valid /= fp2int.io.output.valid
        self.io.toint_data.bits /= fp2int.io.output.bits.toint
        with when(fp2int.io.output.valid & mem_cp_valid & mem_ctrl.toint):
            self.io.cp_resp.bits.data /= fp2int.io.output.bits.toint
            self.io.cp_resp.valid /= 1

        int2fp = zqh_int_to_fp('int2fp', latency = 2)
        int2fp.io.input.valid /= req_valid & ex_ctrl.fromint
        int2fp.io.input.bits /= fp2int.io.input.bits
        int2fp.io.input.bits.in1 /= mux(
            ex_cp_valid, 
            self.io.cp_req.bits.in1, 
            self.io.fromint_data)

        fp2fp = zqh_fp_to_fp('fp2fp', latency = 2)
        fp2fp.io.input.valid /= req_valid & ex_ctrl.fastpipe
        fp2fp.io.input.bits /= fp2int.io.input.bits
        fp2fp.io.lt /= fp2int.io.output.bits.lt

        divSqrt_wen = bits('divSqrt_wen', init = 0)
        divSqrt_inFlight = bits('divSqrt_inFlight', init = 0)
        divSqrt_waddr = reg('divSqrt_waddr', w = 5)
        divSqrt_typeTag = bits('divSqrt_typeTag', w = log2_up(len(self.p.floatTypes)))
        divSqrt_wdata = bits('divSqrt_wdata', w = self.p.flen+1)
        divSqrt_flags = bits('divSqrt_flags', w = zqh_fp_constants.FLAGS_SZ)

        ## writeback arbitration
        class Pipe(object):
            def __init__(self, p, lat, cond, res):
                self.p = p
                self.lat = lat
                self.cond = cond
                self.res = res

        if (self.p.flen > 32):
            fma_d = zqh_fpu_fma_pipe(
                'fma_d', 
                latency = self.p.dfmaLatency, 
                t = zqh_f_type.D())
            fma_d.io.input.valid /= req_valid & ex_ctrl.fma & ~ex_ctrl.singleOut
            fma_d.io.input.bits /= fuInput(fma_d.p.t)
        pipes = [
            Pipe(
                fp2fp,
                fp2fp.p.latency,
                lambda c: c.fastpipe,
                fp2fp.io.output.bits),
            Pipe(
                int2fp, 
                int2fp.p.latency,
                lambda c: c.fromint,
                int2fp.io.output.bits),
            Pipe(
                fma_s,
                fma_s.p.latency,
                lambda c: c.fma & c.singleOut,
                fma_s.io.output.bits)]
        if (self.p.flen > 32):
            pipes.append(Pipe(
                fma_d,
                fma_d.p.latency,
                lambda c: c.fma & ~c.singleOut,
                fma_d.io.output.bits))

        def latencyMask(c, offset):
            assert(all(list(map(lambda _: _.lat >= offset, pipes))))
            return reduce(
                lambda x, y: x | y, list(map(
                    lambda p: mux(
                        p.cond(c),
                        value(1 << p.lat-offset),
                        value(0)),
                    pipes)))
        def pipeid(c):
            return reduce(
                lambda x, y: x | y,
                list(map(
                    lambda p: mux(p[0].cond(c), value(p[1]), value(0)),
                    list(zip(pipes, range(len(pipes)))))))
        maxLatency = max(list(map(lambda _: _.lat, pipes)))
        memLatencyMask = latencyMask(mem_ctrl, 2)

        class WBInfo(bundle):
            def set_var(self):
                super(WBInfo, self).set_var()
                self.var(bits('rd', w = 5))
                self.var(bits('single'))
                self.var(bits('cp'))
                self.var(bits('pipeid', w = log2_ceil(len(pipes))))

        wen = reg_r('wen', w = maxLatency-1)
        wbInfo = vec('wbInfo', gen = WBInfo, n = maxLatency-1).as_reg()
        mem_wen = mem_reg_valid & (mem_ctrl.fma | mem_ctrl.fastpipe | mem_ctrl.fromint)
        write_port_busy = reg_en(
            'write_port_busy',
            next = 
                (mem_wen & (memLatencyMask & latencyMask(ex_ctrl, 1)).r_or()) |
                (wen & latencyMask(ex_ctrl, 0)).r_or(),
            en = req_valid)

        for i in range(maxLatency-2):
            with when (wen[i+1]):
                wbInfo[i] /= wbInfo[i+1]
        wen /= wen >> 1
        with when (mem_wen):
            with when (~killm):
                wen /= wen >> 1 | memLatencyMask
            for i in range(maxLatency-1):
                with when (~write_port_busy & memLatencyMask[i]):
                    wbInfo[i].cp /= mem_cp_valid
                    wbInfo[i].single /= mem_ctrl.singleOut
                    wbInfo[i].pipeid /= pipeid(mem_ctrl)
                    wbInfo[i].rd /= mem_reg_inst[11:7]

        waddr = mux(divSqrt_wen, divSqrt_waddr, wbInfo[0].rd)
        wdouble = mux(divSqrt_wen, divSqrt_typeTag, ~wbInfo[0].single)
        wdata = self.p.box2(
            mux(
                divSqrt_wen,
                divSqrt_wdata,
                sel_bin(wbInfo[0].pipeid, list(map(lambda _: _.res.data, pipes)))),
            wdouble)
        wexc = sel_bin(wbInfo[0].pipeid, list(map(lambda _: _.res.exc, pipes)))
        with when ((~wbInfo[0].cp & wen[0]) | divSqrt_wen):
            vassert(self.p.consistent(wdata))
            regfile(waddr, wdata)
            #no need if (self.p.enableCommitLog):
            #no need     vprintln("f%d p%d 0x%x", (waddr, waddr + 32, self.p.ieee(wdata)))
        with when (wbInfo[0].cp & wen[0]):
            self.io.cp_resp.bits.data /= wdata
            self.io.cp_resp.valid /= 1
        self.io.cp_req.ready /= ~ex_reg_valid

        wb_toint_valid = wb_reg_valid & wb_ctrl.toint
        wb_toint_exc = reg_en(
            'wb_toint_exc',
            w = fp2int.io.output.bits.exc.get_w(),
            next = fp2int.io.output.bits.exc, en = mem_ctrl.toint)
        self.io.fcsr_flags.valid /= wb_toint_valid | divSqrt_wen | wen[0]
        self.io.fcsr_flags.bits /= (
            mux(wb_toint_valid, wb_toint_exc, value(0)) | 
            mux(divSqrt_wen, divSqrt_flags, value(0)) | 
            mux(wen[0], wexc, value(0)))

        divSqrt_write_port_busy = (mem_ctrl.div | mem_ctrl.sqrt) & wen.r_or()
        self.io.fcsr_rdy /= ~(
            (ex_reg_valid & ex_ctrl.wflags) |
            (mem_reg_valid & mem_ctrl.wflags) |
            (wb_reg_valid & wb_ctrl.toint) |
            wen.r_or() |
            divSqrt_inFlight)
        self.io.nack_mem /= write_port_busy | divSqrt_write_port_busy | divSqrt_inFlight
        self.io.dec /= fp_decoder.io.sigs
        def useScoreboard(f):
            return reduce(
                lambda x, y: x | y,
                list(map(
                    lambda x: f(x),
                    list(filter(
                        lambda _: _[0].lat > 3,
                        list(zip(pipes, range(len(pipes)))))))),
                value(0).to_bits())
        self.io.sboard_set /= (
            wb_reg_valid &
            ~wb_cp_valid &
            reg(
                next = 
                    useScoreboard(lambda _: _[0].cond(mem_ctrl)) | 
                    mem_ctrl.div | 
                    mem_ctrl.sqrt))
        self.io.sboard_clr /= (
            ~wb_cp_valid &
            (
                divSqrt_wen | 
                (
                    wen[0] & 
                    useScoreboard(lambda x: wbInfo[0].pipeid == value(x[1])))))
        self.io.sboard_clra /= waddr
        ## we don't currently support round-max-magnitude (rm=4)
        self.io.illegal_rm /= (
            self.io.inst.bits[14:12].match_any([5, 6]) |
            ((self.io.inst.bits[14:12] == 7) & (self.io.fcsr_rm >= 5)))

        if (self.p.divSqrt):
            divSqrt_killed = reg('divSqrt_killed')
            t_idx = 0
            for t in self.p.floatTypes:
                tag = ~mem_ctrl.singleOut ## TODO typeTag
                divSqrt = DivSqrtRecFN_small(
                    'divSqrt_'+str(t_idx),
                    expWidth = t.exp,
                    sigWidth = t.sig,
                    options = 0)
                divSqrt.io.input.valid /= (
                     mem_reg_valid &
                     (tag == self.p.typeTag(t)) &
                     (mem_ctrl.div | mem_ctrl.sqrt) &
                     ~divSqrt_inFlight)
                divSqrt.io.input.bits.sqrtOp /= mem_ctrl.sqrt
                divSqrt.io.input.bits.a /= self.p.maxType.unsafeConvert(
                    fp2int.io.output.bits.input.in1, t)
                divSqrt.io.input.bits.b /= self.p.maxType.unsafeConvert(
                    fp2int.io.output.bits.input.in2, t)
                divSqrt.io.input.bits.roundingMode /= fp2int.io.output.bits.input.rm
                divSqrt.io.input.bits.detectTininess /= consts.tininess_afterRounding()

                with when (~divSqrt.io.input.ready):
                    divSqrt_inFlight /= 1
                ## only 1 in flight

                with when (divSqrt.io.input.fire()):
                    divSqrt_killed /= killm
                    divSqrt_waddr /= mem_reg_inst[11:7]

                with when (divSqrt.io.output.fire()):
                    divSqrt_wen /= ~divSqrt_killed
                    divSqrt_wdata /= self.p.sanitizeNaN(divSqrt.io.output.bits.data, t)
                    divSqrt_flags /= divSqrt.io.output.bits.exceptionFlags
                    divSqrt_typeTag /= self.p.typeTag(t)
                t_idx = t_idx + 1
        else:
            with when (id_ctrl.div | id_ctrl.sqrt):
                self.io.illegal_rm /= 1

class zqh_fpu_slow(module):
    def set_par(self):
        super(zqh_fpu_slow, self).set_par()
        self.p = zqh_fpu_parameter()

    def set_port(self):
        super(zqh_fpu_slow, self).set_port()
        self.io = zqh_fpu_io('io')

    def main(self):
        super(zqh_fpu_slow, self).main()

        inst = self.io.inst.bits
        inst_buf = reg('inst_buf', w = self.io.inst.bits.get_w())
        fp_decoder = zqh_fpu_decoder('fp_decoder')
        fp_decoder.io.inst /= inst
        inst_ctrl = fp_decoder.io.sigs
        inst_ctrl_buf = zqh_fpu_ctrl_sigs('inst_ctrl_buf').as_reg()

        regfile = vec(
            'regfile', 
            gen = lambda _: reg(_, w = self.p.flen+1),
            n = self.p.num_gprs)
        fma_s = zqh_fpu_fma_pipe(
            'fma_s',
            latency = self.p.sfmaLatency,
            t = zqh_f_type.S())
        fp2int = zqh_fp_to_int('fp2int')
        int2fp = zqh_int_to_fp('int2fp', latency = 2)
        fp2fp = zqh_fp_to_fp('fp2fp', latency = 2)
        if (self.p.flen > 32):
            fma_d = zqh_fpu_fma_pipe(
                'fma_d',
                latency = self.p.dfmaLatency,
                t = zqh_f_type.D())
        if (self.p.divSqrt):
          div_sqrt_s = DivSqrtRecFN_small(
                'div_sqrt_s',
                expWidth = zqh_f_type.S().exp, 
                sigWidth = zqh_f_type.S().sig,
                options = 0)
          if (self.p.flen > 32):
              div_sqrt_d = DivSqrtRecFN_small(
                  'div_sqrt_d',
                  expWidth = zqh_f_type.D().exp, 
                  sigWidth = zqh_f_type.D().sig, 
                  options = 0)


        ####
        #FSM state control
        (s_ready, s_busy, s_done) = range(3)
        state = reg_rs('state', w = 2, rs = s_ready)
        pipe_resp_valid = bits('pipe_resp_valid', init = 0)
        state_is_ready = state == s_ready
        state_is_busy = state == s_busy
        
        with when(state == s_ready):
            with when(self.io.inst.fire()):
                with when(inst_ctrl.fromint | inst_ctrl.toint | inst_ctrl.fastpipe |
                    inst_ctrl.fma | inst_ctrl.div | inst_ctrl.sqrt):
                    state /= s_busy
                    inst_ctrl_buf /= inst_ctrl
                    inst_buf /= inst
        with when(state == s_busy):
            with when(pipe_resp_valid):
                state /= s_done
        with when(state == s_done):
            state /= s_ready

        self.io.inst.ready /= state_is_ready


        inst_ra = list(map(lambda _: bits('inst_ra_'+str(_), w = 5), range(3)))
        inst_rs = list(map(lambda a: regfile[a], inst_ra))
        with when (self.io.inst.valid):
            with when (inst_ctrl.ren1):
                with when (~inst_ctrl.swap12):
                    inst_ra[0] /= self.io.inst.bits[19:15] 
                with when (inst_ctrl.swap12):
                    inst_ra[1] /= self.io.inst.bits[19:15] 
            with when (inst_ctrl.ren2):
                with when (inst_ctrl.swap12):
                    inst_ra[0] /= self.io.inst.bits[24:20] 
                with when (inst_ctrl.swap23):
                    inst_ra[2] /= self.io.inst.bits[24:20] 
                with when (~inst_ctrl.swap12 & ~inst_ctrl.swap23):
                    inst_ra[1] /= self.io.inst.bits[24:20] 
            with when (inst_ctrl.ren3):
                inst_ra[2] /= self.io.inst.bits[31:27] 

        def fuInput(minT):
          req = zqh_fp_input()
          tag = ~inst_ctrl.singleIn
          req /= inst_ctrl
          req.rm /= mux(inst[14:12] == 7, self.io.fcsr_rm, inst[14:12])
          req.in1 /= self.p.unbox(inst_rs[0], tag, minT)
          req.in2 /= self.p.unbox(inst_rs[1], tag, minT)
          req.in3 /= self.p.unbox(inst_rs[2], tag, minT)
          req.typ /= inst[21:20]
          req.fmaCmd /= inst[3:2] | (~inst_ctrl.ren3 & inst[27])
          return req
        
        fu_in_default = fuInput(None)

        ####
        #int to fp
        int2fp.io.input.valid /= state_is_ready & self.io.inst.fire() & inst_ctrl.fromint
        int2fp.io.input.bits /= fu_in_default
        int2fp.io.input.bits.in1 /= self.io.fromint_data


        ####
        #fp to int
        fp2int.io.input.valid /= (
            state_is_ready & 
            self.io.inst.fire() & 
            (
                inst_ctrl.toint | 
                inst_ctrl.div | 
                inst_ctrl.sqrt | 
                (inst_ctrl.fastpipe & inst_ctrl.wflags)))
        fp2int.io.input.bits /= fu_in_default
        self.io.store_data.valid /= fp2int.io.output.valid
        self.io.store_data.bits /= fp2int.io.output.bits.store
        self.io.toint_data.valid /= fp2int.io.output.valid
        self.io.toint_data.bits /= fp2int.io.output.bits.toint


        ####
        #fp to fp
        fp2fp.io.input.valid /= state_is_ready & self.io.inst.fire() & inst_ctrl.fastpipe
        fp2fp.io.input.bits /= fu_in_default
        fp2fp.io.lt /= (
            reg(next = fp2int.io.output.bits.lt) if (fp2int.p.latency is None) else 
            fp2int.io.output.bits.lt)


        ####
        #single float multiply and add
        fma_s.io.input.valid /= (
            state_is_ready & 
            self.io.inst.fire() & 
            inst_ctrl.fma & 
            inst_ctrl.singleOut)
        fma_s.io.input.bits /= fuInput(fma_s.p.t)


        ####
        #double float multiply and add
        fma_d.io.input.valid /= state_is_ready & self.io.inst.fire() & inst_ctrl.fma & ~inst_ctrl.singleOut
        fma_d.io.input.bits /= fuInput(fma_d.p.t)


        ####
        #div/sqrt
        if (self.p.divSqrt):
            div_sqrt_s.io.input.valid /= (
                state_is_ready & 
                self.io.inst.fire() & 
                inst_ctrl.singleOut & 
                (inst_ctrl.div | inst_ctrl.sqrt))
            div_sqrt_s.io.input.bits.sqrtOp /= inst_ctrl.sqrt
            div_sqrt_s.io.input.bits.a /= self.p.maxType.unsafeConvert(
                fp2int.io.output.bits.input.in1,
                zqh_f_type.S())
            div_sqrt_s.io.input.bits.b /= self.p.maxType.unsafeConvert(
                fp2int.io.output.bits.input.in2,
                zqh_f_type.S())
            div_sqrt_s.io.input.bits.roundingMode /= fp2int.io.output.bits.input.rm
            div_sqrt_s.io.input.bits.detectTininess /= consts.tininess_afterRounding()

            if (self.p.flen > 32):
                div_sqrt_d.io.input.valid /= (
                    state_is_ready & 
                    self.io.inst.fire() & 
                    ~inst_ctrl.singleOut & 
                    (inst_ctrl.div | inst_ctrl.sqrt))
                div_sqrt_d.io.input.bits.sqrtOp /= inst_ctrl.sqrt
                div_sqrt_d.io.input.bits.a /= self.p.maxType.unsafeConvert(
                    fp2int.io.output.bits.input.in1,
                    zqh_f_type.D())
                div_sqrt_d.io.input.bits.b /= self.p.maxType.unsafeConvert(
                    fp2int.io.output.bits.input.in2, 
                    zqh_f_type.D())
                div_sqrt_d.io.input.bits.roundingMode /= fp2int.io.output.bits.input.rm
                div_sqrt_d.io.input.bits.detectTininess /= consts.tininess_afterRounding()


        ####
        #lsu load response write regfile
        with when (self.io.lsu_resp.valid):
            wdata = self.p.recode(
                self.io.lsu_resp.bits.data,
                self.io.lsu_resp.bits.type[0])
            regfile(self.io.lsu_resp.bits.tag, wdata)
            vassert(self.p.consistent(wdata))


        pipe_resp_valid /= (
            (inst_ctrl_buf.fromint & int2fp.io.output.valid) |
            (inst_ctrl_buf.fastpipe & fp2fp.io.output.valid) |
            (inst_ctrl_buf.fma & inst_ctrl_buf.singleOut & fma_s.io.output.valid) |
            (inst_ctrl_buf.fma & ~inst_ctrl_buf.singleOut & fma_d.io.output.valid) |
            (inst_ctrl_buf.div & inst_ctrl_buf.singleOut & div_sqrt_s.io.output.valid) |
            (inst_ctrl_buf.div & ~inst_ctrl_buf.singleOut & div_sqrt_d.io.output.valid) |
            (inst_ctrl_buf.sqrt & inst_ctrl_buf.singleOut & div_sqrt_s.io.output.valid) |
            (inst_ctrl_buf.sqrt & ~inst_ctrl_buf.singleOut & div_sqrt_d.io.output.valid) |
            (inst_ctrl_buf.toint))


        wen_toint = self.io.inst.fire() & inst_ctrl.toint
        wen = inst_ctrl_buf.wen & pipe_resp_valid
        waddr = inst_buf[11:7]
        wdouble = ~inst_ctrl_buf.singleOut
        wdata_map = [
            (
                int2fp.io.output.valid,
                int2fp.io.output.bits.data,
                int2fp.io.output.bits.exc),
            (
                fp2fp.io.output.valid,
                fp2fp.io.output.bits.data,
                fp2fp.io.output.bits.exc),
            (
                fma_s.io.output.valid,
                fma_s.io.output.bits.data,
                fma_s.io.output.bits.exc),
            (
                fma_d.io.output.valid,
                fma_d.io.output.bits.data,
                fma_d.io.output.bits.exc),
            (div_sqrt_s.io.output.valid, self.p.sanitizeNaN(
                div_sqrt_s.io.output.bits.data,
                zqh_f_type.S()), div_sqrt_s.io.output.bits.exceptionFlags),
            (div_sqrt_d.io.output.valid, self.p.sanitizeNaN(
                div_sqrt_d.io.output.bits.data,
                zqh_f_type.D()), div_sqrt_d.io.output.bits.exceptionFlags)]
        wdata = self.p.box2(
            sel_oh(map(lambda _:_[0], wdata_map), map(lambda _: _[1], wdata_map)),
            wdouble)
        wexc = sel_oh(map(lambda _:_[0], wdata_map), map(lambda _: _[2], wdata_map))

        with when (wen):
            vassert(self.p.consistent(wdata))
            regfile(waddr, wdata)

        wb_toint_exc = fp2int.io.output.bits.exc
        self.io.fcsr_flags.valid /= wen_toint | wen
        self.io.fcsr_flags.bits /= mux(wen_toint, wb_toint_exc, mux(wen, wexc, 0))


        self.io.sboard_set /= state_is_ready & self.io.inst.fire() & inst_ctrl.wen
        self.io.sboard_clr /= wen
        self.io.sboard_clra /= waddr


        self.io.illegal_rm /= (
            self.io.inst.bits[14:12].match_any([5, 6]) | 
            ((self.io.inst.bits[14:12] == 7) & (self.io.fcsr_rm >= 5)))

        self.io.fcsr_rdy /= state_is_ready

        self.io.dec /= fp_decoder.io.sigs
