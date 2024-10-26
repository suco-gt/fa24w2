#########################################################################################################
# tomasulo.py
# This is where you will implement your main Tomasulo logic.
#
#########################################################################################################

import copy

##################################################################################################################################
# GLOBAL VARIABLES & CLASSES
# Please do not edit these.
##################################################################################################################################

# RegisterFile
# Defines a single register.
class Register:
    def __init__(self, number, tag, ready_bit=1):
        self.number = number
        self.tag = tag
        self.ready_bit = ready_bit

# ReservationStation
# Defines a single reservation station, which is used to track a single instruction.
class ReservationStation:
    def __init__(self, instruction_opcode, instruction_count,
                 dest_reg, dest_reg_tag,
                 src_reg1, src_reg1_ready_bit, src_reg1_tag,
                 src_reg2, src_reg2_ready_bit, src_reg2_tag):

        self.instruction_opcode = instruction_opcode
        self.instruction_count = instruction_count

        self.dest_reg = dest_reg
        self.dest_reg_tag = dest_reg_tag

        self.src_reg1 = src_reg1
        self.src_reg1_ready_bit = src_reg1_ready_bit
        self.src_reg1_tag = src_reg1_tag

        self.src_reg2 = src_reg2
        self.src_reg2_ready_bit = src_reg2_ready_bit
        self.src_reg2_tag = src_reg2_tag

# FunctionalUnit
# Defines a single function unit. These include ALUs, MULs, and LSUs.
class FunctionalUnit:
    def __init__(self, fu_type, associated_reservation_station, busy, cycle_time, current_cycles_spent_executing):
        self.fu_type = fu_type
        self.associated_reservation_station = associated_reservation_station
        self.busy = busy
        self.cycle_time = cycle_time
        self.current_cycles_spent_executing = current_cycles_spent_executing

# Defines our functional units.
alu_functional_units = []
mul_functional_units = []
lsu_functional_units = []

# Defines our register file as a list of Register objects.
register_file = []

# Defines the scheduling unit as a list of ReservationStations
scheduling_unit = []
scheduling_unit_max_size = 0

# For keeping track of unique tags.
global_tag_counter = 20


##################################################################################################################################
# STAGE 3: Exec
#
# This stage of execution is responsible for first moving each reservation station/instruction through
# the functional units. We do this by looping over all our functional units and progressing them. If we find
# that a reservation station/instruction has completed, we remove it from the functional unit, mark the functional
# unit as free, and then put it on the common_data_bus: a list of reservation stations/instructions that have completed.

# Next, once we have progressed all functional units and gathered all our completed reservation stations, we'll
# want to go and update our scheduling unit and register file. We'll want to remove the completed reservation
# station from the scheduling unit (since, well, its officially completed), as well as update any reservation
# stations that are waiting on our instruction to complete (i.e., their source registers have matching tags as our
# completed instruction's dest. reg!). We'll also update our register file to mark the completed instruction's
# destination register as no longer busy (if it was a write)
##################################################################################################################################

def stage_exec():

    global alu_functional_units
    global mul_functional_units
    global lsu_functional_units
    global register_file
    global scheduling_unit_max_size
    global scheduling_unit
    global global_tag_counter

    print("Stage Exec:")
    common_data_bus = []

    ## Progress through ALUs

    for alu in alu_functional_units:

        # If an ALU is currently busy (i.e. it has an associated reservation station), check if the number of
        # cycles spent executing is equal to the cycle time. If it is, then this ALU has completed its instruction.
        # We can then broadcast that reservation station on the CDB, and clear the ALU

        if (alu.busy == 1 and (alu.cycle_time == alu.current_cycles_spent_executing)):

            print(f"    Instruction Completed in ALU {alu.associated_reservation_station.instruction_count}: {alu.associated_reservation_station.instruction_opcode}  R{alu.associated_reservation_station.dest_reg}, R{alu.associated_reservation_station.src_reg1}, R{alu.associated_reservation_station.src_reg2}")
            common_data_bus.append(alu.associated_reservation_station)
            alu.associated_reservation_station = 0
            alu.busy = 0
            alu.current_cycles_spent_executing = 0

    ## Progress through MULs

    for mul in mul_functional_units:

        # If a MUL is currently busy (i.e. it has an associated reservation station), check if the number of
        # cycles spent executing is equal to the cycle time. If it is, then this MUL has completed its instruction.
        # We can then broadcast that reservation station on the CDB, and clear the MUL.

        # Otherwise, if the MUL is currently not done finished with its instruction, increment the number of cycles
        # it has currently spent executing the instruction.

        if (mul.busy == 1 and (mul.cycle_time == mul.current_cycles_spent_executing)):

            print(f"    Instruction Completed in MUL {mul.associated_reservation_station.instruction_count}: {mul.associated_reservation_station.instruction_opcode}  R{mul.associated_reservation_station.dest_reg}, R{mul.associated_reservation_station.src_reg1}, R{mul.associated_reservation_station.src_reg2}")
            common_data_bus.append(alu.associated_reservation_station)
            mul.associated_reservation_station = 0
            mul.busy = 0
            mul.current_cycles_spent_executing = 0

        elif (mul.busy == 1):

            mul.current_cycles_spent_executing += 1

    ## Progress through LSUs

    for lsu in lsu_functional_units:

        # If an LSU is currently busy (i.e. it has an associated reservation station), check if the number of
        # cycles spent executing is equal to the cycle time. If it is, then this MUL has completed its instruction.
        # We can then broadcast that reservation station on the CDB, and clear the MUL.

        # Otherwise, if the MUL is currently not done finished with its instruction, increment the number of cycles
        # it has currently spent executing the instruction.

        if (lsu.busy == 1 and (lsu.cycle_time == lsu.current_cycles_spent_executing)):

            print(f"    Instruction Completed in LSU {lsu.associated_reservation_station.instruction_count}: {lsu.associated_reservation_station.instruction_opcode}  R{lsu.associated_reservation_station.dest_reg}, R{lsu.associated_reservation_station.src_reg1}, R{lsu.associated_reservation_station.src_reg2}")
            common_data_bus.append(lsu.associated_reservation_station)
            lsu.associated_reservation_station = 0
            lsu.busy = 0
            lsu.current_cycles_spent_executing = 0

        elif (lsu.busy == 1):

            lsu.current_cycles_spent_executing += 1


    ## Now, we have all the completed instructions broadcasting on the CDB. Iterate through them all, and then update
    # the reservation stations currently in the scheduling unit and the register file.

    instructions_completed = len(common_data_bus)

    if (instructions_completed == 0):
        print("    Stage Exec Completed: 0 instructions were completed!")
        print(" ")
        return 0

    for reservation_station_cdb in common_data_bus:

        # Loop through all the registers in the register file. If the reservation station's dest_reg_tag matches
        # that register's tag, then set the register's ready_bit to 1, as we have successfully written to the register!

        if (reservation_station_cdb.instruction_opcode != "STORE"):
            for register in register_file:
                if (reservation_station_cdb.dest_reg_tag == register.tag):
                    num = register.number
                    print(f"    Updating Reg {num} to ready")
                    register.ready_bit = 1

        # Loop through all the reservation_stations in the scheduling unit. If the scheduling unit's R.S. has a matching
        # src_reg1_tag or src_reg2_tag, then update it.

        for reservation_station_sched in scheduling_unit:

            if (reservation_station_cdb.dest_reg_tag == reservation_station_sched.src_reg1_tag):
                print(f"    Updating Scheduling Unit: Readying SRC Register 1 for Instruction {reservation_station_sched.instruction_count}: {reservation_station_sched.instruction_opcode} R{reservation_station_sched.dest_reg}, R{reservation_station_sched.src_reg1}, R{reservation_station_sched.src_reg2}")
                reservation_station_sched.src_reg1_ready_bit = 1

            if (reservation_station_cdb.instruction_opcode != "LOAD"):
                if (reservation_station_cdb.dest_reg_tag == reservation_station_sched.src_reg2_tag):
                    print(f"    Updating Scheduling Unit: Readying SRC Register 2 for Instruction {reservation_station_sched.instruction_count}: {reservation_station_sched.instruction_opcode} R{reservation_station_sched.dest_reg}, R{reservation_station_sched.src_reg1}, R{reservation_station_sched.src_reg2}")
                    reservation_station_sched.src_reg2_ready_bit = 1


    print(f"    Stage Exec Completed: {instructions_completed} instructions were completed!")
    return instructions_completed


##################################################################################################################################
# STAGE 2: Fire
#
# This stage is responsible for looking through the scheduling unit and firing instructions that have their
# source pregs marked as ready. Note that when multiple instructions are ready to fire in a given
# cycle, they must be fired in program order.

# We'll first loop through our entire scheduling unit to see what instructions are ready to execute. Then, we
# will fire them to our functional units (removing them from the scheduling unit and then updating the functional
# unit's fields).
##################################################################################################################################

def stage_fire():

    global alu_functional_units
    global mul_functional_units
    global lsu_functional_units
    global register_file
    global scheduling_unit_max_size
    global scheduling_unit
    global global_tag_counter

    print("Stage Fire:")

    instructions_fired = 0

    # We'll track all the reservation_stations ready to fire in arrays. Loop through the scheduling unit and add any
    # instructions ready to fire to these arrays

    ready_to_fire_alu_res_stations = []
    ready_to_fire_mul_res_stations = []
    ready_to_fire_lsu_res_stations = []

    for reservation_station in scheduling_unit:

        if (reservation_station.instruction_opcode == "ADD" or reservation_station.instruction_opcode == "SUB"):

            if (reservation_station.src_reg1_ready_bit == 1 and reservation_station.src_reg2_ready_bit == 1):
                print(f"    Ready to fire {reservation_station.instruction_count}: {reservation_station.instruction_opcode} R{reservation_station.dest_reg}, R{reservation_station.src_reg1}, R{reservation_station.src_reg2} ")
                ready_to_fire_alu_res_stations.append(reservation_station)

        if (reservation_station.instruction_opcode == "MUL"):

            if (reservation_station.src_reg1_ready_bit == 1 and reservation_station.src_reg2_ready_bit == 1):
                print(f"    Ready to fire {reservation_station.instruction_count}: {reservation_station.instruction_opcode} R{reservation_station.dest_reg}, R{reservation_station.src_reg1}, R{reservation_station.src_reg2} ")
                ready_to_fire_mul_res_stations.append(reservation_station)

        if (reservation_station.instruction_opcode == "LOAD"):

            if (reservation_station.src_reg1_ready_bit == 1):
                print(f"    Ready to fire {reservation_station.instruction_count}: {reservation_station.instruction_opcode} R{reservation_station.dest_reg}, R{reservation_station.src_reg1}, R{reservation_station.src_reg2} ")
                ready_to_fire_lsu_res_stations.append(reservation_station)

        if (reservation_station.instruction_opcode == "STORE"):

            if (reservation_station.src_reg1_ready_bit == 1 and reservation_station.src_reg2_ready_bit == 1):
                print(f"    Ready to fire {reservation_station.instruction_count}: {reservation_station.instruction_opcode} R{reservation_station.dest_reg}, R{reservation_station.src_reg1}, R{reservation_station.src_reg2} ")
                ready_to_fire_lsu_res_stations.append(reservation_station)

    # Now that we have gathered which reservation stations are ready to be fired, we'll attempt to fire them.

    # Iterate through all our alu functional units. If any of them are free (busy == 0), then select a reservation
    # station from the ready_to_fire_alu_res_station list. Then, fire it on the function unit by setting its
    # associated_reservation_station, busy to 1, cycle_time to 1, and current_cycles_spent_executing to 1

    if (len(ready_to_fire_alu_res_stations) == len(ready_to_fire_mul_res_stations) == len(ready_to_fire_lsu_res_stations) == 0):
        print("    Stage Fire Completed: No instructions were ready to fire!")
        print(" ")
        return

    i = 0
    while (ready_to_fire_alu_res_stations and i < len(alu_functional_units)):

        if (alu_functional_units[i].busy == 0):

            index = find_index_of_reservation_station_with_lowest_instruction_count(ready_to_fire_alu_res_stations)
            reservation_station_to_fire = copy.deepcopy(ready_to_fire_alu_res_stations[index])
            print(f"    Firing Instruction to ALU {i}: {reservation_station_to_fire.instruction_count}: {reservation_station_to_fire.instruction_opcode} R{reservation_station_to_fire.dest_reg}, R{reservation_station_to_fire.src_reg1}, R{reservation_station_to_fire.src_reg2} ")
            instructions_fired += 1
            remove_reservation_station_from_scheduling_unit(ready_to_fire_alu_res_stations[index])

            alu_functional_units[i].associated_reservation_station = reservation_station_to_fire
            alu_functional_units[i].busy = 1
            alu_functional_units[i].cycle_time = 1
            alu_functional_units[i].current_cycles_spent_executing = 1
            ready_to_fire_alu_res_stations.pop(index)


        i += 1

    # Iterate through all our mul functional units. If any of them are free (busy == 0), then select a reservation
    # station from the ready_to_fire_mul_res_station list. Then, fire it on the function unit by setting its
    # associated_reservation_station, busy to 1, cycle_time to 3, and current_cycles_spent_executing to 1
    j = 0
    while (ready_to_fire_mul_res_stations and j < len(mul_functional_units)):

        if (mul_functional_units[j].busy == 0):

            index = find_index_of_reservation_station_with_lowest_instruction_count(ready_to_fire_mul_res_stations)
            reservation_station_to_fire = copy.deepcopy(ready_to_fire_mul_res_stations[index])
            print(f"Firing Instruction to MUL {j}: {reservation_station_to_fire.instruction_count}: {reservation_station_to_fire.instruction_opcode} R{reservation_station_to_fire.dest_reg}, R{reservation_station_to_fire.src_reg1}, R{reservation_station_to_fire.src_reg2} ")
            instructions_fired += 1
            remove_reservation_station_from_scheduling_unit(ready_to_fire_mul_res_stations[index])

            mul_functional_units[j].associated_reservation_station = reservation_station_to_fire
            mul_functional_units[j].busy = 1
            mul_functional_units[j].cycle_time = 3
            mul_functional_units[j].current_cycles_spent_executing = 1
            ready_to_fire_mul_res_stations.pop(index)

        j += 1

    # Iterate through all our mul functional units. If any of them are free (busy == 0), then select a reservation
    # station from the ready_to_fire_mul_res_station list. Then, fire it on the function unit! If its a load instruction,
    # it should spend 4 cycles in the lsu unit. If its a store instruction, it only spends 2.
    k = 0
    while (ready_to_fire_lsu_res_stations and k < len(lsu_functional_units)):

        if (lsu_functional_units[k].busy == 0):

            index = find_index_of_reservation_station_with_lowest_instruction_count(ready_to_fire_lsu_res_stations)
            reservation_station_to_fire = copy.deepcopy(ready_to_fire_lsu_res_stations[index])
            print(f"    Firing Instruction to LSU {k}: {reservation_station_to_fire.instruction_count}: {reservation_station_to_fire.instruction_opcode}, R{reservation_station_to_fire.dest_reg}, R{reservation_station_to_fire.src_reg1}, R{reservation_station_to_fire.src_reg2} ")
            instructions_fired += 1
            remove_reservation_station_from_scheduling_unit(ready_to_fire_lsu_res_stations[index])

            lsu_functional_units[k].associated_reservation_station = reservation_station_to_fire
            lsu_functional_units[k].busy = 1
            ready_to_fire_lsu_res_stations.pop(index)

            if (reservation_station_to_fire.instruction_opcode == "LOAD"):
                lsu_functional_units[k].cycle_time = 4
                lsu_functional_units[k].current_cycles_spent_executing = 1

            if (reservation_station_to_fire.instruction_opcode == "STORE"):
                lsu_functional_units[k].cycle_time = 2
                lsu_functional_units[k].current_cycles_spent_executing = 1

        k += 1

    print(f"    Stage Fire Completed: {instructions_fired} instructions were fired!")
    print(" ")

##################################################################################################################################
# STAGE 1: Dispatch
#
# This stage is responsible for adding incoming instructions to the scheduling unit.

# The driver will give this function an list of instruction objects to add to the unit. If the scheduling unit
# is totally full, then we will not add it to our scheduling unit. If we have room in our scheduling unit,
# we'll create a reservation station for the instruction, update the register file, and then add our
# new reservation station to the scheduling queue.
##################################################################################################################################

def stage_dispatch(instructions):

    global alu_functional_units
    global mul_functional_units
    global lsu_functional_units
    global register_file
    global scheduling_unit_max_size
    global scheduling_unit
    global global_tag_counter

    print("Stage Dispatch:")

    if (len(instructions) == 0):
            print_scheduling_unit()
            print(f"    Stage Dispatch Completed. No more instructions were added to the Scheduling Unit")
            print(" ")
            return 0

    instructions_added = 0
    for instruction in instructions:

        if (len(scheduling_unit) >= scheduling_unit_max_size):
            print_scheduling_unit()
            print(f"    Stage Dispatch Completed. {instructions_added} instructions were added to the Scheduling Unit")
            print(" ")
            return instructions_added

        instruction_opcode = instruction.opcode
        instruction_count = instruction.count

        dest_reg = instruction.dest_reg
        if (dest_reg != -1):
            dest_reg_tag = generate_unique_tag()
        else:
            dest_reg_tag = -1

        src_reg1 = instruction.src_reg1
        src_reg1_ready_bit = -1
        src_reg1_tag = -1

        src_reg2 = instruction.src_reg2
        src_reg2_ready_bit = -1
        src_reg2_tag = -1

        # Loop through the register file to determine whether or not the src1_reg is ready (if it is, yay! if not, then just copy its tag and set its
        # ready bit to zero) and src2_reg is ready (same thing: if its ready, hurray! if not, copy its tag and set its ready bit to zero).

        for register in register_file:
            if (register.number == src_reg1):
                if (register.ready_bit == 1):
                    src_reg1_ready_bit = 1
                else:
                    src_reg1_ready_bit = 0
                    src_reg1_tag = register.tag

            if (register.number == src_reg2):
                if (register.ready_bit == 1):
                    src_reg2_ready_bit = 1
                else:
                    src_reg2_ready_bit = 0
                    src_reg2_tag = register.tag

        # Then, if the instruction involves writing data to a register, update the register file once again to set the dest_reg's ready bit to 0.

        if (dest_reg != -1):
            for register in register_file:
                if (register.number == dest_reg):
                    register.ready_bit = 0
                    register.tag = dest_reg_tag

        # We can now finally create the reservation station, and then append it to our scheduling unit!

        reservation_station = ReservationStation(instruction_opcode, instruction_count, dest_reg, dest_reg_tag, src_reg1, src_reg1_ready_bit, src_reg1_tag, src_reg2, src_reg2_ready_bit, src_reg2_tag)
        print(f"    Adding Instruction to Scheduling Unit: {reservation_station.instruction_count}: {reservation_station.instruction_opcode} R{reservation_station.dest_reg}, R{reservation_station.src_reg1}, R{reservation_station.src_reg2} ")
        scheduling_unit.append(reservation_station)
        instructions_added += 1


    print_scheduling_unit()
    print(f"    Stage Dispatch Completed. {instructions_added} instructions were added to the Scheduling Unit")
    print(" ")
    return instructions_added



##################################################################################################################################
# Helper Functions
#
# These are helper functions that you may use to complete your implementation.
##################################################################################################################################


# Function that, given any list of reservation station, finds the index of the reservation station that has
# the lowest instruction count.
def find_index_of_reservation_station_with_lowest_instruction_count(rs_list):

    min_instruction_count = rs_list[0].instruction_count
    index_of_instruction = 0
    i = 0

    for reservation_station in rs_list:
        if (reservation_station.instruction_count < min_instruction_count):
            min_instruction_count = reservation_station.instruction_count
            index_of_instruction = i
        i += 1
    return index_of_instruction

# Function that removes a given reservation station from the scheduling unit.
def remove_reservation_station_from_scheduling_unit(reservation_station):


    ic = reservation_station.instruction_count
    opcode = reservation_station.instruction_opcode
    i = 0
    k = 0
    for rs in scheduling_unit:
        if (rs.instruction_count == ic and rs.instruction_opcode == opcode):
            k = 1
            print(f"    Instruction {ic}: {opcode} has been removed from the scheduling unit")
            scheduling_unit.pop(i)
            return
        i += 1

    if (k == 0):
        print(f"    Error: Instruction {ic}: {opcode} has not been found in the scheduling unit")

# Function that generates a unique numerical tag.
def generate_unique_tag():

    global global_tag_counter
    num = global_tag_counter
    global_tag_counter += 1
    return num

# Function that neatly prints the contents of the scheduling unit
def print_scheduling_unit():
    print("    Scheduling Unit View:")
    print("    -------------------------------------------------------------------------------------------")
    print("    | R.S. # | Count | Opcode |  DR  | DR Tag | SRC1  | Ready |  Tag  | SRC2  | Ready |  Tag  |")
    print("    -------------------------------------------------------------------------------------------")

    global scheduling_unit
    n = 0
    for rs in scheduling_unit:
        # Define field variables for clarity
        count = rs.instruction_count
        opcode = rs.instruction_opcode
        dr = f"R{rs.dest_reg}"
        dr_tag = f"#{rs.dest_reg_tag}"
        src1 = f"R{rs.src_reg1}"
        src1_ready = rs.src_reg1_ready_bit
        src1_tag = f"#{rs.src_reg1_tag}"
        src2 = f"R{rs.src_reg2}"
        src2_ready = rs.src_reg2_ready_bit
        src2_tag = f"#{rs.src_reg2_tag}"

        # Print each line with fixed-width fields
        print(f"    |   {n:<4} | {count:<5} | {opcode:<6} | {dr:<4} | {dr_tag:<6} | {src1:<5} | {src1_ready:<5} | {src1_tag:<5} | {src2:<5} | {src2_ready:<5} | {src2_tag:<5} |")

        n += 1






##################################################################################################################################
# Initialization Function
#
# This function initializes and configures the Tomasulo Simulator
##################################################################################################################################

def initialize_tomasulo(num_of_alus, num_of_muls, num_of_lsus, num_of_regs, scheduling_unit_size):

    global alu_functional_units
    global mul_functional_units
    global lsu_functional_units
    global register_file
    global scheduling_unit_max_size
    global scheduling_unit
    global global_tag_counter

    alu_functional_units = [
        FunctionalUnit(
            fu_type = "alu",
            associated_reservation_station = None,
            busy = 0,
            cycle_time = 1,
            current_cycles_spent_executing = 0
        ) for _ in range(num_of_alus)
    ]

    mul_functional_units = [
        FunctionalUnit(
            fu_type = "mul",
            associated_reservation_station = None,
            busy = 0,
            cycle_time = 3,
            current_cycles_spent_executing = 0
        ) for _ in range(num_of_muls)
    ]

    lsu_functional_units = [
        FunctionalUnit(
            fu_type = "lsu",
            associated_reservation_station = None,
            busy = 0,
            cycle_time = -1,
            current_cycles_spent_executing = 0
        ) for _ in range(num_of_lsus)
    ]

    register_file = [
        Register(
            number = i,
            tag = -1
        ) for i in range(num_of_regs)
    ]

    scheduling_unit_max_size = scheduling_unit_size