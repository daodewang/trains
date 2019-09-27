import json
import networkx as nx
from operator import itemgetter
import matplotlib.pyplot as plt


def getSandT():
    stations = set()
    trains = []
    with open('Dtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        #print(len(dinfo))

        for train in dinfo:
            trains.append(train[0])
            for stop in train[1]:
                stations.add(stop[0])

    with open('Gtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        #print(len(dinfo))

        for train in dinfo:
            trains.append(train[0])
            for stop in train[1]:
                stations.add(stop[0])

    return stations, trains


def sta2city(k, citys):
    r = False

    if k == '上海虹桥':
        r = True
        k = '上海'
    if k == '合肥北城':
        r = True
        k = '合肥'
    if k == '戚墅堰':
        r = True
        k = '常州'
    if k == '深圳坪山':
        r = True
        k = '深圳'
    if k in {'汉口', '武昌', '天河机场', '毛陈', '金银潭'}:
        r = True
        k = '武汉'
    if k[-1] in {'东', '南', '西', '北'} and len(k) > 2:
        r = True
        k = k[0:-1]

    return r, k


def getTimePaths(citys):
    paths = dict()
    with open('Dtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)

        for train in dinfo:
            L = len(train[1])
            for i in range(L-2):
                r, k1 = sta2city(train[1][i][0], citys)
                r, k2 = sta2city(train[1][i+1][0], citys)

                edgekey = str(k1) + '-' + str(k2)
                start = train[1][i][2].split(':')
                arrive = train[1][i+1][2].split(':')
                weight = 60*(int(arrive[0])-int(start[0]))+(int(arrive[1])-int(start[1]))
                if edgekey in paths:
                    paths[edgekey].append(weight)
                else:
                    paths[edgekey] = [weight]

    with open('Gtrain_infos.json', 'r', encoding='utf-8') as f:
            dinfo = json.load(f)

            for train in dinfo:
                L = len(train[1])
                for i in range(L - 2):
                    r, k1 = sta2city(train[1][i][0], citys)
                    r, k2 = sta2city(train[1][i + 1][0], citys)

                    edgekey = str(k1) + '-' + str(k2)
                    start = train[1][i][2].split(':')
                    arrive = train[1][i + 1][2].split(':')
                    weight = 60 * (int(arrive[0]) - int(start[0])) + (int(arrive[1]) - int(start[1]))
                    if edgekey in paths:
                        paths[edgekey].append(weight)
                    else:
                        paths[edgekey] = [weight]

    return paths


def getTimeEdges(paths):
    edges = []
    for k, v in paths.items():
        weight = int(sum(v)/len(v))
        nodes = k.split('-')
        edges.append((nodes[0], nodes[1], {'time': weight}))
    return edges


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


def main():
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

    '''
    # 赋权图
    G.add_nodes_from(sj)
    G.add_edges_from(timedges)
    
    btw = nx.algorithms.centrality.betweenness_centrality(G, weight='time')
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))

    btw = nx.algorithms.centrality.betweenness_centrality(G)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))

    deg = G.degree()
    sub = [node[0] for node in deg if node[1] == 2]

    addons = [ '湛江', '北海', '福州', '上海']
    st = set(sub) | set(addons)
    
    btw = nx.algorithms.centrality.betweenness_centrality_subset(G,  weight='time', sources=st, targets=st)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))
    btw = nx.algorithms.centrality.betweenness_centrality_subset(G, sources=st, targets=st)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))
'''
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
    print(data)
    plt.hist(data, bins=100)
    plt.show()

    fig1, ax1 = plt.subplots()
    ax1.hist(data, bins=1000)
    ax1.set_xscale("log")
    ax1.set_xlim(1e0, 1e3)
    ax1.grid()
    plt.draw()
    plt.show()


if __name__ == "__main__":
    main()


