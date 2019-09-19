// -*- mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*-
#include "stemparameter.h"

#include "Organism.h"

#include <cmath>
#include <iostream>
#include <chrono>
#include <assert.h>

namespace CRootBox {

/**
 * @return Mean maximal stem length of this stem type
 */
double StemSpecificParameter::getK() const {
    double l = std::accumulate(ln.begin(), ln.end(), 0.);
    return l+la+lb;
}

/**
 * @copydoc OrganParameter::toString()
 */
std::string StemSpecificParameter::toString() const
{
    std::stringstream str;
    str << "subType\t" << subType << std::endl;
    str << "lb\t" << lb << std::endl << "la\t" << la << std::endl;
    str << "nob\t" << nob << std::endl << "r\t" << r << std::endl << "a\t" << a << std::endl;
    str << "theta\t" << theta << std::endl << "rlt\t" << rlt << std::endl;
    str << "ln\t";
    for (int i=0; i<ln.size(); i++) {
        str << ln[i] << " ";
    }
    str << std::endl;
    return str.str();
}



/**
 * Default constructor sets up hashmaps for class introspection
 */
StemRandomParameter::StemRandomParameter(Organism* p) :OrganRandomParameter(p)
{
    // base class default values
    name = "undefined";
    organType = Organism::ot_stem;
    subType = -1;
    f_tf = new Tropism(p);
    bindParmeters();
}

/**
 * Destructor: delete all callback functions
 */
StemRandomParameter::~StemRandomParameter()
{
    delete f_tf;
    delete f_gf;
    delete f_se;
    delete f_sa;
    delete f_sbp;
}

/**
 * @copydoc OrganTypeParameter::copy()
 */
OrganRandomParameter* StemRandomParameter::copy(Organism* p)
{
    StemRandomParameter* r = new StemRandomParameter(*this); // copy constructor breaks class introspection
    r->plant = p;
    r->bindParmeters(); // fix class introspection
    r->f_tf = f_tf->copy(p); // copy call back classes
    r->f_gf = f_gf->copy();
    r->f_se = f_se->copy();
    r->f_sa = f_sa->copy();
    r->f_sbp = f_sbp->copy();
    return r;
}

/**
 * @copydoc OrganTypeParameter::realize()
 *
 * Creates a specific stem from the stem type parameters.
 * @return Specific stem parameters derived from the stem type parameters
 */
OrganSpecificParameter* StemRandomParameter::realize()
{
    //& std::cout << "StemTypeParameter::realize(): subType " << subType << "\n" << std::flush;
    double lb_ = std::max(lb + plant->randn()*lbs, 0.); // length of basal zone
    double la_ = std::max(la + plant->randn()*las, 0.); // length of apical zone
    std::vector<double> ln_; // stores the inter-distances
    int nob_ = std::max(round(nob + plant->randn()*nobs), 0.); // maximal number of branches
    	switch(lnf) {
		case 0: // homogeneously distributed stem nodes
		for (int i = 0; i<nob_-1; i++) { // create inter-stem distances
			double d = std::max(ln +plant->randn()*lns,1e-9); //Normal function of equal internode distance
			ln_.push_back(d);


		}break;
		case 1: //  nodes distance increase linearly
		for (int i = 0; i<nob_*2-1; i++) { // create inter-stem distances
			double d =  std::max(ln*(1+i) +plant->randn()*lns,1e-9); //std::max(  );//ln +plant->randn()*lns,1e-9);
			ln_.push_back(d);
			ln_.push_back(0);

		}break;
		case 2: //nodes distance decrease linearly
		for (int i = 0; i<nob_-1; i++) { // create inter-stem distances
			double d =  std::max(ln*(1+i) +plant->randn()*lns,1e-9); //std::max(  );//ln +plant->randn()*lns,1e-9);
			ln_.push_back(d);

		}break;
		case 3: //nodes distance decrease exponential
		for (int i = 0; i<nob_-1; i++) { // create inter-stem distances
			double d =  std::max(ln +plant->randn()*lns,1e-9); //std::max(  );//ln +plant->randn()*lns,1e-9);
			ln_.push_back(d);

		}break;

		case 4://nodes distance decrease exponential
		for (int i = 0; i<nob_*2-1; i++) { // create inter-stem distances
			double d =  std::max(ln/(1+i) +plant->randn()*lns,1e-9); //std::max(  );//ln +plant->randn()*lns,1e-9);
			ln_.push_back(d);
			ln_.push_back(0);
		} break;
		case 5://nodes distance decrease exponential
		for (int i = 0; i<nob_*2-1; i++) { // create inter-stem distances
			double d =  std::max(ln/(1+i) +plant->randn()*lns,1e-9); //std::max(  );//ln +plant->randn()*lns,1e-9);
			ln_.push_back(d);
		};break;
default:
		throw 1; // TODO make a nice one
	}


    double r_ = std::max(r + plant->randn()*rs, 0.); // initial elongation
    double a_ = std::max(a + plant->randn()*as, 0.); // radius
    double theta_ = std::max(theta + plant->randn()*thetas, 0.); // initial elongation
    double rlt_ = std::max(rlt + plant->randn()*rlts, 0.); // stem life time
    OrganSpecificParameter* p = new StemSpecificParameter(subType,lb_,la_,ln_,nob_,r_,a_,theta_,rlt_);
    return p;
}

/**
 * Choose (dice) lateral type based on stem parameters successor and successorP
 *
 * @param pos       spatial position (for coupling to a soil model)
 * @return          stem sub type of the lateral stem
 */
int StemRandomParameter::getLateralType(const Vector3d& pos)
{
    assert(successor.size()==successorP.size()
        && "StemTypeParameter::getLateralType: Successor sub type and probability vector does not have the same size");
    if (successorP.size()>0) { // at least 1 successor type
        double d = plant->rand(); // in [0,1]
        int i=0;
        double p=successorP.at(i);
        i++;
        while ((p<d) && (i<successorP.size())) {
            p+=successorP.at(i);
            i++;
        }
        if (p>=d) { // success
            // std::cout << "lateral type " << successor.at(i-1) << "\n" << std::flush;
            return successor.at(i-1);
        } else { // no successors
            // std::cout << "no lateral type " << std::flush;
            return -1;
        }
    } else {
        return -1; // no successors
    }
}

/**
 * @copydoc OrganTypeParameter::toString()
 *
 * We need to add the parameters that are not in the hashmaps (i.e. successor, and successorP)
 */
std::string StemRandomParameter::toString(bool verbose) const {

    if (verbose) {
        std::string s = OrganRandomParameter::toString(true);
        std::stringstream str;
        str << "successor\t";
        for (int i=0; i<successor.size(); i++) {
            str << successor[i] << " ";
        }
        str << "\t" << description.at("successor") << std::endl;
        str << "successorP\t";
        for (int i=0; i<successorP.size(); i++) {
            str << successorP[i] << " ";
        }
        str << "\t" << description.at("successorP") << std::endl;
        return s.insert(s.length()-4, str.str());
    } else {
        return OrganRandomParameter::toString(false);
    }

}

/**
 * @copydoc OrganTypeParameter::readXML()
 *
 * We need to add the parameters that are not in the hashmaps (i.e. successor, and successorP)
 *
 * If the parameter successor or successorP are not in the element, they are set to zero size.
 */
void StemRandomParameter::readXML(tinyxml2::XMLElement* element)
{
    OrganRandomParameter::readXML(element);
    tinyxml2::XMLElement* p = element->FirstChildElement("parameter");
    successor.resize(0);
    successorP.resize(0);
    while(p) {
        std::string key = p->Attribute("name");
        if (key.compare("successor")==0)  {
            successor.push_back(p->IntAttribute("type"));
            successorP.push_back(p->DoubleAttribute("percentage"));
        }
        p = p->NextSiblingElement("parameter");
    }
    double p_ = std::accumulate(successorP.begin(), successorP.end(), 0.);
    if  ((p_<1) && (p_!=0))  {
        std::cout << "StemRandomParameter::readXML: Warning! percentages to not add up to 1. \n";
    }
    assert(successor.size()==successorP.size() &&
        "StemTypeParameter::readXML: Successor sub type and probability vector does not have the same size" );
}

/**
 * @copydoc OrganTypeParameter::writeXML()
 *
 * We need to add the parameters that are not in the hashmaps (i.e. successor, and successorP)
 */
tinyxml2::XMLElement* StemRandomParameter::writeXML(tinyxml2::XMLDocument& doc, bool comments) const
{
    assert(successor.size()==successorP.size() &&
        "StemTypeParameter::writeXML: Successor sub type and probability vector does not have the same size" );
    tinyxml2::XMLElement* element = OrganRandomParameter::writeXML(doc, comments);
    for (int i = 0; i<successor.size(); i++) {
        tinyxml2::XMLElement* p = doc.NewElement("parameter");
        p->SetAttribute("name", "successor");
        p->SetAttribute("number", i);
        p->SetAttribute("type", successor[i]);
        p->SetAttribute("percentage", float(successorP[i]));
        element->InsertEndChild(p);
        if (comments) {
            std::string str = description.at("successor");
            tinyxml2::XMLComment* c = doc.NewComment(str.c_str());
            element->InsertEndChild(c);
        }

    }
    double p_ = std::accumulate(successorP.begin(), successorP.end(), 0.);
    if ((p_<1) && (p_!=0)) {
        std::cout << "StemRandomParameter::writeXML: Warning! percentages do not add up to 1. = " << p_ << "\n";
    }
    return element;
}

/**
 * Sets up class introspection by linking parameter names to their class members,
 * additionally adds a description for each parameter, for toString and writeXML
 */
void StemRandomParameter::bindParmeters()
{
    bindParameter("organType", &organType, "Organ type (unspecified organ = 0, seed = 1, stem = 2, stem = 3, leaf = 4)");
    bindParameter("subType", &subType, "Unique identifier of this sub type");
    bindParameter("lb", &lb, "Basal zone [cm]", &lbs);
    bindParameter("la", &la, "Apical zone [cm]", &las);
    bindParameter("ln", &ln, "Inter-lateral distance [cm]", &lns);
    bindParameter("nob", &nob, "Maximal number of laterals [1]", &nobs);
    bindParameter("r", &r, "Initial growth rate [cm day-1]", &rs);
    bindParameter("a", &r, "Stem radius [cm]", &as);
    bindParameter("RotBeta", &RotBeta, "RevRotation of the stem");
    bindParameter("BetaDev", &BetaDev, "RevRotation deviation");
    bindParameter("InitBeta", &InitBeta, "Initial RevRotation");
    bindParameter("tropismT", &tropismT, "Type of stem tropism (plagio = 0, gravi = 1, exo = 2, hydro, chemo = 3)");
    bindParameter("tropismN", &tropismN, "Number of trials of stem tropism");
    bindParameter("tropismS", &tropismS, "Mean value of expected change of stem tropism [1/cm]");
    bindParameter("dx", &dx, "Axial resolution [cm] (maximal segment size)");
    bindParameter("theta", &theta, "Angle between stem and parent stem [rad]", &thetas);
    bindParameter("rlt", &rlt, "Stem life time [day]", &rlts);
    bindParameter("gf", &gf, "Growth function number [1]", &rlts);
    // other parameters (descriptions only)
    description["name"]  = "Name of the sub type of the organ, e.g. small lateral";
    description["successor"] = "Sub type of lateral stems";
    description["successorP"] = "Probability of each sub type to occur";
}

} // end namespace CRootBox