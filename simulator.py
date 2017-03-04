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
cs = [[0 for x in range(32)] for y in range(22)]
mem = [0 for x in range(512)]
CSIR = [0 for x in range(22)]
CSIGNALS = [0 for x in range(22)]
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
cs[1][IR_OUT] = 1
cs[1][PC_IN] = 1
cs[2][PC_INCR] = 1
cs[2][READ] = 1
cs[3][IR_IN] = 1
cs[3][MDR_OUT] = 1
cs[4][BRTABLE] = 1
cs[5][IR_OUT] = 1
cs[5][MAR_IN] = 1
cs[6][READ] = 1
cs[7][ACC_IN] = 1
cs[7][PC_IN] = 1
cs[8][IR_OUT] = 1
cs[8][MAR_IN] = 1
cs[9][READ] = 1
cs[10][ACC_OUT] = 1
cs[10][ALU_ADD] = 1
cs[11][ACC_IN] = 1
cs[11][TMP_OUT] = 1
cs[12][IR_OUT] = 1
cs[12][MAR_IN] = 1
cs[13][ACC_OUT] = 1
cs[13][MDR_IN] = 1
cs[14][WRITE] = 1
cs[15][OR_ADDR] = 1

#next addr
cs[0][NEXT] = 2
cs[1][NEXT] = 0
cs[2][NEXT] = 3
cs[3][NEXT] = 4
cs[5][NEXT] = 6
cs[6][NEXT] = 7
cs[7][NEXT] = 0
cs[8][NEXT] = 9
cs[9][NEXT] = 10
cs[10][NEXT] = 11
cs[11][NEXT] = 0
cs[12][NEXT] = 13
cs[13][NEXT] = 14
cs[14][NEXT] = 0
cs[15][NEXT] = 0

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

#hex to int
def hextoint(val):
    ret = int(val, 16)
    if ret >= 2048:
        ret -= 4096
    return ret

#file input
def read():
    i = 0
    f = open("microism.txt", "r")
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

def load(addr):
    global PC, IR, MAR, MDR, ACC, CSAR 
    #T1
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #T2
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #T3
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #T4br table
    cycle_print()
    CSAR = 5 
    #T5 
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #T6
    cycle_print()
    MDR = mem[MAR]
    CSAR = cs[CSAR][NEXT] 
    #T7
    cycle_print()
    ACC = hextoint(str(MDR))
    CSAR = cs[CSAR][NEXT] 
    
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

def jmpi(addr):
    global PC, IR, MAR, MDR, ACC, CSAR 
    #T1
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #T2
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #T3
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #T4br table
    #T5 
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #T6
    cycle_print()
    MDR = mem[MAR]
    CSAR = cs[CSAR][NEXT] 
    #T7
    cycle_print()
    PC = hextoint(str(MDR))
    CSAR = cs[CSAR][NEXT]

    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

def jsub(addr):
    global PC, IR, MAR, MDR, ACC, CSAR 
    #T1
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #T2
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #T3
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #T4br table
    CSAR = 15
    #T5
    cycle_print()
    PC = addr + 1
    CSAR = cs[CSAR][NEXT]
    #T6
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #T6
    cycle_print()
    MDR = PC
    CSAR = cs[CSAR][NEXT] 
    #T7
    cycle_print()
    mem[MAR] = MDR
    CSAR = cs[CSAR][NEXT] 
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")



def add(addr):
    global PC, IR, MAR, MDR, ACC, CSAR,TMP
    #T1
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #T2
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #T3
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #T4 br table
    cycle_print()
    CSAR = 8
    #T5
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #T6
    cycle_print()
    MDR = mem[MAR]
    CSAR = cs[CSAR][NEXT] 
    #T7
    cycle_print()
    TMP = hextoint(str(MDR)) + ACC
    CSAR = cs[CSAR][NEXT] 
    #T8
    cycle_print()
    ACC = TMP
    CSAR = cs[CSAR][NEXT] 
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

def sub(addr):
    global PC, IR, MAR, MDR, ACC, CSAR,TMP
    #T1
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #T2
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #T3
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #T4 br table
    cycle_print()
    CSAR = 8
    #T5
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #T6
    cycle_print()
    MDR = mem[MAR]
    CSAR = cs[CSAR][NEXT] 
    #T7
    cycle_print()
    TMP = ACC - hextoint(str(MDR))
    CSAR = cs[CSAR][NEXT] 
    #T8
    cycle_print()
    ACC = TMP
    CSAR = cs[CSAR][NEXT] 
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")


def store(addr):
    global PC, IR, MAR, MDR, ACC, CSAR
    #T1
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #T2
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #T3
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #T4 br table
    cycle_print()
    CSAR = 12
    #T5
    cycle_print()
    MAR = addr
    CSAR = cs[CSAR][NEXT] 
    #T6
    cycle_print()
    MDR = ACC
    CSAR = cs[CSAR][NEXT] 
    #T7
    cycle_print()
    mem[MAR] = MDR
    CSAR = cs[CSAR][NEXT] 
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

def brz(addr):
    global PC, IR, MAR, MDR, ACC, CSAR
    #T1
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #T2
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #T3
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #T4 br table
    cycle_print()
    CSAR = 15 
    #T5
    cycle_print()
    if ACC == 0:
        PC = addr
        CSAR = 1
        cycle_print()
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

def halt(addr):
    global PC, IR, MAR, MDR, ACC, halt, CSAR
    #T1
    cycle_print()
    MAR = int(PC)
    CSAR = cs[CSAR][NEXT] 
    #T2
    cycle_print()
    MDR = mem[MAR]
    PC += 1
    CSAR = cs[CSAR][NEXT] 
    #T3
    cycle_print()
    IR = MDR
    CSAR = cs[CSAR][NEXT] 
    #T4 br table
    cycle_print()
    halt = True
    CSAR = 0
    print("    +---+---+---+---+---+---+/----//---------------------//---------------/")

def cycle_print():
    global PC, IR, MAR, MDR, ACC, halt, CYCLE, TMP

    print ("%4s:%3s %3s %3s %3s %3s %3s " 
           % (CYCLE, PC, IR, MAR, MDR, ACC, TMP), end='')
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
