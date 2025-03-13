#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate diameter with NEATM.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess, os
from argparse import ArgumentParser as ap


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


if __name__ == "__main__":
    parser = ap(description="Plot TPM results for NEOMIR.")
    parser.add_argument(
        "--idx_obj", type=int, nargs="*", default=[1],
        help="Index of objects to be plotted")
    parser.add_argument(
        "--all", action="store_true", default=False,
        help="Try to plot all resuls")
    parser.add_argument(
        "--key_flux", type=str, default="flux8",
        help="Key used to calculate diameter")
    parser.add_argument(
        "--resdir", type=str, default="tpmresult",
        help="Directory with output files")
    parser.add_argument(
        "--eta", type=float, default=1.0,
        help="beaming parameter")
    parser.add_argument(
        "--out", type=str, default="NEATM_res.txt",
        help="Output filename")
    parser.add_argument(
        "--outdir", type=str, default="data",
        help="Directory for output file")
    args = parser.parse_args()

    resdir = args.resdir
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    Gamma_values = [0, 50, 150, 300, 500, 1000]
    key_flux = args.key_flux
    
    if args.all:
        # Try to find object id
        filenames = [f.name for f in os.scandir(resdir)]
        # Extract object id from TI150_res_012.txta
        filenames_part = [f.split("_")[-1] for f in filenames]
        idx_plot = [int(f.split(".")[0]) for f in filenames_part]
        idx_plot = list(set(idx_plot))
    else:
        idx_plot = args.idx_obj

    # Read lam, beta, flux, TI, objid
    df_list = []
    for idx_obj in idx_plot:
        print(f"READ results of OBJ{idx_obj:03d}")
        
        # Loop over each Gamma value to load data and generate a plot
        for idx, Gamma in enumerate(Gamma_values):
            filename = f"TI{Gamma}_res_{idx_obj:03d}.txt"  # Load the corresponding Gamma file
            filename = os.path.join(resdir, filename)
            data = np.loadtxt(filename)

            # Extract columns: lon, lat, flux5, flux8,  x1, y1, z1, x2, y2, z2
            lon, lat, flux5, flux8 = data[:, 1], data[:, 2], data[:, 3], data[:, 4]
            x1, y1, z1     = data[:, 5], data[:, 6], data[:, 7]
            x2, y2, z2     = data[:, 8], data[:, 9], data[:, 10]

            df = pd.DataFrame(dict(
                lon=lon, lat=lat, flux5=flux5, flux8=flux8,
                X=x1, Y=y1, Z=z1, MirX=x2, MirY=y2, MirZ=z2
                ))
            df["TI"] = Gamma
            df["objid"] = idx_obj

            df_list.append(df)
    df = pd.concat(df_list)

    # Calculate alpha, r, and delta
    df = calc_aspect(df)

    # NEATM 
    # Assumption
    H = 25
    # geometric albedo
    pv = 0.1 
    # H=25 and pv=0.1 -> D=42
    D_true = 42
    eta = args.eta
    print("Parameters for NEATM")
    print(f"  H={H}, eta={eta}")
    D_NEATM_list = []
    df = df.reset_index(drop=True)

    if args.key_flux == "flux8":
        w = 8.0
        key_flux = "flux8"
    elif args.keu_flux == "flux5":
        w = 5.0
        key_flux = "flux5"
    else:
        assert False, "Not implemented."

    for idx, row in df.iterrows():
        if (idx%1000)==0:
            print(f"  {idx}/{len(df)}")
        # TODO Check
        # Convert micronJy to Jy

        flux = row[key_flux]*1e-6
        fluxerr = flux*0.1
        lon   = row["lon"]
        lat   = row["lat"]
        r     = row["r"]
        delta = row["delta"]
        alpha = row["alpha"]
        cmd = f'echo {H} 0.15 0.9 {eta} 0.1 {r} {delta} {alpha} {w} {flux} {fluxerr} | fittm -m 1 | grep "o>"'

        p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        comm = p.communicate()
        D_NEATM = float(comm[0].decode('ascii').split()[1])
        # Diameter in m
        D_NEATM_list.append(D_NEATM*1e3)


    df["D_NEATM"] = D_NEATM_list
    df["D_true"] = D_true

    # Save results in a new file
    out = args.out
    outdir = args.outdir
    out = os.path.join(outdir, out)
    df.to_csv(out, sep=" ")

