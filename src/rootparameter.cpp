// -*- mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*-
#include "rootparameter.h"

#include "Organism.h"

#include <cmath>
#include <iostream>
#include <chrono>
#include <assert.h>

namespace CPlantBox {

/**
 * @return Mean maximal root length of this root type
 */
double RootSpecificParameter::getK() const {
    double l = std::accumulate(ln.begin(), ln.end(), 0.);
    return l+la+lb;
}

/**
 * @copydoc OrganParameter::toString()
 */
std::string RootSpecificParameter::toString() const
{
    std::stringstream str;
    str << "subType\t" << subType << std::endl;
    str << "lb\t" << lb << std::endl << "la\t" << la << std::endl;
    str << "nob\t" << nob() << std::endl << "r\t" << r << std::endl << "a\t" << a << std::endl;
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
RootRandomParameter::RootRandomParameter(std::shared_ptr<Organism> plant) :OrganRandomParameter(plant)
{
    // base class default values
    name = "undefined";
    organType = Organism::ot_root;
    subType = -1;
    f_tf = std::make_shared<Tropism>(plant);
    bindParameters();
}

/**
 * @copydoc OrganTypeParameter::copy()
 */
std::shared_ptr<OrganRandomParameter> RootRandomParameter::copy(std::shared_ptr<Organism> p)
{
    // std::cout << "RootRandomParameter::copy\n"<< std::flush;
    auto r = std::make_shared<RootRandomParameter>(*this); // copy constructor breaks class introspection
    r->plant = p;
    r->bindParameters(); // fix class introspection
    r->f_tf = f_tf->copy(p); // copy call back function classes
    r->f_gf = f_gf->copy();
    r->f_se = f_se->copy();
    r->f_sa = f_sa->copy();
    r->f_sbp = f_sbp->copy();
    return r;
}

/**
 * @copydoc OrganTypeParameter::realize()
 *
 * Creates a specific root from the root type parameters.
 * @return Specific root parameters derived from the root type parameters
 */
std::shared_ptr<OrganSpecificParameter> RootRandomParameter::realize()
{
    auto p = plant.lock();
    //& std::cout << "RootTypeParameter::realize(): subType " << subType << "\n" << std::flush;
    double lb_ = std::max(lb + p->randn()*lbs, 0.); // length of basal zone
    double la_ = std::max(la + p->randn()*las, 0.); // length of apical zone
    std::vector<double> ln_; // stores the inter-distances
    int nob_ = std::max(round(nob() + p->randn()*nobs()), 1.); // maximal number of branches
    double sum_ln = nob_*ln; // mean length of lateral zone
    for (int i = 0; i<nob_-1; i++) { // create inter-root distances
    	double z = ((double)i+0.5)*ln; // regular position along root lateral zone
    	double f = lnk*(z-sum_ln/2.); // evaluate slope lnk f(mid) = 0
        double d = std::max(ln * f + p->randn()*lns, 1.e-5); // miminum is 1.e-5
        ln_.push_back(d);
    }
    double r_ = std::max(r + p->randn()*rs, 0.); // initial elongation
    double a_ = std::max(a + p->randn()*as, 0.); // radius
    double theta_ = std::max(theta + p->randn()*thetas, 0.); // initial elongation
    double rlt_ = std::max(rlt + p->randn()*rlts, 0.); // root life time
    return std::make_shared<RootSpecificParameter>(subType,lb_,la_,ln_,nob_,r_,a_,theta_,rlt_);
}

/**
 * Choose (dice) lateral type based on root parameters successor and successorP
 *
 * @param pos       spatial position (for coupling to a soil model)
 * @return          root sub type of the lateral root
 */
int RootRandomParameter::getLateralType(const Vector3d& pos)
{
    assert(successor.size()==successorP.size()
        && "RootTypeParameter::getLateralType: Successor sub type and probability vector does not have the same size");
    if (successorP.size()>0) { // at least 1 successor type
        double d = plant.lock()->rand(); // in [0,1]
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
 * The standard deviation of number of branches is calculated form root maximal length lmax, and
 * its standard deviation lmaxs
 *
 * todo I have no idea why this holds...
 */
double RootRandomParameter::nobs() const
{
    double nobs = (lmaxs/lmax - lns/ln)*lmax/ln; // error propagation
    if (la>0) {
        nobs -= (las/la - lns/ln)*la/ln;
    }
    if (lb>0) {
        nobs -= (lbs/lb - lns/ln)*lb/ln;
    }
    return std::max(nobs,0.);
}

/**
 * @copydoc OrganTypeParameter::toString()
 *
 * We need to add the parameters that are not in the hashmaps (i.e. successor, and successorP)
 */
std::string RootRandomParameter::toString(bool verbose) const {

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
void RootRandomParameter::readXML(tinyxml2::XMLElement* element)
{
    OrganRandomParameter::readXML(element);
    tinyxml2::XMLElement* p = element->FirstChildElement("parameter");
    successor.resize(0);
    successorP.resize(0);
    while(p!=nullptr) {
        const char* str = p->Attribute("name");
        if (str!=nullptr) {
            std::string key = std::string(str);
            if (key.compare("successor")==0)  {
                successor.push_back(p->IntAttribute("type", 1.));
                successorP.push_back(p->DoubleAttribute("percentage", 1.));
            }
        } else {
            std::cout << "RootRandomParameter::readXML: warning! tag has no attribute 'name' \n" << std::flush;
        }
        p = p->NextSiblingElement("parameter");
    }
    double p_ = std::accumulate(successorP.begin(), successorP.end(), 0.);
    if  ((p_<1) && (p_!=0))  {
        std::cout << "RootRandomParameter::readXML: Warning! percentages to not add up to 1. \n";
    }
    assert(successor.size()==successorP.size() &&
        "RootTypeParameter::readXML: Successor sub type and probability vector does not have the same size" );
}

/**
 * @copydoc OrganTypeParameter::writeXML()
 *
 * We only need to add the parameters that are not in the hashmaps (i.e. successor, and successorP)
 */
tinyxml2::XMLElement* RootRandomParameter::writeXML(tinyxml2::XMLDocument& doc, bool comments) const
{
    assert(successor.size()==successorP.size() &&
        "RootTypeParameter::writeXML: Successor sub type and probability vector does not have the same size" );
    tinyxml2::XMLElement* element = OrganRandomParameter::writeXML(doc, comments);
    for (int i = 0; i<successor.size(); i++) {
        tinyxml2::XMLElement* p = doc.NewElement("parameter");
        p->SetAttribute("name", "successor");
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
        std::cout << "RootRandomParameter:  double getK() const { return std::max(nob-1,double(0))*ln+la+lb; }  ///< returns the mean maximal leaf length [cm]:writeXML: Warning! percentages do not add up to 1. = " << p_ << "\n";
    }
    return element;
}

/**
 * CPlantBox parameter reader (DEPRICATED)
 */
void RootRandomParameter::read(std::istream & cin)
{
    std::cout << "RootRandomParameter::read is deprecated, use readXML instead \n";
    char ch[256]; // dummy
    cin.getline(ch,256);
    std::string s; // dummy
    cin >> s >> subType >> s >> name >> s >> lb >> lbs >> s >> la >> las >> s >> ln >> lns >> s >> lmax >> lmaxs;
    cin >> s >> r >> rs >> s >> a >> as >> s >> colorR >> colorG >> colorB >> s >> tropismT >> tropismN >> tropismS >> s >> dx;
    int n;
    cin  >> s >> n;
    successor.clear();
    int is;
    for (int i=0; i<n; i++) {
        cin >> is;
        successor.push_back(is);
    }
    cin >> s >> n;
    successorP.clear();
    double ds;
    for (int i=0; i<n; i++) {
        cin >> ds;
        successorP.push_back(ds);
    }
    cin >> s >> theta >> thetas >> s >> rlt >> rlts >> s >> gf >> s;
}

/**
 * CPlantBox parameter write (DEPRICATED)
 */
void RootRandomParameter::write(std::ostream & cout) const {
    std::cout << "RootRandomParameter::write is deprecated, use writeXML instead \n";
    cout << "# Root type parameter for " << name << "\n";
    cout << "type\t" << subType << "\n" << "name\t" << name << "\n" << "lb\t"<< lb <<"\t"<< lbs << "\n" << "la\t"<< la <<"\t"<< las << "\n"
        << "ln\t" << ln << "\t" << lns << "\n" << "lmax\t"<< lmax <<"\t"<< lmaxs << "\n" << "r\t"<< r <<"\t"<< rs << "\n" <<
        "a\t" << a << "\t" << as << "\n" << "color\t"<< colorR <<"\t"<< colorG << "\t" << colorB << "\n"
        << "tropism\t"<< tropismT <<"\t"<< tropismN << "\t" << tropismS << "\n" << "dx\t" << dx << "\n" << "successor\t" << successor.size() << "\t";
    for (size_t i=0; i<successor.size(); i++) {
        cout << successor[i] << "\t";
    }
    cout << "\n" << "successorP\t" << successorP.size() <<"\t";
    for (size_t i=0; i<successorP.size(); i++) {
        cout << successorP[i] << "\t";
    }
    cout << "\n" << "theta\t" << theta << "\t" << thetas << "\n" << "rlt\t" << rlt << "\t" << rlts << "\n" << "gf\t" << gf << "\n";
}

/**
 * Sets up class introspection by linking parameter names to their class members,
 * additionally adds a description for each parameter, for toString and writeXML
 */
void RootRandomParameter::bindParameters()
{
	OrganRandomParameter::bindParameters();
    bindParameter("lb", &lb, "Basal zone [cm]", &lbs);
    bindParameter("la", &la, "Apical zone [cm]", &las);
    bindParameter("ln", &ln, "Inter-lateral distance [cm]", &lns);
    bindParameter("lmax", &lmax, "Maximal root length [cm]", &lmaxs);
    bindParameter("r", &r, "Initial growth rate [cm day-1]", &rs);
    bindParameter("colorR", &colorR, "Root color, red component [0.-1.]");
    bindParameter("colorG", &colorG, "Root color, green component [0.-1.]");
    bindParameter("colorB", &colorB, "Root color, blue component [0.-1.]");
    bindParameter("tropismT", &tropismT, "Type of root tropism (plagio = 0, gravi = 1, exo = 2, hydro, chemo = 3)");
    bindParameter("tropismN", &tropismN, "Number of trials of root tropism");
    bindParameter("tropismS", &tropismS, "Mean value of expected change of root tropism [1/cm]");
    bindParameter("dx", &dx, "Axial resolution [cm] (maximal segment size)");
    bindParameter("theta", &theta, "Angle between root and parent root [rad]", &thetas);
    bindParameter("rlt", &rlt, "Root life time [day]", &rlts);
    bindParameter("gf", &gf, "Growth function number [1]", &rlts);
   // NEW
    bindParameter("lnk", &lnk, "Slope of inter-lateral distances [1]");
    bindParameter("ldelay", &lnk, "Lateral root emergence delay [day]", &ldelays);
    // other parameters (descriptions only)
    description["successor"] = "Sub type of lateral roots";
    description["successorP"] = "Probability of each sub type to occur";
}

} // end namespace CPlantBox
