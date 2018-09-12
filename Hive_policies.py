import os
import argparse
import json

# Setting Variables
NprodUser='admin'
NprodPass='admin'
NprodSrv="http://localhost:6080/service/public/api/policy"
ProdSrv="http://localhost:6080/service/public/api/policy"
ProdUser='admin'
ProdPass='adminprd'
RangerAudit='false'
HomeDir = os.getcwd()
Defaultfields = ["hive","Inclusion","true"]
df = Defaultfields
Envtype = ""

json_structure = ("policyName","databases","tables","columns","description",
                  "repositoryName","repositoryType","tableType","columnType",
                  "isEnabled","isAuditEnabled","permMapList","groupList","permList")
js = json_structure

def check_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e','--environment', help='Environment prod or mini', required=True)
    parser.add_argument('-f','--file', help='REQXXXXXXXXX.csv', required=True)
    parser.add_argument('-t','--type', help='use "insert" for new policies or "append" for existing policies', required=False)
    args = parser.parse_args()

    global CsvArq
    global EnvSet
    global EnvType
    global LogDir
    global RangerList
    global Env

    EnvSet = str.lower(args.environment)
    if args.type is not None:
        EnvType = str.lower(args.type)
    CsvArq = args.file
    RangerList = '{}/{}'.format(HomeDir,CsvArq)
    LogDir = CsvArq.split('.csv')

    if (EnvSet == "prod"):
        df.insert(0,'PRD_hive')
        Env=[ProdUser,ProdPass,ProdSrv]
    elif (EnvSet == "mini"):
        df.insert(0,'NONPROD_hive')
        Env=[NprodUser,NprodPass,NprodSrv]

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

def Open_RangerList():
    with open(RangerList) as csvfile:
        lines = csvfile.readlines()
        for line in lines:
            global permstr
            global permlist
            global cl
            csvList = line.split(';')
            cl = csvList[1::]
            permlist = (cl[6:12])
            if EnvType == "append":
                Backup_Policy()
            else:
                Convert_Json_Insert()


def Convert_Json_Insert():
    while '' in permlist:
        global newkeyvalue
        permlist.remove('')
        permstr = '", "'.join(permlist)
        permstr = str.lower(permstr)
    newkeyvalue=('{{ "{12}":"{0}", "{13}":"{1}", "{14}":"{2}", "{15}":"{3}", "{16}":"{4}", "{17}":"{8}", '
                    '"{18}":"{9}", "{19}":"{10}","{20}":"{10}","{21}":"{11}", "{22}":"{5}", "{23}": '
                    '[{{ "{24}": ["{6}"], "{25}": ["{7}"] }}] '
                    '}}'.format(cl[0],cl[2],cl[3],cl[4],cl[-1],cl[5],cl[1],permstr,df[0],df[1],df[2],df[3],
                    js[0],js[1],js[2],js[3],js[4],js[5],js[6],js[7],js[8],js[9],js[10],js[11],js[12],js[13]))
    newkeyvalue=newkeyvalue.replace('\n',' ').replace('\r','')
    print("\nCONVERT JSON    {}\n".format(newkeyvalue))
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

def Backup_Policy():
    global backupfile
    CurlCmd = ("curl -q -k -H 'Content-Type: application/json' -u {0}:{1} -X "
                       "GET {2}?policyName={3} | jq -c .vXPolicies[]".format(Env[0],Env[1],Env[2],cl[0]))
    os.system(CurlCmd + '> {}/backup/{}/{}.json'.format(HomeDir, LogDir[0], cl[0]))
    print(CurlCmd)
    backupfile = ('{}/backup/{}/{}.json'.format(HomeDir, LogDir[0], cl[0]))
    Convert_Json_Append()

def Convert_Json_Append():
    with open(backupfile, 'r') as jsonbkp:
        newperm = cl[6:12]
        newgroup = [cl[1]]
        texto = jsonbkp.read()
        data = json.loads(texto)
        newdata = [data['permMapList']]
        permlist = newperm
        grouplist = newgroup
        newdata = str(newdata)
        newdata = newdata.replace("u'", '"').replace("[[","").replace("]]","").replace("'",'"')
        while '' in permlist:
            permlist.remove('')
        permstr = '", "'.join(permlist)
        permstr = str.lower(permstr)


        while '' in grouplist:
            grouplist.remove('')
        groupstr = '", "'.join(grouplist)
        groupstr = str.lower(groupstr)

        global newkeyvalue
        global polid
        polid = data['id']

        newkeyvalue=('{{ "{12}":"{0}", "{13}":"{1}", "{14}":"{2}", "{15}":"{3}", "{16}":"{4}", "{17}":"{8}",'
                     '"{18}":"{9}", "{19}":"{10}","{20}":"{10}","{21}":"{11}", "{22}":"{5}", "{23}": '
                     '[ {26}, {{ "{24}": ["{6}"], "{25}": ["{7}"] }}] '
                     '}}'.format(cl[0],cl[2],cl[3],cl[4],cl[-1],cl[5],groupstr,permstr,df[0],df[1],df[2],df[3],
                     js[0],js[1],js[2],js[3],js[4],js[5],js[6],js[7],js[8],js[9],js[10],js[11],js[12],js[13], newdata))

        newkeyvalue=newkeyvalue.replace('\n',' ').replace('\r','')
        print("\n{}\n".format(newkeyvalue))
        Append_Policy()

def Append_Policy():
            CurlCmd = ("curl -i -w 'RESP_CODE: %{{response_code}} ' -k -H 'Content-Type: application/json' -u {0}:{1} -X "
                       "PUT {2}/{5} -d @stage/{3}/{4}.json "
                       "-o jsonlog/{3}/{4}.log".format(Env[0],Env[1],Env[2],LogDir[0],cl[0],polid))
            jsonlogfile= open('{}/stage/{}/{}.json'.format(HomeDir, LogDir[0], cl[0]), 'w')
            jsonlogfile.write(newkeyvalue)
            jsonlogfile.close()

            print("{}\n".format(CurlCmd))
            os.system(CurlCmd)

def main():
    check_args()
    check_rangerpol()
    Open_RangerList()

if __name__ == '__main__':
    main()
