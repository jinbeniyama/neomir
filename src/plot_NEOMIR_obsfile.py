#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check r, delta, and alpha.
And plot objects and Earth.
"""
from argparse import ArgumentParser as ap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


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
        "--obsdir", type=str, default="obsfile",
        help="Directory with output files")
    parser.add_argument(
        "--out", type=str, default="aspect.jpg",
        help="Output filename")
    parser.add_argument(
        "--outdir", type=str, default="plot",
        help="Directory for output file")
    args = parser.parse_args()

    obsdir = args.obsdir
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    # Try to find object id
    filenames = [f.name for f in os.scandir(obsdir)]
    
    df_list = []
    for idx_fi, fi in enumerate(filenames):
        fi = os.path.join(obsdir, fi)
        with open(fi, "r") as f:
            f = f.readlines()
            # Extract positions
            
            xyz = f[3].replace("\n", "")
            xyzMIR = f[4].replace("\n", "")
            xyz = xyz.split()
            xyzMIR = xyzMIR.split()
            x1, y1, z1     = float(xyz[0]), float(xyz[1]), float(xyz[2])
            x2, y2, z2     = float(xyzMIR[0]), float(xyzMIR[1]), float(xyzMIR[2])

            df = pd.DataFrame(dict(
                X=[x1], Y=[y1], Z=[z1], MirX=[x2], MirY=[y2], MirZ=[z2]
                ))
            df["objid"] = idx_fi
            df_list.append(df)
    df = pd.concat(df_list)

    # Calculate alpha, r, and delta
    df = calc_aspect(df)
    r_set = set(df["r"])
    delta_set = set(df["delta"])
    alpha_set = set(df["alpha"])


    # Plot r, delta, alpha dependence =========================================
    fig = plt.figure(figsize=(16, 6))
    ax_a = fig.add_axes([0.10, 0.20, 0.25, 0.7])
    ax_r = fig.add_axes([0.40, 0.20, 0.25, 0.7])
    ax_d = fig.add_axes([0.70, 0.20, 0.25, 0.7])

    ax_a.set_xlabel("Phase angle [deg]")
    ax_r.set_xlabel("Heliocentric distance [au]")
    ax_d.set_xlabel("NEOMIR-centric distance [au]")

    ax_a.set_ylabel("N")
    ax_r.set_ylabel("N")
    ax_d.set_ylabel("N")

    bins = np.arange(0, 151, 5)
    ax_a.hist(
        alpha_set, bins=bins, histtype="step", label="All", color="black")
    bins = np.arange(0.5, 1.1, 0.05)
    ax_r.hist(
        r_set, bins=bins, histtype="step", label="All", color="black")
    bins = np.arange(0.0, 0.5, 0.05)
    ax_d.hist(
        delta_set, bins=bins, histtype="step", label="All", color="black")

    ax_a.legend()
    ax_r.legend()
    ax_d.legend()

    out = args.out
    out = os.path.join(outdir, out)
    plt.savefig(out)
    plt.close()
    # Plot r, delta, alpha dependence =========================================
