PART1_UNIT_CHKS = $(patsubst %.output,%.myout,$(wildcard part1TestCases/unitTests/*.output))
$(PART1_UNIT_CHKS) : %.myout : % pivot.py
	./pivot.py -part 1 -lpdict $< > $@
	diff -w $<.output $@ 

PART2_UNIT_CHKS = $(patsubst %.output,%.myout,$(wildcard part2TestCases/unitTests/*.output))
$(PART2_UNIT_CHKS) : %.myout : % pivot.py
	./pivot.py -part 2 -lpdict $< > $@
	diff -w $<.output $@ 

PART3_UNIT_CHKS = $(patsubst %.out,%.myout,$(wildcard initializationTests/unitTests/*.out initializationTests/unitTests/moreTests/*.out))
$(PART3_UNIT_CHKS) : %.myout : % pivot.py
	./pivot.py -part 3 -lpdict $< > $@
	diff -w $<.out $@ 

PART4_UNIT_CHKS = $(patsubst %.output,%.myout,$(wildcard ilpTests/unitTests/*.output))
$(PART4_UNIT_CHKS) : %.myout : % pivot.py
	./pivot.py -part 4 -lpdict $< > $@
	diff -w $<.output $@ 

PART1_ASSGNS    = $(patsubst %,%.myout,$(wildcard part1TestCases/assignmentParts/*.dict))
$(PART1_ASSGNS) : %.myout : % pivot.py
	./pivot.py -part 1 -lpdict $< > $@

PART2_ASSGNS    = $(patsubst %,%.myout,$(wildcard part2TestCases/assignmentParts/*.dict))
$(PART2_ASSGNS) : %.myout : % pivot.py
	./pivot.py -part 2 -lpdict $< > $@

PART3_ASSGNS    = $(patsubst %,%.myout,$(wildcard initializationTests/assignmentTests/*.dict))
$(PART3_ASSGNS) : %.myout : % pivot.py
	./pivot.py -part 3 -lpdict $< > $@

PART4_ASSGNS    = $(patsubst %,%.myout,$(wildcard ilpTests/assignmentTests/*.dict))
$(PART4_ASSGNS) : %.myout : % pivot.py
	./pivot.py -part 4 -lpdict $< > $@

.PHONY: part1 part2 part3 part4 all
part1 : $(PART1_UNIT_CHKS) $(PART1_ASSGNS)
part2 : $(PART2_UNIT_CHKS) $(PART2_ASSGNS)
part3 : $(PART3_UNIT_CHKS) $(PART3_ASSGNS)
part4 : $(PART4_UNIT_CHKS) $(PART4_ASSGNS)
all : part1 part2 part3 part4
