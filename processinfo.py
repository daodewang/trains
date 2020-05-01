import json
import networkx as nx
from operator import itemgetter
import matplotlib.pyplot as plt
import requests


# 将上一步的到的paths转换为无向图的边
def getUDEdges(paths):
    edges = []
    for k in paths.items():
        node = k.split('-')
        edges.append((node[0], node[1]))
    return edges


def getCBEdges(paths):
    edges = []
    for k, v in paths.items():
        weight = len(v)
        node = k.split('-')
        edges.append((node[0], node[1], {'no': weight}))
    return edges


def getTimeEdges(paths):
    edges = []
    for k, v in paths.items():
        weight = int(sum(v)/len(v))
        nodes = k.split('-')
        edges.append((nodes[0], nodes[1], {'time': weight}))
    return edges


def loadinfo(injson):
    with open(injson, 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        return dinfo


def main():

    Dinfo = loadinfo('DNode_Edge.json')
    print(len(Dinfo[2]))
    print(Dinfo[2])
    print(len(Dinfo[3]))


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



