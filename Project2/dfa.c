#include <stdio.h>

int main(int argc, char *argv[]){
	
	bool rename = false;
	int delay = 0;

	//open argc - 1
	FILE *fp;


	//get command line flags
	int f;
	while((f = getopt(argc, argv, "rl:")) != -1){
		switch(f){
			case 'r': rename = true;
						 break;
			case 'l': delay = atoi(optarg);
						 break;
			default:
						 break;
		}
	}


	return 0;
}
