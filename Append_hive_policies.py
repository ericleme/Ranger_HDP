#!/usr/bin/env python
#######################################################################
# Author: Eric Leme                                                 ###
# Date: 21/08/2018 v1                                               ###
# Summary: Append more than one Ranger policies based on csv file   ###
#          automatically, this is used when you already have a      ### 
#          policy created on your Ranger                            ###
#######################################################################

import os
import sys
import json, ast
import argparse

# Setting Variables
NprodUser='admin'
NprodPass='vsq#rgr#0'
NprodSrv="http://10.238.10.152:6080/service/public/api/policy"
ProdSrv="http://10.240.4.118:6080/service/public/api/policy"
ProdUser='admin'
ProdPass='Bl4ckmamb4'
RangerAudit='false'
HomeDir = os.getcwd()
Defaultfields = ["hive","Inclusion","true"]
df = Defaultfields
backupfile = str()

def check_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e','--environment', help='Environment prod or mini', required=True)
    parser.add_argument('-f','--file', help='REQXXXXXXXXXX.csv', required=True)
    args = parser.parse_args()

    global CsvArq
    global EnvSet
    global RangerList
    global LogDir

    EnvSet = str.lower(args.environment)
    CsvArq = args.file
    RangerList = '{}/{}'.format(HomeDir,CsvArq)
    LogDir = CsvArq.split('.csv')
    check_rangerpol()

def check_rangerpol():

    if not os.path.exists('{}/jsonlog/{}'.format(HomeDir,LogDir[0])):
        os.makedirs('{}/jsonlog/{}'.format(HomeDir,LogDir[0]))

    if not os.path.exists('{}/stage/{}'.format(HomeDir,LogDir[0])):
        os.makedirs('{}/stage/{}'.format(HomeDir,LogDir[0]))

    if not os.path.exists('{}/backup/{}'.format(HomeDir,LogDir[0])):
        os.makedirs('{}/backup/{}'.format(HomeDir,LogDir[0]))

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
    global Env

    if (EnvSet == "prod"):
        df.insert(0,'TLVBRPRDK_hive')
        Env=[ProdUser,ProdPass,ProdSrv]

    elif (EnvSet == "mini"):
        df.insert(0,'TLV_MINICLU_hive')
        Env=[NprodUser,NprodPass,NprodSrv]

    with open(RangerList) as csvfile:
        lines = csvfile.readlines()
        global line
        for line in lines:
            global cl
            global newkeyvalue
            csvList = line.split(';')
            cl = csvList[1::]
            backup_pol()

def backup_pol():
    global backupfile
    CurlCmd = ("curl -q -k -H 'Content-Type: application/json' -u {0}:{1} -X "
                       "GET {2}?policyName={3} | jq -c .vXPolicies[]".format(Env[0],Env[1],Env[2],cl[0]))
    os.system(CurlCmd + '> {}/backup/{}/{}.json'.format(HomeDir, LogDir[0], cl[0]))
    print(CurlCmd)
    backupfile = ('{}/backup/{}/{}.json'.format(HomeDir, LogDir[0], cl[0]))

    append_policy()

def append_policy():
    with open(backupfile, 'r') as jsonbkp:
        newperm = cl[6:12]
        newgroup = [cl[1]]
        texto = jsonbkp.read()
        data = json.loads(texto)
        newdata = [data['permMapList']]
        permlist = newperm
        grouplist = newgroup
        #permlist = [x.encode('UTF8') for x in permlist]
        #grouplist = [x.encode('UTF8') for x in grouplist]
        newdata = str(newdata)
        newdata = newdata.replace("u'", '"').replace("[[","").replace("]]","").replace("'",'"')
        while '' in permlist:
            permlist.remove('')
        permstr = '", "'.join(permlist)

        while '' in grouplist:
            grouplist.remove('')
        groupstr = '", "'.join(grouplist)

        global newkeyvalue
        global polid
        polid = data['id']
        newkeyvalue=('{{ "policyName":"{0}", "databases":"{1}", "tables":"{2}", "columns":"{3}", "description":"{4}", "repositoryName":"{8}", "repositoryType":"{9}", "tableType":"{10}","columnType":"{10}", "isEnabled":"{11}", "isAuditEnabled":"{5}", "permMapList": [ {12}, {{ "groupList": ["{6}"], "permList": ["{7}"] }}] }}'.format(cl[0],cl[2],cl[3],cl[4],cl[-1],cl[5],groupstr,permstr,df[0],df[1],df[2],df[3],newdata))
        newkeyvalue=newkeyvalue.replace('\n',' ').replace('\r','')
        print("\n{}\n".format(newkeyvalue))
        Insert_Policy()

def Insert_Policy():
            CurlCmd = ("curl -i -w 'RESP_CODE: %{{response_code}} ' -k -H 'Content-Type: application/json' -u {0}:{1} -X "
                       "PUT {2}/{5} -d @stage/{3}/{4}.json "
                       "-o jsonlog/{3}/{4}.log".format(Env[0],Env[1],Env[2],LogDir[0],cl[0],polid))
            jsonlogfile= open('{}/stage/{}/{}.json'.format(HomeDir, LogDir[0], cl[0]), 'w')
            jsonlogfile.write(newkeyvalue)
            jsonlogfile.close()

            print("{}\n".format(CurlCmd))
            os.system(CurlCmd)

if __name__ == '__main__':
    check_args()
