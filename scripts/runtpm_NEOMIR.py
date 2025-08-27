#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser as ap
import numpy as np
import subprocess, os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager


def run_simulation(i, rotP_hr, lam, beta, Gamma, obs, eph, obj, spindir, label):

    spinf = f"spin{i:03d}_TI{Gamma}_{label}.txt"
    with open(f'{spindir}/{spinf}', 'wt') as f:
        print(lam, beta, rotP_hr, 0, 0, file=f)
    
    # emissivity
    eps = 0.9
    D_km = 1.0
    BondA = 0.039

    # Assume no craters (ca = 0, cr = 0)
    cmd = f'echo {obj} {eph} {eps} {Gamma} {BondA} 0 0 | runtpm -o {obs} -S {spindir}/{spinf} -s {D_km} | grep "f>"'
    p = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    comm = p.communicate()
    output = comm[0].decode('ascii').strip()

    if not output:
        raise ValueError(f"Command produced no output: {cmd}")
    
    split_output = output.split()
    if len(split_output) <= 7:
        raise IndexError(f"Unexpected command output: {output}")
    
    # Fluxes in microJy
    # The first flux is "7"
    # 7 to 20 micron
    #with open("test", "w") as f:
    #    f.writelines(split_output)

    if Gamma == 0:
        fluxes = " ".join(f"{float(split_output[7 + (i - 5) * 10]) * 1e6}" for i in range(5, 21))
    else:
        fluxes = " ".join(f"{float(split_output[7 + (i - 5) * 11]) * 1e6}" for i in range(5, 21))
    # Extract locations of asteroids from obsfile
    with open(obs) as f_obs: 
        lines = f_obs.readlines()
        xyz1 = lines[3]
        x1, y1, z1 = xyz1.split()
        xyz2 = lines[4]
        x2, y2, z2 = xyz2.split()

    log_entry = f"{i} {D_km} {lam} {beta} {x1} {y1} {z1} {x2} {y2} {z2} {fluxes}\n"
    return log_entry  # Return the formatted log entry


def main_tpm(obs, eph, obj, N, M, rotP_hr, Gamma_values, label, spindir, outdir):
    # Make the (lam, beta) 
    # Assume N x M = 300
    seed = 0
    np.random.seed(seed)

    # Generate random values for lam, beta
    lam_list = np.random.uniform(0, 360, N*M)
    beta_list = np.random.uniform(-90, 90, N*M)

    # Initialize manager for shared list
    with Manager() as manager:
        for Gamma in Gamma_values:  # Iterate over each Gamma value
            print(f"Running simulations for Gamma = {Gamma}...")
            results = manager.list()  # Create a new list for each Gamma value
            for cycle in range(M):
                lam_list_M, beta_list_M = lam_list[cycle*N:(cycle+1)*N], beta_list[cycle*N:(cycle+1)*N]
                with ProcessPoolExecutor(max_workers=N) as executor:
                    futures = [executor.submit(run_simulation, i, rotP_hr, lam_list_M[i], beta_list_M[i], Gamma, obs, eph, obj, spindir, label) for i in range(N)]
                    cycle_results = [f.result() for f in futures]
                    results.extend(cycle_results)  # Append the results for this cycle

                print(f"Cycle {cycle + 1}/{M} for Gamma = {Gamma} completed.")
            
            # Write all results for the current Gamma value to the file
            header = "idx D_km lam beta x1 y1 z1 x2 y2 z2 flux5 flux6 flux7 flux8 flux9 flux10 flux11 flux12 flux13 flux14 flux15 flux16 flux17 flux18 flux19 flux20\n"
            with open(f'{outdir}/TI{Gamma}_res_{label}.txt', "w") as f:
                f.write(header)
                f.writelines(results)  # Write all results at once

if __name__ == "__main__":
    parser = ap(description="Run TPM for NEOMIR project.")
    parser.add_argument(
        "--eph", type=str, nargs="*", default="eph.txt",
        help="Ephem files")
    parser.add_argument(
        "--obs", type=str, nargs="*", default="obs.txt",
        help="Obs files")
    parser.add_argument(
        "--obj", type=str, default="obj.txt",
        help="Obj file")
    parser.add_argument(
        "--gamma", type=int, nargs="*", default=[0, 50, 150, 300, 500, 1000],
        help="Thermal inertia")
    parser.add_argument(
        "--rotP_hr", type=float, default=0.0968,
        help="Rotation period in hour")
    parser.add_argument(
        "--spindir", type=str, default="spinfile",
        help="Directory for output file")
    parser.add_argument(
        "--outdir", type=str, default="tpmresult",
        help="Directory for output file")
    args = parser.parse_args()
   
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    spindir = args.spindir
    os.makedirs(spindir, exist_ok=True)
    
    N_obs, N_eph = len(args.obs), len(args.eph)
    assert N_obs == N_eph, "Check the input files."

    # Do tpm
    N = 30  # Number of parallel processes
    M = 10  # Number of cycles per Gamma value
    for n in range(N_obs):
        obs, eph = args.obs[n], args.eph[n]
        label = f"{n+1:03d}"
        main_tpm(obs, eph, args.obj, N, M, args.rotP_hr, args.gamma, label, spindir, outdir)
