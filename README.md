# CMT-R

This is an implementation for training Multinomial Logit (MNL) choice models intended to be used in conjunction with the Choice Model Trees / Market Segmentation Trees package (https://github.com/rtm2130/MST/). Our MNL implementation calls the R-based mnlogit package which has relatively fast computation time. Currently, our implementation only supports Python 2.7 and has only been tested in OS X, Python 2.7.15, and R 3.6.1.

To use this package with MSTs, simply drag and drop all files in this repository into the https://github.com/rtm2130/MST/ directory (overwriting where applicable). Please note that this repo has the GPLv2 license, which is more restrictive on terms of use than the MST repo's MIT license. 

## Package Installation

### Prerequisites

First, clone the MST and CMT-R repos. This can be done through opening a command prompt / terminal and typing: `git clone https://github.com/rtm2130/MST.git` followed by `git clone https://github.com/rtm2130/CMT-R.git` (if these commands do not work then install git). Drag and drop all files from the CMT-R directory into the MST directory, overwriting files with the same name whenever prompted.

Install the conda command-line tool. This can be accomplished through installing miniforge, miniconda, or anaconda. We advise users to consult the license terms of use for these tools because as of 2023-02-26 miniconda and anaconda are not free for commercial use.

Open a command prompt / terminal and execute the following steps:
1. Update conda: `conda update -n base -c defaults conda`
2. Install the conda-forge channel into conda: `conda config --add channels conda-forge`

### Installing Package Dependencies Except for mnlogit

In this step, we will be creating a new conda virtual environment called `mstenv` which will contain Python 2.7.15, R 3.6.1, and the package dependencies except for the mnlogit package. Open a command prompt / terminal and execute the steps below.

#### Installation Method 1 (OS X only): Install virtual environment .yml file

1. Navigate into the MST directory: `cd MST`
2. Build the recommended MST virtual environment which will be named mstenv: `conda env create -n mstenv --file environment_mst.yml`
3. To test the install, activate the newly-created MST virtual environment: `conda activate mstenv`.
4. If the command was successful, deactivate the environment: `conda deactivate`. 

#### Installation Method 2: Build the environment from scratch

1. Build a new MST virtual environment which will be named mstenv with the recommended Python and R versions: `conda create --name mstenv python=2.7.15 r-essentials r-base=3.6.1`
2. Activate the newly-created MST virtual environment: `conda activate mstenv`. All subsequent steps should be followed within the activated virtual environment. 
3. Install the pandas, scikit-learn, joblib, and rpy2 packages. Execute the following: `conda install pandas`, `conda install scikit-learn`, `conda install -c anaconda joblib`, `conda install -c r rpy2`
4. Install tensorflow ensuring compatibility with python 2.7. The following worked for us: `pip install --upgrade tensorflow`
5. Install the R package dependencies. Execute the following: `conda install -c conda-forge r-data.table  r-matrixstats=0.57.0 r-mlogit=1.1.1`. If these commands do not work then you may need to install additional channels, e.g. `conda config --add channels defaults` and `conda config --add channels bioconda`
6. Deactivate the environment: `conda deactivate`

### Installing mnlogit

1. Navigate into the MST directory (`cd MST`) and activate the newly-created MST virtual environment (`conda activate mstenv`). All subsequent steps should be followed within the activated virtual environment.
2. Install the mnlogit package into the virtual environment. We present two approaches for doing so.

Approach 1: Type `R` in the command prompt / terminal and hit ENTER. This will open up the R command prompt. Enter the command `install.packages("mnlogit_1.2.6.tar.gz", repos=NULL, type="source")`. If any errors occur in the package installation, try Approach 2 instead. Exit from R command prompt through typing `q()` followed by `n`.

Approach 2: This approach will use RStudio to install the package. First, install RStudio if it is not present on your computer. Next, open RStudio from command prompt / terminal within the activated virtual environment. We emphasize RStudio must be opened via command line rather than simply clicking on the application. For OS X, this can be accomplished by entering in terminal the following command: `/Applications/RStudio.app/Contents/MacOS/RStudio`. Within RStudio, click on "Tools" and "Install Packages". In the "Install from" field, click "Package Archive File" and direct the package install to the "mnlogit_1.2.6.tar.gz" file within the MST directory. Click "Install" and close RStudio.

3. Deactivate the newly-created MST virtual environment: `conda deactivate`
4. Going forward, users should activate their MST virtual environment prior to working with the code in this repo via `conda activate mstenv`.

## Running the Package Demos / Testing Installation

To test the package installation or demo the package, users can take the following steps:
1. Open command prompt / terminal and navigate into the MST directory
2. Activate the MST virtual environment: `conda activate mstenv`
3. We will first demo MST's implementation of Choice Model Trees. Open mst.py. At the top of the file under "Import proper leaf model here:" , ensure that only one leaf model is being imported which should read `from leaf_model_mnl import *`. In command prompt / terminal, execute command `python cmt_example.py` which will run the MST on a synthetic choice modeling dataset. At the end of execution, the test set error will be outputted which should be under 0.05.
5. We will next demo MST's implementation of Isotonic Regression Trees. Open mst.py. At the top of the file under "Import proper leaf model here:" , ensure that only one leaf model is being imported which should read `from leaf_model_isoreg import *`. In command prompt / terminal, execute command `python irt_example.py` which will run the MST on a synthetic ad auction dataset. At the end of execution, the test set error will be outputted which should be under 0.05.

## Running MSTs on the Swiss Metro dataset
To run MSTs on the Swiss Metro dataset used by our paper, please take the following steps:
1. Copy the files leaf_model_mnl_tensorflow.py and mst.py from the https://github.com/rtm2130/MST repo to the /scripts/src directory
2. Copy the files newmnlogit.R, leaf_model_mnl.py, and leaf_model_mnl_rmnlogit.py from the https://github.com/rtm2130/CMT-R repo to the /scripts/src directory
3. Create and activate a virtual environment following the steps from this repo
4. Open the /scripts/src/newmnlogit.R file and at the top of the file, change `ro.r.source("newmnlogit.R")` to `ro.r.source("src/newmnlogit.R")`
5. Open /scripts/src/mst.py and ensure that at the top of the file the correct leaf model is being imported (`from leaf_model_mnl import *`)
6. Within the activated virtual environment, execute the scripts for running the Swiss Metro dataset located within the scripts/ directory.
