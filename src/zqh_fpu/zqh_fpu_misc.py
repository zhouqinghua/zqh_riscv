#source code coming from: https://github.com/chipsalliance/rocket-chip/blob/master/src/main/scala/tile/FPU.scala
#re-write by python and do some modifications

import sys
import os
from phgl_imp import *

class zqh_fp_constants(object):
    RM_SZ = 3
    FLAGS_SZ = 5
