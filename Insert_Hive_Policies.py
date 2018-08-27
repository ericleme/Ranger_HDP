#!/usr/bin/env python
#######################################################################
# Author: Eric Leme                                                 ###
# Date: 21/08/2018 v1                                               ###
# Summary: Execute more than one Ranger policies based on csv file  ###
#          automatically                                            ###
#######################################################################

import os
import sys
import json
import argparse

# Setting Variables
HomeDir = os.getcwd()

def check_args():
    #Setting Local Variables
    NprodUser='admin'
    NprodPass='admin'
    NprodSrv="http://localhost:6080/service/public/api/policy"
    ProdSrv="http://prodServer:6080/service/public/api/policy"
    ProdUser='admin'
    ProdPass='Hardpwd'
    Defaultfields = ["hive","Inclusion","true"]

    #Setting Global Variables
    global CsvArq
    global EnvSet
    global RangerList
    global LogDir
    global df
    global Env

    #Setting Required Options for execution
    parser = argparse.ArgumentParser()
    parser.add_argument('-e','--environment', help='Environment "Prod" or "NonProd"\n', required=True)
    parser.add_argument('-f','--file', help='REQUISITIONXXXX.csv\n', required=True)
    args = parser.parse_args()

    EnvSet = str.lower(args.environment)
    CsvArq = args.file
    RangerList = '{}/{}'.format(HomeDir,CsvArq)
    LogDir = CsvArq.split('.')
    df = Defaultfields

    if (EnvSet == "prod"):
        df.insert(0,'PROD_hive')
        Env=[ProdUser,ProdPass,ProdSrv]
    elif (EnvSet == "nonprod"):
        df.insert(0,'NONPROD_hive')
        Env=[NprodUser,NprodPass,NprodSrv]

    check_rangerpol()

def check_rangerpol():

    if not os.path.exists('{}/jsonlog/{}'.format(HomeDir,LogDir[0])):
        os.makedirs('{}/jsonlog/{}'.format(HomeDir,LogDir[0]))

    if not os.path.exists('{}/stage/{}'.format(HomeDir,LogDir[0])):
        os.makedirs('{}/stage/{}'.format(HomeDir,LogDir[0]))

    if not os.path.exists('{}/old_csv/{}'.format(HomeDir,LogDir[0])):
        os.makedirs('{}/old_csv/'.format(HomeDir))

    try:
        f = open('{}'.format(RangerList))
    except IOError:
        print('File {} does not exist\n\n'.format(RangerList))

    try:
        os.system('/usr/bin/dos2unix {}\n\n'.format(RangerList))
    except Exception:
        print('dos2unix not found\n\n')

    convert_json()

def convert_json():
    with open(RangerList) as csvfile:
        lines = csvfile.readlines()
        for line in lines:
            global permstr
            global cl
            global newkeyvalue
            csvList = line.split(';')
            cl = csvList[1::]
            permlist = (cl[6:12])
            #Removing Null from Permission List
            while '' in permlist:
                permlist.remove('')
            permstr = '", "'.join(permlist)

            newkeyvalue=('{{ "policyName":"{0}", "databases":"{1}", "tables":"{2}", "columns":"{3}", "description":"{4}", "repositoryName":"{8}", "repositoryType":"{9}", "tableType":"{10}","columnType":"{10}", '
                         '"isEnabled":"{11}", "isAuditEnabled":"{5}", "permMapList": [{{ "groupList": ["{6}"],'
                         '"permList": ["{7}"] }}] '
                         '}}'.format(cl[0],cl[2],cl[3],cl[4],cl[-1],cl[5],cl[1],permstr,df[0],df[1],df[2],df[3]))
            newkeyvalue=newkeyvalue.replace('\n',' ').replace('\r','')
            print("\n{}\n".format(newkeyvalue))

            Insert_Policy()

def Insert_Policy():
            CurlCmd = ("curl -i -w 'RESP_CODE: %{{response_code}} ' -H 'Content-Type: application/json' -u {0}:{1} -X "
                       "POST {2} -d @stage/{3}/{4}.json "
                       "-o jsonlog/{3}/{4}.log".format(Env[0],Env[1],Env[2],LogDir[0],cl[0]))
            jsonlogfile= open('{}/stage/{}/{}.json'.format(HomeDir, LogDir[0], cl[0]), 'w')
            jsonlogfile.write(newkeyvalue)
            jsonlogfile.close()

            print("{}\n".format(CurlCmd))
            os.system(CurlCmd)

if __name__ == '__main__':
    check_args()
