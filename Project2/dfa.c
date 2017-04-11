#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

struct inst{
	char regs[20];
	char full_inst[20];
	int level;
	int orig_level;

}inst;

int check(struct inst current, struct inst check){
	char *cur;
	cur = strtok(current.regs, "$");
	while(cur != NULL){
		if(strstr(check.regs, cur) != NULL){
			return 1;
		}
		cur = strtok(NULL, "$");	
	}
	//not found
	return 0;
}

int main(int argc, char *argv[]){
	
//	bool rename = false;
	int delay = 1;
	char line[16];
	char * cur;

	//open argc - 1
	FILE *fp;
	fp = fopen(argv[argc-1], "r");


	//get command line flags
	int f;
	while((f = getopt(argc, argv, "rl:")) != -1){
		switch(f){
			case 'r':
						 break;

			case 'l': delay = atoi(optarg);
						 
						 break;

			default:
						 break;
		}
	}
	printf("load delay set to %d\n", delay);

	int lines=0;
	while(fgets(line, sizeof(line), fp)){
		lines++;
	}
	rewind(fp);

	struct inst instructions[lines];

	int level=0;
	char in[20];
	//go through each line
	while(fgets(line, sizeof(line), fp)){
		strcpy(instructions[level].full_inst, line);
		instructions[level].level = level;  //please fix this ugly code later
		instructions[level].orig_level = level;
		//tokeninze line
		cur = strtok(line, " ,()\n");
		while(cur != NULL){
			//check for register indicator, ignoring duplicates
			if(strstr(cur, "$") != NULL && strstr(in, cur) == NULL){
				strcat(in, cur);	
			}
			cur = strtok(NULL, " ,()\n");
		}
		//save the registers
		strcpy(instructions[level++].regs, in);
		strcpy(in, "");
	}
	fclose(fp);

	int i;
	int j;
	int k;
	int found = 0;
	int moved;
	
	//go through lines and raise level if possible
	for(i=1; i<lines; i++){
		j=1;
		found = 0;
		moved = 0;
		//change level as many times as needed
		while(found == 0 && j>=0){
			//check if current regs are in previous instruction
			found = check(instructions[i], instructions[i-j]);
			if(found == 0){
				instructions[i].level = instructions[i-j].level;
				moved = 1;
			}
			j++;
		}
		//if an inst moved up, adjust following instructions
		if(moved == 1)
			for(k=i+1; k<lines; k++)
				instructions[k].level--;
	}
	
	//check for delay
	if(delay !=1){
		for(i=0; i<lines; i++){
			level = instructions[i].level;
			//if current inst is lw, adjust level of subsequent insts
			if(strstr(instructions[i].full_inst, "lw") != NULL){
				for(j=i+1; j<lines; j++){
					//dont adjust things on the same level
					if(instructions[j].level != level)
						instructions[j].level += delay-1;
		
				}	
			}
		}
	}	
	
	//sort to group levels together
	struct inst temp;
	for(i=lines-1; i>=0; i--){
		for(j=1; j<=i; j++){
			if(instructions[j-1].level > instructions[j].level){
				temp = instructions[j-1];
				instructions[j-1] = instructions[j];
				instructions[j] = temp;
			}
		}
	}


	//print result
	int print = -1;
	for(i=0; i<lines; i++){
		if(print != instructions[i].level){
			print = instructions[i].level;
			printf("level %d instructions:\n", print);
		}
		printf("	%d %s", instructions[i].orig_level, instructions[i].full_inst);
	}

	printf("the data flow can be executed in %d cycles\n", instructions[lines-1].level+1);
	


	return 0;
}
