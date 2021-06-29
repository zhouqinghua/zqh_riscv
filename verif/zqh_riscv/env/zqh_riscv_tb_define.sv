//zqh_core tb define

//`define CLOCK_PERIOD 1.0
//`define U_DLY_IN 0.1
//`define U_DLY_OUT 0.1
`define RESET_DELAY 3777.7

//path define
`define ZQH_TOP top
`define ZQH_DUT top.test_harness.dut
`define ZQH_CORE_WRAP(N) `ZQH_DUT.system.tile.core_wrap_``N``
//`define ZQH_DUT1 top.DUT1

//tilelink
//{{{
`define ZQH_CORE_TILELINK_SIZE_W    4
`define ZQH_CORE_TILELINK_SOURCE_W  8
`define ZQH_CORE_TILELINK_ADDRESS_W 32
`define ZQH_CORE_TILELINK_MASK_W    8
`define ZQH_CORE_TILELINK_DATA_W    64
`define ZQH_CORE_TILELINK_SINK_W    8

typedef enum bit[2:0] {
    ZQH_CORE_TILELINK_A_OPCODE_PUT_FULL_DATA    = 0,
    ZQH_CORE_TILELINK_A_OPCODE_PUT_PARTIAL_DATA = 1,
    ZQH_CORE_TILELINK_A_OPCODE_ARITHMETIC_DATA  = 2,
    ZQH_CORE_TILELINK_A_OPCODE_LOGICAL_DATA     = 3,
    ZQH_CORE_TILELINK_A_OPCODE_GET              = 4,
    ZQH_CORE_TILELINK_A_OPCODE_INTENT           = 5,
    ZQH_CORE_TILELINK_A_OPCODE_ACQUIRE          = 6
} zqh_core_tilelink_a_opcode;

typedef enum bit[2:0] {
    ZQH_CORE_TILELINK_B_OPCODE_PUT_FULL_DATA    = 0,
    ZQH_CORE_TILELINK_B_OPCODE_PUT_PARTIAL_DATA = 1,
    ZQH_CORE_TILELINK_B_OPCODE_ARITHMETIC_DATA  = 2,
    ZQH_CORE_TILELINK_B_OPCODE_LOGICAL_DATA     = 3,
    ZQH_CORE_TILELINK_B_OPCODE_GET              = 4,
    ZQH_CORE_TILELINK_B_OPCODE_INTENT           = 5 
} zqh_core_tilelink_b_opcode;

typedef enum bit[2:0] {
    ZQH_CORE_TILELINK_C_OPCODE_ACCESS_ACK      = 0,
    ZQH_CORE_TILELINK_C_OPCODE_ACCESS_ACK_DATA = 1,
    ZQH_CORE_TILELINK_C_OPCODE_HINT_ACK        = 2,
    ZQH_CORE_TILELINK_C_OPCODE_PROBE_ACK       = 4,
    ZQH_CORE_TILELINK_C_OPCODE_PROBE_ACK_DATA  = 5,
    ZQH_CORE_TILELINK_C_OPCODE_RELEASE         = 6,
    ZQH_CORE_TILELINK_C_OPCODE_RELEASE_DATA    = 7
} zqh_core_tilelink_c_opcode;

typedef enum bit[2:0] {
    ZQH_CORE_TILELINK_D_OPCODE_ACCESS_ACK      = 0,
    ZQH_CORE_TILELINK_D_OPCODE_ACCESS_ACK_DATA = 1,
    ZQH_CORE_TILELINK_D_OPCODE_HINT_ACK        = 2,
    ZQH_CORE_TILELINK_D_OPCODE_GRANT           = 4,
    ZQH_CORE_TILELINK_D_OPCODE_GRANT_DATA      = 5,
    ZQH_CORE_TILELINK_D_OPCODE_RELEASE_ACK     = 6 
} zqh_core_tilelink_d_opcode;
//}}}

//axi4
//{{{
`define ZQH_CORE_AXI4_ID_W     8
`define ZQH_CORE_AXI4_ADDR_W   32 
`define ZQH_CORE_AXI4_LEN_W    8 
`define ZQH_CORE_AXI4_SIZE_W   3 
`define ZQH_CORE_AXI4_BURST_W  2 
`define ZQH_CORE_AXI4_CACHE_W  4 
`define ZQH_CORE_AXI4_PROT_W   3 
`define ZQH_CORE_AXI4_QOS_W    4 
`define ZQH_CORE_AXI4_REGION_W 0
`define ZQH_CORE_AXI4_USER_W   0
`define ZQH_CORE_AXI4_DATA_W   64
`define ZQH_CORE_AXI4_STRB_W   8
`define ZQH_CORE_AXI4_RESP_W   2

typedef enum bit[`ZQH_CORE_AXI4_RESP_W - 1 : 0] {
    ZQH_CORE_AXI4_RESP_OKAY = 0,
    ZQH_CORE_AXI4_RESP_EXOKAY = 1,
    ZQH_CORE_AXI4_RESP_SLVERR = 2,
    ZQH_CORE_AXI4_RESP_DECERR = 3 
} zqh_core_axi4_resp_code;

//}}}

//
//i2c
//{{{
typedef enum bit[3 : 0] {
    ZQH_CORE_I2C_SLAVE_IDLE        = 0,
    ZQH_CORE_I2C_SLAVE_START       = 1,
    ZQH_CORE_I2C_SLAVE_ADDR        = 2,
    ZQH_CORE_I2C_SLAVE_RX          = 3,
    ZQH_CORE_I2C_SLAVE_RX_ACK      = 4,
    ZQH_CORE_I2C_SLAVE_TX          = 5,
    ZQH_CORE_I2C_SLAVE_TX_ACK      = 6,
    ZQH_CORE_I2C_SLAVE_SCL_STRETCH = 7 
} zqh_core_i2c_slave_state;

typedef enum bit[3 : 0] {
    ZQH_CORE_I2C_MASTER_IDLE      = 0,
    ZQH_CORE_I2C_MASTER_START     = 1,
    ZQH_CORE_I2C_MASTER_WRITE     = 2,
    ZQH_CORE_I2C_MASTER_READ      = 3,
    ZQH_CORE_I2C_MASTER_STOP      = 4,
    ZQH_CORE_I2C_MASTER_ACK_W     = 5,
    ZQH_CORE_I2C_MASTER_ACK_R     = 6,
    ZQH_CORE_I2C_MASTER_HOLD      = 7 
} zqh_core_i2c_master_state;
//}}}


//DMI regs
`define DMI_SBCS                            32'h38

`define DMI_SBCS_SBBUSY_OFFSET        21
`define DMI_SBCS_SBBUSY_LENGTH        1
`define DMI_SBCS_SBBUSY               (32'h1 << `DMI_SBCS_SBBUSY_OFFSET)

`define DMI_SBCS_SBBUSYERROR_OFFSET        22
`define DMI_SBCS_SBBUSYERROR_LENGTH        1
`define DMI_SBCS_SBBUSYERROR               (32'h1 << `DMI_SBCS_SBBUSYERROR_OFFSET)

/*
* When a 1 is written here, triggers a read at the address in {\tt
* sbaddress} using the access size set by \Fsbaccess.
 */
`define DMI_SBCS_SBSINGLEREAD_OFFSET        20
`define DMI_SBCS_SBSINGLEREAD_LENGTH        1
`define DMI_SBCS_SBSINGLEREAD               (32'h1 << `DMI_SBCS_SBSINGLEREAD_OFFSET)
/*
* Select the access size to use for system bus accesses triggered by
* writes to the {\tt sbaddress} registers or \Rsbdatazero.
*
* 0: 8-bit
*
* 1: 16-bit
*
* 2: 32-bit
*
* 3: 64-bit
*
* 4: 128-bit
*
* If an unsupported system bus access size is written here,
* the DM may not perform the access, or may perform the access
* with any access size.
 */
`define DMI_SBCS_SBACCESS_OFFSET            17
`define DMI_SBCS_SBACCESS_LENGTH            3
`define DMI_SBCS_SBACCESS                   (32'h7 << `DMI_SBCS_SBACCESS_OFFSET)
/*
* When 1, the internal address value (used by the system bus master)
* is incremented by the access size (in bytes) selected in \Fsbaccess
* after every system bus access.
 */
`define DMI_SBCS_SBAUTOINCREMENT_OFFSET     16
`define DMI_SBCS_SBAUTOINCREMENT_LENGTH     1
`define DMI_SBCS_SBAUTOINCREMENT            (32'h1 << `DMI_SBCS_SBAUTOINCREMENT_OFFSET)
/*
* When 1, every read from \Rsbdatazero automatically triggers a system
* bus read at the new address.
 */
`define DMI_SBCS_SBAUTOREAD_OFFSET          15
`define DMI_SBCS_SBAUTOREAD_LENGTH          1
`define DMI_SBCS_SBAUTOREAD                 (32'h1 << `DMI_SBCS_SBAUTOREAD_OFFSET)
/*
* When the debug module's system bus
* master causes a bus error, this field gets set. The bits in this
* field remain set until they are cleared by writing 1 to them.
* While this field is non-zero, no more system bus accesses can be
* initiated by the debug module.
*
* 0: There was no bus error.
*
* 1: There was a timeout.
*
* 2: A bad address was accessed.
*
* 3: There was some other error (eg. alignment).
*
* 4: The system bus master was busy when one of the
* {\tt sbaddress} or {\tt sbdata} registers was written,
* or the {\tt sbdata} register was read when it had
* stale data.
 */
`define DMI_SBCS_SBERROR_OFFSET             12
`define DMI_SBCS_SBERROR_LENGTH             3
`define DMI_SBCS_SBERROR                    (32'h7 << `DMI_SBCS_SBERROR_OFFSET)
/*
* Width of system bus addresses in bits. (0 indicates there is no bus
* access support.)
 */
`define DMI_SBCS_SBASIZE_OFFSET             5
`define DMI_SBCS_SBASIZE_LENGTH             7
`define DMI_SBCS_SBASIZE                    (32'h7f << `DMI_SBCS_SBASIZE_OFFSET)
/*
* 1 when 128-bit system bus accesses are supported.
 */
`define DMI_SBCS_SBACCESS128_OFFSET         4
`define DMI_SBCS_SBACCESS128_LENGTH         1
`define DMI_SBCS_SBACCESS128                (32'h1 << `DMI_SBCS_SBACCESS128_OFFSET)
/*
* 1 when 64-bit system bus accesses are supported.
 */
`define DMI_SBCS_SBACCESS64_OFFSET          3
`define DMI_SBCS_SBACCESS64_LENGTH          1
`define DMI_SBCS_SBACCESS64                 (32'h1 << `DMI_SBCS_SBACCESS64_OFFSET)
/*
* 1 when 32-bit system bus accesses are supported.
 */
`define DMI_SBCS_SBACCESS32_OFFSET          2
`define DMI_SBCS_SBACCESS32_LENGTH          1
`define DMI_SBCS_SBACCESS32                 (32'h1 << `DMI_SBCS_SBACCESS32_OFFSET)
/*
* 1 when 16-bit system bus accesses are supported.
 */
`define DMI_SBCS_SBACCESS16_OFFSET          1
`define DMI_SBCS_SBACCESS16_LENGTH          1
`define DMI_SBCS_SBACCESS16                 (32'h1 << `DMI_SBCS_SBACCESS16_OFFSET)
/*
* 1 when 8-bit system bus accesses are supported.
 */
`define DMI_SBCS_SBACCESS8_OFFSET           0
`define DMI_SBCS_SBACCESS8_LENGTH           1
`define DMI_SBCS_SBACCESS8                  (32'h1 << `DMI_SBCS_SBACCESS8_OFFSET)
`define DMI_SBADDRESS0                      32'h39
/*
* Accesses bits 31:0 of the internal address.
 */
`define DMI_SBADDRESS0_ADDRESS_OFFSET       0
`define DMI_SBADDRESS0_ADDRESS_LENGTH       32
`define DMI_SBADDRESS0_ADDRESS              (32'hffffffff << `DMI_SBADDRESS0_ADDRESS_OFFSET)
`define DMI_SBADDRESS1                      32'h3a
/*
* Accesses bits 63:32 of the internal address (if the system address
* bus is that wide).
 */
`define DMI_SBADDRESS1_ADDRESS_OFFSET       0
`define DMI_SBADDRESS1_ADDRESS_LENGTH       32
`define DMI_SBADDRESS1_ADDRESS              (32'hffffffff << `DMI_SBADDRESS1_ADDRESS_OFFSET)
`define DMI_SBADDRESS2                      32'h3b
/*
* Accesses bits 95:64 of the internal address (if the system address
* bus is that wide).
 */
`define DMI_SBADDRESS2_ADDRESS_OFFSET       0
`define DMI_SBADDRESS2_ADDRESS_LENGTH       32
`define DMI_SBADDRESS2_ADDRESS              (32'hffffffff << `DMI_SBADDRESS2_ADDRESS_OFFSET)
`define DMI_SBDATA0                         32'h3c
/*
* Accesses bits 31:0 of the internal data.
 */
`define DMI_SBDATA0_DATA_OFFSET             0
`define DMI_SBDATA0_DATA_LENGTH             32
`define DMI_SBDATA0_DATA                    (32'hffffffff << `DMI_SBDATA0_DATA_OFFSET)
`define DMI_SBDATA1                         32'h3d
/*
* Accesses bits 63:32 of the internal data (if the system bus is
* that wide).
 */
`define DMI_SBDATA1_DATA_OFFSET             0
`define DMI_SBDATA1_DATA_LENGTH             32
`define DMI_SBDATA1_DATA                    (32'hffffffff << `DMI_SBDATA1_DATA_OFFSET)
`define DMI_SBDATA2                         32'h3e
/*
* Accesses bits 95:64 of the internal data (if the system bus is
* that wide).
 */
`define DMI_SBDATA2_DATA_OFFSET             0
`define DMI_SBDATA2_DATA_LENGTH             32
`define DMI_SBDATA2_DATA                    (32'hffffffff << `DMI_SBDATA2_DATA_OFFSET)
`define DMI_SBDATA3                         32'h3f
/*
* Accesses bits 127:96 of the internal data (if the system bus is
* that wide).
 */
`define DMI_SBDATA3_DATA_OFFSET             0
`define DMI_SBDATA3_DATA_LENGTH             32
`define DMI_SBDATA3_DATA                    (32'hffffffff << `DMI_SBDATA3_DATA_OFFSET)


//spi0 cfg regs
`define SPI0_BASE 32'h10014000
`define SPI0_SCKDIV  (`SPI0_BASE + 32'h000)
`define SPI0_SCKMODE (`SPI0_BASE + 32'h004)
`define SPI0_CSID    (`SPI0_BASE + 32'h010)
`define SPI0_CSDEF   (`SPI0_BASE + 32'h014)
`define SPI0_CSMODE  (`SPI0_BASE + 32'h018)
`define SPI0_DELAY0  (`SPI0_BASE + 32'h028)
`define SPI0_DELAY1  (`SPI0_BASE + 32'h02c)
`define SPI0_FMT     (`SPI0_BASE + 32'h040)
`define SPI0_TXDATA  (`SPI0_BASE + 32'h048)
`define SPI0_RXDATA  (`SPI0_BASE + 32'h04c)
`define SPI0_TXMARK  (`SPI0_BASE + 32'h050)
`define SPI0_RXMARK  (`SPI0_BASE + 32'h054)
`define SPI0_FCTRL   (`SPI0_BASE + 32'h060)
`define SPI0_FFMT    (`SPI0_BASE + 32'h064)
`define SPI0_IE      (`SPI0_BASE + 32'h070)
`define SPI0_IP      (`SPI0_BASE + 32'h074)

