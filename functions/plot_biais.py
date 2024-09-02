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

    # plt.ylim(0,1)
    plt.legend(frameon=False)
    plt.xlabel("Time (s)")
    plt.ylabel("Normalised Velocity Error")
    plt.tight_layout()
    case.save_plot(f"{name_out}_{nmodes}")

def compare_bias_sota(case, sota,name_out):

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

    fig = plt.figure("Bias", clear=True)
    for err in error_list:


        this_color = next(cycle_color)
        plt.plot(
            t,
            error[err],
            color=this_color,
            label=err
        )
        plt.plot(
            t,
            error_sota[err],
            color=this_color,
            linestyle="--",
            # label=err + f"{sota.sota_type}SOTA"
        )

    # plt.ylim(0,1)
    plt.legend(frameon=False)
    plt.xlabel("Time (s)")
    plt.ylabel("Normalised Velocity Error")
    plt.tight_layout()
    sota.save_plot(f"{name_out}_{nmodes}")

if __name__ == "__main__":

    working_dir = "/home/fregnault/data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1"
    case = pyRedLUM(
        res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_4_0.001_100_neglectedPressure_centered",
        save_dir=working_dir,
    )

    sota = pyRedLUM(
        res_folder=f"{working_dir}/ITHACAoutput/Reduced_coeff_4_DSOTA",
        save_dir=working_dir,
        sota_type="D"
    )


    compare_bias_sota(case,sota,f"compare_bias_{sota.sota_type}SOTA")

    plot_bias(sota,f"bias_{sota.sota_type}SOTA")


