# Fall 2024 Workshop 2: CPU Architecture

## SETUP INSTRUCTIONS

You're welcome to copy and paste these files, but the easiest way is to clone this Github Repository. To do so, you must have Git installed on your computer. [Download the latest version here](https://git-scm.com/downloads). Simply open up a terminal in the location you want the project to go (we recommend making a separate folder), and then run `git clone https://github.com/suco-gt/fa24w2.git`, which will copy all the files automatically.

This workshop involves using Python extensively. If you're a bit rusty, the [W3 Schools Manual](https://www.w3schools.com/python/) is an excellent resoruce to quickly browse. Please ensure that you have Python or Python3 downloaded on your computer, as you will need it to run the code. [Download the latest Python version here](https://www.python.org/downloads/). 

## INTRODUCTION: `tomasulo.py`

In this workshop, we'll be implementing a CPU simulator, specifically one that simulates Tomasulo's algorithm. Our simulator will be implemented in the `tomasulo.py` file, where we'll implement three functions that define all the logic for our CPU. These three functions are `stage_dispatch`, `stage_fire`, and `stage_exec`. Our workshop will see us implementing these three functions, which collectively manage the 3 data structures/components involved in Tomasulo's algorithm: the scheduling unit, functional units, and the register file. 

```
tomasulo.py

def stage_exec():
  # Stage 3: Responsible for executing and completing instructions.

def stage_fire():
  # Stage 2: Responsible for moving instructions from the scheduling unit to the functional units, where they get executed.

def stage_dispatch():
  # Stage 1: Responsible for adding incoming instructions to the scheduling unit.

```
### THE SCHEDULING UNIT
The Scheduling Unit is our component/data structure that temporarily holds instructions that are waiting to be executed. You can think of it like almost like a complex "queue" for instructions that are waiting to fire. When instructions are ready to be executed, they will be "fired" to a functional unit that will handle their completion. 

Each "entry" of the scheduling unit is called a reservation station. A reservation stations simply holds info about the instruction that's waiting to execute, such as it's opcode, it's source and destination registers, as well info about the current state of those registers. In our simulator, we define a reservation station as a class in `tomasulo.py`
```
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
```
You'll notice the familiar fields from an instruction, like the opcode, count, dest_reg, and src regs, but reservation stations also have fields labeled `tag` and `ready_bit`. These correspond to the unique tag IDs and ready bits associated with Tomasulo's algorithm! 

The scheduling unit itself is just implemented as a standard list of these reservation_station objects. We also define its maximum size with the `scheduling_unit_max_size` variable in `tomasulo.py`
```
# Defines the scheduling unit as a list of ReservationStations
scheduling_unit = []
scheduling_unit_max_size = 0
```
### THE REGISTER FILE
Once again, our register file must contain both a `tag` field and `ready` bit field to track each register's current status in Tomasulo's algorithm. Like the scheduling unit and reservation stations, registers and register file are defined as a class and an array of `Register` objects in `tomasulo.py`
```
# RegisterFile
# Defines a single register.
class Register:
    def __init__(self, number, tag, ready_bit=1):
        self.number = number
        self.tag = tag
        self.ready_bit = ready_bit
```
```
register_file = []
```
You are able to define how many registers you want to have in the `driver.py` file. We'll get to that eventually.

### FUNCTIONAL UNITS
We have 3 types of functional units in our simulator: Arithmatic Logic Units (ALUs), Multiplication Units (MULs), and Load-Store Units (LSUs). ALUs are responsible for performing the mathematical operations required to execute ADD and SUB instructions. MUL units are required to execute MUL instructions. Lastly, LSUs can access memory and execute LOAD and STORE instructions. Each unit is defined in an overall `FunctionalUnit` class in tomasulo.py
```
# FunctionalUnit
# Defines a single function unit. These include ALUs, MULs, and LSUs.
class FunctionalUnit:
    def __init__(self, fu_type, associated_reservation_station, busy, cycle_time, current_cycles_spent_executing):
        self.fu_type = fu_type
        self.associated_reservation_station = associated_reservation_station
        self.busy = busy
        self.cycle_time = cycle_time
        self.current_cycles_spent_executing = current_cycles_spent_executing
```
The `associated_reservation_station` field will hold the reservation station of the instruction the functional unit is currently operating on. For instance, if `ADD R0, R1, R2` is executing on ALU #1, then the `associated_reservation_station` field would be set to that instruction's reservation station. The `busy` field represents whether the functional unit is busy (1) or not (0). `cycle_time` refers to how many cycles it takes for a functional unit to execute. 
* ADD instructions take 1 cycle
* SUB instructions take 1 cycle
* MUL instructions take 3 cycles
* LOAD instructions take 4 cycles
* STORE instructions take 2 cycles

`current_cycles_spent_executing` refers to how many cycles the instruction that's occupying the functional unit has currently taken. For example, if the `ADD R0, R1, R2` instruction has spent 1 cycle in ALU #1, then this field will be set to 1. Note that, upon firing an instruction to a functional unit, you should set its `current_cycles_spent_executing` to start at 1. You will set all of these fields when firing an instruction in the `stage_fire` function.

These functional units are contained in the following global lists in `tomasulo.py`
```
# Defines our functional units.
alu_functional_units = []
mul_functional_units = []
lsu_functional_units = []
```

## YOUR TASK
As mentioned, your task is to complete the "TO-DO" sections of the three functions in `tomasulo.py`: `stage_exec`, `stage_fire`, and `stage_dispatch`. Each function is responsible for performing a step of Tomasulo's algorithm in a single cycle. They are described as follows.

### `stage_dispatch`
* This is the first stage, which is responsible for simply adding new instructions to the scheduling unit.
* This will take in a list of `Instruction` objects (given to you by the driver code, `driver.py`).
* Your job is to create `ReservationStation` objects for each of these instructions until either 1) The scheduling unit is full, or 2) There are no more Instructions to add.
* You will also need to update the register file based on Tomasulo's algorithm.

### `stage_fire`
* Once instructions have been added to the scheduling unit, we'll see if we can fire them.
* "Firing" an instruction simply means deploying it to a functional unit to be executed and then completed.
* In `stage_fire`, we'll check all of the reservation stations in the scheduling unit, looking to see if any of them are ready to fire.
* An instruction/reservation station can be fired if 1) all of its source registers' ready bit(s) are 1, and 2) there is a functional unit that is free.
* To actually perform the firing on an instruction, we'll remove its reservation station from the scheduling unit and copy it over to the `associated_reservation_station` field in the functional unit.

### `stage_exec`
* With instructions in our the functional units, we'll need to manage them.
* `stage_exec` simply updates all our instructions/reservation stations that are currently executing in the functional units, incrementing their `current_cycles_spent_executing` field by 1, as 
