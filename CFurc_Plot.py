import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from numpy import log10

def PlotAndSave(Plot = True, Save = False, Name = "", Format = "pdf"):
    if (Plot): 
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()
    if (Save):
        plt.savefig(fname = Name+"."+Format, format = Format)
    plt.close()
    return

def GetParamsFormat (Params, Errors, Names):
    String = ""
    for K in zip(Names, Params, Errors):
        String += "\n${:}$ $=$ ${:2.2f}\\pm {:.2f}$".format(K[0], K[1], K[2])
    return String

def SetTicksY (Ax, Minor = False, EveryNth = 1):
    for N, Label in enumerate(Ax.yaxis.get_ticklabels(minor = Minor)):
        if N % EveryNth:
            Label.set_visible(False)
    return

def LogAxisY (Ax, Minor = False, MajorDecimal = 1, MinorDecimal = 1):
    MajorString = "{:."+str(MajorDecimal)+"f}"
    Ax.yaxis.set_major_formatter(tk.FuncFormatter(lambda X, _ : MajorString.format(log10(X))))
    if Minor:
        MinorString = "{:."+str(MinorDecimal)+"f}"
        Ax.yaxis.set_minor_formatter(tk.FuncFormatter(lambda X, _ : MinorString.format(log10(X))))
    return

def SetTicksX (Ax, Minor = False, EveryNth = 1):
    for N, Label in enumerate(Ax.xaxis.get_ticklabels(minor = Minor)):
        if N % EveryNth:
            Label.set_visible(False)
    return

def LogAxisY (Ax, Minor = False, MajorDecimal = 1, MinorDecimal = 1):
    MajorString = "{:."+str(MajorDecimal)+"f}"
    Ax.yaxis.set_major_formatter(tk.FuncFormatter(lambda X, _ : MajorString.format(log10(X))))
    if Minor:
        MinorString = "{:."+str(MinorDecimal)+"f}"
        Ax.yaxis.set_minor_formatter(tk.FuncFormatter(lambda X, _ : MinorString.format(log10(X))))
    return