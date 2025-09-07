#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot SED!

Note that idx_obj == 1 is the first object (i.e., 43176445 in position.txt, objid==0 in FRM_control_10_1b.txt etc.)
"""
from argparse import ArgumentParser as ap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.interpolate import griddata

from NEOMIR_common import mycolor


if __name__ == "__main__":
    parser = ap(description="Plot SED of an object for NEOMIR.")
    parser.add_argument(
        "--idx_obj", type=int, nargs="*", default=[1],
        help="Index of objects to be plotted")
    parser.add_argument(
        "--resdir", type=str, default="tpmresult",
        help="Directory with output files")
    parser.add_argument(
        "--TI", type=int, nargs="*", default=None,
        help="Thermal inertia")
    parser.add_argument(
        "--yr", type=float, nargs=2, default=None,
        help="Y range")
    parser.add_argument(
        "--cmap", type=str, default="inferno",
        help="Color map")
    parser.add_argument(
        "--out", type=str, default=None,
        help="Output filename (only for N(idx_obj)==1)")
    args = parser.parse_args()

    resdir = args.resdir
    
    if args.TI is not None:
        Gamma_values = args.TI
    else:
        Gamma_values = [0, 50, 150, 300, 500, 1000]
    cmap = args.cmap
    
    idx_plot = args.idx_obj

    if args.out:
        out = args.out
    else:
        out = f"tpmres_NEOMIR_obj{idx_obj:03d}.jpg"

    # From 1 km to 42 m (H=25, pv=0.1)
    sf = (42./1000.)**2

    for idx_obj in idx_plot:
        print(f"Make a figure for OBJ{idx_obj:03d}")
        
        # Create a 3x2 subplot
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_axes([0.18, 0.15, 0.8, 0.75])
        ax.set_xlabel(r"Wavelength [$\mu$m]")
        ax.set_ylabel(r"Flux density [$\mu$Jy]")
        ax.set_yscale("log")
        
        # Loop over each Gamma value to load data and generate a plot
        for idx_ti, Gamma in enumerate(Gamma_values):
            filename = f"TI{Gamma}_res_{idx_obj:03d}.txt"  # Load the corresponding Gamma file
            filename = os.path.join(resdir, filename)
            df = pd.read_csv(filename, sep=" ")

            keys_flux = [x for x in set(df.columns) if "flux" in x]
            # Loop for pole 
            for idx, row in df.iterrows():
                w_list, f_list = [], []
                for key_flux in keys_flux:
                    w = key_flux.replace("flux", "")
                    # Micro junsky
                    f = row[key_flux]
                    w_list.append(float(w))
                    # Consider scale factor
                    f_list.append(float(f)*sf)

                pairs = sorted(zip(w_list, f_list), key=lambda x: x[0])
                w_list, f_list = map(list, zip(*pairs))
                label = f"idx_pole: {idx}"
                label = None
                lw = 2
                col = mycolor[idx_ti]
                ax.plot(w_list, f_list, label=label, lw=lw, color=col)

            assert len(set(df["x1"])) == 1, "Check the code."
            x1, y1, z1 = df["x1"].values[0], df["y1"].values[0], df["z1"].values[0]
            x2, y2, z2 = df["x2"].values[0], df["y2"].values[0], df["z2"].values[0]
            print(f"x1, y1, z1 = {x1}, {y1}, {z1}")
            print(f"x2, y2, z2 = {x2}, {y2}, {z2}")

            # Calculate alpha, r, delta
            S = np.array([x1, y1, z1]).T
            r = np.sqrt(np.sum(S**2))
            O = np.array([x2, y2, z2]).T
            delta = np.sqrt(np.sum(O**2))
            SO = S*O
            alpha = np.arccos(np.sum(SO)/r/delta)*180/np.pi
            if idx_ti == 0:
                print(f"  r, delta, alpha = {r:.2f}, {delta:.2f}, {alpha:.2f}")
            #print(f"  Fluxes ({key_flux}) [microJy] when thermal inertia = {Gamma:04d}: min={np.min(flux):.2f}, max={np.max(flux):.2f}, median={np.median(flux):.2f}, std={np.std(flux):.2f}")
                    
            info = r"(r, $\Delta$, $\alpha$) = " + f"({r:.2f} au, {delta:.2f} au, {alpha:.2f} deg)"
            ax.set_title(info)
        
        
        if args.yr is not None:
            ax.set_ylim(args.yr)
        ax.legend()
        plt.savefig(out)
        plt.close()
