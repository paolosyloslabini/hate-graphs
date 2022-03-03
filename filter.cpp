#include "comp_mats.h"
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <fstream> //ifstream

#include <cmath> // std::abs
#include <string>
#include <map>
#include <set>

#include <random>
#include <vector>
#include <algorithm>    //

#include <unistd.h> //getopt, optarg


using namespace std;

int main(int argc, char* argv[])
{

    string infile;
    string outfile = "test_output.txt";

    //terminal options loop
    opterr = 0;
    char c;
    while ((c = getopt(argc, argv, "f:o")) != -1)
        switch (c)
        {
        case 'f':// select input file
            infile = optarg;
            break;
        
        case 'o':// select input file
            outfile = optarg;
            break;
        
        case '?':
            fprintf(stderr, "Option -%c does not exists, or requires an argument.\n", optopt);
            return 1;
        default:
            abort();
        }

    CSR cmat;
    cmat.read_edgelist(infile);
    cmat.save_to_edgelist(infile);

}
