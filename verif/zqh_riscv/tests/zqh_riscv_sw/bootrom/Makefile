
GCC=riscv64-unknown-elf-gcc
OBJCOPY=riscv64-unknown-elf-objcopy
OBJDUMP=riscv64-unknown-elf-objdump
HEX_FIX=../../../../scripts/zqh_sw_hex_fix.py

all: bootrom.hex.fix

clean:
	rm -rf bootrom.elf bootrom.elf.dump bootrom.hex bootrom.hex.fix

%.hex.fix: %.hex
	$(HEX_FIX) --hex_in=$<

%.hex: %.elf
	$(OBJCOPY) -O verilog $< $@


%.elf: %.S linker.ld
	$(GCC) -Tlinker.ld $< -nostdlib -static -Wl,--no-gc-sections -o $@
	$(OBJDUMP) -D $@ | tee $@.dump
