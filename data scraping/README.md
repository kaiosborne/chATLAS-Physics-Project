# Physics-Project
Group 17a's repository for the group project.

The following is the full process in which the data processing team converted the data provided in directories into a fully embeded vector database. Ready for vector searches to be run on it.

## Paper Data Extraction

The first part of the code extracts the necessary information, from the directories of paper files. This is done using the following python script: get-mentions.py which is part of the data scraping algorthm of the github.
This script takes in the directory of the papers of each experiment such as ATLAS or CMS. It then ouptuts the generated data in a file location of your choice. The format should be of the following format:


        {

        "name": "Figure 1",
        "mentions": [
            "Figure 1(a) shows the local \\(p\\)-value as a function of \\(m_{X}\\) for a narrow resonance that decays into a pair of SM Higgs bosons whose decay branching ratios are predicted under \\(m_{h}=125\\,\\mathrm{GeV}\\)",
            "Figure 1(b) shows the upper limits at the 95% confidence level (CL) on the resonant \\(hh\\) production cross section as a function of \\(m_{X}\\), assuming that \\(h\\) is the SM Higgs boson",
            "Figure 1: (a) Local \\(p\\)-value and (b) observed and expected upper limits at the 95% CL on the resonant Higgs boson pair production cross section as a function of the resonance mass \\(m_{X}\\)"
        ],
        "atlusUrl": "https://cds.cern.ch/record/2882365",
        "paper": "CDS_Record_2882365",
        "paperName": "Combination of searches for resonant Higgs boson pair production using $pp$ collisions at $\\sqrt{s}=13$ TeV with the ATLAS detector"
    },


This should therefore extract the name of each figure, its caption and mentions under the heading mentions, the atlas url, which will indicate the paper from which this image came from. Then the CDS_Record name of the paper and the actual scientific paper name from which the image was sourced.

## Image URL extraction

The next scripts are individually tailored to each experiments format in which the image meta data files were formated. Essentially the code works by looking at the paper directory, then opening each meta data file, finding the url. This leads to an html page on which there should normally be a link leading to the page particular which contains the locations of all the images within that paper. In some cases the image urls are embedded on the initial page without needing to go to another html link.
The python scripts for this process are found in the image scraping folder on the github repository they are called: ATLAS CONFERENCE NOTES URL EXTRACTION.py, ATLAS IMAGE URL EXTRACTION.py and CMS URL Extraction.py. This should give an output of this : 


    {
        "name": ".thumb_fig_01.png",
        "url": "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SOFT-2010-01///.thumb_fig_01.png"
    },
    {
        "name": ".thumb_fig_02.png",
        "url": "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SOFT-2010-01///.thumb_fig_02.png"
    },
    {
        "name": ".thumb_fig_03.png",
        "url": "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SOFT-2010-01///.thumb_fig_03.png"
    }
The code takes in the paper directory and returns a directory of JSON files each named after the paper from which the images were extracted.

## Image URL merging with paper data 

The following section takes the image url directory for each paper set as well as the output paper data for each section and merges them to the correct image entries.
The code for this is once again available on the github repository under the folder merge: ATLAS CONFERENCE MERGE.py, ATLAS MERGE.py, CMS MERGE.py.
This will output something of this format :

    {

        "name": "Figure 1",
        "mentions": [
            "Figure 1(a) shows the local \\(p\\)-value as a function of \\(m_{X}\\) for a narrow resonance that decays into a pair of SM Higgs bosons whose decay branching ratios are predicted under \\(m_{h}=125\\,\\mathrm{GeV}\\)",
            "Figure 1(b) shows the upper limits at the 95% confidence level (CL) on the resonant \\(hh\\) production cross section as a function of \\(m_{X}\\), assuming that \\(h\\) is the SM Higgs boson",
            "Figure 1: (a) Local \\(p\\)-value and (b) observed and expected upper limits at the 95% CL on the resonant Higgs boson pair production cross section as a function of the resonance mass \\(m_{X}\\)"
        ],
        "atlusUrl": "https://cds.cern.ch/record/2882365",
        "paper": "CDS_Record_2882365",
        "paperName": "Combination of searches for resonant Higgs boson pair production using $pp$ collisions at $\\sqrt{s}=13$ TeV with the ATLAS detector",
        "imageUrls": [
            "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/HDBS-2023-17///.thumb_fig_01a.png",
            "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/HDBS-2023-17///.thumb_fig_01b.png"
        ]
    }

# Merging the JSON databases 

The following code will merge however many JSON databases you have produced, currently it is set to 3 JSON files and merging them into 1 put it can be easily adapted. This code is found in the first section of the Combining and clearing code.py python script.

# Embedding the database

The following code will embed the database with vectors so that the vector search can be run on it. The code for this is called Embedding.py. Having run this the database should have the following output format.

     {
        "name": "Figure 1",
        "mentions": [
            "Figure 1(a) shows the local \\(p\\)-value as a function of \\(m_{X}\\) for a narrow resonance that decays into a pair of SM Higgs bosons whose decay branching ratios are predicted under \\(m_{h}=125\\,\\mathrm{GeV}\\)",
            "Figure 1(b) shows the upper limits at the 95% confidence level (CL) on the resonant \\(hh\\) production cross section as a function of \\(m_{X}\\), assuming that \\(h\\) is the SM Higgs boson",
            "Figure 1: (a) Local \\(p\\)-value and (b) observed and expected upper limits at the 95% CL on the resonant Higgs boson pair production cross section as a function of the resonance mass \\(m_{X}\\)"
        ],
        "atlusUrl": "https://cds.cern.ch/record/2882365",
        "paper": "CDS_Record_2882365",
        "paperName": "Combination of searches for resonant Higgs boson pair production using $pp$ collisions at $\\sqrt{s}=13$ TeV with the ATLAS detector",
        "imageUrls": [
            "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/HDBS-2023-17///.thumb_fig_01a.png",
            "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/HDBS-2023-17///.thumb_fig_01b.png"
        ],
        "embedded vector": [
            -0.09764965623617172,
            0.052059356123209,
            0.0385596826672554,
            ....
        ]
    }

# Cleaning up the database
This code cleans up the database for any sections in which the url entries were found to be empty due to missing images not being available on the corresponding websites.
This code is the second part of the Combining and clearing code.py python script.

Having run all of this code in this order you should now have succesfully made a vector database.