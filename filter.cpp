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
    DataT alpha = 0.1;
    bool weighted = 0;
    string delimiter = " ";

    //terminal options loop
    opterr = 0;
    char c;
    while ((c = getopt(argc, argv, "a:d:f:o:w")) != -1)
        switch (c)
        {
        case 'a':// select filter alpha
            alpha = stof(optarg);
            break;

        case 'd':// select output file
            delimiter = optarg;
            break;

        case 'f':// select input file
            infile = optarg;
            break;
        
        case 'o':// select output file
            outfile = optarg;
            break;
        
        case 'w':// weighted? 
            if (stoi(optarg) != 0) weighted = true;
            break;

        case '?':
            fprintf(stderr, "Option -%c does not exists, or requires an argument.\n", optopt);
            return 1;
        default:
            abort();
        }

    CSR cmat;
    cmat.read_edgelist(infile);
    disparity_filter(cmat, alpha);
    cmat.save_to_edgelist(outfile);

}
