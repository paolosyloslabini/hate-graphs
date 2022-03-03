#pragma once
typedef float DataT; //precision for matrix entries
typedef long int intT;

#include <algorithm>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <math.h>       /* pow */



template< typename T >
intT insert_sorted(std::vector<T>& vec, T const& item)
{
    auto pos = std::upper_bound(vec.begin(), vec.end(), item);
    vec.insert
    (
        pos,
        item
    );
    return pos - vec.begin();
}

bool filter(DataT weight, DataT total_weight, intT degree, const DataT alpha)
{
    DataT p = std::pow(1. - (weight / total_weight)), (degree - 1));
    return p < alpha;
}

struct CSR {

    std::vector<std::vector<intT>> ja;    /* pointer-to-pointer to store column (row) indices      */
    std::vector<std::vector<DataT>> ma;   /* pointer-to-pointer to store nonzero entries           */
    bool weighted;

    intT rows()
    {
        return ja.size();
    }

    intT nzcount(intT row)
    {
        return ja[row].size();
    }

    intT add_element(intT row, intT col, DataT val = 1)
    {
        //inefficient. Use binary search?
        if (row >= rows() || col >= rows()) return 1;


        bool exists = std::find(ja[row].begin(), ja[row].end(), col) != std::end(ja[row]);
        if (exists) return 1;

        auto pos = std::upper_bound(ja[row].begin(), ja[row].end(), col) - ja[row].begin(); //find the insert position
        ja[row].insert(ja[row].begin() + pos, col);

        if (weighted)
        {
            ma[row].insert(ma[row].begin() + pos, val);
        }
    }

    int read_edgelist(std::string filename, std::string delimiter = " ", bool weighted = false)
    {
        std::ifstream infile;

        infile.open(filename);
        intT last_node = -1;
        intT current_node;
        std::string temp;
        intT max_column = 0;
        intT i = -1;
        this->weighted = weighted;

        while (infile.peek() == '#' or infile.peek() == '%') infile.ignore(2048, '\n');
        while (getline(infile, temp)) {

            int del_pos = temp.find(delimiter);
            int del_size = delimiter.length();

            //find parent node
            std::string first_node_string = temp.substr(0, del_pos); //retrieve the part of the string before the delimiter
            current_node = stoi(first_node_string);
            temp.erase(0, del_pos + del_size);

            //find child node
            del_pos = temp.find(delimiter);
            std::string second_node_string = temp.substr(0, del_pos); //retrieve the part of the string after the delimiter
            intT child = stoi(second_node_string);
            temp.erase(0, del_pos + del_size);

            //find node value
            DataT weight = 1.0;
            if(weighted)
            {
                //find weight value
                del_pos = temp.find(delimiter);
                std::string weight_string = temp.substr(0, del_pos); //retrieve the part of the string after the delimiter
                weight = stof(second_node_string);
            }

            if (current_node > i)
            {
                while (i < current_node)
                {
                    std::vector<intT> new_ja;
                    std::vector<DataT> new_ma;
                    ja.push_back(new_ja);
                    ma.push_back(new_ma);
                    i++;
                }
            }
            else if (current_node < i)
            {
                std::cerr << "CANNOT READ MATRIX. INDICES MUST INCREASE" << std::endl;
                return 1;
            }
            ja[i].push_back(child);
            ma[i].push_back(weight);
        }
        return 0;
    }

    bool edge_exists(intT row, intT col)
    {
        //inefficient. Use binary search;
        return std::find(ja[row].begin(), ja[row].end(), col) != ja[row].end();
    }

    int symmetrize_add()
    {
        for (intT row = 0; row < rows(); row++)
        {
            auto ja = this->ja[row];
            auto ma = this->ma[row];
            intT degree = this->nzcount(row);
            for (intT nz = 0; nz < degree; nz++)
            {
                intT col = ja[nz];
                DataT weight = ma[nz];

                //add edge if not present
                if (col > row && !edge_exists(row, col))
                {
                    intT insertion_pos = insert_sorted(ja, col);
                    ma.insert(ma.begin() + insertion_pos, weight);
                }
            }
        }
        return 0;
    }

    int symmetrize_del()
    {
        for (intT row = 0; row < rows(); row++)
        {
            auto ja = this->ja[row];
            auto ma = this->ma[row];
            intT degree = this->nzcount(row);
            for (intT nz = 0; nz < degree; nz++)
            {
                intT col = ja[nz];

                //flag edge if the symmetric is not present
                if (col > row && !edge_exists(row, col))
                {
                    ja[nz] = -1;
                    ma[nz] = -1;
                }
            }
            //remove flagged elements. Keep order;
            ja.erase(remove(ja.begin(), ja.end(), -1), ja.end());
            ma.erase(remove(ma.begin(), ma.end(), -1), ma.end());
        }
        return 0;
    }

    int save_to_edgelist(std::string filename, std::string delimiter = " ")
    {
        std::ofstream outfile(filename);
        for (intT row = 0; row < rows(); row++)
        {
            auto ja = this->ja[row];
            auto ma = this->ma[row];
            for (intT nz = 0; nz < ja.size(); nz++)
            {
                intT col = ja[nz];
                DataT weight = ma[nz];
                outfile << row << delimiter << col << delimiter << weight << std::endl;
            }
        }
        outfile.close();
        return 0;
    }
};



int disparity_filter(CSR& cmat, DataT alpha)
{
    //NON negative weights only

    //GENERATE THE VECTOR OF SUMS
    std::vector<DataT> weight_sums(cmat.rows(), 0.0);
    for (intT i = 0; i < cmat.rows(); i++)
    {
        for (auto w : cmat.ma[i])
        {
            weight_sums[i] += w;
        }
    }


    //APPLY FILTER
    for (intT row = 0; row < cmat.rows(); row++)
    {
        intT degree = cmat.nzcount(row);
        auto weight_sum = weight_sums[row];
        auto ja = cmat.ja[row];
        auto ma = cmat.ma[row];

        for (intT nz = 0; nz < degree; nz++)
        {

            DataT weight = ma[nz];
            if (filter(weight, weight_sum, degree, alpha))
            {
                //flag elements for removal
                ja[nz] = -1;
                ma[nz] = -1;
            }

            //remove flagged elements. Keep order;
            ja.erase(remove(ja.begin(), ja.end(), -1), ja.end());
            ma.erase(remove(ma.begin(), ma.end(), -1), ma.end());
        }
    }

    return 0;
}