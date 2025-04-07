#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check r, delta, and alpha.
And plot objects and Earth.
"""
from argparse import ArgumentParser as ap
import pandas as pd
import matplotlib.pyplot as plt
import os
from astroquery.jplhorizons import Horizons

mycolor = [
    "#AD002D", "#1e50a2", "#69821b", "#f055f0", "#afafb0", 
    "#0095b9", "#89c3eb", "#ec6800", "cyan", "gold"]

if __name__ == "__main__":
    parser = ap(description="Plot TPM results for NEOMIR.")
    parser.add_argument(
        "obsdir1", type=str,
        help="Directory with output files")
    parser.add_argument(
        "obsdir2", type=str,
        help="Directory with output files")
    parser.add_argument(
        "--out", type=str, default="loc.jpg",
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

    df1["x"] = -df1["X"]
    df1["y"] = -df1["Y"]
    df1["z"] = -df1["Z"]
    df2["x"] = -df2["X"]
    df2["y"] = -df2["Y"]
    df2["z"] = -df2["Z"]


    out = args.out
    out = os.path.join(args.outdir, out)

    # Plot
    # 500 represents the center
    # @0 represents that coordinate origin is the solar barycenter, 
    # @10 represents that coordinate origin is the Sun-body center
    # location='500@0' seems bad for this purpose
    # The location is not overlapped.
    # Default is 500@10 (Sun-body center), not 500@0 (barucenter)
    wid = 1.5
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_axes([0.15, 0.15, 0.8, 0.8])
    
    ax.set_xlim([-wid, wid])
    ax.set_ylim([-wid, wid])
    ax.set_xlabel("x [au]")
    ax.set_ylabel("y [au]")
    
    # Oroginal 
    for idx, row in df1.iterrows():
        col = mycolor[0]
        mark = "o"
        si = 50
        if idx == 0:
            lab = f"Original asteroids N={len(df1)}"
        else:
            lab = None
        ax.scatter(
            row["x"], row["y"], color=col, lw=1, ls="solid", 
            label=lab, zorder=-1, s=si, marker=mark, facecolor="None")
    # Control
    for idx, row in df2.iterrows():
        col = mycolor[1]
        mark = "x"
        si = 50
        if idx == 0:
            lab = f"Control asteroids N={len(df2)}\n(Symmetric with respect to the NEOMIR)"
        else:
            lab = None
        ax.scatter(row["x"], row["y"], color=col, lw=1, ls="solid", label=lab, zorder=-1, s=si, marker=mark)

    # Earth
    t0 = "2024-08-14"
    t1 = "2025-08-15"
    Earth1 = Horizons(
        location='500@10',
        id="399", epochs={'start':t0, 'stop':t1, 'step':"1d"})
    Earth1 = Earth1.vectors()
    lab = "Earth orbit"
    ax.plot(Earth1["x"], Earth1["y"], color="grey", lw=1.5, ls="dashed", label=lab, zorder=-1)
    # Sun
    ax.scatter(0, 0, marker="x", color="black", lw=1.5, s=200)

    ax.legend(loc="lower left", fontsize=12)
    plt.savefig(out)
    plt.close()
