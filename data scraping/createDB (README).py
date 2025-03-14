'''
would be file to run all of the code in this directory
the current run order for everything to work nicely is:

getMentionsMathsAbbrevs - finds every plot and table for input folder full of folders containing LATEX.txt META_INFO.txt 
and saves to .json file. Additionally it saves the caption of the figure, every sentence it was mentioned in the overall paper
every piece of latex maths present in mentions and caption, along with the first sentence that latex appeared in in the paper.
Every abbreviation in the caption and mentions are also saved along with a long form definition that is calculated from its
overall context in the paper.

getMathsDefinitionsAsyncGPT - calls the OpenAI API to determine what each piece of latex represents, given its initial context.
The context field is replaced with the found definition given by the API (using 4o-mini)

getKeywordsAsyncGPT - calls OpenAI API to determine 5 (or whatever set) keywords to describe each plot/table, and adds to json.

splitMentions - splits ["mentions"] key into ["caption"] and ["mentions"] splitting the mentions from the actual caption

Image scraping folder - these scripts create a json for each paper containing the urls of the images of the plots, different files ran for 
each data type (e.g CMS, ATLAS Paper, CONF note)

Merge folder - these scripts  merge these link jsons with the current overall database
at this stage or early it might make sense to create different databases for each input data type and merge later
since they only work on the specific input type they were designed for
-potential for improvement here!

Now back with database of figures now with links to images attached (sometimes more than one)

splitPlots - splits any figures with more than one image into subplots e.g Figure 7 has 4 images - turns into Figure 7 (a)
Figure 7 (b) etc... 

getGraphTypeLLM - downloads and runs CLIP model locally to determine the plot type from a pre-determined list of options
(reccommend refining these options)

embedding - creates an embedding matrix for each figure and adds to the json, can tailor which parts of each figure
form part of the embedding matrix, which could effect search results, this completes the database, which can now be loaded by 
app_chroma in the App Product folder and be vector searched upon.
'''