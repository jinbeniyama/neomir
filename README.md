# Thermal modeling for NEOMIR
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[developer mail](mailto:beniyama@oca.eu)

## Overview
Codes for thermal modeling of minor bodies in preparation for NEOMIR.

## Data (in /data)
* sph32.obj (spheprical shape model used in the paper)
* position.txt (positions of original objects observed by NEOMIR)

## TPM (hit the commands in .)
```
# Make observations and ephemerides files for original objects
python src/make_NEOMIR_obseph.py --pos data/position.txt --outobs data/obsfile_original --outeph data/ephemfile_original
# Make observations and ephemerides files for control objects
python src/make_NEOMIR_obseph.py --pos data/position.txt --outobs data/obsfile_control --outeph data/ephemfile_control --pseudo

# Do TPM for original objects
python src/runtpm_NEOMIR.py --obs data/obsfile_original/* --eph data/ephemfile_original/* --obj data/sph32.obj --outdir data/tpmout_original
# Do TPM for control objects
python src/runtpm_NEOMIR.py --obs data/obsfile_control/* --eph data/ephemfile_control/* --obj data/sph32.obj --outdir data/tpmout_control
```
Then all results are saved in `./data/tpmout_original` and `./data/tpmout_control`.


## Plotting figures in the paper (hit the commands in ./plot)
```
# Plot locations of original asteroids and control asteroids (Figure 1.)
python ../src/plot_NEOMIR_loc.py ../data/obsfile_original ../data/obsfile_control 
```

```
# Plot aspect data of original asteroids and control asteroids (Figure 2.)
python ../src/plot_NEOMIR_aspect.py ../data/obsfile_original ../data/obsfile_control 
```
