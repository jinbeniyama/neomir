#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser as ap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from NEOMIR_common import mycolor, handle_tpmres, calc_aspect


if __name__ == "__main__":
    parser = ap(description="Plot TPM results for NEOMIR.")
    parser.add_argument(
        "--idx_obj", type=int, nargs="*", default=[1],
        help="Index of objects to be plotted")
    parser.add_argument(
        "--resdir1", type=str, default="tpmresult",
        help="Directory with output files")
    parser.add_argument(
        "--resdir2", type=str, default="tpmresult_pseudo",
        help="Directory with output files")
    parser.add_argument(
        "--outdir", type=str, default="fig",
        help="Directory for output file")
    parser.add_argument(
        "--out", type=str, default="8flux_aspect.png",
        help="Output file")
    args = parser.parse_args()

    resdir1 = args.resdir1
    resdir2 = args.resdir2
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    Gamma_values = [0, 50, 150, 300, 500, 1000]
    key_flux = "flux8"
    # Font size
    fs = 14
    
    # Read original objects
    df1 = handle_tpmres(resdir1)
    # Read control objects
    df2 = handle_tpmres(resdir2)
    # Merge
    df = pd.concat([df1, df2])

    # Calculate alpha, r, and delta
    df = calc_aspect(df)

    # Plot r, delta, alpha vs. flux (TI dependence) ===========================
    fig = plt.figure(figsize=(16, 14))
    ax_a = fig.add_axes([0.10, 0.58, 0.25, 0.37])
    ax_r = fig.add_axes([0.40, 0.58, 0.25, 0.37])
    ax_d = fig.add_axes([0.70, 0.58, 0.25, 0.37])
    ax_a2 = fig.add_axes([0.10, 0.10, 0.25, 0.37])
    ax_r2 = fig.add_axes([0.40, 0.10, 0.25, 0.37])
    ax_d2 = fig.add_axes([0.70, 0.10, 0.25, 0.37])
    ax_a2.set_xlabel(r"Phase angle, $\alpha$ [deg]", fontsize=fs)
    ax_r2.set_xlabel("Heliocentric distance, r [au]", fontsize=fs)
    ax_d2.set_xlabel(r"NEOMIR-centric distance, $\Delta$ [au]", fontsize=fs)
    ax_a.set_ylabel("Flux density [$\mu$Jy]", fontsize=fs)
    ax_a2.set_ylabel(r"Flux density$\times \Delta^2$ [$\mu$Jy]", fontsize=fs)


    for idx_TI, TI in enumerate(Gamma_values):
        df_TI = df[df["TI"] == TI]
        zorder = 100 - idx_TI

        label = f"{TI} tiu"

        ax_a.scatter(
            df_TI["alpha"], df_TI[key_flux], label=label, color=mycolor[idx_TI], s=15, marker="o", fc="None", zorder=zorder)
        ax_r.scatter(
            df_TI["r"], df_TI[key_flux], label=label, color=mycolor[idx_TI], s=15, marker="o", fc="None", zorder=zorder)
        ax_d.scatter(
            df_TI["delta"], df_TI[key_flux], label=label, color=mycolor[idx_TI], s=15, marker="o", fc="None", zorder=zorder)

        # Normalize the flux with delta
        # We cannot correct the effect of r, which affects the temperature dist.
        df_TI[key_flux] = df_TI[key_flux]*df_TI["delta"]*df_TI["delta"]

        ax_a2.scatter(
            df_TI["alpha"], df_TI[key_flux], label=label, color=mycolor[idx_TI], s=15, marker="o", fc="None", zorder=zorder)
        ax_r2.scatter(
            df_TI["r"], df_TI[key_flux], label=label, color=mycolor[idx_TI], s=15, marker="o", fc="None", zorder=zorder)
        ax_d2.scatter(
            df_TI["delta"], df_TI[key_flux], label=label, color=mycolor[idx_TI], s=15, marker="o", fc="None", zorder=zorder)
     
    for ax in fig.axes:
        ax.set_yscale("log")
        ax.legend()
    out = os.path.join(outdir, args.out)
    plt.savefig(out)
    plt.close()
    # Plot r, delta, alpha vs. flux (TI dependence) ===========================


    assert False, 1
    ## Prograde
    #df_pro = df[df["lat"] >= 0]
    #df_ret = df[df["lat"] < 0]
    #
    #f5_min = np.min(df["flux5"])
    #f5_max = np.max(df["flux5"])
    #f8_min = np.min(df["flux8"])
    #f8_max = np.max(df["flux8"])
    #df5_min = df[df["flux5"] == f5_min]
    #df5_max = df[df["flux5"] == f5_max]
    #df8_min = df[df["flux8"] == f8_min]
    #df8_max = df[df["flux8"] == f8_max]
    #print("Minimum 5 micron flux:")
    #print(df5_min)
    #print("Minimum 8 micron flux:")
    #print(df8_min)
    #print("Maximum 5 micron flux:")
    #print(df5_max)
    #print("Maximum 8 micron flux:")
    #print(df8_max)
    #out1 = f"tpmres_NEOMIR_stat_TI.jpg"
    #out1 = os.path.join(outdir, out1)
    #out2 = f"tpmres_NEOMIR_stat_geometry.jpg"
    #out2 = os.path.join(outdir, out2)
    # Plot Pro/retrograde, TI,  ===============================================
    fig = plt.figure(figsize=(16, 12))
    ax_lon = fig.add_axes([0.40, 0.55, 0.2, 0.35])
    ax_lat = fig.add_axes([0.70, 0.55, 0.2, 0.35])
    ax_f = fig.add_axes([0.10, 0.55, 0.25, 0.35])
    ax_f_TI = fig.add_axes([0.10, 0.10, 0.8, 0.35])

    ax_lon.set_xlabel("Longitude [deg]")
    ax_lon.set_ylabel("N")
    ax_lat.set_xlabel("Latitude [deg]")
    ax_lat.set_ylabel("N")

    # All
    for ax, key in zip([ax_lon, ax_lat], ["lon", "lat"]):
        
        if key == "lon":
            bins = np.arange(0, 361, 1)
        elif key == "lat":
            bins = np.arange(-90, 91, 1)
        ax.hist(
            df[key], bins=bins, histtype="step", label="Result of TPMs",
            color="black")
        # Prograde
        ax.hist(
            df_pro[key], bins=bins, histtype="step", label="Prograde",
            color="red")
        # Retrograde
        ax.hist(
            df_ret[key], bins=bins, histtype="step", label="Retrograde",
            color="blue")
        ax.legend()
    
    for ax in [ax_f, ax_f_TI]:
        ax.set_xlabel("Flux density [$\mu$Jy]")
        ax.set_ylabel("N")
        ax.grid()
        ax.set_xscale("log")
        ax.set_yscale("log")
    # Micro Jy
    bins = np.logspace(np.log10(1), np.log10(1e7), 100)


    # All
    ax_f.hist(
        df[key_flux], bins=bins, histtype="step", label="All",
        color="black")
    # Prograde
    ax_f.hist(
        df_pro[key_flux], bins=bins, histtype="step", label="Prograde",
        color="red")
    # Retrograde
    ax_f.hist(
        df_ret[key_flux], bins=bins, histtype="step", label="Retrograde",
        color="blue")
    # Detection limit of NEOMIR
    # TODO: check
    lim_NEOMIR_micronJy = 100
    ymin, ymax =ax_f.get_ylim()
    ax_f.vlines(
        lim_NEOMIR_micronJy, ymin, ymax, color="green", ls="dashed",
        label=f"NEOMIR limit {lim_NEOMIR_micronJy}" + "$\mu$Jy")
    ax_f.set_ylim([ymin, ymax])
    ax_f.legend()
    
    # All
    ax_f_TI.hist(
        df[key_flux], bins=bins, histtype="step", label="All",
        color="black")

    for TI in Gamma_values:
        df_TI = df[df["TI"] == TI]
        # Retrograde
        ax_f_TI.hist(
            df_TI[key_flux], bins=bins, histtype="step", label=f"TI={TI} tiu")
    # Detection limit of NEOMIR
    # TODO: check
    lim_NEOMIR_micronJy = 100
    ymin, ymax =ax_f_TI.get_ylim()
    ax_f_TI.vlines(
        lim_NEOMIR_micronJy, ymin, ymax, color="green", ls="dashed",
        label=f"NEOMIR limit {lim_NEOMIR_micronJy}" + "$\mu$Jy")
    ax_f_TI.set_ylim([ymin, ymax])
    ax_f_TI.legend()
    plt.savefig(out1)
    plt.close()
    # Plot Pro/retrograde, TI,  ===============================================



    r_set = set(df["r"])
    delta_set = set(df["delta"])
    alpha_set = set(df["alpha"])


    # Plot r, delta, alpha dependence =========================================
    fig = plt.figure(figsize=(16, 16))
    ax_a = fig.add_axes([0.10, 0.55, 0.25, 0.3])
    ax_r = fig.add_axes([0.40, 0.55, 0.25, 0.3])
    ax_d = fig.add_axes([0.70, 0.55, 0.25, 0.3])

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
    plt.savefig(out2)
    plt.close()
    # Plot r, delta, alpha dependence =========================================
