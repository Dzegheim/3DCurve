#include <iostream>
#include <fstream>
#include <vector>
#include <iterator>
#include <numeric>
#include <cmath>
#include <filesystem>
#include <algorithm>

//https://github.com/danielaparker/jsoncons
#include <jsoncons/json.hpp>

//Should be in the same project
#include "VectorOperations.h"
//In Libraries
#include "Pipeline.h"
#include "ExploreDirectory.h"

using VectorOpearations::GetVariation;
using VectorOpearations::Normalize;
using VectorOpearations::CrossProduct;

#define MINIMUM_WORKING_CONDITION 5

void WriteData (const jsoncons::wojson& JData, const std::filesystem::path& OutPath, 
    const std::wstring& OutputName, const int FileNumber) {
    //Save Data
    std::wstring Number;
    {
        std::wstringstream Temp;
        Temp << std::setw(4) << std::setfill(L'0') << FileNumber+1;
        Number = Temp.str();
    }
    std::filesystem::path Output =  OutPath/std::wstring(OutputName+L"_"+Number+L".json");
    std::wofstream OutStream (Output);
    OutStream << JData;
    OutStream.close();
}

//Porcata
typedef jsoncons::basic_json<wchar_t, jsoncons::preserve_order_policy, std::allocator<char>> J;
//Porcate
double operator-(const J & A, const J & B) {
	return A.as<double>()-B.as<double>();
}
double operator*(const J & A, const J & B) {
	return A.as<double>()*B.as<double>();
}
void operator/=(J & A, const double B) {
	auto C = A.as<double>();
	C /= B;
	A = C;
	return;
}

int main(int Nargs, char** Args) {
	std::vector<std::wstring> IOArgs;
    if (Nargs > 1) {
        //The paths are necessary for conversion.
        IOArgs.push_back(std::filesystem::path(Args[1]).wstring());
    }
    if (Nargs > 2) {
        //The paths are necessary for conversion.
        IOArgs.push_back(std::filesystem::path(Args[2]).wstring());
    }
    int IOCheck = Pipeline::MakePipe (IOArgs);
    if (IOCheck >= 0) {
        std::wistream & Input = ((IOCheck == 3) or (IOCheck == 1)) ? *Pipeline::PipeInput : std::wcin;
        std::wostream & Output = ((IOCheck == 3) or (IOCheck == 2)) ? *Pipeline::PipeOutput : std::wcout;
    	
        //Process instructions
		jsoncons::wojson Instructions;
        Instructions = jsoncons::wojson::parse(Input);
		const auto DeltaS = Instructions[L"DeltaS"].as<double>();
		const auto Epsilon = Instructions[L"Epsilon"].as<double>();
		const auto Verbose = Instructions[L"Verbose"].as<bool>();
       	const std::filesystem::path InputPath = Instructions[L"InputPath"].as<std::wstring>();
   		const auto InputNames = Instructions[L"InputNames"].as<std::vector<std::wstring>>();
        const std::filesystem::path OutputPath = Instructions[L"OutputPath"].as<std::wstring>();
       	const auto OutputNames = Instructions[L"OutputNames"].as<std::vector<std::wstring>>();
    	for (size_t I = 0; I != InputNames.size(); ++I) {
    		auto Files = Explore::ExploreDirectoryByName(InputNames[I], InputPath);
    		std::sort(std::begin(Files), std::end(Files));
    		for (size_t J = 0; J != Files.size(); ++J){
    			if (Verbose) {
    				Output << L"Working on "<<Files[J]<<L'\n';
    			}
				jsoncons::wojson JData;
				{
	 				jsoncons::wojson ExpData;
					{
						auto Temp = std::wifstream(InputPath/Files[J]);
						ExpData = jsoncons::wojson::parse(Temp);
						if (ExpData[L"List"].size() < MINIMUM_WORKING_CONDITION) {continue;}
					}
					//Prepare the Json for the data
					JData[L"Coordinates"] = jsoncons::wojson::make_array<2>(ExpData[L"List"].size(), 3, 0.);
					auto CoordEnd = JData[L"Coordinates"].array_range().end();
					auto Coord = JData[L"Coordinates"].array_range().begin();
					auto CoordExp = ExpData[L"List"].array_range().begin();
					while (Coord != CoordEnd) {
						*Coord = (*CoordExp)/*.as<jsoncons::wojson>()*/;
						++Coord;
						++CoordExp;
					}
				}
				JData[L"Coordinates"].erase(
					std::unique(
						JData[L"Coordinates"].array_range().begin(),
						JData[L"Coordinates"].array_range().end(),
						[Epsilon] (auto A, auto B) {
							return std::sqrt((A[0]-B[0])*(A[0]-B[0])+(A[1]-B[1])*(A[1]-B[1])+(A[2]-B[2])*(A[2]-B[2])) < Epsilon;
						}
					),
					JData[L"Coordinates"].array_range().end());
				JData[L"Tangents"]  = jsoncons::wojson::make_array<2>(JData[L"Coordinates"].size()-1, 3, 0.);
				JData[L"Normals"]   = jsoncons::wojson::make_array<2>(JData[L"Coordinates"].size()-2, 3, 0.);
				JData[L"Binormals"] = jsoncons::wojson::make_array<2>(JData[L"Coordinates"].size()-2, 3, 0.);
				JData[L"Curvature"] = jsoncons::wojson::make_array<1>(JData[L"Coordinates"].size()-2, 0.);
				JData[L"Torsion"]    = jsoncons::wojson::make_array<1>(JData[L"Coordinates"].size()-3, 0.);
				//Get the tangent unitary vectors
				{
					auto CoordAdv = JData[L"Coordinates"].array_range().begin();
					std::advance (CoordAdv, 1);
					auto Coord = JData[L"Coordinates"].array_range().begin();
					auto Tang = JData[L"Tangents"].array_range().begin();
					auto TangEnd = JData[L"Tangents"].array_range().end();
					while (Tang != TangEnd) {
						GetVariation (
							DeltaS,
							(*Tang).array_range().begin(),
							(*Coord).array_range().begin(),
							(*Coord).array_range().end(),
							(*CoordAdv).array_range().begin()
							);
						Normalize <double> (
							(*Tang).array_range().begin(),
							(*Tang).array_range().end()
							);
						++Coord;
						++CoordAdv;
						++Tang;
					}
				}
				//Get the normal unitary vectors
				{
					auto TangAdv = JData[L"Tangents"].array_range().begin();
					std::advance (TangAdv, 1);
					auto Tang = JData[L"Tangents"].array_range().begin();
					auto Norm = JData[L"Normals"].array_range().begin();
					auto NormEnd = JData[L"Normals"].array_range().end();
					auto Curv = JData[L"Curvature"].array_range().begin();
					while (Norm != NormEnd) {
						GetVariation (
							DeltaS,
							(*Norm).array_range().begin(),
							(*Tang).array_range().begin(),
							(*Tang).array_range().end(),
							(*TangAdv).array_range().begin()
							);
						*Curv = Normalize <double> (
							(*Norm).array_range().begin(),
							(*Norm).array_range().end()
							);
						++Tang;
						++TangAdv;
						++Norm;
						++Curv;
					}
				}
				//Get the binormal unitary vectors
				{
					auto Tang = JData[L"Tangents"].array_range().begin();
					auto Norm = JData[L"Normals"].array_range().begin();
					auto Binorm = JData[L"Binormals"].array_range().begin();
					auto BinormEnd = JData[L"Binormals"].array_range().end();
					while (Binorm != BinormEnd) {
						CrossProduct(
							(*Binorm).array_range().begin(),
							(*Tang).array_range().begin(),
							(*Norm).array_range().begin()
						);
						++Tang;
						++Norm;
						++Binorm;
					}
				}
				//Get the torsion
				{
					jsoncons::wojson SupportJ;
					SupportJ[L"BinormDer"] = jsoncons::wojson::make_array<2>(JData[L"Coordinates"].size()-3, 3, 0.);
					auto Binorm = JData[L"Binormals"].array_range().begin();
					auto BinormAdv = JData[L"Binormals"].array_range().begin();
					std::advance(BinormAdv, 1);
					auto BinDer = SupportJ[L"BinormDer"].array_range().begin();
					auto BinDerEnd = SupportJ[L"BinormDer"].array_range().end();
					auto Torq = JData[L"Torsion"].array_range().begin();
					while (BinDer != BinDerEnd) {
						GetVariation (
							DeltaS,
							(*BinDer).array_range().begin(),
							(*Binorm).array_range().begin(),
							(*Binorm).array_range().end(),
							(*BinormAdv).array_range().begin()
							);
						*Torq = -Normalize <double> (
							(*BinDer).array_range().begin(),
							(*BinDer).array_range().end()
							);
						++Binorm;
						++BinormAdv;
						++BinDer;
						++Torq;
					}
				}
				//Dump everything to file
				WriteData(JData, OutputPath, OutputNames[I], J);
			}
		}
	}
}