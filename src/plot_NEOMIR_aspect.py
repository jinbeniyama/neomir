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
        "obsdir1", type=str,
        help="Directory with output files")
    parser.add_argument(
        "obsdir2", type=str,
        help="Directory with output files")
    parser.add_argument(
        "--out", type=str, default="aspect.jpg",
        help="Output filename")
    parser.add_argument(
        "--outdir", type=str, default="plot",
        help="Directory for output file")
    args = parser.parse_args()

    obsdir1 = args.obsdir1
    obsdir2 = args.obsdir2
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)


    # Original objects ========================================================
    filenames1 = [f.name for f in os.scandir(obsdir1)]
    df1_list = []
    for idx_fi, fi in enumerate(filenames1):
        fi = os.path.join(obsdir1, fi)
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
            df1_list.append(df)
    df1 = pd.concat(df1_list)
    df1 = df1.reset_index(drop=True)
    # Original objects ========================================================


    # Control objects =========================================================
    filenames2 = [f.name for f in os.scandir(obsdir2)]
    df2_list = []
    for idx_fi, fi in enumerate(filenames2):
        fi = os.path.join(obsdir2, fi)
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
            df2_list.append(df)
    df2 = pd.concat(df2_list)
    df2 = df2.reset_index(drop=True)
    # Control objects =========================================================

    # Calculate alpha, r, and delta
    df1 = calc_aspect(df1)
    df2 = calc_aspect(df2)
    r1_set = set(df1["r"])
    delta1_set = set(df1["delta"])
    alpha1_set = set(df1["alpha"])
    r2_set = set(df2["r"])
    delta2_set = set(df2["delta"])
    alpha2_set = set(df2["alpha"])


    # Plot r, delta, alpha dependence =========================================
    fig = plt.figure(figsize=(16, 6))
    ax_a = fig.add_axes([0.07, 0.20, 0.24, 0.7])
    ax_r = fig.add_axes([0.40, 0.20, 0.24, 0.7])
    ax_d = fig.add_axes([0.73, 0.20, 0.24, 0.7])

    ax_a.set_xlabel("Phase angle [deg]")
    ax_r.set_xlabel("Heliocentric distance [au]")
    ax_d.set_xlabel("NEOMIR-centric distance [au]")

    ax_a.set_ylabel("N")
    ax_r.set_ylabel("N")
    ax_d.set_ylabel("N")

    lab_ori, lab_pse = f"Original asteroids N={len(df1)}", f"Control asteroids N={len(df2)}"
    col_ori, col_pse = "red", "blue"
    ls_ori, ls_pse = "solid", "dashed"
    
    bins = np.arange(0, 151, 5)
    ax_a.hist(
        alpha1_set, bins=bins, histtype="step", label=lab_ori, color=col_ori, ls=ls_ori)
    ax_a.hist(
        alpha2_set, bins=bins, histtype="step", label=lab_pse, color=col_pse, ls=ls_pse)

    bins = np.arange(0.6, 1.4, 0.04)
    ax_r.hist(
        r1_set, bins=bins, histtype="step", label=lab_ori, color=col_ori, ls=ls_ori)
    ax_r.hist(
        r2_set, bins=bins, histtype="step", label=lab_pse, color=col_pse, ls=ls_pse)

    bins = np.arange(0.0, 0.4, 0.02)
    ax_d.hist(
        delta1_set, bins=bins, histtype="step", label=lab_ori, color=col_ori, ls=ls_ori)
    ax_d.hist(
        delta2_set, bins=bins, histtype="step", label=lab_pse, color=col_pse, ls=ls_pse)

    ax_a.legend()
    ax_r.legend()
    ax_d.legend()

    out = args.out
    out = os.path.join(outdir, out)
    plt.savefig(out)
    plt.close()
    # Plot r, delta, alpha dependence =========================================
