import os
import re
import csv

acfDict = {
    "AppState":{
        "appid": "1",
        "Universe": "1",
        "name": "1",
        "StateFlags": "4",
        "installdir": "1",
        "LastUpdated": "1",
        "UpdateResult": "0",
        "SizeOnDisk": "1",
        "buildid": "1",
        "LastOwner": "0",
        "BytesToDownload": "0",
        "BytesDownloaded": "0",
        "AutoUpdateBehavior": "0",
        "AllowOtherDownloadsWhileRunning": "0",
        "ScheduledAutoUpdate": "0",
        "InstalledDepots": {},
        "MountedDepots": {},
        "UserConfig":{
            "language": "schinese"
        }
    }
}
deep = 0
kvspace = "\t\t"
quotation = "\""

steamPath = r"M:\SteamLibrary\steamapps"

def parseFile():
    depotsArr = []
    f = open("info.acf", "r", encoding="utf-8")
    i = 0
    isFindDepot = False
    while i < 1150:
        s = f.readline()
        if not s:
            break

        r = s.find("metacritic_name")
        if r > -1: 
            l = r + len("metacritic_name")+4
            sub = s[l:-2]
            acfDict["AppState"]["name"] = sub

        r = s.find("installdir")
        if (r > -1):
            l = r + len("installdir")+4
            sub = s[l:-2]
            acfDict["AppState"]["installdir"] = sub
        
        r = s.find("\"depots\"")
        if (r > -1):
            isFindDepot = True
        if isFindDepot:
            strList = re.findall(r'\d{6}', s)
            if (len(strList) == 1 and len(s) == 11):
                strList.append(f.tell())
                print(strList, len(s))
                depotsArr.append(strList)
        i += 1
    
    for lt in depotsArr:
        f.seek(lt[1]+5, 0)
        print(lt)
        i = 0
        while i < 150:
            s = f.readline()
            if not s:
                break
            strList = re.findall(r'\d{6}', s)
            if (len(strList) == 1 and len(s) == 11):
                print(strList, len(strList), len(s))
                break
            
            r = s.find("public")
            if r > -1: 
                l = r + len("public")+4
                sub = s[l:-2]
                if len(sub) > 0:
                    acfDict["AppState"]["InstalledDepots"][lt[0]] = {"manifest": sub}
                    acfDict["AppState"]["MountedDepots"][lt[0]] = sub

            r = s.find("depotfromapp")
            if r > -1: 
                l = r + len("depotfromapp")+4
                sub = s[l:-2]
                if not ("SharedDepots" in acfDict["AppState"]):
                    acfDict["AppState"]["SharedDepots"] = {}
                    acfDict["AppState"]["SharedDepots"][lt[0]] = sub
                else:
                    acfDict["AppState"]["SharedDepots"][lt[0]] = sub
            i += 1
    f.close()
    os.remove("info.acf")

def deepSpace(deep):
    s = ""
    i = 0
    while i < deep:
        s += "\t"
        i += 1
    return s

def writeFile(appid):
    filename = steamPath + r"\appmanifest_" + appid +".acf"
    fl = open(filename,"w+", encoding="utf-8")
    print(filename, fl)
    def doWrite(map):
        global deep
        for k in map:
            if type(map[k]) == str:
                fl.write(deepSpace(deep) + quotation + k + quotation + kvspace + quotation + map[k] + quotation + "\n")
            elif type(map[k]) == dict:
                fl.write(deepSpace(deep) + quotation + k + quotation + "\n")
                fl.write(deepSpace(deep) + "{\n")
                deep += 1
                doWrite(map[k])
                deep -= 1
                fl.write(deepSpace(deep) + "}\n")
    doWrite(acfDict)
    fl.close()


if __name__ == "__main__":
    appid = 570
    account = "jiahong16"
    passwd = "zzmx2sjh"
    dirname = "dota 2 beta"
    data = csv.reader(open("steam_idpw.csv", "r", encoding="utf-8"))
    for line in data:
        if (line[0] != "Gloud_game_ID"):
            appid = line[3]
            account = line[1]
            passwd = line[2]
            dirname = line[4]
            downloadPath = os.path.dirname(os.path.abspath(__file__)) + r"\publish\DepotDownloader.exe"
            downloadStr = r'{} -app {} -user {} -pass {} -dir "{}\common\{}" -validate -max-servers 50 -max-downloads 50'.format(downloadPath, appid, account, passwd, steamPath,dirname)
            print(downloadStr)
            os.system(downloadStr)
            acfDict["AppState"]["appid"] = str(appid)
            cmdPath = os.path.dirname(os.path.abspath(__file__)) + r"\steamcmd\steamcmd.exe"
            steamcmdStr = r"{} +login {} {} +app_info_update 1 +app_info_print {} +quit >> info.acf".format(cmdPath, account, passwd, appid)
            print(steamcmdStr)
            ret = os.system(steamcmdStr)
            print("ret= ", ret)
            parseFile()
            writeFile(str(appid))