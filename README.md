# Ranger_HDP
Automated Script to submit rules or append in Ranger HortonWorks based on CSV file.

# Environment
Hortonworks 2.6.4 with Ranger.
Python 2.7.5

1 - Download example-csv.xls and fill the columns as you need, after that remove the first line (guide) and export this xls as csv file.

2 - Put this csv file on the same path as python script.

3 - Change the local variables as you wish, following the configurations of your environment.If you have only one environment just set as "prod"

4 - run python as below
#python Hive_policies.py -e PROD -f example.csv -t insert

# For more information:
$ python Hive_policies.py -h
usage: Hive_policies.py [-h] -e ENVIRONMENT -f FILE [-t TYPE]

optional arguments:
-h, --help            show this help message and exit
-e ENVIRONMENT, --environment ENVIRONMENT
                        Environment prod or dev
-f FILE, --file FILE  FileXXXXXXXXX.csv
-t TYPE, --type TYPE  use "insert" for new policies or "append" for existing
                        policies

