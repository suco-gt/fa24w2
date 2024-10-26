#########################################################################################################
# driver.py
# This is the driver file that will call your Tomasulo simulator, and execute the instruction.
#
#########################################################################################################

import tomasulo
import instruction

program_instructions = []

def single_cycle_processor(i):
    print(f"=========================================== C  Y  C  L  E  {i} ============================================")
    global program_instructions
    num_completed = tomasulo.stage_exec()
    tomasulo.stage_fire()
    num_dispatched = tomasulo.stage_dispatch(program_instructions)

    if num_dispatched > 0:
        del program_instructions[:num_dispatched]

    return num_completed


def main():
    global program_instructions
    filename = "program_basic.txt"
    program_instructions = []
    print(f"Starting Tomasulo Simulation! ")
    print(" ")
    print(" ")

    ###################################
    num_of_alus = 1
    num_of_muls = 0
    num_of_lsus = 1
    num_of_regs = 4
    scheduling_unit_size = 4
    ###################################

    tomasulo.initialize_tomasulo(num_of_alus, num_of_muls, num_of_lsus, num_of_regs, scheduling_unit_size)

    i = 1
    initial_num_of_program_instructions = len(program_instructions)
    total_instructions_completed = 0
    while (initial_num_of_program_instructions > total_instructions_completed):
        instructions_completed_in_cycle = single_cycle_processor(i)
        total_instructions_completed += instructions_completed_in_cycle
        i += 1



if __name__ == "__main__":
    main()