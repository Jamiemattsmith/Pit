/* Red Pitaya C API example Acquiring a signal from a buffer  
 * This application acquires a signal on a specific channel */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "redpitaya/rp.h"

int main(int argc, char **argv){
	int NSMP;
	float time;
	printf("Enter Time to Sample for:\n");//Time Input in seconds
	scanf("%f",&time);
	NSMP=(int)(time*1953150);//Samples calculated assuming decimation of 64
        /* Print error, if rp_Init() function failed */
        if(rp_Init() != RP_OK){
                fprintf(stderr, "Rp api init failed!\n");
        }
	
	FILE *f = fopen("data.txt", "w");//Data file name defined, maybe could be user input
	if (f == NULL)
	{
    		printf("Error opening file!\n");//Test for error opening file
    		exit(1);
	}
	
	//node* head = NULL;
	float *dat = (float*)malloc(NSMP * sizeof(float));
	if(dat == NULL)
    	{
        	printf("A tad too much data perhaps\n");//Tests if enough memory is available and
        	exit(0);//                                Stops program if there isn't
    	}
	int cnt = 0;
	uint32_t posnow = 0;
	uint32_t posold = 0;
        uint32_t buff_size = 16384;
        float *buff = (float *)malloc(buff_size * sizeof(float));
	if(buff == NULL)
    	{
        	printf("A tad too much data perhaps\n");//Tests if enough memory is available
		free(dat);
        	exit(0);
    	}	
	float freq=0;
        rp_AcqReset();
	rp_AcqSetArmKeep(true);//Lets buffer be continually updated
        rp_AcqSetDecimation(RP_DEC_64);//Sets decimation factor
	uint32_t decfac;
	rp_AcqGetDecimationFactor(&decfac);
	printf("Decimation Factor: %d\n",decfac);//prints decimation factor	
        rp_AcqSetTriggerLevel(RP_CH_1, 0);
        rp_AcqSetTriggerDelay(0);
	printf("Allocated Memory\n");

        rp_AcqStart();
	sleep(1);
        rp_AcqSetTriggerSrc(RP_TRIG_SRC_DISABLED);
	printf("Started Acquisition\n");
	rp_AcqGetWritePointer(&posnow);
	int i;
	while(1){
		buff_size=16384;
		posold=posnow;//old pointer is set to previous new pointer
		rp_AcqGetWritePointer(&posnow);//new pointer set to current position
             
        	rp_AcqGetDataPosV(RP_CH_1,posold,posnow, buff, &buff_size);//data between pointers is obtained and placed in buff array
        	for(i = 1; i != buff_size; i++){
			if(cnt!=NSMP){
				dat[cnt]=buff[i];//data stored in ram (buff array data appended to dat array)
				cnt++;
			}
        	}
		if(cnt==NSMP){break;}
	}
	printf("Saving Data to SD card\n");
	for(i = NSMP; i !=0; i--){
		fprintf(f,"%f\n",(dat[NSMP-i]*1.0275));//Saved to SD card +amplitude scaling (if necessary)
	}
	rp_AcqGetSamplingRateHz(&freq);
	printf("Smp Freq = %f\n",freq);
        /* Releasing resources */
        free(buff);
	free(dat);
        rp_Release();
        return 0;
}
        
