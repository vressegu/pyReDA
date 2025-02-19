from pyredlum import pyRedLUM
import matplotlib.pyplot as plt

def plot_bias(case,name_out=None):

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
    case.save_plot(name_save)

def compare_bias(case1, case2, name_out=None,error_list=[]):

    # Load the data
    error1 = case1.load_errors()
    nmodes1 = case1.get_nmodes()

    # Get the list of error to plot
    if len(error_list) == 0:
        error_list = error1.keys()
    print(error_list)
    error2  = case2.load_errors()
    nmodes2 = case2.get_nmodes()

    if nmodes2 != nmodes1:
        raise ValueError(f"Not the same number of modes for case 1 ({nmodes1}) and 2 ({nmodes2})")

    # Get the time for the xaxis
    t = case1.get_t_sim()

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
            error1[err],
            color=this_color,
            label=err
        )
        ax.plot(
            t,
            error2[err],
            color=this_color,
            linestyle="--",
            # label=err + f"{sota.sota_type}SOTA"
        )

    ax.legend(frameon=False)

    # Draw line just to add it to the legend
    fake_line_case, = axl.plot([], [], color="black", label=case1.name)
    fake_line_sota, = axl.plot([], [], color="black", linestyle="--", label=case2.name)
    legend = axl.legend(frameon=False,loc="center",ncol=2)


    #

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Normalised Velocity Error")
    fig.tight_layout()

    if name_out:
        name_save = f"{name_out}_{nmodes1}"
    else:
        name_save = f"compare_bias_{case1.name}-{case2.name}_{nmodes1}"

    print("Saving : ",name_save)
    case2.save_plot(name_save)

if __name__ == "__main__":

    # working_dir = "/home/fregnault/Data/red_lum_cpp_data/DNS300/ROMDNS-v3.4.1"
    working_dir = "C:/Users/florian.regnault/Documents/data/L2/"
    case = pyRedLUM(
        res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_2_0.001_100_neglectedPressure_centered",
        # res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_4_0.001_100_neglectedPressure_centered",
        save_dir=working_dir,
        name = "NoSto"
    )

    sota = pyRedLUM(
        res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_2_D-SOTA",
        # res_folder=f"{working_dir}/ITHACAoutput/Sto_Reduced_coeff_2_0.001_100_neglectedPressure_centered",
        save_dir=working_dir,
        sota_type="D",
        name = "SOTA"
    )


    compare_bias(case,sota)

    plot_bias(sota,f"bias_{sota.sota_type}SOTA")


