#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot 8 micron flux!
"""
from argparse import ArgumentParser as ap
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.interpolate import griddata


if __name__ == "__main__":
    parser = ap(description="Plot TPM results for NEOMIR.")
    parser.add_argument(
        "--idx_obj", type=int, nargs="*", default=[1],
        help="Index of objects to be plotted")
    parser.add_argument(
        "--all", action="store_true", default=False,
        help="Try to plot all resuls")
    parser.add_argument(
        "--resdir", type=str, default="tpmresult",
        help="Directory with output files")
    parser.add_argument(
        "--vmin", type=float, default=20.0,
        help="Minimum value")
    parser.add_argument(
        "--vmax", type=float, default=400.0,
        help="Maximum value")
    parser.add_argument(
        "--cmap", type=str, default="inferno",
        help="Color map")
    parser.add_argument(
        "--out", type=str, default=None,
        help="Output filename (only for N(idx_obj)==1)")
    parser.add_argument(
        "--outdir", type=str, default="plot",
        help="Directory for output file")
    args = parser.parse_args()

    resdir = args.resdir
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    Gamma_values = [0, 50, 150, 300, 500, 1000]
    vmin, vmax = args.vmin, args.vmax
    cmap = args.cmap
    
    if args.all:
        # Try to find object id
        filenames = [f.name for f in os.scandir(resdir)]
        # Extract object id from TI150_res_012.txta
        filenames_part = [f.split("_")[-1] for f in filenames]
        idx_plot = [int(f.split(".")[0]) for f in filenames_part]
        idx_plot = list(set(idx_plot))
    else:
        idx_plot = args.idx_obj


    for idx_obj in idx_plot:
        print(f"Make a figure for OBJ{idx_obj:03d}")
        
        if args.out:
            out = args.out
        else:
            out = f"tpmres_NEOMIR_obj{idx_obj:03d}.jpg"
        out = os.path.join(outdir, out)


        allFluxes=[]
        
        # Define grid resolution
        num_points = 100  # Adjust for finer/coarser smoothing
        lon_grid = np.linspace(0, 360, num_points)
        lat_grid = np.linspace(-90, 90, num_points)
        lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)
        
        # Create a 3x2 subplot
        fig = plt.figure(figsize=(12, 16))
        ax1 = fig.add_axes([0.1, 0.70, 0.3, 0.22])
        ax2 = fig.add_axes([0.6, 0.70, 0.3, 0.22])
        ax3 = fig.add_axes([0.1, 0.38, 0.3, 0.22])
        ax4 = fig.add_axes([0.6, 0.38, 0.3, 0.22])
        ax5 = fig.add_axes([0.1, 0.06, 0.3, 0.22])
        ax6 = fig.add_axes([0.6, 0.06, 0.3, 0.22])
       


        axs = [ax1, ax2, ax3, ax4, ax5, ax6]
        
        # Loop over each Gamma value to load data and generate a plot
        for idx, Gamma in enumerate(Gamma_values):
            filename = f"TI{Gamma}_res_{idx_obj:03d}.txt"  # Load the corresponding Gamma file
            filename = os.path.join(resdir, filename)
            data = np.loadtxt(filename)
        
            # Extract columns: lon, lat, flux
            lon, lat, flux5, flux8 = data[:, 2], data[:, 3], data[:, 4], data[:, 5]
            # Since we used asteroids with diameters of 1 km in TPM to avoid the loss of digits,
            # we have to slace fluxes here.
            # From 1 km to 42 m (H=25, pv=0.1)
            sf = (42./1000.)**2
            flux5, flux8 = flux5*sf, flux8*sf

            # These are common
            x1, y1, z1     = data[:, 6][0], data[:, 7][0], data[:, 8][0]
            x2, y2, z2     = data[:, 9][0], data[:, 10][0], data[:, 11][0]

            # Calculate alpha, r, delta
            S = np.array([x1, y1, z1]).T
            r = np.sqrt(np.sum(S**2))
            O = np.array([x2, y2, z2]).T
            delta = np.sqrt(np.sum(O**2))
            SO = S*O
            alpha = np.arccos(np.sum(SO)/r/delta)*180/np.pi
            print(f"  r, delta, alpha = {r:.2f}, {delta:.2f}, {alpha:.2f}")
            print(f"Gamma {Gamma}: min={np.min(flux8)}, max={np.max(flux8)}, median={np.median(flux8)}, std={np.std(flux8)}")
            
                    
            info = r"(r, $\Delta$, $\alpha$) = " + f"({r:.2f} au, {delta:.2f} au, {alpha:.2f} deg)"
            #ax1.text(0.5, 1.2, info, size=22, horizontalalignment="left", transform=ax1.transAxes)
            fig.suptitle(info, fontsize=20)
        
            # Interpolate scattered data to grid
            flux_grid = griddata((lon, lat), flux8, (lon_mesh, lat_mesh), method='cubic')
        
            # Plot in the correct subplot (3x2 grid)
            ax = axs[idx] 
            c = ax.contourf(lon_mesh, lat_mesh, flux_grid, levels=50, cmap=cmap, vmin=vmin, vmax=vmax)
            fig.colorbar(c, ax=ax, label=r'Flux deinsity ($\mu$Jy)')
        
            # Add contour lines
            contour_lines = ax.contour(lon_mesh, lat_mesh, flux_grid, levels=10, colors='red', linewidths=0.5)
        
            # Add labels to contour lines
            ax.clabel(contour_lines, inline=True, fontsize=10, fmt="%.0f", colors='red')
        
            # Set labels and title
            ax.set_xlabel('Ecliptic longitude of north rotation pole', fontsize=14)
            ax.set_ylabel('Ecliptic latitude of north rotation pole', fontsize=14)
            ax.set_xlim([0,  360])
            ax.set_ylim([-90, 90])
            ax.set_title(r"$\Gamma$" + f" = {Gamma} tiu", fontsize=14)
            if (Gamma>0):
                allFluxes.extend(flux8)
        
        # Useless?
        #allFluxes = np.sort(allFluxes)
        #plt.plot(allFluxes, np.arange(1,len(allFluxes)+1)/len(allFluxes))
        plt.savefig(out)
        plt.close()
