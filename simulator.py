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
PC = 0 
MAR = 0
IR = 0
MDR = 0
ACC = 0
TMP = 0
CSAR = 0

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
cs[13][NEXT] = 4
cs[14][NEXT] = 0
cs[15][NEXT] = 0

#file input
def read():
    i = 0
    f = open("microism.txt", "r")
    for line in f:
        for word in line.split():
            if word != "-1":
                mem[i] = word
            i+=1

#main
read()

print("low memory:", end='')
for x in range(20):
    print(" ", mem[x], end='')
    if x==9:
        print("")
        print("         ", end='')
