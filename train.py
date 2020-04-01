import re
import json
import requests
from bs4 import BeautifulSoup
import collections
import time


# 下载所有的车次数据 | 保存为 tnumber_datas.txt 文件
def download_tnumber_datas(tn_datas_url):
    requests.adapters.DEFAULT_RETRIES = 5
    response = requests.get(tn_datas_url, stream=True,verify=False)
    status = response.status_code
    if status == 200:
        with open('stations_datas.txt', 'wb') as tfile:
            for chunk in response.iter_content(chunk_size=102400): # 成块读取数据
                if chunk:
                    tfile.write(chunk)


'''
# 下载需要的文件
tn_datas_url='https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0'
download_tnumber_datas(tn_datas_url)

station_datas_url='https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9002'
download_tnumber_datas(station_datas_url)


#分析train_list.txt文件 得出火车 出发站到终点站的数据
def trainListStartToEnd():
    global station_start_end_set
    with open('train_list.txt','rb') as of:
        text=of.readline()
        tt=text.decode("utf-8")
        ss=tt.replace("},{","}\n{").replace("2017-","\n").replace("[","\n").split("\n")
        m_list=list()
        for s in ss:
            pattern = re.compile(r'\((\w+-\w+)\)')
            match = pattern.search(s)
            if match:
                m_list.append(match.group(1))
        station_start_end_set=set(m_list)


init_url='https://kyfw.12306.cn/otn/queryTrainInfo/init '
query_url='https://kyfw.12306.cn/otn/leftTicket/query?'

# 利用出发站到终点站 爬取期间的列车数据
def getTrainNoList(back_date, train_date, from_station, from_station_name, to_station, to_station_name):
    post_data = {'back_train_date': back_date,
                 '_json_att': "", 'flag': 'dc',
                 'leftTicketDTO.from_station': from_station,
                 'leftTicketDTO.to_station': to_station,
                 'leftTicketDTO.from_station_name': from_station_name,
                 'leftTicketDTO.to_station_name': to_station_name,
                 'leftTicketDTO.train_date': train_date,
                 'pre_step_flag': 'index',
                 'purpose_code': 'ADULT'}

    init_resp = requests.post(init_url, data=post_data, headers=HEADERS, allow_redirects=True, verify=False)
    cookies = init_resp.cookies
    cookies.set('_jc_save_fromStation', from_station_name + ',' + from_station, domain='kyfw.12306.cn', path='/')
    cookies.set('_jc_save_toStation', to_station_name + ',' + to_station, domain='kyfw.12306.cn', path='/')
    cookies.set('_jc_save_fromDate', train_date, domain='kyfw.12306.cn', path='/')
    cookies.set('_jc_save_toDate', back_date, domain='kyfw.12306.cn', path='/')
    cookies.set('_jc_save_wfdc_flag', 'dc', domain='kyfw.12306.cn', path='/')
    url = query_url + "leftTicketDTO.train_date=" + train_date + "&leftTicketDTO.from_station=" + from_station + "&leftTicketDTO.to_station=" + to_station + "&purpose_codes=ADULT"
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=True, cookies=cookies, verify=False, timeout=10)
        data = ""
        if response.status_code == 200:
            data = response.content
        data = data.decode("UTF-8")
        return data, cookies
    except  Exception as err:
        logger.exception(
            'getTrainNoList error 获取车次列表错误 日期' + train_date + '从' + from_station_name + '到' + to_station_name + ' :%s',
            err)
        return None, None


#trainListStartToEnd()
'''

# 提取动车、高铁信息


'''
with open('train_list.txt','r', encoding='utf-8') as f:

    strJson = json.load(f)

    onedayD = strJson["2019-07-16"]['D']
    with open('Dtrain.txt', 'w', encoding='utf-8') as ff:
        json.dump(onedayD,ff)

    onedayG = strJson["2019-07-16"]['G']
    with open('Gtrain.txt', 'w', encoding='utf-8') as ff:
        json.dump(onedayG, ff)

    with open('Dtrain.txt', 'w', encoding='utf-8') as f2:
        json.dump(onedayD,f2)

    listD = [e['station_train_code'] for e in onedayD]
    listG = [e['station_train_code'] for e in onedayG]
    print(len(onedayD))
    print(listD)
    print(len(onedayG))
    print(listG)
'''


# 精简信息，只有车次
'''
with open('Dtrain.txt', 'r', encoding='utf-8') as f:
    patten = r'\(.*?\)'
    data = f.read()
    newdata = re.sub(patten, '', data)

    with open('Dshorter_list.txt', 'w', encoding='utf-8') as f2:
        f2.write(newdata)


'''
#获取车次列表

f = open('Dshorter_list.txt', 'r', encoding='utf-8')
strJson = json.load(f)
listD = [e['station_train_code'] for e in strJson]
print(len(listD),listD)
f.close()

f = open('Gshorter_list.txt', 'r', encoding='utf-8')
strJson = json.load(f)
listG = [e['station_train_code'] for e in strJson]
print(len(listG),listG)
f.close()

baseurl = 'https://trains.ctrip.com/trainbooking/TrainSchedule/'

StopClass = collections.namedtuple('StopClass', ['name', 'stop', 'start'])
TrainClass = collections.namedtuple('TrainClass', ['train', 'stops'])


def getTrainInfo(trainNo='G1'):
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


'''
# crawle and save to file
Gtrains = []
i = 0
for train in listG:
    Gtrains.append(getTrainInfo(train))
    if i % 100 == 0:
        print(i)
    time.sleep(0.1)
    i = i+1

with open('Gtrain_infos.json', 'w', encoding='gb2312') as fd:
    fd.write(json.dumps(Gtrains))

'''
print('OK')



