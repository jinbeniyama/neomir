#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        "--outdir", type=str, default="plot",
        help="Directory for output file")
    args = parser.parse_args()

    resdir = args.resdir
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    Gamma_values = [0, 50, 150, 300, 500, 1000]
    
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
        ax1 = fig.add_axes([0.1, 0.65, 0.3, 0.22])
        ax2 = fig.add_axes([0.6, 0.65, 0.3, 0.22])
        ax3 = fig.add_axes([0.1, 0.35, 0.3, 0.22])
        ax4 = fig.add_axes([0.6, 0.35, 0.3, 0.22])
        ax5 = fig.add_axes([0.1, 0.05, 0.3, 0.22])
        ax6 = fig.add_axes([0.6, 0.05, 0.3, 0.22])
       


        axs = [ax1, ax2, ax3, ax4, ax5, ax6]
        
        # Loop over each Gamma value to load data and generate a plot
        for idx, Gamma in enumerate(Gamma_values):
            filename = f"TI{Gamma}_res_{idx_obj:03d}.txt"  # Load the corresponding Gamma file
            filename = os.path.join(resdir, filename)
            data = np.loadtxt(filename)
        
            # Extract columns: lon, lat, flux
            lon, lat, flux = data[:, 1], data[:, 2], data[:, 3]
            # These are common
            x1, y1, z1     = data[:, 4][0], data[:, 5][0], data[:, 6][0]
            x2, y2, z2     = data[:, 7][0], data[:, 8][0], data[:, 9][0]

            # Calculate alpha, r, delta
            S = np.array([x1, y1, z1]).T
            r = np.sqrt(np.sum(S**2))
            O = np.array([x2, y2, z2]).T
            delta = np.sqrt(np.sum(O**2))
            SO = S*O
            alpha = np.arccos(np.sum(SO)/r/delta)*180/np.pi
            print(f"  r, delta, alpha = {r:.2f}, {delta:.2f}, {alpha:.2f}")

            print(f"Gamma {Gamma}: min={np.min(flux)}, max={np.max(flux)}, median={np.median(flux)}, std={np.std(flux)}")
            
                    
            info = f"(r, delta, alpha) = ({r:.2f} au, {delta:.2f} au, {alpha:.2f} deg)"
            ax1.text(0.5, 1.2, info, size=22, transform=ax1.transAxes)
        
            # Interpolate scattered data to grid
            flux_grid = griddata((lon, lat), flux, (lon_mesh, lat_mesh), method='cubic')
        
            # Plot in the correct subplot (3x2 grid)
            ax = axs[idx] 
            c = ax.contourf(lon_mesh, lat_mesh, flux_grid, levels=50, cmap='viridis', vmin=20, vmax=400)
            fig.colorbar(c, ax=ax, label='Flux (microJy)')
        
            # Add contour lines
            contour_lines = ax.contour(lon_mesh, lat_mesh, flux_grid, levels=10, colors='red', linewidths=0.5)
        
            # Add labels to contour lines
            ax.clabel(contour_lines, inline=True, fontsize=10, fmt="%.0f", colors='red')
        
            # Set labels and title
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_xlim([0,  360])
            ax.set_ylim([-90, 90])
            ax.set_title(f"Gamma = {Gamma} tiu")
            if (Gamma>0):
                allFluxes.extend(flux)
        
        
        allFluxes=np.sort(allFluxes)
        plt.plot(allFluxes, np.arange(1,len(allFluxes)+1)/len(allFluxes))
        plt.savefig(out)
        plt.close()
