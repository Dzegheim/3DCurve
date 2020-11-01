import matplotlib.pyplot as plt
import matplotlib.ticker as tk
import json
import numpy as np
import os
import glob
from scipy.optimize import curve_fit
import scipy.stats as ss

import argparse
from argparse import ArgumentParser
class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        return argparse.HelpFormatter._split_lines(self, text, width)

def NoFiles(FileList):
    for Element in FileList:
        if Element:
            return False
    return True

END = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"

NBins = [20, 20, 20, 20, 20, 20, 20, 20]

def Plot(P):
    if (P): 
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()
    plt.close()
    return

def GetParamsFormat (Params, Errors, Names):
    String = ""
    for K in zip(Names, Params, Errors):
        String += "\n${:}$ $=$ ${:2.2f}\\pm {:.2f}$".format(K[0], K[1], K[2])
    return String

def ExpLawT (X, Mod, Exp, X0):
    return Mod*np.exp((X-X0)*Exp)
def PowLawT (X, Mod, Exp, X0):
    return Mod*((X-X0)**Exp)
def GammaLawT (X, Mod, Exp1, Exp2, X0):
    return Mod*((X-X0)**Exp1)*np.exp((X-X0)*Exp2)
def MaxBoltT (X, Mod, Exp1, Exp2, X0):
    return Mod*((X-X0)**Exp1)*np.exp(((X-X0)**Exp1)*Exp2)
def SelfExpT (X, Mod, Exp, X0):
    return (Mod*(X-X0))**(Exp*(X-X0))

def ExpLaw (X, Mod, Exp):
    return Mod*np.exp(X*Exp)
def PowLaw (X, Mod, Exp):
    return Mod*(X**Exp)
def GammaLaw (X, Mod, Exp1, Exp2):
    return Mod*(X**Exp1)*np.exp(X*Exp2)

Exps = ["E1", "E2", "E3", "E4", "E1", "E2", "E3", "E4"]
FastSlow = ["fast", "fast", "fast", "fast", "slow", "slow", "slow", "slow"]
Food = ["food", "no food", "food", "no food", "food", "no food", "food", "no food"]
Fits = ["ExpLawT", "PowLawT", "ExpLawT", "PowLawT", "ExpLawT", "ExpLawT", "ExpLawT", "ExpLawT"]
#Fits = ["GammaLawT", "PowLawT", "GammaLawT", "PowLawT", "ExpLawT", "ExpLawT", "ExpLawT", "ExpLawT"]
#K0 = [1, 2, 1, 2, 2, 3, 2, 2] #Con gamma
K0 = [2, 2, 2, 2, 2, 3, 2, 3] #Con exp
K1 = [15, 20, 16, 20, 9, 13, 10, 12]
ParamsInit = [
    #Fast
    [575.09459511,  -2.31475339,   0.87420774],
    #[ 1.00147193e+04, -5.14753558e-02, -1.74756947e+00,  1.50235754e-01],
    [95.48850397, -1.71369986,  0.12205367],
    #[ 1.00147193e+04, -1.74756947e+00,  1.50235754e-01],
    [ 5.79149509, -1.93579998,  4.06955861],
    [ 270.718416, -1.68653986,  .109372058],
    #Slow
    [ 0.04812365, -5.57413187,  2.46289627],
    [ 0.65344911, -4.77902377,  2.51116258],
    [ 1.09412477, -6.39887101,  1.80105166],
    [ 0.72867062, -4.38889259,  2.68541256]
    ]

Labels = {
    "GammaLawT" : "$Y$ $=$ $C$ $\\left(X-X_{0}\\right)^{\\alpha}$ $\\exp\\left[\\beta(X-X_{0})\\right]$",
    "ExpLawT" : "$Y$ $=$ $C$ $\\exp\\left[\\beta(X-X_{0})\\right]$",
    "PowLawT" : "$Y$ $=$ $C$ $\\left(X-X_{0}\\right)^{\\alpha}$",
    "SelfExpT" : "$Y$ $=$ $C$ $\\left[\\zeta\\left(X-X_{0}\\right)\\right]^{\\zeta\\left(X-X_{0}\\right)}$"
}
PossibleFits = {
    "GammaLawT" : GammaLawT,
    "ExpLawT" : ExpLawT,
    "PowLawT" : PowLawT,
    "SelfExpT" : SelfExpT
}
Names = {
    "GammaLawT" : ["C", "\\alpha", "\\beta", "X_{0}"],
    "ExpLawT" : ["C", "\\beta", "X_{0}"],
    "PowLawT" : ["C", "\\alpha", "X_{0}"],
    "SelfExpT" : ["C", "\\zeta", "X_{0}"]
}

Parser = ArgumentParser(description = "", formatter_class = SmartFormatter)
Parser.add_argument("Directory", metavar= "-D", type = str, action = "store", help = "Path to the directory containing the files.")
Parser.add_argument("Keys", metavar = "-K", nargs = "+", help = "A list of keys. All files in the folder containing a Key in the name will be read. If a file contains two or more keys it will be read more than once. If each key is associated only to a single file there are no requirements for confirmation on plotting.")
Parser.add_argument("-P", "--P", "--p", action = "store_true", help = "If given the data is plotted.")
Parser.add_argument("-V", "--V", "--v", action = "store_true", help = "If given the program will print all the informations about normalization and orthogonality.")
Parser.add_argument("-C", "--C", "--c", action = "store_false", help = "If given the vectors will not be plotted.")
Args = Parser.parse_args()

if not os.path.isdir(Args.Directory):
    exit("Invalid input path.")
AllFiles = np.empty((len(Args.Keys), 0)).tolist()
for I in range(len(Args.Keys)):
    AllFiles[I] = glob.glob(Args.Directory+"*"+Args.Keys[I]+"*.json")
    AllFiles[I].sort()
AllFiles = [X for X in AllFiles if X != []]
if NoFiles(AllFiles):
    exit ("No valid files given.")

for Files in AllFiles:
    Ind = AllFiles.index(Files)
    for File in Files:
        Data = json.load(open(File, 'r'))
        Fig, Ax = plt.subplots(2)
        Curv = [X for X in Data["Curvature"] if X is not None]
        Tors = [X for X in Data["Torsion"] if X is not None]
        
        Hist, Bins, Cosi = Ax[0].hist(Curv, bins = NBins[Ind])
        BinsCenter = np.mean(np.vstack([Bins[0:-1], Bins[1:]]), axis=0)
        Params, Covs = curve_fit(PossibleFits[Fits[Ind]], BinsCenter[K0[Ind]:K1[Ind]], Hist[K0[Ind]:K1[Ind]], p0=ParamsInit[Ind], sigma = np.sqrt(Hist[K0[Ind]:K1[Ind]]), maxfev = 1000000000)

        XX = np.linspace(BinsCenter[K0[Ind]], Bins[K1[Ind]], 5000)
        YY = PossibleFits[Fits[Ind]](XX, *Params)

        Stat, Prob = ss.ks_2samp(Hist[K0[Ind]:K1[Ind]], YY)
        FitLabel = Labels[Fits[Ind]]+"\nKS test probability: {:.3f}".format(Prob)+GetParamsFormat(Params, np.sqrt(np.diag(Covs)), Names[Fits[Ind]])

        print()
        print (Params)
        print (np.sqrt(np.diag(Covs)))
        print (Prob)
        print()

        Ax[0].set_xlabel("Curvature ($mm^{-1}$)")
        Ax[0].set_ylabel("Occurrences")
        Ax[0].set_yscale("log")
        Ax[0].plot(XX, YY, color = "red", label = FitLabel)
        Ax[0].legend(loc='upper right', frameon = False)

        Ax[1].hist(Tors, bins = NBins[Ind])
        Ax[1].set_xlabel("Torsion ($mm^{-1} s^3$)")
        Ax[1].set_ylabel("Occurrences")
        Ax[1].set_yscale("log")
        
        Fig.suptitle(Exps[Ind]+" ("+FastSlow[Ind]+", "+Food[Ind]+") curvature and torsion histogram.")
        Plot(Args.P)