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


# 去携程爬取指定车次的时刻表
def crawlTrainInfo(trainNo='G1'):
    baseurl = 'https://trains.ctrip.com/trainbooking/TrainSchedule/'
    StopClass = collections.namedtuple('StopClass', ['name', 'stop', 'start'])
    TrainClass = collections.namedtuple('TrainClass', ['train', 'stops'])
    try:
        r = requests.get(baseurl+trainNo)
        r.raise_for_status()
        r.encoding = "gb2312"

        soup = BeautifulSoup(r.text.replace("\n", ""), 'html.parser')
        target_regexp = re.compile(r'ctl00\_MainContentPlaceHolder\_rptStopOverStation.*')
        tt = soup.find_all(id=target_regexp)
        stops = []
        for e in tt:
            stop = e.parent.next_sibling.next_sibling
            start = stop.next_sibling.next_sibling
            station = StopClass(e.string, stop.string.strip(), start.string.strip())
            if station == '畲江北':
                print(trainNo)
                print(r.text)
                break
            stops.append(station)

        return TrainClass(trainNo, stops)
    except Exception as e:
        print(e)


# 获取列车时刻表，保存到json文件
def getSch(inshorter, outjson):
    f = open(inshorter, 'r', encoding='utf-8')
    strJson = json.load(f)
    listT = [e['station_train_code'] for e in strJson]
    print(len(listT), listT)
    f.close()

    Trains = []
    i = 0
    for train in listT:
        Trains.append(crawlTrainInfo(train))
        if i % 100 == 0:
            print(i)
        time.sleep(0.1)
        i = i + 1

    with open(outjson, 'w', encoding='gb2312') as fd:
        fd.write(json.dumps(Trains))


# 避免重复查询，把已查记录存好
SC = dict()


# 将车站转换为所在的城市
def s2c(station):
    address = station + '站'
    if address in SC:
        return SC[address]
    else:
        key = '27ea3472ed190ddbc5e3160188e74111'
        url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={key}'

        r = requests.get(url)
        info = r.json()

        if info['count'] == '0':  # 未查到该车站
            SC[address] = 0
            return 0
        else:
            city = info['geocodes'][0]['city']
            if city == []:
                SC[address] = 0
                return 0
            else:
                SC[address] = city
                return city


# 将时刻表转化为图的节点和边（初步）
# Dtrain_infos.json, Gtrain_infos.json 保存了每个车次的时刻表，包括站名，到站时间，离站时间
# 从这两个文件中提取出图的节点-城市，边（一站连接的两个城市，）
# 节点用集合stations表示
# 每条边用一个字典元素表示，键名为“某站-某站”，值为一个列表，列表元素为（时间，车次）
# 在高德地图上查不到所在城市的车站和关联的边保存至odds和oddsPaths
def getNandE(injson, outjson):
    stations = set()    # xx市
    trains = []
    paths = dict()
    odds = set()
    oddsPaths = dict()
    with open(injson, 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        # print(len(dinfo))
        i0 = 0

        for train in dinfo:
            trains.append(train[0])

            if i0 % 100 == 0:
                print(train[0])
            i0 = i0 + 1

            for stop in train[1]:
                #print('stop: ' + stop[0])
                city = s2c(stop[0])
                if city == 0:
                    odds.add(stop[0])
                else:
                    try:
                        stations.add(city)
                    except:
                        print('error!')
                        print(SC)
                        print(city)
                        print(stop[0])
                        return 0

            LEN = len(train[1])
            for i in range(LEN - 2):
                k1 = s2c(train[1][i][0])
                k2 = s2c(train[1][i + 1][0])

                start = train[1][i][2].split(':')
                arrive = train[1][i + 1][2].split(':')
                weight = 60 * (int(arrive[0]) - int(start[0])) + (int(arrive[1]) - int(start[1]))

                if k1 == 0 or k2 == 0:
                    edgekey = train[1][i][0] + '-' + train[1][i + 1][0]
                    if edgekey in oddsPaths:
                        oddsPaths[edgekey].append((weight, train[0]))
                    else:
                        oddsPaths[edgekey] = [(weight, train[0])]
                else:
                    edgekey = k1 + '-' + k2   # xx市-xx市
                    if edgekey in paths:
                        paths[edgekey].append((weight, train[0]))
                    else:
                        paths[edgekey] = [(weight, train[0])]

    out = (list(stations), paths, list(odds), oddsPaths)

    with open(outjson, 'w', encoding='gb2312') as fd:
        fd.write(json.dumps(out))


def main():
    # 下载需要的文件
    tn_data_url = 'https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0'
    #download_data(tn_data_url, 'tnumber_datas.txt')

    station_data_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9002'
    #download_data(station_data_url, 'stations_datas.txt')

    #get_train_info()

    getSch('Dshorter_list.txt', 'Dtrain_infos.json')
    #getSch('Gshorter_list.txt', 'Gtrain_infos.json')
    #getNandE('Dtrain_infos.json', 'DNode_Edge.json')
    #getNandE('Gtrain_infos.json', 'GNode_Edge.json')


if __name__ == "__main__":
    main()



