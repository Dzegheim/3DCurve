from matplotlib.pyplot import figure, axes
from mpl_toolkits import mplot3d
from json import load
from numpy import array

from CFurc_Argparse import ArgumentParser, SmartFormatter
from CFurc_Plot import PlotAndSave
from CFurc_OSManip import NoFiles, GetFiles, CheckSizes
from CFurc_DataManip import GetNonNullData, CheckNorm, CheckOrtho
from CFurc_Colors import RED, GREEN, YELLOW, BLUE, END, BOLD

Parser = ArgumentParser(description = "", formatter_class = SmartFormatter)
Parser.add_argument("Directory", metavar= "-D", type = str, action = "store", help = "Path to the directory containing the files.")
Parser.add_argument("Keys", metavar = "-K", nargs = "+", help = "A list of keys. All files in the folder containing a Key in the name will be read. If a file contains two or more keys it will be read more than once. If each key is associated only to a single file there are no requirements for confirmation on plotting.")
Parser.add_argument("-Plot", "--P", "--p", action = "store_true", help = "If given the data is plotted.")
Parser.add_argument("-Save", "--S", "--s", action = "store_true", help = "If given the data is saved.")
Parser.add_argument("-Verbose", "--V", "--v", action = "store_true", help = "If given the program will print all the informations about normalization and orthogonality.")
Parser.add_argument("-Curve Only", "--C", "--c", action = "store_false", help = "If given the vectors will not be plotted, only the curve will be.")
Args = Parser.parse_args()

AllFiles = GetFiles(Args.Directory, Args.Keys)
if NoFiles(AllFiles):
    exit ("No valid files given.")
Mode = CheckSizes(AllFiles)
    
for Files in AllFiles:
    TotNormTang = array([0, 0, 0])
    TotNormNorm = array([0, 0, 0])
    TotNormBinorm = array([0, 0, 0])
    TotOrthTangNorm = array([0, 0, 0, 0])
    TotOrthTangBinorm = array([0, 0, 0, 0])
    TotOrthNormBinorm = array([0, 0, 0, 0])
    for File in Files:
        Data = load(open(File, 'r'))
        CoordData = array(GetNonNullData(Data, "Coordinates"))
        TangData = array(GetNonNullData(Data, "Tangents"))
        NormData = array(GetNonNullData(Data, "Normals"))
        BinormData = array(GetNonNullData(Data, "Binormals"))
        
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
            Fig = figure()
            Ax = axes(projection='3d')
            Ax.plot3D(CoordData[0], CoordData[1], CoordData[2], "blue", label = "Trajectory")
            Ax.set_xlabel("X")
            Ax.set_ylabel("Y")
            Ax.set_zlabel("Z")
            if Args.C:
                Jump =   3#2000
                Width = .8
                Ratio = .1
                Ax.quiver(CoordData[0][:len(CoordData[0])-1:Jump], CoordData[1][:len(CoordData[0])-1:Jump], CoordData[2][:len(CoordData[0])-1:Jump], TangData[0][::Jump], TangData[1][::Jump], TangData[2][::Jump], color="red", arrow_length_ratio = Ratio, linewidths = Width, label = "Tangent") 
                Ax.quiver(CoordData[0][:len(CoordData[0])-2:Jump], CoordData[1][:len(CoordData[0])-2:Jump], CoordData[2][:len(CoordData[0])-2:Jump], NormData[0][::Jump], NormData[1][::Jump], NormData[2][::Jump], color="green", arrow_length_ratio = Ratio, linewidths = Width, label = "Normal") 
                Ax.quiver(CoordData[0][:len(CoordData[0])-2:Jump], CoordData[1][:len(CoordData[0])-2:Jump], CoordData[2][:len(CoordData[0])-2:Jump], BinormData[0][::Jump], BinormData[1][::Jump], BinormData[2][::Jump], color="black", arrow_length_ratio = Ratio, linewidths = Width, label = "Binormal") 
            Ax.legend()
            PlotAndSave(Plot = Args.P, Save = Args.S, Format = "pdf", Name = "")#"./Figs/Frenet"+Exps[Ind]+FastSlow[Ind])
    if not Mode:
        print ("\n", BOLD, "For Key ", BLUE, Args.Keys[AllFiles.index(Files)], END, sep = "")
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