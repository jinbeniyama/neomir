# Thermal modeling for NEOMIR
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[developer mail](mailto:beniyama@oca.eu)

## Overview
Codes for thermal modeling of minor bodies in preparation for NEOMIR.

## Data (in /data)
* `sph32.obj` (spheprical shape model with a diameter of 1 km used in the paper)
* `position.txt` (positions of original objects observed by NEOMIR, in prep.)
* `spinfile` (directory with spin files, for both original and control objects)
* `tpmout_original` (directory with output of TPMs of original objects)
* `tpmout_control` (directory with output of TPMs of control objects)

## TPM (hit the commands in ./)
```
# Make observations and ephemerides files for original objects
python src/make_NEOMIR_obseph.py --pos data/position.txt --outobs data/obsfile_original --outeph data/ephemfile_original
# Make observations and ephemerides files for control objects
python src/make_NEOMIR_obseph.py --pos data/position.txt --outobs data/obsfile_control --outeph data/ephemfile_control --pseudo

# Do TPM for original objects
python src/runtpm_NEOMIR.py --obs data/obsfile_original/* --eph data/ephemfile_original/* --obj data/sph32.obj --outdir data/tpmout_original --spindir data/spinfile
# Do TPM for control objects
python src/runtpm_NEOMIR.py --obs data/obsfile_control/* --eph data/ephemfile_control/* --obj data/sph32.obj --outdir data/tpmout_control --spindir data/spinfile
```
Then all results are saved in `./data/tpmout_original` and `./data/tpmout_control`.
I note that spinfiles are identical for original and control objects since the random seeds are specified in the code.


## Plotting figures in the paper (hit the commands in ./, figures are saved in ./fig)
```
# Plot locations of original asteroids and control asteroids (Figure 1.)
python src/plot_objectslocation.py data/obsfile_original data/obsfile_control 
```

```
# Plot aspect data of original asteroids and control asteroids (Figure 2.)
python src/plot_aspect.py data/obsfile_original data/obsfile_control 
```

```
# Plot results
# Plot first one (original, Figure 4.)
python src/plot_8flux_map.py --resdir data/tpmout_original --out obj1_flux_original.png --outdir fig --idx_obj 1 --vmin 20 --vmax 400
# Plot first one (pseudo, Figure 5.)
python src/plot_8flux_map.py --resdir data/tpmout_control  --out obj1_flux_control.png --outdir fig --idx_obj 1 --vmin 20 --vmax 400
# You can plot all at once with `--all` option (148 objects x 6 TI = 888 files)
```


## Miscellaneous
```
# Check spin pole distributions of our samples
# Check flux, prograde, retrograde, TI
plot_tpmres_stat.py --resdir1 tpmresult_2bands --resdir2 tpmresult_2bands_pseudo --outdir plot 
```
