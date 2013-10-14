PART1_UNIT_CHKS = $(patsubst %.output,%.myout,$(wildcard part1TestCases/unitTests/*.output))
$(PART1_UNIT_CHKS) : %.myout : % pivot.py
	./pivot.py -part 1 -lpdict $< > $@
	diff -w $<.output $@ 

PART2_UNIT_CHKS = $(patsubst %.output,%.myout,$(wildcard part2TestCases/unitTests/*.output))
$(PART2_UNIT_CHKS) : %.myout : % pivot.py
	./pivot.py -part 2 -lpdict $< > $@
	diff -w $<.output $@ 

PART1_ASSGNS    = $(patsubst %,%.myout,$(wildcard part1TestCases/assignmentParts/*.dict))
$(PART1_ASSGNS) : %.myout : % pivot.py
	./pivot.py -part 1 -lpdict $< > $@

PART2_ASSGNS    = $(patsubst %,%.myout,$(wildcard part2TestCases/assignmentParts/*.dict))
$(PART2_ASSGNS) : %.myout : % pivot.py
	./pivot.py -part 2 -lpdict $< > $@

.PHONY: part1 part2
part1 : $(PART1_UNIT_CHKS) $(PART1_ASSGNS)
part2 : $(PART2_UNIT_CHKS) $(PART2_ASSGNS)
