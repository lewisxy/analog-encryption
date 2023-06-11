import math
import secrets
import time

from typing import Callable, Any

import numpy as np
import numpy.fft
import matplotlib.pyplot as plt
import sounddevice as sd

import utils
import permutations

def complex_from_polar(magnitude: np.ndarray, angle: np.ndarray):
    """create a complex array from magnitude and angle"""
    return magnitude * np.exp(1j * angle)

# size of each frame
block_size = 1024

fsps = 8000 # audio sample frequency
freq = np.linspace(-block_size / 2, block_size / 2 - 1, block_size) / block_size * fsps
usable_freq = np.logical_and(np.abs(freq) > 300, np.abs(freq) < 3400)
permutation_size = int(np.sum(usable_freq) / 2)
print(permutation_size)

usable_freq_shifted = np.fft.ifftshift(usable_freq)
# masks to perform permutations
permutation_mask = np.fft.ifftshift(np.logical_and(usable_freq, freq > 0))
reverse_permutation_mask = np.fft.ifftshift(np.logical_and(usable_freq, freq < 0))

# plt.figure()
# plt.plot(freq, permutation_mask, 'r', label="permutation mask")
# plt.plot(freq, reverse_permutation_mask, 'b', label="permutation mask (reversed)")
# plt.legend()
# plt.xlabel("Frequency (Hz)")
# plt.show()

# read PCM audio samples from file
samples = utils.read_raw_audio("sample_8000hz.raw")

# setup audio output
audio_out = sd.OutputStream(samplerate=fsps, channels=1, dtype='int16')
audio_out.start()

idx = 0
while True:
    data = samples[idx:idx+block_size].astype("float")
    if len(data) < block_size:
        break

    spectrum = np.fft.fft(data)
    p = permutations.random_permutation(secrets.token_bytes, permutation_size)

    # direct permutation
    spectrum[permutation_mask] = spectrum[permutation_mask][p]
    spectrum[reverse_permutation_mask] = spectrum[reverse_permutation_mask][::-1][p][::-1]

    # permutate phase only
    # angles = np.angle(spectrum[permutation_mask])[p]
    # spectrum[permutation_mask] = complex_from_polar(np.absolute(spectrum[permutation_mask]), angles)
    # angles = np.angle(spectrum[reverse_permutation_mask][::-1])[p][::-1]
    # spectrum[reverse_permutation_mask] = complex_from_polar(np.absolute(spectrum[reverse_permutation_mask]), angles)

    # permute magnitude only
    # mag = np.absolute(spectrum[permutation_mask])[p]
    # spectrum[permutation_mask] = complex_from_polar(mag, np.angle(spectrum[permutation_mask]))
    # mag = np.absolute(spectrum[reverse_permutation_mask][::-1])[p][::-1]
    # spectrum[reverse_permutation_mask] = complex_from_polar(mag, np.angle(spectrum[reverse_permutation_mask]))

    enc_data = np.real(np.fft.ifft(spectrum))

    write_available = audio_out.write_available
    audio_out.write(enc_data[:write_available].astype('int16'))
    # audio_out.write(data.astype('int16'))
    time.sleep(block_size / fsps)

    idx += block_size

audio_out.stop()