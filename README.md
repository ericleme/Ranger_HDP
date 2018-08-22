# Ranger_HDP
Automated Script to submit rules in Ranger HortonWorks based on CSV file.

# Environment
Hortonworks 2.6.4 with Ranger.
Python 2.7.5

PS: This script is working only for new rules, appending rules is still developing.

1 - Download example-csv.xls and fill the columns as you need, after that remove the first line (guide) and export this xls as csv file.

2 - Put this csv file on the same path as python script.

3 - Change the local variables as you wish, following the configurations of your environment.If you have only one environment just set as "prod"

4 - run python as below
#python hive_policies.py -e PROD -f example.csv

# For more information:
$ python hive_policies.py -h
usage: hive_policies.py [-h] -e ENVIRONMENT -f FILE
  
optional arguments:
  -h, --help            show this help message and exit
  -e ENVIRONMENT, --environment ENVIRONMENT
                        Environment "Prod" or "NonProd"
  -f FILE, --file FILE  REQXXXXXXXXXX.csv
  
  I hope this help!
