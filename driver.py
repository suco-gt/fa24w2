#########################################################################################################
# driver.py
# This is the driver file that will call your Tomasulo simulator, and execute the instruction.
#
#########################################################################################################

from typing import List
import tomasulo
from instruction import Instruction


program_instructions = []

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
    file_path = "program_basic.txt"
    decode_file(file_path)
    for instruction in program_instructions:
        print(instruction)
     
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