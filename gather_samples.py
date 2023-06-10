import time
import numpy as np
import copy as copy
from rtlsdr import RtlSdr

fsps = 1000*256

fc = 1.42e9

dt = 1.0/fsps

nyquist = fsps/2.0

N = 2560

print("N: ", N)

try:
    sdr.close()
    print("closed old sdr")
except NameError:
    print("could not find sdr")

sdr = RtlSdr()

sdr.sample_rate = fsps
sdr.center_freq = fc

sdr.gain = 42.0

print("sample rate: ", fsps)
print("center frequency: ", fc)

#avg_pow_arr = np.zeros(100)

filename = 't4-1bit/Low-avg_pow_samps-1bit'
gathered_pow_arr = np.zeros(100)

for j in range (0, 100):
    avg_pow_arr = np.zeros(500)
    tot_pow = 0
    #filename = 't2-1bit/1.' + str(j) + '-Low-avg_pow_samps-1bit'

    for i in range (0, 500):
        samples = ((np.zeros((N))+1j)-1j)
        samples = sdr.read_samples(N)
        avg_pow = np.real(samples.dot(samples.conj()))
        avg_pow_arr[i] = avg_pow
        tot_pow += avg_pow
    #print("avg pow: ", avg_pow_arr)
    gathered_pow_arr[j] = tot_pow
np.savetxt(filename, gathered_pow_arr)

