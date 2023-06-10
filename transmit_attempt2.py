import time
from datetime import date
import numpy as  np
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
from copy import copy
from rtlsdr import RtlSdr 
np.set_printoptions(precision=2)

# Configure GPIO board
GPIO.setmode(GPIO.BCM)
pwrPin = 17
GPIO.setup(pwrPin, GPIO.IN, pull_up_down=PUD_DOWN)

# Making samples per sec a multiple of 256 
fsps = 1000*256# = about 2560 sps

# frequency 1.42 GHz
fc = 1.42e9

# specify sampling frequency
dt = 1.0/fsps # time step size between samples
nyquist = fsps /2.0

# Cna change time for gathering samples
#Tmax = 10.0
Tmax = 5.0
#Tmax = 2.5
#Tmax = 1.0

# Number of samples to gather during time frame
N = 2560 # N must be a multiple of 256

print("The number of samples to collect, N= ",N)

try:
    sdr.close()
    print("closed old sdr")
except NameError:
    print("Could not find SDR")

sdr = RtlSdr()

sdr.sample_rate = fsps 
sdr.center_freq = 1.42e9

# sdr.gain = 'auto'
sdr.gain = 42.0 # This is max on rtl_sdr v4, according to sdr.valid_gains_db

print("Sample Rate     : ", sdr.sample_rate)
print("Center frequency: ", sdr.center_freq)

# x = samples 
tot_power = 0

func_gen_fc = 0.5 # frequency on the function gen (0.1 Hz means that the square wave will be ten seconds)

#   |-----|     |
#   |     |     |
#   |     |-----|

#   5 sec  5 sec

n = Tmax/(1/func_gen_fc)
print("# of periods we want to capture: ", n)

#pow_arr = np.zeros(shape=((round(n*2)), samps))
idx = 0

samps = round(N/(n*2))
print("# of samples gathered per transition: ", samps)

sleep_time = (1/func_gen_fc)/2

# time it takes to gather samples
sampling_window = N/fsps

# calculate offset for when to start the sdr reading during each state
first_offset = (sleep_time - sampling_window)/2

print("Thread will sleep for : ", sleep_count)

#power array with dimensions of n transitions and sample's read per transition
raw_pow_arr = np.zeros(((round(n*2)), samps), dtype=np.complex_)


# n will correspond to number of periods generated for the time frame for gathering samples

offset = first_offset

for i in range(0, round(n)):
    GPIO.wait_for_edge(pwrPin, GPIO.RISING, timeout=10000)

    # waiting for high state
    time.sleep(first_offset)
    samples = ((np.zeros((samps))+1j)-1j)
    samples = sdr.read_samples(samps) # Collect N samples on the sdr
    raw_pow_arr[idx] = samples
    idx = idx + 1

    # waiting for low state
    time.sleep(sleep_time)
    
    samples = ((np.zeros((samps))+1j)-1j)
    samples = sdr.read_samples(samps) # Collect N samples on the sdr
    raw_pow_arr[idx] = samples
    idx = idx + 1
        
# Compute average power per sample after all samples are read
avg_hi_pow_arr = np.zeros(round(n))
avg_lo_pow_arr = np.zeros(round(n))


idx = 0
for j in range(0, round(n)):
    samples = raw_pow_arr[idx]
    pow_hi = np.real(samples.dot(samples.conj()))
    avg_hi_pow_arr[j] = pow_hi
    idx = idx + 1
    samples = raw_pow_arr[idx]
    pow_lo = np.real(samples.dot(samples.conj()))
    avg_lo_pow_arr[j] = pow_lo
    idx = idx + 1
    tot_power += pow_hi - pow_lo

print("Average power: ", avg_hi_pow_arr)
print("low: ", avg_lo_pow_arr)
print("tot pow: ", tot_power)
np.savetxt('6-1-23-transmit-1hz-avg-pow', avg_pow_arr)
np.savetxt('6-1-23-transmit-1hz-raw-samples', raw_pow_arr)

