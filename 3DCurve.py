import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import json
import numpy as np
import os
import glob

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

def Plot(P):
	if (P):	
		figManager = plt.get_current_fig_manager()
		figManager.window.showMaximized()
		plt.show()
	plt.close()
	return

def GetData(Data, Key):
	NewData = [[], [], []]
	NewData[0] = [X[0] if X[0] is not None else 0. for X in Data[Key]]
	NewData[1] = [X[1] if X[1] is not None else 0. for X in Data[Key]]
	NewData[2] = [X[2] if X[2] is not None else 0. for X in Data[Key]]
	return np.array(NewData)

#Code to check if vector is unitary
NormMin = 0.95
NormMax = 1.05
NormTolMin = 0.90
NormTolMax = 1.10
def CheckNorm(Data, Verbose, Mode):
	Data =  [np.array(X) for X in zip(*Data)]
	Norms = [np.linalg.norm(X) for X in Data]
	Count = 0
	CountTol = 0
	for X in Norms:
		if not NormTolMin < X < NormTolMax:
			CountTol += 1
		elif not NormMin < X < NormMax:
			Count += 1
		if Verbose and Mode:
			print(GREEN if NormMin < X < NormMax  else YELLOW if NormTolMin < X < NormTolMax else RED, "{:.4f}".format(X), END, sep = "", end = " ")
	if Mode:
		if Verbose:
			print()
		print ("Number of vectors: ", BLUE, len(Data), END, sep = "")
		print ("Number of non-unitary vectors (5%): ", YELLOW if Count else GREEN, Count, END, sep = "")
		print ("Number of non-unitary vectors (10%): ", RED if CountTol else GREEN, CountTol, END, sep = "")
	return np.array([Count, CountTol, len(Data)])

#Code to check if vectors are orthogonal
DotLim = 0.05
DotTol = 0.10
def CheckOrtho(DataA, DataB, Verbose, Mode):
	DataA =  [np.array(X) for X in zip(*DataA)]
	DataB =  [np.array(X) for X in zip(*DataB)]
	Dots = [np.dot(X[0], X[1]) for X in zip(DataA, DataB)]
	Count = 0
	CountTol = 0
	for X in Dots:
		if np.abs(X) > DotTol:
			CountTol += 1
		elif np.abs(X) > DotLim:
			Count += 1
		if Verbose and Mode:
			print(GREEN if np.abs(X) < DotLim  else YELLOW if np.abs(X) < DotTol else RED, "{:.4f}".format(np.abs(X)), END, sep = "", end = " ")
	if Mode:
		if Verbose:
			print()
		print ("Number of vectors: ", BLUE, len(DataA), END, sep = "")
		print ("Number of non-orthogonal vectors: (5%): ", YELLOW if Count else GREEN, Count, END, sep = "")
		print ("Number of non-orthogonal vectors: (10%): ", RED if CountTol else GREEN, CountTol, END, sep = "")
	return np.array([Count, CountTol, len(DataA), len(DataB)])

def CheckSizes(Data, Size = 1):
	It = iter(Data)
	return all(len(Datum) == Size for Datum in It)
 
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
Mode = CheckSizes(AllFiles)
	
for Files in AllFiles:
	TotNormTang = np.array([0, 0, 0])
	TotNormNorm = np.array([0, 0, 0])
	TotNormBinorm = np.array([0, 0, 0])
	TotOrthTangNorm = np.array([0, 0, 0, 0])
	TotOrthTangBinorm = np.array([0, 0, 0, 0])
	TotOrthNormBinorm = np.array([0, 0, 0, 0])
	for File in Files:
		Data = json.load(open(File, 'r'))
		CoordData = GetData(Data, "Coordinates")
		TangData = GetData(Data, "Tangents")
		NormData = GetData(Data, "Normals")
		BinormData = GetData(Data, "Binormals")
		
		if Mode:
			print (BOLD, "\nFor file ",BLUE, File, ":", END,sep = "")
			print (BOLD, "Checking if vectors are unitary", END, sep = "")
			print ("For tangents:")
		TotNormTang += CheckNorm(TangData, Args.V, Mode)
		if Mode:
			print ("For normals:")
		TotNormNorm += CheckNorm(NormData, Args.V, Mode)
		if Mode:
			print ("For binormals:")
		TotNormBinorm += CheckNorm(BinormData, Args.V, Mode)
		if Mode:
			print ("\n",BOLD, "Checking if vectors are orthogonal", END, sep = "")
			print ("For tangents vs normals:")
		TotOrthTangNorm += CheckOrtho(TangData[:,:len(TangData[0])-1], NormData, Args.V, Mode)
		if Mode:
			print ("For tangents vs binormals:")
		TotOrthTangBinorm += CheckOrtho(TangData[:,:len(TangData[0])-1], BinormData, Args.V, Mode)
		if Mode:
			print ("For normals vs binormals:")
		TotOrthNormBinorm += CheckOrtho(NormData, BinormData, Args.V, Mode)
		
		if Mode:
			print()
			Fig = plt.figure()
			Ax = plt.axes(projection='3d')
			Ax.plot3D(CoordData[0], CoordData[1], CoordData[2], "blue", label = "Trajectory")
			Ax.set_xlabel("X")
			Ax.set_ylabel("Y")
			Ax.set_zlabel("Z")
			if Args.C:
				Jump =   5#200
				Width = .8
				Ratio = .1
				Ax.quiver(CoordData[0][:len(CoordData[0])-1:Jump], CoordData[1][:len(CoordData[0])-1:Jump], CoordData[2][:len(CoordData[0])-1:Jump], TangData[0][::Jump], TangData[1][::Jump], TangData[2][::Jump], color="red", arrow_length_ratio = Ratio, linewidths = Width, label = "Tangent") 
				Ax.quiver(CoordData[0][:len(CoordData[0])-2:Jump], CoordData[1][:len(CoordData[0])-2:Jump], CoordData[2][:len(CoordData[0])-2:Jump], NormData[0][::Jump], NormData[1][::Jump], NormData[2][::Jump], color="green", arrow_length_ratio = Ratio, linewidths = Width, label = "Normal") 
				Ax.quiver(CoordData[0][:len(CoordData[0])-2:Jump], CoordData[1][:len(CoordData[0])-2:Jump], CoordData[2][:len(CoordData[0])-2:Jump], BinormData[0][::Jump], BinormData[1][::Jump], BinormData[2][::Jump], color="black", arrow_length_ratio = Ratio, linewidths = Width, label = "Binormal") 
			Ax.legend()
			#XLim = 2.5
			#YLim = 2.5
			#ZLim = 5.
			#Ax.set_xlim3d(-XLim,XLim)
			#Ax.set_ylim3d(-YLim,YLim)
			#Ax.set_zlim3d(-0,ZLim)
			Plot(Args.P)
	if not Mode:
		print (BOLD, "For Key ", BLUE, Args.Keys[AllFiles.index(Files)], END, sep = "")
		print (BOLD, "\nChecking if vectors are unitary", END, sep="")
		print("For tangents:\n\tBad data (5%): ", YELLOW, TotNormTang[0], END, "\n\tBad data (10%): ", RED, TotNormTang[1], END, sep = "")
		print("\tTotal number of vectors: ", TotNormTang[2], sep = "")
		print ("\tBad data ratio:", YELLOW, "{:.3f}".format(TotNormTang[0]/TotNormTang[2]), END, " ", RED, "{:.3f}".format(TotNormTang[1]/TotNormTang[2]), END, sep = "")
		print("For normals:\n\tBad data (5%): ", YELLOW, TotNormNorm[0], END, "\n\tBad data (10%): ", RED, TotNormNorm[1], END, sep = "")
		print("\tTotal number of vectors: ", TotNormNorm[2], sep = "")
		print ("\tBad data ratio: ", YELLOW, "{:.3f}".format(TotNormNorm[0]/TotNormNorm[2]), END, " ", RED, "{:.3f}".format(TotNormNorm[1]/TotNormNorm[2]), END, sep = "")
		print("For binormals:\n\tBad data (5%): ", YELLOW, TotNormBinorm[0], END, "\n\tBad data (10%): ", RED, TotNormBinorm[1], END, sep = "")
		print("\tTotal number of vectors: ", TotNormBinorm[2], sep = "")
		print ("\tBad data ratio: ", YELLOW, "{:.3f}".format(TotNormBinorm[0]/TotNormBinorm[2]), END, " ", RED, "{:.3f}".format(TotNormBinorm[1]/TotNormBinorm[2]), END, sep = "")
		print (BOLD, "\nChecking if vectors are orthogonal", END, sep="")
		print("For tangents vs normals:\n\tBad data (5%): ", YELLOW, TotOrthTangNorm[0], END, "\n\tBad data (10%): ", RED, TotOrthTangNorm[1], END, sep = "")
		print("\tTotal number of vectors: ", TotOrthTangNorm[2], "-", TotOrthTangNorm[3], sep = "")
		print ("\tBad data ratio: ", YELLOW, "{:.3f}".format(TotOrthTangNorm[0]/TotOrthTangNorm[2]), END, " ", RED, "{:.3f}".format(TotOrthTangNorm[1]/TotOrthTangNorm[2]), END, sep = "")
		print("For tangents vs binormals:\n\tBad data (5%): ", YELLOW, TotOrthTangBinorm[0], END, "\n\tBad data (10%): ", RED, TotOrthTangBinorm[1], END, sep = "")
		print("\tTotal number of vectors: ", TotOrthTangBinorm[2], "-", TotOrthTangBinorm[3], sep = "")
		print ("\tBad data ratio: ", YELLOW, "{:.3f}".format(TotOrthTangBinorm[0]/TotOrthTangBinorm[2]), END, " ", RED, "{:.3f}".format(TotOrthTangBinorm[1]/TotOrthTangBinorm[2]), END, sep = "")
		print("For normals vs binormals:\n\tBad data (5%): ", YELLOW, TotOrthNormBinorm[0], END, "\n\tBad data (10%): ", RED, TotOrthNormBinorm[1], END, sep = "")
		print("\tTotal number of vectors: ", TotOrthNormBinorm[2], "-", TotOrthNormBinorm[3], sep = "")
		print ("\tBad data ratio: ", YELLOW, "{:.3f}".format(TotOrthNormBinorm[0]/TotOrthNormBinorm[2]), END, " ", RED, "{:.3f}".format(TotOrthNormBinorm[1]/TotOrthNormBinorm[2]), END, sep = "")