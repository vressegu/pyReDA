import matplotlib as mpl
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["#000000", "#E69F00", "#56B4E9","#009E73","#0072B2","#D55E00","CC79A7","#F0E442"])
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

    def __init__(self, res_folder="./",save_dir ="./",verbose=0,sota_type=None,name=None):
        """
        :param res_folder: Folder containing the results in npy format
        :param save_dir: Path where you should change your
        :param verbose: int that indicates how much information you want about what is going on in pyRedLUM
        """
        self.res_folder = res_folder
        self.save_dir = save_dir
        self.verbose = verbose
        self.sota_type = sota_type
        self.name = name

        self.check_pressure_modes()

        for path_dir in [res_folder,save_dir]:
            if not os.path.exists(path_dir):
                raise ValueError(f"{path_dir} does not exists")


    def check_pressure_modes(self):
        """
        Use the case name to know if we expect to see pressure modes
        """

        if "reducedOrderPressure" in self.name:
            self.has_p_modes = True
            self.info("Case has pressure modes",2)
        else:
            self.info("Case has no pressure modes",2)
            self.has_p_modes = False

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

    @load_once("nSnapshots")
    def get_nSnapshots(self):

        param = self.param_from_controlDict_file()

        # t0_learningBase, t1_learningBase, t0_testBase, t1_testBase, n_simu, inflatNut, interpFieldCenteredOrNot, HypRedSto, DEIMInterpolatedField, n_particles
        ithacadict = self.param_from_ITHACADict_file()

        dt = param[0]
        t0 = ithacadict[0]
        t1 = ithacadict[1]

        n = (t1 - t0) / dt

        return n

    @load_once("lambda")
    def load_lambda(self):
        lambdaFile = f"{self.res_folder}/../EigenValuesandVector_{self.get_nmodes()}modes/Eigenvalues_U.npy"
        eigen = np.load(lambdaFile)
        lambdaFile2 = f"{self.res_folder}/../EigenValuesandVector_{self.get_nmodes()}modes/EigenvectorLambda_U.npy"
        n = self.get_nSnapshots() # Normalize by the number of snapshots
        lb = np.load(lambdaFile2) / np.sqrt(n)
        eigen_norm = eigen / n
        return lb

    @load_once("nmodes")
    def get_nmodes(self):
        self.info("Loading nmode",2)
        # List the number of IC modes of velocity to get the number of modes
        nmodes = len(glob(f"{self.res_folder}/IC_temporalModes_U*.npy"))
        return nmodes

    @load_once("nmodesp")
    def get_nmodes_p(self):
        self.info("Loading nmode for pressure",2)
        # List the number of IC modes of velocity to get the number of modes
        nmodes = len(glob(f"{self.res_folder}/IC_temporalModes_p*.npy"))
        return nmodes

    @load_once("mode_ref")
    def load_modesRef(self):
        self.info("Loading reference mode",2)
        nmode = self.get_nmodes()
        modeRef = np.load(f"{self.res_folder}/../temporalModesSimulation_{nmode}modes/U.npy")
        return modeRef

    @load_once("mode_refp")
    def load_modesRef_p(self):
        self.info("Loading p reference mode",2)
        nmode = self.get_nmodes_p()
        modeRef = np.load(f"{self.res_folder}/../temporalModesSimulation_centered_{nmode}modes/p.npy")
        return modeRef

    # ==========================
    # Functions loading the data
    # ==========================
    @load_once("meanMode")
    def load_meanModes(self):
        self.info("Loading meanMode",2)
        meanMode = np.load(f"{self.res_folder}/mean_temporalModes_U.npy")
        return meanMode

    @load_once("meanModep")
    def load_meanModes_p(self):
        self.info("Loading meanMode",2)
        meanMode = np.load(f"{self.res_folder}/mean_temporalModes_p.npy")
        return meanMode

    @load_once("ICs")
    def load_ICs(self):
        IC_list = []
        self.info("Loading ICs",2)
        for i in range(1, self.nmodes + 1):
            IC_list.append(np.load(f"{self.res_folder}/IC_temporalModes_U_{i}.npy"))
        return IC_list

    @load_once("ICsp")
    def load_ICs_p(self):
        IC_list = []
        self.info("Loading ICs",2)
        for i in range(1, self.nmodes + 1):
            IC_list.append(np.load(f"{self.res_folder}/IC_temporalModes_p_{i}.npy"))
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

    def param_from_ITHACADict_file(self):

        # 1) t0_learningBase : initial time for learning basis
        # 2) t1_learningBase : Final time for learning basis
        # 3) t0_testBase : initial time for test basis
        # 4) t1_testBase : Final time for test basis
        # 5) n_simu : Time step decreasing factor for ROM time integration
        # 6) inflatNut : for case LES only
        # 7) interpFieldCenteredOrNot : for case LES only
        # 8) HypRedSto : for case LES only
        # 9) DEIMInterpolatedField : for case LES only
        param_file = Path(f"{self.res_folder}/../../system/ITHACAdict")

        if param_file.exists():
            inflatNut = ''
            interpFieldCenteredOrNot = ''
            HypRedSto = ''
            DEIMInterpolatedField = ''
            f_param = open(param_file, 'r')
            N_bracket = 0
            while True:
                line = f_param.readline()
                if not line:
                    break
                else:
                    line = line.replace(';', '')  # suppress COMMA
                    line = line.replace('"', '')  # suppress QUOTE
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
                        if re.search('InitialTime ', line):
                            if str(a[0]) == 'InitialTime':
                                t0_learningBase = float(a[-2])
                        if re.search('FinalTime ', line):
                            if str(a[0]) == 'FinalTime':
                                t1_learningBase = float(a[-2])
                                t0_testBase = t1_learningBase
                        if re.search('FinalTimeSimulation ', line):
                            if str(a[0]) == 'FinalTimeSimulation':
                                t1_testBase = float(a[-2])
                        if re.search('nSimu ', line):
                            if str(a[0]) == 'nSimu':
                                n_simu = int(a[-2])
                        if re.search('nParticules ', line):
                            if str(a[0]) == 'nParticules':
                                n_particles = int(a[-2])
                        if re.search('nmodes ', line):
                            if str(a[0]) == 'nmodes':
                                n_modes = int(a[-2])
                        if re.search('inflatNut ', line):
                            if str(a[0]) == 'inflatNut':
                                inflatNut = int(a[-2])
                        if re.search('interpFieldCenteredOrNot ', line):
                            if str(a[0]) == 'interpFieldCenteredOrNot':
                                interpFieldCenteredOrNot = int(a[-2])
                        if re.search('HypRedSto ', line):
                            if str(a[0]) == 'HypRedSto':
                                HypRedSto = int(a[-2])
                        if re.search('DEIMInterpolatedField ', line):
                            if str(a[0]) == 'DEIMInterpolatedField':
                                DEIMInterpolatedField = str(a[-2])

        return t0_learningBase, t1_learningBase, t0_testBase, t1_testBase, n_simu, inflatNut, interpFieldCenteredOrNot, HypRedSto, DEIMInterpolatedField, n_particles

    def save_plot(self, name):
        """
        Function that saves the current active plot in png and pdf format
        :param name: name of the saved file
        :return:
        """
        # Checking that plot directory exists
        os.makedirs(f"{self.save_dir}/plots", exist_ok=True)
        os.makedirs(f"{self.save_dir}/plots/pdf", exist_ok=True)

        self.info(f"Saving plots to {self.save_dir}/plots/{name}",1)

        plt.savefig(f"{self.save_dir}/plots/{name}.png")
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
