Update: 10/24

The basic code for tomasulo.py has been pushed and entered in. As part of the exercise, students will complete the stage_exec, stage_fire, and stage_dispatch functions. These functions implement the actual Tomasulo logic. Right now, they are (somewhat) untested. These 3 functions essentially "progress" the processor through a single cycle. Stage_exec (stage 3) completes any instructions by removing them from the functional units, and updates the register file and scheduling unit. Stage_fire (stage 2) will fire any "ready" instruction/reservation station to the functional units and remove them from the scheduling unit. Stage_dispatch (stage 1) will add an instruction to the scheduling unit.

A good way to think of it is that each "stage" function progresses instructions/reservation stations through the following pipeline in our processor.

-> Scheduling Unit -> Functional Units (ALUs, etc.) -> Completed Instructions

The leftmost arrow would be stage_dispatch, the next stage_fire, and rightmost/last stage_exec. The way our simulator will work is a driver file will call these in reverse-order (exec, fire, and then dispatch) to  progress the processor pipeline in a single cycle. Hopefully that made sense. If you want details on what each stage does, look at the code and my notes.

The majority of work now lies in 1) building out the driver file, and 2) testing. ONE TASK THAT NEEDS TO GET DONE AND REQUIRES NO KNOWLEDGE TO IMPLEMENT is writing a basic decoder. Essentially, the files program_basic.txt and program_complex.txt are text files that contain a basic program of assembly instructions, like such:

ADD R1, R2, R3
MUL R3, R1, R4
STORE R1, R2
LOAD R5, R6
SUB R1, R2, R5

These are the 5 assembly instructions in our fake "language" that our processor executes. Simple, right? All you need to do is simply write some code in driver.py (or another file, whatevers easier) that parses a specified txt file (like program_basic.txt or program_complex.txt) and converts the assembly into "Instruction" objects. You can see this class in the file instruction.py. Essentially, the code should just 1) parse each line in the file, 2) identify the opcode, count, DR, SR1, SR2 from the line of text and create an Instruction object from that, and 3) add that instruction object to a list of other instruction objects. Super simple!

Some notes: Count = what line the instruction is on. For example, in the short snippet above, ADD's count should be 1 (cause its on line 1), and LOAD's count should be 4 (its on line 4 duh). Additionally, LOAD instructions have only 1 Source reg (SR1). STORE instructions have 2 Source regs (SR1 and SR2) but no Dest Reg (DR). in the instances where there is no dest reg or other source reg, populate the instruction object's field with -1. For example, all STORE instruction's dest_reg field should be -1, since no store instruction has a dest reg. One final note: the five instructions you see above are the only ones you'll deal with: just ADD, MUL, STORE, LOAD, and SUB. Good luck!
