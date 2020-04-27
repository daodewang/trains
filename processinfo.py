import json
import networkx as nx
from operator import itemgetter
import matplotlib.pyplot as plt
import requests


# 将车站转换为所在的城市
def s2c(station):
    key = '27ea3472ed190ddbc5e3160188e74111'
    address = station + '站'
    url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={key}'

    r = requests.get(url)
    #print('addr: ' + address)
    #print(r)
    info = r.json()

    if info['count'] == '0':  # 未查到该车站
        return 0
    else:
        city = info['geocodes'][0]['city']
        return city


# 将时刻表转化为图的节点和边
# Dtrain_infos.json, Gtrain_infos.json 保存了每个车次的时刻表，包括站名，到站时间，离站时间
def getNandE():
    stations = set()
    trains = []
    paths = dict()
    odds = set()
    oddsPaths = dict()
    with open('Dtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        # print(len(dinfo))
        i0 = 0

        for train in dinfo:
            trains.append(train[0])
            print(f'{i0}' + train[0])

            i0 = i0+1
            if i0 == 5:
                break

            for stop in train[1]:
                #print('stop: ' + stop[0])
                city = s2c(stop[0])
                if city == 0:
                    odds.add(stop[0])
                else:
                    stations.add(city)

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
                    edgekey = str(k1) + '-' + str(k2)
                    if edgekey in paths:
                        paths[edgekey].append((weight, train[0]))
                    else:
                        paths[edgekey] = [(weight, train[0])]

    print(stations)
    print(trains)
    print(paths)
    print(oddsPaths)


def getTimeEdges(paths):
    edges = []
    for k, v in paths.items():
        weight = int(sum(v)/len(v))
        nodes = k.split('-')
        edges.append((nodes[0], nodes[1], {'time': weight}))
    return edges


'''
def getEdges(paths):
    edges = []
    for k, v in paths.items():
        weight = len(v)
        nodes = k.split('-')
        edges.append((nodes[0], nodes[1], {'weight': weight}))

    return edges


def getS_Tedge(stations):
    edges = []
    odd = set()
    with open('Dtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)

        for train in dinfo:
            for stop in train[1]:
                k = stop[0]
                r, k1 = sta2city(k, stations)
                if r:
                    odd.add(k)
                    k = k1
                edges.append((train[0], k))

    with open('Gtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)

        for train in dinfo:
            for stop in train[1]:
                k = stop[0]
                r, k1 = sta2city(k, stations)
                if r:
                    odd.add(k)
                    k = k1
                edges.append((train[0], k))
    return edges, odd
'''


def main():
    getNandE()
    '''
    G = nx.DiGraph()

    stations, trains = getSandT()
    print('stations: %d' % len(stations))

    # odd 是被聚类去掉的站点
    edges, odd = getS_Tedge(stations)
    print('odds: %d' % len(odd))

    sj = stations - odd
    print('stations - odds: %d' % len(sj))

    paths = getTimePaths(sj)
    timedges = getTimeEdges(paths)

    
    # 赋权图
    G.add_nodes_from(sj)
    G.add_edges_from(timedges)
    
    btw = nx.algorithms.centrality.betweenness_centrality(G, weight='time')
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))

    btw = nx.algorithms.centrality.betweenness_centrality(G)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))

    deg = G.degree()
    print(sorted(deg, key=lambda x: (x[1]), reverse=True))
    data = [x[1] for x in deg if x[1] > 0]
    data1 = [len(bin(d))-1 for d in data]

    
    sub = [node[0] for node in deg if node[1] == 2]

    addons = [ '湛江', '北海', '福州', '上海']
    st = set(sub) | set(addons)

    
    
    btw = nx.algorithms.centrality.betweenness_centrality_subset(G,  weight='time', sources=st, targets=st)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))
    btw = nx.algorithms.centrality.betweenness_centrality_subset(G, sources=st, targets=st)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True)
    

    # 二部图
    edges, odd = getS_Tedge(stations)
    print(len(odd))

    G1 = nx.DiGraph()

    G1.add_nodes_from(trains)
    G1.add_nodes_from(sj)
    G1.add_edges_from(edges)

    ind = G1.in_degree()
    print(ind)
    print(sorted(ind, key=lambda x: (x[1]), reverse=True))
    data = [x[1] for x in ind if x[1] > 0]
    data1 = [len(bin(d)) - 1 for d in data]


    # print(data)
    plt.hist(data1, bins=100)
    plt.show()

    fig1, ax1 = plt.subplots()
    ax1.hist(data, bins=100)
    ax1.set_xscale("log")
    ax1.set_xlim(1e0, 1e2)
    ax1.grid()
    plt.draw()
    plt.show()'''


if __name__ == "__main__":
    main()



