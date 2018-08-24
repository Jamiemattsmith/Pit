#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include "redpitaya/rp.h"
#define M_PI 3.14159265358979323846

int main(int argc, char **argv){
	int len=0;
	int c;
	char cmnd[20];
	int i;
	int n;
	int cnt=0;
	uint32_t posnow = 0;
	uint32_t posold =0;
	float zeros[16384]={0.0};
	/* Print error, if rp_Init() function failed */
	if(rp_Init() != RP_OK){
		fprintf(stderr, "Rp api init failed!\n");
	}

	
	FILE *f = fopen("data.txt", "r");
	if (f == NULL)
	{
    		printf("Error opening file!\n");//Opens data file if it exists
    		exit(1);
	}
	printf("Counting Data for Memory Allocation\n");//counts data so the appropriate 
	for (c=getc(f);c!= EOF; c= getc(f)){            //amount of memory can be allocated
		if (c=='\n'){
			len++;
		}
	}
	printf("Counted Data: %d\n",len);
	rewind(f);
	float *half = (float *)malloc((len+16384) * sizeof(float));;//Memory allocated
	printf("Allocated Memory\nCollecting Data from SD Card\n");
	for (i=0; i<len; i++){
		fscanf(f,"%f\n",&half[i]);//Data placed in RAM for faster access
	}
	for (i=0; i<16384; i++){
		half[len+i]=0.0;//16384 zeros placed on end to clear output buffer after generation
	}
	len=len+16384;	
	printf("Collected Data\n");
	rp_GenWaveform(RP_CH_1, RP_WAVEFORM_DC);
	rp_GenMode(RP_CH_1, RP_GEN_MODE_CONTINUOUS);
	rp_GenAmp(RP_CH_1, 1.0);

	rp_GenFreq(RP_CH_1, 119);
	rp_updateData(RP_CH_1, zeros, 0,16384);
	rp_GenOutEnable(RP_CH_1);
	rp_GenOutEnable(RP_CH_2);
	while(1){
		printf("Enter Command: ");
		scanf("%s",cmnd);
		if(!strcmp(cmnd,"exit")){break;}
		if(!strcmp(cmnd,"generate")){
			printf("Commencing Generation\n");
			cnt=0;
			rp_GetReadPointer(&posnow);		
			while(1){
				posold=posnow;//"old pointer" set to previous "new pointer"
				rp_GetReadPointer(&posnow);//new pointer set to current read pointer location
				n=posnow-posold;
				n=n>0? n:16384+n;
				if (cnt !=len){
					if (cnt+n>=len){
						n=len-cnt;
						rp_updateData(RP_CH_1, half+cnt, posold,n);//Data that has been read is replaced with future data
						break;                                     //so that when the read pointer returns to the location, 
					}                                                  //new data is being outputted, not the sam point as before
					rp_updateData(RP_CH_1, half+cnt, posold,n);
					cnt = cnt+n;
				}
			}
		}
		else{printf("Command Not Valid\n");}
	}
	free(half);//releases resources
	rp_Release();
	fclose(f);
}
