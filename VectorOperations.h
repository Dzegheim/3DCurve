#ifndef VECTOROPS_H
#define VECTOROPS_H

#include <cmath>
#include <vector>
#include <iterator>

namespace VectorOpearations {
	template<typename InIt, typename OutIt>	void CrossProduct (OutIt, InIt, InIt);
	template<typename T, typename InIt> T Normalize (InIt, InIt);
	template<typename T, typename InIt, typename OutIt> void GetVariation (const T, OutIt, InIt, InIt, InIt);
}
//Computes standard cross product in R^3
//Prerequistes: Beg1 and Beg2 must have a dimension of at least 3
template<typename InIt, typename OutIt>
void VectorOpearations::CrossProduct (OutIt Out, InIt Beg1, InIt Beg2) {
	*Out++ = *(Beg1+1)**(Beg2+2)-*(Beg1+2)**(Beg2+1); 
	*Out++ = *(Beg1+2)**(Beg2)-*(Beg1)**(Beg2+2); 
	*Out = *(Beg1)**(Beg2+1)-*(Beg1+1)**(Beg2); 
	return;
}

//Normalizes a vector and returns its starting module
//InIt must be copyable
template<typename T, typename InIt>
T VectorOpearations::Normalize (InIt Beg, InIt End) {
	if (Beg != End) {
		auto CopyBeg = Beg;
		T Module = 0;
		while (CopyBeg != End) {
			Module += *CopyBeg**CopyBeg;
			++CopyBeg;
		}
		Module = std::sqrt(Module);
		while (Beg != End) {
			*Beg /= Module;
			++Beg;
		}
		return Module;
	}
	return {};
}

//Computes variation vector of 2 vectors with respect to DeltaS
//The distance between Beg1 and End1 must be at least the same for Beg2 and its ending
//DeltaS must be non-zero.
template<typename T, typename InIt, typename OutIt>
void VectorOpearations::GetVariation (const T DeltaS, OutIt Out, InIt Beg1, InIt End1, InIt Beg2) {
	while (Beg1 != End1) {
		*Out = (*Beg2-*Beg1)/DeltaS;
		++Out;
		++Beg1;
		++Beg2;
	}
	return;
}

#endif