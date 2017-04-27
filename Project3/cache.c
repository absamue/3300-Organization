#include <stdio.h>
#include <string.h>
#include <stdlib.h>

struct processor{
	char addr[3], *action, paddr[3]; //addr in cache | read/write | addr for printing
	int rhit, whit, rmiss, wmiss, wrd1, wrd2; //read/write hit/miss | values in cache line
	char state, prev_state; //modified/shared/invalid
	int active; //is this the processor we are using
};

int mem[512]; //512 words
int READ=0, RIM=0, WB=0, INV=0; //count of bus actions
char *BUS;	//bus state
struct processor *p0, *p1;

void state_print(struct processor *p0, struct processor *p1, char* bus){
	
	//print info for p0
	if(p0->state == 'I')
		printf("           I ----- ---- ----	");
	else if(p0->active == 1){
		printf("%-5s %s  %c   %s    %d    %d    ", p0->action, p0->paddr, p0->state, p0->addr, p0->wrd1, p0->wrd2);
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
		printf("	  %-5s %s  %c   %s    %d    %d\n", p1->action, p1->paddr, p1->state, p1->addr, p1->wrd1, p1->wrd2);
	}
	else{
		printf("		     %c   %s    %d    %d\n", p1->state, p1->addr, p1->wrd1, p1->wrd2);
	}
}

int hextoint(char addr[3]){
	return (int)strtol(addr, NULL, 16);
}

/* This colossal mess of a function implements the MSI cache
 * state-transition represented by the following:
 *
 * Active processor:
 *  cache hit, current state, action  |  new state / bus action
  ----------------------------------+--------------------------
     miss          I         read   |     S       READ
     miss          I         write  |     M       RIM
     miss          S         read   |     S       READ
     miss          S         write  |     M       RIM
     miss          M         read   |     S       WBr then READ
     miss          M         write  |     M       WBr then RIM
     hit           S         read   |     S       (none)
     hit           S         write  |     M       INV
     hit           M         read   |     M       (none)
     hit           M         write  |     M       (none)

	  Snooping Processor:
	  address, current state, bus action  |  new state /  revised
   match                              |              bus action
  ------------------------------------+------------------------
    no           x           x        | no change
    yes          S           READ     |     S
    yes          S           RIM      |     I
    yes          S           INV      |     I
    yes          M           READ     |     S          RD/WB
    yes          M           RIM      |     I          RIM/WB
*/
void process(char action, char addr[3], int proc){
	struct processor *active;
	struct processor *snoop;

	//determine active processor
	if(proc == 0){
		active = p0;
		snoop = p1;
	}
	else{
		active = p1;
		snoop = p0;
	}


	//check for a cache hit
	int hit, i;
	int loc = hextoint(addr);
	int memloc = loc/4; //referenced memory index
	int cur = hextoint(active->addr);
	//referencing word2
	if(memloc%2){
		if(loc-4 == cur)
			hit = 1;
		else
			hit = 0;
	}
	//referencing word1
	else{
		if(loc == cur)
			hit = 1;
		else
			hit = 0;
	}


	//cache hit
	//the following if-else follows the same structure as documented in the
	//first case throughout
	if(hit){
		switch(active->state){
			case 'S':
				if(action == 'r'){
					//set acion
					active->action = "read";
					//increase miss/hit count
					active->rhit++;
					//change state according to table
					active->state = 'S';
					//set bus according to table
					BUS = "(none)";
				}
				else{
					active->action = "write";
					active->whit++;
					active->state = 'M';
					BUS = "INV";
					mem[memloc]++;
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
					mem[memloc]++;
				}
				break;
			default:
				break;
		}
	}
	//cache miss
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
					mem[memloc]++;
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
					mem[memloc]++;
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
					mem[memloc]++;
				}
				break;
			default:
				printf("miss default\n");
				break;

		}
	}

	//update cache line values based on which one was referenced
	if(memloc%2){
		active->wrd2 = mem[memloc];
		active->wrd1 = mem[memloc-1];
	}
	else{
		active->wrd2 = mem[memloc+1];
		active->wrd1 = mem[memloc];
	}


	cur = hextoint(snoop->addr);
	//referencing word2
	if(memloc%2){
		if(loc-4 == cur)
			hit = 1;
		else
			hit = 0;
	}
	//referencing word1
	else{
		if(loc == cur)
			hit = 1;
		else
			hit = 0;
	}
	//check snooping cache
	if(hit){
		switch(snoop->state){
			case 'S':
				switch(BUS[1]){
					case 'I':
						snoop->prev_state = 'S';
						snoop->state = 'I';
						for(i=0;i<3;i++)
							snoop->addr[i] = 'f';

						break;
					case 'N':
						snoop->prev_state = 'S';
						snoop->state = 'I';
						for(i=0;i<3;i++)
							snoop->addr[i] = 'f';
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
						for(i=0;i<3;i++)
							snoop->addr[i] = 'f';
						BUS = "RIM/WB";
						break;
				}
				break;
		}
	}


	//set the cache's current line value in addr
	if(active->state != 'I'){
		if(memloc%2){
			sprintf(active->addr, "%x", loc-4);	
		}
		else{
			strcpy(active->addr, addr);
		}
		strcpy(active->paddr, addr);
	}

	//set the pointer back to the global varible for each processor
	//depending on which was active/snooping
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

	//increase the counters for the appropriate bus action
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

	//print details
	state_print(p0, p1, BUS);
}


int main(int argc, char *argv[]){

	printf("        processor 0              bus               processor 1\n");
	printf("----------------------------    ------    ----------------------------\n");
	printf("  action     cache contents     action      action     cache contents\n");
	printf("             addr  wrd0 wrd1                           addr  wrd0 wrd1\n");
	printf("           I ----- ---- ----                         I ----- ---- ----\n");



	char line[6];
	char addr[3];
	int i;
	
	p0 = malloc(sizeof(struct processor));
	p1 = malloc(sizeof(struct processor));

	//set default values
	p0->state = p1->state = 'I';
	p0->prev_state = p1->prev_state = 'I';
	p0->action = p1->action = "";
	p0->rhit = p0->whit = p1->rhit = p1->whit = p0->rmiss = p1->rmiss = p0->wmiss = p1->wmiss = 0;
	p0->active = p1->active = 0;
	for(i=0; i<3; i++){
		p0->addr[i] = 'f';
		p1->addr[i] = 'f';
	}
	BUS = "temp";

	while(scanf("%s", &line) == 1){
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

	
	//print cache hit/miss counts and bus action information
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
