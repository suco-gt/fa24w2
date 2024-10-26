#########################################################################################################
# driver.py
# This is the driver file that will call your Tomasulo simulator, and execute the instruction.
#
#
#
#########################################################################################################

from typing import List
import tomasulo
from instruction import Instruction

def decode_file(file_path: str) -> List[Instruction]:
    instructions = []
    
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
            instructions.append(instruction)
    
    return instructions

# Example usage:
def main():
    file_path = "program_basic.txt"
    instructions = decode_file(file_path)
    for instruction in instructions:
        print(instruction)


if __name__ == "__main__":
    main()