# Avero Backend Coding Exercise
This project is based on the instructions given by the Avero Backend Coding Exercise described [here](https://github.com/AveroLLC/reporting-api-exercise).  The goal was to develop an API that delivers three different types of reports based on Point Of Sale (POS) data.  The code repository and instructions for launching the reporting API on a local server are described in this Readme file.


## Setup
These setup instructions are designed for a UNIX like terminal.  Following these instructions, I was able to successfully launch this application from an AWS EC2 instance with the Ubuntu 16.04 operating system.

  1.  Clone the GitHub Repository
    - git clone https://github.com/jbhersch/avero_assessment.git


  2.  Change directories into the avero_assessment repo.
    - cd avero_assessment


  3.  Change permissions on initialization scripts
    - chmod +x initialize_1.sh
    - chmod +x initialize_2.sh


  4.  Run the initialize_1.sh script.  This script downloads and installs the python requirements.  There will be several prompts throughout this process, type either 'yes' or 'y' as they come up.  I developed this API on my personal machine where python is run through Anaconda.  Rather than try and decouple that, I added Anaconda to the system requirements installed by initialize_1.sh.  Anaconda takes a few minutes to download and install, so apologies for the wait.
    - . initialize_1.sh


  5.  Run initialize_2.sh script.  Running initialize_1.sh leaves you in the root directory, so you will need to change directories back into the avero_assessment repo before running initialize_2.sh.  initialize_2.sh activates a virtual environment, installs necessary packages, and changes directories into the main Django project - avero_assessment/reporting_api.
    - change directories to the avero_assessment repo
    - . initialize_2.sh


  6.  The final step is to run the Django server, which is somewhat subjective to the environment the API is being run from.  Running initialize_2.sh leaves you in the main Django project directory with an active virtual environment.  Getting the application to launch from here depends on the system that it is being run from.  For example, if this is being run from a local environment with access to a web browser, then the user can type the following into the terminal and access the api at 'http://127.0.0.1:8000/'
    - python manage.py runserver

  However, if this is being run from an EC2 instance for example, where the instance has a public ip address of ###.##.##.##, then the API can be accessed at 'http://ec2-###-##-##-##.compute-1.amazonaws.com:8000/' by typing the following into the terminal
    - python manage.py runserver ec2-###-##-##-##.compute-1.amazonaws.com:8000


## POS API Data Retrieval
Per the instructions, the data from the POS APIs was written to flat csv files.  These files are located in avero_assessment/reporting_api/reporting_api/data/ and were written by the script, [write_flat_files.py](https://github.com/jbhersch/avero_assessment/blob/master/write_flat_files.py).


## Report Types

### Labor Cost Percentage (LCP)

### Food Cost Percentage (FCP)

### Employee Gross Sales (EGS)
