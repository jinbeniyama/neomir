#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os

Gamma_values = [0, 50, 150, 300, 500, 1000]
mycolor = [
    "#AD002D", "#1e50a2", "#69821b", "#f055f0", "#afafb0", "#0095b9",
    "#89c3eb", "#ec6800", "cyan", "gold", "magenta"]


def handle_tpmres(resdir, key_flux):
    filenames = [f.name for f in os.scandir(resdir)]
    df_list = []
    for idx_obj, fi in enumerate(filenames):
        filename = os.path.join(resdir, fi)
        # Extract TI from TI300_res_141.txt
        TI = int(fi.split("_")[0][2:])
        df = pd.read_csv(filename, sep=" ")

        lon = df["lam"]
        lat = df["beta"]
        flux = df[key_flux]

        # These are common
        x1, y1, z1 = df["x1"], df["y1"], df["z1"]
        x2, y2, z2 = df["x2"], df["y2"], df["z2"]

        # Since we used asteroids with diameters of 1 km in TPM to avoid the loss of digits,
        # we have to slace fluxes here.
        # From 1 km to 42 m (H=25, pv=0.1)
        sf = (42./1000.)**2

        df = pd.DataFrame(dict(
            lon=lon, lat=lat, flux=flux,
            X=x1, Y=y1, Z=z1, MirX=x2, MirY=y2, MirZ=z2
            ))
        df["TI"] = TI
        df["objid"] = idx_obj
        df_list.append(df)
    df = pd.concat(df_list)
    return df


def calc_aspect(df):
    """
    Calculate alpha, delta, and r.

    Parameter
    ---------
    df : pandas.DataFrame
        input dataframe

    Return
    ------
    df : pandas.DataFrame
        output dataframe
    """
    S = np.array([df['X'].values, df['Y'].values, df['Z'].values]).T
    normaS = np.sqrt(np.sum(S**2, axis=1))
    O = np.array([df['MirX'].values, df['MirY'].values, df['MirZ'].values]).T
    normaO = np.sqrt(np.sum(O**2, axis=1))
    SO = S*O
    pha = np.arccos(np.sum(SO, axis=1)/normaO/normaS)*180/np.pi
   
    df["r"] = normaS
    df["delta"] = normaO
    df["alpha"] = pha
    return df
