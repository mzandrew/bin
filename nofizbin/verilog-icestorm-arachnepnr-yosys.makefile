# icestorm/arachne-pnr/yosys makefile
# written 2017-12-01 by mza
# https://github.com/mzandrew/bin/blob/master/nofizbin/verilog-icestorm-arachnepnr-yosys.makefile
# originally based on Makefile in rot.v example project
# with help from http://make.mad-scientist.net/papers/advanced-auto-dependency-generation/
# last updated 2020-06-01 by mza

# goes nicely with https://raw.githubusercontent.com/mzandrew/hdl/master/verilog/write_verilog_dependency_file.py

#list_of_all_verilog_files := $(wildcard src/*.v)
list_of_all_icestick_verilog_files := $(shell grep -l icestick src/*.v)
list_of_all_icezero_verilog_files := $(shell grep -l icezero src/*.v)
#list_of_all_unknown_verilog_files := $(shell grep -l '(icezero\|icestick)' src/*.v)
list_of_all_verilog_dependency_files := $(wildcard work/*.d)

#bash dependency builder :
# for each in src/*.v; do echo $each; grep -h include $each; if [ $? -eq 0 ]; then echo "found"; list=$(grep include $each | sed -e "s,\`include \"\(.*\)\",src/\1,"); list=$(echo $list); new=$(echo $each | sed -e "s,^src/,," | sed -e "s,.v$,,"); dep="work/${new}.d"; echo "work/${new}.blif $dep : $each $list" > $dep; fi; done

work/%.d : src/%.v
	@if [ ! -e work ]; then mkdir work; fi
	@#echo $<
	@./write_verilog_dependency_file.py $<

work/%.out : src/%.v work/%.d
	@iverilog -m testbench $< -o $@ -I src

work/%.vcd : work/%.out
	@vvp $<
	@gtkwave $@

work/%.icezero.blif : src/%.v work/%.d
	@if [ ! -e work ]; then mkdir work; fi
	@echo; echo $<
	@nice yosys -q -p "synth_ice40 -top top -blif $@" $<
	@#ls -lart $@

work/%.icestick.blif : src/%.v work/%.d
	@if [ ! -e work ]; then mkdir work; fi
	@echo; echo $<
	@nice yosys -q -p "synth_ice40 -top top -blif $@" $<
	@#ls -lart $@

work/%.json : src/%.v
	@if [ ! -e work ]; then mkdir work; fi
	@#nice yosys -q -p "prep -top top -flatten; write_json $@" $<
	@nice yosys -q -p "prep -top top; write_json $@" $<
	@#ls -lart $@

work/%.svg : work/%.json
	@if [ ! -e work ]; then mkdir work; fi
	@nice node bin/netlistsvg.js $< -o $@
	@#ls -lart $@

work/%.icestick.txt : src/icestick.pcf work/%.icestick.blif
	@if [ ! -e work ]; then mkdir work; fi
	@nice arachne-pnr -p $^ -o $@ -d 1k -P tq144
	@#ls -lart $@

work/%.icezero.txt : src/icezero.pcf work/%.icezero.blif
	@if [ ! -e work ]; then mkdir work; fi
	@nice arachne-pnr -p $^ -o $@ -d 8k -P tq144:4k
	@#ls -lart $@

work/%.bin : work/%.txt
	@if [ ! -e work ]; then mkdir work; fi
	@nice icepack $< $@
	@ls -lart $@

work/%.timing-report : work/%.icestick.txt
	@if [ ! -e work ]; then mkdir work; fi
	@nice icetime -mt -p src/icestick.pcf -P tg144 -d hx1k $< > tmp
	@mv tmp $@

work/%.timing-report : work/%.icezero.txt
	@if [ ! -e work ]; then mkdir work; fi
	@nice icetime -mt -p src/icezero.pcf -P tg144:4k -d hx4k $< > tmp
	@mv tmp $@

default:
	@#ls -lart $(list_of_all_verilog_files)
	@echo "updating dependency files..."
	@$(MAKE) $(list_of_all_icestick_verilog_files:src/%.v=work/%.d)
	@$(MAKE) $(list_of_all_icezero_verilog_files:src/%.v=work/%.d)
	@echo "building firmware..."
	@$(MAKE) $(list_of_all_icestick_verilog_files:src/%.v=work/%.icestick.bin)
	@$(MAKE) $(list_of_all_icezero_verilog_files:src/%.v=work/%.icezero.bin)
	@#$(MAKE) $(list_of_all_verilog_files:src/%.v=work/%.timing-report)
	@#$(MAKE) $(list_of_all_verilog_files:src/%.v=work/%.svg)
	@echo "done"
	@ls -lart $(list_of_all_icestick_verilog_files:src/%.v=work/%.icestick.bin)
	@ls -lart $(list_of_all_icezero_verilog_files:src/%.v=work/%.icezero.bin)

prog:
	@echo "iceprog work/blah.bin"

clean:
	rm -rf work

.PRECIOUS : work/%.d work/%.json work/%.timing-report work/%.icestick.txt work/%.icestick.blif work/%.icezero.txt work/%.icezero.blif # keep intermediate files

MAKEFLAGS += --silent

include $(list_of_all_verilog_dependency_files)
#ls $(wildcard $(patsubst src/%.v,work/%.d,$(basename $(SRCS))))

#amza-test001.bin: mza-test001.v mza-test001.pcf
#	nice yosys -q -p "synth_ice40 -blif mza-test001.blif" mza-test001.v
#	nice arachne-pnr -p mza-test001.pcf mza-test001.blif -o mza-test001.txt
#	#icebox_explain mza-test001.txt > mza-test001.ex
#	nice icepack mza-test001.txt mza-test001.bin
#	icetime -mt -p src/icestick.pcf -P tg144 -d hx1k work/mza-test009.multi-segment-driver.txt 

#	yosys -q -p "synth_ice40 -blif $PRJ.blif" $PRJ.v
#	arachne-pnr $PRJ.blif -d 8k -P tq144:4k --post-place-blif $PRJ.post.blif
#	yosys -q -o $PRJ.post.json $PRJ.post.blif

