from plot_bt_dB_MCMC_varying_error_NoEV import height
from pyredlum import pyRedLUM
import matplotlib.pyplot as plt
from icecream import ic
import tuftelike as tf

def plot_all_modes(pr):

    def setup_legend(axl,handle,labels):
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


    nmodes = pr.get_nmodes()
    meanModes = pr.load_meanModes()
    modesRef = pr.load_modesRef()
    ICs = pr.load_ICs()
    eigen = pr.load_lambda()

    print(eigen)

    dt = pr.get_dt()
    t = pr.get_t_sim()


    nrow, ncol = pr.get_size_mode_mozaic(nmodes)

    width_of_one_plot = 6
    height_of_one_plot = 4

    fig = plt.figure(
        "All modes",
        figsize=(width_of_one_plot*nrow,height_of_one_plot*ncol)
    )

    height_ratios = nrow * [1]

    # Adding one extra row for the legend
    nrow += 1

    height_ratios.insert(0,0.1)
    ic(nrow,ncol)

    gs = plt.GridSpec(
        nrow,
        ncol,
        height_ratios=height_ratios
    )

    # Axes containing the data
    axs = []
    for i in range(1,nrow):
        for j in range(ncol):
            ic(i,j)
            axs.append(fig.add_subplot(gs[i, j]))

    # Ax containing the legend taking the full first line
    axl = fig.add_subplot(gs[0,:])

    # Plotting the data
    for n in range(nmodes):
        axs[n].plot(
            t,
            modesRef[:,n],
            color="black",
            linestyle="--",
            label="Reference"
        )

        axs[n].plot(
            t,
            meanModes[:, n],
            label="Mean mode"
        )

        axs[n].fill_between(
            t,
            ICs[n][:,0],
            ICs[n][:,1],
            alpha=0.5,
            color="orange",
            label="Confidence Interval"
        )

    # Cleaning extra axes
    for n in range(nmodes,(nrow-1)*ncol):
        fig.delaxes(axs[n])

    # Aesthetic things

    handles,labels = axs[1].get_legend_handles_labels()
    setup_legend(axl,handles,labels)

    for n in range(nmodes):
        ss = axs[n].get_subplotspec()
        axs[n].set_title(f"Mode {n+1}")
        if ss.is_last_row():
            axs[n].set_xlabel(
                "Time (s)",
                fontsize=14
            )
        else:
            axs[n].set_xticklabels([])
        if ss.is_first_col():
            axs[n].set_ylabel(
                "Mode amplitude",
                fontsize=14
            )
        # else:
        #     axs[n].set_yticks([])

        axs[n].spines["top"].set_visible(False)
        axs[n].spines["right"].set_visible(False)

    plt.tight_layout()
    pr.save_plot(f"modes_{nmodes}.png")


if __name__ == "__main__":
    pr = pyRedLUM(
        res_folder="/home/fregnault/data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1/ITHACAoutput/Reduced_coeff_4_0.001_100_neglectedPressure_centered",
        save_dir="/home/fregnault/data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1/", verbose=1)


    plot_all_modes(pr)
