from numpy import sqrt, diag, dot, mean, linspace, vstack
from matplotlib.pyplot import figure
from json import load
from scipy.optimize import curve_fit
from scipy.stats import ks_2samp

from CFurc_Argparse import ArgumentParser, SmartFormatter
from CFurc_Plot import PlotAndSave, GetParamsFormat, SetTicksY, LogAxisY
from CFurc_OSManip import NoFiles, GetFiles
from CFurc_FitFuncs import ExpLawT, PowLawT, GammaLawT

NBins = [20, 20, 20, 20, 20, 20, 20, 20]
TorsMinTicks = [4, 2, 4, 2, 1, 1, 2, 1]

Exps = ["E1", "E2", "E3", "E4", "E1", "E2", "E3", "E4"]
FastSlow = ["fast", "fast", "fast", "fast", "slow", "slow", "slow", "slow"]
Food = ["food", "no food", "food", "no food", "food", "no food", "food", "no food"]
Fits = ["ExpLawT", "PowLawT", "ExpLawT", "PowLawT", "ExpLawT", "ExpLawT", "ExpLawT", "ExpLawT"]
K0 = [2, 2, 2, 2, 2, 3, 2, 3]
K1 = [15, 20, 16, 20, 9, 13, 10, 12]
ParamsInit = [
    #Fast
    [ 0.04819713, -0.1543169 ,  2.17366977],
    [ 0.13609586, -1.71370038,  1.83080384],
    [ 0.07126269, -0.12905334,  0.5323467 ],
    [ 0.2197765 , -1.6865406 ,  1.64057921],
    #[575.09459511,  -2.31475339,   0.87420774],
    #[95.48850397, -1.71369986,  0.12205367],
    #[ 5.79149509, -1.93579998,  4.06955861],
    #[ 270.718416, -1.68653986,  .109372058],
    #Slow
    [ 1.34355626, -0.37160881, -2.00850294],
    [ 0.50478375, -0.31860157,  0.76632117],
    [ 0.77184598, -0.42659173,  0.21559254],
    [ 0.56761622, -0.31655837,  0.19878062]
    #[ 0.09067554, -5.57413186,  0.83554892],
    #[ 2.16770303, -4.77902356,  0.31280609],
    #[ 0.04601584, -6.39887318,  0.87825138],
    #[ 0.08433923, -4.74837525,  0.98508945]
    ]

Labels = {
    "GammaLawT" : "$Y$ $=$ $C$ $\\left(X-X_{0}\\right)^{\\alpha}$ $\\exp\\left[\\beta(X-X_{0})\\right]$",
    "ExpLawT" : "$Y$ $=$ $C$ $\\exp\\left[\\beta(X-X_{0})\\right]$",
    "PowLawT" : "$Y$ $=$ $C$ $\\left(X-X_{0}\\right)^{\\alpha}$",
}
PossibleFits = {
    "GammaLawT" : GammaLawT,
    "ExpLawT" : ExpLawT,
    "PowLawT" : PowLawT,
}
Names = {
    "GammaLawT" : ["C", "\\alpha", "\\beta", "X_{0}"],
    "ExpLawT" : ["C", "\\beta", "X_{0}"],
    "PowLawT" : ["C", "\\alpha", "X_{0}"],
}

Parser = ArgumentParser(description = "", formatter_class = SmartFormatter)
Parser.add_argument("Directory", metavar= "-D", type = str, action = "store", help = "Path to the directory containing the files.")
Parser.add_argument("Keys", metavar = "-K", nargs = "+", help = "A list of keys. All files in the folder containing a Key in the name will be read. If a file contains two or more keys it will be read more than once. If each key is associated only to a single file there are no requirements for confirmation on plotting.")
Parser.add_argument("-Plot", "--P", "--p", action = "store_true", help = "If given the data is plotted.")
Parser.add_argument("-Save", "--S", "--s", action = "store_true", help = "If given the data is saved.")
Args = Parser.parse_args()

AllFiles = GetFiles(Args.Directory, Args.Keys)
if NoFiles(AllFiles):
    exit ("No valid files given.")

for Files in AllFiles:
    Ind = AllFiles.index(Files)
    for File in Files:
        Data = load(open(File, 'r'))
        Fig = figure()
        Grid = Fig.add_gridspec(2, 1, hspace = .5)
        Ax0 = Fig.add_subplot(Grid[0, 0])
        Ax1 = Fig.add_subplot(Grid[1, 0])
        Curv = [X for X in Data["Curvature"] if X is not None]
        DsTorsVsNorm = [-dot(X[0], X[1]) for X in zip(Data["Normals"][:len(Data["Normals"])-2], Data["BinormDer"]) if all(A is not None for A in X[0]) and all(A is not None for A in X[1])]
        Hist, Bins, Cosi = Ax0.hist(Curv, bins = NBins[Ind], density =  True, stacked = True)
                
        BinsCenter = mean(vstack([Bins[0:-1], Bins[1:]]), axis=0)
        Params, Covs = curve_fit(PossibleFits[Fits[Ind]], BinsCenter[K0[Ind]:K1[Ind]], Hist[K0[Ind]:K1[Ind]], p0=ParamsInit[Ind], sigma = sqrt(Hist[K0[Ind]:K1[Ind]]), maxfev = 1000000000)

        XX = linspace(BinsCenter[K0[Ind]], Bins[K1[Ind]], 5000)
        YY = PossibleFits[Fits[Ind]](XX, *Params)

        Stat, Prob = ks_2samp(Hist[K0[Ind]:K1[Ind]], YY)
        FitLabel = Labels[Fits[Ind]]+"\nKS test probability: {:.3f}".format(Prob)+"\n${:}$ $=$ ${:2.2f}\\pm {:.2f}$".format(Names[Fits[Ind]][1], Params[1], sqrt(diag(Covs))[1])

        print ()
        print (Params)
        print (sqrt(diag(Covs)))
        print (Prob)
        print ()
                
        Ax0.set_xlabel("Curvature ($mm^{-1}$)")
        Ax0.set_ylabel("$\\log_{10}\\left(PDF\\right)$")
        Ax0.set_yscale("log")
        SetTicksY(Ax0, False, 1)
        SetTicksY(Ax0, True, 1000000)
        LogAxisY(Ax0, True, 0, 1)
        Ax0.plot(XX, YY, color = "red", label = FitLabel)
        Ax0.legend(loc='upper right', frameon = False)

        Ax1.hist(DsTorsVsNorm, bins = NBins[Ind], density =  True, stacked = True)
        #Ax1.hist(Tors, bins = NBins[Ind])
        Ax1.set_xlabel("Torsion ($mm^{-1}$)")
        Ax1.set_ylabel("$\\log_{10}\\left(PDF\\right)$")
        Ax1.set_yscale("log")
        LogAxisY(Ax1, True, 2, 2)
        SetTicksY(Ax1, False, 1)
        SetTicksY(Ax1, True, TorsMinTicks[Ind])
        
        Fig.suptitle(Exps[Ind]+" ("+FastSlow[Ind]+", "+Food[Ind]+") curvature and torsion histogram.")
        PlotAndSave(Plot = Args.P, Save = Args.S, Format = "pdf", Name = "./Figs/CurvTors"+Exps[Ind]+FastSlow[Ind])
