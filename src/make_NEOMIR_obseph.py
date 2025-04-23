#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Make obs file and ephem file for NEOMIR paper..
"""
import os 
from argparse import ArgumentParser as ap
import pandas as pd
from astropy import constants as const


if __name__ == "__main__":
    parser = ap(description="Make obs and eph file for tpm.")
    parser.add_argument(
        "--pos", type=str, default="position.txt",
        help="Output file")
    parser.add_argument(
        "--outeph", type=str, default="ephemfile",
        help="Directory for output file")
    parser.add_argument(
        "--outobs", type=str, default="obsfile",
        help="Directory for output file")
    parser.add_argument(
        "--pseudo", action="store_true", default=False,
        help="Make a pseudo objects")
    args = parser.parse_args()
   
    outeph = args.outeph
    os.makedirs(outeph, exist_ok=True)
    outobs = args.outobs
    os.makedirs(outobs, exist_ok=True)
    
    au_km = const.au.to("km").value

    # Read the file
    df = pd.read_csv(args.pos, sep="|", skiprows=1)


    for idx, row in df.iterrows():
        print(f"Make obs & eph files: {idx:03d}")
        x_ast, y_ast, z_ast = row["X"], row["Y"], row["Z"]
        x_mir, y_mir, z_mir = row["MirX"], row["MirY"], row["MirZ"]
        # Convert to au
        x_ast /= au_km
        y_ast /= au_km
        z_ast /= au_km
        x_mir /= au_km
        y_mir /= au_km
        z_mir /= au_km
        print(f"  x_ast, y_ast, z_ast = {x_ast}, {y_ast}, {z_ast}")
        print(f"  x_mir, y_mir, z_mir = {x_mir}, {y_mir}, {z_mir}")

        # Make pseudo objects at symmetric positions with respect to the earth
        if args.pseudo:
            # x, y, z = (X-2MirX, Y-2MirY, Z-2MirZ)
            # x, y, z = (-MirX, -MirY, -MirZ)
            x_ast = x_ast - 2*x_mir 
            y_ast = y_ast - 2*y_mir 
            z_ast = z_ast - 2*z_mir 
            x_mir = -x_mir
            y_mir = -y_mir
            z_mir = -z_mir
            print("Make pseudo object")
            print(f"  x_ast, y_ast, z_ast = {x_ast}, {y_ast}, {z_ast}")
            print(f"  x_mir, y_mir, z_mir = {x_mir}, {y_mir}, {z_mir}")


        # Ephemeris file ======================================================
        # JD r_X r_Y r_Z
        # the position of the body in the heliocentric ecliptic reference frame 
        # as SEEN AT THE ASTEROID. (i.e., Just the location)
        # Ast -> Sun vector

        # Consider Margin
        t0 = 5
        t1 = 5.0001
        
        eph = f"eph_{idx+1:03d}.txt"
        eph = os.path.join(outeph, eph)

        with open(eph, "w") as f:
                f.write(f"0 {x_ast} {y_ast} {z_ast}\n")
                f.write(f"{t0} {x_ast} {y_ast} {z_ast}\n")
                f.write(f"{t1} {x_ast} {y_ast} {z_ast}\n")
            
        # Ephemeris file ======================================================


        # Observation file ====================================================
        # --------------
        # Nobs
        # 
        # JD Ndata
        # r_X r_Y r_Z (as for ephemeris file)
        # x y z
        # heliocentric X,Y,Z components of the vector from the asteroid to the Earth 
        # as SEEN AT THE ASTEROID. (i.e., Just the location)
        Nobs = 1
        Ndata = 16

        obs = f"obs_{idx+1:03d}.txt"
        obs = os.path.join(outobs, obs)
        with open(obs, "w") as f:
            f.write(f"{Nobs}\n")
            f.write("\n")
            f.write(f"{t0} {Ndata}\n")
            f.write(f"{x_ast} {y_ast} {z_ast}\n")
            f.write(f"{x_mir} {y_mir} {z_mir}\n")
            # Dummy fluxes
            f.write(f"5 1 1\n")
            f.write(f"6 1 1\n")
            f.write(f"7 1 1\n")
            f.write(f"8 1 1\n")
            f.write(f"9 1 1\n")
            f.write(f"10 1 1\n")
            f.write(f"11 1 1\n")
            f.write(f"12 1 1\n")
            f.write(f"13 1 1\n")
            f.write(f"14 1 1\n")
            f.write(f"15 1 1\n")
            f.write(f"16 1 1\n")
            f.write(f"17 1 1\n")
            f.write(f"18 1 1\n")
            f.write(f"19 1 1\n")
            f.write(f"20 1 1\n")
        # Observation file ====================================================
