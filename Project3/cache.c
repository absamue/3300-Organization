#include <stdio.h>
#include <string.h>

struct processor{
	char *addr, *action;
	int rhit, whit, rmiss, wmiss, wrd1, wrd2;
	char state;

};

int mem[512];
int READ=0, RIM=0, WB=0, INV=0;
char *BUS;
struct processor p0, p1;

void state_print(struct processor p0, struct processor p1, char* bus){
	if(p0.state == 'I')
		printf("           I ----- ---- ----	");
	else
		printf("%s	%s	%c	%s	%d	%d	", p0.action, p0.addr, p0.state, p0.addr, p0.wrd1, p0.wrd2);
	printf("%s		", bus);
	if(p1.state == 'I')
		printf("I ----- ---- ----\n");
	else
		printf("%s	%s	%c	%s	%d	%d\n", p1.action, p1.addr, p1.state, p1.addr, p1.wrd1, p1.wrd2);

}

void process(struct processor active, struct processor snoop, char action, char addr[3], int proc){
	
	//cache hit
	if(strcmp(active.addr, addr) == 0){

		switch(active.state){
			case 'S':
				if(action == 'r'){
					active.action = "read";
					active.rhit++;
					active.state = 'S';
					BUS = "(none)";
				}
				else{
					active.action = "write";
					active.whit++;
					active.state = 'M';
					BUS = "INV";
				}
				break;
			case 'M':
				if(action == 'r'){
					active.action = "read";
					active.rhit++;
					active.state = 'M';
					BUS = "(none)";
				}
				else{
					active.action = "write";
					active.whit++;
					active.state = 'M';
					BUS = "(none)";
				}
				break;
		}
	}
	else{
		switch(active.state){
			case 'I':
				if(action == 'r'){
					active.action = "read";
					active.rmiss++;
					active.state = 'S';
					BUS = "READ";
				}
				else{
					active.action = "write";
					active.wmiss++;
					active.state = 'M';
					BUS = "RIM";
				}
				break;
			case 'S':
				if(action == 'r'){
					active.action = "read";
					active.rmiss++;
					active.state = 'S';
					BUS = "READ";
				}
				else{
					active.action = "write";
					active.wmiss++;
					active.state = 'M';
					BUS = "RIM";
				}
				break;
			case 'M':
				if(action == 'r'){
					active.action = "read";
					active.rmiss++;
					active.state = 'S';
					BUS = "READ";
					printf("                                WBr\n");
				}
				else{
					active.action = "write";
					active.wmiss++;
					active.state = 'M';
					BUS = "RIM";
					printf("                                WBr\n");
				}
				break;
		}

	}

	if(strcmp(snoop.addr, addr) == 0){
		switch(snoop.state){
			case 'S':
				switch(BUS[1]){
					case 'I':
						snoop.state = 'I';
						break;
					case 'N':
						snoop.state = 'I';
						break;
				}
				break;
			case 'M':
				switch(BUS[1]){
					case 'E':
						snoop.state = 'S';
						BUS = "RD/WB";
						break;
					case 'I':
						snoop.state = 'I';
						BUS = "RIM/WB";
						break;
				}
				break;
		}
	}

	if(proc == 0){
		p0 = active;
		p1 = snoop;
	}
	else{
		p1 = active;
		p0 = snoop;
	}

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
	

	p0.state = p1.state = 'I';
	p0.addr = p1.addr = "";
	p0.action = p1.action = "";
	p0.rhit = p0.whit = p1.rhit = p1.whit = p0.rmiss = p1.rmiss = p0.wmiss = p1.wmiss = 0;

	while(fgets(line, sizeof(line), fp)){
		//p0 selected
		if(line[0] == '0'){
			for(i=0; i<3; i++){
				addr[i] = line[i+2];
			}
			process(p0, p1, line[1], addr, 0);
		}
		//p1 selected
		else if(line[0] == '1'){
			for(i=0; i<3; i++){
				addr[i] = line[i+2];
			}
			process(p1, p0, line[1], addr, 1);
		}
		//end processing
	}

	

	printf("\nStats:\n");
	printf("  processor 0        processor 1        bus\n");
	printf("---------------    ---------------    --------\n");
	printf("read hits     %d    read hits     %d    READs  %d\n", p0.rhit, p1.rhit, READ);
	printf("read misses   %d    read misses   %d    RIMS   %d\n", p0.rmiss, p1.rmiss, RIM);
	printf("write hits    %d    write hits    %d    WBs    %d\n", p0.whit, p1.whit, WB);
	printf("write misses  %d    write misses  %d    INVs   %d\n", p0.wmiss, p1.wmiss, INV);
	printf("---------------    ---------------    --------\n");

	return 0;
}
