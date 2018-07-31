# icestorm/arachne-pnr/yosys makefile
# written 2017-12-01 by mza
# https://github.com/mzandrew/bin/blob/master/nofizbin/verilog-icestorm-arachnepnr-yosys.makefile
# originally based on Makefile in rot.v example project
# with help from http://make.mad-scientist.net/papers/advanced-auto-dependency-generation/
# last updated 2018-07-31 by mza

# goes nicely with https://raw.githubusercontent.com/mzandrew/hdl/master/verilog/write_verilog_dependency_file.py

list_of_all_verilog_files := $(wildcard src/*.v)
list_of_all_verilog_dependency_files := $(wildcard work/*.d)

#bash dependency builder :
# for each in src/*.v; do echo $each; grep -h include $each; if [ $? -eq 0 ]; then echo "found"; list=$(grep include $each | sed -e "s,\`include \"\(.*\)\",src/\1,"); list=$(echo $list); new=$(echo $each | sed -e "s,^src/,," | sed -e "s,.v$,,"); dep="work/${new}.d"; echo "work/${new}.blif $dep : $each $list" > $dep; fi; done

work/%.d : src/%.v
	@if [ ! -e work ]; then mkdir work; fi
	@./write_verilog_dependency_file.py $<

work/%.blif : src/%.v work/%.d
	@if [ ! -e work ]; then mkdir work; fi
	@echo $<
	@nice yosys -q -p "synth_ice40 -blif $@" $<
	@#ls -lart $@

work/%.txt : src/icestick.pcf work/%.blif
	@if [ ! -e work ]; then mkdir work; fi
	@nice arachne-pnr -p $^ -o $@
	@#ls -lart $@

work/%.bin : work/%.txt
	@if [ ! -e work ]; then mkdir work; fi
	@nice icepack $< $@
	@ls -lart $@

default:
	@#ls -lart $(list_of_all_verilog_files)
	@$(MAKE) $(list_of_all_verilog_files:src/%.v=work/%.d)
	@$(MAKE) $(list_of_all_verilog_files:src/%.v=work/%.bin)
	@ls -lart $(list_of_all_verilog_files:src/%.v=work/%.bin)

prog:
	@echo "iceprog work/blah.bin"

clean:
	rm -rf work

.PRECIOUS : work/%.blif work/%.txt work/%.d # keep intermediate files

MAKEFLAGS += --silent

include $(list_of_all_verilog_dependency_files)
#ls $(wildcard $(patsubst src/%.v,work/%.d,$(basename $(SRCS))))

#amza-test001.bin: mza-test001.v mza-test001.pcf
#	nice yosys -q -p "synth_ice40 -blif mza-test001.blif" mza-test001.v
#	nice arachne-pnr -p mza-test001.pcf mza-test001.blif -o mza-test001.txt
#	#icebox_explain mza-test001.txt > mza-test001.ex
#	nice icepack mza-test001.txt mza-test001.bin

