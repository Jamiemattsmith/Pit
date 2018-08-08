#!/usr/bin/python

import sys
import redpitaya_scpi as scpi
import matplotlib.pyplot as plot
import time
rp_s = scpi.scpi("148.122.56.1")                                                 
buff_string=""
dec=1.00000000
freq=7632.0
while(1):
	mode=input("Select mode")
	if mode=="acq":
		x=[]
		rp_s.tx_txt("ACQ:DEC "+str(int(dec)))
		rp_s.tx_txt('ACQ:START')
		rp_s.tx_txt("ACQ:TRIG:DLY 16384")
		rp_s.tx_txt('ACQ:TRIG NOW')                                               
		while 1:
			rp_s.tx_txt('ACQ:TRIG:STAT?')
			if rp_s.rx_txt() == 'TD':
				break
		rp_s.tx_txt('ACQ:SOUR1:DATA?') 		
		buff_string=rp_s.rx_txt()
		rp_s.tx_txt('ACQ:WPOS?')
		print(rp_s.rx_txt())		
		buff_string = buff_string.strip('{}\n\r').replace(" ","").split(',')          
		buff = list(map(float, buff_string))
		err=0
		for item in buff:
			if item>1 or item<-1:
				err=1
		for item in range(len(buff)):
			b=((item/125)*dec)
			x.append(b)
		strbuff=str(buff)
		strbuff=str(buff)[1:len(str(buff))-1]
		strbuff.strip('{}\n\r').replace(" ","").split(',')						
		plot.plot(x,buff)                                                                
		plot.ylabel('Voltage')
		plot.xlabel('Time (us)')
		plot.show()
		if err==1:
			print("ERR: Data sample exceeds amplitude range!!!")
	elif mode=="dec":
		dec=float(input())
		rp_s.tx_txt("ACQ:DEC "+str(int(dec)))
	elif mode=="freq":
		freq=float(input())
	else:
		rp_s.tx_txt('GEN:RST')		
		rp_s.tx_txt("SOUR1:FUNC ARBITRARY")
		rp_s.tx_txt("SOUR1:FREQ:FIX "+str(7632/dec))     
		rp_s.tx_txt("SOUR1:BURS:NCYC 1")
		rp_s.tx_txt("SOUR1:BURS:NOR 0")			
		rp_s.tx_txt("SOUR1:TRAC:DATA:DATA "+strbuff) 
		time.sleep(2)
		rp_s.tx_txt("OUTPUT1:STATE ON")