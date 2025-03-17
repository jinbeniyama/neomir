#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot NEATM results.
"""
from argparse import ArgumentParser as ap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as ticker

mycolor = [
    "#AD002D",
    "#1e50a2",
    "#69821b",
    "#f055f0",
    "#afafb0",
    "#0095b9",
    "#89c3eb",
    "#ec6800",
    "cyan",
    "gold",
    "magenta"
    ]


if __name__ == "__main__":
    parser = ap(description="Plot NEATM results for NEOMIR.")
    parser.add_argument(
        "res", type=str, nargs="*",
        help="Result of NEATM")
    parser.add_argument(
        "--out", type=str, default="NEATM_res.png",
        help="Directory for output file")
    parser.add_argument(
        "--ymax", type=float, default=0,
        help="Maxmimum y")
    parser.add_argument(
        "--outdir", type=str, default="plot",
        help="Directory for output file")
    args = parser.parse_args()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    Gamma_values = [0, 50, 150, 300, 500, 1000]
    
    df_list = []
    for res in args.res:
        df = pd.read_csv(res, sep=" ")
        df_list.append(df)

    df = pd.concat(df_list)

    model = list(set(df["model"]))[0]

    # Diameter ratio
    df["Dr"] = df["D_NEATM"]/df["D_true"]

    # Plot
    fig = plt.figure(figsize=(16, 4))
    ax_a = fig.add_axes([0.05, 0.20, 0.18, 0.7])
    ax_r = fig.add_axes([0.29, 0.20, 0.18, 0.7])
    ax_d = fig.add_axes([0.53, 0.20, 0.18, 0.7])
    ax_e = fig.add_axes([0.77, 0.20, 0.18, 0.7])

    ax_a.set_xlabel("Phase angle [deg]", fontsize=12)
    ax_r.set_xlabel("Heliocentric distance [au]", fontsize=12)
    ax_d.set_xlabel("NEOMIR-centric distance [au]", fontsize=12)
    ax_a.set_ylabel(r"$D_{" + model + r"}/D_{true}$", fontsize=12)
    ax_e.set_xlabel("Beaming parameter", fontsize=12)
    ax_e.set_ylabel("N", fontsize=12)

    for idx_TI, TI in enumerate(Gamma_values):
        df_TI = df[df["TI"] == TI]
        zorder = 100 - idx_TI
        shift = idx_TI*1

        ax_a.scatter(
            df_TI["alpha"]+shift, df_TI["Dr"], label=f"{TI} tiu", color=mycolor[idx_TI], s=5, marker="o", fc="None", zorder=zorder)
        ax_r.scatter(
            df_TI["r"], df_TI["Dr"], label=f"{TI} tiu", color=mycolor[idx_TI], s=5, marker="o", fc="None", zorder=zorder)
        ax_d.scatter(
            df_TI["delta"], df_TI["Dr"], label=f"{TI} tiu", color=mycolor[idx_TI], s=5, marker="o", fc="None", zorder=zorder)
        ax_e.hist(df_TI["eta"], histtype="step", color=mycolor[idx_TI])

    yticks = np.arange(0, 7, 1.0)
    for ax in [ax_a, ax_r, ax_d]:
        ax.legend()
        ax.yaxis.set_major_locator(ticker.FixedLocator(yticks))
        if args.ymax:
            ax.set_ylim([0, args.ymax])
    out = os.path.join(outdir, args.out)
    plt.savefig(out)
    plt.close()
