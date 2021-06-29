import sys
import os
from phgl_imp import *
sys.path.append("..")
from zqh_test_harness_common.zqh_test_harness_common_ut import zqh_test_harness_common_ut
from zqh_full_chip_r1.zqh_full_chip_r1_main import zqh_full_chip_r1

class zqh_test_harness_ut(zqh_test_harness_common_ut):
    def instance_dut(self):
        return zqh_full_chip_r1('dut')
