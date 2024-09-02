import matplotlib.pyplot as plt
from pathlib import Path
from param_from_Dict_file import param_from_ITHACADict_file
from glob import glob
import numpy as np
import os
from functools import wraps
import re

def load_once(attr_name):
    """
    function that allows to load the data only once when calling a method that loads the data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check if the attribute already exists in the instance
            if not hasattr(self, attr_name):
                # If it doesn't exist, call the function and set the attribute
                setattr(self, attr_name, func(self, *args, **kwargs))
            # Return the existing or newly set attribute
            return getattr(self, attr_name)
        return wrapper
    return decorator


class pyRedLUM:
    """
    Class that handles the data structure of the output of the RedLUM code
    """

    def __init__(self, res_folder="./",save_dir ="./",verbose=0):
        """
        :param res_folder: Folder containing the results in npy format
        :param save_dir: Path where you should change your
        :param verbose: int that indicates how much information you want about what is going on in pyRedLUM
        """
        self.res_folder = res_folder
        self.save_dir = save_dir
        self.verbose = verbose
        self.sota_type = sota_type

    def info(self,message,verbose):
        """
        Custom print function that handle different level of verbose
        :param message:  Message to be displayed
        :param verbose: Level of verbose
        """
        start_color = "\033[91m"
        end_color = "\033[0m"
        if self.verbose >= verbose:
            print(f"{start_color} |pyRedLUM| {end_color} {message}")

    # ================
    # Getter function
    # ================
    def get_error_list(self):
        """
        Initialize the list of error files expected to be found in self.res_folder
        """
        return ["bias", "globalStd", "minDist", "rmse", "Err0"]

    @load_once("t")
    def get_t_sim(self):
        """
        Compute the time axis (useful for plots)
        """
        mode = self.load_meanModes()
        t = np.array(range(len(mode))) * self.get_dt()
        return t

    @load_once("dt")
    def get_dt(self):
        self.info("Loading dt in controlDict",2)
        param = self.param_from_controlDict_file()
        return param[0]

    @load_once("lambda")
    def load_lambda(self):
        lambdaFile = f"{self.res_folder}/../EigenValuesandVector_{self.get_nmodes()}modes/EigenvaluesNormalized_U.npy"
        eigen = np.load(lambdaFile)
        return eigen

    @load_once("nmodes")
    def get_nmodes(self):
        self.info("Loading nmode",2)
        # List the number of IC modes to get the number of modes
        nmodes = len(glob(f"{self.res_folder}/IC_*.npy"))
        return nmodes

    @load_once("mode_ref")
    def load_modesRef(self):
        self.info("Loading reference mode",2)
        nmode = self.get_nmodes()
        modeRef = np.load(f"{self.res_folder}/../temporalModesSimulation_{nmode}modes/U.npy")
        return modeRef
    # ==========================
    # Functions loading the data
    # ==========================
    @load_once("meanMode")
    def load_meanModes(self):
        self.info("Loading meanMode",2)
        meanMode = np.load(f"{self.res_folder}/mean_temporalModes_U.npy")
        return meanMode

    @load_once("ICs")
    def load_ICs(self):
        IC_list = []
        self.info("Loading ICs",2)
        for i in range(1, self.nmodes + 1):
            IC_list.append(np.load(f"{self.res_folder}/IC_temporalModes_U_{i}.npy"))
        return IC_list

    @load_once("error")
    def load_errors(self):
        """
        Functions that loads npy data related to the error if one is not found then a print is done
        """
        error = dict({})
        error_list = self.get_error_list()

        self.info("Loading Errors",2)

        for err in error_list:
            try:
                error[err] = np.load(f"{self.res_folder}/{err}_temporalModes_U.npy")
            except:
                print(f"{self.res_folder}/{err}_temporalModes_U.npy not found ! skipping it. ")

        return error


    # ===================
    # Helper function
    # ===================

    def param_from_controlDict_file(self):

        # 1) dt_DNS : DNS files saving period (>> DNS time step)
        # 2) t0_DNS : start time for DNS
        # 3) t1_DNS : end time for DNS

        param_file = Path(f"{self.res_folder}/../../system/controlDict")

        if param_file.exists():
            f_param = open(param_file, 'r')
            N_bracket = 0
            while True:
                line = f_param.readline()
                if not line:
                    break
                else:
                    line = line.replace(';', '')  # suppress COMMA
                    line = line.replace('\t', ' ')  # replace TAB by one BLANK
                    line = line.replace('\n', ' ')  # replace RETURN by one BLANK
                    line = re.sub(' +', ' ', line)  # replace multiple BLANKs by a single BLANK
                    line = re.sub(' {', '{', line)  # brackets must be the first word
                    line = re.sub(' }', '}', line)  # brackets must be the first word
                    # => line is now a string with last character=BLANK
                    a = line.split('/');
                    line = a[0];
                    a = line.split(' ')
                    if a[0] == '{':
                        N_bracket = N_bracket + 1
                    if a[0] == '}':
                        N_bracket = N_bracket - 1
                    if N_bracket == 0:
                        if re.search('writeInterval ', line):
                            if str(a[0]) == 'writeInterval':
                                dt_DNS = float(a[-2])
                        if re.search('startTime ', line):
                            if str(a[0]) == 'startTime':
                                t0_DNS = float(a[-2])
                        if re.search('endTime ', line):
                            if str(a[0]) == 'endTime':
                                t1_DNS = float(a[-2])

        return dt_DNS, t0_DNS, t1_DNS

    def save_plot(self, name):
        """
        Function that saves the current active plot in png and pdf format
        :param name: name of the saved file
        :return:
        """
        # Checking that plot directory exists
        os.makedirs(f"{self.save_dir}/plots", exist_ok=True)
        os.makedirs(f"{self.save_dir}/plots/pdf", exist_ok=True)

        self.info(f"Saving plots to {self.save_dir}",1)

        plt.savefig(f"{self.save_dir}/plots/{name}")
        plt.savefig(f"{self.save_dir}/plots/pdf/{name}.pdf")



    def get_size_mode_mozaic(self,nmodes):
        """
        :param nmodes: Number of modes for the given plots
        :return: number of columns and rows such that the grid looks more like a square
        """
        ncol = int(np.ceil(np.sqrt(nmodes)))
        nrow = int(np.ceil(nmodes / ncol))
        return nrow, ncol

    def finalize_plot(self,fig):
        pass



