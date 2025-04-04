# Physics-Project
Group 3's repository for the group project.

The following is the full process in which the data processing team converted the data provided in directories into a fully embeded vector database. Ready for vector searches to be run on it.

## Paper Data Extraction

The first part of the code extracts the necessary information, from the directories of paper files. This is done using the following python script: getMentionsMathsAbbrevs.py.
This script takes in the directory of the papers of each experiment such as ATLAS or CMS. It then ouptuts the generated data in a file location of your choice. The format should be of the following format:


       {
        "name": "Figure 2",
        "mentions": [
            "Figure 2a shows the \\(S/\\sqrt{B}\\) and \\(S/B\\) ratios for the different regions under consideration in the single-lepton channel based on the simulations described in Sect",
            "The expected proportions of different backgrounds in each region are shown in Fig. 2b",
            "Figure 2: Single-lepton channel: a \\(S/\\sqrt{B}\\) ratio for each of the regions assuming SM cross sections and branching fractions, and \\(m_{H}=125\\,\\mathrm{GeV}\\)"
        ],
        "atlusUrl": "https://cds.cern.ch/record/2001975",
        "paper": "CDS_Record_2001975",
        "paperName": "Search for the Standard Model Higgs boson produced in association with top quarks and decaying into $b\\bar{b}$ in pp collisions at $\\sqrt{s}$ = 8 TeV with the ATLAS detector",
        "abbrevs": [
            "SM"
        ],
        "abbrevDefinitions": [
            "Standard Model"
        ],
        "maths": [
            "\\(S/\\sqrt{B}\\)",
            "\\(S/B\\)",
            "\\(m_{H}=125\\,\\mathrm{GeV}\\)"
        ],
        "mathsContext": [
            "Figure 2a shows the \\(S/\\sqrt{B}\\) and \\(S/B\\) ratios for the different regions under consideration in the single-lepton channel based on the simulations described in Sect",
            "Figure 2a shows the \\(S/\\sqrt{B}\\) and \\(S/B\\) ratios for the different regions under consideration in the single-lepton channel based on the simulations described in Sect",
            "The regions with a signal-to-background ratio \\(S/B>1\\,\\%\\) and \\(S/\\sqrt{B}>0.3\\), where \\(S\\) and \\(B\\) denote the expected signal for a SM Higgs boson with \\(m_{H}=125\\,\\mathrm{GeV}\\), and background, respectively, are referred to as \"signal-rich regions\", as they provide most of the sensitivity to the signal"
        ]
    },


This should therefore extract the name of each figure, its caption and mentions under the heading mentions, the atlas url, which will indicate the paper from which this image came from. Then the CDS_Record name of the paper and the actual scientific paper name from which the image was sourced. It also extracts and defines abbreviations, and captures instances of latex maths in the caption and mentions and stores the context it was defined in.

Subsequent scripts add additional information, define latex maths using api calls, and refine datafields. Outlined further in Data Scraping readme.

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
        "name": "Figure 6",
        "atlusUrl": "https://cds.cern.ch/record/2002197",
        "paper": "CDS_Record_2002197",
        "paperName": "Search for vector-like $B$ quarks in events with one isolated lepton, missing transverse momentum and jets at $\\sqrt{s}=$ 8 TeV with the ATLAS detector",
        "abbrevs": [],
        "abbrevDefinitions": [],
        "maths": [
            "\\(-1\\)",
            "\\(+0.95\\)"
        ],
        "mathsDefinitions": [
            "Background-like events.",
            "Upper boundary of the background-dominated region in BDT values."
        ],
        "keywords": "BDT discriminant, signal region, uniform binning, nonuniform binning, exclusion limits, background-dominated region, observed limit curve, expected limit curve, signal-enriched bins.",
        "mentions": [
            "Figure 6 shows the distribution of the BDT discriminant for data in the signal region of the BDT analysis",
            "Figure 6(a) shows the entire range of the BDT discriminant with uniform binning",
            "Figure 6(b) shows the same data in the nonuniform binning optimized for the determination of the final exclusion limits, with the background-dominated region of BDT values from \\(-1\\) to \\(+0.95\\) combined in a single bin.\n",
            "The final discriminating variable for the BDT analysis is the distribution of the BDT discriminant, using the binning in Fig. 6(b)",
            "The observed limit curve is slightly lower than the expected limit curve due to the small deficit of observed events in Fig. 6(b), compared to the background expectation, in the signal-enriched bins of the BDT discriminant near a value of 1.0"
        ],
        "caption": "Figure 6: (color online)",
        "imageUrls": [
            "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/EXOT-2014-17///.thumb_fig_06a.png",
            "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/EXOT-2014-17///.thumb_fig_06b.png"
        ]
    },

The plots must then be split into subplots, and then an ai model can be used to catagorise plot type, using splitPlots andGetGraphTypeLLM.

# Merging the JSON databases 

The following code will merge however many JSON databases you have produced, currently it is set to 3 JSON files and merging them into 1 put it can be easily adapted. This code is found in the first section of the Combining and clearing code.py python script.

# Embedding the database

The following code will embed the database with vectors so that the vector search can be run on it. The code for this is called Embedding.py. Having run this the database should have the following output format.

     {
        "name": "Figure 2 (a)",
        "atlusUrl": "https://cds.cern.ch/record/2001975",
        "paper": "CDS_Record_2001975",
        "paperName": "Search for the Standard Model Higgs boson produced in association with top quarks and decaying into $b\\bar{b}$ in pp collisions at $\\sqrt{s}$ = 8 TeV with the ATLAS detector",
        "abbrevs": [
            "SM"
        ],
        "abbrevDefinitions": [
            "Standard Model"
        ],
        "maths": [
            "\\(S/\\sqrt{B}\\)",
            "\\(S/B\\)",
            "\\(m_{H}=125\\,\\mathrm{GeV}\\)"
        ],
        "mathsDefinitions": [
            "Signal-to-background significance ratio.",
            "Signal-to-background ratio.",
            "Mass of the Standard Model Higgs boson, approximately 125 GeV."
        ],
        "keywords": "Single-lepton channel, ratios, backgrounds, simulations, SM cross sections, branching fractions.",
        "mentions": [
            "Figure 2a shows the \\(S/\\sqrt{B}\\) and \\(S/B\\) ratios for the different regions under consideration in the single-lepton channel based on the simulations described in Sect",
            "The expected proportions of different backgrounds in each region are shown in Fig. 2b"
        ],
        "caption": "Figure 2: Single-lepton channel: a \\(S/\\sqrt{B}\\) ratio for each of the regions assuming SM (Standard Model) cross sections and branching fractions, and \\(m_{H}=125\\,\\mathrm{GeV}\\)",
        "imageUrls": "https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/HIGG-2013-27///.thumb_fig_02a.png",
        "figureType": "Residual or Pull Distribution",
        "embeddedVector": [
            -0.03530595824122429,
            .... (very long)
        ]
    },

# Cleaning up the database
This code cleans up the database for any sections in which the url entries were found to be empty due to missing images not being available on the corresponding websites.
This code is the second part of the Combining and clearing code.py python script.

Having run all of this code in this order you should now have succesfully made a vector database.