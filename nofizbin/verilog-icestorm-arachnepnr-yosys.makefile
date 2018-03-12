# icestorm/arachne-pnr/yosys makefile
# written 2017-12-01 by mza
# based on Makefile in rot.v example project
# last updated 2017-12-04

list_of_all_verilog_files := $(wildcard src/*.v)

work/%.blif : src/%.v
	@if [ ! -e work ]; then mkdir work; fi
	nice yosys -q -p "synth_ice40 -blif $@" $<
	@ls -lart $@

work/%.txt : src/icestick.pcf work/%.blif
	nice arachne-pnr -p $^ -o $@
	@ls -lart $@

work/%.bin : work/%.txt
	nice icepack $< $@
	@ls -lart $@

default:
	@ls -lart $(list_of_all_verilog_files)
	$(MAKE) $(list_of_all_verilog_files:src/%.v=work/%.bin)
	@ls -lart $(list_of_all_verilog_files:src/%.v=work/%.bin)

prog:
	@echo "iceprog work/blah.bin"

clean:
	rm -rf work

.PRECIOUS : work/%.blif work/%.txt # keep intermediate files

#amza-test001.bin: mza-test001.v mza-test001.pcf
#	nice yosys -q -p "synth_ice40 -blif mza-test001.blif" mza-test001.v
#	nice arachne-pnr -p mza-test001.pcf mza-test001.blif -o mza-test001.txt
#	#icebox_explain mza-test001.txt > mza-test001.ex
#	nice icepack mza-test001.txt mza-test001.bin

