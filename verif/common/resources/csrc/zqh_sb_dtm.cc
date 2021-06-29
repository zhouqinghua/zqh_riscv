#include <math.h>
#include <assert.h>
#include "zqh_sb_dtm.h"
#include "debug_defines.h"

sb_dtm_t::sb_dtm_t(int argc, char** argv)
  : dtm_t(argc, argv)
{
}

sb_dtm_t::~sb_dtm_t()
{
}

#define DMI_SBCS_SBBUSY_OFFSET        21
#define DMI_SBCS_SBBUSY_LENGTH        1
#define DMI_SBCS_SBBUSY               (0x1 << DMI_SBCS_SBBUSY_OFFSET)

#define DMI_SBCS_SBBUSYERROR_OFFSET        22
#define DMI_SBCS_SBBUSYERROR_LENGTH        1
#define DMI_SBCS_SBBUSYERROR               (0x1 << DMI_SBCS_SBBUSYERROR_OFFSET)

void sb_dtm_t::read_chunk(uint64_t taddr, size_t len, void* dst)
{
  uint32_t data[2];

  uint8_t * curr = (uint8_t*) dst;

  printf("zqh: read_chunk\n");
  printf("zqh: read_chunk taddr = 0x%x\n", taddr);
  printf("zqh: read_chunk len = %d\n", len);

  for (size_t i = 0; i < (len * 8 / new_xlen); i++){
    //set sbcs
    write(DMI_SBCS, DMI_SBCS_SBBUSYERROR | DMI_SBCS_SBSINGLEREAD | (((uint32_t)log2(new_xlen/8)) << DMI_SBCS_SBACCESS_OFFSET) | DMI_SBCS_SBERROR);

    //set access address
    data[0] = (uint32_t) (taddr + i*new_xlen/8);
    if (new_xlen > 32) {
      data[1] = (uint32_t) ((taddr + i*new_xlen/8) >> 32);
      write(DMI_SBADDRESS1, data[1]);
    }
    write(DMI_SBADDRESS0, data[0]);


    //wait done
    uint32_t sbcs_rd_data;
    uint32_t sbcs_busy = 1;
    uint32_t sbcs_error;
    while(sbcs_busy) {
        sbcs_rd_data = read(DMI_SBCS);
        sbcs_busy = (sbcs_rd_data & DMI_SBCS_SBBUSY) >> DMI_SBCS_SBBUSY_OFFSET;
        sbcs_error = (sbcs_rd_data & DMI_SBCS_SBERROR) >> DMI_SBCS_SBERROR_OFFSET;
    }
    assert(sbcs_error == 0);



    //readout data
    data[1] = read(DMI_SBDATA1);
    data[0] = read(DMI_SBDATA0);
    memcpy(curr, data, new_xlen/8);
    curr += new_xlen/8;
    printf("zqh: read_chunk data0 = 0x%x\n", data[0]);
    printf("zqh: read_chunk data1 = 0x%x\n", data[1]);
    printf("zqh: read_chunk done %d\n", i);
  }
}

void sb_dtm_t::write_chunk(uint64_t taddr, size_t len, const void* src)
{  
  uint32_t data[2];
  const uint8_t * curr = (const uint8_t*) src;

  printf("zqh: write_chunk\n");
  printf("zqh: write_chunk taddr = 0x%x\n", taddr);
  printf("zqh: write_chunk len = %d\n", len);
  for (size_t i = 0; i < (len * 8 / new_xlen); i++){
    //set sbcs
    write(DMI_SBCS, DMI_SBCS_SBBUSYERROR | (((uint32_t)log2(new_xlen/8)) << DMI_SBCS_SBACCESS_OFFSET) | DMI_SBCS_SBERROR);

    //set address
    data[0] = (uint32_t) (taddr + i*new_xlen/8);
    if (new_xlen > 32) {
      data[1] = (uint32_t) ((taddr + i*new_xlen/8) >> 32);
      write(DMI_SBADDRESS1, data[1]);
    }
    write(DMI_SBADDRESS0, data[0]);

    memcpy(data, curr, new_xlen/8);
    curr += new_xlen/8;
    if (new_xlen == 64) {
      write(DMI_SBDATA1, data[1]);
    }
    write(DMI_SBDATA0, data[0]);

    //wait done
    uint32_t sbcs_rd_data;
    uint32_t sbcs_busy = 1;
    uint32_t sbcs_error;
    while(sbcs_busy) {
        sbcs_rd_data = read(DMI_SBCS);
        sbcs_busy = (sbcs_rd_data & DMI_SBCS_SBBUSY) >> DMI_SBCS_SBBUSY_OFFSET;
        sbcs_error = (sbcs_rd_data & DMI_SBCS_SBERROR) >> DMI_SBCS_SBERROR_OFFSET;
    }
    assert(sbcs_error == 0);

    printf("zqh: write_chunk data0 = 0x%x\n", data[0]);
    printf("zqh: write_chunk data1 = 0x%x\n", data[1]);
    printf("zqh: write_chunk done %d\n", i);

  }


}

void sb_dtm_t::clear_chunk(uint64_t taddr, size_t len)
{
    printf("zqh: clear_chunk\n");
    printf("zqh: clear_chunk taddr = 0x%x\n", taddr);
    printf("zqh: clear_chunk len = 0x%x\n", len);
    const uint8_t curr[8] = {0,0,0,0,0,0,0,0};
    for (int i = 0; i < len*8/new_xlen; i++) {
        write_chunk(taddr + i * (new_xlen/8), new_xlen/8, curr);
    }
    printf("zqh: clear_chunk done\n");
}

