#!/usr/bin/env python3
import matplotlib
import argparse

from plot_modes_bp import plot_all_modes

matplotlib.use("Agg")
from pyredlum import pyRedLUM
from plot_bias_bp import plot_bias
import plot_modes_bp
import os

##
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="redlum-plot",
        description="redlum-plot is a script that is using the pyRedLUM framework allowing to quickly produce plots of the\
        RedLUM algorithm"
    )
    parser.add_argument("-v","--verbose",type=int,default=0,help="increase output verbosity")
    parser.add_argument("-n","--name",type=str,default=None,help="Specify name used when saving plots")
    working_dir = os.getcwd()
    plotting_dir = f"{working_dir}"

    # Getting arguments stored in parser
    args = parser.parse_args()
    verbose = args.verbose
    name = args.name

    if name is None:
        name = os.getcwd().split("/")[-1]

    case = pyRedLUM(
        res_folder=working_dir,
        save_dir=plotting_dir,
        name = name,
        verbose=verbose
    )

    plot_bias(case)
    plot_all_modes(case)
##