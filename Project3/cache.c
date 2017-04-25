#include <stdio.h>
#include <string.h>
#include <stdlib.h>

struct processor{
	char addr[3], *action;
	int rhit, whit, rmiss, wmiss, wrd1, wrd2;
	char state;
	int active;
};

int mem[512];
int READ=0, RIM=0, WB=0, INV=0;
char *BUS;
struct processor *p0, *p1;

void state_print(struct processor *p0, struct processor *p1, char* bus){
	
	//print info for p0
	if(p0->state == 'I')
		printf("           I ----- ---- ----	");
	else if(p0->active == 1){
		printf("%-5s %s  %c   %s    %d    %d    ", p0->action, p0->addr, p0->state, p0->addr, p0->wrd1, p0->wrd2);
	}
	else{
		printf("           %c   %s    %d    %d    ", p0->state, p0->addr, p0->wrd1, p0->wrd2);

	}
	//print bus action
	printf("%s", bus);

	//print info for p1
	if(p1->state == 'I')
		printf("	   	     I ----- ---- ----\n");
	else if(p1->active == 1){
		printf("	  %-5s %s  %c   %s    %d    %d\n", p1->action, p1->addr, p1->state, p1->addr, p1->wrd1, p1->wrd2);
	}
	else{
		printf("		     %c   %s    %d    %d\n", p1->state, p1->addr, p1->wrd1, p1->wrd2);
	}
}

void process(char action, char addr[3], int proc){
	struct processor *active;
	struct processor *snoop;

	if(proc == 0){
		active = p0;
		snoop = p1;
	}
	else{
		active = p1;
		snoop = p0;
	}


	//cache hit
	if(strcmp(active->addr, addr) == 0){

		switch(active->state){
			case 'S':
				if(action == 'r'){
					active->action = "read";
					active->rhit++;
					active->state = 'S';
					BUS = "(none)";
				}
				else{
					active->action = "write";
					active->whit++;
					active->state = 'M';
					BUS = "INV";
				}
				break;
			case 'M':
				if(action == 'r'){
					active->action = "read";
					active->rhit++;
					active->state = 'M';
					BUS = "(none)";
				}
				else{
					active->action = "write";
					active->whit++;
					active->state = 'M';
					BUS = "(none)";
				}
				break;
			default:
				printf("hit default\n");
				break;
		}
	}
	else{
		switch(active->state){
			case 'I':
				if(action == 'r'){
					active->action = "read";
					active->rmiss++;
					active->state = 'S';
					BUS = "READ";
				}
				else{
					active->action = "write";
					active->wmiss++;
					active->state = 'M';
					BUS = "RIM";
				}
				break;
			case 'S':
				if(action == 'r'){
					active->action = "read";
					active->rmiss++;
					active->state = 'S';
					BUS = "READ";
				}
				else{
					active->action = "write";
					active->wmiss++;
					active->state = 'M';
					BUS = "RIM";
				}
				break;
			case 'M':
				if(action == 'r'){
					active->action = "read";
					active->rmiss++;
					active->state = 'S';
					BUS = "READ";
					printf("                                WBr\n");
					WB++;
				}
				else{
					active->action = "write";
					active->wmiss++;
					active->state = 'M';
					BUS = "RIM";
					printf("                                WBr\n");
					WB++;
				}
				break;
			default:
				printf("miss default\n");
				break;

		}

	}


	if(strcmp(snoop->addr, addr) == 0){
		switch(snoop->state){
			case 'S':
				switch(BUS[1]){
					case 'I':
						snoop->state = 'I';
						break;
					case 'N':
						snoop->state = 'I';
						break;
					case 'E':
						snoop->state = 'S';
						break;
				}
				break;
			case 'M':
				switch(BUS[1]){
					case 'E':
						snoop->state = 'S';
						BUS = "RD/WB";
						break;
					case 'I':
						snoop->state = 'I';
						BUS = "RIM/WB";
						break;
				}
				break;
		}
	}

	strcpy(active->addr, addr);
	if(proc == 0){
		p0 = active;
		p0->active = 1;
		p1 = snoop;
		p1->active = 0;
	}
	else{
		p1 = active;
		p1->active = 1;
		p0 = snoop;
		p0->active = 0;
	}

	if(strstr(BUS, "RE") != NULL)
		READ++;
	if(strstr(BUS, "RD") != NULL)
		READ++;
	if(strstr(BUS, "INV") != NULL)
		INV++;
	if(strstr(BUS, "RIM") != NULL)
		RIM++;
	if(strstr(BUS, "WB") != NULL)
		WB++;

	state_print(p0, p1, BUS);
}


int main(int argc, char *argv[]){

	printf("        processor 0              bus               processor 1\n");
	printf("----------------------------    ------    ----------------------------\n");
	printf("  action     cache contents     action      action     cache contents\n");
	printf("             addr  wrd0 wrd1                           addr  wrd0 wrd1\n");
	printf("           I ----- ---- ----                         I ----- ---- ----\n");



	FILE *fp = fopen(argv[argc-1], "r");
	char line[6];
	char addr[3];
	int i;
	
	p0 = malloc(sizeof(struct processor));
	p1 = malloc(sizeof(struct processor));

	p0->state = p1->state = 'I';
	p0->action = p1->action = "";
	p0->rhit = p0->whit = p1->rhit = p1->whit = p0->rmiss = p1->rmiss = p0->wmiss = p1->wmiss = 0;
	p0->active = p1->active = 0;

	while(fgets(line, sizeof(line), fp)){
		//p0->selected
		if(line[0] == '0'){
			for(i=0; i<3; i++){
				addr[i] = line[i+2];
			}
			process(line[1], addr, 0);
		}
		//p1->selected
		else if(line[0] == '1'){
			for(i=0; i<3; i++){
				addr[i] = line[i+2];
			}
			process(line[1], addr, 1);
		}
		//end processing
	}

	

	printf("\nStats:\n");
	printf("  processor 0        processor 1        bus\n");
	printf("---------------    ---------------    --------\n");
	printf("read hits     %d    read hits     %d    READs  %d\n", p0->rhit, p1->rhit, READ);
	printf("read misses   %d    read misses   %d    RIMS   %d\n", p0->rmiss, p1->rmiss, RIM);
	printf("write hits    %d    write hits    %d    WBs    %d\n", p0->whit, p1->whit, WB);
	printf("write misses  %d    write misses  %d    INVs   %d\n", p0->wmiss, p1->wmiss, INV);
	printf("---------------    ---------------    --------\n");

	double p1hr = (double)(p1->rhit + p1->whit) / (double)(p1->rmiss + p1->wmiss + p1->rhit + p1->whit);
	p1hr *= 100;
	double p0hr = (double)(p0->rhit + p0->whit) / (double)(p0->rmiss + p0->wmiss + p0->rhit + p0->whit);
	p0hr *= 100;
	int total = READ + RIM + WB + INV;

	printf("hit rate %2.1f%%     hit rate %2.1f%%     total  %d\n", p0hr, p1hr, total);

	return 0;
}
