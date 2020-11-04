import os
import glob

def NoFiles(FileList):
    for Element in FileList:
        if Element:
            return False
    return True

def GetFiles (Path, Keys):
	if not os.path.isdir(Path):
	    print ("Invalid input path.")
	    return [[]]
	AllFiles = [None]*len(Keys)#np.empty((len(Args.Keys), 0)).tolist()
	for I in range(len(Keys)):
	    AllFiles[I] = glob.glob(Path+"*"+Keys[I]+"*.json")
	    AllFiles[I].sort()
	AllFiles = [X for X in AllFiles if X != []]
	return AllFiles

def CheckSizes(Data, Size = 1):
	It = iter(Data)
	return all(len(Datum) == Size for Datum in It)