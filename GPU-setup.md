# Setting up GPUs 

This document details how to access GPUs from a Jupyter notebook.

## Logging on 

Use SSH to get into “login node”. Eg.  ssh xzcapwel@dias.hpc.phys.ucl.ac.uk

## Preliminary setup

When you first login to the login node the following needs to be performed. Note that these steps only have to be preformed once.

### Create virtual environment

Run the following lines (explanations are given in brackets):
```
eval "$(/share/apps/anaconda/3-2022.05/bin/conda shell.bash hook)" 
```
(Starts conda shell)

```
conda activate
```
(activates conda in your current shell)

```
export TMPDIR=/state/partition1/tmp
```
(not sure if this is required)

```
conda create -n myenv python=3.10 pip
```
(creates a virtual environment called `myenv`)

```
conda activate myenv
```
(activates the `myenv` virtual environment)

```
pip install nougat-ocr
pip install notebook
```
(installs required libraries in virtual environment, note you can just do this in the notebook)

```
conda deactivate
```
(exit myenv and conda environments)

### Modify SH files

In this method, the .sh folders are directly modified so that the GPU is set up straight away with the virtual environment required (the myenv environment created in the last step). 

The orginal .sh files can be copied via command
```
cp /share/apps/anaconda/jupyter-slurm-singularity.sh /share/apps/anaconda/singularity-jupyter.sh
```

The jupyter-slurm-singuarity.sh file sets up the GPU requirements. The final line runs singularity-jupyter.sh which lauches Jupyter notebooks in the myenv environment.

The SSH files have to each be edited via the nano command in order to set up the correct GPU and virtual machine.

The changes in jupyter-slurm-singularity.sh are:

Change the 1st line to
```
#!/bin/bash -l 
```
(required for the bash shell to start with the correct properties, I think)

Add bellow the 2nd line
```
#SBATCH --gres=gpu:a100:1
```
(means your only asking for one GPU)

In singularity-jupyter.sh replace the whole document with:

```
#!/bin/bash -l
eval "$(/share/apps/anaconda/3-2022.05/bin/conda shell.bash hook)"
conda init bash
conda activate
export TMPDIR=/state/partition1/tmp
conda activate myenv
jupyter-notebook --no-browser --port=${port} --ip=${node}
```

The first line tells the terminal to run this script as bash. The 2nd to 4th lines get the conda that is required and activates the myenv virtual environment. The 5th line changes the temporary directory of the bash shell to /state/partition1/tmp (means any data wont be accidentally deleted). The 6th runs Jupyter notebook on a GPU at the correct location.


## Getting to the notebooks

Run the following commands to open jupyter notebooks with the GPU:
```
sbatch jupyter-slurm-singularity.sh
```
(runs jupyter-slurm-singularity.sh)

```
cat jupyter-notebook-*.log 
```
(displays text in .log file)

if you have more than one .log file then replace * with the number returned by the last command. May need to be run several times until output is seen.
 
Inside the .log file, copy the 2nd line and run it in a local bash shell (sets up tunnel with GPU). The 2nd line will look something like 
> ssh -N -L PPPP:compute-gpu-0-1:PPPP UUU@dias.hpc.phys.ucl.ac.uk

(connects to dias.hpc.phys.ucl.ac.uk and sets up a tunnel so we can see the notebook in a browser on our machine)
Find the web address in the form http://127.0.0.1:PPPP/tree, this is the location of the jupyter notebook. Open this in a browser

## Notes

* The memory allocated may need to be increased more for some of the larger files
* Any other required libraries can be installed either in the Conda shell or in a Jupyter notebook itself (pip commands can be run with a !)
