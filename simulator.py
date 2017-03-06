'''
CPSC 3300 - S17
Project 1 - Microprogrammed processor simulator

This project simulates a microprogrammed processor. It reads in
instructions in hex format from the file microsim.txt, and then simulates
running the given commands.

To execute this file on the Clemson lab machines, use the command:
'python simulator.py'

The program will then simulate the instructions, and print the values of
the CPU registers and the microcode instructions to stdout.
'''
from __future__ import print_function

#constants
ACC_IN = 0 
ACC_OUT = 1
ALU_ADD = 2
ALU_SUB = 3
IR_IN = 4
IR_OUT = 5
MAR_IN = 6
MDR_IN = 7
MDR_OUT = 8
PC_IN = 9
PC_OUT = 10
PC_INCR = 11
READ = 12
TMP_OUT = 13
WRITE = 14
BRTABLE = 15
NEXT = 16
OR_ADDR = 17

#declarations
cs = [[0 for x in range(22)] for y in range(32)]
mem = [0 for x in range(512)]
CSIR = [0 for x in range(8)]
CSIGNALS = [0 for x in range(32)]
PC = 0 
MAR = 0
IR = 0
MDR = 0
ACC = 0
TMP = 0
CSAR = 0
CYCLE = 1
halt = False

#generate cs
cs[0][MAR_IN] = 1
cs[0][PC_OUT] = 1
cs[0][NEXT] = 2
cs[1][IR_OUT] = 1
cs[1][PC_IN] = 1
cs[1][NEXT] = 0
cs[2][PC_INCR] = 1
cs[2][READ] = 1
cs[2][NEXT] = 3
cs[3][IR_IN] = 1
cs[3][MDR_OUT] = 1
cs[3][NEXT] = 4
cs[4][BRTABLE] = 1
cs[5][IR_OUT] = 1
cs[5][MAR_IN] = 1
cs[5][NEXT] = 6
cs[6][READ] = 1
cs[6][NEXT] = 7
cs[7][ACC_IN] = 1
cs[7][PC_IN] = 1
cs[7][NEXT] = 0
cs[8][IR_OUT] = 1
cs[8][MAR_IN] = 1
cs[8][NEXT] = 9
cs[9][READ] = 1
cs[9][NEXT] = 10
cs[10][ACC_OUT] = 1
cs[10][ALU_ADD] = 1
cs[10][NEXT] = 11
cs[11][ACC_IN] = 1
cs[11][TMP_OUT] = 1
cs[11][NEXT] = 0
cs[12][IR_OUT] = 1
cs[12][MAR_IN] = 1
cs[12][NEXT] = 13
cs[13][ACC_OUT] = 1
cs[13][MDR_IN] = 1
cs[13][NEXT] = 14
cs[14][WRITE] = 1
cs[14][NEXT] = 0
cs[15][OR_ADDR] = 1
cs[15][NEXT] = 0
#extra instructions
#sub
cs[16][MAR_IN] = 1
cs[16][IR_OUT] = 1
cs[16][NEXT] = 17
cs[17][READ] = 1
cs[17][NEXT] = 18
cs[18][ACC_OUT] = 1
cs[18][ALU_SUB] = 1
cs[18][NEXT] = 19
cs[19][ACC_IN] = 1
cs[19][TMP_OUT] = 1
cs[19][NEXT] = 0
#jsub
cs[20][MAR_IN] = 1
cs[20][IR_OUT] = 1
cs[20][NEXT] = 21
cs[21][MDR_IN] = 1
cs[21][PC_OUT] = 1
cs[21][NEXT] = 22
cs[22][WRITE] = 1
cs[22][NEXT] = 23
cs[23][PC_IN] = 1
cs[23][IR_OUT] = 1
cs[23][NEXT] = 24
cs[24][PC_INCR] = 1
cs[24][NEXT] = 0
#jmpi
cs[25][MAR_IN] = 1
cs[25][IR_OUT] = 1
cs[25][NEXT] = 26
cs[26][READ] = 1
cs[26][NEXT] = 27
cs[27][PC_IN] = 1
cs[27][MDR_OUT] = 1
cs[27][NEXT] = 0

#control signal names
CSIGNALS[0] = "MAR_in PC_out"
CSIGNALS[1] = "PC_in IR_out"
CSIGNALS[2] = "pc_incr read"
CSIGNALS[3] = "IR_in MDR_out"
CSIGNALS[4] = "br_table"
CSIGNALS[5] = "MAR_in IR_out"
CSIGNALS[6] = "read"
CSIGNALS[7] = "ACC_in MDR_out"
CSIGNALS[8] = "MAR_in IR_out"
CSIGNALS[9] = "read"
CSIGNALS[10] = "ACC_out alu_add"
CSIGNALS[11] = "ACC_in TMP_out"
CSIGNALS[12] = "MAR_in IR_out"
CSIGNALS[13] = "MDR_in ACC_out"
CSIGNALS[14] = "write"
CSIGNALS[15] = "or_addr"
CSIGNALS[16] = "MAR_in IR_out"
CSIGNALS[17] = "read"
CSIGNALS[18] = "ACC_out ALU_sub"
CSIGNALS[19] = "ACC_in TMP_out"
CSIGNALS[20] = "MAR_in IR_out"
CSIGNALS[21] = "MDR_in PC_out"
CSIGNALS[22] = "write"
CSIGNALS[23] = "PC_in IR_out"
CSIGNALS[24] = "PC_incr"
CSIGNALS[25] = "MAR_in IR_out"
CSIGNALS[26] = "read"
CSIGNALS[27] = "PC_in MDR_out"

#CSIR used for brtable
CSIR[0] = 5
CSIR[1] = 8
CSIR[2] = 12 
CSIR[3] = 15
CSIR[4] = 16 
CSIR[5] = 20
CSIR[6] = 25

#hex to int
def hextoint(val):
    #converto to int
    ret = int(val, 16)
    #check if negative
    if ret >= 2048:
        ret -= 4096
    return ret

#file input
#place each item in file into mem[i] until we end, excluding -1
def read():
    i = 0
    f = open("microsim.txt", "r")
    for line in f:
        for word in line.split():
            if word != "-1":
                mem[i] = word
                i+=1

#print memory contents
def mem_print():
    print("low memory:", end='')
    for x in range(20):
        cur = " " + str(mem[x])
        print(cur.rjust(5), end='')
        if x==9:
            print("")
            print("           ", end='')
    print("\n")

#process mem
def process():
    global PC, halt
    while halt != True:
        #get 11 bit instruction as binary string
        instruction = str(bin(int(str(mem[PC]), 16))[2:].zfill(12))
    
        #get address as int
        addr = int(instruction[-9:], 2)
    
        #get opcode as int and execute it
        opcode = int(instruction[:3], 2)
        execute(opcode,addr)

#do opcode instruction
def execute(opcode, addr):
    options = {
        0 : load,
        1 : add,
        2 : store,
        3 : brz,
        4 : sub,
        5 : jsub,
        6 : jmpi,
        7 : halt,
    }
    options[opcode](addr)

#place contents of specified memory location into the ACC
def load(addr):
    global PC, IR, MAR, MDR, ACC, CSAR 
    #get address from PC
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #get memory at address
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #place memory into instruction register
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #branch based on CSIR
    cycle_print()
    CSAR = CSIR[0]
    #set mar to address of instruction
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #set MDR to memory value
    cycle_print()
    MDR = mem[MAR]
    CSAR = cs[CSAR][NEXT] 
    #place memory value into ACC as int
    cycle_print()
    ACC = hextoint(str(MDR))
    CSAR = cs[CSAR][NEXT] 
    
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

#place memory value into PC
def jmpi(addr):
    global PC, IR, MAR, MDR, ACC, CSAR 
    #get address from PC
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #get memory at address
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #place memory into instruction register
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #branch based on CSIR
    cycle_print()
    CSAR = CSIR[6]
    #place address from instruction into MAR
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #set MDR to memory value at address
    cycle_print()
    MDR = mem[MAR]
    CSAR = cs[CSAR][NEXT] 
    #place MDR into PC
    cycle_print()
    PC = hextoint(str(MDR))
    CSAR = cs[CSAR][NEXT]

    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

#save PC memory and update PC to new value
def jsub(addr):
    global PC, IR, MAR, MDR, ACC, CSAR 
    #get address from PC
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #get memory at address
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #place memory into instruction register
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #branch based on CSIR
    cycle_print()
    CSAR = CSIR[5]
    #place address from instruction into MAR
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT]
    #place PC into MDR
    cycle_print()
    MDR = PC
    CSAR = cs[CSAR][NEXT]
    #set mem[addr] as the saved PC
    cycle_print()
    mem[MAR] = format(MDR, 'x')
    CSAR = cs[CSAR][NEXT]
    #increment the PC
    cycle_print()
    PC = addr + 1
    CSAR = cs[CSAR][NEXT]
    cycle_print()
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")


#add contents of memory to the accumulator
def add(addr):
    global PC, IR, MAR, MDR, ACC, CSAR,TMP
    #get address from PC
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #get memory at address
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #place memory into instruction register
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #branch based on CSIR
    cycle_print()
    CSAR = CSIR[1]
    #set MAR as address from instruction
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #set MDR as value from address
    cycle_print()
    MDR = mem[MAR]
    CSAR = cs[CSAR][NEXT] 
    #do addition and place in TMP
    cycle_print()
    TMP = hextoint(str(MDR)) + ACC
    CSAR = cs[CSAR][NEXT] 
    #place TMP's value back into ACC
    cycle_print()
    ACC = TMP
    CSAR = cs[CSAR][NEXT] 
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

#subtract the contents of memory from the accumulator
def sub(addr):
    global PC, IR, MAR, MDR, ACC, CSAR,TMP
    #get address from PC
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #get memory at address
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #place memory into instruction register
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #branch based on CSIR
    cycle_print()
    CSAR = CSIR[4]
    #set MAR as address from instruction
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #set MDR as value from address
    cycle_print()
    MDR = mem[MAR]
    CSAR = cs[CSAR][NEXT] 
    #do subtraction and place in TMP
    cycle_print()
    TMP = int(ACC) - hextoint(str(MDR))
    CSAR = cs[CSAR][NEXT] 
    #place TMP's value back into ACC
    cycle_print()
    ACC = TMP
    CSAR = cs[CSAR][NEXT] 
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

#place value of accumulator into memory
def store(addr):
    global PC, IR, MAR, MDR, ACC, CSAR
    #get address from PC
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #get memory at address
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #place memory into instruction register
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #branch based on CSIR
    cycle_print()
    CSAR = CSIR[2]
    #set MAR as address from instruction
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #set MDR to value of ACC
    cycle_print()
    MDR = ACC
    CSAR = cs[CSAR][NEXT] 
    #write to memory in hex
    cycle_print()
    mem[MAR] = format(int(MDR) & 0xfff, 'x')
    CSAR = cs[CSAR][NEXT] 
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

#update PC if ACC==0
def brz(addr):
    global PC, IR, MAR, MDR, ACC, CSAR
    #get address from PC
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #get memory at address
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #place memory into instruction register
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #branch based on CSIR
    cycle_print()
    CSAR = CSIR[3]
    #if ACC==0, set PC to given address
    cycle_print()
    if ACC == 0:
        PC = addr
        CSAR = 1
        cycle_print()
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

#stop execution
def halt(addr):
    global PC, IR, MAR, MDR, ACC, halt, CSAR
    #get address from PC
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #get memory at address
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #place memory into instruction register
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #branch based on CSIR
    cycle_print()
    halt = True
    CSAR = 0
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

#convert a given int to hex
def inttohex(val):
    if(type(val) is int):
        if(val<0):
            val = format(val & 0xfff, 'x')
        else:
            val = format(val, 'x')
    return val

#print out the registers, CSIR, and control signals
def cycle_print():
    global PC, IR, MAR, MDR, ACC, halt, CYCLE, TMP
    acc = inttohex(ACC)
    tmp = inttohex(TMP)
    mar = inttohex(MAR)
    mdr = inttohex(MDR)
    print ("%4s:%3s %3s %3s %3s %3s %3s " 
           % (CYCLE, PC, IR, mar, mdr, acc, tmp), end='')
    print("%5s  " %(format(CSAR, '01x')), end='')
    CYCLE += 1
    for i in range(16):
        print (cs[CSAR][i], end='')
    print ("|%2s|%1s  " % (format(cs[CSAR][NEXT], '02x'), cs[CSAR][OR_ADDR])
           , CSIGNALS[CSAR])
    

#main
read()
mem_print()
print("cycle  PC  IR MAR MDR ACC TMP  CSAR          CSIR            cntl signals")
print("    +---+---+---+---+---+---+/----//---------------------//---------------/")
process()
print("")
mem_print()
