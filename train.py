import re
import json
import requests
from bs4 import BeautifulSoup
import collections
import time


# 从data_url下载所有的车次数据 | 保存为 name.txt 文件
def download_data(data_url, name):
    requests.adapters.DEFAULT_RETRIES = 5
    response = requests.get(data_url, stream=True, verify=False)
    status = response.status_code
    if status == 200:
        with open(name, 'wb') as tfile:
            for chunk in response.iter_content(chunk_size=102400):  # 成块读取数据
                if chunk:
                    tfile.write(chunk)


# 提取车次信息，保存到 xshorter_list.txt
def get_train_info():
    with open('train_list.txt', 'r', encoding='utf-8') as f:

        strJson = json.load(f)

        onedayD = strJson["2019-10-18"]['D']
        with open('Dtrain.txt', 'w', encoding='utf-8') as f1:
            json.dump(onedayD, f1)

        with open('Dtrain.txt', 'r', encoding='utf-8') as f2:
            patten = r'\(.*?\)'
            data = f2.read()
            newdata = re.sub(patten, '', data)

            with open('Dshorter_list.txt', 'w', encoding='utf-8') as f3:
                f3.write(newdata)

        onedayG = strJson["2019-10-18"]['G']
        with open('Gtrain.txt', 'w', encoding='utf-8') as f1:
            json.dump(onedayG, f1)

        with open('Gtrain.txt', 'r', encoding='utf-8') as f2:
            patten = r'\(.*?\)'
            data = f2.read()
            newdata = re.sub(patten, '', data)

            with open('Gshorter_list.txt', 'w', encoding='utf-8') as f3:
                f3.write(newdata)

        listD = [e['station_train_code'] for e in onedayD]
        listG = [e['station_train_code'] for e in onedayG]
        print(len(onedayD))
        print(listD)
        print(len(onedayG))
        print(listG)


# 为了找错，存储爬取的网页
TMP = 0


# 去高铁网爬取指定车次时刻表
def crawlTrainInfo_gaotie(trainNo='G1'):
    url = f'http://shike.gaotie.cn/checi.asp?checi={trainNo}'
    StopClass = collections.namedtuple('StopClass', ['name', 'stop', 'start'])
    TrainClass = collections.namedtuple('TrainClass', ['train', 'stops'])
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = "gbk"
        global TMP
        TMP = r.text

        soup = BeautifulSoup(r.text.replace("\n", ""), 'html.parser')
        tt = soup.find(text="站次")
        biaotou = tt.parent.parent.parent
        stops = []
        for web in biaotou.next_siblings:
            s = web.find_all('td')
            name = s[1].contents[0].contents[0].text
            start = s[2].text
            stop = s[3].text
            if start == '始发站':
                start = stop
            if stop == '终点站':
                stop = start

            station = StopClass(name, start, stop)
            stops.append(station)

        return TrainClass(trainNo, stops)
    except Exception as e:
        if str(e).startswith("'NoneType'"):
            raise Exception('notrain')
        elif str(e).startswith("'NavigableString'"):
            raise Exception('connecterr')
        else:
            print(e)


# 去携程爬取指定车次的时刻表
def crawlTrainInfo_xc(trainNo='G1'):
    baseurl = 'https://trains.ctrip.com/trainbooking/TrainSchedule/'
    StopClass = collections.namedtuple('StopClass', ['name', 'stop', 'start'])
    TrainClass = collections.namedtuple('TrainClass', ['train', 'stops'])
    try:
        r = requests.get(baseurl+trainNo)
        r.raise_for_status()
        r.encoding = "gbk"
        global TMP
        TMP = r.text

        soup = BeautifulSoup(r.text.replace("\n", ""), 'html.parser')
        target_regexp = re.compile(r'ctl00\_MainContentPlaceHolder\_rptStopOverStation.*')
        tt = soup.find_all(id=target_regexp)
        stops = []
        for e in tt:
            stop = e.parent.next_sibling.next_sibling
            start = stop.next_sibling.next_sibling
            station = StopClass(e.string + '站', stop.string.strip(), start.string.strip())
            stops.append(station)

        return TrainClass(trainNo, stops)
    except Exception as e:
        print(e)


# 避免重复查询，把已查记录存好
SC = dict()
newOS = set()


# 将文件中的站-城映射保存到SC
def initSC(infile):
    for line in open(infile, 'r', encoding='utf-8'):
        #print(line)
        mapping = line.split('-')
        s = mapping[0]
        c = mapping[1].strip('\n')
        if s not in SC:
            SC[s] = c


# 将车站转换为所在的城市
def s2c(station):
    address = station
    global SC
    global newOS
    if address in SC:
        return SC[address]
    else:
        key = '27ea3472ed190ddbc5e3160188e74111'
        url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={key}'

        r = requests.get(url)
        info = r.json()

        if info['count'] == '0':  # 未查到该车站
            print(address)
            newOS.add(address)
            SC[address] = 0
            return 0
        else:
            city = info['geocodes'][0]['city']
            if city == []:
                newOS.add(address)
                SC[address] = 0
                return 0
            else:
                SC[address] = city
                return city


# 获取列车时刻表，保存到json文件
# 将时刻表转化为图的节点和边（初步）
# Dtrain_infos.json, Gtrain_infos.json 保存了每个车次的时刻表，包括站名，到站时间，离站时间
# 从这两个文件中提取出图的节点-城市，边（一站连接的两个城市，）
# 节点用集合stations表示
# 每条边用一个字典元素表示，键名为“某站-某站”，值为一个列表，列表元素为（时间，车次）
# 在高德地图上查不到所在城市的车站和关联的边保存至odds和oddsPaths
def getSch(inshorter, type='D', jixu=0):
    f = open(inshorter, 'r', encoding='utf-8')
    strJson = json.load(f)
    listT = [e['station_train_code'] for e in strJson]
    print(len(listT), listT)
    f.close()

    log = []
    TNs = []
    failtrains = []
    tryagain = []

    if jixu == 0:
        Trains = []
        stations = set()  # xx市
        paths = dict()
        odds = set()
        oddsPaths = dict()
    else:
        with open(type + 'Node_Edge_gtw.json', 'r', encoding='utf-8') as f:
            out = json.load(f)
            stations = set(out[0])
            paths = out[1]
            odds = set(out[2])
            oddsPaths = out[3]

        with open(type + 'train_infos_gtw.json', 'r', encoding='utf-8') as ff:
            Trains = json.load(ff)

        pos = listT.index(jixu)
        listT = listT[pos:-1]
        print(listT)

    i = 0
    try:
        for train in listT:
            #print(Trains)
            #print(paths)
            try:
                infos = crawlTrainInfo_gaotie(train)
            except Exception as e:
                if str(e) == 'notrain':
                    failtrains.append(train)
                    continue
                elif str(e) == 'connecterr':
                    tryagain.append(train)
                    continue
                else:
                    print(e)
                    continue


            trainNo = infos[0]

            Trains.append(infos)
            if i % 100 == 0:
                print(i)
            time.sleep(0.1)
            i = i + 1

            TNs.append(trainNo)

            for stop in infos[1]:
                # print('stop: ' + stop[0])
                city = s2c(stop[0])
                if city == 0:
                    odds.add(stop[0])
                    log.append(TMP)
                    #print(trainNo + ' ' + stop[0])
                else:
                    stations.add(city)

            LEN = len(infos[1])

            for ti in range(LEN - 2):
                k1 = s2c(infos[1][ti][0])
                k2 = s2c(infos[1][ti + 1][0])

                start = infos[1][ti][2].split(':')
                arrive = infos[1][ti + 1][2].split(':')
                weight = 60 * (int(arrive[0]) - int(start[0])) + (int(arrive[1]) - int(start[1]))

                if k1 == 0 or k2 == 0:
                    edgekey = infos[1][ti][0] + '-' + infos[1][ti + 1][0]
                    if edgekey in oddsPaths:
                        oddsPaths[edgekey].append((weight, infos[0]))
                    else:
                        oddsPaths[edgekey] = [(weight, infos[0])]
                else:
                    edgekey = k1 + '-' + k2  # xx市-xx市
                    if edgekey in paths:
                        paths[edgekey].append((weight, infos[0]))
                    else:
                        paths[edgekey] = [(weight, infos[0])]
    except Exception as e:
        print(e)
        print(train)

    out = (list(stations), paths, list(odds), oddsPaths)

    print(Trains)
    print(paths)

    with open(type + 'train_infos_gtw.json', 'w', encoding='utf-8') as ft:
        ft.write(json.dumps(Trains))

    with open(type + 'Node_Edge_gtw.json', 'w', encoding='utf-8') as fn:
        fn.write(json.dumps(out))

    with open(type + 'crawl_fail.json', 'w', encoding='utf-8') as ff:
        ff.write(json.dumps((failtrains, tryagain)))


# 从携程补充一些时刻表
def getSch_xc(type='D', jixu=0):
    with open(type + 'crawl_fail.json', 'r', encoding='utf-8') as f:
        strJson = json.load(f)

        listT = strJson[0]
        listT.extend(strJson[1])
        print(len(listT), listT)


    log = []
    TNs = []
    failtrains = []
    tryagain = []

    if jixu == 0:
        Trains = []
        stations = set()  # xx市
        paths = dict()
        odds = set()
        oddsPaths = dict()
    else:
        with open(type + 'Node_Edge_xc.json', 'r', encoding='utf-8') as f:
            out = json.load(f)
            stations = set(out[0])
            paths = out[1]
            odds = set(out[2])
            oddsPaths = out[3]

        with open(type + 'train_infos_xc.json', 'r', encoding='utf-8') as ff:
            Trains = json.load(ff)

        pos = listT.index(jixu)
        listT = listT[pos:-1]
        print(listT)

    i = 0
    try:
        for train in listT:
            try:
                infos = crawlTrainInfo_xc(train)
            except Exception as e:
                if str(e) == 'notrain':
                    failtrains.append(train)
                    continue
                elif str(e) == 'connecterr':
                    tryagain.append(train)
                    continue
                else:
                    print(e)
                    print(train)
                    continue


            trainNo = infos[0]

            Trains.append(infos)
            if i % 100 == 0:
                print(i)
            time.sleep(0.1)
            i = i + 1

            TNs.append(trainNo)

            for stop in infos[1]:
                # print('stop: ' + stop[0])
                city = s2c(stop[0])
                if city == 0:
                    odds.add(stop[0])
                    log.append(TMP)
                    #print(trainNo + ' ' + stop[0])
                else:
                    stations.add(city)

            LEN = len(infos[1])

            for ti in range(LEN - 2):
                k1 = s2c(infos[1][ti][0])
                k2 = s2c(infos[1][ti + 1][0])

                start = infos[1][ti][2].split(':')
                arrive = infos[1][ti + 1][2].split(':')
                weight = 60 * (int(arrive[0]) - int(start[0])) + (int(arrive[1]) - int(start[1]))

                if k1 == 0 or k2 == 0:
                    edgekey = infos[1][ti][0] + '-' + infos[1][ti + 1][0]
                    if edgekey in oddsPaths:
                        oddsPaths[edgekey].append((weight, infos[0]))
                    else:
                        oddsPaths[edgekey] = [(weight, infos[0])]
                else:
                    edgekey = k1 + '-' + k2  # xx市-xx市
                    if edgekey in paths:
                        paths[edgekey].append((weight, infos[0]))
                    else:
                        paths[edgekey] = [(weight, infos[0])]

    except Exception as e:
        print(e)
        print(train)

    out = (list(stations), paths, list(odds), oddsPaths)

    with open(type + 'train_infos_xc.json', 'w', encoding='utf-8') as ft:
        ft.write(json.dumps(Trains))

    with open(type + 'Node_Edge_xc.json', 'w', encoding='utf-8') as fn:
        fn.write(json.dumps(out))

    with open(type + 'crawl_fail_xc.json', 'w', encoding='utf-8') as ff:
        ff.write(json.dumps((failtrains, tryagain)))


def main():
    # 下载需要的文件
    #tn_data_url = 'https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0'
    #download_data(tn_data_url, 'tnumber_datas.txt')

    #station_data_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9002'
    #download_data(station_data_url, 'stations_datas.txt')

    #get_train_info()

    initSC('oddstations.txt')

    #getSch('Dshorter_list.txt', 'D')
    getSch_xc('G')

    #getSch('Gshorter_list.txt', 'G')
    print(newOS)

    #print(crawlTrainInfo_gaotie('D29'))
    #crawlTrainInfo()
    '''
    D617,D620,D707,D708,D765
    '''


if __name__ == "__main__":
    main()



