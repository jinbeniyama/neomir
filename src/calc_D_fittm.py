#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate diameter with NEATM/FRM.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess, os
from argparse import ArgumentParser as ap


def read_tpmres_neomir(resdir, idx_plot, Gamma_valuea):
    """

    Parameters
    ----------
    resdir : str
        directory with tpm results
    idx_plot : array-like   
        index of objects to be analyzed
    Gamma_values : array-like
        thermal inertia
    """
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
            D, lon, lat  = data[:, 1], data[:, 2], data[:, 3], 
            flux5, flux8 = data[:, 4], data[:, 5]
            x1, y1, z1   = data[:, 6], data[:, 7], data[:, 8]
            x2, y2, z2   = data[:, 9], data[:, 10], data[:, 11]

            df = pd.DataFrame(dict(
                D=D, lon=lon, lat=lat, flux5=flux5, flux8=flux8,
                X=x1, Y=y1, Z=z1, MirX=x2, MirY=y2, MirZ=z2
                ))
            df["TI"] = Gamma
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


if __name__ == "__main__":
    parser = ap(description="Plot TPM results for NEOMIR.")
    parser.add_argument(
        "--idx_obj", type=int, nargs="*", default=[1],
        help="Index of objects to be plotted")
    parser.add_argument(
        "--all", action="store_true", default=False,
        help="Try to plot all resuls")
    parser.add_argument(
        "--model", type=str, default="NEATM",
        help="Model (NEATM or FRM)")
    parser.add_argument(
        "--fiteta", action="store_true", default=False,
        help="Fit eta")
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

    # Optimized for NEOMIR paper in 2025
    Gamma_values = [0, 50, 150, 300, 500, 1000]
    w5, key_flux5 = 5.0, "flux5"
    w8, key_flux8 = 8.0, "flux8"

    # To calculate NEATM flux, we need D,
    # but H and pv are neccesary as inputs
    # in km
    D_true = 1
    # geometric albedo (assumed)
    pv = 0.1 
    # D=1 and pv=0.1 -> H=18.118
    H = 18.118

    # Model (NEATM or FRM)
    model = args.model
    if model == "NEATM":
        if args.fiteta:
            N_model = 0
            etafit  = 1
            print("Use NEATM fitting eta")
        else:
            N_model = 1
            etafit  = 0
            print("Use NEATM w/ fixed eta")
    elif model == "FRM":
        N_model = 3
        etafit  = 0
        print("Use FRM")
    
    if args.all:
        # Try to find object id
        filenames = [f.name for f in os.scandir(resdir)]
        # Extract object id from TI150_res_012.txta
        filenames_part = [f.split("_")[-1] for f in filenames]
        idx_plot = [int(f.split(".")[0]) for f in filenames_part]
        idx_plot = list(set(idx_plot))
    else:
        idx_plot = args.idx_obj
    
    df = read_tpmres_neomir(resdir, idx_plot, Gamma_values)



    # Calculate alpha, r, and delta
    df = calc_aspect(df)

    eta = args.eta
    print("Parameters for NEATM")
    print(f"  H={H}, eta={eta}")
    D_NEATM_list = []
    eta_NEATM_list = []
    df = df.reset_index(drop=True)

    for idx, row in df.iterrows():
        if (idx%1000)==0:
            print(f"  {idx}/{len(df)}")
        # Convert micronJy to Jy
        flux5 = row[key_flux5]*1e-6
        flux8 = row[key_flux8]*1e-6
        fluxerr5 = flux5*0.1
        fluxerr8 = flux8*0.1
        lon   = row["lon"]
        lat   = row["lat"]
        r     = row["r"]
        delta = row["delta"]
        alpha = row["alpha"]
        
        # Use 2-bands
        # Note: eta is not used in FRM. (output is always eta of 1)
        #       So of cource eta is not fit in FRM.
        if args.fiteta:
            # TODO: {w5} {flux5} {fluxerr5} {w8} {flux8} {fluxerr8} and 
            #       {w8} {flux8} {fluxerr8} {w5} {flux5} {fluxerr5} give different results?
            cmd = f'echo {H} 0.15 0.9 {eta} 0.1 {r} {delta} {alpha} {w5} {flux5} {fluxerr5} {w8} {flux8} {fluxerr8} | fittm -m {N_model} | grep "o>"'
        # Use only 8 micron
        else:
            cmd = f'echo {H} 0.15 0.9 {eta} 0.1 {r} {delta} {alpha} {w8} {flux8} {fluxerr8} | fittm -m {N_model} | grep "o>"'

        
        p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        comm = p.communicate()
        res = comm[0].decode("ascii").split()
        D_NEATM = float(res[1])
        eta_NEATM = float(res[5])
        # Diameter in km
        D_NEATM_list.append(D_NEATM)
        eta_NEATM_list.append(eta_NEATM)

    df["D_NEATM"] = D_NEATM_list
    df["D_true"] = D_true
    df["model"] = args.model
    df["eta"] = eta_NEATM_list
    df["etafit"] = etafit

    # Save results in a new file
    out = args.out
    outdir = args.outdir
    out = os.path.join(outdir, out)
    df.to_csv(out, sep=" ")
