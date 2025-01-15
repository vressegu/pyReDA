#! /home/fregnault/.conda/envs/mecaflu2/bin/python
import os
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from param_from_Dict_file import param_from_controlDict_file,param_from_ITHACADict_file
# from convert_Cmat_to_python_Topos_FakePIV import define_folder_results
from pathlib import Path
# from collections import namedtuple
# from convert_Cmat_to_python_Topos_FakePIV import load_errors
# from param_from_info_txt_file import main_globalParam_from_info_txt_file

##
def get_mode_folder():
    folders = glob("ITHACAoutput/*")

    folder_found = False
    for fol in folders:
        if "Reduced_coeff" in fol:
            mode_folder = fol
            folder_found = True

    if not folder_found:
        raise ValueError("Mode Folder not found")

    return mode_folder

def get_t_sim():

    dt = get_dt()
    modes, ICs = load_modes()

    t = np.array(range(len(modes[:, 0]))) * dt

    return t


def get_nmodes():
    mode_folder = get_mode_folder()

    # List the number of IC modes to get the number of modes
    nmodes = len(glob(f"{mode_folder}/IC_*.npy"))

    return nmodes

def get_dt():
    controlDict = Path("system/controlDict")
    param = param_from_controlDict_file(controlDict)
    return param[0]

def get_error_list():
    return ["bias", "globalStd", "minDist", "rmse", "Err0"]

def load_modes():
    mode_folder = get_mode_folder()
    modes = np.load(f"{mode_folder}/mean_temporalModes_U.npy")
    nmode = get_nmodes()

    IC_list = []
    for i in range(1,nmode+1):
        IC_list.append(np.load(f"{mode_folder}/IC_temporalModes_U_{i}.npy"))

    return modes, IC_list


def save_plot(name):

    # Checking that plot directory exists
    os.makedirs("plots", exist_ok=True)

    plt.savefig(f"plots/{name}.png")

    os.makedirs("plots/pdf", exist_ok=True)
    plt.savefig(f"plots/pdf/{name}.pdf")


def my_load_errors():
    mode_folder = get_mode_folder()
    error_list = get_error_list()
    error = dict({})
    for err in error_list:
        try:
            error[err] = np.load(f"{mode_folder}/{err}_temporalModes_U.npy")
        except:
            print(f"{mode_folder}/{err}_temporalModes_U.npy not found ! Skipping it. ")

    return error


def get_size_mozaic(nmodes):

    ncol = int(np.ceil(np.sqrt(nmodes)))
    nrow = int(np.ceil(nmodes / ncol))

    return nrow,ncol

def plot_bias():
    error = my_load_errors()
    nmodes = get_nmodes()

    error_list = error.keys()

    t = get_t_sim()

    fig = plt.figure("Bias",clear=True)
    for err in error_list:
        plt.plot(t,error[err], label=err)

    plt.legend(frameon=False)
    plt.xlabel("Time (s)")
    plt.ylabel("Normalised Velocity Error")
    plt.tight_layout()
    save_plot(f"bias_{nmodes}")

def plot_all_modes():

    nmodes = get_nmodes()
    modes, ICs = load_modes()

    dt = get_dt()
    t = np.array(range(len(modes[:, 0]))) * dt

    nrow, ncol = get_size_mozaic(nmodes)

    width_of_one_plot = 6
    height_of_one_plot = 4

    fig = plt.figure("All modes",figsize=(width_of_one_plot*nrow,height_of_one_plot*ncol))
    gs = plt.GridSpec(nrow, ncol)
    axs = []
    for i in range(nrow):
        for j in range(ncol):
            axs.append(fig.add_subplot(gs[i, j]))

    # Plotting the data
    for n in range(nmodes):
        to_plot = modes[:, n]
        # error_to_plot = ICs[:, n] / 2
        axs[n].plot(t,modes[:, n])
        axs[n].fill_between(t, ICs[n][:,0], ICs[n][:,1], alpha=0.5,color="orange")

    # Cleaning extra axes
    for n in range(nmodes,nrow*ncol):
        fig.delaxes(axs[n])

    # Aesthetic things
    for n in range(nmodes):
        ss = axs[n].get_subplotspec()
        axs[n].set_title(f"Mode {n+1}")
        if ss.is_last_row():
            axs[n].set_xlabel("Time (s)")
        else:
            axs[n].set_xticks([])
        if ss.is_first_col():
            axs[n].set_ylabel("Mode amplitude")
        else:
            axs[n].set_yticks([])


    plt.tight_layout()
    save_plot(f"modes_{nmodes}.png")
##
if __name__ == "__main__":
    plt.ion()
    plot_bias()
    # plot_all_modes()


    # param_file = Path("system/ITHACAdict")
    # controlDict_file = Path("system/controlDict")
    # runinfo_file = Path("/home/fregnault/pyReDA/run_info.txt")
    # PARAM = dict({})
    # PARAM = dotdict(PARAM)
    #
    # type_data_C, bool_PFD, code_DATA_from_matlab, code_ROM_from_matlab, \
    #     code_Assimilation, code_load_run, init_centred_on_ref, \
    #     redlumcpp_code_version, PATH_openfoam_data, \
    #     beta_2, beta_3, xObs, yObs,n_modes,hilbert_space = main_globalParam_from_info_txt_file(runinfo_file)
    #
    #
    # t0_learningBase, t1_learningBase, t0_testBase, t1_testBase, n_simu, inflatNut, interpFieldCenteredOrNot, HypRedSto, DEIMInterpolatedField,n_particles = param_from_ITHACADict_file(
    #     param_file)
    #
    # Re = type_data_C[-4:]
    # print(Re)
    # if type_data_C[0:3] == "LES":
    #     bool_DEIM = True
    # else:
    #     bool_DEIM = False
    #
    # bool_useHypRedSto = bool(HypRedSto)
    # bool_interpFieldCenteredOrNot = bool(interpFieldCenteredOrNot)
    #
    # dt_DNS, t0_DNS, t1_DNS = param_from_controlDict_file(controlDict_file)
    #
    # adv_corrected = True
    #
    #
    #
    # PARAM["code_Assimilation"] = code_Assimilation
    # PARAM["adv_corrected"] = adv_corrected
    # PARAM["nb_modes"] = n_modes
    # PARAM["PATH_ROM"] = Path("/home/fregnault/data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1/ITHACAoutput")
    # print("Path not taken into account correctly")
    # PARAM["n_simu"] = n_simu
    # PARAM["dt_DNS"] = dt_DNS
    # PARAM.HilbertSpace = hilbert_space
    # PARAM.temporalScheme = "euler"
    # PARAM.t0_learningBase = t0_learningBase
    # PARAM.t1_learningBase = t1_learningBase
    # PARAM.t0_testBase = t0_testBase
    # PARAM.t1_testBase = t1_testBase
    #
    # error = my_load_errors()
    #
    # folder, file_format = define_folder_results(PARAM, n_simu, n_particles, bool_PFD, bool_DEIM, inflatNut,  bool_interpFieldCenteredOrNot, bool_useHypRedSto, DEIMInterpolatedField)
    #
    # print("here")
    #
    # bias, rmse, minDist = load_errors(PARAM, n_simu, n_particles, bool_PFD, \
    #                                   bool_DEIM, inflatNut, bool_interpFieldCenteredOrNot, bool_useHypRedSto,
    #                                   DEIMInterpolatedField)
    # print("done")
##
