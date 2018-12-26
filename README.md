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

  The argument following runserver will vary depending on where the application is being run from.


## POS API Data Retrieval
Per the instructions, the data from the POS APIs was written to flat csv files.  These files are located in avero_assessment/reporting_api/reporting_api/data/ and were written by the script, [write_flat_files.py](https://github.com/jbhersch/avero_assessment/blob/master/write_flat_files.py).


## Report Types
There are three report types available for this API - Labor Cost Percentage, Food Cost Percentage, and Employee Gross Sales, each of which is discussed in more detail in the following sections.  All three report types require business_id, start date time, end date time, and time interval in the url request.  For a given business_id, all three report types provide different metrics across N time intervals that span the start date time and the end date time.  I've structured all three APIs such that the last time interval always ends with the end date time, even if that results in the last time interval spanning a shorter time increment than the rest.

All three reports use the Checks model/table.  In order to determine the relevant checks for a given time interval, only the checks that are closed during the time interval of interest are examined.  

Note - The values returned for LCP and FCP are percentages.

### Labor Cost Percentage (LCP)
For a given time interval, the LCP is the ratio of labor cost to revenue.  In addition to the Checks table, the LCP requires the OrderedItems and LaborEntries tables.  OrderedItems are related to the Checks table via the 'check_id' column.  By finding the check ids that closed during a given time interval, the un-voided ordered items tied to the relevant check ids can be examined, and the revenue they provide can be summed up.  Each labor entry record has a clock in and clock out field.  The LaborEntries table is then filtered on business id, clock in, and clock out to determine which records are applicable to the time interval of interest.  Once the appropriate LaborEntries records are determined, the labor cost can be calculated with the product of hours worked and hourly rate.  

### Food Cost Percentage (FCP)
The FCP is the ratio of the amount charged for food items (price) to the amount it costs to make (cost).  I wasn't exactly sure how to calculate this metric given the time interval constraints.  Also, the example given in the instructions only provides a value for each time increment and doesn't itemize the menu items.  So, the API created returns the FCP ratio of all the items sold by a given business during the time interval of interest.  

Similar to LCP, the first step is to isolate the check ids that closed during each time interval of interest.  From there, the ordered items for each check can be determined.  The voided ordered items are filtered out, and the price and cost are summed for all the ordered items sold during the given time interval and the FCP ratio is determined from there.

### Employee Gross Sales (EGS)
EGS is the sum of price charged for all items sold by a given employee during a given time interval.  Unlike LCP and FCP, the data returned by the EGS report is itemized by employee name.  This is achieved by filtering the Checks for the time interval of interest, then joining the filtered Checks model and OrderedItems model on the 'check id' field.  Once the two tables have been joined, they can be grouped by employee name and the price of all items sold can be summed.  This produces an EGS value for each employee that worked during the time interval of interest.
