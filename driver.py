#########################################################################################################
# driver.py
# This is the driver file that will call your Tomasulo simulator, and execute the instruction.
#
# Please do not edit anything in this function besides the code marked in "main" ()
#########################################################################################################

from typing import List
import tomasulo
from instruction import Instruction

program_instructions = []

# This function takes in a file path and turns it into a list of instructions, which is set as the
# global variable program_instructions
def decode_file(file_path: str) -> List[Instruction]:
    global program_instructions

    with open(file_path, 'r') as file:
        for count, line in enumerate(file, start=1):  # Start count at 1 for line number

            # Remove comments (anything after ';') and strip whitespace
            line = line.split(';', 1)[0].strip()

            if not line:  # Skip empty lines or lines that are only comments
                continue

            parts = line.split()
            opcode = parts[0]
            regs = [int(reg[1:].split(",")[0]) for reg in parts if reg.startswith("R")]

            # Default values
            dest_reg, src_reg1, src_reg2 = -1, -1, -1

            if opcode in ("ADD", "MUL", "SUB") and len(regs) == 3:
                dest_reg, src_reg1, src_reg2 = regs
            elif opcode == "LOAD" and len(regs) == 2:
                dest_reg, src_reg1 = regs[0], regs[1]
            elif opcode == "STORE" and len(regs) == 2:
                src_reg1, src_reg2 = regs
            else:
                print(f"BAD INSTRUCTION: line {count}, {line}")
                continue

            instruction = Instruction(opcode=opcode, count=count, dest_reg=dest_reg, src_reg1=src_reg1, src_reg2=src_reg2)
            program_instructions.append(instruction)

# This is the function that calls your Tomasulo stages! Notice how it calls stage_exec, stage_fire, and then stage_dispatch?
# By calling those functions, we "move" our instructions through a pipeline!

def single_cycle_processor(i):
    print(f"=========================================== C  Y  C  L  E  {i} ============================================")
    global program_instructions

    # Call all three stages (Dispatch, Fire, Exec) in reverse order!

    num_completed = tomasulo.stage_exec()
    tomasulo.stage_fire()
    num_dispatched = tomasulo.stage_dispatch(program_instructions)

    if num_dispatched > 0:
        del program_instructions[:num_dispatched]

    return num_completed

# Main function
def main():

    #########################################################################################################
    # EDIT ME (up to you)

    # Here, you can customize your processor! Set the number of ALUs, MULs, and LSUs (must have at least 1). You can
    # also specify the program you want to execute by changing the "program_filename",. Lastly, you can change how many
    # reservation stations your scheduling unit can hold at once by changing "scheduling_unit_size" !

    # IMPORTANT: num_of_regs MUST be 4 if executing program_basic, program_medium, or program_complex. If executing
    # program_massive, please set it to 8.

    num_of_alus = 2
    num_of_muls = 2
    num_of_lsus = 2

    program_filename = "program_complex.txt"

    scheduling_unit_size = 6
    num_of_regs = 4

    #########################################################################################################

    print("Processor Configuration:")
    print(f"Number of ALUs: {num_of_alus}")
    print(f"Number of MULs: {num_of_muls}")
    print(f"Number of LSUs: {num_of_lsus}")
    print(f"Scheduling Unit Size: {scheduling_unit_size}")
    print(f"Number of Registers: {num_of_regs}")
    print(" ")
    print(f"Starting Tomasulo Simulation! ")
    print(" ")
    print(" ")

    global program_instructions
    decode_file(program_filename)

    tomasulo.initialize_tomasulo(num_of_alus, num_of_muls, num_of_lsus, num_of_regs, scheduling_unit_size)

    i = 1
    initial_num_of_program_instructions = len(program_instructions)
    total_instructions_completed = 0
    while (initial_num_of_program_instructions > total_instructions_completed):
        instructions_completed_in_cycle = single_cycle_processor(i)
        total_instructions_completed += instructions_completed_in_cycle
        i += 1

    ipc = total_instructions_completed / (i-1)
    print("===========================================================================================================")
    print(" ")
    print(f"Program: {program_filename}")
    print(f"Total Instructions: {total_instructions_completed}")
    print(f"Total Cycles: {i-1}")
    print(f"IPC: {ipc}")

if __name__ == "__main__":
    main()