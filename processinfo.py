import json
import networkx as nx
from operator import itemgetter
import matplotlib.pyplot as plt


def getSandT():
    stations = set()
    trains = []
    with open('Dtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        print(len(dinfo))

        for train in dinfo:
            trains.append(train[0])
            for stop in train[1]:
                stations.add(stop[0])

    with open('Gtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        print(len(dinfo))

        for train in dinfo:
            trains.append(train[0])
            for stop in train[1]:
                stations.add(stop[0])

    return stations, trains


def getPaths():
    paths = dict()
    with open('Dtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        print(len(dinfo))
        j=0
        for train in dinfo:
            j=j+1
            L = len(train[1])
            for i in range(L-2):
                edgekey = str(train[1][i][0]) + '-' + str(train[1][i+1][0])
                start = train[1][i][2].split(':')
                arrive = train[1][i+1][2].split(':')
                weight = 60*(int(arrive[0])-int(start[0]))+(int(arrive[1])-int(start[1]))
                if edgekey in paths:
                    paths[edgekey].append(weight)
                else:
                    paths[edgekey] = [weight]

    with open('Gtrain_infos.json', 'r', encoding='utf-8') as f:
            dinfo = json.load(f)
            print(len(dinfo))
            j = 0
            for train in dinfo:
                j = j + 1
                L = len(train[1])
                for i in range(L - 2):
                    edgekey = str(train[1][i][0]) + '-' + str(train[1][i + 1][0])
                    start = train[1][i][2].split(':')
                    arrive = train[1][i + 1][2].split(':')
                    weight = 60 * (int(arrive[0]) - int(start[0])) + (int(arrive[1]) - int(start[1]))
                    if edgekey in paths:
                        paths[edgekey].append(weight)
                    else:
                        paths[edgekey] = [weight]

    print(len(paths))
    return paths


def getTimeEdges(paths):
    edges = []
    for k, v in paths.items():
        weight = int(sum(v)/len(v))
        nodes = k.split('-')
        edges.append((nodes[0], nodes[1], {'weight': weight}))
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
                if k == '上海虹桥':
                    odd.add(k)
                    k = '上海'
                if k == '合肥北城':
                    odd.add(k)
                    k = '合肥'
                if k == '戚墅堰':
                    odd.add(k)
                    k = '常州'
                if k == '深圳坪山':
                    odd.add(k)
                    k = '深圳'
                if k == '汉口' or k == '武昌':
                    odd.add(k)
                    k = '武汉'
                if k[-1] in {'东', '南', '西', '北'}:
                    k1 = k[0:-1]
                    if k1 in stations:
                        odd.add(k)
                        k = k1
                edges.append((train[0], k))

    with open('Gtrain_infos.json', 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        print(len(dinfo))

        for train in dinfo:
            for stop in train[1]:
                k = stop[0]
                if k == '上海虹桥':
                    k = '上海'
                if k == '合肥北城':
                    k = '合肥'
                if k == '戚墅堰':
                    k = '常州'
                if k == '深圳坪山':
                    odd.add(k)
                    k = '深圳'
                if k == '汉口' or k == '武昌':
                    odd.add(k)
                    k = '武汉'
                if k[-1] in {'东', '南', '西', '北'}:
                    k1 = k[0:-1]
                    if k1 in stations:
                        odd.add(k)
                        k = k1
                edges.append((train[0], k))

    print(len(edges))

    return edges, odd


def main():
    stations, trains = getSandT()
    print(len(stations))

    edges, odd = getS_Tedge(stations)
    print(len(odd))

    sj = stations - odd
    print(len(sj))

    G = nx.DiGraph()
    G.add_nodes_from(trains)
    G.add_nodes_from(sj)
    G.add_edges_from(edges)

    ind = G.in_degree()
    print(ind)
    print(sorted(ind, key=lambda x: (x[1]), reverse=True))


if __name__ == "__main__":
    main()


