import struct

import numpy as np
import numpy.fft
import matplotlib.pyplot as plt

def read_raw_audio(filename):
    with open(filename, "rb") as f:
        data = f.read()
        sample_read = int(len(data) / 2)
        samples = np.array([struct.unpack("<h", data[2*i:2*i+2])[0] for i in range(sample_read)], dtype='int16')
        return samples

def write_raw_audio(filename, samples):
    # return number of samples written
    count = 0
    with open(filename, "wb") as f:
        for x in samples:
            f.write(struct.pack("<h", x))
            count += 1
    return count

def get_freqs(n, fsps):
    if n % 2 == 0:
        return np.linspace(-n / 2, n / 2 - 1, n) / n * fsps
    else:
        return np.linspace(-n / 2, n / 2, n) / n * fsps

def get_times(n, fsps):
    return np.linspace(0, n - 1, n) / fsps

def plot_spectrum(signal, fsps=None, **kwargs):
    spectrum = np.abs(np.fft.fftshift(np.fft.fft(signal)))
    fsps = len(signal) if fsps is None else fsps
    freqs = get_freqs(len(signal), fsps)
    
    plt.figure()
    plt.plot(freqs, spectrum)
    plt.show(**kwargs)
