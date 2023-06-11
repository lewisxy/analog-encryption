# analog-encryption

- `direct_encrypt.py` and `direct_encrypt.ipynb` contains experiments of directly encrypting analog signals.

- `packet.py` contains a implmentation of encrypted packet format.

- `digital_processing.py` contains experiments of recording and encoding audio using SILK library.

Other files dependencies.

SILK library is from: https://github.com/ploverlake/silk

Small tweaks are needed to build SILK shared library for python to use (by default it only builds static library).
Prebuilt MacOS (arm64) library is provided here. If you would like to build it for other platforms, please let me know.

