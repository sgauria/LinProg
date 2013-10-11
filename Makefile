# placeholder
PART1_REFS = $(wildcard part1TestCases/unitTests/*.output)
PART1_UNIT_CHKS = $(patsubst %.output,%.myout,$(PART1_REFS))

$(PART1_UNIT_CHKS) : %.myout : % pivot1.py
	./pivot1.py -lpdict $< > $@
	diff -w $<.output $@ 

.PHONY: part1
part1 : $(PART1_UNIT_CHKS)
