import numpy as np
from pyredlum import pyRedLUM
import matplotlib as mpl
import matplotlib.pyplot as plt

# import mplcyberpunk
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["#000000", "#E69F00", "#56B4E9","#009E73","#F0E442","#0072B2","#D55E00","CC79A7"])
# plt.style.use("cyberpunk")

def setup_legend(axl, handle, labels):
    """
    :param axl: ax that contains the legend
    :param handle: Handles  of the plot to put in the legend
    :param labels: Labels of the plot to put in the legend
    :return: Function that do a "fake" plot in order to place the legend in a new ax
    """

    axl.legend(
        handle,
        labels,
        frameon=False,
        ncol=len(handle),
        loc="center"
    )
    axl.axis("off")


def plot_all_modes(case,name_out=False):

    color = dict({"U":"red",
                  "p":"blue"})

    title = dict({"U":"Velocity mode",
    "p":"Pressure modes"})

    for dtype in ["U","p"]:

        if (dtype == "p") & (not case.has_p_modes):

            continue

        if dtype == "U" :
            nmodes = case.get_nmodes()
            meanModes = case.load_meanModes()
            modesRef = case.load_modesRef()
            ICs = case.load_ICs()

        elif dtype == "p":
            print("here")
            nmodes = case.get_nmodes_p()
            meanModes = case.load_meanModes_p()
            modesRef = case.load_modesRef_p()
            ICs = case.load_ICs_p()
        else:
            raise ValueError("Wrong type of dtype")


        dt = case.get_dt()
        t = case.get_t_sim()


        nrow, ncol = case.get_size_mode_mozaic(nmodes)

        width_of_one_plot = 6
        height_of_one_plot = 4

        fig = plt.figure(
            "All modes",
            figsize=(width_of_one_plot*nrow,height_of_one_plot*ncol),
            clear=True
        )

        height_ratios = nrow * [1]

        # Adding one extra row for the legend
        nrow += 1

        height_ratios.insert(0,0.1)

        gs = plt.GridSpec(
            nrow,
            ncol,
            height_ratios=height_ratios
        )

        # Axes containing the data
        axs = []
        for i in range(1,nrow):
            for j in range(ncol):
                axs.append(fig.add_subplot(gs[i, j]))

        # Ax containing the legend taking the full first line
        axl = fig.add_subplot(gs[0,:])

        # Plotting the data
        for n in range(nmodes):
            axs[n].plot(
                t,
                modesRef[:,n],
                color=color[dtype],
                linestyle="--",
                label="Reference"
            )

            axs[n].plot(
                t,
                meanModes[:, n],
                color="green",
                label="Mean mode"
            )

            axs[n].fill_between(
                t,
                ICs[n][:,0],
                ICs[n][:,1],
                alpha=0.5,
                color="lightgreen",
                linewidth=0,
                label="Confidence Interval"
            )

        # Cleaning extra axes
        for n in range(nmodes,(nrow-1)*ncol):
            axs[n].axis("off")

        # Aesthetic things

        handles,labels = axs[1].get_legend_handles_labels()
        setup_legend(axl,handles,labels)

        for n in range(nmodes):
            ss = axs[n].get_subplotspec()

            # mplcyberpunk.make_lines_glow(axs[n])
            # Title
            axs[n].set_title(f"Mode {n+1}")

            # Xlabel
            if ss.is_last_row():
                axs[n].set_xlabel(
                    "Time (s)",
                    fontsize=14
                )
            else:
                # Removing xtick labels for axes that are not at the bottom
                axs[n].set_xticklabels([])

            # List of ax on the left of the plot
            ax_left = []

            # Ylabel
            if ss.is_first_col():
                axs[n].set_ylabel(
                    "Mode amplitude",
                    fontsize=14
                )
                # Add ax to the list for aligning ylabel
                ax_left.append(axs[n])
            # else:
            #     axs[n].set_yticks([])


            # Ylim
            # Use whatever formula that works to have nice

            margin = 0.5 # Taking [margin x 100] % above and below the max
            axs[n].set_ylim(
                -np.max(meanModes[:, n]) * (1 + margin),
                np.max(meanModes[:, n]) * (1 + margin)
            )

            # Removing unnecessary spines
            axs[n].spines["top"].set_visible(False)
            axs[n].spines["right"].set_visible(False)

        fig.align_ylabels(ax_left)

        fig.suptitle(title[dtype])

        plt.tight_layout()
        if name_out:
            name_save = f"{dtype}_{name_out}_{nmodes}"
        else:
            name_save = f"{dtype}_modes_{case.name}_{nmodes}"

        case.save_plot(name_save)

def compare_SOTA_modes(case,sota):

    nmodes = case.get_nmodes()
    meanModes = case.load_meanModes()
    modesRef = case.load_modesRef()
    ICs = case.load_ICs()
    eigen = case.load_lambda()

    nmodes_sota = sota.get_nmodes()
    meanModes_sota = sota.load_meanModes()
    ICs_sota = sota.load_ICs()

    dt = case.get_dt()
    t = case.get_t_sim()


    nrow, ncol = case.get_size_mode_mozaic(nmodes)

    width_of_one_plot = 14
    height_of_one_plot = 4

    fig = plt.figure(
        "Compare modes",
        figsize=(width_of_one_plot*nrow,height_of_one_plot*ncol),
        clear=True
    )

    height_ratios = nrow * [1]

    # Adding one extra row for the legend
    nrow += 1

    height_ratios.insert(0,0.2)

    gs = plt.GridSpec(
        nrow,
        ncol,
        height_ratios=height_ratios
    )

    # Axes containing the data
    axs = []
    for i in range(1,nrow):
        for j in range(ncol):
            axs.append(fig.add_subplot(gs[i, j]))

    # Ax containing the legend taking the full first line
    axl = fig.add_subplot(gs[0,:])

    # Plotting the data
    for n in range(nmodes):
        axs[n].plot(
            t,
            modesRef[:,n],
            color="red",
            linestyle="--",
            label="Reference"
        )

        axs[n].plot(
            t,
            meanModes[:, n],
            color="green",
            label=f"Mean mode {case.name}"
        )

        axs[n].fill_between(
            t,
            ICs[n][:,0],
            ICs[n][:,1],
            alpha=0.5,
            color="lightgreen",
            linewidth=0,
            label=f"Confidence Interval {case.name}"
        )

        axs[n].plot(
            t,
            meanModes_sota[:, n],
            color="blue",
            label=f"{sota.name} Mean mode",
            zorder=-1
        )

        axs[n].fill_between(
            t,
            ICs_sota[n][:,0],
            ICs_sota[n][:,1],
            alpha=0.5,
            color="lightblue",
            linewidth=0,
            zorder=-2,
            label=f"{sota.name} Confidence Interval"
        )

    # Cleaning extra axes
    for n in range(nmodes,(nrow-1)*ncol):
        axs[n].axis("off")

    # Aesthetic things
    handles,labels = axs[1].get_legend_handles_labels()
    setup_legend(axl,handles,labels )

    for n in range(nmodes):
        ss = axs[n].get_subplotspec()

        # mplcyberpunk.make_lines_glow(axs[n])
        # Title
        axs[n].set_title(f"Mode {n+1}")

        # Xlabel
        if ss.is_last_row():
            axs[n].set_xlabel(
                "Time (s)",
                fontsize=14
            )
        else:
            # Removing xtick labels for axes that are not at the bottom
            axs[n].set_xticklabels([])

        # List of ax on the left of the plot
        ax_left = []

        # Ylabel
        if ss.is_first_col():
            axs[n].set_ylabel(
                "Mode amplitude",
                fontsize=14
            )
            # Add ax to the list for aligning ylabel
            ax_left.append(axs[n])
        # else:
        #     axs[n].set_yticks([])


        # Ylim
        # value_ylim = eigen[n]
        # axs[n].set_ylim(-value_ylim,value_ylim)
        margin = 0.5 # Taking marginx100 % above and below the max
        axs[n].set_ylim(
            -np.max(meanModes[:, n]) * (1 + margin),
            np.max(meanModes[:, n]) * (1 + margin)
            )

            # Removing unnecessary spines
        axs[n].spines["top"].set_visible(False)
        axs[n].spines["right"].set_visible(False)
        axs[n].set_xlim(0,50)

    fig.align_ylabels(ax_left)
    fig.suptitle("Velocity Mode")
    plt.tight_layout()
    case.save_plot(f"compare_{case.name}-{sota.name}_{nmodes}")

if __name__ == "__main__":

    working_dir = "/home/fregnault/Data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1"
    case = pyRedLUM(
        res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_2_0.001_100_neglectedPressure_centered",
        save_dir=working_dir,
        name = "NoSto"
    )

    sota = pyRedLUM(
        res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_2_D-SOTA",
        save_dir=working_dir,
        sota_type="D",
        name = "SOTA"
    )

    # sota = pyRedLUM(
    #     res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_2_D-SOTA",
    #     # res_folder=f"{working_dir}/ITHACAoutput/Ref_Reduced_coeff_2_0.001_100_neglectedPressure_centered",
    #     save_dir=working_dir,
    #     sota_type="D",
    #     name = "SOTA"
    # )

    plot_all_modes(case)
    compare_SOTA_modes(sota,case)
