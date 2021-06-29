#ifndef __ZQH_COMMON_DEF_H
#define __ZQH_COMMON_DEF_H

#define CLINT_MSIP(H)     ((volatile uint32_t *) (CLINT_BASE + 0x0000 + H*4))
#define CLINT_MTIMECMP(H) ((volatile uint64_t *) (CLINT_BASE + 0x4000 + H*8))
#define CLINT_MTIMECMP_L(H) ((volatile uint32_t *) (CLINT_BASE + 0x4000 + H*8))
#define CLINT_MTIMECMP_H(H) ((volatile uint32_t *) (CLINT_BASE + 0x4004 + H*8))
#define CLINT_MTIME    ((volatile uint64_t *) (CLINT_BASE + 0xbff8))
#define CLINT_MTIME_L    ((volatile uint32_t *) (CLINT_BASE + 0xbff8))
#define CLINT_MTIME_H    ((volatile uint32_t *) (CLINT_BASE + 0xbffc))

#define DMA_BASE 0x03000000
#define DMA_CHN_NUM 1
#define DMA_CHN_BASE(CHN)     (DMA_BASE + 0x1000 * CHN)
#define DMA_CONTROL(CHN)      ((volatile uint32_t *) (DMA_CHN_BASE(CHN) + 0x0000))
#define DMA_NEXT_CONFIG(CHN)  ((volatile uint32_t *) (DMA_CHN_BASE(CHN) + 0x0004))
#define DMA_NEXT_BYTES(CHN)   ((volatile uint64_t *) (DMA_CHN_BASE(CHN) + 0x0008))
#define DMA_NEXT_DEST(CHN)    ((volatile uint64_t *) (DMA_CHN_BASE(CHN) + 0x0010))
#define DMA_NEXT_SOURCE(CHN)  ((volatile uint64_t *) (DMA_CHN_BASE(CHN) + 0x0018))
#define DMA_EXEC_CONFIG(CHN)  ((volatile uint32_t *) (DMA_CHN_BASE(CHN) + 0x0104))
#define DMA_EXEC_BYTES(CHN)   ((volatile uint64_t *) (DMA_CHN_BASE(CHN) + 0x0108))
#define DMA_EXEC_DEST(CHN)    ((volatile uint64_t *) (DMA_CHN_BASE(CHN) + 0x0110))
#define DMA_EXEC_SOURCE(CHN)  ((volatile uint64_t *) (DMA_CHN_BASE(CHN) + 0x0118))

#define PLIC_BASE 0x0c000000
#define PLIC_PRIORITY         ((volatile uint32_t *) (PLIC_BASE + 0x0000))
#define PLIC_PENDING          ((volatile uint32_t *) (PLIC_BASE + 0x1000))
#define PLIC_ENABLE_M(H)         ((volatile uint32_t *) (PLIC_BASE + 0x2000 + H*0x100))
#define PLIC_ENABLE_S(H)         ((volatile uint32_t *) (PLIC_BASE + 0x2080 + H*0x100))
#define PLIC_THRESHOLD_M(H)      ((volatile uint32_t *) (PLIC_BASE + 0x200000 + H*0x2000))
#define PLIC_THRESHOLD_S(H)      ((volatile uint32_t *) (PLIC_BASE + 0x201000 + H*0x2000))
#define PLIC_CLAIM_COMPLETE_M(H) ((volatile uint32_t *) (PLIC_BASE + 0x200004 + H*0x2000))
#define PLIC_CLAIM_COMPLETE_S(H) ((volatile uint32_t *) (PLIC_BASE + 0x201004 + H*0x2000))
#define PLIC_INT_NUM 32 //id0 is always ignored
#define PLIC_INT_ID_NONE  0
#define PLIC_INT_ID_DMA_DONE(CHN) (1 + CHN*2)
#define PLIC_INT_ID_DMA_ERROR(CHN) (2 + CHN*2)
#define PLIC_INT_ID_GPIO0    (1 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_GPIO1    (2 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_GPIO2    (3 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_GPIO3    (4 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_GPIO4    (5 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_GPIO5    (6 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_GPIO6    (7 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_GPIO7    (8 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_UART0    (9 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_SPI0     (10 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_PWM0     (11 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_I2C      (12 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_MAC      (13 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_DDR_CTRL (14 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_USB_CTRL0 (15 + DMA_CHN_NUM*2)
#define PLIC_INT_ID_USB_CTRL1 (16 + DMA_CHN_NUM*2)


#define CAUSE_MACHINE_SOFTWARE_INTERRUPT 0x8000000000000003
#define CAUSE_MACHINE_TIMER_INTERRUPT 0x8000000000000007
#define CAUSE_SUPERVISOR_EXTERNAL_INTERRUPT 0x8000000000000009
#define CAUSE_MACHINE_EXTERNAL_INTERRUPT 0x800000000000000b

#define CRG_CTRL_BASE 0x10000000
#define CRG_CTRL_CLOCK_REF_CFG ((volatile uint32_t *) (CRG_CTRL_BASE + 0x000))
#define CRG_CTRL_CORE_PLL_CFG  ((volatile uint32_t *) (CRG_CTRL_BASE + 0x004))
#define CRG_CTRL_ETH_PLL_CFG   ((volatile uint32_t *) (CRG_CTRL_BASE + 0x008))
#define CRG_CTRL_DDR_PLL_CFG   ((volatile uint32_t *) (CRG_CTRL_BASE + 0x00c))
#define CRG_CTRL_RESET_CFG     ((volatile uint32_t *) (CRG_CTRL_BASE + 0x010))

#define GPIO_BASE(A) (0x10012000 + 0xd000 * A)
#define GPIO_INPUT_VAL(A)  ((volatile uint32_t *) (GPIO_BASE(A) + 0x000))
#define GPIO_INPUT_EN(A)   ((volatile uint32_t *) (GPIO_BASE(A) + 0x004))
#define GPIO_OUTPUT_EN(A)  ((volatile uint32_t *) (GPIO_BASE(A) + 0x008))
#define GPIO_OUTPUT_VAL(A) ((volatile uint32_t *) (GPIO_BASE(A) + 0x00c))
#define GPIO_PUE(A)        ((volatile uint32_t *) (GPIO_BASE(A) + 0x010))
#define GPIO_DS(A)         ((volatile uint32_t *) (GPIO_BASE(A) + 0x014))
#define GPIO_RISE_IE(A)    ((volatile uint32_t *) (GPIO_BASE(A) + 0x018))
#define GPIO_RISE_IP(A)    ((volatile uint32_t *) (GPIO_BASE(A) + 0x01c))
#define GPIO_FALL_IE(A)    ((volatile uint32_t *) (GPIO_BASE(A) + 0x020))
#define GPIO_FALL_IP(A)    ((volatile uint32_t *) (GPIO_BASE(A) + 0x024))
#define GPIO_HIGH_IE(A)    ((volatile uint32_t *) (GPIO_BASE(A) + 0x028))
#define GPIO_HIGH_IP(A)    ((volatile uint32_t *) (GPIO_BASE(A) + 0x02c))
#define GPIO_LOW_IE(A)     ((volatile uint32_t *) (GPIO_BASE(A) + 0x030))
#define GPIO_LOW_IP(A)     ((volatile uint32_t *) (GPIO_BASE(A) + 0x034))
#define GPIO_IOF_EN(A)     ((volatile uint32_t *) (GPIO_BASE(A) + 0x038))
#define GPIO_IOF_SEL(A)    ((volatile uint32_t *) (GPIO_BASE(A) + 0x03c))
#define GPIO_OUT_XOR(A)    ((volatile uint32_t *) (GPIO_BASE(A) + 0x040))

#define UART0_BASE 0x10013000
#define UART0_TXDATA    ((volatile uint32_t *) (UART0_BASE + 0x000))
#define UART0_RXDATA    ((volatile uint32_t *) (UART0_BASE + 0x004))
#define UART0_TXCTRL    ((volatile uint32_t *) (UART0_BASE + 0x008))
#define UART0_RXCTRL    ((volatile uint32_t *) (UART0_BASE + 0x00c))
#define UART0_IE        ((volatile uint32_t *) (UART0_BASE + 0x010))
#define UART0_IP        ((volatile uint32_t *) (UART0_BASE + 0x014))
#define UART0_DIV       ((volatile uint32_t *) (UART0_BASE + 0x018))
#define UART0_ERROR     ((volatile uint32_t *) (UART0_BASE + 0x01c))

#define SPI0_BASE 0x10014000
#define SPI0_SCKDIV  ((volatile uint32_t *) (SPI0_BASE + 0x000))
#define SPI0_SCKMODE ((volatile uint32_t *) (SPI0_BASE + 0x004))
#define SPI0_CSID    ((volatile uint32_t *) (SPI0_BASE + 0x010))
#define SPI0_CSDEF   ((volatile uint32_t *) (SPI0_BASE + 0x014))
#define SPI0_CSMODE  ((volatile uint32_t *) (SPI0_BASE + 0x018))
#define SPI0_DELAY0  ((volatile uint32_t *) (SPI0_BASE + 0x028))
#define SPI0_DELAY1  ((volatile uint32_t *) (SPI0_BASE + 0x02c))
#define SPI0_FMT     ((volatile uint32_t *) (SPI0_BASE + 0x040))
#define SPI0_TXDATA  ((volatile uint32_t *) (SPI0_BASE + 0x048))
#define SPI0_RXDATA  ((volatile uint32_t *) (SPI0_BASE + 0x04c))
#define SPI0_TXMARK  ((volatile uint32_t *) (SPI0_BASE + 0x050))
#define SPI0_RXMARK  ((volatile uint32_t *) (SPI0_BASE + 0x054))
#define SPI0_FCTRL   ((volatile uint32_t *) (SPI0_BASE + 0x060))
#define SPI0_FFMT    ((volatile uint32_t *) (SPI0_BASE + 0x064))
#define SPI0_IE      ((volatile uint32_t *) (SPI0_BASE + 0x070))
#define SPI0_IP      ((volatile uint32_t *) (SPI0_BASE + 0x074))

#define PWM0_BASE 0x10015000
#define PWM0_PWMCFG   ((volatile uint32_t *) (PWM0_BASE + 0x000))
#define PWM0_PWMCOUNT ((volatile uint32_t *) (PWM0_BASE + 0x008))
#define PWM0_PWMS     ((volatile uint32_t *) (PWM0_BASE + 0x010))
#define PWM0_PWMMAX   ((volatile uint32_t *) (PWM0_BASE + 0x018))
#define PWM0_PWMCMP0  ((volatile uint32_t *) (PWM0_BASE + 0x020))
#define PWM0_PWMCMP1  ((volatile uint32_t *) (PWM0_BASE + 0x024))
#define PWM0_PWMCMP2  ((volatile uint32_t *) (PWM0_BASE + 0x028))
#define PWM0_PWMCMP3  ((volatile uint32_t *) (PWM0_BASE + 0x02c))

#define I2C_BASE 0x10016000
#define I2C_DIV             ((volatile uint32_t *) (I2C_BASE + 0x000))
#define I2C_CONTROL         ((volatile uint32_t *) (I2C_BASE + 0x004))
#define I2C_CFG             ((volatile uint32_t *) (I2C_BASE + 0x008))
#define I2C_DATA            ((volatile uint32_t *) (I2C_BASE + 0x00c))
#define I2C_CMD             ((volatile uint32_t *) (I2C_BASE + 0x010))
#define I2C_STATUS          ((volatile uint32_t *) (I2C_BASE + 0x014))
#define I2C_IE              ((volatile uint32_t *) (I2C_BASE + 0x018))
#define I2C_IP              ((volatile uint32_t *) (I2C_BASE + 0x01c))

#define MAC_BASE 0x10020000
#define MAC_MODE         ((volatile uint32_t *) (MAC_BASE + 0x0000))
#define MAC_IP           ((volatile uint32_t *) (MAC_BASE + 0x0004))
#define MAC_IE           ((volatile uint32_t *) (MAC_BASE + 0x0008))
#define MAC_IPG          ((volatile uint32_t *) (MAC_BASE + 0x000c))
#define MAC_PKT_LEN      ((volatile uint32_t *) (MAC_BASE + 0x0010))
#define MAC_COLL         ((volatile uint32_t *) (MAC_BASE + 0x0014))
#define MAC_TX_BD_L      ((volatile uint32_t *) (MAC_BASE + 0x0020))
#define MAC_TX_BD_H      ((volatile uint32_t *) (MAC_BASE + 0x0024))
#define MAC_TX_CPL       ((volatile uint32_t *) (MAC_BASE + 0x0028))
#define MAC_RX_BD_L      ((volatile uint32_t *) (MAC_BASE + 0x0030))
#define MAC_RX_BD_H      ((volatile uint32_t *) (MAC_BASE + 0x0034))
#define MAC_RX_CPL       ((volatile uint32_t *) (MAC_BASE + 0x0038))
#define MAC_CTRL_CFG     ((volatile uint32_t *) (MAC_BASE + 0x0040))
#define MAC_CTRL_TX      ((volatile uint32_t *) (MAC_BASE + 0x0044))
#define MAC_ADDR_L       ((volatile uint32_t *) (MAC_BASE + 0x0048))
#define MAC_ADDR_H       ((volatile uint32_t *) (MAC_BASE + 0x004c))
#define MAC_HASH_L       ((volatile uint32_t *) (MAC_BASE + 0x0050))
#define MAC_HASH_H       ((volatile uint32_t *) (MAC_BASE + 0x0054))
#define MAC_SMI_CFG      ((volatile uint32_t *) (MAC_BASE + 0x0058))
#define MAC_SMI_CTRL     ((volatile uint32_t *) (MAC_BASE + 0x005c))
#define MAC_SMI_DATA     ((volatile uint32_t *) (MAC_BASE + 0x0060))
#define MAC_FIFO_STATUS  ((volatile uint32_t *) (MAC_BASE + 0x0064))
#define MAC_TX_BUF       ((volatile uint32_t *) (MAC_BASE + 0x8000))
#define MAC_RX_BUF       ((volatile uint32_t *) (MAC_BASE + 0xc000))

#define DDR_MC_BASE 0x10030000
#define DDR_MC_SLICE_NUM 2
#define DDR_MC_CTRL_CFG_BASE 0x10030000
#define DDR_MC_PHY_DS_CFG_BASE 0x10034000
#define DDR_MC_PHY_AC_CFG_BASE (DDR_MC_PHY_DS_CFG_BASE + 0x20 * DDR_MC_SLICE_NUM)
#define DDR_MC_AP_CFG_BASE 0x10038000
#define DDR_MC_CTRL_CFG_REG(IDX) ((volatile uint32_t *) (DDR_MC_CTRL_CFG_BASE + (IDX << 2)))
#define DDR_MC_PHY_DS_CFG_REG(IDX) ((volatile uint32_t *) (DDR_MC_PHY_DS_CFG_BASE + (IDX << 2)))
#define DDR_MC_PHY_AC_CFG_REG(IDX) ((volatile uint32_t *) (DDR_MC_PHY_AC_CFG_BASE + (IDX << 2)))
#define DDR_MC_AP_CFG_REG(IDX) ((volatile uint32_t *) (DDR_MC_AP_CFG_BASE + (IDX << 2)))


#define USB_CTRL_BASE(A) (0x10040000 + 0x10000*A)
#define USB_CTRL_CFG_BASE(A) (0x10040000 + 0x10000*A)
#define USB_CTRL_VERSION(A)    ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0000))
#define USB_CTRL_CONFIG(A)    ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0004))
#define USB_CTRL_HOST_TX_FIFO_DATA(A) ((volatile uint8_t *) (USB_CTRL_CFG_BASE(A) + 0x0008))
#define USB_CTRL_HOST_TX_FIFO_DATA_COUNT(A) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x000c))
#define USB_CTRL_HOST_TX_FIFO_CONTROL(A) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0010))
#define USB_CTRL_HOST_RX_FIFO_DATA(A) ((volatile uint8_t *) (USB_CTRL_CFG_BASE(A) + 0x0014))
#define USB_CTRL_HOST_RX_FIFO_DATA_COUNT(A) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0018))
#define USB_CTRL_HOST_RX_FIFO_CONTROL(A) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x001c))
#define USB_CTRL_HOST_INTERRUPT_STATUS(A) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0020))
#define USB_CTRL_HOST_INTERRUPT_EN(A) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0024))
#define USB_CTRL_DEVICE_TX_FIFO_DATA(A,B) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0100 + 32*B + 0x000))
#define USB_CTRL_DEVICE_TX_FIFO_DATA_COUNT(A,B) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0100 + 32*B + 0x004))
#define USB_CTRL_DEVICE_TX_FIFO_CONTROL(A,B) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0100 + 32*B + 0x008))
#define USB_CTRL_DEVICE_RX_FIFO_DATA(A,B) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0100 + 32*B + 0x00c))
#define USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(A,B) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0100 + 32*B + 0x010))
#define USB_CTRL_DEVICE_RX_FIFO_CONTROL(A,B) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0100 + 32*B + 0x014))
#define USB_CTRL_DEVICE_INTERRUPT_STATUS(A) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0180))
#define USB_CTRL_DEVICE_INTERRUPT_EN(A) ((volatile uint32_t *) (USB_CTRL_CFG_BASE(A) + 0x0184))
#define USB_CTRL_UTMI_CFG_BASE(A) (0x10040200 + 0x10000*A)
#define USB_CTRL_UTMI_HOST_CONTROL(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0000))
#define USB_CTRL_UTMI_HOST_TX_LINE_CONTROL(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0004))
#define USB_CTRL_UTMI_HOST_TX_ADDR(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0008))
#define USB_CTRL_UTMI_HOST_TX_FRAME_NUM(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x000c))
#define USB_CTRL_UTMI_HOST_TX_SOF_TIMER(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0010))
#define USB_CTRL_UTMI_HOST_RX_STATUS(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0014))
#define USB_CTRL_UTMI_HOST_RX_PID(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0018))
#define USB_CTRL_UTMI_HOST_RX_ADDR(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x001c))
#define USB_CTRL_UTMI_HOST_CONNECT_STATE(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0020))
#define USB_CTRL_UTMI_HOST_TRANS_TIMEOUT_CNT(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0024))
#define USB_CTRL_UTMI_DEVICE_TX_LINE_CONTROL(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0100))
#define USB_CTRL_UTMI_DEVICE_CONNECT_STATE(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0104))
#define USB_CTRL_UTMI_DEVICE_ADDR(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0108))
#define USB_CTRL_UTMI_DEVICE_FRAME_NUM(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0110))
#define USB_CTRL_UTMI_DEVICE_TRANS_TIMEOUT_CNT(A) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0114))
#define USB_CTRL_UTMI_DEVICE_CONTROL(A,B) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0140 + 8*B + 0x000))
#define USB_CTRL_UTMI_DEVICE_STATUS(A,B) ((volatile uint32_t *) (USB_CTRL_UTMI_CFG_BASE(A) + 0x0140 + 8*B + 0x004))
#define USB_PHY_CFG_BASE(A) (0x10040400 + 0x10000*A)
#define USB_PHY_CFG0(A) ((volatile uint32_t *) (USB_PHY_CFG_BASE(A) + 0x0000))
#define USB_PHY_CFG1(A) ((volatile uint32_t *) (USB_PHY_CFG_BASE(A) + 0x0004))
#define USB_PHY_CFG2(A) ((volatile uint32_t *) (USB_PHY_CFG_BASE(A) + 0x0008))


#define MMIO_SRAM_MEM_BASE 0x11000000
#define MMIO_PRINT_BASE 0x1f000000

#define PRINT_PTR_HART(H) ((uint8_t *)((MMIO_PRINT_BASE | 0x00f0ff00) + (H << 16)))
#define STOP_PTR_HART(H) ((uint8_t *)((MMIO_PRINT_BASE | 0x00f0fff0) + (H << 16)))

#define SPI_FLASH_XIP_BASE 0x20000000
#define TL_SRAM_MEM_BASE 0x40000000
#define AXI_SRAM_MEM_BASE 0x50000000
//#define MAIN_MEM_BASE 0x80000000
#define DDR_MEM_BASE 0x80000000

#define SPI_FLASH_XIP ((volatile uint8_t *) (SPI_FLASH_XIP_BASE + 0x0000))

#define HART_IO_SPACE_GAP 0x00400000
#define ITIM_BASE 0x60000000
#define DTIM_BASE 0x60200000
#define ITIM_IO_BASE 0x01000000
#define DTIM_IO_BASE 0x01200000
#define ITIM_ADDR(OFFSET) (volatile uint8_t *)(ITIM_BASE + OFFSET)
#define DTIM_ADDR(OFFSET) (volatile uint8_t *)(DTIM_BASE + OFFSET)
#define ITIM_IO_ADDR(HART_ID, OFFSET) (volatile uint8_t *)(ITIM_IO_BASE + HART_IO_SPACE_GAP * HART_ID + OFFSET)
#define DTIM_IO_ADDR(HART_ID, OFFSET) (volatile uint8_t *)(DTIM_IO_BASE + HART_IO_SPACE_GAP * HART_ID + OFFSET)


#define DC_L1_FLUSH_BASE 0x02010000
#define DC_L1_FLUSH_IO_BASE 0x01300000
#define DC_L1_FLUSH_ADDR (volatile uint32_t *)(DC_L1_FLUSH_BASE)
#define DC_L1_FLUSH_IO_ADDR(HART_ID) (volatile uint32_t *)(DC_L1_FLUSH_IO_BASE + HART_IO_SPACE_GAP * HART_ID)

#endif
