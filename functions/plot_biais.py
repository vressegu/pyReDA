from pyredlum import pyRedLUM
import matplotlib.pyplot as plt

def plot_bias(case,name_out):

    # Load the data
    error = case.load_errors()
    nmodes = case.get_nmodes()
    error_list = error.keys()

    # Get the time for the xaxis
    t = case.get_t_sim()

    fig = plt.figure("Bias", clear=True)
    for err in error_list:
        plt.plot(
            t,
            error[err],
            label=err
            )

    # Check if an output name has been decided upon
    if name_out:
        name_save = f"{name_out}_{nmodes}"
    else:
        name_save = f"bias_{case.name}_{nmodes}"

    # plt.ylim(0,1)
    plt.legend(frameon=False)
    plt.xlabel("Time (s)")
    plt.ylabel("Normalised Velocity Error")
    plt.tight_layout()
    case.save_plot(f"{name_out}_{nmodes}")

def compare_bias_sota(case, sota,name_out=None):

    # Load the data
    error = case.load_errors()
    nmodes = case.get_nmodes()
    error_list = error.keys()

    error_sota  = sota.load_errors()
    nmodes_sota = sota.get_nmodes()

    try:
        nmodes_sota == nmodes
    except:
        raise ValueError(f"Not the same number of modes for case ({nmodes}) et sota ({nmodes_sota})")

    # Get the time for the xaxis
    t = case.get_t_sim()

    # Setting up an iterator to have the same color for each error, we then specify dashed lines for the SOTA
    cycle_color = iter(["C0","C1","C2","C3","C4"])

    fig = plt.figure("Compare Bias", clear=True,figsize=(16,9))

    gs = plt.GridSpec(2,1,height_ratios=[1,30])

    ax = fig.add_subplot(gs[1,0])
    axl = fig.add_subplot(gs[0,0])
    axl.axis("off")

    for err in error_list:

        this_color = next(cycle_color)
        ax.plot(
            t,
            error[err],
            color=this_color,
            label=err
        )
        ax.plot(
            t,
            error_sota[err],
            color=this_color,
            linestyle="--",
            # label=err + f"{sota.sota_type}SOTA"
        )

    ax.legend(frameon=False)

    # plt.ylim(0,1)


    fake_line_case, = axl.plot([],[],color="black",label=case.name)
    fake_line_sota, = axl.plot([],[],color="black",linestyle="--",label=sota.name)
    legend = axl.legend(frameon=False,loc="center",ncol=2)


    #

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Normalised Velocity Error")
    fig.tight_layout()

    if name_out:
        name_save = f"{name_out}_{nmodes}"
    else:
        name_save = f"compare_{case.name}-_{sota.name}_{nmodes}"

    sota.save_plot(name_save)

if __name__ == "__main__":

    working_dir = "/home/fregnault/data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1"
    case = pyRedLUM(
        res_folder=f"{working_dir}/ITHACAoutput/Sto_Reduced_coeff_4_0.001_100_fullOrderPressure_centered",
        save_dir=working_dir,
        name = "Sto"
    )

    sota = pyRedLUM(
        res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_4_D-SOTA",
        # res_folder=f"{working_dir}/ITHACAoutput/Sto_Reduced_coeff_4_0.001_100_neglectedPressure_centered",
        save_dir=working_dir,
        sota_type="D",
        name = "D-SOTA"
    )


    compare_bias_sota(case,sota)

    plot_bias(sota,f"bias_{sota.sota_type}SOTA")


