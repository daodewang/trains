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


def main():
    # 下载需要的文件
    tn_data_url = 'https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0'
    #download_data(tn_data_url, 'tnumber_datas.txt')

    station_data_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9002'
    #download_data(station_data_url, 'stations_datas.txt')

    #get_train_info()

    #getSch('Dshorter_list.txt', 'Dtrain_infos.json')
    getSch('Gshorter_list.txt', 'Gtrain_infos.json')


if __name__ == "__main__":
    main()



