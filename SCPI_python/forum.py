import sys
import redpitaya_scpi as scpi
import matplotlib.pyplot as plot
import time
import datetime
tim=[]
meepo=[]
def RedPitaya_WritetoFile ():
	global meepo,rp_s, buffersize_pitaya, pointernow, pointerold, Log_Pitaya_file

	rp_s.tx_txt('ACQ:WPOS?') #ask for the actual pointer position
	pointerold = pointernow
	pointernow = int(rp_s.rx_txt())
	#print(str(pointerold))
	#print(str(pointernow))
	if pointernow > pointerold:
		nsamples = pointernow - pointerold
		rp_s.tx_txt('ACQ:SOUR1:DATA:STA:N? '+str(pointerold)+','+str(nsamples))
		buff_string = rp_s.rx_txt() #get data
		buff_string = buff_string.strip('{}\n\r').replace(" ", "").split(',')
		buff = list(map(float, buff_string)) #data in float format

		for item in buff:
			Log_Pitaya_file.write("%s\n" % item)
			meepo.append(item)
	else:
		nsamples1 = buffersize_pitaya - pointerold+1; #buffersize = 16384
		nsamples2 = pointernow; 
		rp_s.tx_txt('ACQ:SOUR1:DATA:STA:N? '+str(pointerold)+','+str(nsamples1))
		buff_string1 = rp_s.rx_txt() #get data
		rp_s.tx_txt('ACQ:SOUR1:DATA:STA:N? 0,' +str(nsamples2))
		buff_string2 = rp_s.rx_txt() #get data
		buff_string1 = buff_string1.strip('{}\n\r').replace(" ", "").split(',')
		buff1 = list(map(float, buff_string1)) #data in float format
		for item in buff1:
			Log_Pitaya_file.write("%s\n" % item)
			meepo.append(item)
		buff_string2 = buff_string2.strip('{}\n\r').replace(" ", "").split(',')
		buff2 = list(map(float, buff_string2)) #data in float format			
		for item in buff2:
			Log_Pitaya_file.write("%s\n" % item)
			meepo.append(item)

def RedPitaya_Connect ():
	global rp_s, samplingrate_pitaya, buffersize_pitaya, pointernow, pointerold, actual_time_pitaya, old_time_pitaya, decimation
	##OPEN CONNECTION TO RED PITAYA 1
	rp_s = scpi.scpi('148.122.56.1') 
	decimation = 8192
	buffersize_pitaya = 16384 #Buffersize [S]
	samplingrate_pitaya = 125e6/decimation #Sampling rate [S/s]
	rp_s.tx_txt('ACQ:RST') #reset aquire
	rp_s.tx_txt('ACQ:DEC ' + str(decimation)) #set the decimation value
	rp_s.tx_txt('ACQ:SOUR1:GAIN LV') #set voltage level according to jumpers (HV max 20V)
	rp_s.tx_txt('ACQ:SOUR2:GAIN LV') #set voltage level according to jumpers (HV max 20V)
	rp_s.tx_txt('ACQ:TRIG:LEV 0') #Trigger Level: 0 default = 0
	rp_s.tx_txt('ACQ:TRIG:DLY 8192') #Trigger Delay: 8192 Samples default = 0

	##Start the first acquisition
	rp_s.tx_txt('ACQ:START') #Starts acquisition
	rp_s.tx_txt('ACQ:TRIG DISABLED') #disabled --> continuous sampling
	rp_s.tx_txt('ACQ:WPOS?') #ask for the actual pointer position
	actual_time_pitaya = int(round(time.time() * 1000)) #in ms
	old_time_pitaya = actual_time_pitaya
	pointernow = int(rp_s.rx_txt())

def RedPitaya_StartLogging ():
	global Log_Pitaya, Log_Pitaya_file, rp_s, samplingrate_pitaya, buffersize_pitaya, pointernow, pointerold, actual_time_pitaya, old_time_pitaya
	Log_Pitaya = 1
	##########Red pitaya start logging
	RedPitaya_Connect () #CONNECTS TO THE PITAYAS AND OPENS A STREAM

	actual_time = time.strftime("%Y%m%d", time.gmtime())
	tmp_time = datetime.datetime.time(datetime.datetime.now()).strftime('%H_%M_%S')
	actual_time = actual_time + "_" + tmp_time

	Log_Pitaya_file = open("meepo" + actual_time + ".txt","w+")
	Log_Pitaya_file.write("Pitaya Log File from %s\n" % actual_time) #header1
	Log_Pitaya_file.write("Samplingfrequency: %s [S/s]\n" % samplingrate_pitaya) #header2
	Log_Pitaya_file.write("Ch1_1\tCh2_1\tCh1_2\tCh2_2\n") #header3

	print ("Start RedPitaya Logging: " + str(actual_time))

def RedPitaya_StopLogging ():
	global Log_Pitaya_file, rp_s, Log_Pitaya,meepo, decimation
	Log_Pitaya = 0
	Log_Pitaya_file.close() #close logfile stream
	rp_s.tx_txt('ACQ:STOP') #Stops acquisition
	for item in range(len(meepo)):
		tim.append((float(item)/125000000)*decimation)
	plot.plot(tim,meepo)
	plot.ylabel('Voltage')
	plot.show()
	print ("Stop RedPitaya Logging!")
RedPitaya_StartLogging ()
while(1):
	RedPitaya_WritetoFile ()
	if len(meepo)>10000:
		break
print(str(len(meepo)))
strbuff=str(meepo)[1:len(str(meepo[0:16384]))-1]
strbuff.strip('{}\n\r').replace(" ","").split(',')
RedPitaya_StopLogging ()
rp_s.tx_txt('GEN:RST')
time.sleep(1)
rp_s.tx_txt("SOUR1:FUNC ARBITRARY")	
rp_s.tx_txt("SOUR1:TRAC:DATA:DATA "+strbuff)
rp_s.tx_txt("SOUR1:FREQ:FIX "+str(7632/decimation))	
rp_s.tx_txt("OUTPUT1:STATE ON") 
rp_s.tx_txt("SOUR1:BURS:NCYC 1")
rp_s.tx_txt("SOUR1:BURS:NOR 0")
rp_s.tx_txt("SOUR1:BURS:INT:PER 0")			 

