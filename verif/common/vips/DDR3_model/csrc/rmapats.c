// file = 0; split type = patterns; threshold = 100000; total count = 0.
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include "rmapats.h"

scalar dummyScalar;
scalar fScalarIsForced=0;
scalar fScalarIsReleased=0;
scalar fScalarHasChanged=0;
scalar fForceFromNonRoot=0;
scalar fNettypeIsForced=0;
scalar fNettypeIsReleased=0;
void  hsG_0 (struct dummyq_struct * I1093, EBLK  * I1094, U  I651);
void  hsG_0 (struct dummyq_struct * I1093, EBLK  * I1094, U  I651)
{
    U  I1337;
    U  I1338;
    U  I1339;
    struct futq * I1340;
    I1337 = ((U )vcs_clocks) + I651;
    I1339 = I1337 & ((1 << fHashTableSize) - 1);
    I1094->I697 = (EBLK  *)(-1);
    I1094->I701 = I1337;
    if (I1337 < (U )vcs_clocks) {
        I1338 = ((U  *)&vcs_clocks)[1];
        sched_millenium(I1093, I1094, I1338 + 1, I1337);
    }
    else if ((peblkFutQ1Head != ((void *)0)) && (I651 == 1)) {
        I1094->I702 = (struct eblk *)peblkFutQ1Tail;
        peblkFutQ1Tail->I697 = I1094;
        peblkFutQ1Tail = I1094;
    }
    else if ((I1340 = I1093->I1053[I1339].I714)) {
        I1094->I702 = (struct eblk *)I1340->I713;
        I1340->I713->I697 = (RP )I1094;
        I1340->I713 = (RmaEblk  *)I1094;
    }
    else {
        sched_hsopt(I1093, I1094, I1337);
    }
}
void  hsM_0_0__simv_daidir (UB  * pcode, scalar  val)
{
    UB  * I1391;
    if (*(pcode + 0) == val) {
        return  ;
    }
    *(pcode + 0) = val;
    {
        RP  I1274;
        RP  * I691 = (RP  *)(pcode + 8);
        {
            I1274 = *I691;
            if (I1274) {
                hsimDispatchCbkMemOptNoDynElabS(I691, val, 0U);
            }
        }
    }
    {
        RmaNbaGate1  * I1188 = (RmaNbaGate1  *)(pcode + 16);
        scalar  I941 = X4val[val];
        I1188->I948.I788 = (void *)((RP )(((RP )(I1188->I948.I788) & ~0x3)) | (I941));
        NBA_Semiler(0, &I1188->I948);
    }
}
void  hsM_3_0__simv_daidir (UB  * pcode, scalar  val)
{
    UB  * I1391;
    *(pcode + 0) = val;
    {
        RP  I1274;
        RP  * I691 = (RP  *)(pcode + 8);
        {
            I1274 = *I691;
            if (I1274) {
                hsimDispatchCbkMemOptNoDynElabS(I691, val, 0U);
            }
        }
    }
    {
        RmaNbaGate1  * I1188 = (RmaNbaGate1  *)(pcode + 16);
        scalar  I941 = X4val[val];
        I1188->I948.I788 = (void *)((RP )(((RP )(I1188->I948.I788) & ~0x3)) | (I941));
        NBA_Semiler(0, &I1188->I948);
    }
}
#ifdef __cplusplus
extern "C" {
#endif
void SinitHsimPats(void);
#ifdef __cplusplus
}
#endif
