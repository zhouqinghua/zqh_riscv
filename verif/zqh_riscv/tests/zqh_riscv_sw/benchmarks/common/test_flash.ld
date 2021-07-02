/*======================================================================*/
/* Proxy kernel linker script                                           */
/*======================================================================*/
/* This is the linker script used when building the proxy kernel. */

/*----------------------------------------------------------------------*/
/* Setup                                                                */
/*----------------------------------------------------------------------*/

/* The OUTPUT_ARCH command specifies the machine architecture where the
   argument is one of the names used in the BFD library. More
   specifically one of the entires in bfd/cpu-mips.c */

OUTPUT_ARCH( "riscv" )
ENTRY(_start)

/*----------------------------------------------------------------------*/
/* Sections                                                             */
/*----------------------------------------------------------------------*/

SECTIONS
{

  /* text: test code section */
  /*bootloader use 0x20000000 - 0x20002000*/
  . = 0x20002000;
  .text.init : { *(.text.init)}

  .text : { *(.text)}

  .rodata : {*(.rodata*)}

  /*on chip sram skip 1st 8KB*/
  /*. = 0x40002000;*/
  /*on chip sram*/
  /*. = 0x40000000;*/
  /*on chp ITIM sram*/
  /*. = 0x60000000;*/
  /*on chp DTIM sram*/
  . = 0x60200000;
  /* data segment */
  .data : { *(.data) }

  . = ALIGN(0x1000);
  .tohost : { *(.tohost) }

  .sdata : {
    __global_pointer$ = . + 0x800;
    *(.srodata.cst16) *(.srodata.cst8) *(.srodata.cst4) *(.srodata.cst2) *(.srodata*)
    *(.sdata .sdata.* .gnu.linkonce.s.*)
  }

  /* bss segment */
  .sbss : {
    *(.sbss .sbss.* .gnu.linkonce.sb.*)
    *(.scommon)
  }
  .bss : { *(.bss) }

  /* thread-local data segment */
  .tdata :
  {
    _tls_data = .;
    *(.tdata.begin)
    *(.tdata)
    *(.tdata.end)
  }
  .tbss :
  {
    *(.tbss)
    *(.tbss.end)
  }


  /* End of uninitalized data segement */
  _end = .;
}
