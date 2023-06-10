import time
from datetime import date
import numpy as  np
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
from copy import copy
from rtlsdr import RtlSdr 
np.set_printoptions(precision=2)
#import threading

# Configure GPIO board
GPIO.setmode(GPIO.BCM)
pwrPin = 17
GPIO.setup(pwrPin, GPIO.IN)

# Making samples per sec a multiple of 256 
fsps = 1000*256 # = about 256000 sps

# frequency 1.42 GHz
fc = 1.42e9

# specify sampling frequency
dt = 1.0/fsps # time step size between samples
nyquist = fsps /2.0

# Cna change time for gathering samples
Tmax = 10.0
#Tmax = 5.0
#Tmax = 2.5
#Tmax = 1.0

# Number of samples to gather during time frame
N = round(fsps*Tmax) # N must be a multiple of 256

print("The number of samples to collect, N= ",N)

try:
    sdr.close()
    print("closed old sdr")
except NameError:
    print("could not find sdr")

#sdr = RtlSdr()

# sdr.sample_rate = fsps 
# sdr.center_freq = fc

# sdr.gain = 'auto'
# sdr.gain = 42.0 # This is max on rtl_sdr v4, according to sdr.valid_gains_db

# print("Sample Rate     : ", sdr.sample_rate)
# print("Center frequency: ", sdr.center_freq)

tot_power = 0

func_gen_fc = 0.5 # frequency on the function gen (0.1 Hz means that the square wave will be ten seconds)

#   |-----|     |
#   |     |     |
#   |     |-----|

#   5 sec  5 sec

n = Tmax/(1/func_gen_fc)

# Create an arr of zeros that will be populated with power vals
pow_arr = np.zeros(round(n*2))
idx = 0
print("# of periods transitions we want to capture: ", n)

samps_per_transition = round(N/(n*2))
print("# of samples gathered per transition: ", samps_per_transition)

sleep_count = (1/func_gen_fc)/2

print("Thread will sleep for :", sleep_count)

event = GPIO.wait_for_edge(pwrPin, GPIO.RISING, timeout=10000)

# n will correspond to number of square waves generated for the time frame for gathering samples
for i in range(0, round(n)):
    capture = 0
    while GPIO.input(17):
        print("h")
        
        if not capture:
            
            pow_arr[idx] = 1
            idx = idx + 1
            capture = 1
            time.sleep(sleep_count)
        
    capture = 0    
    while not GPIO.input(17):
        print("l")
        if not capture:
            
            pow_arr[idx] = 0
            idx = idx + 1
            capture = 1
            time.sleep(sleep_count)

print("Final results for function generator at ", func_gen_fc, " Hz", ": ")
print(pow_arr)
np.savetxt("100hz_verify_transition-capture", pow_arr)
