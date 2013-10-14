PART1_UNIT_CHKS = $(patsubst %.output,%.myout,$(wildcard part1TestCases/unitTests/*.output))
$(PART1_UNIT_CHKS) : %.myout : % pivot.py
	./pivot.py -part 1 -lpdict $< > $@
	diff -w $<.output $@ 

PART1_ASSGNS    = $(patsubst %,%.myout,$(wildcard part1TestCases/assignmentParts/*.dict))
$(PART1_ASSGNS) : %.myout : % pivot.py
	./pivot.py -part 1 -lpdict $< > $@

.PHONY: part1
part1 : $(PART1_UNIT_CHKS) $(PART1_ASSGNS)
