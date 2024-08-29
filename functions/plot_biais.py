from pyredlum import pyRedLUM
import matplotlib.pyplot as plt

def plot_bias(pr):

    # Load the data
    error = pr.load_errors()
    nmodes = pr.get_nmodes()
    error_list = error.keys()

    # Get the time for the xaxis
    t = pr.get_t_sim()

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
    pr.save_plot(f"bias_{nmodes}")

# def plot_bias():
#     error = pl.load_errors()
#     nmodes = pl.get_nmodes()
#
#     error_list = error.keys()
#
#     t = get_t_sim()
#
#     fig = plt.figure("Bias",clear=True)
#     for err in error_list:
#         plt.plot(t,error[err], label=err)
#
#     plt.legend(frameon=False)
#     plt.xlabel("Time (s)")
#     plt.ylabel("Normalised Velocity Error")
#     plt.tight_layout()
#     save_plot(f"bias_{nmodes}")

# plot = Plotter(res_folder="/home/fregnault/data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1/ITHACAoutput/Reduced_coeff_4_0.001_100_neglectedPressure_centered")
#

if __name__ == "__main__":

    pr = pyRedLUM(
    res_folder="/home/fregnault/data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1/ITHACAoutput/Reduced_coeff_4_0.001_100_neglectedPressure_centered",
    save_dir="/home/fregnault/data/red_lum_cpp_data/DNS100/ROMDNS-v3.4.1/", verbose=2)

    plot_bias(pr)


