#!/usr/bin/env python

import os
import sys

# Setting Variables
RangerUser='admin'
RangerPass='admin'
HomeDir = os.getcwd()
CsvArq = 'csv_test.csv'
RangerList = '{}/{}'.format(HomeDir,CsvArq)
LogDir = CsvArq.split('.csv')
SvrPost="http://localhost:6080/service/public/api/policy"
FileTemp='{}/rangerlist.txt'.format(HomeDir)


if not os.path.exists('{}/jsonlog/{}'.format(HomeDir,LogDir[0])):
    os.makedirs('{}/jsonlog/{}'.format(HomeDir,LogDir[0]))

if not os.path.exists('{}/stage/{}'.format(HomeDir,LogDir[0])):
    os.makedirs('{}/stage/{}'.format(HomeDir,LogDir[0]))

def check_rangerpol(argv):
  pass
    
def convert_json():
    with open(RangerList) as csvfile:
        lines = csvfile.readlines()
        for line in lines:
            csvList = []
            csvList = line.split(';')
            cl = csvList[1::]
            permlist = (cl[6:12])

            #Removing Null columns from Permission List
            while '' in permlist:
                permlist.remove('')

            defaultfields = ("default","hive","Inclusion","true")
            df = defaultfields
            
            newkeyvalue=('{{ "policyName":"{0}",'
                         ' "databases":"{1}",'
                         ' "tables":"{2}",'
                         ' "columns":"{3}",'
                         ' "description":"{4}",'
                         ' "repositoryName":"{8}",'
                         ' "repositoryType":"{9}",'
                         ' "tableType":"{10}",'
                         ' "columnType":"{10}",'
                         ' "isEnabled":"{11}",'
                         ' "isAuditEnabled":"{5}",'
                         ' "permMapList": [{{'
                         '   "groupList": ["{6}"],'
                         '   "permList": ["{7}"]'
                         ' }}]'
                         '"}}'.format(cl[0],cl[1],cl[3],cl[4],cl[-1],cl[5],cl[2],permlist,df[0],df[1],df[2],df[3]))
            CurlCmd = ("curl -i -w 'RESP_CODE: %{{response_code}} ' -H 'Content-Type: application/json' -u {0}:{1} -X "
                       "POST {2} "
                       "-d stage/{3}/{4} "
                       "-o jsonlog/{3}/{4}.log".format(RangerUser,RangerPass,SvrPost,LogDir[0],cl[0]))
            jsonlogfile= open('{}/jsonlog/{}/{}.json'.format(HomeDir, LogDir[0], cl[0]), 'w')
            jsonlogfile.write(newkeyvalue)
            jsonlogfile.close()
            print("{}\n".format(CurlCmd))

def apply_policy():
  pass

if __name__ == '__main__':
    convert_json()
