#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot diameters derived from NEATM/FRM.
"""
from argparse import ArgumentParser as ap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter

from NEOMIR_common import mycolor, Gamma_values


if __name__ == "__main__":
    parser = ap(description="Plot NEATM/FRM diameters for NEOMIR.")
    parser.add_argument(
        "res", type=str, nargs="*",
        help="Result of NEATM/FRM")
    parser.add_argument(
        "--out", type=str, default="diameter_res.png",
        help="Directory for output file")
    parser.add_argument(
        "--outeta", type=str, default="eta.png",
        help="Directory for output file (beaming parameter)")
    parser.add_argument(
        "--ymax", type=float, default=0,
        help="Maxmimum y")
    parser.add_argument(
        "--outdir", type=str, default="fig",
        help="Directory for output file")
    args = parser.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    
    df_list = []
    for res in args.res:
        df = pd.read_csv(res, sep=" ")
        df_list.append(df)

    df = pd.concat(df_list)

    model = list(set(df["model"]))[0]

    # Diameter ratio
    df["Dr"] = df["D_model"]/df["D_true"]

    # Plot
    fig = plt.figure(figsize=(12, 4))
    ax_a = fig.add_axes([0.10, 0.20, 0.23, 0.7])
    ax_r = fig.add_axes([0.40, 0.20, 0.23, 0.7])
    ax_d = fig.add_axes([0.70, 0.20, 0.23, 0.7])

    ax_a.set_xlabel("Phase angle [deg]", fontsize=12)
    ax_r.set_xlabel("Heliocentric distance [au]", fontsize=12)
    ax_d.set_xlabel("NEOMIR-centric distance [au]", fontsize=12)
    ax_a.set_ylabel(r"$D_{" + model + r"}/D_{true}$", fontsize=12)

    for idx_TI, TI in enumerate(Gamma_values):
        df_TI = df[df["TI"] == TI]
        df_negative_D = df_TI[df_TI["Dr"] < 0] 
        Nall = len(df_TI)
        Nn = len(df_negative_D)
        zorder = 100 - idx_TI
        shift = idx_TI*1
        # For FRM 
        if Nn > 0:
            label=f"{TI} tiu (N={Nall}, Nnegative={Nn})"
        else:
            label=f"{TI} tiu, N={Nall}"
        ax_a.scatter(
            df_TI["alpha"]+shift, df_TI["Dr"], label=label, color=mycolor[idx_TI], s=5, marker="o", fc="None", zorder=zorder)
        ax_r.scatter(
            df_TI["r"], df_TI["Dr"], label=label, color=mycolor[idx_TI], s=5, marker="o", fc="None", zorder=zorder)
        ax_d.scatter(
            df_TI["delta"], df_TI["Dr"], label=label, color=mycolor[idx_TI], s=5, marker="o", fc="None", zorder=zorder)

    for ax in [ax_a, ax_r, ax_d]:
        ax.legend(fontsize=8)
        if args.ymax:
            yticks = np.arange(0, 7, 1.0)
            ax.yaxis.set_major_locator(ticker.FixedLocator(yticks))
            ax.set_ylim([0, args.ymax])
        else:
            ax.set_ylim([0.3, 5.5])
            ax.set_yscale("log")

            label_map = {0.3: "30%", 0.5: "50%", 1: "100%", 2: "200%", 3: "300%", 4: "400%", 5: "500%"}
            label_map = {0.3: 0.3,  0.5: 0.5, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
            
            ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: label_map.get(y, "")))
            
            ax.yaxis.set_minor_formatter(FuncFormatter(lambda y, _: label_map.get(y, "")))
            
            ax.tick_params(axis='y', which='major', length=6, width=1)
            ax.tick_params(axis='y', which='minor', length=3, width=1, labelsize=10)


    out = os.path.join(outdir, args.out)
    plt.savefig(out)
    plt.close()

    # Plot beaming parameters for NEATM
    if model == "NEATM":
        fig = plt.figure(figsize=(8, 6))
        ax_e = fig.add_axes([0.15, 0.15, 0.8, 0.8])
        ax_e.set_xlabel("Beaming parameter", fontsize=12)
        ax_e.set_ylabel("N", fontsize=12)
        ax_e.set_yscale("log")
        x0 = df["eta"].min()-0.10
        x1 = df["eta"].max()+0.10

         # Define bin edges for histogram (0.1 step)
        eta_min = np.floor(df["eta"].min())
        eta_max = np.ceil(df["eta"].max())
        bins = np.arange(eta_min, eta_max + 0.1, 0.1)
        print(f"Global eta range: {eta_min}--{eta_max}")

        for idx_TI, TI in enumerate(Gamma_values):
            df_TI = df[df["TI"] == TI]
            eta_min_ti = np.floor(df_TI["eta"].min())
            eta_max_ti = np.ceil(df_TI["eta"].max())
            print(f"  Local eta range (TI={TI}): {eta_min_ti}--{eta_max_ti}")
            Nall = len(df_TI)
            label=f"{TI} tiu, N={Nall}"
            ax_e.hist(
                df_TI["eta"], histtype="step", bins=bins, color=mycolor[idx_TI], label=label)
        ax_e.set_xlim([x0, x1])
        ax_e.legend()
        out = os.path.join(outdir, args.outeta)
        plt.savefig(out)
        plt.close()
