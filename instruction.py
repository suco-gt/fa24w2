#########################################################################################################
# Instruction.py
# A class for representing a single instruction.
#
# DO NOT MODIFY THIS FILE
#########################################################################################################

class Instruction:
    def __init__(self, opcode, count, dest_reg=0, src_reg1=0, src_reg2=0):
        self.opcode = opcode                                   # Instruction opcode (e.g., "ADD", "MUL", "LOAD", etc.)
        self.count = count                                     # Instruction count (e.g., 3 for third instruction in the program)
        self.dest_reg = dest_reg                               # Destination register (e.g., "R1", "R2", etc., or 0 if not applicable)
        self.src_reg1 = src_reg1                               # Source register 1 (e.g., "R1", "R2", etc., or 0 if not applicable)
        self.src_reg2 = src_reg2                               # Source register 2 (e.g., "R1", "R2", etc., or 0 if not applicable)

    def __repr__(self):
        return (f"Instruction(type={self.opcode}, order=Not Implemented, "
                f"dest_reg={self.dest_reg}, src_reg1={self.src_reg1}, src_reg2={self.src_reg2})")
