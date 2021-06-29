#define FLASH_XIP_BASE 0x20000000
#define SRAM_BASE      0x40000000
#define DDR_BASE       0x80000000

.section .text.start, "ax", @progbits
.option norvc
.globl _start
_start:
  li s0, FLASH_XIP_BASE
  j 1f
.align 4
  li s0, SRAM_BASE
  j 1f
.align 4
  li s0, DDR_BASE
  j 1f
1:
  csrr a0, mhartid
  la a1, _dtb
  jr s0

.section .text.hang, "ax", @progbits
.globl _hang
_hang:
  csrr a0, mhartid
  la a1, _dtb
1:
  wfi
  j 1b

.section .rodata.dtb, "a", @progbits
.globl _dtb
.align 5, 0
_dtb:
.ascii "DTB goes here"
